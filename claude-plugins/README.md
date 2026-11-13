# Heuremen LLC plugins for Claude Code

Plugins from Heuremen LLC (https://indahl.ai). Each plugin is named `indahl-...`; its section below uses the short name.

```
/plugin marketplace add Heuremen-LLC/indahl.ai
/plugin install indahl-standards@heuremen
/plugin install indahl-readcheck@heuremen
/plugin install indahl-qia-calibration@heuremen
/plugin install indahl-darkwave@heuremen
/plugin install indahl-data@heuremen
/plugin install indahl-reproduce@heuremen
/plugin install indahl-eval-check@heuremen
/plugin install indahl-prereg@heuremen
```

## Outside text is treated as data

Every plugin that reads outside text (a paper, a kit README, a released file, an API response) tells the agent to treat it as data,
not instructions: if fetched text contains instructions aimed at the agent, it quotes them to you and carries on with the check. This
is an instruction to the agent, not a guarantee. The guards that hold regardless are in code: `--yes` and `--yes-commit`, the tty check
on a paid darkwave submit, and read-only file handling.

Claude cannot start the `/reproduce` or `/darkwave` commands on its own, and the skills tell it never to add `--yes` or `--yes-commit`.
The scripts can still be run from a shell, so keep Claude Code's permission prompt on for Bash: that prompt is the gate that does not
depend on the model. A paid darkwave submit (`measure --yes`) runs only from your own terminal.

## standards

`/standards <arXiv id | DOI | file | claim>` checks a paper or a measured claim against the Standards claim codes F1 to F7
(https://indahl.ai/standard) and returns a recount card. Every code gets one of four statuses: PRESENT, ABSENT, CANNOT_TELL (with a
reason: NOT_RELEASED, UNREADABLE or METHOD_UNSTATED) or NOT_APPLICABLE, or, if its test was not run, is listed as not tested (F7
needs a classical method actually run). Every PRESENT carries a verbatim quote and its location. Any
recompute shows its arithmetic from the paper's printed numbers, with the rounding range. The card says what the paper prints and what
recomputes. It names no cause.

A PRESENT is one reader's proposal with its quote, an erratum candidate to check, not a confirmed finding and not a verdict on the
study or its authors. In our own counts a finding needs two readers. The codes that sort papers are F2, F3, F5 and F6. F1, F4 and F7 are
recorded for context: F1 also fires on routine practice, so read it beside the others rather than alone. Tested blind on two papers
with known findings (all four found); that shows recall on known positives, not a hit rate.

The full Standard, its JSON form and schema ship inside the plugin under `skills/standards-check/references/`.

## readcheck

A gate for research repositories. When Claude Code runs `git commit` and the commit stages a reading (a file named like `*results*`,
`*outcomes*`, `*readings*` or `RESULTS*.md`), the commit is refused unless a complete `CHECK.json` sits in the same folder or above it.
The block has one answer per Standards recount requirement, REQ-01 to REQ-13: 01 name the ruler before the number, 02 write the
baseline down first, 03 state the data source, 04 state the version read, 05 use reading outcomes, 06 give each reading its interval
and level, 07 test the instrument first, 08 publish receipts, 09 name dropped material, 10 publish corrections beside the first
reading, 11 keep CANNOT_TELL as its own result, 12 state what was not tested, 13 print the counts beside every headline share.

The gate checks that every answer is present, not that it is right. It is a Claude Code hook. It recognises `git commit` and
`git -C <dir> commit` in Claude Code's Bash calls, including chained forms such as `git add X && git commit` and `cd repo && git commit`
(checked against everything the chain could add). Commits made by scripts, `git -c ... commit`, subshells or your own terminal are not
caught; run `readcheck.py staged` in your own pre-commit hook for those. The REQ texts are taken word for word from the released
Standard (published as Faults and Guards 2.0.0, DOI 10.5281/zenodo.24164794).

```
/readcheck new results/run7 "the reading this folder holds"
/readcheck verify results/run7
/readcheck staged
```

Set your own file patterns in `.readcheck.json` at the repository root: `{"globs": ["*_scores.csv", "eval_*.json"]}`.
The script also runs on its own: `python3 plugins/readcheck/scripts/readcheck.py --help`.

## qia-calibration

`/qia-check` runs the QIA calibration checker (the same code as `pip install qia-check` 1.0.2) on IBM Quantum calibration records saved in
Qiskit's BackendProperties format.

`/qia-t1t2` measures T1 and a Hahn-echo T2 on chosen qubits in one job on your own IBM Quantum account and compares the ratio with
IBM's published pair (the QIA pack's same-job check). `--selftest` needs no device; `--estimate` prints the QPU seconds and submits
nothing; the paid run (`--yes`) only runs from your own terminal, and Claude cannot start the command on its own.

Every flag and change is in one of two categories: **T1 and T2** (STALE, T2>2T1, PAIR, T1/T2 changes) and **Error figures** (ZERO,
readout-error changes).

