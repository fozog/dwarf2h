from __future__ import annotations

import argparse
from collections.abc import Callable

from .extract import add_extract_arguments, run_extract_command, set_log_enabled
from .kdk import add_kdk_list_arguments, run_kdk_list_command
from .platforms import add_platforms_list_arguments, run_platforms_list_command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kdk2h",
        description="Tools for extracting DWARF types and inspecting installed KDKs.",
    )
    parser.add_argument(
        "--with-log",
        action="store_true",
        help="Enable verbose status logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract DWARF declarations from a KDK/ELF/Mach-O file.",
    )
    add_extract_arguments(extract_parser)
    extract_parser.set_defaults(command_handler=run_extract_command)

    kdk_list_parser = subparsers.add_parser(
        "kdk-list",
        help="List installed KDKs and their available platforms.",
    )
    add_kdk_list_arguments(kdk_list_parser)
    kdk_list_parser.set_defaults(command_handler=run_kdk_list_command)

    platforms_list_parser = subparsers.add_parser(
        "platforms-list",
        help="List known Apple platform codes.",
    )
    add_platforms_list_arguments(platforms_list_parser)
    platforms_list_parser.set_defaults(command_handler=run_platforms_list_command)

    args = parser.parse_args(argv)
    set_log_enabled(bool(getattr(args, "with_log", False)))
    handler = getattr(args, "command_handler", None)
    if not isinstance(handler, Callable):
        parser.print_help()
        return 1
    return int(handler(args))
