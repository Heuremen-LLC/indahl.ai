# Referee report: DSA section (two filings, one platform)

Referee: read-only refuting pass, 9 November 2026 HST (10 November UTC). Nothing in `social_index/dsa/` was edited.
Inputs read: PLAN.md and all five addenda, git history, dsa_tick.py, dsa_db.py, dsa_reports.py, dsa_html.py, data/dsa.json, data/automation_*.json, data/sources.json, data/context_notes.json, summary_dsa.json, section_dsa.html, the Annex II instructions of Regulation 2024/2835, the database API documentation and the dsa-tdb aggregate documentation, DSA Articles 17 and 24, and the raw files under data/raw/.

Referee code and outputs are in `dsa_referee/code/` (the referee's own readers, independent of dsa_db.py, dsa_reports.py and xls_biff.py):
- `recount_db.py` reads every part file of the 17 complete monthly aggregates (2,111 parquet files, 183,306,116 aggregate rows). `recount_ct.py` adds content types, the ads flag and `incompatible_content_illegal`. `db_side.py` and `db_side2.py` rebuild every delivered count and band edge and diff them against dsa.json.
- `rep.py` (CSV/zip), an XLSX reader inside `stated_all.py`, and `myxls.py` (a BIFF8 .xls reader written for this pass) rebuild every stated value. `stated_recount.json` is the output.
- `html_check.py` regenerates every number in the four page tables from dsa.json and diffs the page.
- `relabel_rows.json` lists every row this report asks to change, with the fix that changes it.

## Verdict

**FIX THEN SHIP.** The build cannot ship as it stands. The arithmetic is right on both sides. Every stated value, every delivered count, every band edge and every number on the page reproduces exactly from raw. The blocking problem is a mapping error. YouTube, Google Maps and Google Play publish their ads moderation in separate `_Ads` template files. The pipeline drops those files on the report side but counts the ads statements on the database side. For YouTube that turns BELOW into ABOVE. Three more problems must be fixed before ship. The notice rows compare sets that the two filings label differently. Addenda 4 and 5 were applied to some platforms and not to others whose notes or arithmetic qualify on the same terms. And several split rows read in opposite directions because the two filings label the same decisions differently. After the fixes, the rows that change (YouTube, Google Maps, Google Play, Facebook, Instagram, the notice rows) need one more referee pass before they go public, because the YouTube reading reverses direction.

Rows to change: 87 of 475 (85 required, 2 a documented judgment call). The full list is at the end and in `code/relabel_rows.json`.

---

## 1. Recounts from raw

### Database side

My reduction matches dsa.json exactly on D_app, D_cre and the Iceland/Liechtenstein/Norway-only count for every measured row, and on D_lo and D_hi (including own_auto, the late-day allowance and the short-day shortfall) for every row. Mismatches: 0. The shortfall inputs come from the saved per-platform download pages. My own parse of those pages for X, YouTube and TikTok gives the same published daily totals.

Daily totals over all platforms against the Commission's published totals: 370 days match exactly, 120 match within 0.043%, and 3 fail (30 September, 1 October, 2 October 2026, the same three days as Addendum 2). Nothing is missing before 1 November 2026. The aggregate lacks 1 and 2 November 2026, and the download page lists no file for those days either. On the six days of Addendum 1, the simple aggregate is exactly 2.0000 times the complete aggregate, and the complete aggregate equals the published total to the statement. Territorial scopes classed as naming no EU state are only IS, LI, NO and their combinations (350,199 statements in all). No mis-coded EU state (for example EL for Greece) shows up.

### Report side

All 405 stated values with a figure were reread with my own readers. Mismatches: 0. (For Apple 2025H2, my reader needed one fix to match the service cell "AppStore", and the values agree.) The file versions chosen are the latest: X's corrected sheets, Amazon's sheet 6 version 2, Snapchat V2, Pinterest's 2026-10-08 update, Wikipedia's corrected upload.

### The requested rows (stated / database by decision date / database by submission date / published outcome)

| Row | Stated | D_app | D_cre | Published | Referee |
|---|---|---|---|---|---|
| YouTube Jan–Jun 2026, all measures | 36,427,838 (34,496,297 + 1,931,541) | 42,198,828 | 42,030,289 | ABOVE 1.158 [1.153, 1.162] | Figures right, mapping wrong (see M1): BELOW 0.081 |
| YouTube Jan–Jun 2026, solely | 34,496,297 | 23,682,089 | 23,600,496 | BELOW | Stays BELOW once ads are removed (non-ads fully automated: 169,866) |
| YouTube Jan–Jun 2026, not | 1,931,541 | 16,003,761 | 15,917,847 | ABOVE 8.29 | CANNOT TELL once ads are removed (non-ads 269,006, plus 2,512,978 partially) |
| X Jul–Dec 2025, all measures | 21,270,193 | 216,372 | 216,487 | BELOW 0.010 | Confirmed |
| X Jul–Dec 2025, own initiative | sheet 5 TOTAL blank | 0 | 0 | CANNOT TELL | Confirmed (blank rule) |
| X Jul–Dec 2025, own T&C | 220,937,367 (corrected file, largest column 186,083,779) | 0 | 0 | BELOW | Confirmed. X's zip also holds the original sheet 6 at 20,868,183. BELOW either way |
| X Jan–Jun 2026, all measures | 17,896,502 | 1,308,137 | 1,306,755 | BELOW 0.073 | Confirmed |
| X Jan–Jun 2026, own initiative | 148,269,257 (0 + 148,269,257) | 0 | 0 | BELOW | Confirmed |
| Google Shopping Jan–Jun 2026, all measures | 1,696,060,640 | 1,706,954,363 | 1,605,399,478 | CONSISTENT [0.946, 1.010] | Confirmed |
| Google Shopping Jan–Jun 2026, own T&C | 1,696,059,537 | 1,705,725,110 | 1,604,190,366 | CONSISTENT | Confirmed |
| Google Shopping Jan–Jun 2026, notices | 1,103 (192 + 911) | 1,217,662 | 1,197,517 | ABOVE 1,104× | Figures right, mapping not like for like (M2) |
| Facebook Jan–Jun 2026, all measures | 182,815,409 | 215,709,809 | 215,737,001 | ABOVE 1.180 | Figures right. Meta's own note makes the service split unreliable (N-A) |
| Facebook Jan–Jun 2026, own illegal / own T&C | 168,282 / 182,647,127 | 20,170 / 215,491,312 | 20,145 / 215,517,896 | BELOW / ABOVE | Opposite readings on one ground split (M4) |
| Instagram Jan–Jun 2026, all measures | 64,344,212 | 48,904,375 | 48,863,021 | BELOW 0.760 | Figures right. Same Meta note (N-A) |
| Instagram Jan–Jun 2026, notices | 68,147 (1,820 + 66,327) | 134,329 | 133,446 | ABOVE 1.97 | Items notified 367,661 → CANNOT TELL (M2) |
| Snapchat Jul–Dec 2025, notices | 2,961 (2 + 2,959) | 1,755,931 | 1,755,931 | ABOVE 593× | Figures right. Snap's note moves user reports out of sheet 4 (M2, N-A) |
| Snapchat Jan–Jun 2026, notices | 4,223 (28 + 4,195) | 1,792,050 | 1,792,015 | ABOVE 424× | Same |
| Snapchat TF notices, both halves | 407 / 634 | 390 / 1,063 | 390 / 1,062 | CANNOT TELL | Confirmed |

Five random rows, drawn with `random.Random(20261110).sample` from the 292 rows that have a stated figure and are not named above. All reproduce:
- Zalando Jan–Jun 2026, not: 2,745 against 2,676 / 5,123. CANNOT TELL.
- Amazon Jan–Jun 2026, own T&C: 437,190,165 against 273,230,109 / 251,552,333. CANNOT TELL (the plan rule reads BELOW).
- Wikipedia Jan–Jun 2026, own illegal: 0 against 0. CONSISTENT (my BIFF reader).
- XVideos Jul–Dec 2025, TF notices: 0 + 0 against 0. CANNOT TELL.
- Google Maps Jan–Jun 2026, all measures: 12,731,584 against 25,525,203 / 25,457,290. ABOVE. Still ABOVE once ads are removed (1.70).

---

## 2. Field mapping

### M1. Ads templates are dropped on one side and counted on the other. Severity: blocks ship.

Evidence. The Google reports for YouTube, Google Maps and Google Play each contain `8_automated_means_Ads.csv` and `6_own_initiative_TC_Ads.csv` next to the main sheets. dsa_reports.py excludes any sheet whose name ends in "ads" (the `ADS` regex, plus the `(?![ _]*ads)` lookahead on sheet 8). The database side keeps every statement. The complete aggregate carries a `CONTENT_TYPE_AD` flag:

| Service, half | Ads template (sheet 8 total) | DB ads statements (app basis) | Ratio | Main template | DB non-ads statements | Ratio |
|---|---|---|---|---|---|---|
| YouTube Jul–Dec 2025 | 48,253,773 | 48,746,693 (94.7% of all) | 1.010 | 30,366,858 | 2,704,863 | 0.089 |
| YouTube Jan–Jun 2026 | 38,746,603 | 39,246,978 (93.0%) | 1.013 | 36,427,838 | 2,951,850 | 0.081 |
| Google Maps Jul–Dec 2025 | 3,470,387 | 3,530,472 | 1.017 | 26,509,207 | 27,141,449 | 1.024 |
| Google Maps Jan–Jun 2026 | 3,741,944 | 3,784,792 | 1.011 | 12,731,584 | 21,740,411 | 1.708 |
| Google Play Jul–Dec 2025 | 271,794 | 271,772 | 1.000 | 4,234,416 | 1,236,506 | 0.292 |
| Google Play Jan–Jun 2026 | 201,814 | 201,512 | 0.999 | 4,331,843 | 1,080,391 | 0.249 |

The match holds field by field. YouTube ads, Jan–Jun 2026: template solely 23,139,243 against database fully automated 23,512,223, and template not 15,607,360 against database not automated 15,734,755. YouTube's large "not automated" ABOVE (8.29 and 12.9) is the ads template showing through. Google Shopping (0.1% ads) and its report ("metrics reflect ... both unpaid content and advertisements") are consistent. Apart from Temu (0.2%), no other mapped platform has ad-flagged statements.

Effect. YouTube all measures flips from ABOVE to BELOW in both halves. Own T&C flips the same way (0.084, 0.077). Not automated flips from ABOVE to CANNOT TELL. The Jan–Jun 2026 TF notice row (3,474 statements, all of them ads) flips from ABOVE to CANNOT TELL. The Jan–Jun 2026 share row flips from BELOW to CANNOT TELL. For Google Maps Jul–Dec 2025, all measures and own T&C flip from ABOVE to CONSISTENT (1.024 to 1.054), solely and share flip from CANNOT TELL to CONSISTENT, and not automated flips from ABOVE to CANNOT TELL. Google Maps Jan–Jun 2026 stays ABOVE on all measures, solely and own T&C, with not automated becoming CANNOT TELL. Google Play outcomes do not change. 15 rows change.

Fix. For any service whose report has an `_Ads` template, compare non-ads statements (`CONTENT_TYPE_AD` false) with the main template. Add ads rows that compare ads statements with the Ads template. Say on the page which side carries the ads. Commit this as a dated addendum labelled "defined after the data". Re-referee the YouTube rows before publishing, because the public reading reverses direction.

### M2. "Actions on notices" against statements labelled Article 16 or trusted flagger. Severity: fix before ship.

The template (Annex II 1.3) defines columns L and N as "the number of actions that were taken after a notice". It does not say whether an action is counted per notice or per item. Column H counts items notified. The database files one statement per decision, which means per item. Two failures follow.

(a) Unit. When a report counts actions per notice, the database can hold more statements than actions without anything being missing. The report's own column H bounds this. Setting the upper edge of the stated band to max(actions, items notified) turns every remaining notice ABOVE into CANNOT TELL. Examples: Facebook Jul–Dec 2025 drops to r_lo 0.11, Instagram Jan–Jun 2026 to 0.36, TikTok Jan–Jun 2026 to 0.40, Shein to 0.47 and 0.54, Google Play to 0.70 and 0.96, WhatsApp to 0.90. On TF notices with column I: Facebook 0.016, TikTok 0.84 and 0.53.

(b) Label. On 11 notice rows the database holds more notice-labelled statements than the report says items were notified at all, so no counting unit can reconcile the two:

| Row | Items notified (col. H) | DB A16+TF statements |
|---|---|---|
| Snapchat H2 / H1 | 6,726 / 9,117 | 1,755,931 / 1,792,050 |
| Google Shopping H2 / H1 | 2,339 / 3,473 | 1,252,070 / 1,217,662 |
| XVideos H2 / H1 | 9,773 / 12,582 | 521,146 / 379,253 |
| XNXX H2 / H1 | 17,255 / 17,837 | 67,586 / 55,123 |
| LinkedIn H2 | 1,503 | 24,564 |
| Amazon H2 / H1 | 186,122 / 167,678 | 931,347 / 700,281 |

Snap explains it in its own sheet 4 note: "EU user reports of Community Guidelines violations, previously included here, have been reclassified to the 'own initiative' fields." LinkedIn's database notice count goes from 24,564 in H2 to 4 in H1 while its report goes from 484 to 2,730, so the label moved between halves. Google Shopping's report counts 1,611 notices received in H1 against 1.2 million notice-labelled statements.

The BELOW side is no safer. Apple files every statement as own initiative (zero A16, TF or other-notification statements), so its notice BELOW only reflects that label choice. WhatsApp's TF BELOW is 4 against 0.

Fix. Show notice and TF-notice rows without an outcome ("the two filings label notice sources differently"), with the counts kept. Keep an outcome only where it holds when every statement the platform filed is counted. Only X Jul–Dec 2025 notices passes that test: all 218,598 X statements are fewer than 0.9 × 388,095. This changes 28 rows: 18 notice ABOVE, 4 TF ABOVE (YouTube's TF row is under M1), Apple notice BELOW in both halves, WhatsApp TF BELOW, and notice CONSISTENT for Instagram H2, Google Maps H1 and Zalando H1 (with items allowed, r_lo falls to 0.17, 0.71 and 0.31). Label the rule as defined after the data.

### M3. X and "other type of notification". Severity: note.

Every X statement in the window is labelled other type of notification, with ground illegal content, and 99.9% carry content type synthetic media (216,236 of 216,372 in H2, 1,308,014 of 1,308,137 in H1). X files nothing as own initiative and nothing as an Article 16 or trusted flagger notice. The plan puts other-notification on the upper edge of both the own and notice bands, so X's upper edges equal its whole filing. Every X BELOW therefore holds even if every X statement is counted under every filter. The X readings stand. One gap: 1,469 statements under the name "X (formerly Twitter)", created 19 November 2025, have the same profile, with application dates in October and November 2025. They are not mapped. X Jul–Dec 2025 goes from 216,372 to 217,841, and no outcome moves. Fix: map the name or disclose it.

### M4. Label-dependent splits read in opposite directions. Severity: fix before ship.

The split measures (solely or not, own illegal or own T&C, own or notice) depend on how each filing labels the same decision. The plan bridges only the partially-automated and other-notification categories. In 13 pairs one half reads ABOVE and the other BELOW, which is the signature of a label difference rather than missing or extra statements. Examples: XVideos (database fully automated 0, report solely 229,270, database not automated 598,010, report not 35,949), XNXX, Temu H2, Pornhub H2, WhatsApp (report 886,271 own-initiative illegal measures, all geo-blocks, against 0 illegal-ground statements, and 102,483 T&C measures against 198,183 T&C statements), Snapchat H1 (own illegal ABOVE on one statement), Facebook H1. After M1 and N-A, 11 pairs (22 rows) remain.

The same logic as the other-notification allowance applies to ground. The other ground's own-initiative statements belong on the upper edge of each ground split. That changes own-illegal BELOW for Facebook (both halves), Instagram (both halves) and Pornhub H2. It applies to source as well. Notice-labelled statements beyond the items notified belong on the upper edge of own. That changes only XVideos H2 own (r_hi goes to 2.46). XVideos H2 own T&C is already in a pair.

Fix. Relabel these 28 rows CANNOT TELL with the reason "the two filings label this split differently". Keep the label-free rows (all measures, and own as sheets 5 plus 6) as the readings. Label the rule as defined after the data.

---

## 3. The addenda

### Is publishing under them sound?

**KG2 (Addendum 1): sound.** The failure sits entirely in the simple aggregate. It is exactly 2.0000 times the complete aggregate on 9–12 February and 30–31 May 2026, and the complete aggregate equals the published daily totals to the statement on those days. No reading uses the simple aggregate. Replacing KG2 with KG1-all is right, and KG1-all reproduces (370 exact, 120 within 0.043%, 3 failures).

**KG4 (Addendum 1.2): sound.** 1–2 November 2026 lie outside both created-date windows. The allowance tops out at 110 statements (Amazon H2 total) and flips no row.

**Addenda 2–3: sound and conservative.** The per-platform shortfall goes only on upper edges, so it can remove gaps and never create one. It is far wider than the data supports. Only 703 statements created on 30 September to 2 October 2026 carry an application date in either half, all of them Amazon. Yet TikTok's rows carry 272,044 and Temu's 244,093. Acceptable as written, but say on the page that this allowance is the reason many TF and own-illegal rows read "cannot tell".

**Provenance: note.** `data/tick_log.txt` (written 21:11:41) records a full build, "475 rows, outcomes {'CANNOT_TELL': 475}", with KG1-all failing. That run happened before Addendum 2 (committed 21:13:47) and Addendum 3 (21:18:01). heuremen_kit.apply_gate keeps `outcome_before_gate` on every row, so a file of computed comparisons existed when those addenda were written "before any comparison row was read". The claim cannot be checked. The risk is low because both addenda only widen bands. Disclose the 21:11 gated build in PLAN.md.

### Rows each addendum flips

| Addendum | Rows flipped | Direction |
|---|---|---|
| 1 (gate replaced) | 231 rows decided that the plan as committed leaves CANNOT TELL (all 475 rows are CANNOT TELL as committed, 27 of them NOTHING RETURNED under the addenda) | Un-gates outcomes of both kinds, gaps and agreements |
| 1.2 (1–2 Nov allowance) | 0 | — |
| 2 | 0 (replaced by 3) | — |
| 3 (short-day shortfall) | 48 | All to CANNOT TELL (BELOW 27, CONSISTENT 21) |
| 4 (platform notes) | 10 | All to CANNOT TELL (BELOW 9, ABOVE 1) |
| 5 (restriction columns) | 0 | — |

Addenda 4 and 5 do not move outcomes toward gaps. They only remove gaps. The problem is coverage. Each was applied to some platforms and not to others that qualify on the same terms (section 6). Uneven removal of gaps leaves gaps standing selectively, which is the neutrality failure.

### Disclosure. Severity: fix before ship.

The page never says that under the plan as committed every row reads "cannot tell" because KG2 and KG4 failed. Add one plain sentence: "Two of the four checks committed with the plan failed. Under the plan as committed every row would read cannot tell. We located both failures before reading the comparisons and replaced the checks in dated addenda."

---

## 4. Bands

- **Decision date against submission date: adequate.** The two bases differ sharply where platforms file late. Amazon's H2 decisions: 46.9% filed after 31 December, with batches in February and March 2026. TikTok: a batch of 107.9 million in January 2026. Shein: 96.8% of its H2 statements filed in April 2026. Zalando: 89% filed in March and April 2026. Taking the min and max of the two bases covers this inside the window.
- **Filings after 7 November: note.** Amazon, Shein, Zalando and the App Store have a history of filing months late. Their H1 counts can still grow. Amazon's H1 batch (148.9 million) arrived in August, and nothing large has arrived since. Name "statements filed after 7 November 2026" in the reason for BELOW rows.
- **Partially automated category: adequate** for what it covers. Facebook, Instagram, Amazon and Pinterest label almost everything partially automated, so their solely and not rows are CANNOT TELL, which is correct. It does not cover filings that label the same decision fully automated in one place and not automated in the other (M4).
- **Rows inside an honest band:**
  - Every notice ABOVE (M2).
  - YouTube and Google Maps ABOVE (M1).
  - XVideos H2 own BELOW (M4).
  - Instagram's and Pinterest's own and own-T&C rows once Addendum 5 is applied by arithmetic (section 6).
  - Amazon H1 all measures and not automated, if the band allows that Amazon's sheet 8 total (437,879,351) is built from its sheet 6 column sum (437,190,165, which equals the sum of columns H to U) plus notices. With the largest column (250,178,676) plus notices as the lower edge, r_hi is 1.10 and the row becomes CANNOT TELL. This is a judgment call. Decide it and write the decision down.
- **Small counts: fix before ship.** The agreement band is purely relative. These rows are decided by fewer than 100 statements:
  - Snapchat H1 own illegal: ABOVE on 1 statement against a stated 0.
  - TikTok H1 TF: ABOVE by 3 statements past the 1.10 edge.
  - TikTok H2 TF: ABOVE by 31.
  - Pornhub H1 own illegal: ABOVE by 31.
  - WhatsApp TF: BELOW, 4 against 0.
  - WhatsApp notices: ABOVE by 93.

  Add an absolute floor, for example "the edge must be cleared by at least 100 statements", labelled defined after the data. All but Pornhub H1 own illegal are already covered by M2 or M4.
- **Rounding at the edge: note.** YouTube H2 solely prints its upper edge as "0.900" (actual 0.90031) and Zalando H2 all measures prints "1.100" (actual 1.0997). Both read "cannot tell" correctly, but the printed edges look like they sit on the line. Print four significant figures within 0.005 of an edge.

---

## 5. Copy

Checked and clean:
- No adjectives about platforms outside quoted notes. The only hit is "very large online platform", the legal term.
- No cause named in our own words. Causes appear only inside the platforms' quoted notes.
- The bracket is defined ("the range the scope differences we can size allow. It is not a sampling interval").
- Every figure says where it lives (sheet 8 Total number, sheets 5 and 6 TOTAL column F, sheet 4 TOTAL).
- No semicolons in visible copy.
- Rows that use Addenda 4 or 5 carry "defined after the data".
- Every number on the page matches the data: 407 table cells regenerated, 0 differences. The automation-fields table matches my recount on all 46 rows. The simple-aggregate sentence ("counts statements twice") is exact.

Fix before ship:
1. **The BELOW reason names one unsized difference** (unknown contact details) as if it were the only one. Name the others the reports themselves show: how a filing counts one decision (per item, per account, per restriction type, TOTAL built as a column sum), filtering at upload (LinkedIn's note: "automatically filter out certain policy-violating content at the time of creation", Apple: "ratings and reviews removed before ... publication"), and statements filed after 7 November 2026.
2. **The ABOVE reason** should name its unsized differences the same way: how each filing attributes EU relevance, and one decision filed as more than one statement. The aggregate cannot detect re-filings.
3. **Plan-as-committed sentence** (section 3).
4. **Ads.** Once M1 is fixed, say which rows exclude ads. Until then the automation-fields table shows YouTube shares that are 93% ads moderation.
5. **"Matches the Commission's published daily totals on every day but three"** should read "within 0.05% on every day but three".

Note: the read date prints as "10 November 2026", the UTC date with no zone. House rule is HST in public. Either print 9 November 2026 or label the zone.

---

## 6. Neutrality (same rules for every platform)

**N-A. Addendum 4 was applied to some notes and not to others that fit its own wording. Severity: fix before ship.**
- **Snapchat, sheet 4.** "EU user reports of Community Guidelines violations, previously included here, have been reclassified to the 'own initiative' fields." Addendum 4 rule two covers exactly this: "a note stating the field leaves out measures the database can hold". Snapchat notices ABOVE (593× and 424×) should have become CANNOT TELL. Snap's trusted flagger note ("a single 'action' ... may encompass ... multiple individual pieces of content") was applied to TF notices only. Column O sits inside column N, so it bears on the notice row too. Covered by M2.
- **Facebook and Instagram, sheet 6.** "Visibility restriction removal contains some actions for Facebook and Instagram combined" and "The data in this column [provision of the service termination] contains actions for Facebook and Instagram combined". Both reports' sheet 6 TOTAL equals the column sum, and each sheet 8 total equals sheets 5 plus 6, so the shared actions reach all three measures. The note does not say which service carries them, so both directions apply. That gives 11 rows to CANNOT TELL: Facebook H1 all measures, own and own T&C (ABOVE), Instagram H1 all measures, solely, own, own T&C and own solely automated (BELOW), and Instagram H2 all measures, own and own T&C (CONSISTENT). Addendum 4.4 mentions only the French Guiana and Åland note. A combined Facebook plus Instagram row is the clean replacement: H2 is 236,955,892 against 227,835,881, giving 1.040 [1.040, 1.097] CONSISTENT. H1 is 264,614,184 against 247,159,621, giving 1.071 [1.071, 1.116] CANNOT TELL.
- **Apple.** Account terminations "include terminations of App Store developers, Apple Media Services customers and Apple Ads advertisers" (5,044,102 and 3,615,694), which reaches beyond the App Store. Removals include reviews removed "before ... publication". No Apple outcome moves even with the terminations taken out (the largest column, 11.4 million and 8.1 million, still dwarfs 107,555 and 50,872 statements). Record the reason it does not change the outcome, as Addendum 4.4 does for others.
- **Notes with no effect.** WhatsApp ("violations ... for either service can result in account termination for both services") has a blank account-termination column. Meta's own note that its age-restricted, interaction-restricted and labelled columns are "not taken on the basis that the content is illegal or violates our terms" also covers blank columns. Snap's "Other" column (low-quality content, 14,285 and 8,619) is too small to move anything. List these in the addendum so a reader can see every note was handled by one rule.

**N-B. The Addendum 5 trigger is not neutral. Severity: fix before ship.** Addendum 5 fires for TikTok, X and Snapchat because their notes say TOTAL is a column sum. Sheet 6 TOTAL equals the sum of columns H to U exactly in 38 of the 45 reports (36 without Wikipedia's all-zero rows). That covers both halves of Facebook, Instagram, Amazon, Apple, Pinterest, LinkedIn, YouTube, Google Maps, Google Play, Google Shopping, Temu, Shein, XVideos, XNXX, Zalando and X, plus WhatsApp, Booking.com H2, Snapchat H1 and TikTok H1. The exceptions are AliExpress, Booking.com H1, Pornhub, Snapchat H2 and TikTok H2. TikTok H2 is below its own sum even though TikTok's note says it sums the columns. The addendum's logic ("a decision appears at most once in each column") holds for every one of these. Applied by arithmetic it flips 6 rows to CANNOT TELL (Instagram own and own T&C in both halves, Pinterest own T&C in both halves). Where it was applied it flipped none. Fix: apply it to every report whose TOTAL equals the column sum, or withdraw it. Withdrawing changes no published outcome but leaves the unit difference unsized for everyone, so the BELOW reason must then name it (section 5).

**N-C. Equal treatment holds elsewhere.** Names map exactly for every platform (apart from the X variant in M3). The template and blank-field rules are applied uniformly. Every platform gets the same bands, other than the uneven Addendum 4 and 5 coverage above.

---

## Rows to drop or relabel

Required changes (85), then the judgment call (2). "→ CT" means show the counts without an outcome or as CANNOT TELL with the stated reason.

**B1 ads split (recompute, blocks ship), 15 rows**
- YouTube Jul–Dec 2025: all measures ABOVE → BELOW, solely CT → BELOW, not automated ABOVE → CT, own T&C ABOVE → BELOW.
- YouTube Jan–Jun 2026: all measures ABOVE → BELOW, not automated ABOVE → CT, own T&C ABOVE → BELOW, TF notices ABOVE → CT, share BELOW → CT.
- Google Maps Jul–Dec 2025: all measures ABOVE → CONSISTENT, solely CT → CONSISTENT, own T&C ABOVE → CONSISTENT, not automated ABOVE → CT, share CT → CONSISTENT.
- Google Maps Jan–Jun 2026: not automated ABOVE → CT.
- Google Play rows are recomputed with the same outcomes.
- Add ads rows for all three services.

**F1 notices → CT, 28 rows.** Keep X Jul–Dec 2025 notices BELOW.
- Notices ABOVE: Facebook H2, Instagram H1, TikTok H1, LinkedIn H2, Snapchat H2 and H1, Amazon H2, Shein H2 and H1, Google Play H2 and H1, Google Shopping H2 and H1, XVideos H2 and H1, XNXX H2 and H1, WhatsApp H1.
- TF notices ABOVE: Facebook H1, TikTok H2 and H1, Google Shopping H1.
- Notices BELOW: Apple H2 and H1. TF notices BELOW: WhatsApp H1.
- Notices CONSISTENT: Instagram H2, Google Maps H1, Zalando H1.

**F2 Meta combined-services note → CT, 11 rows**
- Facebook H1: all measures, own, own T&C.
- Instagram H1: all measures, solely, own, own T&C, own solely automated.
- Instagram H2: all measures, own, own T&C.
- Add the Facebook plus Instagram combined rows.

**F3 Addendum 5 applied by arithmetic → CT, 2 rows (plus Instagram, already in F2)**
- Pinterest own T&C, H2 and H1.

**F4 label-dependent splits → CT, 28 rows**
- Opposite pairs: Pornhub H2 solely and not, Snapchat H1 own illegal and own T&C, Temu H2 solely and not, WhatsApp H1 own illegal and own T&C, XNXX H2 and H1 solely, not, own illegal and own T&C, XVideos H2 solely, not, own illegal and own T&C, XVideos H1 solely and not.
- Ground allowance: own illegal for Facebook H2 and H1, Instagram H2 and H1, Pornhub H2.
- Source allowance: XVideos H2 own.

**F5 small count → CT, 1 row**
- Pornhub H1 own illegal.

**Judgment call, 2 rows (decide and document)**
- Amazon H1 all measures and not automated, BELOW → CT, if sheet 8 is read as built from sheet 6 column sums.

What remains after the required changes: 39 ABOVE, 84 BELOW, 35 CONSISTENT, 290 CANNOT TELL, 27 NOTHING RETURNED.
- All measures ABOVE: AliExpress H2 and H1, Google Maps H1, Pornhub H1, TikTok H1, XVideos H2 and H1.
- All measures BELOW: Apple H2 and H1, LinkedIn H2 and H1, Temu H2 and H1, WhatsApp H1, X H2 and H1, XNXX H2 and H1, YouTube H2 and H1. Amazon H1 too unless the judgment call changes it.
- All measures CONSISTENT: Booking.com H2, Google Maps H2, Google Shopping H2 and H1, Pinterest H1.

Every rule introduced by these fixes is defined after the data. Each must go into PLAN.md as a dated addendum and carry the "defined after the data" label on the page, with the plan's own outcome kept on the row.

---

# SECOND PASS

Referee: read-only, 9 November 2026 HST (10 November UTC). Scope as asked: the YouTube, Google Maps and Google Play main and ads rows, the Facebook, Instagram and combined rows, every notice row, Addendum 6.5, and the page against the data. Inputs: PLAN.md Addendum 6 and its record of effects (commits 7cbdf70 and 54baba4), the new dsa_tick.py, dsa_db.py, dsa_reports.py and dsa_html.py, data/dsa.json, summary_dsa.json, section_dsa.html and public/*.json. Nothing in `social_index/dsa/` was edited, and `git status` there is clean. The aggregates are the same files as in pass one (no sha1 changed, newest day still 7 November 2026). The builder's own run of my first-pass scripts left its outputs in `dsa_referee/code/out/`. I left them there.

New referee code in `dsa_referee/code/`:
- `recount_db2.py` redoes the reduction with the ads flag and the X alias.
- `stated_all2.py` rereads every report, now including the Ads sheets, spam rows, order items and trusted flagger items.
- `second_pass.py`, `second_pass_share.py` and `second_pass_final.py` are my own implementation of Addendum 6 as written in PLAN.md.
- `html_check2.py` checks all six page tables.

## Result in one line

Everything reproduces. My implementation of Addendum 6 gives the same stated value, stated edges, D_app, D_lo, D_hi and outcome on every comparison row:
- 387 main rows (every platform with a report, all nine measures)
- 24 ads rows and 12 combined rows
- 51 share rows

Final counts match: 39 / 82 / 35 / 292 / 27 on the original rows, 6 consistent and 24 cannot tell on the ads rows, 14 cannot tell on the combined rows. The same 9 label-split pairs appear. The six rows that differ from my first-pass expectation all follow from Addendum 6 as written (details under item 4).

Rerunning my first-pass `db_side.py` gives 39 differences. They are exactly the ads split on the three Google services' main rows plus the X alias (+1,469 on X July–December 2025), which my new reduction confirms. The automation-fields data (52 rows, now split into ads and non-ads) matches my recount with 0 differences. `public/dsa.json` (528 rows) carries the same numbers as data/dsa.json. It differs only in 107 reason strings where the unsized-difference sentences are shortened to a pointer to the legend, which holds the full text.

## 1. YouTube, Google Maps and Google Play, main and ads rows

All values and outcomes reproduce. The main rows now count only statements not flagged as ads:
- **YouTube:** all measures BELOW in both halves, 0.089 [0.089, 0.106] and 0.081 [0.081, 0.094]. Own initiative on terms and conditions BELOW, 0.084 and 0.077. Solely BELOW, not automated CANNOT TELL.
- **Google Maps July–December 2025:** all measures CONSISTENT, 1.024 [1.024, 1.062]. Solely and own initiative on terms and conditions are CONSISTENT too.
- **Google Maps January–June 2026:** all measures ABOVE, 1.708 [1.704, 1.752].
- **Google Play:** not automated ABOVE in both halves. Its lower edges (1.485 and 1.119) clear 1.10 by more than 100 statements. Other Play rows CANNOT TELL.

Ads rows: YouTube ads all measures and own initiative on terms and conditions read CONSISTENT in both halves. Its share rows are CONSISTENT too. Every other ads row reads CANNOT TELL, from the column-sum bounds (item 4).

Notes:
- Notice rows for these three services use non-ads statements as "every statement the platform filed". Sheet 4 has no ads version, so notices about ads may be inside it, and all statements would be the safer upper edge. No outcome moves, because no notice row for these services can read below.
- The full short-day shortfall goes on both the main and the ads row of a service. That is conservative on each.

## 2. Facebook, Instagram and the combined rows

All values reproduce, and every row reads CANNOT TELL.
- Per-service rows of all measures, solely, not automated, own initiative, own initiative on terms and conditions, own solely automated and share are CANNOT TELL under 6.3 (Meta's combined-services note, both directions). Where a row was already CANNOT TELL from the wider bands, the note had nothing to change.
- Own illegal is CANNOT TELL under 6.6. Notices are CANNOT TELL under 6.2.
- Combined rows: the column-sum lower edge is the larger of the two services' largest columns, which leaves every combined band wide: upper edges run from 1.18 to 3.37, and there is no upper edge at all on not automated.

Two notes:
- The combined lower edge subtracts both services' spam rows from that one largest column. That is conservative and changes no reading.
- The page line "their own rows read cannot tell and the combined row reads both together" should say that the combined row also reads cannot tell, and why.

## 3. Notice rows

There are 96 notice rows: 89 CANNOT TELL, 6 NOTHING RETURNED, and 1 BELOW. Every notice row with a stated figure has D_lo 0, and its stated upper edge is the larger of the actions and the report's notified items (column H, or column I for trusted flagger rows).

The one BELOW is X July–December 2025. Even all of X's statements (220,067 with the allowances) fall below 0.9 × 388,095, clearing the edge by 129,219 statements. Addendum 6.2 is implemented as written, and the reason text on every notice row says so.

## 4. Addendum 6.5

**Committed before effects: confirmed as far as git can show.** The 6.5 text is verbatim in commit 7cbdf70 (22:31:09). Code and outputs come later (dsa_tick.py at 22:51, build commit 22:54). The Amazon effect was already known from my first pass, where I named it as the judgment call.

**Applied evenly: yes.** My implementation applies the identity test to every main, ads and combined report and moves the same rows:
- **Identity holds** for Facebook, Instagram, the combined rows, YouTube main (sheets 5 and 6 plus notices), LinkedIn, Amazon January–June 2026 (plus notices, 0.0064%), Zalando, Apple, Google Maps, Google Play, Google Shopping, WhatsApp and all six Ads templates. The Ads templates match exactly.
- **No match:** every other report. Closest misses are Pinterest January–June 2026 at 0.98%, Shein at 0.32% to 0.82% and Amazon July–December 2025 at 166%.
- **Tolerance:** no report sits near the 0.1% edge in a way that matters. Facebook's "plus notices" variant is at exactly 0.1000%, but its "sheets 5 and 6" identity is exact.

**Rows moved.** Before platform notes and 6.7 there are 27. Three Instagram rows are cannot tell anyway under 6.3, which leaves the builder's 24:
- Amazon January–June 2026 all measures and not automated (BELOW).
- YouTube July–December 2025 share (BELOW).
- Apple July–December 2025 share (ABOVE).
- The combined July–December 2025 all-measures row (CONSISTENT).
- 19 ads rows (18 CONSISTENT, plus Google Play ads July–December 2025 not automated, BELOW).

**Sound: yes, as a conservative bound.** It extends 6.4's premise (a TOTAL equal to its column sum may count one decision in several columns) to a sheet 8 total that is built from those TOTALs. It only lowers the stated lower edge, or widens the stated share, so it can remove a reading but never create one. Its cost is real. The ads database counts match the Ads TOTALs to within 0% to 2%, which shows no sign of double counting. Yet the rule turns 18 ads agreements into cannot tell. That follows from the rule as committed and is applied to every report alike.

Implementation notes (no outcome moves):
- The identity test takes the first candidate within 0.1%, not the closest. For LinkedIn, Google Play and Google Shopping, "sheets 5 and 6" is chosen although "plus notice actions" is exact. That lowers 16 lower edges by the notice actions (484 to 2,730 statements). With the closest identity, no outcome changes. Align the code or the PLAN text ("plus its notice actions").
- The inherited edge subtracts order items and spam rows again, even where the identity did not include orders. Conservative.

**The other five differences from my expectation follow the committed order of rules:**
- Snapchat January–June 2026 own initiative on terms and conditions stays BELOW. Its partner's ABOVE rested on one statement and is floored under 6.8 before 6.7 runs, as 6.7 says.
- XVideos July–December 2025 own illegal stays ABOVE. 6.6's source allowance made its partner CANNOT TELL first.

Both are as written. Note that XVideos own illegal ABOVE (31,016 against 5,196) sits beside own and own on terms and conditions reading cannot tell. It is still label-dependent in substance.

**Disclosure. Severity: fix before ship.**
- On the four main rows 6.5 moves, the page shows "defined after the data, plan rule reads ...". Good.
- On the ads and combined rows the cell says only "row defined after the data", and the reason text does not name 6.4 or 6.5. A reader cannot see that YouTube ads solely, every Google Maps and Google Play ads row, and the combined July–December 2025 total read cannot tell because of the column-sum bound, and would read consistent without it.
- Fix: on those rows, add the restriction-column label and the reading without the bound, the same way main rows show the plan rule.

## 5. The page against the data

527 numbers in the six tables, regenerated from data/dsa.json and automation_period.json: 0 differences.
- Every comparison row (except NOTHING RETURNED and blank shares) appears on the page, and all 9 label-split rows match the data.
- No printed band edge sits on 0.90 or 1.10. Five significant figures print near an edge, for example 1.0974 and 1.0991.
- Visible copy has no semicolons. The read date is in HST. The plan-as-committed sentence, the unsized differences for above and below, "within 0.05%" and the floor of 100 statements are all on the page.

Fix before ship:
1. "Stated zero: consistent if the database holds none, above if it holds some across the whole band" no longer matches the rules. Snapchat January–June 2026 own illegal holds 1 statement against a stated zero and reads cannot tell under 6.8. It should say "at least 100".
2. The ads and combined disclosure from item 4.

Notes:
- PLAN 6.10 says four significant figures near an edge. The page prints five, rightly, so 1.0997 does not print as 1.100. Correct the plan text.
- 19 reason strings in data/dsa.json and public/dsa.json join rule texts with "; ". Join them with ". " instead.
- The below reason could also name deceptive high-volume commercial content that a report does not label as spam (Article 17(2)). The bands size spam only where a report labels it.

## Verdict, second pass

**FIX THEN SHIP.** The first-pass fixes are in and correct. Every number and outcome in scope reproduces independently, and Addendum 6.5 is sound and evenly applied. Three copy changes remain, and none of them changes a number or an outcome:
- the stated-zero sentence,
- the reading without the column-sum bound on ads and combined rows,
- the combined-row line in the Meta note.

Once those are made, it can ship without another referee pass.
