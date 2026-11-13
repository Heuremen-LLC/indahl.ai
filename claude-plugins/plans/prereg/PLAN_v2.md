# prereg: plan amendment v2, before code

Heuremen LLC, 13 November 2026. Amends PLAN.md, which stays as it was. Answers the outside referee's pre-code pass (verdict MOVES):
glue stays folded in as `prereg cover`.

## The run side is usually self-held

Every `check` outcome carries the run time's witness class: `host_read` (fetched from the provider by job id at check time, raw response
saved), `user_file` (a log or record the user supplied), `wrapper` (written by `prereg run` at start: self-held but not typed), or
`user_stated` (`--first-run TIME`). BEFORE reads "the witnessed push precedes the first run in the supplied record", never "precedes any
run". METHOD_UNSTATED is kept for a run record with no parseable start; a user-given time reads normally with class `user_stated`.
Not tested: earlier runs (pilots, dry runs) absent from the record; prereg cannot see them.

## Sealed, not passed at check time

SEAL.json holds `tolerance_s` (default 120) and `run_record_kind` (ibm_job, ci_log, wrapper, user_stated). `check` reads both from the
seal and refuses a flag or a record of a different kind. Each plan version is a new SEAL file beside the first, never an edit (REQ-10).

## Forking plans

`check` lists every SEAL file in the repository's history that was pushed before the run, with the files each names, and prints how many
of them name a file in the run's cover set when that is more than one. Not tested: that the cited plan was the only plan.

## The witness

- `witness` runs right after the push: it saves the host's raw response and its sha256, and requests an archive.org capture of the public
  API URL (an outside copy, not a timestamp chain).
- The push is bound to the seal: the pushed head must have the seal commit as an ancestor (git merge-base --is-ancestor), and the
  repository in the response must match the seal's remote. A later force-push that drops the commit is recorded.
- Retention of the host's activity record is not assumed; a witness read after it is gone reads CANNOT_TELL (NOT_RELEASED).
- Private repositories: the record is held by the host but not publicly checkable; the output says so.

## Committed bytes

`seal` refuses a named file with uncommitted changes and records both the git blob id and the sha256 of the committed bytes
(git cat-file). `verify` reports blob drift and working-tree drift separately.

## cover needs a wrapper

`prereg run -- CMD` records at start: the command, files named in argv, cwd and host; `git status` with untracked and ignored files;
the sha256 of every script and config in the repository; its own start time (class `wrapper`). `cover` compares the wrapper's record
with the seal. Files outside the repository are listed by path where argv names them. Not tested: files a process opened that no record
names (prereg does not trace system calls).

## Gates

`seal` writes a commit to the user's repository: the skill asks before it. The skill tells the agent never to push; the guard that holds
regardless is Claude Code's permission prompt for Bash, which should stay on. Times with no offset are refused (as in stampwatch).

## Real cases, expected outcomes written now

- stampwatch rule 4: PLAN_v4 (commit 2eb0da1, pushed 2026-11-13T18:31Z per the host's activity record) against the start of the first
  test-pair read. The start time comes from a house file (the result file's creation and the run log), class `user_file`; expected BEFORE,
  stated as recall on a known-answer house case. It tests witness and check only (it was never sealed with prereg). If it does not read
  BEFORE, that is reported, not tuned.
- The 31 Oct near-edge case (a plan committed 42 s before the first job): expected CANNOT_TELL (STRADDLES_EDGE) if its push record exists
  on the host. HELD until the referee names the repository and commit; it is not reconstructed from memory.
