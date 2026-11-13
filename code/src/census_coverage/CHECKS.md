
## 2026-11-11 11:26 CENSUS COVERAGE desk first read: 2020 Census state counts against the PES net coverage error at the Census 90 percent interval, with Demographic Analysis as a separate cell
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same quantity both sides: each area's published census household count and its PES net coverage error with standard error, one release (dataset 2020/dec/pes, PES20-G-02RV). The gate drops nothing: 51 of 51 areas have a standard error, 0 CANNOT_TELL. Puerto Rico (null row, separate table) is out of frame by plan. Plan commit ed9e74d 11:23:30 -05:00, sha256 04aaab1b, data/plan_seal.json, first reading 16:24:38Z.
- II: n/a: one published figure per area, not a repeated item, so no item flips. Repeat floor is that the API values equal the Census PDF values for all 51 areas (gate reader). Expected flags with nothing off: 5.1 of 51 at 90 percent two sided, 14 flagged, above the rough floor of 9.6 (areas not independent, described only).
- III: holds: below and above printed apart, never a net. 6 BELOW (Arkansas, Florida, Illinois, Mississippi, Tennessee, Texas) and 8 ABOVE (Delaware, Hawaii, Massachusetts, Minnesota, New York, Ohio, Rhode Island, Utah). The national cell and the DA middle series agree in sign (both slight undercount), the DA low series is an overcount, shown.
- V: holds: ruler is 1.645 times the published SE around the published NCE (Census 90 percent two sided test, PES20-G-02RV source and accuracy). Second ruler is Census own asterisk list, used as a gate, and it equals our BELOW and ABOVE sets exactly. The DA range is a separate second method on a different population, never merged.
- VI: holds: four outcomes kept, 6 BELOW, 8 ABOVE, 37 CONSISTENT, 0 CANNOT_TELL, both alternatives in PLAN.md. CONSISTENT is read as the survey interval being too wide to separate count from estimate, not as the count being right. National PES cell CONSISTENT (-0.24, SE 0.25). DA cell CONSISTENT (range +0.22 to -1.21 holds zero).
- R: holds: counts from summary_coverage.json of the run at 16:24 UTC plus reruns (display only fixes). First run had two gates FAIL (reader, census_flags) because my PDF parser regex missed counts under one million such as 700,000, fixed in the regex and rerun, rule and plan unchanged, then all six gates pass. Hand read from Census Appendix Table 3: Arkansas 2,929,000 -5.04 SE 2.21 asterisk, Texas 28,540,000 -1.92 0.82 asterisk, California 38,620,000 0.47 0.65, Hawaii 1,415,000 6.79 1.68 asterisk, Florida 21,070,000 -3.48 0.91 asterisk. Appendix Table 4 Arkansas omissions 10.1 SE 2.0, duplication 1.4 SE 0.3, other 0.8 SE 0.2 equal H_STATES. DA from release CB22-CN.02 Table 1 (0.22, -0.35, -1.21, PES -0.24 SE 0.25) text in data/raw/census_release_20220310.html.
- P1: holds: quotes in PLAN.md copied from the Census PDF text (data/raw/*.txt): 'statistically significant at the 90 percent confidence level (alpha = 0.10) using a two-sided test'. Remote Alaska and group quarters exclusion from the source and accuracy statement Target Population and Appendix Table 3 footnote. The page quotes none and paraphrases.
- P2: holds: every table figure says it is from the API group G_STATES or H_STATES, resident totals from the redistricting file, DA from the 10 March 2022 release, and the page states the run date and plan seal. Household counts rounded to the thousand by Census.
- P3: holds: sign convention (negative undercount, census minus DSE) matches PES20-G-02RV section 2. Interval label says it is ours, 1.645 times SE. The Census charts show 90 percent intervals, the page says so in those words.
- P4: holds: no cause is named for any area. The page says the SE leaves out nonsampling error, as Census states, and names no reason for a reading. The page says it does not judge the count.
- P5: holds: the 90 percent interval is named as ours from published NCE and SE. The DA range is called a range of scenarios, not an interval. The floor line says it treats areas as independent.
- P6: holds: the headline states the four counts only. CONSISTENT is not described as correct. Components are labelled as read against the national rate, separate from the net reading.
- P7: n/a: not shipped, no ledger row made, draft only for the outside referee (instruction). Ledger first, ledger/ship.sh later.
- P8: cannot tell: draft page built to census_coverage.html and the visible text was read in full through the lint extract, but it has not been rendered in a browser or served with /style.css, because shipping is out of scope.
- P9: holds: lint_copy.py gives 0 hits (no semicolons, no AI statement, no judgement word, no cause wording, no digit in a heading). The hits it first caught, 'right or wrong' and a year in headings, were rewritten. Census named terms (net coverage error, standard error, nonsampling error, erroneous enumeration) are cleared as technical terms in the lint regex. The Census Data API line is present.
- P10: holds: the only look before the seal (full list printed once with the 1.645 marker) is disclosed in PLAN.md and on the page. Nothing else is post hoc.
- O1: n/a: static one-time desk, 51 fixed rows, no tick or scheduler registered, no rider on the tick bus.
- O2: holds: the two gate failures on the first run were called failures, the readings were turned to CANNOT_TELL by the gate code, and the parser was fixed before the second run. A failed gate also stops build_page.py.
- O3: n/a: no GPU used.
- O4: n/a: no live job, liveness not needed. One run takes under a second under the .coverage.lock run lock.
- O5: holds: scripts use paths relative to their own folder, standard library only, run with python3 -I, API key read at call time by the scout cget.sh and never written (grep of the folder for the key text found nothing).
- O6: n/a: no GPU job.

## 2026-11-11 post-referee display fixes (census_coverage_referee/REFEREE.md, FIX THEN SHIP). Copy and display only, no rule, no outcome, no count changed. Summary and gates unchanged.
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: summary_coverage.json is untouched (run of 2026-11-11T16:25:01Z), counts 6 BELOW, 8 ABOVE, 37 CONSISTENT, 0 CANNOT_TELL are the same, the referee recounted all 51 areas with zero differences
- II: n/a: no repeated item
- III: holds: BELOW and ABOVE still printed apart, legend added under the table
- V: holds: ruler unchanged, 1.645 times the published SE. Added to the page: lowest flagged ratio 1.93 (Delaware), highest unflagged 1.58 (Louisiana), so no multiplier from 1.59 to 1.93 changes the 14 (computed in build_page.py from the summary)
- VI: holds: four outcomes kept, CANNOT_TELL 0 stated in the lead
- R: holds: display fix 1, CUT. The duplicate and other-erroneous readings were cut from the page entirely, and the omissions reading with them. Why: published values and SEs are rounded to 0.1 and moving each by 0.05 flips 24 of 51 duplicate readings and 33 of 51 other-erroneous readings (omissions 3), so those flags are rounding artifacts. BELOW and ABOVE meant count against survey for the net reading and rate against national for components, and omissions ABOVE is the undercount direction while net ABOVE is overcount, so a reader would cross them. 12 of the 15 omissions flags are the same states as the 14 net flags, so they restated the net reading. The cut was made after the pre-seal look and after the first reading, and is recorded here as such. The component table now shows each value with its standard error and a United States first row, no reading words and no counts. summary_coverage.json still holds the component readings and the page does not print them.
- R: holds: display fix 2. The line comparing 14 flagged areas with about 5 expected by chance was cut. Replaced by: Census marks the same 14 areas, a 90 percent test flags about one area in ten when nothing is off, the areas are not independent, so we do not read the count of 14 as a result. (Referee: under shared error P(14 or more) is 0.02 at rho 0.2 to 0.11 at 0.6, and nobody knows rho.)
- R: holds: display fix 3. Seal sentence now reads sealed before any count of outcomes was computed, and the closing section lists what came before the seal: raw pull, one look at the full list, replication not prediction, code committed after the first reading, the first run that failed two checks on the parser, rule unchanged.
- R: holds: display fix 4. Lead now reads each read one of three ways, and CANNOT_TELL is kept as its own count (none here).
- R: holds: display fix 5. Plain words added for standard error, nonsampling error and the 90 percent interval.
- R: holds: display fix 6. BELOW and ABOVE legend added under the full states table.
- R: holds: display fix 7. Resident-total column is labelled includes group quarters and Remote Alaska, not used in the reading, and the text says the gap is not an undercount figure.
- R: holds: display fix 8. DA cell no longer says CONSISTENT, it says the range holds zero and not an interval. All three series are listed with their sign, high series -1.21 is an undercount.
- R: holds: display fix 9. Census's own rule is replaced by the 90 percent level Census states.
- P1: n/a: no quoted text
- P2: holds: sources and run date unchanged
- P3: holds: sign convention unchanged
- P4: holds: no cause named, does not say Census is wrong, the survey is Census's own measure of its own count
- P5: holds: interval is ours, DA range is called a range
- P6: holds: nothing stronger than the table says
- P7: holds: ledger rows staged first, flipped live inside the ship lock
- P8: cannot tell: rendered with the site CSS only at ship, verified live after
- P9: holds: lint_copy.py 0 hits after the rebuild
- P10: holds: the cuts are disclosed above as post-look display fixes, no rule was set after the data

## 2026-11-11 11:34 CENSUS COVERAGE desk ship record: every printed table row and number as shipped (durable source for the censuscov.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from census_coverage.html as built from summary_coverage.json of the run at 2026-11-11T16:25:01Z, and make_rows.py asserts 107 table rows against the 4 outcome rows, 51 areas and 52 component rows
- II: n/a: a table copied as shipped, no comparison between runs
- III: holds: BELOW and ABOVE are separate rows, CANNOT_TELL has its own row (0)
- V: holds: one ruler, 1.645 times the published standard error, the range 1.59 to 1.93 is computed from the summary
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of 2026-11-11T16:25:01Z, no number typed by hand, the post-referee display fixes are in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line carries the area name and the columns the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the interval is ours and the lines say so on the page
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cov-record censuscov.outcome.below: BELOW 6 Arkansas, Florida, Illinois, Mississippi, Tennessee and Texas
cov-record censuscov.outcome.above: ABOVE 8 Delaware, Hawaii, Massachusetts, Minnesota, New York, Ohio, Rhode Island and Utah
cov-record censuscov.outcome.consistent: CONSISTENT 37 the remaining areas, listed in the full table
cov-record censuscov.outcome.cannot_tell: CANNOT_TELL 0 none, every area publishes a standard error
cov-record censuscov.area.alabama: Alabama 4,896,000 5,024,279 -1.05 1.22 -3.06 to 0.96 CONSISTENT
cov-record censuscov.area.alaska: Alaska 700,000 733,391 1.12 2.45 -2.91 to 5.15 CONSISTENT
cov-record censuscov.area.arizona: Arizona 6,991,000 7,151,502 -0.16 1.59 -2.78 to 2.46 CONSISTENT
cov-record censuscov.area.arkansas: Arkansas 2,929,000 3,011,524 -5.04 2.21 -8.68 to -1.40 BELOW
cov-record censuscov.area.california: California 38,620,000 39,538,223 0.47 0.65 -0.60 to 1.54 CONSISTENT
cov-record censuscov.area.colorado: Colorado 5,647,000 5,773,714 2.19 1.45 -0.20 to 4.58 CONSISTENT
cov-record censuscov.area.connecticut: Connecticut 3,498,000 3,605,944 -0.13 1.71 -2.94 to 2.68 CONSISTENT
cov-record censuscov.area.delaware: Delaware 967,000 989,948 5.45 2.82 0.81 to 10.09 ABOVE
cov-record censuscov.area.district-of-columbia: District of Columbia 649,000 689,545 4.59 4.93 -3.52 to 12.70 CONSISTENT
cov-record censuscov.area.florida: Florida 21,070,000 21,538,187 -3.48 0.91 -4.98 to -1.98 BELOW
cov-record censuscov.area.georgia: Georgia 10,460,000 10,711,908 0.31 1.11 -1.52 to 2.14 CONSISTENT
cov-record censuscov.area.hawaii: Hawaii 1,415,000 1,455,271 6.79 1.68 4.03 to 9.55 ABOVE
cov-record censuscov.area.idaho: Idaho 1,789,000 1,839,106 -1.55 1.62 -4.21 to 1.11 CONSISTENT
cov-record censuscov.area.illinois: Illinois 12,540,000 12,812,508 -1.97 0.89 -3.43 to -0.51 BELOW
cov-record censuscov.area.indiana: Indiana 6,607,000 6,785,528 0.21 0.94 -1.34 to 1.76 CONSISTENT
cov-record censuscov.area.iowa: Iowa 3,092,000 3,190,369 -2.04 3.25 -7.39 to 3.31 CONSISTENT
cov-record censuscov.area.kansas: Kansas 2,851,000 2,937,880 -0.81 1.42 -3.15 to 1.53 CONSISTENT
cov-record censuscov.area.kentucky: Kentucky 4,381,000 4,505,836 -1.18 1.50 -3.65 to 1.29 CONSISTENT
cov-record censuscov.area.louisiana: Louisiana 4,534,000 4,657,757 -3.73 2.36 -7.61 to 0.15 CONSISTENT
cov-record censuscov.area.maine: Maine 1,326,000 1,362,359 2.20 1.90 -0.93 to 5.33 CONSISTENT
cov-record censuscov.area.maryland: Maryland 6,052,000 6,177,224 -1.17 1.41 -3.49 to 1.15 CONSISTENT
cov-record censuscov.area.massachusetts: Massachusetts 6,784,000 7,029,917 2.24 1.06 0.50 to 3.98 ABOVE
cov-record censuscov.area.michigan: Michigan 9,856,000 10,077,331 0.14 0.68 -0.98 to 1.26 CONSISTENT
cov-record censuscov.area.minnesota: Minnesota 5,568,000 5,706,494 3.84 0.97 2.24 to 5.44 ABOVE
cov-record censuscov.area.mississippi: Mississippi 2,868,000 2,961,279 -4.11 1.63 -6.79 to -1.43 BELOW
cov-record censuscov.area.missouri: Missouri 5,986,000 6,154,913 -1.05 0.97 -2.65 to 0.55 CONSISTENT
cov-record censuscov.area.montana: Montana 1,055,000 1,084,225 -4.39 3.70 -10.48 to 1.70 CONSISTENT
cov-record censuscov.area.nebraska: Nebraska 1,912,000 1,961,504 -0.73 1.35 -2.95 to 1.49 CONSISTENT
cov-record censuscov.area.nevada: Nevada 3,068,000 3,104,614 4.42 3.44 -1.24 to 10.08 CONSISTENT
cov-record censuscov.area.new-hampshire: New Hampshire 1,335,000 1,377,529 0.53 1.58 -2.07 to 3.13 CONSISTENT
cov-record censuscov.area.new-jersey: New Jersey 9,109,000 9,288,994 -0.12 0.93 -1.65 to 1.41 CONSISTENT
cov-record censuscov.area.new-mexico: New Mexico 2,075,000 2,117,522 0.10 2.42 -3.88 to 4.08 CONSISTENT
cov-record censuscov.area.new-york: New York 19,590,000 20,201,249 3.44 0.94 1.89 to 4.99 ABOVE
cov-record censuscov.area.north-carolina: North Carolina 10,150,000 10,439,388 -1.59 1.09 -3.38 to 0.20 CONSISTENT
cov-record censuscov.area.north-dakota: North Dakota 753,000 779,094 -0.35 1.86 -3.41 to 2.71 CONSISTENT
cov-record censuscov.area.ohio: Ohio 11,500,000 11,799,448 1.49 0.67 0.39 to 2.59 ABOVE
cov-record censuscov.area.oklahoma: Oklahoma 3,842,000 3,959,353 2.41 1.89 -0.70 to 5.52 CONSISTENT
cov-record censuscov.area.oregon: Oregon 4,140,000 4,237,256 1.00 1.22 -1.01 to 3.01 CONSISTENT
cov-record censuscov.area.pennsylvania: Pennsylvania 12,600,000 13,002,700 0.48 0.67 -0.62 to 1.58 CONSISTENT
cov-record censuscov.area.rhode-island: Rhode Island 1,052,000 1,097,379 5.05 1.43 2.70 to 7.40 ABOVE
cov-record censuscov.area.south-carolina: South Carolina 4,980,000 5,118,425 -1.36 1.26 -3.43 to 0.71 CONSISTENT
cov-record censuscov.area.south-dakota: South Dakota 855,000 886,667 -0.42 1.87 -3.50 to 2.66 CONSISTENT
cov-record censuscov.area.tennessee: Tennessee 6,754,000 6,910,840 -4.78 1.51 -7.26 to -2.30 BELOW
cov-record censuscov.area.texas: Texas 28,540,000 29,145,505 -1.92 0.82 -3.27 to -0.57 BELOW
cov-record censuscov.area.utah: Utah 3,216,000 3,271,616 2.59 1.23 0.57 to 4.61 ABOVE
cov-record censuscov.area.vermont: Vermont 618,000 643,077 1.48 1.83 -1.53 to 4.49 CONSISTENT
cov-record censuscov.area.virginia: Virginia 8,395,000 8,631,393 -0.35 1.11 -2.18 to 1.48 CONSISTENT
cov-record censuscov.area.washington: Washington 7,545,000 7,705,281 0.29 1.08 -1.49 to 2.07 CONSISTENT
cov-record censuscov.area.west-virginia: West Virginia 1,742,000 1,793,716 1.53 4.40 -5.71 to 8.77 CONSISTENT
cov-record censuscov.area.wisconsin: Wisconsin 5,742,000 5,893,718 0.85 0.86 -0.56 to 2.26 CONSISTENT
cov-record censuscov.area.wyoming: Wyoming 564,000 576,851 -2.60 2.01 -5.91 to 0.71 CONSISTENT
cov-record censuscov.comp.united-states: United States 5.8 ± 0.24 1.6 ± 0.04 0.6 ± 0.03
cov-record censuscov.comp.alabama: Alabama 6.6 ± 1.1 1.8 ± 0.3 0.5 ± 0.1
cov-record censuscov.comp.alaska: Alaska 5.8 ± 2.3 2.5 ± 0.7 0.6 ± 0.2
cov-record censuscov.comp.arizona: Arizona 5.7 ± 1.5 1.4 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.arkansas: Arkansas 10.1 ± 2.0 1.4 ± 0.3 0.8 ± 0.2
cov-record censuscov.comp.california: California 5.3 ± 0.6 1.4 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.colorado: Colorado 4.4 ± 1.0 2.5 ± 0.8 0.4 ± 0.1
cov-record censuscov.comp.connecticut: Connecticut 7.2 ± 1.3 2.6 ± 0.6 0.6 ± 0.1
cov-record censuscov.comp.delaware: Delaware 0.7 ± 2.6 1.3 ± 0.4 0.4 ± 0.1
cov-record censuscov.comp.district-of-columbia: District of Columbia 5.1 ± 3.9 2.5 ± 0.6 1.2 ± 0.3
cov-record censuscov.comp.florida: Florida 9.2 ± 0.8 1.3 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.georgia: Georgia 5.5 ± 1.0 1.4 ± 0.2 0.8 ± 0.1
cov-record censuscov.comp.hawaii: Hawaii 3.5 ± 1.3 5.5 ± 0.7 0.5 ± 0.1
cov-record censuscov.comp.idaho: Idaho 5.6 ± 1.5 0.7 ± 0.4 0.5 ± 0.1
cov-record censuscov.comp.illinois: Illinois 7.8 ± 0.8 1.6 ± 0.2 0.4 ± 0.1
cov-record censuscov.comp.indiana: Indiana 4.9 ± 0.9 1.5 ± 0.2 0.4 ± 0.1
cov-record censuscov.comp.iowa: Iowa 6.5 ± 3.1 1.1 ± 0.2 0.2 ± 0.1
cov-record censuscov.comp.kansas: Kansas 5.7 ± 1.4 1.6 ± 0.3 0.5 ± 0.2
cov-record censuscov.comp.kentucky: Kentucky 6.6 ± 1.4 1.7 ± 0.3 0.9 ± 0.2
cov-record censuscov.comp.louisiana: Louisiana 10.4 ± 2.3 2.3 ± 0.4 0.7 ± 0.1
cov-record censuscov.comp.maine: Maine 3.4 ± 1.9 2.0 ± 0.5 0.6 ± 0.2
cov-record censuscov.comp.maryland: Maryland 6.6 ± 1.3 1.0 ± 0.2 0.6 ± 0.2
cov-record censuscov.comp.massachusetts: Massachusetts 4.9 ± 0.9 2.2 ± 0.3 0.9 ± 0.2
cov-record censuscov.comp.michigan: Michigan 5.0 ± 0.7 1.3 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.minnesota: Minnesota 1.8 ± 0.9 1.4 ± 0.2 1.2 ± 0.3
cov-record censuscov.comp.mississippi: Mississippi 9.9 ± 1.5 1.9 ± 0.6 0.8 ± 0.3
cov-record censuscov.comp.missouri: Missouri 6.1 ± 0.9 1.2 ± 0.2 0.4 ± 0.1
cov-record censuscov.comp.montana: Montana 11.1 ± 3.7 3.3 ± 0.7 0.5 ± 0.2
cov-record censuscov.comp.nebraska: Nebraska 5.8 ± 1.1 1.4 ± 0.3 0.5 ± 0.1
cov-record censuscov.comp.nevada: Nevada 0.9 ± 3.3 0.7 ± 0.3 0.4 ± 0.1
cov-record censuscov.comp.new-hampshire: New Hampshire 4.5 ± 1.6 1.2 ± 0.3 0.5 ± 0.2
cov-record censuscov.comp.new-jersey: New Jersey 6.8 ± 0.9 1.9 ± 0.3 0.5 ± 0.2
cov-record censuscov.comp.new-mexico: New Mexico 7.3 ± 2.1 2.9 ± 0.7 0.5 ± 0.1
cov-record censuscov.comp.new-york: New York 5.9 ± 0.8 3.0 ± 0.2 0.6 ± 0.1
cov-record censuscov.comp.north-carolina: North Carolina 7.0 ± 1.1 1.3 ± 0.2 0.7 ± 0.1
cov-record censuscov.comp.north-dakota: North Dakota 5.7 ± 1.7 1.5 ± 0.3 0.5 ± 0.2
cov-record censuscov.comp.ohio: Ohio 3.7 ± 0.7 1.3 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.oklahoma: Oklahoma 3.1 ± 1.5 1.9 ± 0.6 0.4 ± 0.1
cov-record censuscov.comp.oregon: Oregon 4.1 ± 1.1 1.3 ± 0.4 0.5 ± 0.1
cov-record censuscov.comp.pennsylvania: Pennsylvania 4.4 ± 0.6 1.2 ± 0.1 0.5 ± 0.1
cov-record censuscov.comp.rhode-island: Rhode Island 2.3 ± 1.2 2.2 ± 0.4 0.5 ± 0.2
cov-record censuscov.comp.south-carolina: South Carolina 6.6 ± 1.1 1.2 ± 0.2 0.9 ± 0.2
cov-record censuscov.comp.south-dakota: South Dakota 5.4 ± 1.6 1.1 ± 0.3 1.1 ± 0.8
cov-record censuscov.comp.tennessee: Tennessee 10.1 ± 1.4 1.7 ± 0.3 0.7 ± 0.1
cov-record censuscov.comp.texas: Texas 7.6 ± 0.8 1.5 ± 0.1 0.6 ± 0.1
cov-record censuscov.comp.utah: Utah 2.8 ± 1.2 1.1 ± 0.2 0.4 ± 0.1
cov-record censuscov.comp.vermont: Vermont 5.8 ± 1.6 3.1 ± 0.8 0.6 ± 0.2
cov-record censuscov.comp.virginia: Virginia 5.5 ± 0.9 0.9 ± 0.1 1.1 ± 0.5
cov-record censuscov.comp.washington: Washington 4.8 ± 1.0 1.0 ± 0.2 0.6 ± 0.2
cov-record censuscov.comp.west-virginia: West Virginia 4.3 ± 3.9 2.2 ± 0.4 0.8 ± 0.3
cov-record censuscov.comp.wisconsin: Wisconsin 4.6 ± 0.8 1.3 ± 0.2 0.9 ± 0.3
cov-record censuscov.comp.wyoming: Wyoming 7.6 ± 1.9 1.2 ± 0.3 0.2 ± 0.1
cov-record censuscov.headline: 6 areas BELOW, 8 ABOVE, 37 CONSISTENT, 0 CANNOT_TELL
cov-record censuscov.ruler: The lowest flagged ratio of net coverage error to standard error is 1.93 (Delaware) and the highest unflagged is 1.58 (Louisiana), so no multiplier from 1.59 to 1.93 changes the 14 flagged areas
cov-record censuscov.floor: Census marks the same 14 areas. A 90 percent test flags about one area in ten when nothing is off, and the areas are not independent of each other, so we do not read the count of 14 as a result
cov-record censuscov.us: For the nation the survey gives a net coverage error of -0.24 percent with a standard error of 0.25, so the 90 percent interval is -0.65 to 0.17 percent and the national cell reads CONSISTENT
cov-record censuscov.da: The low series is a net coverage error of 0.22 percent and is an overcount, the middle series is -0.35 percent and is an undercount, and the high series is -1.21 percent and is an undercount
cov-record censuscov.da_pes: The survey national estimate of -0.24 percent sits inside that range
cov-record censuscov.frame: The survey covers the household population of the 50 states and the District of Columbia on 1 April 2020

## 2026-11-12 10:26 Faults and Guards 2.0 migration of the CENSUS COVERAGE outcome rule (PLAN_ADDENDUM_std2.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md and data/plan_seal.json are untouched, the plan hash still matches the seal and the addendum is a new file committed as 1576990 before the re-run
- II: holds: the 14 flagged areas are the same set as before and are still compared with the 5.1 expected at 90 percent two sided (floor unchanged), the 37 that held zero are not netted into any share
- III: holds: BELOW 6 and ABOVE 8 stay separate, and every non-outcome number of summary_coverage.json equals the backup summary_coverage.json.bak-20261112-std2 for all 51 areas and all 102 component rows
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before the re-run, zero is a point figure with no tolerance read with K.read(bound=0), the 1.645 multiplier and 90 percent level are unchanged, no size that matters is invented
- VI: holds: BELOW 6, ABOVE 8, CANNOT_TELL 37 all STRADDLES_EDGE, CONSISTENT 0, the both-alternatives test is not applied because no size is named and the page and the addendum say so
- R: holds: counts are read from summary_coverage.json of the re-run with all six gates passed, REQ-13 reads 0 NOTHING_RETURNED and 37 of 51 CANNOT_TELL, 37 STRADDLES_EDGE, components CONSISTENT 101 to 0 and CANNOT_TELL 36, 27 and 38
- P1: n/a: no quotation of any source is added or changed by this migration
- P2: n/a: no new figure is added, every number keeps its area name and the table it comes from
- P3: n/a: no setting label of any source is touched by this change
- P4: holds: no cause is named, the added page text says only which closed reason a cannot tell carries and that zero has no tolerance
- P5: holds: the interval is still ours, normal 1.645 times the published standard error, and the page says an interval holding zero is not read as agreement with zero
- P6: holds: the page says CANNOT_TELL does not say the count is right, no stronger than the reading, and the Demographic Analysis range reads the same way as a range
- P7: holds: the 41 changed censuscov rows are updated in one locked pass through ledger.py load, save and checks_ref with outcome, source.grep and surface text together, new cov-record lines are in this entry, nothing is deployed from here
- P8: cannot tell: census_coverage.html was rebuilt and lint_copy.py reports 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences, no semicolons in the added text, no digit in any heading, lint_copy.py 0 hits
- P10: holds: the addendum is dated 12 Nov 2026 and committed before any reading under the new rule, the flips fall out of the rule and no tolerance was chosen after the data
cov-record censuscov.outcome.consistent: CONSISTENT 0 not available, zero has no tolerance and no size that matters is named
cov-record censuscov.outcome.cannot_tell: CANNOT_TELL 37 37 STRADDLES_EDGE, the interval holds zero, listed in the full table. Every area publishes a standard error, so none is NO_INTERVAL_FORMABLE
cov-record censuscov.area.alabama: Alabama 4,896,000 5,024,279 -1.05 1.22 -3.06 to 0.96 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.alaska: Alaska 700,000 733,391 1.12 2.45 -2.91 to 5.15 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.arizona: Arizona 6,991,000 7,151,502 -0.16 1.59 -2.78 to 2.46 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.california: California 38,620,000 39,538,223 0.47 0.65 -0.60 to 1.54 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.colorado: Colorado 5,647,000 5,773,714 2.19 1.45 -0.20 to 4.58 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.connecticut: Connecticut 3,498,000 3,605,944 -0.13 1.71 -2.94 to 2.68 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.district-of-columbia: District of Columbia 649,000 689,545 4.59 4.93 -3.52 to 12.70 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.georgia: Georgia 10,460,000 10,711,908 0.31 1.11 -1.52 to 2.14 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.idaho: Idaho 1,789,000 1,839,106 -1.55 1.62 -4.21 to 1.11 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.indiana: Indiana 6,607,000 6,785,528 0.21 0.94 -1.34 to 1.76 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.iowa: Iowa 3,092,000 3,190,369 -2.04 3.25 -7.39 to 3.31 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.kansas: Kansas 2,851,000 2,937,880 -0.81 1.42 -3.15 to 1.53 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.kentucky: Kentucky 4,381,000 4,505,836 -1.18 1.50 -3.65 to 1.29 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.louisiana: Louisiana 4,534,000 4,657,757 -3.73 2.36 -7.61 to 0.15 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.maine: Maine 1,326,000 1,362,359 2.20 1.90 -0.93 to 5.33 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.maryland: Maryland 6,052,000 6,177,224 -1.17 1.41 -3.49 to 1.15 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.michigan: Michigan 9,856,000 10,077,331 0.14 0.68 -0.98 to 1.26 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.missouri: Missouri 5,986,000 6,154,913 -1.05 0.97 -2.65 to 0.55 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.montana: Montana 1,055,000 1,084,225 -4.39 3.70 -10.48 to 1.70 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.nebraska: Nebraska 1,912,000 1,961,504 -0.73 1.35 -2.95 to 1.49 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.nevada: Nevada 3,068,000 3,104,614 4.42 3.44 -1.24 to 10.08 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.new-hampshire: New Hampshire 1,335,000 1,377,529 0.53 1.58 -2.07 to 3.13 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.new-jersey: New Jersey 9,109,000 9,288,994 -0.12 0.93 -1.65 to 1.41 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.new-mexico: New Mexico 2,075,000 2,117,522 0.10 2.42 -3.88 to 4.08 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.north-carolina: North Carolina 10,150,000 10,439,388 -1.59 1.09 -3.38 to 0.20 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.north-dakota: North Dakota 753,000 779,094 -0.35 1.86 -3.41 to 2.71 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.oklahoma: Oklahoma 3,842,000 3,959,353 2.41 1.89 -0.70 to 5.52 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.oregon: Oregon 4,140,000 4,237,256 1.00 1.22 -1.01 to 3.01 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.pennsylvania: Pennsylvania 12,600,000 13,002,700 0.48 0.67 -0.62 to 1.58 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.south-carolina: South Carolina 4,980,000 5,118,425 -1.36 1.26 -3.43 to 0.71 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.south-dakota: South Dakota 855,000 886,667 -0.42 1.87 -3.50 to 2.66 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.vermont: Vermont 618,000 643,077 1.48 1.83 -1.53 to 4.49 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.virginia: Virginia 8,395,000 8,631,393 -0.35 1.11 -2.18 to 1.48 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.washington: Washington 7,545,000 7,705,281 0.29 1.08 -1.49 to 2.07 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.west-virginia: West Virginia 1,742,000 1,793,716 1.53 4.40 -5.71 to 8.77 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.wisconsin: Wisconsin 5,742,000 5,893,718 0.85 0.86 -0.56 to 2.26 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.area.wyoming: Wyoming 564,000 576,851 -2.60 2.01 -5.91 to 0.71 CANNOT_TELL (STRADDLES_EDGE)
cov-record censuscov.headline: 6 areas BELOW, 8 ABOVE, 37 CANNOT_TELL
cov-record censuscov.us: For the nation the survey gives a net coverage error of -0.24 percent with a standard error of 0.25, so the 90 percent interval is -0.65 to 0.17 percent and the national cell reads CANNOT_TELL (STRADDLES_EDGE)
