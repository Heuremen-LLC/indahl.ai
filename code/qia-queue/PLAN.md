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

## Note 1 (29 Oct, committed before seven days of readings exist): the analysis this record is for
Question: does the number of pending jobs IBM reports predict how long our own jobs wait?
Rule, fixed now. When 7 days of hourly readings are held, each finished job of ours is joined to the last reading of its processor taken before the job was created (a job with no reading in the 90 minutes before it is dropped and the number dropped is reported). For each processor with at least 20 joined jobs, the Spearman rank correlation between pending count and wait, with a bootstrap 95% interval over jobs (4,000 resamples, seed 7). Outcome per processor: ABOVE if the interval sits wholly above 0.3, BELOW if wholly below 0 and the pending counts spanned at least a factor of 3, CONSISTENT if wholly within -0.3 to 0.3, otherwise CANNOT_TELL. Fewer than 20 joined jobs, or pending counts spanning less than a factor of 3: CANNOT_TELL.
Our jobs are not a random sample of jobs: they come from a few runs, mostly short. The result is a statement about our jobs only. The reading is shown on /qia only after it is computed under this rule, and the page says how many jobs were joined and dropped.


## Note (29 Oct, from the internal audit)
This plan did not state its unit and what it does not claim in one place. Stated now, with no change to any rule, read or outcome. Unit: one hourly reading of one processor's pending count, and one finished job of ours for the wait. Not claimed: a predicted wait, that our jobs stand for anyone else's, or anything about IBM's scheduling policy.
