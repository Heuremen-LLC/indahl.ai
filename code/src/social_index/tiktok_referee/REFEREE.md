# Referee report: TikTok section (quarterly report against EU filings)

Referee: read-only refuting pass, 10 November 2026 UTC. This pass finishes a referee run that a Mac reboot cut off at about 05:40Z, after it had written its recounts but before it wrote a report. Nothing in `social_index/tiktok/` was edited.

Inputs read: PLAN.md with Addenda 1 to 3, CHECKS.md, tiktok_tick.py (read only, never imported), data/tiktok.json, data/components.json, data/sources.json, summary_tiktok.json, section_tiktok.html, the CGER release zips (README, dashboard templates, CSV), the database API documentation saved in data/raw/codebooks, TikTok's saved download pages (platform 30), and section 1's data/dsa.json and context_notes.json for TikTok's own DSA report.

## Verdict

**FIX THEN SHIP.** The arithmetic is right. All 60 EU rows, every market value on the page and all 404 numbers and outcomes in the page tables reproduce exactly from raw with our own code. The like-for-like check fails on the headline row, the same way the DSA section failed on notice rows. "Removed before any report" in TikTok's report and "own voluntary initiative" in the database are not the same set. The DSA rules count a removal that follows an ordinary user report as own initiative, and TikTok's own DSA report confirms that it does so. That definition alone predicts the ABOVE in all 12 quarters, so the headline does not stand. The 2026 automation BELOW changes direction depending on whether TikTok's new AI moderation category counts as automated in the database. Two copy items also block: one wrong number and limits the plan promised but the page does not carry. After the fixes, no committed outcome is decided. One reading defined after the data stays decided (videos removed, Jan to Mar 2026, ABOVE, with its limits stated). This changes rows and copy but no figures, so the next pass can be a page check only.

## Blocking items, each with its exact fix

**B1. "Removed before any report" against "own voluntary initiative" is not like for like. This covers all 12 quarters, in both the committed and the after-the-data columns.**
- TikTok's report defines proactive removal as removal "before it's reported", meaning before any user report.
- In the database, SOURCE_VOLUNTARY is "own voluntary initiative". Commission Implementing Regulation 2024/2835 (quoted in social_index/dsa/PLAN.md) defines own initiative as a decision "not preceded by an order from a Member State authority or a notice submitted through a notice and action mechanism as referenced in Article 16". An ordinary in-app report of a guidelines breach is not an Article 16 notice, so a removal after one is own initiative under the DSA.
- TikTok's DSA report note (section 1, context_notes.json) says the same in its own words. Notice actions are items "removed due to violation of our Policies and following being reported for illegal content".
- The counts show it, from TikTok's own filings:
  - In its report, TikTok puts at least 267,726 videos removed after a user report in Jan to Jun 2026, in the 25 listed EU markets alone (141,789 plus 125,937, at the rounding floor).
  - TikTok's DSA report for the same half year states 92,256 actions on notices across every content type.
  - The database holds 16,089 notice-labelled video removal statements for that half (12,875 plus 3,214).
  - So at least 175,000 reported-then-removed videos sit in "own initiative" in TikTok's DSA filings by definition.
- The database's 98.4% to 99.99% own-initiative share is therefore a superset measure, and the gap of 0.5 to 1.5 points or more is what the definitions predict. No label-free bound exists. The database has no field for "before any user report".
- Fix:
  - Set all 12 proactive_rate EU rows to CANNOT_TELL in both columns, with the reason "The two filings define report differently. TikTok's report counts any user report. The DSA counts only notices under Article 16, so removals after other user reports are filed as own initiative." Keep every figure.
  - Mark the rule as defined after the data, as a referee finding, in PLAN.md Addendum 4.
  - Retitle the table "Removed before any report (TikTok report) and own initiative (database)", and rename the database column "Database, own voluntary initiative".
  - Change the Apr to Jun 2026 summary row the same way.
  - Remove the headline "removed before any report, ABOVE in 8 quarters" from summary_tiktok.json and from anything Bones relays.
  - Rows moved: 8 committed ABOVE and 11 after-the-data ABOVE become CANNOT_TELL.

