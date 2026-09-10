"""Append-only, durable JSONL transcript."""
from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any, Iterator
import json


class Transcript:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def append(self, item: dict[str, Any]) -> None:
        line = json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n"
        with self._lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(line)
            stream.flush()

    def read(self) -> Iterator[dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)

