# indahl-silent-failure-guard

Quiet is not success. After any action that says it worked, this skill reads the effect back from where it should have landed: the
commit on the remote, the content of the published file, the rows in the table, the text on the live page, the time of the job's
newest output. Each action gets one of four outcomes: VERIFIED, FAILED, NOTHING_RETURNED or CANNOT_TELL. It can also scan scripts for
the patterns that turn failures into silence (output captured and status ignored, swallowed errors, a guard that swaps in a no-op,
rows dropped without a count, two copies of one truth with nothing comparing them, liveness judged by a process existing, a watcher
with no heartbeat).

- `/silent-failure-guard <action or pipeline>`

## The watch guard for Claude Code (hook)

Claude Code waits on long work in two ways: a Bash command run in the background, whose end arrives as "completed (exit code 0)",
and the Monitor tool, whose output lines arrive as notifications. Both report what the wait did, not what the job did. Seven ways
that turns a failure into silence, all of which we hit in our own sessions:

1. **Success-only wait.** `until grep -q "DONE" job.log; do sleep 5; done` never exits if the job crashes, because "DONE" never
   appears. No notification comes, and silence reads as "still running". The Monitor tool's own description warns about this.
   Nothing enforced it.
2. **Success-only stream.** `tail -f job.log | grep "DONE"` in a Monitor produces no event for a crash, a traceback or a refusal.
3. **Buffered stream.** `tail -f job.log | grep pattern` without `--line-buffered` holds matches in grep's buffer, so they never arrive.
4. **Exit code read as the verdict.** A background wait that exits 0 says its condition matched. If the matched line itself reports a
   failure, the notification still says exit code 0. The line has to be read.
5. **Self-matching pgrep.** `until ! pgrep -f "ship.sh"; do sleep 10; done` never ends. The shell running the wait carries "ship.sh"
   in its own command line, so pgrep -f always finds it. Wait on the PID (`while kill -0 PID`) or bracket one letter (`"[s]hip.sh"`).
6. **Padded count.** `[ "$(wc -l < f)" = "2" ]` never matches on macOS, because wc pads its count with spaces. Compare numbers (`-eq`).
7. **No deadline.** A background loop whose condition can never come true waits forever and looks exactly like a healthy wait.
   Every background wait needs a deadline (`end=$((SECONDS+1800))` and `[ $SECONDS -ge $end ]`, a counter, or `timeout`).

Cases 5 to 7 were added on 14 Nov 2026 after five of our own waits hung overnight. The first version of this hook let all of them
through, and its selftest marked the self-matching pgrep wait as safe.

The hook (`hooks/hooks.json`, `scripts/watch_guard.py`) runs before every background Bash command and every Monitor. It refuses
cases 1 to 3 and 5 to 7 with a message telling the model how to fix the watch: add the failure states to the same pattern, add
`--line-buffered`, wait on the PID, compare numbers, give the wait a deadline. It allows anything run in the foreground. `python3 scripts/watch_guard.py selftest` runs its planted cases.

The hook ships in the version from our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`, then
`/plugin install indahl-silent-failure-guard@heuremen`). The plugin directory accepts command hooks only from Verified organizations,
so the directory copy carries the skill only.

Built from our own operations record: in three weeks we logged more than a hundred cases of this one family, including a push that
reported success over a refused commit, a page that drifted from the library it mirrors, and a scheduler that silently replaced new
jobs with a no-op.

## Services this plugin contacts

None. It runs inside your session.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/c6d8603c678d2053aaa4d184ddddb6affd93e75e/claude-plugins/src/silent-failure-guard/scripts/watch_guard.py
  sha256 9d791982654be52e6adb59c31ea2980c47a19836f2faebea392032c5e0295014

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
