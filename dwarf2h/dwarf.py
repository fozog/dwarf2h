from __future__ import annotations

import html
import re
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

VENDOR_TAG_NAMES: dict[int, str] = {
    0x4300: "DW_TAG_APPLE_ptrauth_type",
}

DW_TAG_APPLE_PTRAUTH_TYPE = 0x4300
DW_AT_APPLE_PTRAUTH_KEY = 0x3E04
DW_AT_APPLE_PTRAUTH_ADDR_DISCRIMINATED = 0x3E05
DW_AT_APPLE_PTRAUTH_EXTRA_DISCRIMINATOR = 0x3E06

PTRAUTH_TAG_NAMES = {
    "DW_TAG_APPLE_ptrauth_type",
    "DW_TAG_LLVM_ptrauth_type",
}


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


def _tag_name(tag: object) -> str:
    if isinstance(tag, str):
        return tag
    if isinstance(tag, int):
        known = VENDOR_TAG_NAMES.get(tag)
        if known is not None:
            return known
        return f"DW_TAG_0x{tag:x}"
    return str(tag)


def _attr_value(die: Any, attr_name: str, attr_code: int) -> Any | None:
    attr = die.attributes.get(attr_name)
    if attr is None:
        attr = die.attributes.get(attr_code)
    if attr is None:
        return None
    return getattr(attr, "value", None)


def _is_ptrauth_type(tag: object) -> bool:
    if tag == DW_TAG_APPLE_PTRAUTH_TYPE:
        return True
    return tag in PTRAUTH_TAG_NAMES


def _ptrauth_annotation(die: Any) -> str | None:
    if not _is_ptrauth_type(die.tag):
        return None

    key = _attr_value(die, "DW_AT_APPLE_ptrauth_key", DW_AT_APPLE_PTRAUTH_KEY)
    addr_disc = _attr_value(
        die,
        "DW_AT_APPLE_ptrauth_addr_discriminated",
        DW_AT_APPLE_PTRAUTH_ADDR_DISCRIMINATED,
    )
    if addr_disc is None:
        addr_disc = _attr_value(
            die,
            "DW_AT_APPLE_ptrauth_address_discriminated",
            DW_AT_APPLE_PTRAUTH_ADDR_DISCRIMINATED,
        )
    extra_disc = _attr_value(
        die,
        "DW_AT_APPLE_ptrauth_extra_discriminator",
        DW_AT_APPLE_PTRAUTH_EXTRA_DISCRIMINATOR,
    )

    if not isinstance(key, int):
        return None

    addr_disc_bit = 1 if bool(addr_disc) else 0
    if not isinstance(extra_disc, int):
        extra_disc = 0

    return f"/* __ptrauth(0x{key:02x}, {addr_disc_bit}, 0x{extra_disc:x}) */"


def _format_die(cu_prefix: str, die: Any) -> str:
    name = die_name(die)
    return f"{_tag_name(die.tag)} {name} [{_die_key(cu_prefix, die)}]"


def _resolve_type_attr(die: Any) -> Any | None:
    if "DW_AT_type" not in die.attributes:
        return None
    try:
        return die.get_DIE_from_attribute("DW_AT_type")
    except Exception:
        return None


def _is_traversable_type(die: Any) -> bool:
    if die.tag in TRAVERSABLE_TYPE_TAGS:
        return True
    return _resolve_type_attr(die) is not None


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
    if die.tag == "DW_TAG_atomic_type":
        target = _resolve_type_attr(die)
        if target is None:
            return "_Atomic(void)"
        return f"_Atomic({_c_type_ref(cu_prefix, target)})"
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

    # Handle vendor/extension wrappers that carry an underlying DW_AT_type.
    target = _resolve_type_attr(die)
    if target is not None and target is not die:
        return _c_type_ref(cu_prefix, target)

    return "void"


def _resolve_subroutine_target(die: Any) -> Any | None:
    current = die
    seen: set[int] = set()
    while current is not None:
        ident = id(current)
        if ident in seen:
            return None
        seen.add(ident)

        if current.tag == "DW_TAG_subroutine_type":
            return current

        if _is_ptrauth_type(current.tag):
            current = _resolve_type_attr(current)
            continue

        if current.tag in {"DW_TAG_typedef", "DW_TAG_const_type", "DW_TAG_volatile_type"}:
            current = _resolve_type_attr(current)
            continue

        return None
    return None


