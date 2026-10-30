# Check block

A check block is a short, dated entry that a reading carries before it enters a results file, a paper, a page or a public ledger.
Each line is a required field. A line is answered when it starts with holds:, fixed:, caught:, n/a: or cannot tell: and says what was
checked. A blank, or a line that only says "ok", does not pass.

We built it on 30 October 2026 from the mistakes we logged while measuring. The same questions had been in front of us for weeks, and
many catches still came after a reading had gone out. A question can be skipped. A field that a commit refuses to pass without cannot.

## What is here

- `SPEC.md`: the core fields every reading answers, and the packs for quantum hardware (Q), language-model evaluations (L), public
  copy (P) and live operations (O). Each pack line comes from a mistake we made, with its date.
- `readcheck.py`: writes a template entry and checks that the latest entry is complete.
- `readcheck_hook.py`: a git pre-commit gate. A staged results, readings, hand-check or outcomes file needs the nearest CHECKS.md at or
  above its folder staged in the same commit, with a complete new entry.
- `install_hook.sh`: adds the gate to the pre-commit hook of the repository you are in, keeping any hook already there.
- `test_gate.sh`: builds a throwaway repository and shows the gate refuse and pass, case by case.
- `example/CHECKS.md`: a real entry, from our pass over every page of indahl.ai with this block on 30 October 2026.

## Use

```
python3 readcheck.py new path/to/run --packs L,P --what "what the reading is"
# answer every line in path/to/run/CHECKS.md, then
python3 readcheck.py check path/to/run/CHECKS.md

sh install_hook.sh     # from inside your repository
sh test_gate.sh        # watch it refuse and pass
```

The core is always required. Add the packs that fit the reading. A skip is allowed and goes on the record:
`READCHECK_SKIP="why" git commit ...` writes the reason to `.git/readcheck_skips.jsonl`. Set `READCHECK_PATTERN` to a regular
expression to change which file names count as readings.

Python 3.8 or later, standard library only. Our own release ledger runs the same check, so a new public number, or a change to one,
is refused without a complete entry.

## Where the fields come from

Faults, the failure modes we catalogued in our own measurement work: https://heuremen.org/faults.pdf

Guards, the procedures against them: https://heuremen.org/guards.pdf

License: LICENSE.txt in the repository root.

Heuremen LLC
