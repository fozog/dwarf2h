from __future__ import annotations

import re
import sys
from collections.abc import Callable, Iterable
from typing import Any

from elftools.dwarf.dwarfinfo import DWARFInfo

TYPE_TAGS = {
    "DW_TAG_base_type",
    "DW_TAG_atomic_type",
    "DW_TAG_const_type",
    "DW_TAG_volatile_type",
    "DW_TAG_pointer_type",
    "DW_TAG_array_type",
    "DW_TAG_typedef",
    "DW_TAG_structure_type",
    "DW_TAG_union_type",
    "DW_TAG_enumeration_type",
    "DW_TAG_subroutine_type",
}

COMPOSITE_TYPE_TAGS = {
    "DW_TAG_structure_type",
    "DW_TAG_union_type",
    "DW_TAG_enumeration_type",
}

TRAVERSABLE_TYPE_TAGS = TYPE_TAGS - {"DW_TAG_base_type"}
GRAPH_TYPE_TAGS = TYPE_TAGS


def decode_name(raw_name: object) -> str:
    if raw_name is None:
        return "<anonymous>"
    if isinstance(raw_name, bytes):
        return raw_name.decode("utf-8", errors="replace")
    return str(raw_name)


def die_name(die: Any) -> str:
    name_attr = die.attributes.get("DW_AT_name")
    return decode_name(name_attr.value if name_attr else None)


def iter_declared_types_from_dwarf_info(
    dwarf_info: DWARFInfo,
    *,
    cu_prefix: str = "",
) -> Iterable[tuple[str, str, str]]:
    for cu in dwarf_info.iter_CUs():
        cu_offset = f"{cu_prefix}0x{cu.cu_offset:x}"
        for die in cu.iter_DIEs():
            if die.tag not in TYPE_TAGS:
                continue
            name_attr = die.attributes.get("DW_AT_name")
            name = decode_name(name_attr.value if name_attr else None)
            yield (cu_offset, die.tag, name)


def _die_key(cu_prefix: str, die: Any) -> str:
    return f"{cu_prefix}{die.cu.cu_offset:#x}:{die.offset:#x}"


def _format_die(cu_prefix: str, die: Any) -> str:
    name = die_name(die)
    return f"{die.tag} {name} [{_die_key(cu_prefix, die)}]"


def _resolve_type_attr(die: Any) -> Any | None:
    if "DW_AT_type" not in die.attributes:
        return None
    try:
        return die.get_DIE_from_attribute("DW_AT_type")
    except Exception:
        return None


def _c_tag_name(tag: str) -> str:
    if tag == "DW_TAG_structure_type":
        return "struct"
    if tag == "DW_TAG_union_type":
        return "union"
    if tag == "DW_TAG_enumeration_type":
        return "enum"
    return "type"


def _anon_c_type_name(cu_prefix: str, die: Any) -> str:
    die_key = _die_key(cu_prefix, die).replace(":", "_").replace("x", "")
    return f"__anon_{die_key}"


def _c_type_ref(cu_prefix: str, die: Any) -> str:
    name = die_name(die)

    if die.tag == "DW_TAG_base_type":
        return name
    if die.tag == "DW_TAG_typedef":
        return name
    if die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
        ctag = _c_tag_name(die.tag)
        if name != "<anonymous>":
            return f"{ctag} {name}"
        return f"{ctag} {_anon_c_type_name(cu_prefix, die)}"
    if die.tag == "DW_TAG_const_type":
        target = _resolve_type_attr(die)
        if target is None:
            return "const void"
        return f"const {_c_type_ref(cu_prefix, target)}"
    if die.tag == "DW_TAG_volatile_type":
        target = _resolve_type_attr(die)
        if target is None:
            return "volatile void"
        return f"volatile {_c_type_ref(cu_prefix, target)}"
    if die.tag == "DW_TAG_pointer_type":
        target = _resolve_type_attr(die)
        if target is None:
            return "void *"
        return f"{_c_type_ref(cu_prefix, target)} *"
    if die.tag == "DW_TAG_array_type":
        target = _resolve_type_attr(die)
        if target is None:
            return "void"
        return _c_type_ref(cu_prefix, target)
    if die.tag == "DW_TAG_subroutine_type":
        return "void (*)(void)"
    return "void"


