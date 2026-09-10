"""Device abstraction; implementations never bypass the tool gateway."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class Device(ABC):
    @abstractmethod
    async def invoke(self, operation: str, arguments: dict[str, Any]) -> Any: ...


class FakeDevice(Device):
    """Deterministic device used by tests without physical hardware."""

    def __init__(self, responses: dict[str, Any] | None = None):
        self.responses = responses or {}
        self.operations: list[tuple[str, dict[str, Any]]] = []

    async def invoke(self, operation: str, arguments: dict[str, Any]) -> Any:
        self.operations.append((operation, arguments))
        if operation not in self.responses:
            raise ValueError(f"No fake response configured for: {operation}")
        return self.responses[operation]
