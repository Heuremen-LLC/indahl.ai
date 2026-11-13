# Newsletter edition 1 audit: OY, SOCIAL and method facts (10 Nov 2026)

Read-only. Nothing was edited. Recount scripts and fetched copies are in /private/tmp/claude-501/-Users-heuremen/ba08385b-5844-4963-b441-21052a55d90b/scratchpad/nl_audit/oy_social/ (oy_recount.py, social_recount.py, unmatched_recount.py, ledger_count.py, mit_recount.py, s1_check.py). Live pages fetched about 14:15 UTC on 10 Nov. The ledger was read at 2,789 rows (file modified 14:03 UTC).

## Serious findings first

1. **The OY zero depends on a rule set after the first 41 rows were read.** PLAN_OY_INDEX.md Addendum 2 (25 Oct, about 10:10, before any row) defines MEASURED as an outcome of the school's own "AI policy, guidance, tools or pilots", with learning and grades listed as outcomes. The split into MEASURED-POLICY and MEASURED-PILOT came in commit ecb90f3 at 11:35, after about 41 rows. CMU went in as a MEASURED-POLICY candidate and moved out after the referee. Under the rule written before the read, 6 to 8 of 148 rows measured a learning or grade outcome of their own tool or pilot: Harvard, UMD, MSU, Pitt, JHU, Georgia Tech and Pomona, plus CMU if AI competency counts. The page does not label the policy-level rule as set after the data. The page's own table also lists 10 pilots with results read, so the zero is honest only with the word "policy" kept in.
2. **The rule is not applied evenly between tools.** UNM and Temple tested a licensed Turnitin detector and count as "institution-wide tool", so they are MEASURED-POLICY. The UMD trial tested a study assistant that the university's Division of IT provides, randomized across 30 instructors, with final grades as the outcome. It is filed as a pilot. If it were filed like UNM and Temple, the learning-outcome count would be 1, not 0.
3. **Some "None found" rows mean the site was not reached.** Williams: every live williams.edu host returns a 403 challenge, the committee's Final Report returns 403 and is not archived, and the row was read from the Wayback Machine. Haverford: every www page returns 403. Both show "None found, 25 Oct 2026" on the page. I confirmed both 403s again today. Mississippi State: 18 of 44 provost pages were blocked. Wellesley's teaching-centre and provost pages are behind a login. The desk's own RETRIEVAL_BARRIERS.md says an unread page "is never folded into nothing found". These rows break that rule.
4. **"145 of 148 have a public AI policy or guidance" is not on the page, has no ledger row, and overstates the column.** My recount of the live column gives 146 Found (145 plus Miami's archived copy), 1 None found (our row) and 1 Not looked for yet (St. John Fisher). The cell is set by the first URL in each row's S1 notes, not by a judgement that the document is a policy. Wellesley shows Found, but its own row says "No public AI policy, task-force report, syllabus-statement page or teaching-centre guidance found". The linked page is a programme hub, which I fetched to confirm. Other first links are a news pointer (Clemson), an IT survey story (Buffalo), a workshop listing (Vassar), an events archive (Colgate) and a strategic-plan update (Davidson). LSU and NC State have guidance but state they have no official university policy. Do not print this number.
5. **"45 of 45" hides the outside seat's own outcome.** /seat/live.json (10 Nov 13:51) shows 46 of 46 pages matching and 42 of 43 feeds fresh at the last probe. Over the rolling 24 probes there were 4 incidents, and the seat's committed rule reads that as **ABOVE**. No ledger row exists for the seat counts.
6. **Most of the $1.37B is out of scope by design.** Of $1,374,938,400 unmatched, $984.6M sits with advertisers that list only a tax ID and $342.1M with state registrations. Those are mostly state, local or non-federal advertisers that would not be expected to have an FEC committee. Only $46.3M (1,250 advertisers) lists no ID. Printed bare, "spend matching no FEC committee" reads as a reporting gap. It has no ledger row.
7. **UMD wording.** The 3,387 figure is from the OSF plan, which the paper says was registered "after completion of data collection but before analyses began". Do not call the 3,387 "pre-registered students". The −0.37 SD is the exact-match sample. The full sample showed "not significant evidence of adverse treatment effects" (paper's words), and the page prints both.

## One row per number

| # | Number | My recount | Ledger | Live page | Outcome | Note |
|---|---|---|---|---|---|---|
| O1 | 0 of 148 measured a learning outcome of own AI policy | 0 at policy level. 6 to 8 under the rule written before the read | oy.learning_outcome_zero = 0, live | "0 of 148 … As of 25 October 2026" (hard-coded string in build_matrix_page.py, not computed) | MATCH, STALE (as of 25 Oct) | Findings 1 to 3. Gate depends on the effect |
| O2 | 148 rows | 148 (live list table) | oy.rows_148 = 148 | 148, one of them ours | MATCH | Our own row is counted in every denominator |
| O3 | 74 usage or attitude only | 74 | oy.usage_only = 74 | 74 of 148 | MATCH | 7 of the 74 ran pilots with outcomes (Harvard, CMU, UNC, UMD, MSU, Berkeley, Princeton held). "Usage surveys only" misdescribes them |
| O4 | 47 plan to measure | 47 | oy.planned_only = 47 | 47 of 148 | MATCH | Georgia Tech, Pitt and Pomona are in this bin and did measure pilots. "Only plan to measure" is wrong for them |
| O5 | (breakdown) 3 measured policy or tool, 3 without counts, 21 none found | 3, 3, 21 | oy.measured_policy 3, oy.trial_wo_numbers 3, oy.none_found 21 | same | MATCH | 3+3+47+74+21 = 148. The sweep's "21 had none found" omits the 3 without counts |
| O6 | 8 of 148 cite a chatbot as a source | 8 rows in the table | oy.chatbot_cited_8 = 8 (surface listed only as media_old, not oy_matrix) | 8 of 148 | MATCH | Quotes verified live: Mississippi State (p.15), Montana State, UNLV, UIC and Wesleyan (end of the quote truncated by the fetch tool). Tulane, WashU and WVU were not fetched |
| O7 | 0 of 114 released microdata | 0 (114 rows read for S3) | oy.data_microdata_0 = 0 | 0 of 114 (hard-coded string) | MATCH, STALE | |
| O8 | 76 of 114 released nothing | 76 Nothing, 38 summary only, 34 Not read | oy.data_none_76 = 76 | 76 of 114 | MATCH | |
| O9 | 145 of 148 public AI policy or guidance | 146 Found | none | not printed | MISMATCH, NO_LEDGER_ROW | Finding 4 |
| O10 | MIT names no evidence for 20 of 33 recommendations | 20 of 33 "None stated" in mit_c001/CLAIMS.md | oy.mit = 20 of 33 | same | MATCH | Recounted from the desk's extract, not from the report PDF. The 33 imperatives were picked by hand. Evidence counts as named only when cited in the same subsection |
| O11 | UMD −0.37 SD, 2,379 of 3,387 | Paper abstract: 2,379 students, 30 instructors, −0.37 SD final grade (fetched). 3,387 is in the OSF plan per rows/umd.md, not in the paper | oy.umd = −0.32 to −0.37 | "−0.37 SD in the exact-match sample", "3,387 consenting" | MATCH (numbers), wording fix | Finding 7 |
| S1 | 31 of 6,160 | 31 (21 above, 9 below, 1 consistent). Rule: decided, same outcome on second band and with unseen money in full, ID match, no flags | social.adspend.decided.robust = 31 | 31 of 6,160 | MATCH | Without the flag filter it is 38. Without the unseen-money filter it is 41. The rows are committee-cycles (3,347 committees) |
| S2 | 80 decided | 80 (28 above, 26 below, 26 consistent) | social.adspend.decided = 80 | 80 | MATCH | |
| S3 | 6,056 cannot tell | 6,056 (+24 nothing returned) | social.adspend.cannot_tell = 6,056 | 6,056 | MATCH | Top reasons: band 2,322, agency 2,245, purpose 911 |
| S4 | $1.37B Google spend matching no FEC committee | Summary bins sum to exactly $1,374,938,400 over 13,888 advertisers. My naive recount from the Google CSV gives 14,204 and $1,457M, because the matched advertisers without a scored row are not in adspend.json | none | "$1,374,938,400" | CANNOT_RECOUNT (fully), NO_LEDGER_ROW | Finding 6 |
| M1 | Ledger 2,772 rows (2,730 live, 38 withdrawn) | 2,789 rows: 2,747 live, 38 withdrawn, 2 cannot_tell, 2 held. The sweep's split summed to 2,768, missing these 4 | n/a | not public (no page, /ledger 404, not in the repo) | STALE | It grew by 17 rows after the sweep. Readers cannot check it |
| M2 | Outside seat 45 of 45 | 46 of 46 pages, 42 of 43 feeds, chain 135 of 135. Rolling 24-probe outcome ABOVE (4 incidents) | none | numbers load by script from /seat/live.json | STALE, NO_LEDGER_ROW | Finding 5 |
| M3 | QIA 289 of 1,043 readout calls withdrew | 1,043 − 754 = 289, 27.7% (prints 28 %) | qia.cal.reread_calls = 1043 → 754 | same | MATCH | Arithmetic and ledger only. Not recounted from the raw runs |
| M4 | 24 runs re-read | 24 (4 at 4,096 and 20 at 1,024) | same row | same | MATCH | |

## OY hand-check of rows against sources (17 fetched)

- **Matched:** Mississippi State, Montana State, UNLV, UIC and Wesleyan (chatbot quotes). UNM audit: 84 human texts with 3 flagged, 63 AI texts with 42 missed. Temple: I fetched the PDF myself. It says 28 of 30, "77 of them" of 90 above 1% AI, and 13 of 30. A helper first misread this, and the corrected reading is a match. Auburn ("there has not been an attempt to assess"). Virginia Tech ("did not track pre/post performance benchmarks", C.6.2). Caltech guidance (22 Oct 2023). NC State meeting page (no measured outcome). UMD abstract.
- **Not reached today:** Columbia SOLER (403, so "without counts" is unchecked), Williams (403 on both), Haverford (403 or no answer) and Texas A&M's report. The A&M report answers 404 to non-browser readers. CAMPUS notes it opens in a browser.
- **Not verified:** NC State's "As of May, 2026, there is no official university policy" was not found on provost.ncsu.edu. The row says the DELTA page.
- **Label problem:** Wellesley is Found under policy or guidance, but the page is a programme hub.

## Staleness

OY is one pass from 25 Oct, 16 days old. CAMPUS (pass 43, 10 Nov 09:44) reports 270 of 307 cited sources open, 26 blocked, 5 changed text and 3 gone since the previous pass. Spot searches on the 10 largest listed schools (ASU, UCF, Texas A&M, Ohio State, Florida, Rutgers, Michigan State, Penn State, UT Austin, USF) plus UMD found no institution-level measured learning outcome published after 25 Oct. Florida's 2024 to 2029 QEP has learning outcomes with no results published. Ohio State's AI Fluency pages report rollout only. UMD's trial (before 25 Oct) remains the one item a careful reader would raise.

## /tp desk audit

- **Gate depends on the effect? OY: yes.** The policy-versus-pilot gate turns 6 to 8 into 0, and it was set after rows were read. SOCIAL: in part. The robust filter keeps 31 of 80, and the itemization rule was set after the data. The page discloses this.
- **Net hiding flips? OY:** "0 measured" sits beside a UMD trial that found lower grades. **SEAT:** 46 of 46 at one probe hides the ABOVE rolling outcome. **SOCIAL:** "31 of 6,160" says nothing about direction, and 21 of the 31 read above. **UMD:** −0.37 is the matched sample, and the full sample was not significant.
- **Caveat matches data? OY:** the method box says "none found" means not found in those places. It does not say that some rows' sites returned 403 throughout. **$1.37B:** no caveat that most of it is out of FEC scope.
- **Hard-coded:** both OY zeros are literal strings in build_matrix_page.py, not counted from rows. They will not change if a row changes.

## Suggested newsletter wording

- **Lead (OY):** As of 25 October 2026, none of the 148 colleges and universities on our list had published a measured learning outcome of its own AI policy. Ten had run or funded pilots of AI tools and published results. In one, a University of Maryland randomized trial of its own study assistant, final grades were 0.37 standard deviations lower in the matched sample. We chose the institutions ourselves and read each one once, on 25 October. Two of the sites refused our reader, so for them none found means not reached.
- **Breakdown:** Three measured their own policy or tool, two by testing an AI detector and one by tracking its syllabus policy. Seventy-four had surveys of use or attitudes and no measure of their policy. Forty-seven said they plan to measure.
- **Chatbot:** Eight of the 148 cite a chatbot as a source in their own AI documents.
- **Data:** Of the 114 we read for data, none released the underlying responses of its own AI survey or evaluation. Seventy-six released nothing.
- **Policy count:** do not print 145 of 148.
- **MIT:** The MIT committee report names no evidence for 20 of its 33 recommendations, counting evidence only when the report cites it in the same subsection.
- **UMD:** The trial analysed 2,379 students. Its analysis plan, filed after data collection and before analysis, listed 3,387 consenting students.
- **SOCIAL:** We set Google's stated election ad spend beside FEC filings for 6,160 committee-cycles. In 6,056 the two records cannot tell us whether they agree. In 31 the result holds under every check, and in 21 of those Google states more than the filings show paid to Google.
- **$1.37B:** Google lists $1.37 billion of election ad spend under advertisers that match no FEC committee. Almost all of them list a tax ID or a state registration, which usually marks state or local campaigns outside FEC filing.
- **Ledger:** Every public number has a row in one ledger, 2,789 rows on 10 November, 38 of them withdrawn with their history. (Count it again on print day.)
- **Seat:** An outside runner compares our pages with the public repository. On 10 November all 46 pages matched at the last probe. Over its last 24 probes it logged 4 incidents, which its own rule reads as above.
- **QIA:** QIA re-read 24 calibration runs and printed that 289 of 1,043 readout calls withdrew.
