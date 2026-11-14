---
name: rubicon
description: Decide what "done" means before the work starts, freeze it, then judge the finished work with three blind seats on a three-by-three grid. A two-to-one split is kept as UNRESOLVED with the minority's reason, never averaged away, and each seat must try to build a way the work passes every check and still fails. Returns MET, MISSED, UNRESOLVED or CANNOT_TELL. Use for any task where "it passed the checks" and "it does what was asked" could come apart, such as a migration, a report, a fix, a data export or an agent run.
---

# Indahl Rubicon

Work can pass every check and still fail. It happens in four ways:
- The finish line was written after the work.
- The checks were written by the same hand as the work.
- A check could never fail.
- A majority vote erased the one reviewer who saw the problem.

This skill closes all four. Before any work starts, it writes down and freezes what "done" means. When the work is finished, three blind seats judge it.

The script `scripts/rubicon.py` keeps the record in `.rubicon/` in the working folder. While a task there has frozen criteria, the plugin's Stop hook interrupts the first attempt to finish when there is no verdict or a row is open, and asks for the open rows to be reported.

**Rubicon is a record and a prompt, not a lock.** A second stop goes through, and an agent that edits `.rubicon/` can defeat it. The freeze time comes from this machine's clock. The worker writes the grid file and the seats report their own check results. It catches a careless "done", not a determined one.

Heuremen LLC, https://indahl.ai. The four outcomes are the ones used on every published number. See https://indahl.ai/standard.

## 1. Cross the line: freeze the criteria before any work

Write a criteria file, one line per criterion, in this exact form:

```
- C1: <what must be true when the work is done> | check: <how it is checked> | fails-on: <a concrete wrong result the check must catch>
```

Rules for the criteria:
- **Each one is about the outcome the person wants**, not about the steps taken. "Every order appears once in the export" is an outcome. "Ran the export script" is a step.
- **Each check names how it is read**: a count, a diff, a command, a page, or a question a person answers.
- **Each `fails-on` is a planted wrong answer** the check must catch, for example a duplicated row, a total off by one cent, or a page that returns 200 but is empty. A check that has never been shown to fire proves nothing.
- **Include at least one criterion in the words of the person who asked**, so the work is judged against the request and not against the worker's reading of it.

Show the criteria to the user, then freeze them:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rubicon.py" freeze criteria.md
```

Freezing records a hash. After this the criteria do not change. A criterion added later goes in with `freeze FILE --after` and is labelled **defined after the work** in every verdict.

## 2. Do the work

Do the task. Keep the frozen criteria in view, but do not run the checks as the judge. The judging comes next, from seats that did not do the work.

## 3. The grid: three blind seats, three questions

Start three seats that do not see each other's answers. If the host can start independent subagents (for example the Task or Agent tool in Claude Code), use three. Give each seat the frozen criteria, the original request and the finished work, and nothing about the other seats. Give each a different stance:
- **Seat A, the witness**, judges from the work and the criteria alone.
- **Seat B, the skeptic**, looks first for what is wrong.
- **Seat C, the outsider**, judges as the person who asked would, with no knowledge of how it was built.

If the host cannot start independent seats, run them one after another, writing each answer down before starting the next. Mark the grid `"independent": false`. The verdict then notes that agreement counts for less.

Each seat answers three questions:
1. **For each criterion:** MET, MISSED or CANNOT_TELL, with a reason. It also reports whether it ran the check against the planted wrong answer and saw the check catch it (`planted_fail_caught`).
2. **Predict whether the person who asked would call this done:** true, false or null, with a reason. This is a model's guess about the asker, not the asker.
3. **Build a way the work passes every check and still fails what was asked.** Give a short description, or an empty string if the seat genuinely could not build one.

Write the answers to `grid.json`:

```json
{ "independent": true,
  "agent_rerun": { "C1": true },
  "seats": [
    { "name": "A", "criteria": { "C1": { "outcome": "MET", "planted_fail_caught": true, "reason": "..." } },
      "done": true, "done_reason": "...", "pass_but_fail": "" },
    { "name": "B", "...": "..." },
    { "name": "C", "...": "..." } ] }
```

Before tallying, open what the seats cite. For every criterion, rerun its check against its planted wrong answer yourself where it can
be run, and record what you saw in the grid's `agent_rerun` field (`{"C1": true}` when your own rerun saw the check catch its planted wrong
answer, `false` when you reran it and the check did not catch it, and no entry when it could not be rerun). The script counts MET only
where your own rerun saw the catch. No entry reads UNRESOLVED as self-reported, and `false` reads UNRESOLVED as a check that missed. Where a seat cites a source for a MET or a
pass-but-fail, open it with the source-check procedure (the indahl-source-check skill, if installed). A seat whose only support is
something nobody could open does not count as having shown its answer. Where nothing could be rerun or opened, say so in the report:
the catch is then self-reported.

Then tally it:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rubicon.py" grid grid.json
```

How rows are read:
- **All three seats agree:** the row takes that outcome.
- **Two against one:** the row is **UNRESOLVED**. The minority seat, what it said and its reason are kept in the row. The third answer is the one most often thrown away, so this skill keeps it.
- **Three different answers:** CANNOT_TELL.
- **MET without your own rerun seeing the catch:** UNRESOLVED. No `agent_rerun` entry reads as self-reported, and `false` reads as a check that missed.
- **MET where a seat voting MET did not report the catch:** UNRESOLVED, with that seat named. A seat contradicting its own vote is dissent, and dissent is kept.
- **A seat answer that is missing, or an outcome other than MET, MISSED or CANNOT_TELL:** the grid is refused until it is fixed. Nothing falls through to CANNOT_TELL.
- **Any seat builds a way to pass every check and still fail:** the Q3 row is UNRESOLVED. The criteria have a hole until a criterion closes it.

The overall verdict is MET only when every row is MET. Otherwise it is MISSED if any row missed, UNRESOLVED if any row is open, and CANNOT_TELL otherwise.

## 4. Report, and close or acknowledge every open row

Report the verdict row by row. For each UNRESOLVED row, quote the minority seat's reason or the pass-but-fail description.

When the seats' Q2 prediction is anything but a unanimous MET, ask the person who asked whether they call it done, and record their answer as its own row:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rubicon.py" person yes|no "what they said"
```

It is never mixed into the seat count, so a split Q2 stays open after the person answers yes. Close it by acknowledging Q2 and citing their answer, for example `rubicon.py ack Q2 "the person said it is done, see Q2_PERSON"`. A new grid clears the person's answer, because it was about older work, so ask again after a re-run. Then, for every open row (UNRESOLVED or CANNOT_TELL), do one of two things:
- **Close it:** fix the work, or add a criterion with `freeze FILE --after` that closes the hole, then run the grid again.
- **Acknowledge it:** if the person decides it does not matter, record their reason with `rubicon.py ack ROW "reason in a sentence"`. The row stays open in the record, with the reason beside it. Acknowledging is not resolving.

Never report the task as done while a row is open. Say instead which rows are open and why.

## What this does not do

It does not judge whether the criteria were the right ones to want. It asks for them to be fixed before the work, for each check to be shown catching a wrong answer, and for disagreement to be kept. Seats from one model share blind spots, so their agreement counts once, not three times, and the verdict says which seats were used. Q3 reading MET means no seat built a way to pass and still fail. It does not show that none exists.
