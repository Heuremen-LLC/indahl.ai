# UPTIME plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any vendor read BELOW or ABOVE under the 2.0 outcome rule. All twenty vendors read CANNOT_TELL at this date.

## What this addendum changes
Only the outcome rule and what is printed beside it. The probes, the seats, the vendor list, the rounds, the events, the floor from the control targets, the episodes rule and the notes of Addendum 1 are unchanged. Data, sources and tests are unchanged. Outcomes recorded before this date stand under the rules they named.

## The reading
The quantity is the agreement share of a vendor, the rounds that are not disagreement rounds divided by the vendor's rounds. A disagreement round is one where the page said none and the home seat and the runner seat both failed. A round counts only where both seats made a request and the page was read.

## One-sided rule, bound and edge
The plan's rule is one-sided. It reads a count of disagreement rounds against a threshold and never against a band, so CONSISTENT is not available. The threshold in rounds is the plan's own, the expected count from the floor plus two square roots of it, where the expected count is the upper end of the Wilson 95 percent interval of the control rate times the vendor's rounds. As a share the bound is one minus that threshold divided by the vendor's rounds. The edge is closed. The plan names no band and none is invented here.

## Interval method and level
The interval of the agreement share is a Wilson interval at 95 percent over the vendor's rounds. No resampling is used so no draws or seed apply. The rounds are treated as independent as the plan's Addendum 1 already states. Consecutive disagreement rounds are one episode and the rule on episodes is kept below.

## Outcomes
- BELOW: the whole interval lies below the bound and there are at least two episodes. The service was less reachable than its page stated, as the plan says.
- ABOVE: the whole interval lies above the bound. The agreement is wholly above what the floor allows. This replaces the old CONSISTENT. The plan did not assign ABOVE because a reachable service is the stated case, and under the standard a one-sided reading may print ABOVE, BELOW or CANNOT_TELL only.
- CANNOT_TELL with STRADDLES_EDGE: the interval overlaps the bound.

## Size that matters
The plan names no size that matters. The threshold is derived from the control floor and not from a departure from a null of a stated size, so the both-alternatives test is not applied. The recount says so here and not silently.

## Reasons for the desk's own CANNOT_TELL causes
- Fewer than 300 rounds held: TOO_WIDE_TO_RESOLVE, under owner decision O3 for a reading below the desk's minimum sample.
- No round at all (a vendor with zero rounds): NO_INTERVAL_FORMABLE, because no width can be formed from zero rounds.
- A reading that would be BELOW but has fewer than two episodes: TOO_WIDE_TO_RESOLVE, because fewer than two independent episodes is below the desk's minimum of independent units, under O3.

## Failed reads
A round in which both seats made a request but the status page could not be read is a failed read of a source. It is NOTHING_RETURNED, listed apart per vendor and outside the numerator and denominator. The old code skipped these rounds without counting them and the count is now printed.

## Beside the headline
The summary and the page print the REQ-13 line, the NOTHING_RETURNED count and the share of CANNOT_TELL split by reason, over the vendors read.