def _unwrap_ptrauth_type(die: Any) -> tuple[Any | None, str | None]:
    current = die
    annotation: str | None = None
    seen: set[int] = set()
    while current is not None and _is_ptrauth_type(current.tag):
        ident = id(current)
        if ident in seen:
            return (None, None)
        seen.add(ident)

        current_annotation = _ptrauth_annotation(current)
        if current_annotation is not None:
            annotation = current_annotation
        current = _resolve_type_attr(current)
    return (current, annotation)


def _subroutine_signature(cu_prefix: str, subroutine_die: Any) -> tuple[str, str]:
    return_type_die = _resolve_type_attr(subroutine_die)
    if return_type_die is None:
        return_type = "void"
    else:
        return_type = _c_type_ref(cu_prefix, return_type_die)

    params: list[str] = []
    variadic = False
    for child in subroutine_die.iter_children():
        if child.tag == "DW_TAG_formal_parameter":
            param_type = _resolve_type_attr(child)
            if param_type is None:
                params.append("void")
            else:
                params.append(_c_type_ref(cu_prefix, param_type))
        elif child.tag == "DW_TAG_unspecified_parameters":
            variadic = True

    if not params and not variadic:
        param_list = "void"
    else:
        param_list = ", ".join(params)
        if variadic:
            param_list = f"{param_list}, ..." if param_list else "..."

    return (return_type, param_list)


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
    type_annotation = ""
    if base_type_die is None:
        base_type = "void"
    else:
        base_type_die, ptrauth_annotation = _unwrap_ptrauth_type(base_type_die)
        if ptrauth_annotation is not None:
            type_annotation = f" {ptrauth_annotation}"
        annotation = _ptrauth_annotation(base_type_die)
        target_for_ref = _resolve_type_attr(base_type_die) if annotation is not None else base_type_die
        if target_for_ref is None:
            base_type = "void"
        else:
            base_type = _c_type_ref(cu_prefix, target_for_ref)
        if annotation is not None:
            type_annotation = f" {annotation}"

    dim_suffix = "".join(f"[{dim}]" for dim in dimensions)

    if base_type_die is not None and base_type_die.tag == "DW_TAG_pointer_type":
        pointee, ptrauth_annotation = _unwrap_ptrauth_type(_resolve_type_attr(base_type_die))
        subroutine_die = _resolve_subroutine_target(pointee) if pointee is not None else None
        if subroutine_die is not None:
            return_type, params = _subroutine_signature(cu_prefix, subroutine_die)
            decl_name = f"{name}{dim_suffix}"
            pointer_prefix = "*"
            if ptrauth_annotation is None:
                ptrauth_annotation = type_annotation.strip() or None
            if ptrauth_annotation is not None:
                pointer_prefix = f"* {ptrauth_annotation} "
            elif type_annotation:
                pointer_prefix = f"*{type_annotation} "
            return f"{return_type} ({pointer_prefix}{decl_name})({params})"

    return f"{base_type}{type_annotation} {name}{dim_suffix}"


def _is_anonymous_composite(die: Any) -> bool:
    return die.tag in {
        "DW_TAG_structure_type",
        "DW_TAG_union_type",
        "DW_TAG_enumeration_type",
    } and die_name(die) == "<anonymous>"


def _is_anonymous_typedef_inline_target(die: Any) -> bool:
    return die.tag in {
        "DW_TAG_structure_type",
        "DW_TAG_union_type",
        "DW_TAG_enumeration_type",
    } and die_name(die) == "<anonymous>"


