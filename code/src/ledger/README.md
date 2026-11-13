# Ledger ("Heath Ledger")

One row per public number or claim. The ledger is the state; the paper, heuremen.org, the QIA bill, indahl.ai,
the messages and the Zenodo form follow it.

- `ledger.jsonl` — the rows. Each: the claim, value and interval, outcome (ABOVE / BELOW / CONSISTENT / CANNOT_TELL,
  or RECORD for what a vendor record shows), the file that produces the number (and the exact text it must contain),
  every surface it is printed on (and the exact text there), status (live / withdrawn / cannot_tell), and a dated
  history of every change with its evidence.
- `ledger.py` — the only way to change a row. `list`, `show ID`, `add`, `set`, `on`, `off`, `withdraw`, `cannot_tell`.
  A withdrawal is refused without evidence that exists and the test that was run; an untested cut can only become
  cannot_tell. Nothing is ever deleted.
- `check_ledger.py` — compares every surface with the ledger. MISSING: a live row is no longer printed where it says.
  ZOMBIE: a withdrawn row is still printed. SOURCE: the producing file no longer contains the number. `--coverage`
  counts the decimal numbers on each surface that no row covers yet.

The order is always: ledger edit, then surface edit, then check_ledger.py, then deploy. Both site repos run
check_ledger.py as a pre-commit hook and refuse a commit with drift. This folder is its own git repo, so the
ledger's history can be read back with `git log -p ledger.jsonl`.
