# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 16:30 RANK step one: listing of the current US News top of each education list, every row check in progress, page at /rank under OY
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: step one is a listing, no stated figure is set beside a delivered one yet. The none for step two is in PLAN.md (same quantity, same year, rounding only)
- II: n/a: no comparison made, so no flips to count. Step two counts MATCH, MISMATCH and CANNOT_TELL per figure by reason
- III: n/a: no cells and no sign at step one. Every row reads check in progress
- V: holds: the ruler is US News's own stated method, quoted from each methodology page in raw/*_method_20261110.txt, and the public record named per list in PLAN.md
- VI: holds: four outcomes fixed in PLAN.md before any comparison (MATCH, MISMATCH, CANNOT_TELL by reason, and the recompute CANNOT_TELL when inputs are survey, purchased or modelled)
- R: holds: ranks, names, places, editions and weights read from the US News pages on 2026-11-10 in the owner's signed-in browser, parsed in page and kept in raw/. Ties past row 10 read with Load More (National Universities No. 9 adds University of Chicago, Law No. 9 adds Michigan, Education No. 6 adds UT Austin and Virginia). build_data.py stops if a weight is not in its raw capture
- P1: holds: quotes copied from the captures: "There is no national ranking", "U.S. News uses evaluative tiers instead of traditional ordinal rankings", "Tier 1: Highest-performing (85th-99th percentile)"
- P2: holds: each list names its edition (high schools 2026-2027, colleges 2027, graduate schools 2026) and links its US News list and method page
- P3: holds: list titles, ranks, tie marks and printed figures as US News prints them, including "> 95%" and N/A graduation rates
- P4: holds: no cause named. No characterisation of any school or of US News. The owner's own past school is not a source and no school is singled out
- P5: n/a: no interval at step one
- P6: holds: every row reads check in progress, nothing is said about whether any figure matches
- P7: holds: ledger rows written staged before the site edit, flipped live in the ship step under ledger/site_lock.py, release through ledger/ship.sh
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py 0 hits on rank_body.html, no semicolons, no digits in headings, Heuremen LLC in the shared footer
- P10: holds: the K-8 finding (no national list) and the medicine tiers were read before the plan was sealed and are named in PLAN.md