**B2. The 2026 automated share BELOW turns on how AI moderation is labelled (after-the-data column, Jan to Mar and Apr to Jun 2026).**
- From 2026, TikTok's report counts "AI Moderation" as automated (9.85% and 9.39% of EU listed removals). Before 2026 the automated figure is Automation alone.
- With Automation alone, the report reads 88.4% (Jan to Mar) and 89.0% (Apr to Jun). With the unlisted-market allowance, its range is 87.5% to 88.5% (Jan to Mar) and 88.1% to 89.2% (Apr to Jun). The database's fully automated share is 89.8% to 91.5% and 93.0% to 93.8% (93.9% at the top of the after-the-data range). That reads ABOVE in both quarters, by at least 1.3 and 2.8 points on the after-the-data range.
- With AI moderation counted, both quarters read BELOW. The direction flips on one label. That is the same signature the DSA referee used (M4) to relabel splits.
- TikTok's DSA report gives 94.0% solely automated for Jan to Jun 2026, and section 1 found it consistent with the database. Both of TikTok's DSA filings sit between the report's two readings.
- Fix:
  - In the after-the-data column, set 2026Q1 and 2026Q2 automated_share to CANNOT_TELL, with the reason "Below when AI moderation counts as automated, as TikTok's report counts it from 2026, and Above when it does not. The two filings may count AI moderation differently."
  - Print the Automation-only report share (88.4% and 89.0%) beside the row, in the column defined after the data.
  - Showing that figure names no mechanism. Drop CHECKS.md's P4 reason for keeping it off the page.

**B3. Wrong number in the prose.**
- The page says TikTok "filed up to 94% of a month's removal statements one to three months after the decision".
- Recount, using the desk's own lag definition (calendar months from decision month to filing month): November 2025 video removals, 5,351,631 statements, 97.5% filed one to three months later. December 2025 is 93.8%. For all removals the figures are 97.5% and 92.6%, and for all statements 97.2% and 92.1%.
- Fix: change "up to 94%" to "up to 97%" on the page and in PLAN.md Addendum 2.3.
- The same addendum's "about 36 million statements of all kinds filed in January 2026 for decisions taken in October to December 2025" also does not reproduce. The recount gives 107,859,110 statements of all kinds, 42,173,343 removals of all kinds and 12,595,443 video removals. Correct the addendum. The page does not carry this figure.

**B4. The limits the plan promised are not on the page.**
- PLAN.md says limits we cannot size are "stated on the page as limits, never as causes". The page states none.
- These limits matter for the one decided reading left, videos removed in Jan to Mar 2026, ABOVE (gap +874,363 to +12,341,191, or +4.7% to +66.5%).
- TikTok's report keeps two large removal counts out of "Total videos removed": "Videos removed from fake accounts" (147,943,238 globally in Jan to Mar 2026) and LIVE (50,791,858 sessions suspended). The release gives no market split for either. The database's video content type could hold statements for either, and duplicate statements cannot be detected in the aggregates.
- Fix: in "How we read it", and in the reason on that row, add: "TikTok's report counts videos removed from fake accounts and LIVE sessions apart from videos removed, and gives no market split for either. The database could hold statements for them, and one decision filed twice counts twice. We cannot size these, so an Above may include them."
- Restored videos are not a limit. TikTok's dashboard note says restored videos are "reflected in both the removal volumes and restored volumes".

## What reproduces (recount from raw, own code)

**Delivered side.**
- The desk's grouped month files (data/raw/dsa_tiktok) were checked against Commission files read independently of the desk:
  - 17 months (2025-07 to 2026-11) from section 1's own downloads, with sha1 identical to the desk's receipts.
  - 2 older months (2024-03, 2025-01) downloaded fresh in this pass, with sha1 identical.
  - 10 months were re-extracted and compared (2024-03, 2025-01, 2025-07, 2025-12, 2026-01, 2026-02, 2026-05, 2026-08, 2026-10, 2026-11).
- On every one of those 10 months, TikTok totals, totals by source type, automated decision, decision month, territorial scope, decision ground and creation day, the days-posted-to-decision distribution and the removals by content type match the desk's files exactly. There are 0 mismatching keys.
- Every delivered count, window edge, the Addendum 2.2 allowance (0 in every quarter) and the Addendum 3.2 widening reproduce exactly (code/delivered.py, code/r2_full.py, code/r2_posthoc.py).

