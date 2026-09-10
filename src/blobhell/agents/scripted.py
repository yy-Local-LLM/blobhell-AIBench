"""Deterministic adapter for tests and harness demonstrations."""
from __future__ import annotations

from collections import deque
from typing import Iterable

from .base import Agent, AgentAction, Observation


class ScriptedAgent(Agent):
    name = "scripted"
    model = "deterministic-script"

    def __init__(self, actions: Iterable[AgentAction] | None = None):
        self.actions = deque(actions or [AgentAction(kind="finish", message="No scripted repair was attempted.")])
        self.started = False
        self.finalized = False

    async def start(self, task_context: dict) -> None:
        self.started = True

    async def step(self, observation: Observation) -> AgentAction:
        return self.actions.popleft() if self.actions else AgentAction(kind="finish")

    async def finalize(self) -> None:
        self.finalized = True

