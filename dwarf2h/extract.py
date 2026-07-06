from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

from elftools.common.exceptions import ELFError
from elftools.dwarf.dwarfinfo import DWARFInfo
from elftools.elf.elffile import ELFFile

from .dwarf import (
    decode_name,
    find_named_type,
    iter_declared_types_from_dwarf_info,
    print_type_tree,
    render_all_definitions,
    render_reverse_dependencies,
)
from .macho import load_macho_dwarf_infos
from .system import _get_current_platform_code, _get_running_macos_version

T = TypeVar("T")
_LOG_ENABLED = False


def set_log_enabled(enabled: bool) -> None:
    global _LOG_ENABLED
    _LOG_ENABLED = enabled


def _status(message: str) -> None:
    if _LOG_ENABLED:
        print(f"[status] {message}", file=sys.stderr)


def _resolve_input_path(*, kdk_file: str | None, kdk_tag: str | None) -> Path:
    if kdk_file is not None:
        raw_path = Path(kdk_file)
        if raw_path.is_dir() and raw_path.name.endswith(".dSYM"):
            dwarf_dir = raw_path / "Contents" / "Resources" / "DWARF"
            expected_name = raw_path.name[: -len(".dSYM")]
            expected_path = dwarf_dir / expected_name
            if expected_path.is_file():
                return expected_path

            if dwarf_dir.is_dir():
                dwarf_files = sorted(path for path in dwarf_dir.iterdir() if path.is_file())
                if len(dwarf_files) == 1:
                    return dwarf_files[0]
                if len(dwarf_files) > 1:
                    preview = ", ".join(path.name for path in dwarf_files[:5])
                    raise ValueError(
                        "Ambiguous .dSYM directory: expected "
                        f"{expected_name!r} in {dwarf_dir}, found multiple files: {preview}. "
                        "Please pass --file with the exact DWARF file path."
                    )

            raise ValueError(
                "Invalid .dSYM directory for --file: expected DWARF file at "
                f"{expected_path}"
            )

        return raw_path

    if kdk_tag is None:
        raise ValueError("Either --file or --kdk must be provided.")

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
            f"{kdk_tag}. Please use --file. Matches: {preview}"
        )
    return matches[0]


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

    if sys.platform.startswith("linux"):
        linux_vmlinux = Path("/usr/lib/modules") / os.uname().release / "build" / "vmlinux"
        _status(
            f"No --kdk/--file provided on Linux, using default kernel DWARF file: {linux_vmlinux}"
        )
        return (linux_vmlinux, None)

    platform = _get_current_platform_code()
    version = _get_running_macos_version()
    if platform is None or version is None:
        raise ValueError(
            "Unable to auto-detect local platform/version. Please provide --kdk or --file."
        )

    implicit_tag = f"{platform}@{version}"
    _status(f"No --kdk/--file provided, using local system tag: {implicit_tag}")
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

    dwarf_infos = load_macho_dwarf_infos(dwarf_path, _status)
    return visitor(dwarf_infos)


def iter_declared_types(dwarf_path: Path) -> Iterable[tuple[str, str, str]]:
    def collect(dwarf_infos: list[tuple[str, DWARFInfo]]) -> list[tuple[str, str, str]]:
        rows: list[tuple[str, str, str]] = []
        for cu_prefix, dwarf_info in dwarf_infos:
            rows.extend(iter_declared_types_from_dwarf_info(dwarf_info, cu_prefix=cu_prefix))
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
        "--file",
        type=str,
        help="Direct path to the ELF or Mach-O file containing DWARF info.",
    )
    source_group.add_argument(
        "--kdk",
        type=str,
        help=(
            "KDK tag in the form <platform>@<version>. "
            "If neither --kdk nor --file is provided, macOS auto-detects local "
            "platform/version while Linux uses /usr/lib/modules/$(uname -r)/build/vmlinux."
        ),
    )
    parser.add_argument(
        "type_name",
        nargs="?",
        help="Optional type name to print with recursive dependencies.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract C declarations for all named DWARF types.",
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
    if not args.type_name and not args.all:
        print("Error: extract requires type_name or --all.")
        return 1

    if args.type_name and args.all:
        print("Error: --all cannot be used with type_name.")
        return 1

    if args.header and not (args.type_name or args.all):
        print("Error: --header requires type_name or --all.")
        return 1

    try:
        dwarf_file, effective_kdk_tag = _resolve_effective_input_path(
            kdk_file=args.file,
            kdk_tag=args.kdk,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if not dwarf_file.exists():
        print(f"Error: file not found: {dwarf_file}")
        return 1

    try:
        if args.all:

            def extract_all(dwarf_infos: list[tuple[str, DWARFInfo]]) -> str:
                return render_all_definitions(
                    dwarf_infos,
                    _status,
                    include_dependency_tree=args.with_dependency_tree,
                )

            c_declarations = _run_with_dwarf_infos(dwarf_file, extract_all)
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
        elif args.type_name:

            def print_named_type(dwarf_infos: list[tuple[str, DWARFInfo]]) -> bool:
                found = find_named_type(dwarf_infos, args.type_name, _status)
                if found is None:
                    return False
                cu_prefix, die, is_approximate = found
                if is_approximate:
                    print(
                        f"Note: no exact match for {args.type_name}; using {decode_name(die.attributes['DW_AT_name'].value)}"
                    )
                if args.with_dependency_tree:
                    print("Dependency tree:")
                    print_type_tree(cu_prefix, die)
                    print()

                c_declarations = render_reverse_dependencies(cu_prefix, die, _status)
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
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 0
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    return 0
