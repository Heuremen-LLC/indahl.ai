# Plan addendum for Faults and Guards 2.0, MODEL (12 November 2026)

Written on 12 November 2026 before any reading under Faults and Guards version 2.0.0. MODEL has a working note, PLAN_MLPERF.md, and a CHECKS.md. Neither names a size that matters, a band, a tolerance, an edge convention, an interval method or a list of reasons. The audit of 12 November 2026 therefore could not judge this desk. This addendum decides them. The author of this addendum decided every value below. None was fixed by the original note.

## What is unchanged

Sources, the MLCommons files and their hashes, the vendor pages, the quoted sentences, the claim scripts and every recomputation are unchanged beyond the outcome rule. PLAN_MLPERF.md is not edited. Every outcome recorded earlier stands under the rules it named, and the 2.0 reading is printed beside it.

## What is read

Each statement is a row-level exact read. A figure a vendor prints is held against the same quantity in a published MLCommons file, or a count or rank is recomputed from the file. Nothing is sampled, so the interval of every reading has zero width and no interval method, level, draws or seed applies. The size that matters is not a departure from a null, so no both-alternatives test applies to these rows.

## Band, tolerance and edge

- A printed figure is a point figure. Its tolerance is the rounding of the printed figure, half of its last printed digit, in the figure's own units. A figure printed as 70,610.8 has a tolerance of 0.05. A figure printed with "about", "nearly" or "roughly" is held to the range the claim script states for that row, and the script's range is the band for that row.
- A count, a rank or a name is exact. Its band is the single printed value.
- Edge convention: closed at both edges.
- A reading inside the band is CONSISTENT. A reading above the band is ABOVE, and ABOVE means the file shows more than the statement. A reading below the band is BELOW. Rows with a stated tolerance use the read_exact rule of the kit, band and signed difference. Where a statement names no figure and no tolerance, only a signed difference is printed with no outcome word.
- A one-sided statement such as "at least" or "more than" is read against its single bound and can print only ABOVE, BELOW or CANNOT_TELL. A statement such as "the only submission" or "up to 115%" that is checked by listing the entries or by reproducing the printed figure is a count, name or figure read and is exact, as above.

## How this desk's CANNOT_TELL causes map to the closed reasons

Every CANNOT_TELL on this desk is a statement for which the planned quantity cannot be formed from the files. The causes are a baseline the file does not hold (a standalone baseline, an earlier round, an internal baseline), a statement with no number or no stated threshold ("on par", "near", "among the fastest"), a figure printed only in an image, results the vendor marks as not verified by MLCommons, and a field the files do not carry (serving mode, numeric format, region). A statement with two counts that run in opposite directions is also one the single planned quantity cannot be formed for. All of these are NO_INTERVAL_FORMABLE. STRADDLES_EDGE would need an interval that overlaps a band, and TOO_WIDE_TO_RESOLVE would need an interval that holds the null and a size that matters, and a zero-width reading can do neither.

The notes beside each row keep the specific cause in plain words.

## Failed reads

A fetch or parse that fails is NOTHING_RETURNED, a status of the read, listed apart and outside the numerator and denominator. It is never an outcome of a statement.

## Counts beside the reading

Beside the tally of every source the page prints the count of NOTHING_RETURNED and the share of CANNOT_TELL split by reason (REQ-13), built with the kit's req13.
