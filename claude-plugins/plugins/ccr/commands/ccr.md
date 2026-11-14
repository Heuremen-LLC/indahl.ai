---
description: Custody chain receipts. Start a chain, approve or release files, ask who wrote a file, or verify the record.
argument-hint: init | approve PATH [--lines A-B] | release PATH... | why PATH | verify | anchor
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/ccr/ccr-a11b0fba5295.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/12a6cc29ae2110efa8e335962d0461a64efd533e/claude-plugins/src/ccr/scripts/ccr.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != 'a11b0fba529516f0e0f602bf333ae13227a6911c49b1bd911b208b6849e3b0d8')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/12a6cc29ae2110efa8e335962d0461a64efd533e/claude-plugins/src/ccr/scripts/ccr.py (sha256 a11b0fba529516f0e0f602bf333ae13227a6911c49b1bd911b208b6849e3b0d8).

Run `python3 "$HOME/.cache/indahl-plugins/ccr/ccr-a11b0fba5295.py" $ARGUMENTS` (use `python` where `python3` is unavailable) and report the output plainly.

- For `release`, list each approval's outcome (SAME, MOVED, CHANGED, CANNOT_TELL or GAP) with its reason, and the lines shipped outside any approval. Do not summarise MOVED as SAME.
- For `why`, give the attribution exactly as recorded (WRITTEN_BY, RACE or UNATTRIBUTED). Cause is a judgement. Do not state one unless the user asks you to judge it, and then label it as your judgement and name the entries it rests on.
- For `verify`, list every problem. An empty problem list holds only up to the last anchor and for the sessions the cross-check saw.
