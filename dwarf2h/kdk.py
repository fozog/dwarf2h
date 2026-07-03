from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

KDK_ROOT = Path("/Library/Developer/KDKs")
KDK_NAME_PATTERN = re.compile(r"^KDK_(?P<version>[^_]+)_(?P<build>.+)\.kdk$")
APPLE_BUILD_PATTERN = re.compile(
    r"^(?P<darwin_major>\d+)(?P<train>[A-Z])(?P<train_build>\d+)(?P<suffix>[a-z]?)$"
)


@dataclass(frozen=True)
class InstalledKDK:
    path: Path
    version: str
    build: str
    platforms: tuple[str, ...]


def _decode_apple_version(version: str) -> str:
    return f"MacOS {version}"


def _decode_apple_build(build: str) -> tuple[str, str]:
    match = APPLE_BUILD_PATTERN.match(build)
    if match is None:
        return (f"build {build}", "Darwin ?")

    darwin_major = match.group("darwin_major")
    train = match.group("train")
    train_build = match.group("train_build")
    suffix = match.group("suffix")

    # Apple pre-release convention used by current KDKs:
    # A5xxx => beta build xxx.
    if train == "A" and train_build.startswith("5") and len(train_build) > 1:
        beta_build = train_build[1:]
        if suffix:
            beta_build = f"{beta_build}{suffix}"
        return (f"beta build {beta_build}", f"Darwin {darwin_major}")

    if suffix:
        return (f"release {train} build {train_build} suffix {suffix}", f"Darwin {darwin_major}")
    return (f"release {train} build {train_build}", f"Darwin {darwin_major}")


def _extract_platform(dsym_name: str) -> str | None:
    prefix = "kernel.kasan."
    suffix = ".dSYM"
    if not dsym_name.startswith(prefix) or not dsym_name.endswith(suffix):
        return None
    platform = dsym_name[len(prefix) : -len(suffix)]
    return platform or None


def iter_installed_kdks(kdk_root: Path = KDK_ROOT) -> list[InstalledKDK]:
    if not kdk_root.exists():
        return []

    items: list[InstalledKDK] = []
    for kdk_path in sorted(kdk_root.glob("KDK_*.kdk")):
        if not kdk_path.is_dir():
            continue

        match = KDK_NAME_PATTERN.match(kdk_path.name)
        if match is None:
            continue

        kernels_dir = kdk_path / "System/Library/Kernels"
        platforms: set[str] = set()
        if kernels_dir.exists():
            for dsym_dir in kernels_dir.glob("kernel.kasan.*.dSYM"):
                platform = _extract_platform(dsym_dir.name)
                if platform is not None:
                    platforms.add(platform)

        items.append(
            InstalledKDK(
                path=kdk_path,
                version=match.group("version"),
                build=match.group("build"),
                platforms=tuple(sorted(platforms)),
            )
        )

    return items


def add_kdk_list_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=KDK_ROOT,
        help="KDK root directory (default: /Library/Developer/KDKs).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also print supported platforms and KDK path.",
    )


def _get_running_macos() -> tuple[str, str] | None:
    try:
        version = subprocess.check_output(
            ["sw_vers", "-productVersion"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        build = subprocess.check_output(
            ["sw_vers", "-buildVersion"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if version and build:
            return (version, build)
    except Exception:
        return None
    return None


def run_kdk_list_command(args: argparse.Namespace) -> int:
    running = _get_running_macos()
    items = iter_installed_kdks(args.root)
    rows: list[tuple[str, str, str, str, str, InstalledKDK]] = []
    for item in items:
        marker = "*" if running == (item.version, item.build) else " "
        version_info = _decode_apple_version(item.version)
        build_info, darwin_info = _decode_apple_build(item.build)
        rows.append((marker, f"{item.version}_{item.build}", version_info, build_info, darwin_info, item))

    if not rows:
        return 0

    id_w = max(len("VERSION_BUILD"), *(len(version_build) for _, version_build, _, _, _, _ in rows))
    macos_w = max(len("MACOS"), *(len(version_info) for _, _, version_info, _, _, _ in rows))
    build_w = max(len("BUILD_INFO"), *(len(build_info) for _, _, _, build_info, _, _ in rows))

    for marker, version_build, version_info, build_info, darwin_info, item in rows:
        line = f"{marker} {version_build:<{id_w}}  {version_info:<{macos_w}}  {build_info:<{build_w}}  {darwin_info}"
        if args.full:
            platforms = ",".join(item.platforms) if item.platforms else "-"
            line = f"{line}\tplatforms={platforms}\tpath={item.path}"
        print(line)
    return 0
