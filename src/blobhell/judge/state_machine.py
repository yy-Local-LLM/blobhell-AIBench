"""Declarative evidence judge. Agent messages are intentionally inaccessible."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Callable
import yaml
from .base import Judge


class StateMachineJudge(Judge):
    version = "0.1"

    def __init__(self, criteria: dict[str, Any], evaluators: dict[str, Callable] | None = None):
        self.criteria = criteria
        self.evaluators = evaluators or {}

    @classmethod
    def from_file(cls, path: Path, evaluators: dict[str, Callable] | None = None) -> "StateMachineJudge":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("checks"), list):
            raise ValueError("Judge criteria must contain checks")
        return cls(data, evaluators)

    def _safe_path(self, root: Path, relative: str) -> Path:
        path = (root / relative).resolve()
        if path != root.resolve() and root.resolve() not in path.parents:
            raise ValueError("Evidence path escapes evidence directory")
        return path

    def _check(self, check: dict[str, Any], root: Path) -> tuple[bool, str, list[str]]:
        kind, cfg = check["type"], check.get("config", {})
        if kind == "artifact_exists":
            path = self._safe_path(root, cfg["path"])
            return path.is_file(), "artifact present" if path.is_file() else "artifact missing", [cfg["path"]]
        if kind == "regex":
            path = self._safe_path(root, cfg["path"])
            if not path.is_file(): return False, "evidence file missing", [cfg["path"]]
            matched = re.search(cfg["pattern"], path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE) is not None
            return matched, "pattern matched" if matched else "pattern not found", [cfg["path"]]
        if kind in {"json_value", "manual_observation"}:
            path = self._safe_path(root, cfg["path"])
            if not path.is_file(): return False, "evidence file missing", [cfg["path"]]
            value: Any = json.loads(path.read_text(encoding="utf-8"))
            for key in cfg["key"].split("."):
                if not isinstance(value, dict) or key not in value: return False, "evidence key missing", [cfg["path"]]
                value = value[key]
            expected = cfg.get("equals", True)
            return value == expected, f"observed {value!r}", [cfg["path"]]
        if kind == "mockable":
            evaluator = self.evaluators.get(check["id"])
            if not evaluator: return False, "no evaluator configured", []
            passed, message, evidence = evaluator(root, check)
            return bool(passed), str(message), list(evidence)
        return False, f"check type {kind!r} is not implemented in v0.1", []

    def evaluate(self, evidence_dir: Path, human_technical_hints: int = 0) -> dict[str, Any]:
        checks, required_ok = [], True
        for spec in self.criteria["checks"]:
            try: passed, message, evidence = self._check(spec, evidence_dir)
            except Exception as exc: passed, message, evidence = False, f"evaluation error: {exc}", []
            if spec.get("required", True) and not passed: required_ok = False
            checks.append({"id": spec["id"], "status": "PASS" if passed else "FAIL", "mode": spec["mode"],
                           "required": spec.get("required", True), "message": message, "evidence": evidence})
        if human_technical_hints:
            required_ok = False
            checks.append({"id": "human_technical_hints", "status": "FAIL", "mode": "automatic", "required": True,
                           "message": f"{human_technical_hints} forbidden technical hint(s) recorded", "evidence": []})
        return {"version": self.version, "result": "PASS" if required_ok else "FAIL", "checks": checks}

