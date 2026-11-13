---
description: Write, fill or verify a Standards check block (CHECK.json) for a reading before it is committed
argument-hint: new <folder> "<the reading>" | verify <folder> | staged
---

Run the readcheck tool for: $ARGUMENTS

- `new <folder> "<reading>"`: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/readcheck.py" new <folder> --what "<reading>"`, then fill every
  REQ-01 to REQ-13 answer in the new CHECK.json from what was actually done for this reading (read the code, the data and the run logs;
  never answer from memory). Each answer says what was checked: "holds: <what>", "not applicable: <why>", or what was found and fixed.
  If a requirement was not met, say so in its answer and fix the reading where you can.
- `verify <folder>`: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/readcheck.py" verify <folder>` and report what is missing.
- `staged`: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/readcheck.py" staged` in the repository and report every staged reading without a
  complete block.

The gate hook refuses a `git commit` that stages a reading (files named like *results*, *outcomes*, *readings*, RESULTS*.md) unless a
complete CHECK.json sits in its folder or above. A repository can set its own file patterns in `.readcheck.json` as {"globs": [...]}.
