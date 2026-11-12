# SEAT plan addendum for Faults and Guards 2.0

Dated 12 November 2026. Written before any reading under the 2.0 outcome rule.

## What this addendum changes
Only the rolling outcome rule and what is printed beside it. The probes, the three reads, the known-good control, the two-probe rule for a drifting page, the feed limits and the definition of an incident in Addendum 1 are unchanged. Data, sources and tests are unchanged. Outcomes recorded before this date stand under the rules they named.

## The reading
The quantity is the number of incidents among the last 24 probes that passed their control. An incident is a run of consecutive probes with a drifting page, a feed past its limit or a broken chain, as Addendum 1 says. The count is exact. It is a count of recorded probes and not a sample, so under owner decision O1 it is a reading with an interval of zero width and no interval method, level, draws or seed apply.

## One-sided rule, bound and edge
The plan's rule has one bound that decides, three incidents, the line at which it said the claim fails. The claim is that the live site is the published site and its feeds are current. A reading against a single bound can be ABOVE, BELOW or CANNOT_TELL only, and CONSISTENT is not available. The bound is 3 and the edge is closed at the bound for ABOVE, so three incidents or more read ABOVE, as the plan says "at least 3". Fewer than three incidents read BELOW the bound. The plan named no band, no tolerance and no size that matters, so none is invented and the both-alternatives test is not applied.

## What changes in the words
The plan read CONSISTENT for no incident and CANNOT_TELL for one or two incidents. Under the standard a lone bound has no CONSISTENT and the dead zone of one or two incidents has no closed reason, since an exact count cannot straddle an edge. The result is that zero, one and two incidents all read BELOW the bound of three. The count is printed beside the word so that none and two are not confused. BELOW here says only that the incidents stayed under the number at which the plan calls the claim failed. It does not say the site is good. The plan's earlier reading of one incident as CANNOT_TELL is replaced by BELOW, and that is a change of word with no change of count.

## Reasons for the desk's own CANNOT_TELL causes
- Fewer than 24 probes that passed their control: TOO_WIDE_TO_RESOLVE, under owner decision O3 for a reading below the desk's minimum sample.
- The newest probe more than three hours old: NO_INTERVAL_FORMABLE. The window cannot be read as current, so the reading cannot be formed now. No other closed reason fits and it is stated here that this is the forced case. Where both causes hold, the newest probe being old and fewer than 24 probes, NO_INTERVAL_FORMABLE is used because it comes first in the decision order.

## Failed reads
A probe whose known-good control failed is saved as CONTROL_FAILED with no reading. It is a failed read of a source, NOTHING_RETURNED, listed apart as the failed controls and outside the count of probes and incidents.

## Beside the headline
The summary and the page print the REQ-13 line, the count of failed controls as NOTHING_RETURNED and the share of CANNOT_TELL split by reason.
