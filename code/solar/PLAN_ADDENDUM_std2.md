# SOLAR: plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is written before any new reading under the 2.0 outcome rule. PLAN.md and its two earlier addenda are not edited and the seal in data/plan_seal.json is unchanged. The data, the sources, the frame, the events, the bins, the known-good checks, the Wilson interval and the block bootstrap are unchanged. Only the outcome rule changes, to the reading outcomes of the standard (section 6). Outcomes recorded earlier stand under the rules they named.

## Ruler one, reliability bins
- The quantity is the observed share of days with the event in a bin. The figure it is read against is the mean stated chance of the days in the bin. PLAN.md reads CONSISTENT when the mean stated chance is inside the interval at any width, with no tolerance. That is a point figure with no tolerance, and under 2.0 it has no CONSISTENT. No tolerance is named now, because one named after the data would be a rule written after the data.
- Each bin reads against the bound at the mean stated chance. ABOVE if the lower end of the 95 percent Wilson interval is over the bound. BELOW if the upper end is under it. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.
- Edge convention: closed. An interval end equal to the bound is not over it and not under it.
- Size that matters: none named in PLAN.md and none is named now. The both-alternatives test is not applied to the bins, and the page says so.
- Interval: the Wilson interval at 95 percent, days treated as independent, as in PLAN.md. The block bootstrap interval printed beside it is still described and decides nothing.

## Ruler two, Brier skill
- The plan's two-sided band of minus 0.05 to plus 0.05 around zero is a tolerance, so CONSISTENT stays available. Edge convention closed. The skill is read with the kit's band reading, as the standard defines it in 6.2. ABOVE means the whole interval is above the band edge of plus 0.05. BELOW means the whole interval is below minus 0.05. CONSISTENT means the whole interval is inside the band. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.
- This retires PLAN.md's reading of ABOVE as an interval over zero and BELOW as an interval under zero. The plan named zero and the band as two separate bounds. The owner's rule for a plan with two bounds takes the band edge as the CONSISTENT bound and the other bound as the size that matters, and a size that matters has to be above zero. Zero cannot be one, so the band alone decides. A skill interval that lies over zero but reaches into the band therefore reads CANNOT_TELL with reason STRADDLES_EDGE. Outcomes recorded earlier stand under the rule they named.
- Size that matters: none named. The both-alternatives test is not applied.
- Interval: the plan's moving-block bootstrap over target days in date order, blocks of 27 days, 2,000 replicates, seed 27, 2.5th and 97.5th percentiles, level 95 percent. It is kept in the desk's own code, because the same replicates also give each bin's described bootstrap interval and the desk takes percentiles by nearest rank. The kit's block_bootstrap interpolates between ranks and would move the stored intervals. The interval method is unchanged.

## How the desk's own CANNOT_TELL causes map
- A bin with fewer than 30 days, or a skill reading with fewer than 30 scored days or fewer than 5 event days, reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE (minimum sample rule, owner decision O3).
- A bin with no days, a skill reading whose bootstrap forms no interval, and any reading made while a known-good check has failed read CANNOT_TELL with reason NO_INTERVAL_FORMABLE. A failed check means the records cannot be trusted to form a reading.
- The proton cells stay held, as in Addendum 1. The delivered proton list is incomplete, so the planned quantity cannot be formed, and their bins and skill read CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
- Interval overlaps the bound or the band edge: STRADDLES_EDGE.

## The headline row
PLAN.md fixes the headline as M-class flares, day one, with the big number the count of its bins that read consistent out of bins with 30 or more days. Under 2.0 no bin reads consistent. The big number is now the count of those bins that read CANNOT_TELL, which are the bins whose interval holds the mean stated chance. It is the same count as before and the same eight bins. The line gives the bins that read ABOVE or BELOW, and the Brier skill with its interval and reading, as before. The skill reading is the one the plan already fixed.

## Counts beside the headline (REQ-13)
- Beside the headline the page prints the REQ-13 line over the eight headline bins. NOTHING_RETURNED for the cell counts the days with no report on file, a section that did not parse, no events list for the day, a missing K value and no proton list yet. They are listed apart and are outside the numerator and denominator. Days issued late, days whose dates do not follow the report and days not yet settled are exclusions of the frame and stay counted apart as before.
- The summary also carries a REQ-13 line over every bin with at least one day and every skill reading, held cells included.

## Display line that used the word consistent
The headline line printed how many bins read consistent on the block bootstrap interval. That line is reworded to say how many bootstrap intervals hold the stated chance. It is display only and reads no outcome.

## Expected effect, stated before the new run
The M-class day one skill stays ABOVE. The 34 bins that read CONSISTENT across the scored cells, 4 of them in the headline row, read CANNOT_TELL with reason STRADDLES_EDGE. Under the band reading three skill cells that read BELOW because their interval lay under zero but reached into the band read CANNOT_TELL (STRADDLES_EDGE): high latitude major or severe storm day one and day two, and high latitude storm K 5 or more day two. One described row that read ABOVE reads CANNOT_TELL in the same way. The other skill outcomes are unchanged. No number other than an outcome moves.
