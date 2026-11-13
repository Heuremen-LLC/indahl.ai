# CREDIT, outside referee pass, 10 Nov 2026

Verdict: FIX THEN SHIP.

Every complaint count recounts exactly from the raw file. The complaint readings match except for cells sitting right on a band edge. The card plan (TCCP) side has a parsing error that puts wrong numbers on the page and makes one shown-only sentence false. That has to be fixed before the page goes out. Five wording or disclosure fixes are also needed. None of them changes a sealed rule.

Read against: summary_credit.json generated 2026-11-10T17:56:47Z (gates all true), credit.html of 12:59, PLAN.md at commit 8ef6f26. Referee code is in /Users/heuremen/bones-forge/credit_index_referee/code (own csv stream, own xlsx reader, own block bootstrap with seed 987654, own classifier, nothing imported from the desk). Outputs are in out/ (referee_recount.json, referee_tccp.json, compare.txt).

## Recount, desk against referee

| Item | Desk | Referee |
|---|---|---|
| Rows in file | not printed | 19,045,222 |
| Rows in window | 10,765,407 | 10,765,407 |
| Outside window | 8,279,815 | 8,279,815 |
| Bad dates, bad field counts, timely not Yes/No, no sent date | 0, 0, 0, 0 | 0, 0, 0, 0 |
| Duplicate Complaint IDs (window and whole file) | 0 | 0 and 0 |
| Rows 2021 / 2022 / 2023 / 2024 / 2025 | 495,940 / 800,245 / 1,292,043 / 2,734,252 / 5,442,927 | same |
| Not timely 2021 to 2025 | 6,161 / 5,115 / 5,515 / 7,720 / 24,513 | same |
| Company-months per year | 16,455 / 16,023 / 16,667 / 18,145 / 21,013 | same |
| Companies read per year (1,000 rows and 10 months) | 49 / 47 / 56 / 79 / 115 | same set of names, same rows, not timely and months in every cell |
| Too few per year | 3,297 / 3,188 / 3,328 / 3,509 / 3,851 | same |
| Company and family cells read 2025 | 147 (8,790 too few) | 147 (8,790), all counts equal |
| Bureau window rows / not timely | EQ 3,095,639 / 87, EX 2,669,270 / 74, TU 2,988,010 / 228 | same, weighted bands equal to 6 places |
| All others not timely by year and window | 5,852 / 5,096 / 5,488 / 7,718 / 24,481 / 48,635 | same |
| Response categories, every group, every year and window | as in summary | same in every cell. The old categories (Closed, Closed with relief, Closed without relief) are empty in the window |
| Bureau credit reporting lag buckets, 15 cells | as in summary | same in every bucket. Zero rows sent before received, zero with no sent date |
| Bureau credit reporting not timely, 15 cells | as in summary | same |
| Q1d sent in 0 or 1 day by year | 455,588 / 766,909 / 1,261,184 / 2,692,559 / 5,279,537, 0 sent before received | same |
| Ruler one timely 2025 and interval | 99.5496 [99.3463, 99.6788] CANNOT_TELL | 99.5496 [99.3560, 99.6801] CANNOT_TELL |
| Ruler one 2022 | CONSISTENT, hi 99.4987 | CANNOT_TELL at seed 987654, hi 99.5006 (CONSISTENT in 20 of 20 other referee seeds, see R5) |
| Ruler two 2025 tally | 84 below, 15 above, 16 cannot tell | 83 below, 15 above, 17 cannot tell (seed, see R5) |
| Q1d 2025 | 96.998 [95.48, 98.15] CANNOT_TELL | 96.998 [95.37, 98.13] CANNOT_TELL |
| TCCP plans per file | 648 / 648 / 729 / 628 / 566 / 547 / 663 | same |
| TCCP plans with a median purchase APR | 272 / 233 / 253 / 245 / 551 / 527 / 625 | 260 / 233 / 253 / 245 / 528 / 502 / 599 (R1) |
| TCCP median of plan medians | 26.12 / 28.49 / 29.24 / 27.24 / 25.40 / 25.24 / 23.49 | 26.36 / 28.49 / 29.24 / 27.24 / 25.74 / 25.24 / 24.24 |
| TCCP 10th percentile | 11.50 / 16.97 / 17.55 / 15.90 / 14.85 / 12.93 / 10.92 | 14.90 / 16.97 / 17.55 / 15.90 / 15.97 / 14.90 / 12.25 |
| TCCP 90th percentile | 36.00 / 31.24 / 31.94 / 34.24 / 31.74 / 30.99 / 29.99 | 36.00 / 31.24 / 31.94 / 34.24 / 31.99 / 31.22 / 30.02 |
| Top 25 plans (2023 H2 on) | 203 / 184 / 413 / 410 / 406 | 203 / 184 / 390 / 385 / 380 |
| Top 25 median | 29.24 / 29.24 / 26.74 / 26.24 / 25.99 | 29.24 / 29.24 / 26.99 / 26.74 / 26.74 |
| Top 25 10th to 90th | 2024 H2 18.00 to 33.19, 2025 H1 17.99 to 33.24, 2025 H2 17.86 to 32.49 | 21.74 to 33.49, 21.49 to 33.24, 21.15 to 32.49 |
| Lowest min / highest max | as printed | same |
| Late fee plans | 531 / 552 / 658 / 543 / 487 / 470 / 540 | 538 / 559 / 665 / 550 / 494 / 477 / 550 including $0. The desk drops $0 (7 per file, 10 in 2025 H2). Medians equal at $29 |
| G.19 quarters and values | 2022 Q4 19.07 / 20.40 through 2025 Q4 20.97 / 22.30 | same, header4 is all accounts, header5 is accounts assessed interest |