def _emit_typedef_inline_composite(
    cu_prefix: str,
    typedef_name: str,
    target_die: Any,
    inline_keys: set[str],
) -> str:
    if target_die.tag == "DW_TAG_enumeration_type":
        lines = ["typedef enum {"]
        has_enumerator = False
        for child in target_die.iter_children():
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
        lines.append(f"}} {typedef_name};")
        return "\n".join(lines)

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
        if target is None or not _is_anonymous_typedef_inline_target(target):
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

    bit_size = _attr_to_int(member_die.attributes.get("DW_AT_bit_size"))
    member_type_key = _die_key(cu_prefix, member_type)

    if (
        member_type_key in inline_keys
        and member_type.tag == "DW_TAG_enumeration_type"
    ):
        lines = [f"{indent}enum {{"]
        has_enumerator = False
        for child in member_type.iter_children():
            if child.tag != "DW_TAG_enumerator":
                continue
            has_enumerator = True
            enumerator_name = die_name(child)
            const_attr = child.attributes.get("DW_AT_const_value")
            if const_attr is None:
                lines.append(f"{indent}    {enumerator_name},")
            else:
                lines.append(f"{indent}    {enumerator_name} = {const_attr.value},")
        if not has_enumerator:
            lines.append(f"{indent}    /* no enumerators in DWARF */")

        if is_anonymous_member:
            if bit_size is not None and bit_size >= 0:
                lines.append(f"{indent}}} : {bit_size};")
            else:
                lines.append(f"{indent}}};")
            return lines

        if bit_size is not None and bit_size >= 0:
            lines.append(f"{indent}}} {member_name} : {bit_size};")
        else:
            lines.append(f"{indent}}} {member_name};")
        return lines

    if bit_size is not None and bit_size >= 0:
        if is_anonymous_member:
            return [f"{indent}{_c_type_ref(cu_prefix, member_type)} : {bit_size};"]
        return [f"{indent}{_c_typed_name(cu_prefix, member_type, member_name)} : {bit_size};"]

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
        if target_key in typedef_inline_target_keys and _is_anonymous_typedef_inline_target(target):
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
        # A pointer to struct/union can be declared with an incomplete tag type,
        # so this dependency should not force full struct/union definition ordering.
        if not (
            die.tag == "DW_TAG_pointer_type"
            and direct.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}
        ):
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
            if dependency.tag in GRAPH_TYPE_TAGS or _resolve_type_attr(dependency) is not None:
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


