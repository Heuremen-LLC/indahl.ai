# NOW: plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the new outcome rule. PLAN.md is not edited.

## What changes and what does not
Only the outcome rule for bins changes, to the reading outcomes of section 6 of Faults and Guards 2.0, together with the reason that a CANNOT_TELL carries. The log, the entries, the sources, the criteria, the bins, the 30-entry minimum, the Wilson interval, the Brier score and the bootstrap of the skill are unchanged. Earlier recorded outcomes stand under the rules they named. The frozen reading of 10 November 2026 recorded three Manifold bins as CONSISTENT, and that record and its file stay as they are. The page and the feed are read again under 2.0 from the same numbers, and the two readings are shown side by side in the record.

## What the plan names, as the addendum reads it
Quantity per bin: the share of the bin's events that happened, read against the mean stated probability of the bin.
Figure: the mean stated probability of the bin. This is a point figure. The plan names no tolerance. The plan's rule that CONSISTENT holds if the mean sits inside the Wilson interval, at any width, is not a tolerance, and this addendum does not invent one now, since that would be a rule written after the data.
Reading: bound equal to the mean stated probability, with no band. ABOVE if the lower end of the Wilson interval is above the mean. BELOW if the upper end is below it. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. CONSISTENT is not available.
Size that matters: none named, and the plan reads a point figure and not a departure from a null, so the both-alternatives test is not applied.
Edge convention: closed. An interval whose end equals the mean is not ABOVE or BELOW and reads CANNOT_TELL STRADDLES_EDGE.

## Minimum sample
The plan reads a bin as CANNOT_TELL while it holds fewer than 30 entries. Under owner decision O3 this reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. A bin with no entry has no reading and is not counted.

## Interval methods and levels (unchanged, now named in one place)
Bins: Wilson interval at 95 percent, each entry one unit, as the plan says.
Brier skill: percentile bootstrap over entries, 2,000 draws, seed 20261110, 95 percent. The Brier score and the skill carry an interval and no outcome, as the plan states, so no outcome is printed for them.

## Readings of one event against the record
The plan's entry readings RIGHT, WRONG, HAPPENED and DID_NOT_HAPPEN are readings of one event against a dated record. They have no interval and no figure to read against, so they stay as the plan's words. A CANNOT_TELL entry has no record that decides its criterion, or its criterion has no test the record can answer, or it is a stated probability of catastrophe that one outcome cannot test, or a market resolved to neither yes nor no. No closed reason fits these exactly, so under the owner's rule each carries NO_INTERVAL_FORMABLE, because no test and so no width can be formed. The plan's own sentence stays beside it as the reason text. This holds for the readings written by the rider and by hand, and for the statements of catastrophe that read CANNOT_TELL by design. The log rows are not changed, since the log is append-only. The code maps them when it builds the summary and the feed.

## Failed reads
A failed read of a Manifold market by the rider is NOTHING_RETURNED. It is a status of the read, is listed apart, and the entry gets no outcome row until a later pass reads it. It is outside the numerator and denominator of every share. Entries whose deadline has passed and that have no reading yet are waiting. They are listed apart and are not readings.

## REQ-13 beside each headline share
The headline of the page (right, wrong and cannot tell among the entries read) and the bins of each source carry a block that prints the number of NOTHING_RETURNED reads and the share of CANNOT_TELL among the readings, split by reason.

## What this does to the recorded readings
Manifold resolved set, ten bins read: bins at 0 to 0.1 and 0.2 to 0.3 read BELOW and stay. Bins at 0.1 to 0.2, 0.3 to 0.4 and 0.9 to 1 were recorded CONSISTENT and read CANNOT_TELL with reason STRADDLES_EDGE. The five bins under 30 markets read CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, where they were recorded CANNOT_TELL without a reason. The counts of entries, the Brier score and the skill do not move.
