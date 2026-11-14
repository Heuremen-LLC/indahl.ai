---
name: relay
description: Run long multi-step unattended work as a chain of stages with dependencies, machine lanes, recorded exit codes, explicit blocked states and an end-of-run handoff. Use for training ladders, eval sweeps, data pipelines, or any work that spans machines or sessions and must not fail silently. Use when someone asks about relay, a stage chain, or an overnight run.
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/relay/relay-9d2e36720036.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/46c113e5fedcd0c5292224491ad34de86d2c3af1/claude-plugins/src/relay/scripts/relay.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != '9d2e36720036b69f1ecb857405e4c2067b4137c8db716827579a8e54c8cb63f0')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/46c113e5fedcd0c5292224491ad34de86d2c3af1/claude-plugins/src/relay/scripts/relay.py (sha256 9d2e36720036b69f1ecb857405e4c2067b4137c8db716827579a8e54c8cb63f0).


Data sent: none. The plugin runs locally and sends nothing anywhere unless a stage you write sends it.

# relay

Script: `$HOME/.cache/indahl-plugins/relay/relay-9d2e36720036.py` (Python 3.9 or later, standard library only).

## When to use it

Use it for long unattended work with several steps, where later steps need earlier ones, where some steps need a particular machine, and where you want an honest record in the morning. Examples are a training ladder followed by an eval, a sweep over many models, or an ingest then clean then report pipeline. For one short task, just run it.

## The model

A chain is a JSON file holding a list of stages. Each stage has these fields.

- `id`: a unique name.
- `cmd`: the command as an argument list, for example `["python3", "train.py", "--lr", "1e-5"]`.
- `after`: ids that must finish with exit code 0 first.
- `lane`: a name for a machine or resource. One stage runs per lane at a time and different lanes run in parallel. Default lane is `default`.
- `cwd`: working directory, relative to the chain file unless absolute.
- `finally`: true for a stage that runs once every other stage is done, failed or blocked.
- `decide`: true by convention for a stage that edits the chain (see below).
- `env`: optional extra environment variables.

Every stage sees `RELAY_CHAIN` (path of the chain file) and `RELAY_STAGE` (its own id).

## Running it

`relay.py tick CHAIN.json` does one pass. It records finished stages, marks stages with a failed upstream as BLOCKED, and starts every stage whose dependencies are done and whose lane is free. It is idempotent and does not wait. There is no timer or daemon inside relay. Something you own must call `tick` repeatedly, such as cron, launchd, a CI schedule or a shell loop. Calling it more often costs nothing.

`relay.py status CHAIN.json` lists every stage with one of these states: waiting, running, done rc 0, failed rc N, or BLOCKED, with start and end times. It exits 1 if any stage failed or is blocked.

`relay.py add CHAIN.json STAGE.json` appends one stage and refuses a duplicate id or an unknown dependency.

State is written beside the chain as `CHAIN.state.json`. Exit codes and logs are in `CHAIN.relay/rc/` and `CHAIN.relay/logs/`.

## Outcomes are recorded, never inferred

A stage runs inside a small wrapper that writes the command's own exit code to a file. Done means that file says 0. Failed means any other code. If a process disappears without writing its code, for example after a reboot or a kill, the stage reads FAILED (no rc), never done. A stage whose dependency failed is BLOCKED and says which one. Nothing is skipped quietly and nothing retries on its own.

## Decide stages

A decide stage is an ordinary stage that looks at a result and appends the next stage. For a ladder, an eval stage writes its scores to a file, then a decide stage reads them and calls `relay.py add "$RELAY_CHAIN" next_stage.json` with the next rung, which depends on the decide stage. The next tick picks it up. Keep the rule in the decide script, write it down before the run, and have it print what it chose. If it adds nothing, the ladder ends.

## The finally and handoff stage

A `finally` stage runs after everything else has reached done, failed or blocked, so it runs even when the run broke. Use it to write the summary for the next session. The handoff is optional. Without it, `status` is the record.

An example that asks Claude Code to write the summary from the record:

```json
{"id": "handoff", "finally": true, "lane": "default",
 "cmd": ["sh", "-c", "claude -p \"$(cat handoff_prompt.md)\" > MORNING.md"]}
```

Write `handoff_prompt.md` so it tells Claude to run `relay.py status CHAIN.json`, read the logs and result files it names, and write what finished, what failed, what was blocked, and what to do next. Tell it to quote numbers only from those files. The handoff is written from the record, not from memory of the run.

## How this differs from re-feeding one prompt in a loop

A loop that sends the same prompt again knows only what the model remembers and what it chooses to say. A chain adds the following.

- Dependencies: a step starts only when its inputs finished with code 0.
- Lanes: work for different machines runs in parallel, work for one machine runs one at a time.
- Recorded outcomes: exit codes are in files, so success is never a guess from a log line.
- Explicit blocked states: a failure stops its dependents visibly and the rest of the chain keeps going.
- A handoff written from the record, so the next session starts from facts.

## Checks

Run `python3 $HOME/.cache/indahl-plugins/relay/relay-9d2e36720036.py selftest` to confirm it works on the machine. It plants chains in a temporary directory and checks the rules above.
