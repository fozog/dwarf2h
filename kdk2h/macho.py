from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any

from elftools.dwarf.dwarfinfo import DWARFInfo, DebugSectionDescriptor, DwarfConfig

try:
    from macholib.MachO import MachO  # type: ignore[reportMissingImports]
    from macholib import mach_o as mach_o_consts  # type: ignore[reportMissingImports]
except ImportError:
    MachO = None
    mach_o_consts = None

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


def load_macho_dwarf_infos(
    dwarf_path: Path,
    status_cb: Callable[[str], None],
) -> list[tuple[str, DWARFInfo]]:
    if MachO is None or mach_o_consts is None:
        raise ValueError("Mach-O support requires the 'macholib' package.")

    macho = MachO(str(dwarf_path))
    dwarf_infos: list[tuple[str, DWARFInfo]] = []
    for index, header in enumerate(macho.headers):
        status_cb(f"Loading DWARF sections for slice {index + 1}/{len(macho.headers)}")
        dwarf_info = _build_macho_dwarf_info(dwarf_path, header)
        if dwarf_info is None:
            continue
        has_multiple_archs = len(macho.headers) > 1
        arch_name = _cpu_arch_name(header.header.cputype)
        cu_prefix = f"{arch_name}[{index}]:" if has_multiple_archs else ""
        dwarf_infos.append((cu_prefix, dwarf_info))

    if not dwarf_infos:
        raise ValueError("No DWARF sections were found in this Mach-O file.")

    return dwarf_infos
