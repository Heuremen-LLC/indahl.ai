# prereg: plan, written before any code

Heuremen LLC, 13 November 2026. Idea and scope from Sage (outside referee). This file is pushed before prereg exists.

## What it answers

"Was the plan written before the first run?" with a timestamp the user does not control, and "did the plan cover what actually ran?".
No outside timestamp chain is used (no blockchain, no timestamping service). The outside witness is the push of the sealed plan to the
user's own git host, read back from the host's own record of the push.

## Commands

- `prereg seal FILE...`: writes SEAL.json (each named file's sha256, the git commit that holds them, the remote URL, the local time the
  seal was written, marked self-set) and commits it. It does not push. The skill shows the user the commit and asks before any push;
  pushing is the user's act.
- `prereg witness`: reads the host's own record of when that commit was pushed (GitHub repository activity API; other hosts later) and
  writes WITNESS.json with the raw response saved beside it. A commit date is never used as the witness: it is set by whoever commits.
- `prereg check --first-run TIME | --job-record FILE`: compares the witnessed push time with the first run's start time, read from a job
  record (IBM job metadata, a CI log, a training log's first line) or given by the user, who is then named as its source.
- `prereg verify`: re-hashes every sealed file and lists any that changed after the seal.
- `prereg cover RUN_DIR | --files LIST`: lists files that ran (launchers, configs, scripts, logs named in the run record) whose sha256
  is not in the seal. A seal covers only what it names.

## Outcomes, fixed now

- BEFORE: the witnessed push precedes the first run's start by more than the tolerance.
- AFTER: the first run's start precedes the witnessed push by more than the tolerance.
- CANNOT_TELL with a reason: STRADDLES_EDGE (within the tolerance), NOT_RELEASED (no witness record from the host, or no run record),
  METHOD_UNSTATED (the run's start time has no stated source).
- NOTHING_RETURNED: the host's record could not be read.
Tolerance: 120 s by default (host clocks against run-record clocks); the user may set it before `check`, never after.
`verify` and `cover` report counts and file names, not outcomes.

## Known-good cases

Planted (in a temporary repository with a fake host record): push 1 h before the run (BEFORE); run 1 h before the push (AFTER); 60 s
apart (CANNOT_TELL, STRADDLES_EDGE); no host record (CANNOT_TELL, NOT_RELEASED); a sealed file edited after the seal (verify lists it); a
config that ran but was not sealed (cover lists it); a run time with no source (CANNOT_TELL, METHOD_UNSTATED).
Real: the stampwatch plan in this repository (PLAN.md pushed 2026-11-13T17:26:00Z per the activity record; the first test pair was read
after 2eb0da1 was pushed at 18:31Z): must read BEFORE against the IBM controls run, from the files in plans/stampwatch/witness/.

## Not tested, written now

- Whether the run followed the plan. prereg proves when a file existed on the host, not what the run did.
- The host is trusted: a push record proves the host saw that content at that time, nothing more.
- A plan kept elsewhere (an email, a lab notebook) is outside prereg.

## Scope question for the referee

Sage listed "glue" as its own plugin. This plan folds it in as `prereg cover`, because both read the same seal. If the referee prefers
two plugins, cover moves out unchanged.
