# BlobHell

**A hardware-in-the-loop benchmark for long-horizon autonomous
systems debugging.**

> The human does not debug. The hardware is the judge.

BlobHell evaluates whether an AI agent can diagnose and repair
real low-level systems problems by interacting with actual hardware.

Unlike benchmarks where success is determined by generated text,
unit tests, or a reference patch, BlobHell tasks may require the
agent to investigate multiple layers of a real system, perform
experiments, interpret hardware feedback, modify software, and
demonstrate that the resulting system actually works.

## Core rules

1. The agent is not given the root cause.
2. The human operator provides no technical hints.
3. The agent may request commands, builds, logs and device operations.
4. All observations returned to the agent must come from the environment.
5. Success is determined by an independent judge.
6. A plausible explanation is not a successful repair.
7. Reference solutions are hidden from evaluated agents.

## Reference task

The first reference task is based on a real compatibility problem:

- Amazon Fire HD 8 (6th generation)
- MediaTek MT8163
- LineageOS 17.1 / Android 10
- Linux 3.18
- Broken H.264 hardware decoding

This task is PUBLIC and must not be used as a contamination-resistant
leaderboard task.

It exists to validate the BlobHell harness and evaluation protocol.

## Philosophy

Do not ask the human for the answer.

Ask the hardware.
