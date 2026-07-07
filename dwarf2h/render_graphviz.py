from __future__ import annotations

import html
import re
from typing import Any
from collections.abc import Callable

from elftools.dwarf.dwarfinfo import DWARFInfo

from . import dwarf as _d


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _dot_port_escape(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def _graphviz_html_preserve_indent(line: str) -> str:
    expanded = line.expandtabs(4)
    leading = len(expanded) - len(expanded.lstrip(" "))
    body = html.escape(expanded.lstrip(" "))
    return ("&#160;" * leading) + body


def _graphviz_declarative_target(type_die: Any) -> Any | None:
    current = type_die
    seen: set[int] = set()
    while current is not None:
        marker = id(current)
        if marker in seen:
            return None
        seen.add(marker)

        if current.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
            return current

        if current.tag in {
            "DW_TAG_const_type",
            "DW_TAG_volatile_type",
            "DW_TAG_atomic_type",
            "DW_TAG_typedef",
            "DW_TAG_array_type",
        }:
            current = _d._resolve_type_attr(current)
            continue

        return None

    return None


def _graphviz_member_link_target(member_type: Any) -> Any | None:
    current = member_type
    seen: set[int] = set()

    while current is not None:
        marker = id(current)
        if marker in seen:
            return None
        seen.add(marker)

        if current.tag in {"DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_atomic_type", "DW_TAG_typedef"}:
            current = _d._resolve_type_attr(current)
            continue

        if current.tag == "DW_TAG_array_type":
            base_type, _ = _d._unwrap_array_type(current)
            current = base_type
            continue

        if current.tag == "DW_TAG_pointer_type":
            return _graphviz_declarative_target(_d._resolve_type_attr(current))

        return _graphviz_declarative_target(current)

    return None


def _graphviz_is_inline_anonymous_composite(
    cu_prefix: str,
    member_type: Any,
    included_set: set[str],
) -> bool:
    if member_type is None:
        return False
    if member_type.tag not in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
        return False
    if _d.die_name(member_type) != "<anonymous>":
        return False
    return _d._die_key(cu_prefix, member_type) not in included_set


def _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix: str, root_die: Any) -> set[str]:
    inline_keys: set[str] = set()
    visited: set[int] = set()

    def visit_type(type_die: Any) -> None:
        if type_die is None:
            return

        marker = id(type_die)
        if marker in visited:
            return
        visited.add(marker)

        if type_die.tag in {"DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_atomic_type", "DW_TAG_typedef"}:
            visit_type(_d._resolve_type_attr(type_die))
            return

        if type_die.tag == "DW_TAG_array_type":
            base_type, _ = _d._unwrap_array_type(type_die)
            visit_type(base_type)
            return

        if type_die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
            if _d.die_name(type_die) == "<anonymous>":
                inline_keys.add(_d._die_key(cu_prefix, type_die))

            if type_die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
                for child in type_die.iter_children():
                    if child.tag != "DW_TAG_member":
                        continue
                    visit_type(_d._resolve_type_attr(child))

    visit_type(root_die)
    return inline_keys


def _graphviz_emit_member_rows(
    cu_prefix: str,
    member_die: Any,
    included_set: set[str],
    linkable_targets: set[str],
    *,
    row_index: int,
    port_prefix: str = "m",
    indent: str = "",
) -> tuple[list[tuple[str | None, str]], list[tuple[str, str]]]:
    rows: list[tuple[str | None, str]] = []
    links: list[tuple[str, str]] = []

    member_name = _d.die_name(member_die)
    member_type = _d._resolve_type_attr(member_die)
    port_base = _dot_port_escape(f"{port_prefix}_{row_index}_{member_name}")

    if _graphviz_is_inline_anonymous_composite(cu_prefix, member_type, included_set):
        tag_kw = _d._c_tag_name(member_type.tag)
        rows.append((None, _graphviz_html_preserve_indent(f"{indent}{tag_kw} {{")))

        child_index = 0
        for child in member_type.iter_children():
            if child.tag != "DW_TAG_member":
                continue
            child_rows, child_links = _graphviz_emit_member_rows(
                cu_prefix,
                child,
                included_set,
                linkable_targets,
                row_index=child_index,
                port_prefix=port_base,
                indent=indent + "    ",
            )
            rows.extend(child_rows)
            links.extend(child_links)
            child_index += 1

        suffix = f" {member_name};" if member_name != "<anonymous>" else ";"
        rows.append((None, _graphviz_html_preserve_indent(f"{indent}}}{suffix}")))
        return rows, links

    member_inline_keys = _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix, member_type)
    rendered_lines = _d._emit_member_lines(cu_prefix, member_die, member_inline_keys, "")
    row_text = "<br align=\"left\"/>".join(
        _graphviz_html_preserve_indent(line.rstrip()) for line in rendered_lines if line.strip()
    )
    if not row_text:
        row_text = html.escape("/* unresolved member */")

    rows.append((port_base, row_text))

    if member_type is not None:
        target_die = _graphviz_member_link_target(member_type)
        if target_die is not None:
            target_key = _d._die_key(cu_prefix, target_die)
            if target_key in linkable_targets:
                links.append((port_base, target_key))

    return rows, links