def _attr_to_int(attr: Any) -> int | None:
    value = getattr(attr, "value", None)
    if isinstance(value, int):
        return value
    return None


def _align_up(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return (value + alignment - 1) // alignment * alignment


def _die_byte_size(die: Any) -> int | None:
    size_attr = die.attributes.get("DW_AT_byte_size")
    if size_attr is None:
        return None
    return _attr_to_int(size_attr)


def _type_size_and_align(cu_prefix: str, type_die: Any) -> tuple[int | None, int | None]:
    if type_die.tag in {"DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_typedef"}:
        target = _resolve_type_attr(type_die)
        if target is None:
            return (None, None)
        return _type_size_and_align(cu_prefix, target)

    if type_die.tag == "DW_TAG_array_type":
        elem = _resolve_type_attr(type_die)
        if elem is None:
            return (None, None)
        elem_size, elem_align = _type_size_and_align(cu_prefix, elem)
        dim_size = 1
        has_dim = False
        for child in type_die.iter_children():
            if child.tag != "DW_TAG_subrange_type":
                continue
            part = _subrange_size(child)
            if part == "":
                continue
            has_dim = True
            dim_size *= int(part)
        if elem_size is None:
            return (None, elem_align)
        if not has_dim:
            return (None, elem_align)
        return (elem_size * dim_size, elem_align)

    if type_die.tag == "DW_TAG_pointer_type":
        size = _die_byte_size(type_die)
        if size is None:
            size = 8
        return (size, min(size, 8))

    if type_die.tag == "DW_TAG_subroutine_type":
        return (None, 8)

    if type_die.tag == "DW_TAG_union_type":
        return _composite_size_and_align(cu_prefix, type_die)

    if type_die.tag == "DW_TAG_structure_type":
        return _composite_size_and_align(cu_prefix, type_die)

    size = _die_byte_size(type_die)
    if size is not None and size > 0:
        return (size, min(size, 8))
    return (None, None)


def _composite_size_and_align(cu_prefix: str, die: Any) -> tuple[int | None, int | None]:
    size = _die_byte_size(die)
    max_align = 1
    seen = False
    for child in die.iter_children():
        if child.tag != "DW_TAG_member":
            continue
        if child.attributes.get("DW_AT_bit_size") is not None:
            continue
        member_type = _resolve_type_attr(child)
        if member_type is None:
            continue
        _, member_align = _type_size_and_align(cu_prefix, member_type)
        if member_align is None:
            continue
        max_align = max(max_align, member_align)
        seen = True
    if not seen:
        return (size, None if size is None else 1)
    return (size, max_align)


def _is_packed_composite(cu_prefix: str, die: Any) -> bool:
    if die.tag not in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
        return False

    if die.tag == "DW_TAG_union_type":
        return False

    layout: list[tuple[int, int, int]] = []
    for child in die.iter_children():
        if child.tag != "DW_TAG_member":
            continue
        if child.attributes.get("DW_AT_bit_size") is not None:
            continue

        location = _attr_to_int(child.attributes.get("DW_AT_data_member_location"))
        if location is None:
            continue

        member_type = _resolve_type_attr(child)
        if member_type is None:
            continue
        member_size, member_align = _type_size_and_align(cu_prefix, member_type)
        if member_size is None or member_align is None:
            continue

        layout.append((location, member_size, member_align))

    if not layout:
        return False

    for location, _, member_align in layout:
        if location > 0 and member_align > 1 and (location % member_align) != 0:
            return True

    struct_size = _die_byte_size(die)
    if struct_size is None:
        return False

    max_end = max(location + member_size for location, member_size, _ in layout)
    max_align = max(member_align for _, _, member_align in layout)
    natural_size = _align_up(max_end, max_align)
    return struct_size < natural_size


def _subrange_size(subrange_die: Any) -> str:
    count_attr = subrange_die.attributes.get("DW_AT_count")
    count_value = _attr_to_int(count_attr) if count_attr is not None else None
    if count_value is not None and count_value >= 0:
        return str(count_value)

    upper_attr = subrange_die.attributes.get("DW_AT_upper_bound")
    upper_value = _attr_to_int(upper_attr) if upper_attr is not None else None
    if upper_value is None:
        return ""

    lower_attr = subrange_die.attributes.get("DW_AT_lower_bound")
    lower_value = _attr_to_int(lower_attr) if lower_attr is not None else 0
    if lower_value is None:
        lower_value = 0

    size = upper_value - lower_value + 1
    return str(size) if size > 0 else ""


def _unwrap_array_type(type_die: Any) -> tuple[Any, list[str]]:
    dimensions: list[str] = []
    current = type_die
    while current is not None and current.tag == "DW_TAG_array_type":
        subranges = [child for child in current.iter_children() if child.tag == "DW_TAG_subrange_type"]
        if not subranges:
            dimensions.append("")
        else:
            for subrange in subranges:
                dimensions.append(_subrange_size(subrange))
        current = _resolve_type_attr(current)
    return current, dimensions


def _c_typed_name(cu_prefix: str, type_die: Any, name: str) -> str:
    base_type_die, dimensions = _unwrap_array_type(type_die)
    if base_type_die is None:
        base_type = "void"
    else:
        base_type = _c_type_ref(cu_prefix, base_type_die)

    dim_suffix = "".join(f"[{dim}]" for dim in dimensions)
    return f"{base_type} {name}{dim_suffix}"


def _is_anonymous_composite(die: Any) -> bool:
    return die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"} and die_name(die) == "<anonymous>"


def _emit_typedef_inline_composite(
    cu_prefix: str,
    typedef_name: str,
    target_die: Any,
    inline_keys: set[str],
) -> str:
    tag_kw = _c_tag_name(target_die.tag)
    packed_suffix = " __attribute__((packed))" if _is_packed_composite(cu_prefix, target_die) else ""
    lines = [f"typedef {tag_kw} {{"]
    lines.extend(_emit_composite_members(cu_prefix, target_die, inline_keys, "    "))
    lines.append(f"}}{packed_suffix} {typedef_name};")
    return "\n".join(lines)


def _incoming_edges(
    edges: dict[str, list[tuple[str, str]]],
) -> dict[str, list[tuple[str, str]]]:
    incoming: dict[str, list[tuple[str, str]]] = {}
    for src_key, deps in edges.items():
        for relation, dep_key in deps:
            incoming.setdefault(dep_key, []).append((src_key, relation))
    return incoming


def _typedef_inline_target_keys(
    nodes: dict[str, tuple[str, Any]],
    edges: dict[str, list[tuple[str, str]]],
) -> set[str]:
    incoming = _incoming_edges(edges)
    inline_target_keys: set[str] = set()

    for typedef_key, (cu_prefix, die) in nodes.items():
        if die.tag != "DW_TAG_typedef":
            continue
        if die_name(die) == "<anonymous>":
            continue

        target = _resolve_type_attr(die)
        if target is None or not _is_anonymous_composite(target):
            continue

        target_key = _die_key(cu_prefix, target)
        refs = incoming.get(target_key, [])
        if len(refs) != 1:
            continue
        if refs[0] != (typedef_key, "type"):
            continue

        inline_target_keys.add(target_key)

    return inline_target_keys


def _inline_anonymous_keys(
    nodes: dict[str, tuple[str, Any]],
    edges: dict[str, list[tuple[str, str]]],
    root_key: str,
) -> set[str]:
    incoming = _incoming_edges(edges)
    inline_keys: set[str] = set()
    for node_key, (_, die) in nodes.items():
        if node_key == root_key:
            continue
        if not _is_anonymous_composite(die):
            continue

        refs = incoming.get(node_key, [])
        if len(refs) != 1:
            continue

        src_key, relation = refs[0]
        src_die = nodes[src_key][1] if src_key in nodes else None
        if relation.startswith("member "):
            inline_keys.add(node_key)
        elif relation == "type" and src_die is not None and src_die.tag == "DW_TAG_array_type":
            inline_keys.add(node_key)
    return inline_keys


def _emit_member_lines(
    cu_prefix: str,
    member_die: Any,
    inline_keys: set[str],
    indent: str,
) -> list[str]:
    member_name = die_name(member_die)
    is_anonymous_member = member_name == "<anonymous>"
    member_type = _resolve_type_attr(member_die)
    if member_type is None:
        if is_anonymous_member:
            return [f"{indent}/* unresolved anonymous member */"]
        return [f"{indent}/* unresolved type */ int {member_name};"]

    member_type_key = _die_key(cu_prefix, member_type)
    if member_type_key in inline_keys and member_type.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
        tag_kw = _c_tag_name(member_type.tag)
        lines = [f"{indent}{tag_kw} {{"]
        lines.extend(
            _emit_composite_members(
                cu_prefix,
                member_type,
                inline_keys,
                indent + "    ",
            )
        )
        if is_anonymous_member:
            lines.append(f"{indent}}};")
        else:
            lines.append(f"{indent}}} {member_name};")
        return lines

    if member_type.tag == "DW_TAG_array_type":
        base_type_die, dimensions = _unwrap_array_type(member_type)
        if base_type_die is not None:
            base_type_key = _die_key(cu_prefix, base_type_die)
            if base_type_key in inline_keys and base_type_die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
                tag_kw = _c_tag_name(base_type_die.tag)
                suffix = "".join(f"[{dim}]" for dim in dimensions)
                lines = [f"{indent}{tag_kw} {{"]
                lines.extend(_emit_composite_members(cu_prefix, base_type_die, inline_keys, indent + "    "))
                if is_anonymous_member:
                    lines.append(f"{indent}}}{suffix};")
                else:
                    lines.append(f"{indent}}} {member_name}{suffix};")
                return lines

    if is_anonymous_member:
        return [f"{indent}{_c_type_ref(cu_prefix, member_type)};"]
    return [f"{indent}{_c_typed_name(cu_prefix, member_type, member_name)};"]


def _emit_composite_members(
    cu_prefix: str,
    die: Any,
    inline_keys: set[str],
    indent: str,
) -> list[str]:
    lines: list[str] = []
    has_member = False
    for child in die.iter_children():
        if child.tag != "DW_TAG_member":
            continue
        has_member = True
        lines.extend(_emit_member_lines(cu_prefix, child, inline_keys, indent))

    if not has_member:
        lines.append(f"{indent}/* no members in DWARF */")
    return lines


def _emit_c_declaration_for_node(
    node_key: str,
    nodes: dict[str, tuple[str, Any]],
    inline_keys: set[str],
    typedef_inline_target_keys: set[str],
) -> str | None:
    cu_prefix, die = nodes[node_key]
    name = die_name(die)

    if die.tag == "DW_TAG_base_type":
        return None

    if die.tag == "DW_TAG_typedef":
        if name == "<anonymous>":
            return None
        target = _resolve_type_attr(die)
        if target is None:
            return None

        target_key = _die_key(cu_prefix, target)
        if target_key in typedef_inline_target_keys and _is_anonymous_composite(target):
            return _emit_typedef_inline_composite(cu_prefix, name, target, inline_keys)

        return f"typedef {_c_typed_name(cu_prefix, target, name)};"

    if die.tag == "DW_TAG_enumeration_type":
        enum_name = name if name != "<anonymous>" else _anon_c_type_name(cu_prefix, die)
        lines = [f"enum {enum_name} {{"]
        has_enumerator = False
        for child in die.iter_children():
            if child.tag != "DW_TAG_enumerator":
                continue
            has_enumerator = True
            enumerator_name = die_name(child)
            const_attr = child.attributes.get("DW_AT_const_value")
            if const_attr is None:
                lines.append(f"    {enumerator_name},")
            else:
                lines.append(f"    {enumerator_name} = {const_attr.value},")
        if not has_enumerator:
            lines.append("    /* no enumerators in DWARF */")
        lines.append("};")
        return "\n".join(lines)

    if die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
        tag_kw = _c_tag_name(die.tag)
        tag_name = name if name != "<anonymous>" else _anon_c_type_name(cu_prefix, die)
        packed_suffix = " __attribute__((packed))" if _is_packed_composite(cu_prefix, die) else ""
        lines = [f"{tag_kw} {tag_name} {{"]
        lines.extend(_emit_composite_members(cu_prefix, die, inline_keys, "    "))
        lines.append(f"}}{packed_suffix};")
        return "\n".join(lines)

    return None


def _iter_dependencies(cu_prefix: str, die: Any) -> Iterable[tuple[str, str, Any]]:
    direct = _resolve_type_attr(die)
    if direct is not None:
        yield ("type", cu_prefix, direct)

    if die.tag not in COMPOSITE_TYPE_TAGS:
        return

    if die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
        for child in die.iter_children():
            if child.tag != "DW_TAG_member":
                continue
            child_type = _resolve_type_attr(child)
            if child_type is None:
                continue
            member_name = decode_name(
                child.attributes["DW_AT_name"].value
                if "DW_AT_name" in child.attributes
                else None
            )
            yield (f"member {member_name}", cu_prefix, child_type)


def _build_dependency_graph(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> tuple[dict[str, tuple[str, Any]], dict[str, list[tuple[str, str]]], str]:
    nodes: dict[str, tuple[str, Any]] = {}
    edges: dict[str, list[tuple[str, str]]] = {}
    visited_count = 0
    status_step = 500

    def visit(current_prefix: str, die: Any) -> str:
        nonlocal visited_count
        node_key = _die_key(current_prefix, die)
        if node_key in nodes:
            return node_key

        nodes[node_key] = (current_prefix, die)
        visited_count += 1
        if visited_count % status_step == 0:
            status_cb(f"Building dependency graph: visited {visited_count} type node(s)")
        deps: list[tuple[str, str]] = []
        seen_dep_keys: set[str] = set()
        for relation, dep_prefix, dependency in _iter_dependencies(current_prefix, die):
            dep_key = _die_key(dep_prefix, dependency)
            if dep_key in seen_dep_keys:
                continue
            seen_dep_keys.add(dep_key)
            deps.append((relation, dep_key))
            if dependency.tag in GRAPH_TYPE_TAGS:
                visit(dep_prefix, dependency)

        edges[node_key] = deps
        return node_key

    root_key = visit(cu_prefix, root_die)
    status_cb(f"Dependency graph built: {len(nodes)} node(s), {sum(len(v) for v in edges.values())} edge(s)")
    return nodes, edges, root_key


def _topological_order_from_root(
    nodes: dict[str, tuple[str, Any]],
    edges: dict[str, list[tuple[str, str]]],
    root_key: str,
    status_cb: Callable[[str], None],
) -> list[str]:
    status_cb("Computing reverse dependency order")
    visited: set[str] = set()
    visiting: set[str] = set()
    order: list[str] = []

    def dfs(node_key: str) -> None:
        if node_key in visited:
            return
        if node_key in visiting:
            return

        visiting.add(node_key)
        for _, dep_key in edges.get(node_key, []):
            if dep_key in nodes:
                dfs(dep_key)
        visiting.remove(node_key)
        visited.add(node_key)
        order.append(node_key)

    dfs(root_key)
    status_cb(f"Reverse dependency order ready: {len(order)} node(s)")
    return order


def print_type_tree(cu_prefix: str, root_die: Any) -> None:
    visited: set[str] = set()

    def recurse(current_prefix: str, die: Any, indent: int) -> None:
        key = _die_key(current_prefix, die)
        marker = " " * indent
        if key in visited:
            print(f"{marker}{_format_die(current_prefix, die)} (already shown)")
            return

        visited.add(key)
        print(f"{marker}{_format_die(current_prefix, die)}")

        for relation, dep_prefix, dependency in _iter_dependencies(current_prefix, die):
            relation_marker = " " * (indent + 2)
            print(f"{relation_marker}{relation} -> {_format_die(dep_prefix, dependency)}")
            if dependency.tag in TRAVERSABLE_TYPE_TAGS:
                recurse(dep_prefix, dependency, indent + 4)

    recurse(cu_prefix, root_die, 0)


def find_named_type(
    dwarf_infos: list[tuple[str, DWARFInfo]],
    requested_type: str,
    status_cb: Callable[[str], None],
) -> tuple[str, Any, bool] | None:
    normalized_requested = re.sub(r"_(\d+)(?=_|$)", "", requested_type)
    normalized_match: tuple[str, Any] | None = None
    status_cb(f"Searching for type: {requested_type}")

    for cu_prefix, dwarf_info in dwarf_infos:
        cu_list = list(dwarf_info.iter_CUs())
        total_cus = len(cu_list)
        last_percent = -1
        status_cb(f"Scanning {total_cus} compile unit(s)")
        for index, cu in enumerate(cu_list, start=1):
            percent = int((index * 100) / total_cus) if total_cus > 0 else 100
            if percent == 100 or percent >= last_percent + 10:
                print(f"Searching type in DWARF: {percent}%", file=sys.stderr)
                last_percent = percent
            for die in cu.iter_DIEs():
                if die.tag not in TYPE_TAGS:
                    continue
                if "DW_AT_name" not in die.attributes:
                    continue
                current_name = decode_name(die.attributes["DW_AT_name"].value)
                if current_name == requested_type:
                    status_cb(f"Exact type match found in CU {index}/{total_cus}")
                    return (cu_prefix, die, False)

                normalized_die_name = re.sub(r"_(\d+)(?=_|$)", "", current_name)
                if normalized_match is None and normalized_die_name == normalized_requested:
                    normalized_match = (cu_prefix, die)

    if normalized_match is not None:
        status_cb("Using normalized fallback type match")
        return (normalized_match[0], normalized_match[1], True)
    status_cb("Type not found after full DWARF scan")
    return None


def render_reverse_dependencies(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> str:
    status_cb("Generating C-style reverse dependency output")
    nodes, edges, root_key = _build_dependency_graph(cu_prefix, root_die, status_cb)
    order = _topological_order_from_root(nodes, edges, root_key, status_cb)
    inline_keys = _inline_anonymous_keys(nodes, edges, root_key)
    typedef_inline_target_keys = _typedef_inline_target_keys(nodes, edges)

    lines = [
        "/* kdk2h: https://github.com/fozog/kdk2h */",
    ]
    emitted_count = 0
    for node_key in order:
        if node_key in inline_keys or node_key in typedef_inline_target_keys:
            continue
        declaration = _emit_c_declaration_for_node(
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
) -> str:
    status_cb("Generating global C-style output for all named types")
    lines = [
        "/* kdk2h: https://github.com/fozog/kdk2h */",
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
                if die.tag not in TYPE_TAGS:
                    continue
                if "DW_AT_name" not in die.attributes:
                    continue
                if decode_name(die.attributes["DW_AT_name"].value) == "<anonymous>":
                    continue
                named_roots.append((cu_prefix, die))

    status_cb(f"Found {len(named_roots)} named root type(s)")

    for cu_prefix, root_die in named_roots:
        root_count += 1
        if root_count % 500 == 0:
            status_cb(f"Processing root type {root_count}/{len(named_roots)}")

        nodes, edges, root_key = _build_dependency_graph(cu_prefix, root_die, status_cb)
        order = _topological_order_from_root(nodes, edges, root_key, status_cb)
        inline_keys = _inline_anonymous_keys(nodes, edges, root_key)
        typedef_inline_target_keys = _typedef_inline_target_keys(nodes, edges)

        for node_key in order:
            if node_key in emitted_node_keys:
                continue
            if node_key in inline_keys or node_key in typedef_inline_target_keys:
                continue

            declaration = _emit_c_declaration_for_node(
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
