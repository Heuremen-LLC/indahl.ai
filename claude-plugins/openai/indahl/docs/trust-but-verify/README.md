# indahl-trust-but-verify

Quiet is not success. After any action that says it worked, this skill reads the effect back from where it should have landed: the
commit on the remote, the content of the published file, the rows in the table, the text on the live page, the time of the job's
newest output. Each action gets one of four outcomes: VERIFIED, FAILED, NOTHING_RETURNED or CANNOT_TELL. It can also scan scripts for
the patterns that turn failures into silence (output captured and status ignored, swallowed errors, a guard that swaps in a no-op,
rows dropped without a count, two copies of one truth with nothing comparing them, liveness judged by a process existing, a watcher
with no heartbeat).

- `/trust-but-verify <action or pipeline>`

Built from our own operations record: in three weeks we logged more than a hundred cases of this one family, including a push that
reported success over a refused commit, a page that drifted from the library it mirrors, and a scheduler that silently replaced new
jobs with a no-op.

## Services this plugin contacts

None. It runs inside your session.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.