**Stated side.** Every stated point and range edge reproduces exactly (code/stated.py, own CSV reader, sha256-checked zips). Revisions: 419 cells checked (EU, Norway and global), 0 differ. The desk checks 397 cells, without the global and Norway cells. Same result.

**Day check.**
- The published TikTok daily totals were parsed from the saved pages with our own parser.
- 1,138 days. 1,091 equal the files, including 41 days where neither side has a statement. The 47 that differ include 8 November 2026, which the files do not reach yet.
- Largest differences: 8 May 2026 (1,199,408 in the files against 340,518 published), 30 September 2026 (3,258,409 against 3,442,533), 1 February 2024 and 2 October 2026.
- The page's 858,890 and 184,124 are right.

**Scout correction confirmed.** The scout's 18,928,826 equals the complete aggregate's 18,459,847 plus 468,979. That is exactly the number of video removal statements created on 30 and 31 May 2026, which the simple aggregate holds twice. At the point the gap is +3.3%, and the row reads CANNOT_TELL (gap -0.1% to +44.2%).

**Markets not separable in 2026: confirmed.** Every Apr to Jun and Jan to Mar 2026 video removal statement has scope EEA or EEA_no_IS (two distinct values). Single-country scopes exist only before 2026, for example DE with 412,255 across all decision dates. They feed the 270 market rows read CANNOT_TELL.

## Recount table against the builder (EU rows that carry or carried a decided outcome)

Gap in points for shares and in % of the report figure for counts. "Builder" is section_tiktok.html and data/tiktok.json. "Referee" is the recount under the same rules. "After fixes" applies B1 and B2.

| Quarter | Measure | Report | Database | Gap range | Builder committed / after data | Referee recount | After fixes |
|---|---|---|---|---|---|---|---|
| 2023Q4 | before report / own initiative | 92.9% | 98.4% | +1.5 to +59.0 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2024Q1 | same | 96.4% | 99.95% | +1.4 to +59.6 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2024Q2 | same | 95.9% | 99.98% | +1.3 to +68.1 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2024Q3 | same | 95.4% | 99.4% | +1.1 to +64.8 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2024Q4 | same | 94.9% | 99.61% | +1.2 to +69.2 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2025Q1 | same | 96.4% | 99.99% | +0.9 to +76.2 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2025Q2 | same | 97.5% | 99.99% | +0.5 to +78.5 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2025Q3 | same | 97.4% | 99.99% | +0.7 to +73.6 | Above / Above | Above / Above | Cannot tell / Cannot tell |
| 2025Q4 | same | 97.5% | 99.94% | +0.8 to +66.5 | Cannot tell / Above | Cannot tell / Above | Cannot tell / Cannot tell |
| 2026Q1 | same | 99.2% | 99.94% | +0.7 to +1.8 | Cannot tell / Above | Cannot tell / Above | Cannot tell / Cannot tell |
| 2026Q2 | same | 99.2% | 99.98% | +0.7 to +1.9 (after data -0.3 to +1.9) | Cannot tell / Cannot tell | Cannot tell / Cannot tell | Cannot tell / Cannot tell |
| 2026Q1 | automated share | 98.3% (Automation only 88.4%) | 89.9% | -8.5 to -5.8 | Cannot tell / Below | Cannot tell / Below | Cannot tell / Cannot tell |
| 2026Q2 | automated share | 98.4% (Automation only 89.0%) | 93.0% | -5.4 to -3.5 (after data -6.4 to -3.4) | Cannot tell / Below | Cannot tell / Below | Cannot tell / Cannot tell |
| 2026Q1 | videos removed | 18,545,004 | 20,361,489 | +4.8% to +66.5% (after data +4.7% to +66.5%) | Cannot tell / Above | Cannot tell / Above | Cannot tell / Above, limits stated (B4) |
| 2026Q2 | videos removed | 17,864,150 | 18,459,784 | -0.1% to +44.2% | Cannot tell / Cannot tell | Cannot tell / Cannot tell | unchanged |

