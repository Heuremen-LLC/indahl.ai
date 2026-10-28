# LAUNCH: stated launch time against actual launch time. Plan, written before any snapshot.

## Claim read
Each upcoming orbital launch carries a stated target time (NET, "no earlier than") that providers and the schedule keep revising.
Question: how far is the stated time, read N days ahead, from the time the launch actually happened?

## Data
Launch Library 2 (The Space Devs), public: https://ll.thespacedevs.com/2.3.0/launches/upcoming/ and /previous/. The API stores only the CURRENT NET,
so the stated time is snapshotted by us on every read and kept (data/snapshots.jsonl: launch id, provider, net, net_precision, status, read time).
Actual time: the launch's net after status Success, Failure or Partial Failure (the API then holds the net as flown). Read from /previous/.
One read of upcoming (limit 100) every 6 ticks, one read of previous (limit 100) every 6 ticks, 2 requests, well under the free limit of 15 an hour.
The user agent names this site. History before the first snapshot is not available and is not claimed.

## Rule (fixed now)
A launch is scored once it has flown and at least one snapshot of it was read at least 24 h before its actual time.
Slip at lead L = actual time minus the NET read in the last snapshot at least L before actual. Leads: 1 day, 7 days, 30 days.
Only launches whose net_precision at that snapshot is Minute, Hour or Day are used (Month or coarser leave the question unanswered, counted apart).
Per provider with at least 10 scored launches at a lead, and for all providers: median slip, share slipped by more than 24 h, with a Wilson 95% interval.
Outcome against the stated figure (the stated time is the claim, zero slip is the claim): share slipped more than 24 h at 7 days lead has lower bound above 0.25 = ABOVE (slips more than a quarter of the time);
upper bound below 0.10 = CONSISTENT; otherwise CANNOT_TELL. Under 30 scored launches overall at that lead: CANNOT_TELL for everything. Thresholds fixed here.
Launches that scrub and later fly count by their final flown time; launches cancelled or never flown are counted apart, not scored.
Floor: none needed, the claim has no chance component. Reported: how many launches are scored, how many are waiting.

## Known-good
Before the first full read: pull 3 launches with status Success from /previous/ and confirm net equals the window flown (net inside window_start..window_end) and status is a flown status.

## Addendum 1 (28 Oct, before the first snapshot)
Known-good read on 3 flown launches: net sits inside the window and status reads Success. Precision names seen: Second, Minute. Second counts with Minute, Hour and Day as usable precision.
The list mode omits the provider, so reads use mode=normal. A snapshot row is stored when a launch's net, precision or status changed since its last stored row or the last stored row is older than 6 hours, so the net at any past moment is the last stored row before it.
