# indahl-relay

Run multi-stage unattended work as a chain of stages with dependencies, machine lanes, recorded outcomes and an optional end-of-run handoff. Built for training ladders, eval sweeps and data pipelines. It is not a single-prompt loop.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai

Runs locally. Nothing is sent anywhere unless a stage you write sends it.

## Commands

- `relay.py tick CHAIN.json` starts every stage whose dependencies finished with exit code 0 and whose lane is free, and records each finish.
- `relay.py status CHAIN.json` lists every stage as waiting, running, done rc 0, failed rc N, or BLOCKED, with times.
- `relay.py add CHAIN.json STAGE.json` appends a stage and refuses a duplicate id or an unknown dependency. A decide stage calls this to add the next step.
- `relay.py selftest` runs planted chains in a temporary directory.

Python 3.9 or later, standard library only. In Claude Code the command is `/relay`.

## A chain

```json
[
  {"id": "train", "lane": "gpu", "cmd": ["python3", "train.py"]},
  {"id": "eval", "after": ["train"], "lane": "gpu", "cmd": ["python3", "eval.py"]},
  {"id": "handoff", "finally": true, "cmd": ["sh", "-c", "claude -p \"$(cat handoff_prompt.md)\" > MORNING.md"]}
]
```

The handoff stage is optional.

## No timers inside

relay has no timer and no daemon. `tick` does one pass and exits, and it is safe to call again at any time. Call it from cron, launchd, a CI schedule or a loop you own.

## Failures are never silent

Each stage's outcome is its own exit code, written to a file. A process that vanished without writing it reads FAILED (no rc), not done. A stage whose dependency failed is BLOCKED and listed. Status shows every stage, not only the ones that passed.

## Services this plugin contacts

None. The plugin reads no personal data and stores nothing outside the folder beside your chain file.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.