def _graphviz_should_include_node(node_key: str, nodes: dict[str, tuple[str, Any]]) -> bool:
    _, die = nodes[node_key]
    if die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
        if _d.die_name(die) == "<anonymous>":
            return False
    return True


def _graphviz_node_header(cu_prefix: str, die: Any, name: str) -> tuple[str, str]:
    if die.tag == "DW_TAG_structure_type":
        suffix = " (packed)" if _d._is_packed_composite(cu_prefix, die) else ""
        return ("struct", suffix)
    if die.tag == "DW_TAG_union_type":
        return ("union", "")
    if die.tag == "DW_TAG_enumeration_type":
        return ("enum", "")
    return ("type", "")


def _graphviz_bgcolor_for_die(die: Any) -> str:
    if die.tag == "DW_TAG_structure_type":
        return "LightSteelBlue"
    if die.tag == "DW_TAG_union_type":
        return "LightGoldenrodYellow"
    if die.tag == "DW_TAG_enumeration_type":
        return "PaleGreen"
    return "gray95"


def _graphviz_append_type_box(
    lines: list[str],
    edges: list[str],
    *,
    node_id: str,
    cu_prefix: str,
    die: Any,
    display_name: str,
    included_set: set[str],
    node_ids: dict[str, str],
) -> None:
    linkable_targets = included_set | set(node_ids.keys())
    kind, suffix = _graphviz_node_header(cu_prefix, die, display_name)
    bgcolor = _graphviz_bgcolor_for_die(die)

    lines.append(f"  // {kind} {display_name}{suffix}")
    lines.append(f"  {node_id} [")
    lines.append(
        '    label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="10" bgcolor="'
        + bgcolor
        + '">'
    )
    lines.append(
        "      <tr><td><font point-size=\"12.0\"><b>"
        + html.escape(f"{kind} {display_name}{suffix}")
        + "</b></font></td></tr>"
    )

    if die.tag == "DW_TAG_enumeration_type":
        enum_rows: list[str] = []
        for child in die.iter_children():
            if child.tag != "DW_TAG_enumerator":
                continue
            enum_name = _d.die_name(child)
            const_attr = child.attributes.get("DW_AT_const_value")
            if const_attr is None:
                enum_rows.append(f"{enum_name},")
            else:
                enum_rows.append(f"{enum_name} = {const_attr.value},")
        if not enum_rows:
            enum_rows.append("/* no enumerators in DWARF */")

        lines.append('      <tr><td><table border="0" cellborder="0" cellspacing="0" cellpadding="0">')
        for row in enum_rows:
            lines.append(
                '        <tr><td align="left"><font point-size="8.0">'
                + html.escape(row)
                + "</font></td></tr>"
            )
        lines.append("      </table></td></tr>")
    else:
        member_rows: list[tuple[str | None, str]] = []
        member_idx = 0
        for child in die.iter_children():
            if child.tag != "DW_TAG_member":
                continue

            rendered_rows, pointer_links = _graphviz_emit_member_rows(
                cu_prefix,
                child,
                included_set,
                linkable_targets,
                row_index=member_idx,
            )
            member_rows.extend(rendered_rows)
            for port_name, target_key in pointer_links:
                if target_key in node_ids:
                    dst = node_ids[target_key]
                    edges.append(f"  {node_id}:{port_name} -> {dst}:n;")
            member_idx += 1

        if not member_rows:
            member_rows.append(("m_empty", html.escape("/* no members in DWARF */")))

        lines.append('      <tr><td><table border="0" cellborder="0" cellspacing="0" cellpadding="0">')
        for port_name, row_text in member_rows:
            if port_name is None:
                lines.append(
                    '        <tr><td align="left"><font point-size="8.0">'
                    + row_text
                    + "</font></td></tr>"
                )
            else:
                lines.append(
                    '        <tr><td align="left" port="'
                    + port_name
                    + '"><font point-size="8.0">'
                    + row_text
                    + "</font></td></tr>"
                )
        lines.append("      </table></td></tr>")

    lines.append("    </table>>")
    lines.append("  ];")
    lines.append("")


