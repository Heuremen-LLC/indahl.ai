---
name: silent-failure-guard
description: Quiet is not success. Use after any action that reports it worked - a push, commit, deploy, upload, sync, migration, scheduled job, import, publish or send - and before telling anyone it is done. Reads the effect back from where it should have landed, not from the exit code, an "ok" line or the absence of errors. Also use when asked whether a pipeline, watcher or automation is healthy, or to scan scripts for patterns that hide failures.
---

# Silent failure guard

A failure that makes no noise looks exactly like a success. Exit codes, "ok" lines and empty error logs describe the tool, not the
result. The only proof an action worked is its effect, read from where the effect should be. Heuremen LLC, https://indahl.ai.

## 1. For each action, name the effect and where it lands

Before reading anything back, write one line per action:

- **Claimed:** what the tool said (the "ok", the exit code, the message).
- **Effect:** what should now be true in the world (this commit is on the remote, this file has this content, this table has these
  rows, this page shows this text, this job wrote output after this time).
- **Where:** the place to read it from. The target itself, never the local copy you just wrote, never the tool's own summary.

## 2. Read it back, fresh

- Read from the target: the remote API, the live URL, the database, the output file's modification time and content.
- Beat the caches: CDNs and raw-file hosts can serve the old version for minutes. Use an API read, a cache-busting query or a
  second read later. A stale read is CANNOT_TELL, not FAILED and not VERIFIED.
- Compare like with like: content hash against content hash, row count against row count, the exact text against the exact text.

## 3. Look where failures hide

Each of these has turned a failure into silence in real pipelines:

1. **Output captured, status ignored.** A command run with its output captured and its exit status never checked. A refused commit
   followed by a push of the old head prints "push ok".
2. **Errors swallowed.** A try/except (or `|| true`, or `2>/dev/null`) around the step that failed. An undefined name inside a
   try means the guarded action never runs and nothing says so.
3. **A guard that replaces the job.** An allow-list, feature flag or wrapper that silently substitutes a no-op for the real command.
4. **Rows dropped without a count.** A parser or filter that skips what it cannot read. Count in, count out, and count the
   difference by reason.
5. **Two copies of one truth.** A page and the library it mirrors, a mirror and its source, a config in two places. When one
   changes and nothing compares them, they drift quietly.
6. **Liveness by existence.** A process running, a log file present, or a status of "on schedule" is not work done. Liveness is
   the newest completed output and its time.
7. **A watcher with no heartbeat.** No alert is only good news if the watcher is alive and would fire. Plant a known-bad case it
   must catch, or check its own last run.

## 4. Four outcomes per action, never two

- **VERIFIED:** the effect was read from the target and matches.
- **FAILED:** the effect is absent or wrong. Say what was found instead.
- **NOTHING_RETURNED:** the read-back returned nothing (no response, empty result). This is not a pass.
- **CANNOT_TELL:** the effect could not be read (no access, cache, no way to observe it). Say what would settle it.

Silence is CANNOT_TELL at best. Nothing is reported done until it is VERIFIED.

## 5. Scan scripts for hidden failures (when asked, or when a pipeline is suspect)

Search the code for the patterns in section 3 and list each hit with file and line: subprocess calls that capture output without
checking the return code, bare or broad excepts that pass, `|| true`, `2>/dev/null`, `set +e` regions, writes whose result is not
read back. Do not rewrite them unasked. For each, say what failure it could hide and the smallest fix (check the status, count the
drops, read the effect back).

## Report

A table: action, claimed, effect read back (and where), outcome. Then the hidden-failure patterns found, if a scan was run.
Lead with anything FAILED or NOTHING_RETURNED.
