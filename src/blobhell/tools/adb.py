"""ADB argument construction without invoking a shell."""
from __future__ import annotations
from typing import Any


def adb_argv(tool: str, arguments: dict[str, Any]) -> list[str]:
    serial = arguments.get("serial")
    prefix = ["adb"] + (["-s", str(serial)] if serial else [])
    args = [str(v) for v in arguments.get("args", [])]
    if tool == "adb": return prefix + args
    if tool == "adb_shell": return prefix + ["shell"] + args
    if tool == "adb_logcat": return prefix + ["logcat"] + args
    if tool == "device_reboot": return prefix + ["reboot"]
    if tool == "wait_for_device": return prefix + ["wait-for-device"]
    if tool == "wait_for_boot":
        return prefix + ["shell", "sh", "-c", "while [ \"$(getprop sys.boot_completed)\" != 1 ]; do sleep 1; done"]
    raise ValueError(f"Unknown ADB tool: {tool}")

