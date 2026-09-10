"""Vendor-neutral agent protocol."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Observation:
    kind: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentAction:
    kind: str
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    message: str = ""


class Agent(ABC):
    name = "abstract"
    model = "unknown"

    @abstractmethod
    async def start(self, task_context: dict[str, Any]) -> None: ...

    @abstractmethod
    async def step(self, observation: Observation) -> AgentAction: ...

    @abstractmethod
    async def finalize(self) -> None: ...