- Before a run: STALE (T1 or T2 measured more than 24 hours before the record's update), ZERO (an error value of exactly 0), T2 above
  2 x T1, and PAIR (T1 and T2 measured more than 24 hours apart), for the qubits you name.
- After a run: the record in force at the start, every record stamped during the run, and each change in T1, T2 and readout error.
  A folder that mixes backends is refused unless you name one with `--backend`, so records from different processors are never
  compared as if IBM had recalibrated.

The script is qia-check 1.0.2, byte for byte the release on PyPI (`pip install qia-check`).

Your files are opened read-only and their sha256 is printed before and after. Run on saved files, it opens no network connection;
only `--pull` contacts IBM, with your own saved account. A STALE, ZERO, T2>2T1 or PAIR flag is a flag on a published record, not a
statement about IBM or about your results. Not affiliated with or endorsed by IBM. IBM Quantum and Qiskit are IBM marks, used here only
to name what is checked.

## indahl-data

Every live indahl.ai desk inside Claude Code, through the read-only indahl.ai MCP server (https://indahl.ai/mcp, no key): IBM Quantum
calibration, queue and stability, public time servers, DNS filters, vendor status pages, Hugging Face model sizes and licenses, PyPI
license and install claims, weather and flu forecast calibration, launch slips, link rot, trial reporting, payroll revisions, Fed
projections, model shutdown dates, MLPerf and AILuminate results, and a search over the QIA and IRIS Lists. `/indahl <question>` answers with the count, interval,
outcome and the time it was read. With no question it prints every desk's headline test side by side.

Your questions leave your machine: tool calls go to indahl.ai. The tool list and descriptions are served by indahl.ai when Claude Code
connects; they are not pinned in this plugin. Our server code stores no queries. Cloudflare, which serves the site,
keeps its standard request records. Each answer is a measurement of public data at the time it was read. It is not legal advice and
not a verdict on any vendor, model, package or author. The tools serve the current state: most hold no history (for example,
`ibm_calibration` gives today's medians and 7-day change counts, not last week's medians).

## reproduce

`/reproduce <desk>` fetches that desk's reproduce kit from github.com/Heuremen-LLC/indahl.ai (a sparse checkout of one folder), runs the
kit's own `python3 run.py --check` and reports whether its output matches the published sha256. `/reproduce list` shows every kit.

This runs code downloaded from that repository on your machine. The script prints the commit it fetched and the command, and runs
nothing until you pass `--ref <commit> --yes-commit <commit>` with the commit it printed; if the code moved, it refuses. The MIT
license covers the plugin; a downloaded kit carries the repository's own terms. A matching sha256 shows the kit reproduces its published output with the
desk's own code. It does not show the measurement is right. Tested fresh from GitHub on FLU; every kit is rerun by our own release
gate before each release.

## darkwave-correction

The Darkwave Correction Kit (v1.1.1). It measures the phase turn on untouched qubits after a mid-circuit readout, per readout, and
corrects for it. `/darkwave selftest`
checks the kit on the simulator with no account. `/darkwave measure ... --check` reads the backend with your saved account, builds the circuits and submits nothing. With `--yes`
it submits one 8-circuit job on your own IBM Quantum account and uses your runtime allotment; nothing is submitted without
`--yes`. `/darkwave apply` adds the matching virtual-Z correction to your circuits.
Validated: the self-test on the simulator, and on hardware once, on ibm_kingston on 2 November 2026 (one chip, one calibration
snapshot: the correction gave back 1.012 [0.993, 1.027] of the turn over 113 targets, and 12 % of targets kept more than 1 degree per
readout). Other chips and calibrations are untested. `darkwave_kit.py` is kit v1.1.1: the published v1.1 plus a fix for a crash when printing a target whose
idle coherence is 0 (after the job had run), the docstring wording, and the terminal-only submit. Not affiliated with or
endorsed by IBM. Method and data:
https://doi.org/10.5281/zenodo.23843468.

## eval-check

`/eval-check <claim or path>` checks a language-model evaluation claim, or your own eval run, against twelve house checks: the parser
checked against raw replies first, the setup as part of the result, the repeat floor before any comparison, recounts from released files, dropped items by
reason, judges grading their own labels, paired comparisons, leaks into the prompt, pinned names, aging datasets, and an interval and
outcome on every number. A PRESENT is one reader's proposal with its evidence, not a confirmed finding and not a verdict on the
study, the model or its authors. Nothing is run (a model, a harness, a scorer) without your go.

## prereg

`/prereg` seals a plan in git and later shows, from your git host's own record of the push, whether the plan was pushed before the first
run, and which files that ran the plan did not cover. No outside timestamp chain is used: the witness is the host's push record, never a
commit date (which anyone can set). Outcomes: BEFORE (the witnessed push precedes the first run in the supplied record, never "any run"),
AFTER, CANNOT_TELL (too close for two clocks to separate, no host record, or no stated run time). The tolerance and the run-record kind
are sealed with the plan. Every result names where each time came from; a run time read from the provider (host_read) is not reachable
yet, since prereg has no command that fetches a job by id. `prereg run` wraps the run and records the files present, including ignored
and untracked ones; `cover` lists what ran unsealed. The saved witness hash detects accidental change, not deliberate editing (re-witness
with a live re-fetch). GitHub does not document how long it keeps the activity record: witness right after the push. prereg does not
show that the run followed the plan, or that the cited plan was the only plan. It never pushes; keep Claude Code's permission prompt on.
Plan and real cases: plans/prereg.

## Licenses

These are free to use under the licenses below. They are not open-source licenses.


- `standards`: the Standard text and data, LICENSE-STANDARD.txt (free to use and cite with attribution, including inside prompts and
  tool calls).
- `readcheck`: MIT.
- `qia-calibration`: LICENSE.txt, the same license as `pip install qia-check` (run, copy and change the code with attribution), plus
  NOTICE.txt: loading its text into an AI assistant's context to run the checks is permitted and is not text and data mining.
- `darkwave-correction`: LICENSE.txt (run, copy and change the code with attribution; text and data cited with attribution) and
  NOTICE.txt (in-context use permitted).
- `indahl-data`: LICENSE.txt (plugin files: use, copy and change with attribution; served data: retrieve, quote and cite with
  attribution, no training) and NOTICE.txt (responses in an AI assistant's context are permitted).
- `reproduce`, `prereg`: MIT.
- `eval-check`: LICENSE-STANDARD.txt.

Heuremen LLC · https://indahl.ai
