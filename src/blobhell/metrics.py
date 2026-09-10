"""Run counters derived from events."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Any


def derive_metrics(events: Iterable[dict[str, Any]], wall_time_seconds: float) -> dict[str, Any]:
    items = list(events)
    types = Counter(e["type"] for e in items)
    tools = [e for e in items if e["type"] == "tool_completed"]
    return {
        "wall_time_seconds": round(wall_time_seconds, 3),
        "agent_turns": types["agent_message"],
        "tool_calls": len(tools),
        "builds": sum(1 for e in tools if e["payload"].get("category") == "build"),
        "reboots": sum(1 for e in tools if e["payload"].get("tool") == "device_reboot"),
        "failed_experiments": sum(1 for e in tools if e["payload"].get("exit_code", 0) != 0),
        "human_technical_hints": sum(
            1 for e in items if e["type"] == "human_operator_action" and e["payload"].get("technical_hint")
        ),
    }

