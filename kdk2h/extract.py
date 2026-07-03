from __future__ import annotations

import argparse
import os
import plistlib
import re
import subprocess
import sys
from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, TypeVar

from elftools.common.exceptions import ELFError
from elftools.dwarf.dwarfinfo import DWARFInfo, DebugSectionDescriptor, DwarfConfig
from elftools.elf.elffile import ELFFile

try:
    from macholib.MachO import MachO  # type: ignore[reportMissingImports]
    from macholib import mach_o as mach_o_consts  # type: ignore[reportMissingImports]
except ImportError:
    MachO = None
    mach_o_consts = None

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

T = TypeVar("T")

MACHO_TO_DWARFINFO_SECTIONS = {
    "__debug_info": "debug_info_sec",
    "__debug_aranges": "debug_aranges_sec",
    "__debug_abbrev": "debug_abbrev_sec",
    "__debug_frame": "debug_frame_sec",
    "__eh_frame": "eh_frame_sec",
    "__debug_str": "debug_str_sec",
    "__debug_loc": "debug_loc_sec",
    "__debug_ranges": "debug_ranges_sec",
    "__debug_line": "debug_line_sec",
    "__debug_pubtypes": "debug_pubtypes_sec",
    "__debug_pubnames": "debug_pubnames_sec",
    "__debug_addr": "debug_addr_sec",
    "__debug_str_offs": "debug_str_offsets_sec",
    "__debug_line_str": "debug_line_str_sec",
    "__debug_loclists": "debug_loclists_sec",
    "__debug_rnglists": "debug_rnglists_sec",
    "__debug_sup": "debug_sup_sec",
    "__gnu_debugaltlink": "gnu_debugaltlink_sec",
    "__debug_types": "debug_types_sec",
}


def _decode_name(raw_name: object) -> str:
    if raw_name is None:
        return "<anonymous>"
    if isinstance(raw_name, bytes):
        return raw_name.decode("utf-8", errors="replace")
    return str(raw_name)


def _die_name(die: Any) -> str:
    name_attr = die.attributes.get("DW_AT_name")
    return _decode_name(name_attr.value if name_attr else None)


