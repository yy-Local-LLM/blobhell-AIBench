"""Command-line interface."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from time import strftime, gmtime

from . import __version__
from .agents import ScriptedAgent
from .config import ConfigurationError, load_task
from .judge import StateMachineJudge
from .runner import run_sync


def _summary(result: dict) -> None:
    print(f"BlobHell-AIBench v{__version__}")
    print(f"Task: {result['task']}")
    print(f"Leaderboard eligible: {'yes' if result['leaderboard_eligible'] else 'no'}")
    print("Human technical intervention: forbidden\n")
    print("Independent judge:")
    for check in result["judge"]["checks"]:
        print(f"[{check['status']}] {check['id']}")
    print(f"\nRESULT: {result['result']}")
    print(f"Time: {strftime('%H:%M:%S', gmtime(result['wall_time_seconds']))}")
    print(f"Human hints: {result['human_technical_hints']}\n")
    print("The hardware has spoken.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blobhell")
    subs = parser.add_subparsers(dest="command", required=True)
    validate = subs.add_parser("validate"); validate.add_argument("task")
    run = subs.add_parser("run"); run.add_argument("task"); run.add_argument("--agent", default="scripted", choices=["scripted"]); run.add_argument("--runs-dir", default="runs")
    inspect = subs.add_parser("inspect"); inspect.add_argument("run")
    judge = subs.add_parser("judge"); judge.add_argument("run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            task = load_task(args.task); print(f"Valid task: {task.id} v{task.version}"); return 0
        if args.command == "run":
            task = load_task(args.task)
            result, path = run_sync(task, ScriptedAgent(), Path(args.runs_dir))
            _summary(result); print(f"Artifacts: {path}"); return 0 if result["result"] == "PASS" else 1
        run_dir = Path(args.run).resolve()
        result_path = run_dir / "result.json"
        if args.command == "inspect":
            result = json.loads(result_path.read_text(encoding="utf-8")); _summary(result); return 0
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        judged = StateMachineJudge.from_file(run_dir / "judge-private" / "criteria.yaml").evaluate(
            run_dir / "evidence", metrics.get("human_technical_hints", 0))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        result.update(result=judged["result"], judge=judged, checkpoints={c["id"]: c["status"] for c in judged["checks"]})
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        _summary(result); return 0 if result["result"] == "PASS" else 1
    except (ConfigurationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}"); return 2


if __name__ == "__main__":
    raise SystemExit(main())

