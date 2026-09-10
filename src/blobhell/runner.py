"""Benchmark orchestration with a hard agent/judge boundary."""
from __future__ import annotations
import asyncio
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any

from .agents.base import Agent, Observation
from .config import TaskDefinition
from .events import event
from .judge import StateMachineJudge
from .metrics import derive_metrics
from .tools import ToolGateway
from .transcript import Transcript


class Runner:
    def __init__(self, task: TaskDefinition, agent: Agent, runs_dir: Path, run_id: str | None = None):
        self.task, self.agent = task, agent
        self.run_id = run_id or f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
        self.run_dir = runs_dir.resolve() / self.run_id

    async def run(self) -> dict[str, Any]:
        start = monotonic()
        workspace, evidence, private = self.run_dir / "workspace", self.run_dir / "evidence", self.run_dir / "judge-private"
        for directory in (workspace, evidence, private, self.run_dir / "device-logs"): directory.mkdir(parents=True, exist_ok=True)
        criteria_source = self.task.root / self.task.data["judge"]["criteria"]
        criteria_copy = private / "criteria.yaml"
        shutil.copyfile(criteria_source, criteria_copy)
        transcript = Transcript(self.run_dir / "transcript.jsonl")
        emit = lambda event_type, actor, **data: transcript.append(event(self.run_id, event_type, actor, **data))
        manifest = {"benchmark": "BlobHell-AIBench", "harness_version": "0.1.0", "run_id": self.run_id,
                    "task": self.task.id, "task_version": self.task.version, "agent_adapter": self.agent.name,
                    "model": self.agent.model, "started_at": datetime.now(timezone.utc).isoformat()}
        (self.run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        emit("run_started", "runner", manifest=manifest)
        emit("task_loaded", "runner", task=self.task.id, version=self.task.version)
        gateway = ToolGateway(self.run_id, workspace, self.run_dir, transcript,
                              allowed_tools=set(self.task.data.get("tools", {}).get("allowed", ToolGateway.TOOLS)),
                              timeout=float(self.task.data.get("limits", {}).get("tool_timeout_seconds", 300)))
        failure = None
        try:
            await self.agent.start(self.task.public_context())
            emit("agent_started", "runner", adapter=self.agent.name)
            observation = Observation("task", self.task.public_context())
            for _ in range(int(self.task.data.get("limits", {}).get("max_turns", 100))):
                action = await self.agent.step(observation)
                emit("agent_message", "agent", kind=action.kind, message=action.message)
                if action.kind == "finish": break
                if action.kind != "tool" or not action.tool: raise ValueError(f"Invalid agent action: {action.kind}")
                observation = Observation("tool_result", await gateway.invoke(action.tool, action.arguments))
            else:
                failure = "agent turn limit exceeded"
            await self.agent.finalize()
            emit("agent_finished", "runner", reason=failure or "agent_terminated")
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
            emit("run_failed", "runner", error=failure)
            try: await self.agent.finalize()
            except Exception: pass
        elapsed = monotonic() - start
        metrics = derive_metrics(transcript.read(), elapsed)
        (self.run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        emit("judge_started", "judge", criteria_version="0.1")
        judged = StateMachineJudge.from_file(criteria_copy).evaluate(evidence, metrics["human_technical_hints"])
        if failure: judged["result"] = "ERROR"
        for check in judged["checks"]: emit("judge_check", "judge", **check)
        emit("judge_finished", "judge", result=judged["result"])
        result = {**manifest, "result": judged["result"],
                  "leaderboard_eligible": bool(self.task.data["leaderboard_eligible"]) and judged["result"] == "PASS",
                  "contamination_status": self.task.data["contamination_status"], **metrics,
                  "checkpoints": {c["id"]: c["status"] for c in judged["checks"]}, "judge": judged}
        if failure: result["failure"] = failure
        (self.run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        emit("run_finished", "runner", result=result["result"])
        return result


def run_sync(task: TaskDefinition, agent: Agent, runs_dir: Path) -> tuple[dict[str, Any], Path]:
    runner = Runner(task, agent, runs_dir)
    return asyncio.run(runner.run()), runner.run_dir
