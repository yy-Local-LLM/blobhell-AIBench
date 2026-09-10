"""Task loading, validation, and public-context construction."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import yaml
from jsonschema import Draft202012Validator


class ConfigurationError(ValueError):
    """Raised when benchmark configuration is invalid."""


@dataclass(frozen=True)
class TaskDefinition:
    root: Path
    data: dict[str, Any]
    initial_prompt: str

    @property
    def id(self) -> str:
        return str(self.data["id"])

    @property
    def version(self) -> str:
        return str(self.data["version"])

    def public_context(self) -> dict[str, Any]:
        """Return only fields explicitly safe for the agent."""
        allowed = ("id", "version", "target", "software", "objective", "human_policy", "limits")
        return {**{k: self.data[k] for k in allowed if k in self.data}, "initial_prompt": self.initial_prompt}


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "task.schema.json"


def load_task(path: str | Path, schema_path: Path | None = None) -> TaskDefinition:
    root = Path(path).resolve()
    if not root.is_dir():
        raise ConfigurationError(f"Task directory does not exist: {root}")
    try:
        data = yaml.safe_load((root / "task.yaml").read_text(encoding="utf-8"))
        prompt = (root / "initial_prompt.md").read_text(encoding="utf-8").strip()
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(str(exc)) from exc
    if not isinstance(data, dict):
        raise ConfigurationError("task.yaml must contain a mapping")
    schema = json.loads((schema_path or _schema_path()).read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise ConfigurationError("; ".join(e.message for e in errors))
    judge_rel = Path(data["judge"]["criteria"])
    if judge_rel.is_absolute() or root not in (root / judge_rel).resolve().parents:
        raise ConfigurationError("judge criteria must remain inside the task directory")
    if not (root / judge_rel).is_file():
        raise ConfigurationError(f"Judge criteria missing: {judge_rel}")
    return TaskDefinition(root, data, prompt)