def _iter_declared_types_from_dwarf_info(
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
            name = _decode_name(name_attr.value if name_attr else None)
            yield (cu_offset, die.tag, name)


def _status(message: str) -> None:
    print(f"[status] {message}", file=sys.stderr)


def _resolve_input_path(*, kdk_file: str | None, kdk_tag: str | None) -> Path:
    if kdk_file is not None:
        return Path(kdk_file)

    if kdk_tag is None:
        raise ValueError("Either --kdk-file or --kdk must be provided.")

    if "@" not in kdk_tag:
        raise ValueError("Invalid --kdk format. Expected <platform>@<version>.")

    platform, version = kdk_tag.split("@", 1)
    platform = platform.strip()
    version = version.strip()
    if not platform or not version:
        raise ValueError("Invalid --kdk format. Expected non-empty <platform>@<version>.")

    kdk_root = Path("/Library/Developer/KDKs")
    pattern = (
        f"KDK_{version}_*.kdk/System/Library/Kernels/"
        f"kernel.kasan.{platform}.dSYM/Contents/Resources/DWARF/kernel.kasan.{platform}"
    )
    matches = sorted(kdk_root.glob(pattern))
    if not matches:
        raise ValueError(
            f"No KDK file matched tag {kdk_tag} with pattern {kdk_root / pattern}"
        )
    if len(matches) > 1:
        preview = ", ".join(str(path) for path in matches[:5])
        raise ValueError(
            "Multiple KDK files matched tag "
            f"{kdk_tag}. Please use --kdk-file. Matches: {preview}"
        )
    return matches[0]


def _decode_platform_name(raw: bytes) -> str:
    return raw.decode("ascii", errors="ignore").rstrip("\x00")


def _get_current_platform_code() -> str | None:
    try:
        output = subprocess.check_output(
            ["ioreg", "-a", "-rd1", "-c", "IOPlatformExpertDevice"],
            stderr=subprocess.DEVNULL,
        )
        root = plistlib.loads(output)
        if isinstance(root, list) and root:
            first = root[0]
            if isinstance(first, dict):
                raw = first.get("platform-name")
                if isinstance(raw, bytes):
                    code = _decode_platform_name(raw)
                    if code:
                        return code
    except Exception:
        pass
    return None


def _get_running_macos_version() -> str | None:
    try:
        version = subprocess.check_output(
            ["sw_vers", "-productVersion"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return version or None
    except Exception:
        return None


def _extract_kdk_tag_from_path(path: Path) -> str | None:
    path_str = str(path)
    version_match = re.search(r"/KDK_(?P<version>[^_/]+)_.*?\.kdk/", path_str)
    platform_match = re.search(r"/kernel\.kasan\.(?P<platform>[^/]+)$", path_str)
    if version_match is None or platform_match is None:
        return None
    version = version_match.group("version")
    platform = platform_match.group("platform")
    return f"{platform}@{version}"


def _resolve_effective_input_path(
    *,
    kdk_file: str | None,
    kdk_tag: str | None,
) -> tuple[Path, str | None]:
    if kdk_file is not None or kdk_tag is not None:
        resolved = _resolve_input_path(kdk_file=kdk_file, kdk_tag=kdk_tag)
        if kdk_tag is not None:
            return (resolved, kdk_tag.strip())
        return (resolved, _extract_kdk_tag_from_path(resolved))

    platform = _get_current_platform_code()
    version = _get_running_macos_version()
    if platform is None or version is None:
        raise ValueError(
            "Unable to auto-detect local platform/version. Please provide --kdk or --kdk-file."
        )

    implicit_tag = f"{platform}@{version}"
    _status(f"No --kdk/--kdk-file provided, using local system tag: {implicit_tag}")
    resolved = _resolve_input_path(kdk_file=None, kdk_tag=implicit_tag)
    return (resolved, implicit_tag)


def _run_with_dwarf_infos(
    dwarf_path: Path,
    visitor: Callable[[list[tuple[str, DWARFInfo]]], T],
) -> T:
    try:
        with dwarf_path.open("rb") as stream:
            elf = ELFFile(stream)
            if not elf.has_dwarf_info():
                raise ValueError("No DWARF sections were found in this ELF file.")
            return visitor([("", elf.get_dwarf_info())])
    except ELFError:
        pass

    if MachO is None or mach_o_consts is None:
        raise ValueError("Mach-O support requires the 'macholib' package.")

    macho = MachO(str(dwarf_path))
    dwarf_infos: list[tuple[str, DWARFInfo]] = []
    #_status(f"Mach-O detected, scanning {len(macho.headers)} architecture slice(s)")
    for index, header in enumerate(macho.headers):
        _status(f"Loading DWARF sections for slice {index + 1}/{len(macho.headers)}")
        dwarf_info = _build_macho_dwarf_info(dwarf_path, header)
        if dwarf_info is None:
            continue
        has_multiple_archs = len(macho.headers) > 1
        arch_name = _cpu_arch_name(header.header.cputype)
        cu_prefix = f"{arch_name}[{index}]:" if has_multiple_archs else ""
        dwarf_infos.append((cu_prefix, dwarf_info))

    if not dwarf_infos:
        raise ValueError("No DWARF sections were found in this Mach-O file.")

    return visitor(dwarf_infos)


def _die_key(cu_prefix: str, die: Any) -> str:
    return f"{cu_prefix}{die.cu.cu_offset:#x}:{die.offset:#x}"


def _format_die(cu_prefix: str, die: Any) -> str:
    name = _die_name(die)
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
    name = _die_name(die)

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


def _emit_c_declaration(cu_prefix: str, die: Any) -> str | None:
    name = _die_name(die)

    if die.tag == "DW_TAG_base_type":
        return None

    if die.tag == "DW_TAG_typedef":
        if name == "<anonymous>":
            return None
        target = _resolve_type_attr(die)
        if target is None:
            return None
        return f"typedef {_c_typed_name(cu_prefix, target, name)};"

    if die.tag == "DW_TAG_enumeration_type":
        enum_name = name if name != "<anonymous>" else _anon_c_type_name(cu_prefix, die)
        lines = [f"enum {enum_name} {{"]
        has_enumerator = False
        for child in die.iter_children():
            if child.tag != "DW_TAG_enumerator":
                continue
            has_enumerator = True
            enumerator_name = _die_name(child)
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
        lines = [f"{tag_kw} {tag_name} {{"]
        has_member = False
        for child in die.iter_children():
            if child.tag != "DW_TAG_member":
                continue
            has_member = True
            member_name = _die_name(child)
            member_type = _resolve_type_attr(child)
            if member_type is None:
                lines.append(f"    /* unresolved type */ int {member_name};")
                continue
            lines.append(f"    {_c_typed_name(cu_prefix, member_type, member_name)};")
        if not has_member:
            lines.append("    /* no members in DWARF */")
        lines.append("};")
        return "\n".join(lines)

    return None


def _is_anonymous_composite(die: Any) -> bool:
    return die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"} and _die_name(die) == "<anonymous>"


def _emit_typedef_inline_composite(
    cu_prefix: str,
    typedef_name: str,
    target_die: Any,
    inline_keys: set[str],
) -> str:
    tag_kw = _c_tag_name(target_die.tag)
    lines = [f"typedef {tag_kw} {{"]
    lines.extend(_emit_composite_members(cu_prefix, target_die, inline_keys, "    "))
    lines.append(f"}} {typedef_name};")
    return "\n".join(lines)


def _typedef_inline_target_keys(
    nodes: dict[str, tuple[str, Any]],
    edges: dict[str, list[tuple[str, str]]],
) -> set[str]:
    incoming = _incoming_edges(edges)
    inline_target_keys: set[str] = set()

    for typedef_key, (cu_prefix, die) in nodes.items():
        if die.tag != "DW_TAG_typedef":
            continue
        if _die_name(die) == "<anonymous>":
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


def _incoming_edges(
    edges: dict[str, list[tuple[str, str]]],
) -> dict[str, list[tuple[str, str]]]:
    incoming: dict[str, list[tuple[str, str]]] = {}
    for src_key, deps in edges.items():
        for relation, dep_key in deps:
            incoming.setdefault(dep_key, []).append((src_key, relation))
    return incoming


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
    member_name = _die_name(member_die)
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

    # Inline anonymous composite used as the element type of a member array:
    # struct { ... } field[N]; / union { ... } field[N];
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
    name = _die_name(die)

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
            return _emit_typedef_inline_composite(
                cu_prefix,
                name,
                target,
                inline_keys,
            )

        return f"typedef {_c_typed_name(cu_prefix, target, name)};"

    if die.tag == "DW_TAG_enumeration_type":
        enum_name = name if name != "<anonymous>" else _anon_c_type_name(cu_prefix, die)
        lines = [f"enum {enum_name} {{"]
        has_enumerator = False
        for child in die.iter_children():
            if child.tag != "DW_TAG_enumerator":
                continue
            has_enumerator = True
            enumerator_name = _die_name(child)
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
        lines = [f"{tag_kw} {tag_name} {{"]
        lines.extend(_emit_composite_members(cu_prefix, die, inline_keys, "    "))
        lines.append("};")
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
            member_name = _decode_name(
                child.attributes["DW_AT_name"].value
                if "DW_AT_name" in child.attributes
                else None
            )
            yield (f"member {member_name}", cu_prefix, child_type)


def _build_dependency_graph(
    cu_prefix: str,
    root_die: Any,
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
            _status(f"Building dependency graph: visited {visited_count} type node(s)")
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
    _status(f"Dependency graph built: {len(nodes)} node(s), {sum(len(v) for v in edges.values())} edge(s)")
    return nodes, edges, root_key


def _topological_order_from_root(
    nodes: dict[str, tuple[str, Any]],
    edges: dict[str, list[tuple[str, str]]],
    root_key: str,
) -> list[str]:
    _status("Computing reverse dependency order")
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
    _status(f"Reverse dependency order ready: {len(order)} node(s)")
    return order


def _render_reverse_dependencies(cu_prefix: str, root_die: Any) -> str:
    _status("Generating C-style reverse dependency output")
    nodes, edges, root_key = _build_dependency_graph(cu_prefix, root_die)
    order = _topological_order_from_root(nodes, edges, root_key)
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
            _status(f"Printed {emitted_count} declaration(s)")
    _status(f"C-style output complete: {emitted_count} declaration(s)")
    return "\n".join(lines).rstrip() + "\n"


def _print_type_tree(cu_prefix: str, root_die: Any) -> None:
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


def _find_named_type(
    dwarf_infos: list[tuple[str, DWARFInfo]],
    requested_type: str,
) -> tuple[str, Any, bool] | None:
    normalized_requested = re.sub(r"_(\d+)(?=_|$)", "", requested_type)
    normalized_match: tuple[str, Any] | None = None
    _status(f"Searching for type: {requested_type}")

    for cu_prefix, dwarf_info in dwarf_infos:
        cu_list = list(dwarf_info.iter_CUs())
        total_cus = len(cu_list)
        last_percent = -1
        _status(f"Scanning {total_cus} compile unit(s)")
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
                die_name = _decode_name(die.attributes["DW_AT_name"].value)
                if die_name == requested_type:
                    _status(f"Exact type match found in CU {index}/{total_cus}")
                    return (cu_prefix, die, False)

                normalized_die_name = re.sub(r"_(\d+)(?=_|$)", "", die_name)
                if normalized_match is None and normalized_die_name == normalized_requested:
                    normalized_match = (cu_prefix, die)

    if normalized_match is not None:
        _status("Using normalized fallback type match")
        return (normalized_match[0], normalized_match[1], True)
    _status("Type not found after full DWARF scan")
    return None


def _cpu_arch_name(cputype: int) -> str:
    if mach_o_consts is not None:
        raw_name = mach_o_consts.CPU_TYPE_NAMES.get(cputype)
        if raw_name:
            return str(raw_name).lower()
    return f"cpu_{cputype}"


def _build_macho_dwarf_info(dwarf_path: Path, header: Any) -> DWARFInfo | None:
    if mach_o_consts is None:
        return None

    section_meta: list[tuple[str, int, int]] = []
    for cmd, cmd_data, section_data in header.commands:
        if cmd.cmd not in (mach_o_consts.LC_SEGMENT, mach_o_consts.LC_SEGMENT_64):
            continue
        segname = cmd_data.segname.rstrip(b"\x00").decode("ascii", errors="ignore")
        if segname != "__DWARF":
            continue
        for section in section_data:
            section_name = section.sectname.rstrip(b"\x00").decode(
                "ascii",
                errors="ignore",
            )
            section_meta.append((section_name, section.offset, section.size))

    section_bytes: dict[str, bytes] = {}
    with dwarf_path.open("rb") as stream:
        for section_name, section_offset, section_size in section_meta:
            stream.seek(section_offset)
            section_bytes[section_name] = stream.read(section_size)

    if "__debug_info" not in section_bytes:
        return None

    dwarf_sections: dict[str, DebugSectionDescriptor | None] = {
        value: None for value in MACHO_TO_DWARFINFO_SECTIONS.values()
    }
    for section_name, dwarf_kwarg in MACHO_TO_DWARFINFO_SECTIONS.items():
        payload = section_bytes.get(section_name)
        if payload is None:
            continue
        dwarf_sections[dwarf_kwarg] = DebugSectionDescriptor(
            stream=BytesIO(payload),
            name=section_name,
            global_offset=None,
            size=len(payload),
            address=0,
        )

    config = DwarfConfig(
        little_endian=(header.endian == "<"),
        machine_arch=_cpu_arch_name(header.header.cputype),
        default_address_size=8 if header.header.__class__.__name__.endswith("_64") else 4,
    )
    return DWARFInfo(config=config, **dwarf_sections)


def _iter_declared_types_from_elf(dwarf_path: Path) -> Iterable[tuple[str, str, str]]:
    with dwarf_path.open("rb") as stream:
        elf = ELFFile(stream)
        if not elf.has_dwarf_info():
            raise ValueError("No DWARF sections were found in this ELF file.")
        yield from _iter_declared_types_from_dwarf_info(elf.get_dwarf_info())


def _iter_declared_types_from_macho(dwarf_path: Path) -> Iterable[tuple[str, str, str]]:
    if MachO is None or mach_o_consts is None:
        raise ValueError("Mach-O support requires the 'macholib' package.")

    macho = MachO(str(dwarf_path))
    found_dwarf = False
    for index, header in enumerate(macho.headers):
        dwarf_info = _build_macho_dwarf_info(dwarf_path, header)
        if dwarf_info is None:
            continue
        found_dwarf = True
        has_multiple_archs = len(macho.headers) > 1
        arch_name = _cpu_arch_name(header.header.cputype)
        cu_prefix = f"{arch_name}[{index}]:" if has_multiple_archs else ""
        yield from _iter_declared_types_from_dwarf_info(dwarf_info, cu_prefix=cu_prefix)

    if not found_dwarf:
        raise ValueError("No DWARF sections were found in this Mach-O file.")


def iter_declared_types(dwarf_path: Path) -> Iterable[tuple[str, str, str]]:
    def collect(dwarf_infos: list[tuple[str, DWARFInfo]]) -> list[tuple[str, str, str]]:
        rows: list[tuple[str, str, str]] = []
        for cu_prefix, dwarf_info in dwarf_infos:
            rows.extend(_iter_declared_types_from_dwarf_info(dwarf_info, cu_prefix=cu_prefix))
        return rows

    try:
        rows = _run_with_dwarf_infos(dwarf_path, collect)
        yield from rows
    except Exception as exc:
        raise ValueError(
            "Input is neither a valid ELF file nor a supported Mach-O file with DWARF sections."
        ) from exc


def add_extract_arguments(parser: argparse.ArgumentParser) -> None:
    source_group = parser.add_mutually_exclusive_group(required=False)
    source_group.add_argument(
        "--kdk-file",
        type=str,
        help="Direct path to the ELF or Mach-O file containing DWARF info.",
    )
    source_group.add_argument(
        "--kdk",
        type=str,
        help=(
            "KDK tag in the form <platform>@<version>. "
            "If neither --kdk nor --kdk-file is provided, local platform/version are auto-detected."
        ),
    )
    parser.add_argument(
        "type_name",
        nargs="?",
        help="Optional type name to print with recursive dependencies.",
    )
    parser.add_argument(
        "--with-dependency-tree",
        action="store_true",
        help="Also print the detailed dependency tree before reverse-order C output.",
    )
    parser.add_argument(
        "--header",
        type=str,
        help="Write extracted C declarations to the given header file.",
    )


def run_extract_command(args: argparse.Namespace) -> int:

    if args.header and not args.type_name:
        print("Error: --header requires type_name.")
        return 1

    try:
        dwarf_file, effective_kdk_tag = _resolve_effective_input_path(
            kdk_file=args.kdk_file,
            kdk_tag=args.kdk,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if not dwarf_file.exists():
        print(f"Error: file not found: {dwarf_file}")
        return 1

    try:
        if args.type_name:
            def print_named_type(dwarf_infos: list[tuple[str, DWARFInfo]]) -> bool:
                found = _find_named_type(dwarf_infos, args.type_name)
                if found is None:
                    return False
                cu_prefix, die, is_approximate = found
                if is_approximate:
                    print(
                        f"Note: no exact match for {args.type_name}; using {_decode_name(die.attributes['DW_AT_name'].value)}"
                    )
                if args.with_dependency_tree:
                    print("Dependency tree:")
                    _print_type_tree(cu_prefix, die)
                    print()

                c_declarations = _render_reverse_dependencies(cu_prefix, die)
                if args.header:
                    header_path = Path(args.header)
                    header_path.parent.mkdir(parents=True, exist_ok=True)
                    kdk_label = effective_kdk_tag or "unknown"
                    header_prefix = f"/* extracted from KDK {kdk_label} */\n"
                    header_path.write_text(header_prefix + c_declarations, encoding="utf-8")
                    _status(f"C declarations written to: {header_path}")
                else:
                    print("/* --------------------------- */")
                    print(c_declarations, end="")
                    print("/* --------------------------- */")
                return True

            match_found = _run_with_dwarf_infos(dwarf_file, print_named_type)
            if not match_found:
                print(f"Error: type not found: {args.type_name}")
                return 3
        else:
            for cu_offset, tag, name in iter_declared_types(dwarf_file):
                print(f"{cu_offset} {tag} {name}")
    except BrokenPipeError:
        # Avoid noisy shutdown traceback when output is piped (for example, to head).
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 0
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kdk2h extract",
        description="Print all declared DWARF types found in an ELF or Mach-O file.",
    )
    add_extract_arguments(parser)
    args = parser.parse_args(argv)
    return run_extract_command(args)
