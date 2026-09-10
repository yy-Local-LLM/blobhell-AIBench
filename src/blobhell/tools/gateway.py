"""Controlled, observable gateway for all agent command execution."""
from __future__ import annotations
import os
from pathlib import Path
from time import monotonic
from typing import Any, Callable

from ..events import event
from ..transcript import Transcript
from .adb import adb_argv
from .shell import run_command


class ToolGateway:
    TOOLS = {"shell", "adb", "adb_shell", "adb_logcat", "device_reboot", "wait_for_device", "wait_for_boot"}

    def __init__(self, run_id: str, workspace: Path, artifacts: Path, transcript: Transcript,
                 allowed_tools: set[str] | None = None, env_allowlist: tuple[str, ...] = ("PATH",),
                 timeout: float = 300, console_limit: int = 8000, secrets: tuple[str, ...] = (),
                 executor: Callable[..., Any] = run_command):
        self.run_id, self.workspace, self.artifacts, self.transcript = run_id, workspace.resolve(), artifacts, transcript
        self.allowed_tools = allowed_tools or self.TOOLS
        self.env_allowlist, self.timeout, self.console_limit, self.secrets = env_allowlist, timeout, console_limit, secrets
        self.executor = executor
        (artifacts / "command-logs").mkdir(parents=True, exist_ok=True)
        self.sequence = 0

    def _redact(self, text: str) -> str:
        for secret in self.secrets:
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return text

    async def invoke(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool not in self.allowed_tools or tool not in self.TOOLS:
            raise PermissionError(f"Tool is not allowed: {tool}")
        self.transcript.append(event(self.run_id, "tool_requested", "agent", tool=tool, arguments=arguments))
        cwd = (self.workspace / str(arguments.get("cwd", "."))).resolve()
        if cwd != self.workspace and self.workspace not in cwd.parents:
            raise PermissionError("Working directory escapes the agent workspace")
        if not cwd.is_dir():
            raise FileNotFoundError(cwd)
        argv = arguments.get("argv") if tool == "shell" else adb_argv(tool, arguments)
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            raise ValueError("argv must be a non-empty list of strings")
        timeout = min(float(arguments.get("timeout", self.timeout)), self.timeout)
        safe_args = {**arguments, "argv": argv}
        self.transcript.append(event(self.run_id, "tool_started", "gateway", tool=tool, arguments=safe_args, cwd=str(cwd)))
        started = monotonic()
        env = {key: os.environ[key] for key in self.env_allowlist if key in os.environ}
        result = await self.executor(argv, cwd, env, timeout)
        duration = monotonic() - started
        self.sequence += 1
        stdout = self._redact(result.stdout.decode("utf-8", "replace"))
        stderr = self._redact(result.stderr.decode("utf-8", "replace"))
        log = self.artifacts / "command-logs" / f"{self.sequence:05d}.json"
        import json
        log.write_text(json.dumps({"argv": argv, "cwd": str(cwd), "stdout": stdout, "stderr": stderr}, ensure_ascii=False), encoding="utf-8")
        payload = {"tool": tool, "arguments": safe_args, "cwd": str(cwd), "exit_code": result.exit_code,
                   "duration_seconds": duration, "stdout": stdout, "stderr": stderr,
                   "timed_out": result.timed_out, "full_log": str(log.relative_to(self.artifacts))}
        self.transcript.append(event(self.run_id, "tool_completed", "gateway", **payload))
        return {**payload, "console_stdout": stdout[:self.console_limit], "console_stderr": stderr[:self.console_limit]}

