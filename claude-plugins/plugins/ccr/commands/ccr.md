---
description: Custody chain receipts. Start a chain, approve or release files, ask who wrote a file, or verify the record.
argument-hint: init | approve PATH [--lines A-B] | release PATH... | why PATH | verify | anchor
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/ccr/ccr-544d028599e4.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/798d508c842d2b97459c4d4efb46d4a3ece8ce08/claude-plugins/src/ccr/scripts/ccr.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != '544d028599e41661bdf2f5fbb8d9419435d0cec4e0040877ef2e38102a669d5d')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/798d508c842d2b97459c4d4efb46d4a3ece8ce08/claude-plugins/src/ccr/scripts/ccr.py (sha256 544d028599e41661bdf2f5fbb8d9419435d0cec4e0040877ef2e38102a669d5d).

Run `python3 "$HOME/.cache/indahl-plugins/ccr/ccr-544d028599e4.py" $ARGUMENTS` (use `python` where `python3` is unavailable) and report the output plainly.

- For `release`, list each approval's outcome (SAME, MOVED, CHANGED, CANNOT_TELL or GAP) with its reason, and the lines shipped outside any approval. Do not summarise MOVED as SAME.
- For `why`, give the attribution exactly as recorded (WRITTEN_BY, RACE or UNATTRIBUTED). Cause is a judgement. Do not state one unless the user asks you to judge it, and then label it as your judgement and name the entries it rests on.
- For `verify`, list every problem. An empty problem list holds only up to the last anchor and for the sessions the cross-check saw.
