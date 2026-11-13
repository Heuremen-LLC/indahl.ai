# The Wall (OY) - schools as rows (internal name; outgoing: "Recount Matrix: Learning Research"). No score, no rank: columns only.
Columns per PLAN_OY_INDEX.md addenda 1-2: S0 self-evaluation | S1 document | S2 evidence cited | S3 data released | S4 recs naming evidence | S5 claims priced |
S6 detector stance | S7 own-faculty studies recounted. Search procedure logged per row.

## Row 0 - Heuremen / OY [IN DEVELOPMENT per Wayfinder 25 Oct; re-read at ship] (indahl.ai/oy, source ~/bones-forge/indahl-ai/oy.html + oy/*.html, read 25 Oct by Bones)
- Search: every OY page source read in full (15 pages + index). Live site not re-fetched (local source = deploy source; verify at ship).
- S0: NONE FOUND (no measurement of whether OY's own pages teach anything; nothing to evaluate yet - in development).
- S1: no AI-in-learning policy or guidance document. "none found".
- S2: science claims cite our paper (heuremen.org) and its data DOI; no learning-outcome evidence cited anywhere.
- S3: n/a (no learning study run).
- S4: n/a (no recommendations about AI in learning; the Workshop page gives advice: "Bring the weird idea. Ask, don't order...").
- S5: (a) oy.html "about 2 degrees of turn per look, on four different chips" - ledger-backed (paper), CONSISTENT with the record.
      (b) workshop.html "each app came out better than either would have made alone" - NO TESTABLE CLAIM (no number, no comparison run).
      (c) workshop.html "In June a human and an AI built 23 little apps together" - count UNCHECKED: recount from the Hugging Face record.
      (d) tokens.html "the first time we trained YO, it learned to use just one of them: I" - record check pending (YO training logs).
- S6: no detector stance stated.
- S7: none.
Open items for row 0: recount (c) and (d) from the record; decide with Wayfinder whether (b) stays as worded (it is ours to fix first).

## Row - Cornell University (sweep: SWEEP_ivies.md + cornell_surveys/)
- S0: USAGE-OR-ATTITUDE ONLY (Spring 2025 surveys: self-reported agreement; no measured outcome found).
- S1: survey results page + instruments (May 2025 survey; files Sep 2025 / Feb 2026). Other documents: see SWEEP_ivies.md (2 A, 1 B).
- S3: PARTIAL - group-level counts released as CSV, both instruments; no microdata.
- S5 (priced so far): printed student item n (2,029) exceeds stated respondents (1,988); student group labels sum to 2,539 on an unidentified base -> CANNOT_TELL (overlap explanation withdrawn after referee).
- S7: Kizilcec et al., Science 2026 (UNREAD; data/funding unchecked).

## Row - University of Southern California (L-2, usc_l2/CLAIMS.md)
- S0: NONE FOUND. S1: CET resource page "When AI Helps or Hurts Learning: An Educational Psychology Perspective" (Seli, Fall 2025):
  one descriptive sentence; the framework itself is not on the page (embed UNCLEAR). S2: none cited. S4: n/a. S5: 2 uncited phrases.
  Related page https://cet.usc.edu/ai-teaching-at-usc-tools-guidance-and-faculty-examples/ UNREAD.

## Row - Harvard University (partial: harvard_kestin/)
- S7: Kestin et al. 2025 RECOUNTED: within-student post +0.65 [+0.40,+0.91] ABOVE; release has 122 of 194 "eligible" with both lessons;
  "M" = median; "motivation" = field feel_difficult; t-tests printed as dependent rebuild as independent.
- S0-S6: pending (Harvard institutional documents in SWEEP_ivies.md).

## Agent rows (rows/<slug>.md), hand-checked by Bones (random receipts opened against the live source; check_receipts.py + by hand)
| school | receipts checked | result | notes |
|---|---|---|---|
| brown | 4 | 4 PASS | GAITL report gives n = 697 (p.31) and 693 (p.8) for the same feedback form |
| yale | 4 | 3 PASS, 1 checker artifact (not a quote) | |
| penn | 2 | 2 PASS (PNAS funding verified in Europe PMC full text) | Melumad & Yun PNAS Nexus prints n = 10,462 (abstract) and 10,426 (intro) |
| caltech | 2 | 2 PASS | |
| mit | by hand (C-001) | - | |
| harvard | 2 | 2 PASS (math.harvard.edu 403 live; Wayback 2026-04-12 PASS) | Math survey n not stated; CS50 papers thank "Ed, GitHub, Microsoft, and OpenAI" |
| princeton | 3 | 1 PASS (title change documented in row), 2 UNVERIFIED (site 403 to us; odoc page) | |
| columbia | 2 | 2 PASS | SOLER program page UNREAD (403) - possible S0 MEASURED |
| dartmouth | 2 | 2 PASS (checker URL pairing artifact on the first; quote verified on its own page) | |
| stanford | 2 | 2 PASS | |
| uchicago | 2 | 2 PASS | detector study funded by a Google Cloud program -> company card (row flag) |
| jhu | 0 | NOT CHECKED (row has no URL+quote pairs on one line; all jhu.edu live pages 403, read via Wayback) | re-read live before ship |
| northwestern | 2 | 2 PASS | |
| duke | 2 | 1 PASS, 1 checker artifact (quote is Duke's sentence citing a Stanford study; checker took the Stanford URL) | |
| vanderbilt | 1 | 1 UNVERIFIED (quote is from the paper, URL is its Zenodo record) | faculty study NSF-funded -> card |
| rice | 2 | 2 PASS (provost page 406 live; Wayback 2026-07-06 PASS) | |
| wustl | 2 | 2 PASS | |
| baylor | 2 | 1 PASS, 1 PASS by hand (T&F abstract via OpenAlex; publisher blocks curl) | |
| ttu | 2 | 2 PASS | |
| unt | 2 | 1 PASS, 1 PASS by hand (title via Crossref) | |
| msstate | 2 | 2 PASS | |
| utd | 2 | 2 PASS | |
| uta | 2 | 1 PASS, 1 checker artifact (a filename in parentheses, login-only SharePoint) | |
| uh | 2 | 2 PASS by hand (ACM funder lines NSF + Research Council of Finland via Crossref) | faculty study NSF-funded -> card |
| okstate | 2 | 2 PASS by hand (ITLE PDF via r.jina.ai, okstate blocks curl; Frontiers data statement via r.jina.ai, checker split a line-wrapped quote) | |
| usu | 2 | 2 PASS | |
| kstate | 2 | 1 PASS, 1 checker artifact (quote is the eID sign-in wall, i.e. the row recording a locked page) | |
| wsu | 2 | 2 PASS | |
| montanastate | 2 | 2 PASS | |
| unh | 2 | 1 PASS, 1 checker artifact (URL captured as quote) | |
| udel | 2 | 1 PASS by hand (Gates Foundation INV-006167 via Crossref; private foundation, not gov), 1 FAIL->fixed (title read in a browser 25 Oct: page says "Generative Artificial Intelligence", row had shortened it to "Generative AI"; corrected to verbatim) | |
| uri | 2 | 2 PASS | |
| uvm | 2 | 1 PASS, 1 checker artifact (quote contains "..." ellipses; handle page fetched) - recheck the joined fragments before ship | |
| northeastern | 2 | 2 PASS by hand (r.jina.ai; checker fetch failed) | Senate survey addenda added by Bones (698 / base 690; two dates printed) |
| case | 2 | 2 PASS | syllabus-statement survey PDF read by hand (8 submissions) |
| rochester | 2 | 2 PASS | |
| tulane | 2 | 2 PASS | |
| brandeis | 2 | 2 PASS in a browser (site returns 403 to scripts) | |
| syracuse | 2 | 2 PASS | |
| rpi | 2 | 1 PASS, 1 checker artifact (Box link with the URL captured as quote) | |
| wfu | 2 | 2 PASS | |
| williams | 2 | 1 PASS by hand (DOI affiliation via Crossref), 1 UNVERIFIED live: the Zoom AI Companion pilot announcement now redirects to the OIT home page (agent read an archived copy; all williams.edu pages 403 to scripts) | live re-read owed for every williams quote |
| amherst | 2 | 1 PASS (r.jina.ai), 1 UNVERIFIED: /mm/728779 redirects to a password-required page titled "Emerging Examples from Amherst College"; quoted wording "...from the Amherst College Classroom" not confirmable | |
| swarthmore | 2 | 2 PASS (Zotero group title via r.jina.ai) | |
| pomona | 2 | 1 PASS, 1 checker artifact (Box link title, sign-in) | |
| wellesley | 2 | 2 PASS | |
| bowdoin | 2 | 2 PASS | |
| carleton | 2 | 2 PASS (one in a browser) | |
| middlebury | 2 | 2 PASS | |
| uic | 2 | 2 PASS | |
| drexel | 2 | 2 PASS | |
| gwu | 2 | 1 PASS, 1 recheck owed (library page) | SR 24/8 table verified by hand: 476.2% vs table 472.6%; 84.64% vs 81.64%; no AI category in the table |
| binghamton | 2 | 1 PASS, 1 FAIL-unread (catalog page returns HTTP 202 empty, as the row says) | |
| albany | 2 | 2 PASS | |
| howard | 2 | 2 PASS | |
| fordham | 3 (looser checker) | 1 PASS by hand (r.jina.ai: "the evaluation phase takes place in pilot courses"), 2 UNVERIFIED (Blackboard login, Google Doc) | |
| american | 3 (looser checker) | 0 verified, 3 unresolved: two quotes come from a podcast and a handout (not the pages the checker paired them with) and one is a PDF title; hand re-read of the true sources owed | |
| oberlin | 2 | 2 PASS | |
| macalester | 2 + 3 (looser checker) | 2 PASS, 1 UNVERIFIED (Google Drive file behind sign-in) | |
| kenyon | 3 (looser checker) | 1 PASS, 2 UNVERIFIED (Google Drive files behind sign-in) | |
| bates | 2 | 2 PASS | |
| colgate | 2 | 2 PASS | |
| smith | 2 | 2 PASS | |
| barnard | 2 | 2 PASS | |
| hmc | 2 + 3 (looser checker) | 1 PASS; quotes from the pilot policy Google Doc are UNVERIFIED (sign-in) | |
| haverford | 2 | 2 PASS | |
| davidson | 2 | 2 PASS | |
| grinnell | 2 | 2 PASS | |
| hamilton | 2 | 1 PASS, 1 checker artifact (agent note captured as quote) | |
| colby | 2 | 1 PASS, 1 checker artifact (Drive file title, sign-in) | |
| vassar | 2 | 2 PASS | |
| wesleyan | 2 | 2 PASS (+ "According to Claude" verified live by hand) | |
| cmc | 3 (looser checker) | 3 PASS | |
| smu | 2 | 2 PASS | |
Checker note: check_receipts.py pairs each quote with the FIRST URL on its line, so mixed-source lines produce false FAILs; every FAIL above
was opened by hand. Sites that refuse our fetches (403/406) are checked through Wayback snapshots and marked as such.
| cmu | 3 (by hand, live page) | 3 PASS | S0 MEASURED: own GenAI modules, course-level RCT Fall 2024, 1,368 students / 53 courses (610 control, 758 treatment); outcome = AI competency, not subject learning; 2nd study n = 424 (Copilot vs peer feedback) |
| notre-dame | 2 | 2 PASS | S7 search INCOMPLETE (web-search cap) |
| emory | 2 | 2 PASS | search INCOMPLETE after Garg lead |
| georgetown | 2 | 2 PASS (McMaster PDF via text reader) | search INCOMPLETE |
| nyu | 2 | 2 PASS | Ibrahim et al. 2023 data on GitHub; funding Tamkeen (NYUAD) - card/IN to rule |
| usc (full) | 2 | 2 UNVERIFIED (EdArXiv/OSF DOI renders by script) | search INCOMPLETE |
| tufts | 2 | 2 UNVERIFIED (Box share needs login; ASEE page renders by script) | re-read before ship |
| bu | 2 | 1 PASS, 1 checker artifact | |
Batch 3 note: agents in batches running three-at-once exhausted the session's shared web-search cap; rows marked INCOMPLETE get a re-sweep
pass. Rule from here: at most TWO batches in flight.
| gatech | 2 | 1 PASS, 1 UNVERIFIED (catalog page) | S0 tool-level MEASURED candidate (Socratic Mind; n not on page; paper UNREAD); search pass owed |
| uw-seattle | 2 | 2 PASS | OEA survey n = 2,377, instrument in appendices; search pass owed |
| ucsd | 2 | 1 PASS, 1 UNVERIFIED (ACM DOI) | TritonAI tutor pilot: 68 survey responses, no comparison; search pass owed |
| ucdavis | 2 | 1 PASS, 1 UNVERIFIED (journal DOI) | most hosts 403 to us; 22 UNREAD; search pass owed |
| uci | 2 | 2 PASS | search pass owed |
| ufl | 2 | 1 PASS, 1 UNVERIFIED (Google Drive) | QEP excluded (accreditation) |
| osu | 2 | 2 PASS | |
| psu | 2 | 1 PASS, 1 UNVERIFIED (PDF title line) | |
| berkeley | 2 | 2 PASS | |
| ucla | 2 | 2 PASS | |
| uva | 2 | 2 PASS | provost survey 685 respondents (181 faculty) |
| unc | 2 | 2 PASS | course pilots (CFE/Lenovo grants) |
| uw-madison | 2 | 2 PASS | |
| uiuc | 2 | 1 PASS, 1 UNVERIFIED (protected post title on genai.illinois.edu) | |
| utexas | 2 | 2 PASS | |
| asu | 2 | 2 PASS | |
| rutgers | 2 | 2 PASS | |
| tamu | 2 | 1 PASS (text reader), 1 UNVERIFIED (example page) | |
| ucsb | 2 | 1 PASS (text reader), 1 UNVERIFIED (journal DOI) | |
| uiowa | 2 | 2 PASS (one via text reader) | |
| umd | 2 | 2 PASS | RCT of own VSA tutor, n = 2,379 (S0 pilot, final grade -0.37 SD in matched sample) |
| umn | 2 | 2 UNVERIFIED (handle.net repository + Google Doc render by script) | |
| purdue | 2 | 1 PASS (text reader), 1 FAIL (grants page title not found; page 200, 7 kB) - flag for row agent re-read | Vice Provost guidance: 0 studies cited, 0 of 20 recommendations name evidence; module prints "{citation need}" |
| umich | 2 | 1 PASS (text reader), 1 checker artifact (URL captured as quote) | "Raw result data was only available to the research team"; S7 Lu et al. 2026 NSF -> card |
| msu | 2 | 2 PASS | Khanmigo pilot n = 87, p = 0.12 printed as "very small positive impact" |
| oregonstate | 2 | 2 PASS | |
| buffalo | 2 | 2 PASS | |
| uoregon | 2 | 1 PASS, 1 checker artifact | |
| stonybrook | 2 | 2 PASS | Senate: "AI tools adopted university-wide should be evaluated" (PLANNED) |
| cu-boulder | 2 | 2 PASS | OIT lists AI pilots (tutors, Turnitin Clarity) - results not located |
| indiana | 2 | 2 PASS | |
| ku | 2 | 2 PASS | |
| mizzou | 2 | 2 PASS | Show-Me AI pilot results not located; search pass owed |
| uconn | 2 | 1 PASS, 1 UNVERIFIED | AI4ALL pilot self-report only |
| unl | 2 | 2 PASS | |
| utah | 2 | 0 PASS, 2 UNVERIFIED (news page + ASEE render) | UGuide pilot 700+ students, "early feedback" only |
| ucsc | 2 | 2 PASS | AI Council survey report UCSC-community only |
| ucr | 2 | 1 PASS, 1 UNVERIFIED (Senate committee page renders by script) | |
| colostate | 2 | 1 PASS (text reader; site 403 to curl), 1 UNVERIFIED | Annual Report prints 552 participations and 512 attendance for the same workshop series |
| pitt | 2 | 1 UNVERIFIED (Wiley DOI), 1 checker artifact (URL as quote; page reachable via reader) | DPT anatomy pilot n = 129, no grade difference |
| jhu (pilot) | 1 (Crossref API) | PASS: 22 students grades 7-10, quasi-experimental; funder 'Johns Hopkins University Digital Education and Learning Technologies Grant' | |
| pitt (pilot) | 2 (live, LRDC page) | 2 PASS: "group of 129 hybrid Doctor of Physical Therapy students"; "Final course grades were not significantly different between cohorts" (paper: AJDE 10.1080/08923647.2026.2669412, Pitt Momentum Fund) | |
| msu (pilot) | 4 (report PDF via hcommons API) | 4 PASS | report names its own non-significance (credited) |
| fsu | 2 | 2 UNVERIFIED (page loads; quoted titles not found in fetched HTML) | |
| gsu | 2 | 2 PASS | Studiosity evaluation stated without n -> TRIAL REPORTED WITHOUT NUMBERS |
| uky | 2 | 1 PASS, 1 UNVERIFIED (title not found) | |
| usf | 2 | 1 PASS, 1 checker artifact | competition: "just 40% of invited competitors utilized the offered training" |
| auburn | 2 | 2 PASS | |
| iastate | 2 | 1 PASS, 1 UNVERIFIED (Box share) | |
| temple | 2 | 2 PASS | |
| ucf | 2 | 2 PASS | |
| lsu | 2 | 2 PASS | |
| ua | 2 | 2 PASS | |
| uga | 2 | 1 PASS (Fall 2026 memo live), 1 UNVERIFIED (CTL page renders by script), 1 SharePoint | Turnitin AI detector approved (S6 outlier list) |
| utk | 2 | 0 PASS, 1 UNVERIFIED (OIT page title), 1 checker artifact | arXiv 2609.38029 faculty study to read |
| vt | 2 | 2 PASS | |
| clemson | 2 | 1 PASS, 1 UNVERIFIED (arXiv DOI line) | |
| ncsu | 2 | 2 PASS | "no official university policy" (May 2026) |
| miami | 2 | 2 PASS | Turnitin AI detection "not included" |
| smu | 2 | 2 PASS | |
| uark | 2 | 1 PASS, 1 UNVERIFIED (ASEE DOI) | |
| unm | 4 (live, by hand) | 4 PASS | detector audit: MEASURED-POLICY (detector accuracy) |
| uta | 2 | 2 PASS | |
| utd | 2 | 1 PASS, 1 checker artifact | |
| wvu | 2 | 2 UNVERIFIED (wvu.edu 403 to us) | |
| olemiss | 2 | 2 UNVERIFIED (event page + Box) | |
| ou | 2 | 1 PASS, 1 UNVERIFIED (PDF) | |
| tcu | 2 | 2 PASS | |
| uh | 2 | 2 UNVERIFIED (Canvas login + ACM) | |
| unlv | 2 | 2 PASS (first read UNVERIFIED: quote was linked to the statement page; found on /ai-technology/best-practices live 25 Oct, URL fixed in row, full sentence kept incl. "however, existing university policies already encompass the use of AI technologies") | |

## Addendum (30 Oct 2026, site pass G-11 and G-15) - Cornell University
The Cornell row has no rows/ file. For the public list on /oy: the institution link is the Spring 2025 survey results page named in S1 above (https://academicinnovation.cornell.edu/gen-ai/generative-ai-impact-on-learning-spring-2025-surveys/), and the Public AI policy or guidance link is the CU Committee Report page listed in SWEEP_ivies.md (2023-07-18, https://teaching.cornell.edu/generative-artificial-intelligence/cu-committee-report-generative-artificial-intelligence-education, HTTP 200 on 30 Oct 2026). Set in oy_index/matrix_page/build_matrix_page.py (SRC_OVERRIDE, S1_OVERRIDE).
