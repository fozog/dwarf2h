from __future__ import annotations

import plistlib
import subprocess


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