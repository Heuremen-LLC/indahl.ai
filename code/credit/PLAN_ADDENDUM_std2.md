# CREDIT plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is dated 12 Nov 2026 and is written before any reading is computed under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged. The data, the sources, the frame, the companies and product families, the known-good checks and the tests are unchanged beyond the outcome rule. Outcomes recorded earlier stand under the rules PLAN.md named.

## Bands and edge convention
Every reading in PLAN.md is a two-sided band, so each is read with K.read(lo, hi, band=...) and no size that matters is needed. The both-alternatives test is not applied, and each recount says so.
- Ruler one, the pooled timely share of a year. The band is the one the rounding of the printed figure allows, written in PLAN.md as half-open. "99%" is [98.5, 99.5), "99.6%" is [99.55, 99.65), "99.7%" is [99.65, 99.75). The edge convention is open at the upper edge, written '[)'. The 2025 display against "more than 99%" uses (99, 100], open at the lower edge, as PLAN.md writes it.
- Ruler two, the not timely share of a company, a company and product family pair, and the bureaus over the window. The band is the share the printed figure leaves, which is one minus the ruler one band, for 2025 [0.35, 0.45) percent. The same open upper edge.
- Q1d, the share sent in 0 or 1 day in 2025. The band is [96.5, 97.5) percent that "97%" allows. The same open upper edge.
Under the open upper edge an interval whose lower end equals the band's upper end reads ABOVE, an interval whose upper end equals the band's upper end is not inside the band, and an interval end equal to the lower edge is inside it. PLAN.md wrote the half-open edges, so this is stated and not new.

## Interval method and level
Unchanged. A percentile 95 percent interval from a block bootstrap whose block is one company-month, 2,000 resamples, the statistic the ratio of summed counts, the fixed seed 20261110 joined to a checksum of the cell's name. The Wilson interval shown beside the company readings stays a display and decides nothing. It reads against the same band with the same edge, and its reading carries its own reason.

## How the desk's own CANNOT_TELL causes map to the closed reasons
- A company, or a company and product family pair, with fewer than 1,000 complaints or fewer than 10 months in the year: TOO_WIDE_TO_RESOLVE (owner decision O3). It is counted and not listed, as PLAN.md says.
- An interval that overlaps a band edge without meeting a rule above: STRADDLES_EDGE. This is the reading of Ruler one 2025, 99.55 percent with interval 99.35 to 99.68 against [99.55, 99.65).
- Q1c, the thirty-day reinvestigation period, fixed in PLAN.md as CANNOT_TELL because the file holds no response date and no dispute notice date: NO_INTERVAL_FORMABLE. The quantity cannot be formed from the file.
- Q1b, Table 1 against the database, fixed in PLAN.md as CANNOT_TELL because the bases differ: NO_INTERVAL_FORMABLE. The planned comparison of the same complaints cannot be formed.
- Q2, the stated APRs beside G.19, fixed in PLAN.md as CANNOT_TELL, not like for like: NO_INTERVAL_FORMABLE. The planned quantity cannot be formed from two populations that are not the same kind of thing.
- A known-good gate failure, which turns every outcome into CANNOT_TELL: NO_INTERVAL_FORMABLE. The earlier outcome is kept as outcome_before_gate.
- A reading with no interval: NO_INTERVAL_FORMABLE.

## Failed reads
Rows with a timely value other than Yes or No and rows with an unreadable date are NOTHING_RETURNED. They are a status of the read and never an outcome. They are outside every share. Rows outside the window, rows with sent before received and the other rows PLAN.md lists as counted apart stay counted apart as PLAN.md says.

## Counts beside every headline share
Beside each year's Ruler one reading, and so beside the headline, the recount prints the NOTHING_RETURNED count and the CANNOT_TELL share split by reason (REQ-13, K.req13). The readings counted are that year's Ruler one reading and each company reading under Ruler two for that year, with every company under the minimum counted as CANNOT_TELL TOO_WIDE_TO_RESOLVE. The NOTHING_RETURNED count is the database rows with a timely value other than Yes or No or with an unreadable date, over the whole file, listed apart. This is how this desk reads REQ-13, since the headline share is a share of complaints and a complaint is not itself a reading.

## Effect on recorded outcomes
No reading changes its outcome under this addendum. Ruler one 2025 stays CANNOT_TELL, now with reason STRADDLES_EDGE. 2021, 2023 and 2024 stay CANNOT_TELL with STRADDLES_EDGE and 2022 stays CONSISTENT. Q1d 2025 stays CANNOT_TELL with STRADDLES_EDGE.
