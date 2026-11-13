# prereg real case: stampwatch PLAN_v4 against the first rule-4 read

Witness: the host's activity record (github_activity_20261113.json): the first push carrying commit 2eb0da1 (PLAN_v4) is at
2026-11-13T18:31:20Z (head 2eb0da1).
Run: the first ibm-read output file (stampwatch_work/read.json on the Mac) was created at 2026-11-13T18:31:28.9Z (file birth time).
Class user_file: a house file, self-held.
Gap: 8.9 s. Tolerance 120 s (default). Outcome: CANNOT_TELL (STRADDLES_EDGE).
PLAN_v2 wrote the expectation as BEFORE. It does not read BEFORE; this is reported, not tuned. The read was started in the command after
the push, which leaves no margin that a host clock compared against a local file clock can resolve.

## Corrections after the referee's pass (beside the first reading, not over it)

- The run time is a first-output time (the result file's birth), not the run's start: the read began before 18:31:28.9Z, so the true
  push-to-start gap is at most 8.9 s and could be negative. A first-output time can never support BEFORE. Reading stands: CANNOT_TELL.
- Witness class: the first reading used a saved activity record (user_file). Re-fetched live through prereg's own paging fetch on
  13 Nov: first push carrying 2eb0da1 at 2026-11-13T18:31:20Z, ref refs/heads/main, public repository, 1 page read, 0 pushes not
  checkable locally, no later force push dropping it. It matches the saved record (github_activity_live_refetch_20261113.json).
- v2's "expected BEFORE" was never computed: push and read ran one after the other, so the gap was always going to be seconds.

# prereg real case 2: the 31 Oct keystone preregistration (expectation written by the referee before reading)

Expectation (referee, 13 Nov): BEFORE impossible (the 42 s is commit to job, and a push can only come at or after the commit); STRADDLES_EDGE
if pushed within 78 s of the commit; AFTER beyond that; NOT_RELEASED if the host has no record.
Found: repository ~/bones-forge/the_show/runs/2026-10-31-keystone (local git). Plan commit 0663d84 at 2026-10-31T19:06:58Z, hashes commit
53efdb1 at 19:07:05Z (both commit dates, self-set); first job dbj3oupkdqps738vqag0 submitted 19:07:40Z (fire log, user_file).
The repository has no remote: it was never pushed to a git host. Reading: CANNOT_TELL (NOT_RELEASED). Reported as is.
