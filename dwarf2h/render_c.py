from __future__ import annotations

from typing import Any
from collections.abc import Callable

from elftools.dwarf.dwarfinfo import DWARFInfo

from . import dwarf as _d


def render_reverse_dependencies(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> str:
    status_cb("Generating C-style reverse dependency output")
    nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _d._collect_render_context(
        cu_prefix,
        root_die,
        status_cb,
    )

    lines = [
        "/* dwarf2h: https://github.com/fozog/dwarf2h */",
    ]
    emitted_count = 0
    for node_key in order:
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
        lines.append(declaration)
        lines.append("")
        emitted_count += 1
        if emitted_count % 100 == 0:
            status_cb(f"Printed {emitted_count} declaration(s)")
    status_cb(f"C-style output complete: {emitted_count} declaration(s)")
    return "\n".join(lines).rstrip() + "\n"


def render_all_definitions(
    dwarf_infos: list[tuple[str, DWARFInfo]],
    status_cb: Callable[[str], None],
    *,
    include_dependency_tree: bool = False,
) -> str:
    status_cb("Generating global C-style output for all named types")
    lines = [
        "/* dwarf2h: https://github.com/fozog/dwarf2h */",
        "",
    ]
    emitted_node_keys: set[str] = set()
    emitted_declarations: set[str] = set()
    root_count = 0
    emitted_count = 0

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

    for cu_prefix, root_die in named_roots:
        root_count += 1
        if root_count % 500 == 0:
            status_cb(f"Processing root type {root_count}/{len(named_roots)}")

        nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _d._collect_render_context(
            cu_prefix,
            root_die,
            status_cb,
        )

        if include_dependency_tree:
            root_name = _d.die_name(root_die)
            lines.append(f"Dependency tree for {root_name}:")
            lines.extend(_d._type_tree_lines(cu_prefix, root_die))
            lines.append("")

        for node_key in order:
            if node_key in emitted_node_keys:
                continue
            if node_key in inline_keys or node_key in typedef_inline_target_keys:
                continue

            declaration = _d._emit_c_declaration_for_node(
                node_key,
                nodes,
                inline_keys,
                typedef_inline_target_keys,
            )
            if declaration is None or declaration in emitted_declarations:
                continue

            lines.append(declaration)
            lines.append("")
            emitted_declarations.add(declaration)
            emitted_node_keys.add(node_key)
            emitted_count += 1
            if emitted_count % 500 == 0:
                status_cb(f"Emitted {emitted_count} declaration(s)")

    status_cb(f"Global C-style output complete: {emitted_count} declaration(s)")
    return "\n".join(lines).rstrip() + "\n"
