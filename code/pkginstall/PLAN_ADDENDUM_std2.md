# PKGINSTALL plan addendum for Faults and Guards 2.0

Dated 12 Nov 2026. Written before any reading is computed under Faults and Guards 2.0 (STANDARD.md sections 6.1 to 6.8). PLAN.md is not edited.

## What stays
The data, the sources, the pip dry run, the command reader, the classes, the hand check and the known-good checks are unchanged. Only the outcome rule changes. Every outcome recorded earlier stands under the rules it named, including the reading of 1 of 523 recorded as CONSISTENT.

## The reading
The quantity is the share of DISAGREE (pip fails for a reason the plan names) among AGREE plus DISAGREE. The plan expects it to be zero, so the null is 0. The unit is one project.

## The size that matters, the band and the edge
The size that matters is a share of 0.10. It is the bound the plan gave for ABOVE. The band is [0, 0.05). It is the bound the plan gave for CONSISTENT, "upper end below 0.05", so the upper edge is open and the lower edge is closed. This follows worked example 6.8 of the standard. The plan said it used the same thresholds as HFLICENSE.

## How a reading is decided, in the order of section 6.4
1. No interval can be formed: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
2. The interval holds 0 and also holds 0.10: CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE.
3. The lower end is at or above 0.05: ABOVE. The upper end is below 0.05: CONSISTENT. BELOW cannot occur for a share that cannot go below zero.
4. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.

## The dead zone is closed
The first plan said ABOVE only when the lower end was above 0.10, so a lower end between 0.05 and 0.10 would have printed a bare CANNOT_TELL. Under this addendum a lower end of 0.05 or more reads ABOVE. The 0.10 is used only in step 2.

## Interval method and level
A Wilson interval at 95 percent, z of 1.96, on the share of compared items. This is the method the plan named. Nothing is resampled, so there are no draws and no seed. When nothing disagrees the lower end is exactly 0, and when everything compared disagrees the upper end is exactly 1.

## The causes of CANNOT_TELL that the desk already had
- Fewer than 30 comparable items: TOO_WIDE_TO_RESOLVE, because a reading that small cannot separate 0 from 0.10.
- No comparable item, a zero denominator: NO_INTERVAL_FORMABLE.
- The known-good checks failed in this pass: NO_INTERVAL_FORMABLE. An instrument that failed its own controls forms no interval, and the standard has no closed reason for this case, so it maps here.
- An interval that overlaps 0.05 without holding both 0 and 0.10: STRADDLES_EDGE.

## Failed reads and the REQ-13 line
Three row reasons are failed reads. The description of a project that PyPI did not return ("description not readable"), a pip run that timed out ("pip timed out"), and a pip run that failed in a way the plan does not name ("pip failed in a way the plan does not name"). They are recorded as NOTHING_RETURNED, listed apart in the summary under failed_reads, and are in neither the numerator nor the denominator. They stay NOT_COMPARABLE row labels as before, so no class count moves. The other reasons (no pip install line, a command that does not name the project, other options, a URL or path, a placeholder, no wheel that fits this Python and platform) describe the project and are not failed reads. Beside the headline the page prints the line the kit builds, for example "0 NOTHING_RETURNED. CANNOT_TELL 0 of 1 (none)." The summary carries a reason next to the outcome and a req13 block on the headline.

## Reading under this addendum
1 of 523, interval 0.0003 to 0.0108. The interval does not hold 0, so step 2 does not apply, and the upper end is below 0.05. The reading is CONSISTENT, unchanged. The plan's own limit stays stated. A command that names a project by its own PyPI name has little room to fail.
