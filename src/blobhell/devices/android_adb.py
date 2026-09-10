"""Android device operations routed through a gateway."""
from __future__ import annotations
from typing import Any
from .base import Device


class AndroidAdbDevice(Device):
    def __init__(self, gateway: Any):
        self.gateway = gateway

    async def invoke(self, operation: str, arguments: dict[str, Any]) -> Any:
        mapping = {
            "adb": "adb", "shell": "adb_shell", "logcat": "adb_logcat",
            "reboot": "device_reboot", "wait_for_device": "wait_for_device",
            "wait_for_boot": "wait_for_boot",
        }
        if operation not in mapping:
            raise ValueError(f"Unsupported device operation: {operation}")
        return await self.gateway.invoke(mapping[operation], arguments)

