# FIDELITY: state divorce and marriage counts reported to the CDC, set beside the Census American Community Survey. Plan, written before any state-year was compared by this desk.

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.

## Claim read
The CDC National Center for Health Statistics (NCHS) publishes the number of marriages and the number of divorces and annulments that each state reports, by state of occurrence. The Census Bureau's American Community Survey (ACS) asks residents whether they married or divorced in the last 12 months and publishes the estimate of persons with a 90 percent margin of error.

The two count different things. NCHS counts events where they were licensed or decreed. ACS counts persons where they live now. So a gap between them is a reading of that difference, and it is not a claim that either source is wrong. The page says this in its first paragraph.

Question: for each state, year and event, does the NCHS count sit above, below or inside the ACS interval once the ACS persons are converted to events.

## Disclosure of what was seen before the plan
The scout (SCOUT.md, 11 Nov 2026) printed NCHS counts beside ACS women and men estimates for Texas, Florida, New York and Pennsylvania in 2022 and 2023 (divorce and marriage), and ACS divorce estimates for California. Those 16 state-year-events are in the frame and are not dropped. The scout also read the printed rate tables for the same states. Nothing else was compared. ACS data for all years were pulled after this paragraph was written and not read.

## Frame (fixed now)
Row = (jurisdiction, year, event). Jurisdictions: the 50 states and the District of Columbia (Puerto Rico is not in the NCHS tables). Years: 2010 to 2019 and 2021 to 2024, the ACS 1-year years. 2020 is excluded because the Census did not publish standard 2020 1-year estimates. Events: DIVORCE, MARRIAGE. Every row of the frame gets an outcome and none is dropped. Divorces and marriages are separate cells and are never pooled.

## Stated side
The NCHS count by state of occurrence from the state count tables for 2000 to 2023 (PDF, text extracted). Divorce counts include annulments, and for some states divorce petitions filed or legal separations (NCHS footnote). A state-year printed as not reported is CANNOT_TELL with reason "state does not report". The 2024 count tables are not published (rates only), so every 2024 row is CANNOT_TELL with reason "no stated count" and counts are not backed out from rates times population.

## Second measurement and the conversion (fixed now)
ACS 1-year tables B12503 (divorced in the last year) and B12501 (married in the last year), persons 15 years and over, by state. The primary conversion is the women's estimate: each divorce or marriage between a woman and a man involves exactly one woman, so women who divorced (B12503_010) and women who married (B12501_010) estimate the number of events in opposite-sex couples. The women's estimate is chosen over the men's because it carries one count per event in the mainstream case and because it is fixed here before either was compared. Its limits are named: same-sex events are counted once per partner in the same sex and so are counted by sex of respondent, not once per event, and ACS covers residents, so persons who divorced and then left the state or died, and people who married a nonresident, are placed differently from NCHS. The men's estimate (B12503_005, B12501_005) is computed and shown beside every row. It is displayed and not scored, and rows where the women's and the men's intervals give different outcomes are counted apart as "sex split".
The interval is the published estimate plus and minus the published 90 percent margin of error, as published, lower end not below zero. No conversion to 95 percent is used in the outcome. The 95 percent scale (margin times 1.96 over 1.645) is computed for display only, as a sensitivity. A missing or coded margin is CANNOT_TELL with reason "no ACS interval". ACS 2024 rows are read against no stated count, so they are CANNOT_TELL.

## Rules (fixed now)
Outcome per row, women's interval, NCHS count n, interval [lo, hi] (edges inside):
- ABOVE: n greater than hi. The NCHS count is above the ACS interval.
- BELOW: n less than lo.
- CONSISTENT: n inside [lo, hi].
- CANNOT_TELL, each reason counted apart: state does not report, no stated count, no ACS interval.
Cells: per jurisdiction (event, all years), per year (event, all jurisdictions), and per event overall. Each cell lists counts of ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason. CANNOT_TELL is never folded into any outcome. No share, no test and no net is computed over rows, since a state's consecutive years and the sexes share the same sample and are not independent. A jurisdiction cell reads as the outcome of the majority of its scored rows only when at least 5 rows are scored and one outcome holds at least 80 percent of them, otherwise it reads MIXED, and with fewer than 5 scored rows CANNOT_TELL.

## Occurrence against residence (fixed now)
This is the main limit. A couple may marry or divorce in a state they do not live in. NCHS counts the event where it happens. ACS counts the person where they live. Destination states are counted apart: Nevada for both events and Hawaii for marriage. The headline cell is printed for all jurisdictions and for all except those destination cells, and the page says the rest of the states are not free of the same effect since every state has some. No correction is attempted.

## Described and not scored
The median, over scored rows, of the NCHS count divided by the ACS women's estimate, by jurisdiction and event. The women's against men's ACS estimate. The 95 percent scale outcome counts. Row counts by outcome in each year of NCHS rates for the same state, as a reader check only.

## Both alternatives
A. NCHS counts sit inside the ACS interval for most rows of a state. The cell reads CONSISTENT.
B. NCHS counts sit above or below for most rows. The cell reads ABOVE or BELOW. A cell says where the count sits and names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. The NCHS parse has 52 entries (51 jurisdictions and the United States) with 24 values each for both events, and the sum of reporting states equals the printed United States figure in every year 2000 to 2023 for both events. Every ACS year has 51 jurisdictions with numeric estimates and margins for the used variables, or a coded margin that the rule reads as no ACS interval.
2. Reader. Four hand-read state-years (hand read from the NCHS PDF text and from the ACS summary files, listed in data/known_good_rows.json and CHECKS.md) equal the parsed rows: Texas 2022 divorce, Florida 2023 divorce, New York 2022 marriage, Pennsylvania 2023 marriage. At least 90 percent of reporting state-years 2010 to 2023 give an NCHS count over the ACS B01003 population that rounds to the printed NCHS rate within 0.1.
3. Join. ACS API values for 2022 and 2023 equal the Census table-based summary files for the used variables in at least 99 percent of jurisdiction values.
4. Rule. Synthetic rows read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly, and heuremen_kit's self-test passes.

## Set aside
Provisional against revised NCHS readings (copies are kept from 11 Nov 2026, no reading yet). Any cause for a gap. Other ACS tables, 5-year files, county data, state vital records offices, the BGSU refined rates. Annulments and petitions are not separated.
