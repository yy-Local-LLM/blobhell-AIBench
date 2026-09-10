# BlobHell-AIBench

A hardware-in-the-loop AI benchmark for long-horizon autonomous debugging of real-world legacy systems.

> The human does not debug. The hardware is the judge.

BlobHell-AIBench measures whether an autonomous agent can diagnose, modify, build, deploy, and validate repairs to genuine low-level systems failures. Unlike coding benchmarks that grade a patch or a text answer, BlobHell evaluates observable behavior in an isolated workspace and, where required, on real hardware.

The agent receives a task prompt and controlled tools. Every command and observation is recorded. Human operators may perform requested physical actions and report directly observable state, but may not interpret evidence, suggest commands or causes, or disclose prior knowledge. An agent's claim that it succeeded has no scoring value: a separate judge evaluates independently collected evidence after the agent terminates.

The first task, `giza-vdec-reference`, describes H.264 hardware decoding on the Amazon Fire HD 8 (6th generation). It is a public, contaminated reference task and is permanently leaderboard-ineligible. It validates the harness, logging, task format, judging, and reproducibility. Future hidden tasks are intended for meaningful leaderboard evaluation.

This repository redistributes no Amazon or MediaTek firmware, vendor blobs, DRM components, proprietary libraries, or complete system images. Operators supply authorized hardware and source artifacts separately.

## Quick start

```console
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
blobhell validate tasks/giza-vdec-reference
blobhell run tasks/giza-vdec-reference --agent scripted
blobhell inspect runs/<run-id>
blobhell judge runs/<run-id>
pytest
```

The bundled scripted agent terminates without claiming a repair; therefore the reference run normally fails its required checks. This is deliberate. PASS is never fabricated to demonstrate presentation.

## Architecture

```text
Task -> Agent -> Tool Gateway -> Isolated Workspace -> Device
                                                |
                                      Evidence Collector
                                                |
                                      Independent Judge -> Result
```

Agent adapters are vendor-neutral. The v0.1 adapter is deterministic and intended for harness tests. Shell and ADB access pass through a logged gateway with explicit working directories, environment allowlists, timeouts, redaction, and separate full-output artifacts. The judge configuration is copied into a judge-only run area and is never included in agent context.

See `SPEC.md`, `OPERATOR_POLICY.md`, `TASK_FORMAT.md`, and `RESULT_FORMAT.md` for normative semantics.

## Status

v0.1 provides task validation, a scripted-agent loop, controlled subprocess/ADB tools, JSONL transcripts, run artifacts, declarative evidence checks, independent re-judging, and deterministic tests. Container isolation, production model adapters, authenticated hidden-task packaging, and robust automated video evidence collectors are future work.