All other EU rows (videos removed and automated removals for every quarter, automated share before 2026, within 24 hours for every quarter, and every 2023Q3 row) read CANNOT_TELL from both builder and referee, with identical ranges. Totals:
- EU, committed: builder 8 ABOVE, 52 CANNOT_TELL. After fixes: 60 CANNOT_TELL.
- EU, after the data: builder 11 ABOVE, 2 BELOW, 47 CANNOT_TELL. After fixes: 1 ABOVE, 59 CANNOT_TELL.
- Market rows: 498 NOTHING_RETURNED and 270 CANNOT_TELL, unchanged. No market row can be decided, because no 2026 statement is placed in one market and before 2026 the placed counts are a sliver of the range.

## What each gate drops, by side

**Stated side:**
- 2026: Luxembourg, Malta, Iceland and Liechtenstein are not listed. They are carried as an allowance of 49,999 each, capped by the global remainder (99,998 EU and 199,996 EEA).
- Before 2026: 19 to 23 EU markets are not listed, each carried at the smallest listed market's count. That ranges from 392,920 (2023Q3) to 767,389 (2025Q3), and the allowance comes to 7.9M to 16.9M EU.
- No listed market lacks a value.

**Delivered side, Apr to Jun 2026, decision date, removals that are not ads:**
- Kept: video, 18,459,784.
- Dropped: text without video or image 34,849,101, image without video 2,419,090, other without video or image 5,449,687, account 137,975, audio 136,647. Ads with video are 0.
- Video statements that are not removals are dropped: disabled 200,414, age restricted 424,694, and visibility "other" 52,169,303 (TikTok's DSA note: "labeled as not recommended").
- The mapping is right to drop all of these. CHECKS.md I lists only disabled. Add the other two to the components for completeness. This does not block.
- The narrow (incompatible content) set equals the point set in 2026. Every video removal has ground incompatible content.

## Non-blocking notes

1. **1 February 2024.** KG3-days (b) as committed covers days from 11 February 2024. The desk's own extension shows that 1 February 2024 fails the same 1% test (64,172,650 against 59,466,872). Applied evenly, that would make every 2023Q4 and 2024Q1 EU row CANNOT_TELL in the committed column. Once B1 is in, every one of those rows is CANNOT_TELL anyway. If B1 is not taken, this note becomes blocking for 2023Q4 and 2024Q1 proactive.
2. The page's "1,091 of 1,138 days" counts 41 days where neither side holds a statement, and it counts 8 November 2026, which the files do not reach yet, as a mismatch. Consider "on every day both cover, except 46".
3. NOTHING_RETURNED reasons for unlisted markets do not print what the database holds, which PLAN.md asks for ("The reason prints what the other side holds").
4. Copy, checked:
   - The visible text has no semicolons.
   - Headings carry no counts of our own things.
   - There is no AI statement, and the page names no cause.
   - The after-the-data column is labelled.
   - The B1 and B2 reasons above are written to the same rules.

## Reproduce

From `~/bones-forge/social_index/tiktok_referee/`, run each script with `.venv/bin/python -I code/<script>`. Earlier run, reused after checking:
- `stated.py`: stated recount, writes stated_recount.json.
- `delivered.py`: delivered grid, writes delivered_recount.json.
- `outcomes.py`: committed-rule diff against data/tiktok.json, 0 mismatches. Writes outcomes_recount.json.
- `extract_check.py <unzipped Commission month> <desk parquet>`: desk extraction against a Commission file.
- `revisions.py`, `auto_only.py`, `content_band.py`.

This pass:
- `r2_full.py`: every EU row, committed and after the data. Writes eu_rows_recount.json.
- `r2_posthoc.py`: Addendum 3.2 widening for 2025Q4 to 2026Q2. Writes posthoc_recount.json.
- `r2_daycount.py`: published TikTok daily totals against the files.
- `r2_drops.py`: gate drops, scopes, source type by quarter.
- `r2_page_check.py [section html]`: every page number against the recount. Rerun after the fixes.

Older Commission months downloaded for this pass are in the session scratchpad only, so download again to repeat. Section 1's copies are at social_index/dsa/data/raw/agg/unz.
