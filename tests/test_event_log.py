from blobhell.events import event
from blobhell.transcript import Transcript
from blobhell.metrics import derive_metrics
import json
from jsonschema import Draft202012Validator

def test_transcript_appends(tmp_path):
    log = Transcript(tmp_path / "events.jsonl")
    log.append(event("run", "run_started", "runner", n=1)); log.append(event("run", "run_finished", "runner"))
    assert [x["type"] for x in log.read()] == ["run_started", "run_finished"]

def test_human_intervention_accounting():
    items = [event("run", "human_operator_action", "operator", technical_hint=False),
             event("run", "human_operator_action", "operator", technical_hint=True)]
    assert derive_metrics(items, 1)["human_technical_hints"] == 1

def test_event_matches_schema(root):
    schema = json.loads((root / "schemas/event.schema.json").read_text())
    Draft202012Validator(schema).validate(event("run", "run_started", "runner"))
