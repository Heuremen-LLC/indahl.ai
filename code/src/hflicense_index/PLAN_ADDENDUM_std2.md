# HFLICENSE plan addendum for Faults and Guards 2.0

Dated 12 Nov 2026. Written before any reading is computed under Faults and Guards 2.0 (STANDARD.md sections 6.1 to 6.8). PLAN.md is not edited.

## What stays
The data, the sources, the populations, the stated-license and license-file readers, the families, the hand check, the descriptive rows and the known-good checks are unchanged. Only the outcome rule changes. Every outcome recorded earlier stands under the rules it named, including the Models reading of 0 of 96 recorded as CONSISTENT and the Datasets reading of 0 of 24 recorded as CANNOT_TELL under the first rule.

## The reading
The quantity is the share of DISAGREE among AGREE plus DISAGREE. The plan expects it to be zero, so the null is 0. The unit is one repository. Models and datasets are read as two separate groups, each with its own outcome, reason and REQ-13 line.

## The size that matters, the band and the edge
The size that matters is a share of 0.10. It is the bound the plan gave for ABOVE. The band is [0, 0.05). It is the bound the plan gave for CONSISTENT, "upper end below 0.05", so the upper edge is open and the lower edge is closed. This follows worked example 6.8 of the standard. The plan said it uses the same thresholds as PKGLICENSE, and this addendum states them in full here and in the PKGLICENSE addendum.

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
- Fewer than 30 comparable items in a group: TOO_WIDE_TO_RESOLVE, because a reading that small cannot separate 0 from 0.10.
- No comparable item, a zero denominator: NO_INTERVAL_FORMABLE.
- The known-good checks failed in this pass: NO_INTERVAL_FORMABLE. An instrument that failed its own controls forms no interval, and the standard has no closed reason for this case, so it maps here.
- An interval that overlaps 0.05 without holding both 0 and 0.10: STRADDLES_EDGE.

## Failed reads and the REQ-13 line
Two row reasons are failed reads of a source that a row's reading needs. They are "file list could not be read" and "license file not readable" (a gated repository, or a file that did not return). They are recorded as NOTHING_RETURNED, counted for each group, listed apart in the summary under failed_reads, and are in neither the numerator nor the denominator. They stay NOT_COMPARABLE row labels as before, so no class count moves. The other reasons (no stated license tag, no license file in the repository root, either side a custom or named license) describe the repository and are not failed reads. Beside each group's headline the page prints the line the kit builds, for example "2 NOTHING_RETURNED. CANNOT_TELL 1 of 1 (1 TOO_WIDE_TO_RESOLVE)." The summary carries a reason next to every outcome and a req13 block on every group.

## Reading under this addendum
Models, 0 of 96, interval 0 to 0.0385. The interval holds 0 and does not reach 0.10, so step 2 does not apply, and the upper end is below 0.05. The reading is CONSISTENT, as before. Datasets, 0 of 24. That is under 30 comparable repositories, and the interval 0 to 0.138 holds both 0 and 0.10. The reading is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, as before but now with its reason.
