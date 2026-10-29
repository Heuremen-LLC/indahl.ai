# QIA queue ticker: plan (29 Oct 2026, committed before the first read)
What it shows: for every IBM processor our paid instance can see, the number of jobs IBM reports as pending, read once per hour of Nova ticks (every 9 ticks).
Beside it: the wait our own jobs saw on that processor, measured as the time from created to running in IBM's job record. Median and longest of the last 20 finished jobs, and the age of any job still queued.
Rules:
- Pending count is IBM's number read through the runtime service. We add nothing to it and do not turn it into a predicted wait. IBM publishes no estimate and we publish none.
- Our waits are our jobs only. Different job sizes wait differently, so a processor with fewer than 3 finished jobs of ours shows no median.
- Every read is saved to data/history.jsonl, one row per processor per read. A failed read is saved as NOTHING_RETURNED, never skipped.
- The page shows the last reading and the change against the earliest reading inside the last 24 hours.
- No QPU seconds are used. Keys are read from key files and passed straight to the service.
Outcomes per read: COMMITTED (a count came back) or NOTHING_RETURNED.