## 2026-11-10 17:00 RANK step two intake: public-record pulls (high schools, law, colleges, corrections cases) and the first comparison run (high schools, law)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the sealed rule (rule.py self-test 22 of 22 known answers, including a suppressed marker and a share that must round once)
- II: holds: outcomes counted per figure by reason in data/checks.json. High schools 57 match, 0 mismatch, cannot tell 18 (10 not printed by US News or missing in CCD, 4 suppressed by the state, 2 year not stated by the state, 2 binned state figure). Law 44 match, 0 mismatch, 11 cannot tell (first-time bar, no year on the page)
- III: n/a: no cells or signs, per-figure outcomes only
- V: holds: two readings shown side by side where the page gives no year (law first-time bar): the ABA 2024-graduate rate and the 2023-2024 average US News's method names. Display only, labelled after the data, not scored
- VI: holds: four outcomes kept, MISMATCH possible and tested (synthetic rows). No mismatch found in this run
- R: holds: public figures read by the pull agents from state report-card files, NCES CCD (Urban Institute API), ABA required-disclosure compilation files and PDFs, IPEDS, College Scorecard and college CDS files, each with URL, file and row in public/*.json. US News side from raw/ captures of 2026-11-10
- P1: holds: state test and level names as each state publishes them (for example Virginia pass rate, Georgia Proficient plus Distinguished, Texas Approaches and Meets)
- P2: holds: every figure carries its year on both sides in data/checks.json
- P3: holds: US News labels as printed (Graduation Rate, Reading Proficiency, Total Economically Disadvantaged)
- P4: holds: no cause named. A CCD free-lunch count above enrollment (1,199 of 1,183, Masterman 2024-25) is printed as the two counts only
- P5: n/a: no interval
- P6: holds: a match says the printed figure equals the public figure after rounding, nothing more
- P7: holds: ledger rows for step two are added staged before the page edit
- P8: cannot tell: page checked after the next ship
- P9: holds: lint_copy.py runs on the rendered body before the ship
- P10: caught: two parser faults fixed before any figure was published (the TN "**" marker read as a definition difference, and a lunch share rounded twice, 24 of 536 read as 5 percent instead of 4). The first-time bar side readings are after the data and labelled so

## 2026-11-10 17:45 RANK step two ship after the outside referee: high schools 57 match 0 mismatch 18 cannot tell, National Universities 8 match 0 mismatch 69 cannot tell, National Liberal Arts Colleges 6 match 0 mismatch 64 cannot tell, Law schools 44 match 0 mismatch 11 cannot tell
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: referee recount with its own code (rank_index_referee/step2/code/recompute.py) reproduces every high school, college enrollment and law admissions row. Re-pulls from CCD, the ABA backend, CDS files and four corrections pages agree
- II: holds: per-figure tallies printed per list and per school. No mismatch on any checked list. Cannot tell counted by reason in the table
- III: n/a: per-figure outcomes only, no cells
- V: holds: where the US News page prints no year (college figures other than enrollment, law first-time bar) the figure is scored cannot tell and the public reading is shown beside it, labelled after the data
- VI: holds: four outcomes kept. Mismatch was possible on every scored row (rule.py synthetic tests 22 of 22)
- R: holds: law ultimate bar years and averaging now quoted from the US News method page in raw/method_addendum_20261110.txt ("2021 and 2022 graduates", "two-year, nonweighted average"), read in the owner's browser after the referee flagged that the earlier capture lacked them. CCD 2024-25 quote captured in full in the same file
- P1: holds: corrections quotes verbatim (referee re-read Berkeley, UW-Madison, GW, Emory). GW quote shortened to the first 18 words of the sentence
- P2: holds: every figure shows the year on both sides
- P3: holds: labels as US News and each state print them
- P4: holds: no cause named. The words "error" and "because" appear only inside quotes from the schools' own documents (UW-Madison, Berkeley), cleared here
- P5: n/a: no interval
- P6: fixed: referee step two. Law first-time bar note now quotes the method's own indicator wording. Penn display line corrected to no CDS read. Blue Ribbon line says "Page not found" in a browser and refused automated reads (both captured). Emory row dropped (rank not changed, outside the plan's scope). College display lines print "equal after rounding yes or no" rather than agrees or differs
- P7: holds: rank.checks.* rows staged before the page edit, set live in the locked ship command with the refreshed rank.list.* snippets
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py 4 hits, all cleared: two quotes from school documents and "English I" read as a first-person word
- P10: holds: the college Common Data Set lines and the law first-time bar side readings are after the data and say so

## 2026-11-10 18:40 RANK New Jersey: New Jersey high schools 70 match 1 mismatch 9 cannot tell, New Jersey elementary and middle schools 0 match 0 mismatch 48 cannot tell, New Jersey colleges 4 match 1 mismatch 79 cannot tell, rank claims 12 match 0 mismatch 27 cannot tell
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the sealed rule (rule.py 22 of 22). Every New Jersey figure is read from its file with sheet and row (public/nj/nj_public.json, NJSLA results files, SPR database files, CCD via the Urban Institute API, college CDS files)
- II: holds: per-figure readings counted per list and per school. High school mismatch: Dr. Ronald E McNair High School mathematics, 80 percent printed, 83.2 in the state test files (GEO01 80.2 of 151, ALG01 94.9 of 39). College mismatch: Stevens enrollment, 4,185 printed, 4,206 in CDS 2025-26 B1
- III: n/a: per-figure outcomes only
- V: holds: two rulers side by side for test results: the state's NJSLA test files (scored) and SPR's school-wide figure (shown in each note)
- VI: holds: four outcomes kept, mismatch found and printed on both lists where it occurred
- R: holds: US News side from raw/nj_*_20261110.txt (read in the owner's browser). Addendum 1 sealed at 1eb8b7f before any New Jersey comparison
- P1: holds: rank claims quoted verbatim from saved copies (the pull agent's verify.py checks every quote against its saved page)
- P2: holds: every figure shows its year on both sides. Elementary and middle proficiency and the economically disadvantaged profile figure carry no year from US News and are scored cannot tell, with both state years shown
- P3: holds: state labels as printed (met or exceeded expectations, participation rate, "Fewer then 10 students registered for DLM" spelled as printed)
- P4: holds: participation shown as counts and rates only. No reason given for any student not tested. Not-tested counts are suppressed by the state for all 26 schools and said so
- P5: n/a: no interval
- P6: holds: the claims section says match only when rank, list and edition all equal the list read
- P7: holds: rank.list.nj_* and rank.checks.nj_* rows staged before the page edit
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py 4 hits, all cleared earlier (quotes from school documents and "English I")
- P10: caught: after the first run, high school proficiency was scored against SPR's school-wide figures and gave 6 math and 4 science differences. US News names state assessment data as its source, which New Jersey publishes as the NJSLA test files. Scored against the test files (science to one decimal, math weighted by valid scores), the readings are those above. Both figures are printed in every note and this choice is labelled here as made after the first run. Elementary and middle figures equal the 2023-24 test files in 21 of 32, shown after the data and not scored

## 2026-11-10 19:10 RANK New Jersey ship after the outside referee: New Jersey high schools 70 match 0 mismatch 10 cannot tell, New Jersey elementary and middle schools 0 match 0 mismatch 48 cannot tell, New Jersey colleges 4 match 1 mismatch 79 cannot tell
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: referee recount with its own xlsx reader (rank_index_referee/nj/code) reproduces every New Jersey figure. Re-pulls of 34 NJSLA files and the SPR database are byte-identical to the desk's copies. CCD re-pulled for all 26 schools
- II: holds: tallies above. The one remaining mismatch is Stevens undergraduate enrollment, 4,185 printed (fall 2025, captured on the NJ page) against 4,206 in its Common Data Set 2025-26 item B1
- III: n/a: per-figure outcomes only
- V: holds: per-test files scored, SPR report figures printed beside them, and for mathematics the reading without Algebra I is printed too
- VI: holds: four outcomes kept
- R: holds: NJ college enrollment year "(fall 2025)" captured from the NJ page after the referee (raw/nj_colleges_20261110.txt). Peer assessment wording captured (raw/method_addendum_20261110.txt)
- P1: fixed: referee D5. Claim quotes normalised to the rendered text (spacing before punctuation removed), the High Technology and Biotechnology quotes mark the joined passage with an ellipsis, and the Stevens fragment is the verbatim "No. 59 nationally"
- P2: holds: years on both sides. K-8 rows carry no year from US News and read cannot tell
- P3: fixed: referee D6 and D7. The column is "100 minus participation rate" and the page says the state does not state how alternate-assessment takers enter the rate. The alternate assessment column prints each year as the state prints it
- P4: holds: no reason given for any count, no cause, no motive
- P5: n/a: no interval
- P6: fixed: referee D2. McNair mathematics now reads cannot tell (definition): US News does not state which tests it counts, and the files give 83.2 with Algebra I and 80.2 without. Referee D4: the page now says US News names "2023-2024 state assessment data", that New Jersey publishes it per test, and that reading the per-test files was chosen after a first run against the report figures
- P7: holds: rank.list.nj_* and rank.checks.nj_* staged, flipped live in the locked ship command
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py hits are the four cleared earlier plus "Algebra I" read as a first-person word
- P10: fixed: referee D15. Elementary and middle figures equal the 2023-24 per-test files in 21 of the 24 that could be compared (8 have a suppressed test row). Referee D1: the New Jersey high school list now shows the six high school weights. D11 to D14: source labels follow the method text (proficiency and standardized tests are public inputs with a US News calculation, wording not in the captured pages dropped)

## 2026-11-10 21:20 RANK graduate schools ship after the outside referee: Business schools 24 match 0 mismatch 56 cannot tell, Engineering schools 1 match 0 mismatch 49 cannot tell, Education schools 0 match 0 mismatch 72 cannot tell, Medical schools (Tier 1) 1 match 1 mismatch 94 cannot tell
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the sealed rule (rule.py 22 of 22) under Addendum 2, sealed at 04f16e5 before any graduate comparison. Public figures from each school's own reports, AAMC FACTS, NIH RePORTER, NSF HERD and IPEDS files, each saved with URL and quote (public/grad/*/*_public.json)
- II: holds: per-figure readings counted per list and per school in data/checks_grad.json. One mismatch: Pittsburgh medicine acceptance rate, 3.1% printed, 317 offers of 11,888 applicants (2.7%) in its 2025 admissions statistics. Paid-tier rows counted as cannot tell (paid tier, not read), one per school and indicator
- III: n/a: per-figure outcomes only
- V: holds: where US News's figure is behind its paid tier, the public figure is shown beside it and not scored (HERD and IPEDS labelled as whole-institution scope, NIH RePORTER as school of medicine awards)
- VI: holds: four outcomes kept, mismatch possible on every scored row. One added reading, public percent printed coarser than US News (CANNOT_TELL precision), applies to no row in this run
- R: holds: US News side read 2026-11-10 in the owner's browser without a paid tier (raw/grad_pages_20261110.txt, values under 100 re-read in raw/grad_pages_fix_20261110.txt). HBS and Columbia employment pages read in the browser (raw/manual/grad/). Every page says "details based on 2025 data"
- P1: holds: method quotes verbatim in raw/grad_method_addendum_20261110.txt. School quotes checked against saved text by the pull agents and the referee
- P2: holds: every scored figure shows its year on both sides. MBA employment read as the class of 2025, admissions as fall 2025 entrants, as Addendum 2 fixed before comparison
- P3: holds: labels as US News prints them. Education acceptance row relabelled "as US News prints it" (US News does not qualify it)
- P4: holds: no cause named. Booth's 635 and 60 joint degree students printed as counts, Columbia's sponsored-student statement quoted, no reason given for any gap
- P5: n/a: no interval
- P6: fixed: referee (rank_index_referee/grad/REFEREE_GRAD.md). Booth new entrants mismatch -> cannot tell (definition), Booth prints 635 full-time plus 60 joint degree and "calculated out of 695 students". First parse dropped values under 100 (education faculty and licensure takers, Caltech faculty), re-read and added. Mayo acceptance reason year (2026 figure). Kellogg two-year average from the workbook's unrounded shares. Baylor faculty figure seen only in a search excerpt removed
- P7: holds: rank.checks.mba, eng, edu, med staged before the page edit, set live in the locked ship command with the refreshed rank.list.* snippets
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py 15 hits, all earlier cleared ones (school-document quotes, "English I" and "Algebra I"), none in the graduate sections
- P10: holds: the precision reading and the medicine enrollment definition call (AAMC counts students on leave, US News uses full-time MD students) were made after the data and are named here and in each note
