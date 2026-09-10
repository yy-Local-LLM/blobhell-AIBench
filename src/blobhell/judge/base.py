"""Independent judge contract."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Judge(ABC):
    @abstractmethod
    def evaluate(self, evidence_dir: Path, human_technical_hints: int = 0) -> dict[str, Any]: ...

