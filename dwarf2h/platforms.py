from __future__ import annotations

import argparse
from dataclasses import dataclass

from .system import _get_current_platform_code


@dataclass(frozen=True)
class PlatformInfo:
    code: str
    soc: str
    hardware: str


# Hand-maintained mapping of known Apple platform identifiers.
# Keep this list updated as new platform codes appear in KDKs.
KNOWN_PLATFORMS: tuple[PlatformInfo, ...] = (
    PlatformInfo("t6000", "M1 Pro", "MacBook Pro 14\" & 16\" (2021)"),
    PlatformInfo("t6020", "M2 Pro", "MacBook Pro 14\" & 16\" (2023)"),
    PlatformInfo("t6030", "M3 Pro", "MacBook Pro 14\" & 16\" (Late 2023)"),
    PlatformInfo("t6031", "M3 Max", "MacBook Pro 14\" & 16\" (Late 2023)"),
    PlatformInfo("t6041", "M4 Pro", "MacBook Pro 14\" & 16\" (Late 2024)"),
    PlatformInfo("t6050", "M4 Max", "MacBook Pro 14\" & 16\" (Late 2024)"),
    PlatformInfo("t8103", "M1", "MacBook Air/Pro 13\", Mac mini, iMac 24\" (2020-2021)"),
    PlatformInfo("t8112", "M2", "MacBook Air/Pro 13\", Mac mini (2022-2023)"),
    PlatformInfo("t8122", "M3", "MacBook Air 13\" & 15\" (2024), iMac 24\" (2023)"),
    PlatformInfo("t8132", "M4", "iPad Pro (2024), MacBook Air 13\" & 15\" (2025)"),
    PlatformInfo("t8140", "A17 Pro", "iPhone 15 Pro & 15 Pro Max (2023)"),
    PlatformInfo("t8142", "A18 / A18 Pro", "iPhone 16 family (2024)"),
    PlatformInfo("vmapple", "Virtual Apple SoC", "Apple Virtualization.framework guest platform"),
)

def add_platforms_list_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Print output as CSV.",
    )


def run_platforms_list_command(args: argparse.Namespace) -> int:
    current_platform = _get_current_platform_code()

    if args.csv:
        print("current,platform,soc,hardware")
        for entry in KNOWN_PLATFORMS:
            marker = "*" if entry.code == current_platform else ""
            print(f"{marker},{entry.code},{entry.soc},{entry.hardware}")
        return 0

    rows = [
        ("*" if entry.code == current_platform else "", entry.code, entry.soc, entry.hardware)
        for entry in KNOWN_PLATFORMS
    ]
    mark_w = len("CUR")
    code_w = max(len("PLATFORM"), *(len(code) for _, code, _, _ in rows))
    soc_w = max(len("SOC"), *(len(soc) for _, _, soc, _ in rows))

    print(f"{'CUR':<{mark_w}}  {'PLATFORM':<{code_w}}  {'SOC':<{soc_w}}  HARDWARE")
    print(f"{'-' * mark_w}  {'-' * code_w}  {'-' * soc_w}  {'-' * len('HARDWARE')}")
    for marker, code, soc, hardware in rows:
        print(f"{marker:<{mark_w}}  {code:<{code_w}}  {soc:<{soc_w}}  {hardware}")
    return 0
