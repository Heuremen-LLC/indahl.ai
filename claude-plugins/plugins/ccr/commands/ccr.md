---
description: Custody chain receipts. Start a chain, approve or release files, ask who wrote a file, or verify the record.
argument-hint: init | approve PATH [--lines A-B] | release PATH... | why PATH | verify | anchor
---
Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ccr.py" $ARGUMENTS` (use `python` where `python3` is unavailable) and report the output plainly.

- For `release`, list each approval's outcome (SAME, MOVED, CHANGED, CANNOT_TELL or GAP) with its reason, and the lines shipped outside any approval. Do not summarise MOVED as SAME.
- For `why`, give the attribution exactly as recorded (WRITTEN_BY, RACE or UNATTRIBUTED). Cause is a judgement. Do not state one unless the user asks you to judge it, and then label it as your judgement and name the entries it rests on.
- For `verify`, list every problem. An empty problem list holds only up to the last anchor and for the sessions the cross-check saw.
