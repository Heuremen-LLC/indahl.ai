# SECRECORDS plan addendum for Faults and Guards 2.0

Dated 12 Nov 2026. Written before any reading is computed under Faults and Guards 2.0 (STANDARD.md sections 6.1 to 6.8). PLAN.md is not edited.

## What stays
The data, the sources, the Tranco list, the header reader that follows no redirect, the SPF counter, the DMARC and header descriptive rows, the hand check and the known-good checks are unchanged. Only the outcome rule changes. Every outcome recorded earlier stands under the rules it named. That includes the 8 Nov reading of the HSTS test as ABOVE, the 9 Nov reading of 20 of 144 recorded as CANNOT_TELL, and the SPF reading recorded as CONSISTENT.

## The readings
Two claims are read, each with its own outcome, reason and REQ-13 line. The HSTS preload header: the share of DISAGREE among AGREE plus DISAGREE, where the header does not meet the preload list's own requirements. The SPF lookup limit: the share of DISAGREE among AGREE plus DISAGREE, where the record needs more than ten lookups. The plan expects zero in both, so the null is 0. The unit is one domain. The descriptive rows have no outcome and no claim, and they stay so.

## The size that matters, the band and the edge
The size that matters is a share of 0.10. It is the bound the plan gave for ABOVE. The band is [0, 0.05). It is the bound the plan gave for CONSISTENT, "upper end below 0.05", so the upper edge is open and the lower edge is closed. This follows worked example 6.8 of the standard. The plan has no separate sentence for each claim, and one choice is made for both here.

## How a reading is decided, in the order of section 6.4
1. No interval can be formed: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
2. The interval holds 0 and also holds 0.10: CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE.
3. The lower end is at or above 0.05: ABOVE. The upper end is below 0.05: CONSISTENT. BELOW cannot occur for a share that cannot go below zero.
4. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.

## The dead zone is closed
The first plan said ABOVE only when the lower end was above 0.10, so a lower end between 0.05 and 0.10 printed a bare CANNOT_TELL, and the 9 Nov HSTS reading sat in that range. Under this addendum a lower end of 0.05 or more reads ABOVE. The 0.10 is used only in step 2.

## Interval method and level
A Wilson interval at 95 percent, z of 1.96, on the share of compared items. This is the method the plan named. Nothing is resampled, so there are no draws and no seed. When nothing disagrees the lower end is exactly 0, and when everything compared disagrees the upper end is exactly 1.

## The causes of CANNOT_TELL that the desk already had
- Fewer than 30 comparable items in a claim: TOO_WIDE_TO_RESOLVE, because a reading that small cannot separate 0 from 0.10.
- No comparable item, a zero denominator: NO_INTERVAL_FORMABLE.
- The known-good checks failed in this pass: NO_INTERVAL_FORMABLE. An instrument that failed its own controls forms no interval, and the standard has no closed reason for this case, so it maps here.
- An interval that overlaps 0.05 without holding both 0 and 0.10: STRADDLES_EDGE.

## Failed reads and the REQ-13 line
Row reasons that are failed reads of a source are recorded as NOTHING_RETURNED, counted for each claim, listed apart in the summary under failed_reads, and are in neither the numerator nor the denominator. For the HSTS claim that is "HTTPS request failed". For the SPF claim it is "DNS read failed" and "count cut short", where the count of lookups was cut off because a record could not be fetched. They stay NOT_COMPARABLE row labels as before, so no class count moves. The other reasons (no HSTS header, a header that does not state preload, no SPF record) describe the domain and are not failed reads. Beside each claim's headline the page prints the line the kit builds, for example "0 NOTHING_RETURNED. CANNOT_TELL 0 of 1 (none)." The summary carries a reason next to every outcome and a req13 block on every claim.

## Reading under this addendum
HSTS, 19 of 144, interval 0.0861 to 0.1969. The interval does not hold 0, so step 2 does not apply. The lower end is above 0.05, so the reading is ABOVE. This is a new reading under a new rule, shown beside the earlier CANNOT_TELL, which stands under the rule it named. SPF, 20 of 764, interval 0.017 to 0.0401. It does not hold 0 and the upper end is below 0.05. The reading is CONSISTENT, unchanged.