def _collect_render_context(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> tuple[
    dict[str, tuple[str, Any]],
    dict[str, list[tuple[str, str]]],
    list[str],
    set[str],
    set[str],
    str,
]:
    nodes, edges, root_key = _build_dependency_graph(cu_prefix, root_die, status_cb)
    order = _topological_order_from_root(nodes, edges, root_key, status_cb)
    inline_keys = _inline_anonymous_keys(nodes, edges, root_key)
    typedef_inline_target_keys = _typedef_inline_target_keys(nodes, edges)
    return nodes, edges, order, inline_keys, typedef_inline_target_keys, root_key


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
            current = _resolve_type_attr(current)
            continue

        return None

    return None


def _graphviz_member_pointer_target(member_type: Any) -> Any | None:
    current = member_type
    seen: set[int] = set()
    while current is not None:
        marker = id(current)
        if marker in seen:
            return None
        seen.add(marker)

        if current.tag in {"DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_atomic_type", "DW_TAG_typedef"}:
            current = _resolve_type_attr(current)
            continue

        if current.tag == "DW_TAG_pointer_type":
            return _graphviz_declarative_target(_resolve_type_attr(current))

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
            current = _resolve_type_attr(current)
            continue

        if current.tag == "DW_TAG_array_type":
            base_type, _ = _unwrap_array_type(current)
            current = base_type
            continue

        if current.tag == "DW_TAG_pointer_type":
            return _graphviz_declarative_target(_resolve_type_attr(current))

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
    if die_name(member_type) != "<anonymous>":
        return False
    return _die_key(cu_prefix, member_type) not in included_set


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

    member_name = die_name(member_die)
    member_type = _resolve_type_attr(member_die)
    port_base = _dot_port_escape(f"{port_prefix}_{row_index}_{member_name}")

    if _graphviz_is_inline_anonymous_composite(cu_prefix, member_type, included_set):
        tag_kw = _c_tag_name(member_type.tag)
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
    rendered_lines = _emit_member_lines(cu_prefix, member_die, member_inline_keys, "")
    row_text = "<br align=\"left\"/>".join(
        _graphviz_html_preserve_indent(line.rstrip()) for line in rendered_lines if line.strip()
    )
    if not row_text:
        row_text = html.escape("/* unresolved member */")

    rows.append((port_base, row_text))

    if member_type is not None:
        target_die = _graphviz_member_link_target(member_type)
        if target_die is not None:
            target_key = _die_key(cu_prefix, target_die)
            if target_key in linkable_targets:
                links.append((port_base, target_key))

    return rows, links


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
            visit_type(_resolve_type_attr(type_die))
            return

        if type_die.tag == "DW_TAG_array_type":
            base_type, _ = _unwrap_array_type(type_die)
            visit_type(base_type)
            return

        if type_die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
            if die_name(type_die) == "<anonymous>":
                inline_keys.add(_die_key(cu_prefix, type_die))

            if type_die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type"}:
                for child in type_die.iter_children():
                    if child.tag != "DW_TAG_member":
                        continue
                    visit_type(_resolve_type_attr(child))

    visit_type(root_die)
    return inline_keys


def _graphviz_should_include_node(node_key: str, nodes: dict[str, tuple[str, Any]]) -> bool:
    _, die = nodes[node_key]
    if die.tag in {"DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_enumeration_type"}:
        if die_name(die) == "<anonymous>":
            return False
    return True


def _graphviz_node_header(cu_prefix: str, die: Any, name: str) -> tuple[str, str]:
    if die.tag == "DW_TAG_structure_type":
        suffix = " (packed)" if _is_packed_composite(cu_prefix, die) else ""
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
            enum_name = die_name(child)
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
        typedef_name = die_name(die)
        target = _resolve_type_attr(die)
        if (
            typedef_name == "<anonymous>"
            or target is None
            or not _is_anonymous_typedef_inline_target(target)
            or _die_key(cu_prefix, target) in included_set
        ):
            continue

        nested_inline_keys = _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix, target)
        declaration = _emit_typedef_inline_composite(
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
        target_key = _die_key(cu_prefix, target)
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
        name = die_name(die)
        if name == "<anonymous>":
            name = _anon_c_type_name(cu_prefix, die)
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
                typedef_name = die_name(die)
                target = _resolve_type_attr(die)
                if (
                    typedef_name != "<anonymous>"
                    and target is not None
                    and _is_anonymous_typedef_inline_target(target)
                    and _die_key(cu_prefix, target) not in included_set
                ):
                    nested_inline_keys = _graphviz_collect_inline_anonymous_member_type_keys(cu_prefix, target)
                    declaration = _emit_typedef_inline_composite(
                        cu_prefix,
                        typedef_name,
                        target,
                        nested_inline_keys,
                    )

            if declaration is None:
                declaration = _emit_c_declaration_for_node(node_key, nodes, set(), set())
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


def _type_tree_lines(cu_prefix: str, root_die: Any) -> list[str]:
    visited: set[str] = set()
    lines: list[str] = []

    def recurse(current_prefix: str, die: Any, indent: int) -> None:
        key = _die_key(current_prefix, die)
        marker = " " * indent
        if key in visited:
            lines.append(f"{marker}{_format_die(current_prefix, die)} (already shown)")
            return

        visited.add(key)
        lines.append(f"{marker}{_format_die(current_prefix, die)}")

        for relation, dep_prefix, dependency in _iter_dependencies(current_prefix, die):
            relation_marker = " " * (indent + 2)
            lines.append(f"{relation_marker}{relation} -> {_format_die(dep_prefix, dependency)}")
            if _is_traversable_type(dependency):
                recurse(dep_prefix, dependency, indent + 4)

    recurse(cu_prefix, root_die, 0)
    return lines


def print_type_tree(cu_prefix: str, root_die: Any) -> None:
    for line in _type_tree_lines(cu_prefix, root_die):
        print(line)


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
                status_cb(f"Searching type in DWARF: {percent}%")
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
    nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _collect_render_context(
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

        nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _collect_render_context(
            cu_prefix,
            root_die,
            status_cb,
        )

        if include_dependency_tree:
            root_name = die_name(root_die)
            lines.append(f"Dependency tree for {root_name}:")
            lines.extend(_type_tree_lines(cu_prefix, root_die))
            lines.append("")

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


def render_reverse_dependencies_graphviz(
    cu_prefix: str,
    root_die: Any,
    status_cb: Callable[[str], None],
) -> str:
    status_cb("Generating Graphviz C-header style output")
    nodes, _, order, inline_keys, typedef_inline_target_keys, root_key = _collect_render_context(
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
        declaration = _emit_c_declaration_for_node(
            node_key,
            nodes,
            inline_keys,
            typedef_inline_target_keys,
        )
        if declaration is None:
            continue
        included_keys.append(node_key)

    root_name = die_name(root_die)
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
                if die.tag not in TYPE_TAGS:
                    continue
                if "DW_AT_name" not in die.attributes:
                    continue
                if decode_name(die.attributes["DW_AT_name"].value) == "<anonymous>":
                    continue
                named_roots.append((cu_prefix, die))

    status_cb(f"Found {len(named_roots)} named root type(s)")

    nodes_acc: dict[str, tuple[str, Any]] = {}
    included_order: list[str] = []
    included_set: set[str] = set()

    for root_idx, (cu_prefix, root_die) in enumerate(named_roots, start=1):
        if root_idx % 500 == 0:
            status_cb(f"Processing root type {root_idx}/{len(named_roots)}")

        nodes, _, order, inline_keys, typedef_inline_target_keys, _ = _collect_render_context(
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

            declaration = _emit_c_declaration_for_node(
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
