# Indahl Rubicon

Work can pass every check and still fail. Indahl Rubicon is a gate that asks for the four things that usually go missing, and keeps a record of whether they were done:

| How it happens | What the gate asks for | Who shows it |
|---|---|---|
| The finish line is written after the work | Criteria frozen with a hash before work starts. A criterion added later is labelled "defined after the work" and the grid must run again. | Self-reported: the freeze time is this machine's clock. |
| The checks are written by the same hand as the work | Three blind seats judge the finished work. | Self-reported: the worker writes the grid file and says whether the seats ran independently. |
| A check that cannot fail passes anything | Every criterion names a planted wrong answer, and every seat voting MET must report its check catching it. | Self-reported by the seats, not verified by the script. |
| A majority vote erases the dissent | A two-to-one split reads UNRESOLVED, with the minority's reason kept in the row. | Enforced by the tally. |

Each seat also tries to build a way the work passes every check and still fails what was asked. If any seat builds one, the criteria have a hole, and that row stays UNRESOLVED until a criterion closes it. A MET there means no seat built one. It does not show that none exists.

Outcomes: **MET**, **MISSED**, **UNRESOLVED**, **CANNOT_TELL**.

**Rubicon is a record and a prompt, not a lock.** It interrupts the first attempt to finish and asks for the open rows to be reported. A second stop goes through, and an agent that edits `.rubicon/` can defeat it. It catches a careless "done", not a determined one.

## Install

```
/plugin marketplace add Heuremen-LLC/indahl.ai
/plugin install indahl-rubicon@heuremen
```

Then run `/rubicon <the task in one sentence>`.

## What is in it

- `skills/rubicon/SKILL.md`: the procedure. Freeze the criteria, do the work, run the three-by-three grid, ask the person when the seats are not sure, then close or acknowledge every open row.
- `scripts/rubicon.py`: keeps the record in `.rubicon/` in the working folder. It freezes the criteria, refuses a grid with a missing or unreadable seat answer, tallies the grid, records the asker's own answer as its own row (`person`), records acknowledgements and runs the planted selftest (`python3 scripts/rubicon.py selftest`, 34 cases). Standard library only, and nothing is sent anywhere.
- `hooks/hooks.json`: a Stop hook. It applies only in a folder where criteria have been frozen. There it interrupts the first attempt to finish while there is no verdict, while the verdict was made against older criteria, while the verdict is MISSED, or while a row is UNRESOLVED or CANNOT_TELL and not acknowledged. It never blocks twice in a row, so it cannot trap a session.

An acknowledged row stays open in the record, with the reason beside it. Acknowledging is not resolving.

## Limits

- The gate does not judge whether the criteria were the right ones to want.
- Seats from one model share blind spots, so their agreement counts once, not three times. Every verdict records which seats were used and whether they ran independently.
- The seats' answer on whether the person would call it done is a model's guess about the asker, not the asker. When it is not a unanimous yes, the skill asks the person and records their answer as its own row.

Heuremen LLC, https://indahl.ai. Refereed before release by Sage, the outside referee on our work. MIT licence.

## Credits

Windows fix, 14 Nov 2026: Sage asked, Bones found and fixed. Sage, the outside referee on our work, asked whether `python3` resolves on Windows. Bones ran it on a Windows machine, found it was the Microsoft Store stub that runs nothing (exit 49), so the hook would fail without a word and the check would be silently off, and fixed it in every plugin hook. The hook now falls back to `python`.

Sage also refereed the design before release. She found that adding a criterion after a verdict left the old verdict passing, that CANNOT_TELL rows could not be acknowledged, that missing seat answers fell through instead of refusing, and that the first README described a lock where the code is a record and a prompt.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/1f5b4469ac778f107d10f74ba87286861e8f8a50/claude-plugins/src/rubicon/scripts/rubicon.py
  sha256 106205719ddcdfc9d2724380b8a713b8e24e98b118c4e848fed446387bf8405c

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