## Findings

R1. Blocks ship. The TCCP "not applicable" code is read as an APR.
Evidence: the 2022 H2 file's notes say "Values of 999.00% should be interpreted as "not applicable"". The cells hold 9.99 (999 percent as a fraction). The desk's apr() reads any value above 1 as already in percent, so 9.99 enters as a 9.99 percent APR. The purchase median column holds 9.99 in 12 plans in 2022 H2, 23 in 2024 H2, 25 in 2025 H1 and 26 in 2025 H2, all at top 25 issuers. That inflates "plans with a purchase APR", pulls the medians and the 10th percentiles down (2025 H2 top 25 10th percentile 17.86 against 21.15), and moves the top 25 counts. Every APR in the seven files is a fraction except these codes and one 9.98 (Capital One, 2023 H1, Purchase APR min), which looks like the same code mistyped.
Fix: treat 9.99 (and 9.98) as not applicable, count them apart under "Nothing returned", recompute. The corrected figures are in the table above and in out/referee_tccp.json.

R2. Blocks ship. The shown-only G.19 sentence is false once R1 is fixed.
Evidence: the page says "Each G.19 figure falls inside the 10th to 90th percentile of the top 25 issuers' plan medians in every half year with that flag". With the codes removed, the G.19 all accounts rate sits under the top 25 10th percentile in 2024 H2 (21.47 against 21.74), 2025 H1 (21.16 against 21.49) and 2025 H2 (20.97 against 21.15). The accounts assessed interest rate stays inside in every half year.
Fix: recompute the display flags and write the sentence per half year. The outcome stays CANNOT_TELL.

R3. Fix before ship. "Plans with a purchase APR read" counts plans with a median, and that column changes coverage between files.
Evidence: from 2022 H2 to 2024 H1 the purchase median is blank for about 60 percent of plans (260 of 648, 233 of 648, 253 of 729, 245 of 628 have one), while 600 to 705 plans per file state a purchase APR minimum. From 2024 H2 on, about 95 percent of plans carry a median. So the median of medians covers a different, smaller set of plans in the four older files, and the drop from 29.24 to 25.74 between 2024 H1 and 2024 H2 crosses that break.
Fix: rename the column "Plans with a stated median purchase APR", print the plans with any purchase APR beside it, and say in one sentence that the four older files carry a median for under half their plans, so the medians are not a series across that break.

R4. Fix before ship. A gate was changed after the first run, and the page does not say so. The code is not committed.
Evidence: credit_history.jsonl shows the 17:50:48 run with gate false (rule self-test failed) and every outcome CANNOT_TELL as the plan requires. The 17:54:47 run has gate true and the readings appear. The summary's after_data_note says the planted-cell test "was changed after the first run from one planted draw to coverage over 40 draws". The change is reasonable, since one draw can miss by chance. But it is what turned the readings on, and the page only says "All known-good checks passed on this run". credit_tick.py, build_page.py, credit_headline.py, lint_copy.py and credit.html are untracked in git, while the page says "Plan and code for this page are public".
Fix: put the after_data_note sentence on the page next to the gate line, and commit the code before shipping so the version that made the page is fixed.

R5. Fix before ship. Some named readings are within bootstrap noise of a band edge.
Evidence (referee seeds 1 to 20 plus 987654, 2,000 draws each): Coinbase, Inc. 2025 is printed "above" (lo 0.4501 percent against a band top of 0.45) and reads above in only 7 of 20 seeds. Coinbase money transfer 2025 is printed "cannot tell" and reads above in 20 of 20. ID Analytics, Inc. 2025 is cannot tell in 17 of 20 (desk agrees). Harris & Harris, Ltd. 2025 is below in 19 of 20 (desk agrees). Ruler one 2022 is CONSISTENT in 20 of 20 seeds but its upper end is 99.499 against 99.5. Not one count differs. These are seed effects at an edge. The desk also seeds each cell with [20261110, crc32(name)], which is not literally the plan's "fixed seed 20261110".
Fix: keep the sealed outcomes. Mark every cell whose interval end is within 0.01 percentage points of a band edge as "at the edge of the band" (display only), and state the per-cell seed in the method line.

