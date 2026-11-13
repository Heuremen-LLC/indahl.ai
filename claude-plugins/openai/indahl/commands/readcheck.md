---
description: Write, fill or verify a Standards check block (CHECK.json) for a reading before it is committed
argument-hint: new <folder> "<the reading>" | verify <folder> | staged
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/readcheck/readcheck-cc0e26802ddb.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/readcheck/scripts/readcheck.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != 'cc0e26802ddbcc157def5ea0ee90e8d4a9b2c516336658f34072882c03c90592')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/readcheck/scripts/readcheck.py (sha256 cc0e26802ddbcc157def5ea0ee90e8d4a9b2c516336658f34072882c03c90592).


Run the readcheck tool for: $ARGUMENTS

- `new <folder> "<reading>"`: run `python3 "$HOME/.cache/indahl-plugins/readcheck/readcheck-cc0e26802ddb.py" new <folder> --what "<reading>"`, then fill every
  REQ-01 to REQ-13 answer in the new CHECK.json from what was actually done for this reading (read the code, the data and the run logs;
  never answer from memory). Each answer says what was checked: "holds: <what>", "not applicable: <why>", or what was found and fixed.
  If a requirement was not met, say so in its answer and fix the reading where you can.
- `verify <folder>`: run `python3 "$HOME/.cache/indahl-plugins/readcheck/readcheck-cc0e26802ddb.py" verify <folder>` and report what is missing.
- `staged`: run `python3 "$HOME/.cache/indahl-plugins/readcheck/readcheck-cc0e26802ddb.py" staged` in the repository and report every staged reading without a
  complete block.

The gate hook refuses a `git commit` that stages a reading (files named like *results*, *outcomes*, *readings*, RESULTS*.md) unless a
complete CHECK.json sits in its folder or above. A repository can set its own file patterns in `.readcheck.json` as {"globs": [...]}.
