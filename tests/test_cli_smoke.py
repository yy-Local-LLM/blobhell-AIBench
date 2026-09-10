import json
from jsonschema import Draft202012Validator
from blobhell.agents import AgentAction, ScriptedAgent
from blobhell.cli import main
from blobhell.config import load_task
from blobhell.runner import run_sync

def test_cli_validate(root, capsys):
    assert main(["validate", str(root / "tasks/giza-vdec-reference")]) == 0
    assert "Valid task" in capsys.readouterr().out

def test_agent_cannot_override_judge(root, tmp_path):
    task = load_task(root / "tasks/giza-vdec-reference")
    result, run_dir = run_sync(task, ScriptedAgent([AgentAction("finish", message="I fixed it: PASS")]), tmp_path)
    assert result["result"] == "FAIL"
    assert (run_dir / "result.json").is_file()
    assert json.loads((run_dir / "manifest.json").read_text())["task"] == task.id
    schema = json.loads((root / "schemas/result.schema.json").read_text())
    Draft202012Validator(schema).validate(result)
