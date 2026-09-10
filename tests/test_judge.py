import json
from blobhell.judge import StateMachineJudge

CRITERIA = {"checks": [{"id": "BOOT_OK", "type": "json_value", "mode": "automatic", "required": True, "config": {"path": "state.json", "key": "ok", "equals": True}}]}

def test_judge_pass_and_fail(tmp_path):
    judge = StateMachineJudge(CRITERIA)
    assert judge.evaluate(tmp_path)["result"] == "FAIL"
    (tmp_path / "state.json").write_text(json.dumps({"ok": True}))
    assert judge.evaluate(tmp_path)["result"] == "PASS"

def test_human_hint_forces_failure(tmp_path):
    (tmp_path / "state.json").write_text(json.dumps({"ok": True}))
    assert StateMachineJudge(CRITERIA).evaluate(tmp_path, human_technical_hints=1)["result"] == "FAIL"