def _build_header_like_dot(
    nodes: dict[str, tuple[str, Any]],
    included_keys: list[str],
    *,
    graph_name: str,
    graph_label: str,
    root_key: str | None = None,
) -> str:
    included_set = set(included_keys)
    node_ids = {node_key: f"ref_{idx}" for idx, node_key in enumerate(included_keys)}
    typedef_keys = [key for key in included_keys if nodes[key][1].tag == "DW_TAG_typedef"]
    typedef_multiline_boxes: list[tuple[str, str, str, Any]] = []
    typedef_multiline_typedef_keys: set[str] = set()
    typedef_target_node_ids: dict[str, str] = {}

    for node_key in typedef_keys:
        cu_prefix, die = nodes[node_key]
        typedef_name = _d.die_name(die)
        target = _d._resolve_type_attr(die)
        if (
            typedef_name == "<anonymous>"
            or target is None
            or not _d._is_anonymous_typedef_inline_target(target)
            or _d._die_key(cu_prefix, target) in included_set
        ):
            continue

        nested_inline_keys = _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix, target)
        declaration = _d._emit_typedef_inline_composite(
            cu_prefix,
            typedef_name,
            target,
            nested_inline_keys,
        )
        if "\n" not in declaration:
            continue
        if target.tag not in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
            continue

        typedef_box_id = f"typedef_box_{len(typedef_multiline_boxes)}"
        typedef_multiline_boxes.append((typedef_box_id, typedef_name, cu_prefix, target))
        typedef_multiline_typedef_keys.add(node_key)
        target_key = _d._die_key(cu_prefix, target)
        if target_key not in typedef_target_node_ids:
            typedef_target_node_ids[target_key] = typedef_box_id

    node_ids.update(typedef_target_node_ids)

    lines = [
        f"digraph {graph_name} {{",
        '  graph [label="' + _dot_escape(graph_label) + '", labelloc="t", rankdir="LR", fontname="Helvetica,Arial,sans-serif"];',
        '  node [fontname="Helvetica,Arial,sans-serif", shape=plain, style=filled, fillcolor=gray95];',
        '  edge [fontname="Helvetica,Arial,sans-serif", arrowhead=vee, style=dashed];',
        "",
    ]

    edges: list[str] = []

    for node_key in included_keys:
        cu_prefix, die = nodes[node_key]
        if die.tag not in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
            continue

        node_id = node_ids[node_key]
        name = _d.die_name(die)
        if name == "<anonymous>":
            name = _d._anon_c_type_name(cu_prefix, die)
        _graphviz_append_type_box(
            lines,
            edges,
            node_id=node_id,
            cu_prefix=cu_prefix,
            die=die,
            display_name=name,
            included_set=included_set,
            node_ids=node_ids,
        )

    if typedef_keys:
        lines.append("  // typedefs")
        lines.append("  typedefs [")
        lines.append('    label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="10">')
        lines.append('      <tr><td><font point-size="12.0"><b>Typedefs</b></font></td></tr>')
        lines.append('      <tr><td><table border="0" cellborder="0" cellspacing="0" cellpadding="0">')
        for node_key in typedef_keys:
            if node_key in typedef_multiline_typedef_keys:
                continue

            cu_prefix, die = nodes[node_key]
            declaration: str | None = None

            if die.tag == "DW_TAG_typedef":
                typedef_name = _d.die_name(die)
                target = _d._resolve_type_attr(die)
                if (
                    typedef_name != "<anonymous>"
                    and target is not None
                    and _d._is_anonymous_typedef_inline_target(target)
                    and _d._die_key(cu_prefix, target) not in included_set
                ):
                    nested_inline_keys = _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix, target)
                    declaration = _d._emit_typedef_inline_composite(
                        cu_prefix,
                        typedef_name,
                        target,
                        nested_inline_keys,
                    )

            if declaration is None:
                declaration = _d._emit_c_declaration_for_node(node_key, nodes, set(), set())
            if declaration is None:
                continue
            declaration = html.escape(declaration).replace("\n", "<br align=\"left\"/>")
            lines.append(
                '        <tr><td align="left"><font point-size="8.0">'
                + declaration
                + "</font></td></tr>"
            )
        lines.append("      </table></td></tr>")
        lines.append("    </table>>")
        lines.append("  ];")
        lines.append("")

    for typedef_node_id, typedef_name, cu_prefix, target_die in typedef_multiline_boxes:
        _graphviz_append_type_box(
            lines,
            edges,
            node_id=typedef_node_id,
            cu_prefix=cu_prefix,
            die=target_die,
            display_name=typedef_name,
            included_set=included_set,
            node_ids=node_ids,
        )

    lines.extend(edges)
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_reverse_dependencies_graphviz(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> str:
    status_cb("Generating Graphviz C-header style output")
    nodes, _, order, inline_keys, typedef_inline_target_keys, root_key = _d._collect_render_context(
        cu_prefix,
        root_die,
        status_cb,
    )

    included_keys: list[str] = []
    for node_key in order:
        if not _graphviz_should_include_node(node_key, nodes):
            continue
        if node_key in inline_keys or node_key in typedef_inline_target_keys:
            continue
        declaration = _d._emit_c_declaration_for_node(
            node_key,
            nodes,
            inline_keys,
            typedef_inline_target_keys,
        )
        if declaration is None:
            continue
        included_keys.append(node_key)

    root_name = _d.die_name(root_die)
    status_cb(f"Graphviz output complete: {len(included_keys)} node(s)")
    return _build_header_like_dot(
        nodes,
        included_keys,
        graph_name="dwarf2h_type_dependencies",
        graph_label=f"dwarf2h C model for {root_name}",
        root_key=root_key,
    )


def render_all_definitions_graphviz(
    dwarf_infos: list[tuple[str, DWARFInfo]],
    status_cb: Callable[[str], None],
) -> str:
    status_cb("Generating global Graphviz C-header style output")
    named_roots: list[tuple[str, Any]] = []
    for cu_prefix, dwarf_info in dwarf_infos:
        for cu in dwarf_info.iter_CUs():
            for die in cu.iter_DIEs():
                if die.tag not in _d.TYPE_TAGS:
                    continue
                if "DW_AT_name" not in die.attributes:
                    continue
                if _d.decode_name(die.attributes["DW_AT_name"].value) == "<anonymous>":
                    continue
                named_roots.append((cu_prefix, die))

    status_cb(f"Found {len(named_roots)} named root type(s)")

    nodes_acc: dict[str, tuple[str, Any]] = {}
    included_order: list[str] = []
    included_set: set[str] = set()

    for root_idx, (cu_prefix, root_die) in enumerate(named_roots, start=1):
        if root_idx % 500 == 0:
            status_cb(f"Processing root type {root_idx}/{len(named_roots)}")

        nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _d._collect_render_context(
            cu_prefix,
            root_die,
            status_cb,
        )
        nodes_acc.update(nodes)

        for node_key in order:
            if node_key in included_set:
                continue
            if not _graphviz_should_include_node(node_key, nodes):
                continue
            if node_key in inline_keys or node_key in typedef_inline_target_keys:
                continue

            declaration = _d._emit_c_declaration_for_node(
                node_key,
                nodes,
                inline_keys,
                typedef_inline_target_keys,
            )
            if declaration is None:
                continue

            included_set.add(node_key)
            included_order.append(node_key)

    status_cb(f"Global Graphviz output complete: {len(included_order)} node(s)")
    return _build_header_like_dot(
        nodes_acc,
        included_order,
        graph_name="dwarf2h_all_type_dependencies",
        graph_label="dwarf2h C data model for all named types",
    )