R6. Fix before ship. The Q1c reason uses a legal reading the source does not give.
Evidence: the page says "A complaint to the CFPB is not by itself the dispute notice the statute counts from." No primary source in data/raw/docs says that. The same section of the statute the page quotes, 15 U.S.C. 1681i(e), covers complaints the Bureau sends to the bureaus. Under (e)(3) each bureau "shall (A) review each such complaint to determine whether all legal obligations ... have been met", "(B) provide reports on a regular basis to the Bureau" and "(C) maintain ... records". It sets no day count. The CANNOT_TELL outcome is still right, because the file holds no date of company response and no date a bureau received a dispute.
Fix: drop the sentence. Quote 1681i(e)(3) and keep the no-response-date reason.

R7. Note, with one sentence to add. The base gap has a stated direction, and the printed figures come from this database.
Evidence: the 2025 report says "Complaints closed with an Alerted CFPB response are not published in the Consumer Complaint Database" and that companies gave about 540,800 administrative responses. That is about the size of the gap between more than 5.9 million sent and 5,442,927 published. The 2023 and 2024 reports source the timeliness flag in their footnote to a CFPB search API query with timely=No on this same database. If every unpublished complaint was answered on time, the database's not-timely count over the printed count sent gives 99.18 / 99.38 / 99.59 / 99.73 / 99.58 percent timely for 2021 to 2025, inside every printed band. Coverage of the printed count is 66 percent in 2021 and 92 to 98 percent after that. So the "cannot tell" readings come from the width of the company-month interval, not from any gap between the database and the printed figure. The page's "the two bases differ" is honest but does not say which way.
Fix: add one sentence naming the unpublished Alerted CFPB closures and the 2021 coverage. Optionally show the printed-base share above as display only, labelled as added after the data.

R8. Note. Zero-width intervals decide many "below" readings.
Evidence: a company with no not-timely complaint gets a bootstrap interval of exactly 0 to 0 and reads below. Of the 84 below in 2025, 15 would be cannot tell under Wilson. The page already says this and shows Wilson as display, added after the data. That is honest.
Fix (optional): write "below (none flagged)" in those rows.

R9. Note. One listed "company" is a database label.
Evidence: "Servicer under contract with Federal Student Aid", 3,296 rows in 2025, every one with Company response "Untimely response", reads 100 percent not timely, above.
Fix (optional): add a footnote that this is how the database names the entity and that every row carries "Untimely response". Name no cause.

R10. Note. Band edges are open on the wrong side.
Evidence: the plan writes the 2025 not-timely band as [0.35, 0.45). The timely band [99.55, 99.65) actually leaves (0.35, 0.45]. No reading sits exactly on an edge, so no outcome moves.

R11. Note. Fee fields.
Evidence: the late fee median leaves out plans stating $0 (7 to 10 per file), and the page calls the rest "Plans stating a late fee". summary_credit.json carries annual_fee_zero_share = 0.0 in every file. No file holds a zero annual fee because a blank means none stated, so the field reads as "no plan is fee-free". It is not on the page.
Fix: say "late fee above $0", and drop or rename annual_fee_zero_share before /credit/live.json goes out.

R12. Note. Sources checked.
Every quote in PLAN.md S1 to S4 matches the desk's copies word for word, including both footnote numbers (2025 report fn 24, 2024 report fn 28) and the 2025 Table 1 and 2024 Table 1 credit reporting rows as stored. Live refetches of consumerfinance.gov/complaint/process/, /complaint/data-use/, law.cornell.edu 15 USC 1681i and 12 USC 5534 were byte-identical to the stored copies, with no CAPTCHA or login. The annual report quotes were checked against the desk's .txt extractions only, because no PDF text tool is installed here. The G.19 definition quoted in S6 comes from the current release notes (g19_current.html), not from the history table. The history table labels its column "All credit card amounts", which is the Federal Reserve's own wording. The desk reads header4 as all accounts and header5 as assessed interest, which is correct.

Privacy: summary_credit.json and data/credit_live.json carry no key or value for ZIP code, State, Tags, Issue, Sub-issue, Company public response or narrative, no 5-digit ZIP-like value and no tag value. Clean.

Overclaim check of the page text, beyond the findings above: the headline matches the plan, its counts are exact, and its rule wording includes the 10-month condition. The "each company" section says the printed figure is an average and not a per-company limit. Q2 is held at CANNOT_TELL with the right reasons (plan-level and unweighted against account- or balance-weighted, banks only). The page names no cause.
