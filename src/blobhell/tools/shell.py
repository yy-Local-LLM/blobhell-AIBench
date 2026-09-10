"""Async subprocess primitive."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool


async def run_command(argv: list[str], cwd: Path, env: dict[str, str], timeout: float) -> CommandResult:
    process = await asyncio.create_subprocess_exec(
        *argv, cwd=cwd, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        return CommandResult(process.returncode, stdout, stderr, False)
    except asyncio.TimeoutError:
        process.kill()
        stdout, stderr = await process.communicate()
        return CommandResult(None, stdout, stderr, True)

