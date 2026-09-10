"""Structured event creation."""
from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic
from typing import Any


def event(run_id: str, event_type: str, actor: str, **payload: Any) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "type": event_type,
        "actor": actor,
        "wall_time": datetime.now(timezone.utc).isoformat(),
        "monotonic_seconds": monotonic(),
        "payload": payload,
    }

