# HFSIZE plan addendum for Faults and Guards 2.0

Dated 12 Nov 2026. Written before any reading is computed under Faults and Guards 2.0 (STANDARD.md sections 6.1 to 6.8). PLAN.md is not edited.

## What stays
The data, the sources, the population, the read of the stated size, the packed and quantized list, the band of 0.70 to 1.35 that separates AGREE from DISAGREE, the hand check and the known-good checks are unchanged. Only the outcome rule changes. Every outcome recorded earlier stands under the rules it named. The 10 Nov reading of 12 of 135, with the interval 0.0516 to 0.1489, was recorded as CANNOT_TELL under the first rule and stays so recorded.

## The reading
The quantity is the share of DISAGREE among AGREE plus DISAGREE. The plan expects it to be zero, so the null is 0. The unit is one repository.

## The size that matters, the band and the edge
The size that matters is a share of 0.10. It is the bound the plan gave for ABOVE. The band is [0, 0.05). It is the bound the plan gave for CONSISTENT, "upper end below 0.05", so the upper edge is open and the lower edge is closed. This follows worked example 6.8 of the standard.

## How a reading is decided, in the order of section 6.4
1. No interval can be formed: CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
2. The interval holds 0 and also holds 0.10: CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE.
3. The lower end is at or above 0.05: ABOVE. The upper end is below 0.05: CONSISTENT. BELOW cannot occur for a share that cannot go below zero.
4. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.

## The dead zone is closed
The first plan said ABOVE only when the lower end was above 0.10, so an interval whose lower end sat between 0.05 and 0.10 printed a bare CANNOT_TELL. Under this addendum that range has no gap. A lower end of 0.05 or more reads ABOVE. The 0.10 is used only in step 2.

## Interval method and level
A Wilson interval at 95 percent, z of 1.96, on the share of repositories. This is the method the plan named. Nothing is resampled, so there are no draws and no seed. When no repository disagrees the lower end is exactly 0, and when every compared repository disagrees the upper end is exactly 1.

## The causes of CANNOT_TELL that the desk already had
- Fewer than 30 comparable repositories: TOO_WIDE_TO_RESOLVE, because a reading that small cannot separate 0 from 0.10.
- No comparable repository, a zero denominator: NO_INTERVAL_FORMABLE.
- The known-good checks failed in this pass: NO_INTERVAL_FORMABLE. An instrument that failed its own controls forms no interval, and the standard has no closed reason for this case, so it maps here.
- An interval that overlaps 0.05 without holding both 0 and 0.10: STRADDLES_EDGE.

## Failed reads and the REQ-13 line
HFSIZE reads one list request. A list that returns too few models stops the pass and publishes nothing, so no row is ever a failed read and the count of NOTHING_RETURNED beside the headline is 0. The rows that cannot be compared (no size in the name, packed, a mixture-of-experts name, no safetensors total, a total that contradicts its own breakdown) are NOT_COMPARABLE row labels with their reasons counted apart. They are not failed reads and are in neither the numerator nor the denominator. Beside the headline the page prints the line the kit builds, for example "0 NOTHING_RETURNED. CANNOT_TELL 0 of 1 (none)." The summary carries a reason next to every outcome and a req13 block on the headline.

## Reading under this addendum
On the 10 Nov data the share of 12 of 135 has the interval 0.0516 to 0.1489. It does not hold 0, so step 2 does not apply. The lower end is above 0.05, so the reading is ABOVE. This is a new reading under a new rule, shown beside the earlier CANNOT_TELL, which stands under the rule it named.
