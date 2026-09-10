import yaml
import pytest
from blobhell.config import ConfigurationError, load_task

def test_reference_task_loads(root):
    task = load_task(root / "tasks/giza-vdec-reference")
    assert task.id == "giza-vdec-reference"
    assert task.data["leaderboard_eligible"] is False
    assert "judge" not in task.public_context()

def test_invalid_task_rejected(root, tmp_path):
    source = yaml.safe_load((root / "tasks/giza-vdec-reference/task.yaml").read_text())
    source["human_policy"]["technical_hints"] = "allowed"
    (tmp_path / "task.yaml").write_text(yaml.safe_dump(source))
    (tmp_path / "initial_prompt.md").write_text("test")
    (tmp_path / "judge").mkdir(); (tmp_path / "judge/criteria.yaml").write_text("checks: []")
    with pytest.raises(ConfigurationError): load_task(tmp_path)

