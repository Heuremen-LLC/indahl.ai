# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## Data access and terms (scouted 10 Nov 2026)
- CFPB complaint database: U.S. government work, the search service states license CC0. Company-level counts only. ZIP code, State, Tags, Issue, Sub-issue, Company public response never read into any output. The file carries no narrative column.
- CFPB annual reports, TCCP survey: U.S. government works. Federal Reserve G.19: public.
- Requests one at a time, paced 1.5 s, user agent heuremen-credit/0.1 (+https://indahl.ai/credit). No CAPTCHA or login met, MANUAL_READS.md not needed.

## 2026-11-10 13:40 CREDIT first read and ship after the outside referee: CFPB printed timely and forwarding shares against the complaint database 2021 to 2025, each company against the printed share, bureau closures, FCRA 30 days cannot tell, TCCP beside G.19
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 8ef6f26 at 12:48:03 -05:00 (data/plan_seal.json), first comparison 17:50:48Z, plan unchanged since. Same quantity both sides: the timely flag the CFPB reports define, against the share the CFPB prints, read as the band its rounding allows. The none: companies with no not timely complaint read with a zero-width block interval, Wilson shown beside (15 of 84 below in 2025 would read cannot tell). Nothing returned: 0 bad dates, 0 timely values other than Yes or No, 0 missing sent dates, 0 duplicate ids, 8,279,815 rows outside the window
- II: holds: every cell prints rows, not timely, share, interval and reading apart. Cannot tell is never folded. Ruler one: 2021 cannot tell, 2022 consistent (at the edge), 2023 cannot tell, 2024 cannot tell, 2025 cannot tell. Companies 2025: 84 below, 15 above, 16 cannot tell, 3,851 too few
- III: holds: below and above keep their side: below means fewer not timely than the printed figure leaves. The pooled database share sits under the printed figure in 2021 and 2025 and above it in 2022 and 2024 as point values, all intervals cross or hold the band
- V: holds: plan ruler is the rounding band with the company-month block bootstrap. Shown beside and deciding nothing: Wilson intervals per company, the printed-base share if every unpublished complaint was timely (99.18, 99.38, 99.59, 99.73, 99.58, all inside their bands, referee R7), the more than 99% band for 2025 (consistent)
- VI: holds: four outcomes, both alternatives in the plan. Q1c FCRA 30 days cannot tell by plan (no company response date, no dispute receipt date). Q1d 2025 sent in 0 or 1 day 97.0 percent (95.5 to 98.2) cannot tell against 96.5 to 97.5. TCCP beside G.19 cannot tell, not like for like
- R: holds: counts read from summary_credit.json of the run on the file of 10 Nov 2026 10:15 (sha256 db661817). Gate 2: four cells equal the CFPB search service exactly (Equifax 2023 not timely 4, 2024 not timely 7,720, Experian 2025 rows 1,388,821, 2022 rows 800,245). Referee recount (credit_index_referee/code, own reader, own bootstrap seed 987654): every count identical row for row, 346 company-year cells and 147 company-family cells. Seed-edge differences: 2022 ruler one, Coinbase, Coinbase money transfer, Harris & Harris, ID Analytics (marked at the edge where within 0.01 points). Recorded lines:
  - timely 2021: 489,779 of 495,940
  - timely 2022: 795,130 of 800,245
  - timely 2023: 1,286,528 of 1,292,043
  - timely 2024: 2,726,532 of 2,734,252
  - timely 2025: 5,418,414 of 5,442,927
  - EQUIFAX, INC. 2025: 0 not timely of 1,680,537
  - Experian Information Solutions Inc. 2025: 32 not timely of 1,388,821
  - TRANSUNION INTERMEDIATE HOLDINGS, INC. 2025: 0 not timely of 1,601,849
  - companies 2025: 115 read
  - sent 2025: 5,279,537 of 5,442,927
  - fcra30: cannot tell
  - tccp 2025 H2: top 25 median 26.74
  - compfam 2025: 147 read
- P1: holds: quotes copied from fetched pages on 10 Nov 2026 and checked word for word by the referee: consumerfinance.gov/complaint/process/, /complaint/data-use/, the annual reports 2021 to 2025 (timely shares, footnote definition, 97% in a day or less, Alerted CFPB not published, Table 1), law.cornell.edu 15 USC 1681i (a)(1)(A), (B), (e)(3) and 12 USC 5534(b), G.19 release notes
- P2: holds: page figures come from summary_credit.json through build_page.py and credit_headline.py, the feed /credit/live.json is the same summary with 2025 company cells only, ledger rows credit.* cite this file
- P3: holds: timely, not timely, Company response to consumer categories, Top 25 institution, all accounts and accounts assessed interest as the sources name them. Companies named as the database names them
- P4: holds: no cause named. The page says a reading says where the database sits against a printed figure, not why
- P5: holds: every interval labelled a 95 percent company-month block bootstrap interval, Wilson named as such and shown only
- P6: fixed: referee R1 (TCCP 9.99 and 9.98 not applicable code read as an APR, now counted apart, 78, 1, 27, 27, 26 cells), R2 (the G.19 inside sentence is now computed per half year, all accounts below the top 25 10th percentile in 2024 H2, 2025 H1, 2025 H2), R3 (column renamed, minimum count added, series break stated), R4 (rule gate first-run failure and test change stated on the page, code committed), R5 (at the edge marks, seed stated), R6 (unsourced sentence dropped, 1681i(e)(3) quoted), R7 (base direction sentence and columns), R9 (database label footnote), R11 (late fee above $0, annual fee field dropped). R8, R10 (the not timely band reads (0.35, 0.45], no outcome moves), R12 noted
- P7: holds: ledger rows credit.* written staged before the site edit, flipped live inside the one site_lock ship command, release through ledger/ship.sh only
- P8: cannot tell: checked after the ship on the live page
- P9: holds: lint_copy.py 3 hits, all the company name I.C. System, Inc. read as first person, cleared here. No semicolons, no digits in headings, Heuremen LLC named, byline Wayfinder and Bones
- P10: holds: after-data additions are display only and listed in summary_credit.json after_data_note (Wilson, at the edge, printed-base share, TCCP not applicable code). The rule-gate test change is stated on the page. No band, cell, ruler or outcome definition changed
- O1: holds: rider on the tick bus every 1,800 ticks (about weekly), --publish puts credit_live in the site KV, served at /credit/live.json. tick_bus.py backed up .bak-20261110-credit and compiled with /usr/bin/python3
- O2: holds: a failed fetch names its file in source.stale and the run falls back to the last copy. A failed gate turns every outcome into cannot tell and keeps the original. The privacy gate stops the run before anything is written
- O3: n/a: no GPU, CPU arithmetic only (numpy)
- O4: holds: the feed carries generated and updated, data/credit_history.jsonl gets one line per run
- O5: holds: credit_tick.py chdirs to its own folder, wrangler by absolute path with PATH set as TORNADO does
- O6: n/a: no GPU job runs in this rider
