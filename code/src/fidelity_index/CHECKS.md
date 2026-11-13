
## 2026-11-11 11:24 FIDELITY desk first read: NCHS state counts of divorces and marriages against ACS women estimates with 90 percent margin, 2010 to 2024
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same quantity both sides after conversion: NCHS count of events by occurrence against ACS women estimate read as events, same state and year (PLAN.md 1b571f2 11:22:31 -05:00, data/plan_seal.json). Divorce 714 rows: 25 above, 265 below, 303 inside, 121 cannot tell (51 no stated count 2024, 69 state does not report, 1 no ACS interval Delaware 2018). Marriage 714 rows: 95 above, 313 below, 253 inside, 53 cannot tell (51 no stated count, 2 not reported). Occurrence against residence is not removed, destination cells printed apart
- II: n/a: counts are one pull of fixed published files, not a flip-prone item reading. Repeat floor is that the ACS API values equal the Census table-based summary files in 1020 of 1020 compared values for 2022 and 2023. No net is computed
- III: holds: above and below are printed apart in every cell and never netted. Divorce reads below far more than above, marriage reads below and above with destination states all above. Cannot tell is never folded into either side. Women and men ACS estimates disagree on the outcome in 246 divorce and 85 marriage rows, counted as sex splits
- V: holds: ruler is the published ACS 90 percent margin on the women estimate, against an exact NCHS count. Second rulers shown beside it: men estimate interval and the 95 percent scale (margin times 1.96 over 1.645), both display only in data/fidelity.json. The reading against 90 percent is our conversion, not Census's
- VI: holds: four outcomes kept with both alternatives in PLAN.md. Jurisdiction cells read above, below, inside, mixed or cannot tell by the rule fixed in the plan, no share or test over rows as rows are not independent. Overall cells read MIXED for both events, destination marriage reads above
- R: holds: counts from summary_fidelity.json and data/fidelity.json of the run after the seal. Hand-read rows: Texas 2022 divorce NCHS 56,269 and ACS women 89,194 plus or minus 6,115, Florida 2023 divorce 66,958 and 79,000 plus or minus 5,982, New York 2022 marriage 123,526 and 123,941 plus or minus 5,834, Pennsylvania 2023 marriage 69,242 and 85,201 plus or minus 5,871. All four equal the parsed rows (NCHS from PDF text, ACS from the summary files and the API). NCHS parse: sum of reporting states equals the printed United States figure in all 24 years for both tables. Rate check 1183 of 1242 within 0.1 (95.2 percent, gate 90). Not checked: the PDF layout against the page images, only the text dump
- P1: n/a: the page quotes no source text, it names the tables and files
- P2: holds: page figures all come from summary_fidelity.json and data/fidelity.json, and the page says where each source lives with its URL. NCHS table version is the 2000 to 2023 count PDF and the 2024 rate workbook as pulled 11 Nov 2026, snapshot copies in data/snapshots
- P3: holds: NCHS divorce includes annulments and in some states petitions (said on the page), counts provisional, ACS table names B12501 B12503 and the 90 percent margin as published, 2020 left out and said why
- P4: holds: no row is given a cause. The page says a row above or below names no cause. The occurrence against residence paragraph is named as a limit and the destination states are counted apart, not as an explanation of every gap
- P5: holds: the only interval is the ACS published 90 percent margin and the page says so. No Wilson or other share interval is printed, and the page says rows are not independent
- P6: holds: the headline says the two count different things and the gap is a reading of the difference, not a claim that either is mistaken. The page makes no statement on which source is closer to the true count
- P7: n/a: not shipped, no ledger line, no site edit, no ship.sh. Draft fidelity.html is git-ignored and goes to the outside referee first
- P8: cannot tell: draft built and read as text, it uses /style.css from the site and was not rendered in a browser here
- P9: holds: lint_copy.py on fidelity.html gives 0 hits. No semicolons, no digits in headings, no AI statements, no cause words, we and our reading, Census attribution line present
- P10: caught: one deviation labelled here. The reader-gate tolerance first ran at 0.15 in a draft before the real run and was set back to the plan's 0.1 before any reading was written, it passes at 0.1 (95.2 percent). The page wording changed three words (by hand, because) for the lint, no number changed

## 2026-11-11 FIDELITY desk post-referee fixes (fidelity_referee/REFEREE.md, FIX THEN SHIP, recount 0 differences): display and disclosure only
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no cell re-classed, make_rows.py and summary_fidelity.json untouched, the sealed women's reading stays the scored one. Every added figure is computed in build_page.py or gate2_misses.py from data/fidelity.json, data/nchs_counts.json and the raw rate workbooks
- II: n/a: no second run, the same rows displayed with the men's reading beside them
- III: fixed: post-referee fix 1, men's counts and the both-sexes line added to the lead and both headline tables. Divorce women 25 above, 265 below, 303 inside, men 78, 140, 375, both below 111, both inside 225, both above 11. Marriage women 95, 313, 253, men 95, 332, 234, both below 294, both above 81, both inside 201. All equal the referee's recount
- V: fixed: post-referee fix 1, national baseline sentence from the 2022 sums over reporting states: divorce NCHS over ACS women 0.80 and men 0.89, marriage 0.89 and 0.85
- VI: caught: the referee named Texas, Illinois, Massachusetts, Iowa and Kansas as reading below under both sexes. Under the sealed jurisdiction rule (80 percent of scored rows) the men's reading is below only for Georgia, Illinois, Louisiana and Texas. Massachusetts reads below in 13 of 13 years under women and 4 of 13 under men, Iowa 12 and 9, Kansas 12 and 9. The page leads with the four and says the other three hold under one sex only. The page prints the computed list
- R: holds: referee recount equals the builder on all 1,428 rows, gate 2 reproduced at 1,183 of 1,242
- P1: fixed: post-referee fix 7, NCHS text quoted from the rate workbooks state-divorce-rates and state-marriage-rates (and sd.pdf): "Rates are based on provisional counts of divorces by state of occurrence", "Includes annulments", "Includes divorce petitions filed or legal separations for some counties or States", "Rates are based on provisional counts of marriages by state of occurrence", "Marriage data includes nonlicensed marriages registered". The unsourced "no final series" is gone
- P2: fixed: post-referee fix 8, the 59 gate 2 misses are published as data/gate2_rate_misses.csv with the swap test in data/gate2_swap_check.json, both made by gate2_misses.py, and the page names the file
- P3: fixed: post-referee fixes 2, 3 and 6. Same-sex events: two women counted twice (overcount), two men not counted (undercount), net sign unknown. Non-reporting states: "in some or all years of the frame" with the computed blank runs (CA, HI, IN, MN all frame years, GA 2010 to 2016, LA 2010 to 2012, NM 2016 to 2023). Column renamed "ACS estimate minus NCHS count" with a point-estimate note
- P4: holds: the Louisiana 2022 and 2023 and Georgia 2018 count breaks are noted as printed (LA 9,995 to 3,393 to 4,120, GA 36,464 to 26,327) with no cause and no re-class. The page says the readings cannot show missing records or that either source is mistaken
- P5: holds: no interval or test added, the margin covers ACS sampling only and the page says so
- P6: fixed: post-referee fixes 4 and 5. The sentence "We chose women over men before comparing anything" is replaced by the scout-aware account: scout of 16 state-year-events shown for TX, FL, NY, PA, ACS pulls in the minute before the plan commit and not read, code committed after the first comparison, rate tolerance first 0.15 then 0.1
- P7: n/a: desk-folder work only, wiring and ship are recorded in the ship entry
- P8: cannot tell: page built to fidelity.html and read as text, not rendered in a browser here
- P9: holds: lint_copy.py on fidelity.html gives 0 hits. The Pennsylvania and Philadelphia scout note is left off the page (0 mentions)
- P10: caught: referee fix 5 said 14 divorce state-years in 2016 and 2017 where the NCHS count and rate tables disagree and two rows would flip (Kansas 2017, Maine 2017). Computed at the gate's 0.1 tolerance the count is 12 state-years (IL, IA, KS, ME, MD, MA, TX in 2016, IA, KS, LA, ME, MD in 2017). Under the 2016 and 2017 swap for the six states whose swapped counts fit both rates, three rows change: Kansas 2017 and Maine 2017 inside to below, and Massachusetts 2016 below to inside. The page prints the computed 12 and 3. The referee note that Illinois 2016 is footnoted as revised holds for the marriage table only, the divorce table footnotes Texas 2016 and Maryland 2021. No cell re-classed

## 2026-11-11 11:40 FIDELITY desk ship record: every printed table row and number as shipped (durable source for the fid.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from fidelity.html as built from summary_fidelity.json (run 2026-11-11T16:23:26Z) and data/, and ledger_rows.py asserts the table rows against the page
- II: n/a: a page copied as shipped, no comparison between runs
- III: holds: above and below are separate columns in every row, cannot tell is its own column and never in a count of the other three
- V: holds: one ruler, the published ACS 90 percent margin on the women estimate, the men estimate beside it for the same rows
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of 2026-11-11T16:23:26Z and data/fidelity.json, no number typed by hand, the post-referee display fixes are in the entry before this one
- P1: holds: the NCHS text is quoted from the rate workbooks as printed
- P2: holds: each line carries the label the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the margin is ACS's published one and the page says it covers ACS sampling only
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
fid-record fid.divorce.all.all-jurisdictions-25-265-303-121-mixed: All jurisdictions 25 265 303 121 mixed
fid-record fid.divorce.all.without-destination-states-19-265-296-120-mixed: Without destination states 19 265 296 120 mixed
fid-record fid.divorce.all.destination-states-only-6-0-7-1-mixed: Destination states only 6 0 7 1 mixed
fid-record fid.divorce.sex.nchs-above-25-78-11: NCHS above 25 78 11
fid-record fid.divorce.sex.nchs-below-265-140-111: NCHS below 265 140 111
fid-record fid.divorce.sex.nchs-inside-303-375-225: NCHS inside 303 375 225
fid-record fid.divorce.year.2010-2-24-19-6-mixed: 2010 2 24 19 6 mixed
fid-record fid.divorce.year.2011-1-20-24-6-mixed: 2011 1 20 24 6 mixed
fid-record fid.divorce.year.2012-1-26-18-6-mixed: 2012 1 26 18 6 mixed
fid-record fid.divorce.year.2013-2-22-22-5-mixed: 2013 2 22 22 5 mixed
fid-record fid.divorce.year.2014-3-23-20-5-mixed: 2014 3 23 20 5 mixed
fid-record fid.divorce.year.2015-1-16-29-5-mixed: 2015 1 16 29 5 mixed
fid-record fid.divorce.year.2016-0-16-29-6-mixed: 2016 0 16 29 6 mixed
fid-record fid.divorce.year.2017-1-20-25-5-mixed: 2017 1 20 25 5 mixed
fid-record fid.divorce.year.2018-4-18-23-6-mixed: 2018 4 18 23 6 mixed
fid-record fid.divorce.year.2019-3-15-28-5-mixed: 2019 3 15 28 5 mixed
fid-record fid.divorce.year.2021-3-15-28-5-mixed: 2021 3 15 28 5 mixed
fid-record fid.divorce.year.2022-3-25-18-5-mixed: 2022 3 25 18 5 mixed
fid-record fid.divorce.year.2023-1-25-20-5-mixed: 2023 1 25 20 5 mixed
fid-record fid.divorce.year.2024-0-0-0-51-cannot-tell: 2024 0 0 0 51 cannot tell
fid-record fid.divorce.state.alabama-0-8-5-1-mixed-0-82: Alabama 0 8 5 1 mixed 0.82
fid-record fid.divorce.state.alaska-4-1-8-1-mixed-1-23: Alaska 4 1 8 1 mixed 1.23
fid-record fid.divorce.state.arizona-0-6-7-1-mixed-0-90: Arizona 0 6 7 1 mixed 0.90
fid-record fid.divorce.state.arkansas-0-6-7-1-mixed-0-82: Arkansas 0 6 7 1 mixed 0.82
fid-record fid.divorce.state.california-0-0-0-14-cannot-tell: California 0 0 0 14 cannot tell
fid-record fid.divorce.state.colorado-0-3-10-1-mixed-0-97: Colorado 0 3 10 1 mixed 0.97
fid-record fid.divorce.state.connecticut-1-5-7-1-mixed-0-94: Connecticut 1 5 7 1 mixed 0.94
fid-record fid.divorce.state.delaware-0-5-7-2-mixed-0-78: Delaware 0 5 7 2 mixed 0.78
fid-record fid.divorce.state.district-of-columbia-2-0-11-1-inside-0-95: District of Columbia 2 0 11 1 inside 0.95
fid-record fid.divorce.state.florida-0-2-11-1-inside-1-02: Florida 0 2 11 1 inside 1.02
fid-record fid.divorce.state.georgia-0-5-1-8-below-0-70: Georgia 0 5 1 8 below 0.70
fid-record fid.divorce.state.hawaii-0-0-0-14-cannot-tell: Hawaii 0 0 0 14 cannot tell
fid-record fid.divorce.state.idaho-0-3-10-1-mixed-0-93: Idaho 0 3 10 1 mixed 0.93
fid-record fid.divorce.state.illinois-0-13-0-1-below-0-71: Illinois 0 13 0 1 below 0.71
fid-record fid.divorce.state.indiana-0-0-0-14-cannot-tell: Indiana 0 0 0 14 cannot tell
fid-record fid.divorce.state.iowa-0-12-1-1-below-0-63: Iowa 0 12 1 1 below 0.63
fid-record fid.divorce.state.kansas-0-12-1-1-below-0-68: Kansas 0 12 1 1 below 0.68
fid-record fid.divorce.state.kentucky-0-10-3-1-mixed-0-81: Kentucky 0 10 3 1 mixed 0.81
fid-record fid.divorce.state.louisiana-0-9-1-4-below-0-58: Louisiana 0 9 1 4 below 0.58
fid-record fid.divorce.state.maine-1-2-10-1-mixed-0-85: Maine 1 2 10 1 mixed 0.85
fid-record fid.divorce.state.maryland-0-10-3-1-mixed-0-75: Maryland 0 10 3 1 mixed 0.75
fid-record fid.divorce.state.massachusetts-0-13-0-1-below-0-67: Massachusetts 0 13 0 1 below 0.67
fid-record fid.divorce.state.michigan-0-10-3-1-mixed-0-88: Michigan 0 10 3 1 mixed 0.88
fid-record fid.divorce.state.minnesota-0-0-0-14-cannot-tell: Minnesota 0 0 0 14 cannot tell
fid-record fid.divorce.state.mississippi-0-8-5-1-mixed-0-83: Mississippi 0 8 5 1 mixed 0.83
fid-record fid.divorce.state.missouri-0-9-4-1-mixed-0-85: Missouri 0 9 4 1 mixed 0.85
fid-record fid.divorce.state.montana-1-3-9-1-mixed-0-81: Montana 1 3 9 1 mixed 0.81
fid-record fid.divorce.state.nebraska-0-2-11-1-inside-0-90: Nebraska 0 2 11 1 inside 0.90
fid-record fid.divorce.state.nevada-6-0-7-1-mixed-1-15: Nevada 6 0 7 1 mixed 1.15
fid-record fid.divorce.state.new-hampshire-0-4-9-1-mixed-0-87: New Hampshire 0 4 9 1 mixed 0.87
fid-record fid.divorce.state.new-jersey-2-1-10-1-mixed-1-03: New Jersey 2 1 10 1 mixed 1.03
fid-record fid.divorce.state.new-mexico-0-3-3-8-mixed-0-83: New Mexico 0 3 3 8 mixed 0.83
fid-record fid.divorce.state.new-york-2-4-7-1-mixed-0-95: New York 2 4 7 1 mixed 0.95
fid-record fid.divorce.state.north-carolina-0-5-8-1-mixed-0-91: North Carolina 0 5 8 1 mixed 0.91
fid-record fid.divorce.state.north-dakota-0-1-12-1-inside-0-90: North Dakota 0 1 12 1 inside 0.90
fid-record fid.divorce.state.ohio-0-11-2-1-below-0-88: Ohio 0 11 2 1 below 0.88
fid-record fid.divorce.state.oklahoma-0-4-9-1-mixed-0-95: Oklahoma 0 4 9 1 mixed 0.95
fid-record fid.divorce.state.oregon-0-8-5-1-mixed-0-79: Oregon 0 8 5 1 mixed 0.79
fid-record fid.divorce.state.pennsylvania-0-9-4-1-mixed-0-87: Pennsylvania 0 9 4 1 mixed 0.87
fid-record fid.divorce.state.rhode-island-3-0-10-1-mixed-0-92: Rhode Island 3 0 10 1 mixed 0.92
fid-record fid.divorce.state.south-carolina-0-11-2-1-below-0-78: South Carolina 0 11 2 1 below 0.78
fid-record fid.divorce.state.south-dakota-0-1-12-1-inside-0-88: South Dakota 0 1 12 1 inside 0.88
fid-record fid.divorce.state.tennessee-0-7-6-1-mixed-0-90: Tennessee 0 7 6 1 mixed 0.90
fid-record fid.divorce.state.texas-0-13-0-1-below-0-67: Texas 0 13 0 1 below 0.67
fid-record fid.divorce.state.utah-1-4-8-1-mixed-0-94: Utah 1 4 8 1 mixed 0.94
fid-record fid.divorce.state.vermont-0-0-13-1-inside-1-08: Vermont 0 0 13 1 inside 1.08
fid-record fid.divorce.state.virginia-1-5-7-1-mixed-0-91: Virginia 1 5 7 1 mixed 0.91
fid-record fid.divorce.state.washington-0-7-6-1-mixed-0-89: Washington 0 7 6 1 mixed 0.89
fid-record fid.divorce.state.west-virginia-0-1-12-1-inside-0-90: West Virginia 0 1 12 1 inside 0.90
fid-record fid.divorce.state.wisconsin-0-7-6-1-mixed-0-88: Wisconsin 0 7 6 1 mixed 0.88
fid-record fid.divorce.state.wyoming-1-2-10-1-mixed-1-00: Wyoming 1 2 10 1 mixed 1.00
fid-record fid.divorce.gapbelow.texas-2021-40-107-89-864-7-413-49-757: Texas 2021 40,107 89,864 7,413 49,757
fid-record fid.divorce.gapbelow.texas-2019-61-350-99-315-6-796-37-965: Texas 2019 61,350 99,315 6,796 37,965
fid-record fid.divorce.gapbelow.texas-2011-82-569-119-973-7-584-37-404: Texas 2011 82,569 119,973 7,584 37,404
fid-record fid.divorce.gapbelow.texas-2014-72-785-108-770-6-050-35-985: Texas 2014 72,785 108,770 6,050 35,985
fid-record fid.divorce.gapbelow.texas-2015-71-123-106-445-5-418-35-322: Texas 2015 71,123 106,445 5,418 35,322
fid-record fid.divorce.gapbelow.texas-2012-78-853-113-421-6-010-34-568: Texas 2012 78,853 113,421 6,010 34,568
fid-record fid.divorce.gapabove.new-york-2018-54-329-47-864-4-178-6-465: New York 2018 54,329 47,864 4,178 -6,465
fid-record fid.divorce.gapabove.new-york-2019-56-270-51-468-3-344-4-802: New York 2019 56,270 51,468 3,344 -4,802
fid-record fid.divorce.gapabove.new-jersey-2014-24-837-20-600-1-874-4-237: New Jersey 2014 24,837 20,600 1,874 -4,237
fid-record fid.divorce.gapabove.nevada-2021-13-198-9-787-1-680-3-411: Nevada 2021 13,198 9,787 1,680 -3,411
fid-record fid.divorce.gapabove.nevada-2013-14-290-10-890-1-920-3-400: Nevada 2013 14,290 10,890 1,920 -3,400
fid-record fid.divorce.gapabove.nevada-2014-15-133-11-885-1-674-3-248: Nevada 2014 15,133 11,885 1,674 -3,248
fid-record fid.marriage.all.all-jurisdictions-95-313-253-53-mixed: All jurisdictions 95 313 253 53 mixed
fid-record fid.marriage.all.without-destination-states-69-313-253-51-mixed: Without destination states 69 313 253 51 mixed
fid-record fid.marriage.all.destination-states-only-26-0-0-2-above: Destination states only 26 0 0 2 above
fid-record fid.marriage.sex.nchs-above-95-95-81: NCHS above 95 95 81
fid-record fid.marriage.sex.nchs-below-313-332-294: NCHS below 313 332 294
fid-record fid.marriage.sex.nchs-inside-253-234-201: NCHS inside 253 234 201
fid-record fid.marriage.year.2010-9-23-19-0-mixed: 2010 9 23 19 0 mixed
fid-record fid.marriage.year.2011-9-18-24-0-mixed: 2011 9 18 24 0 mixed
fid-record fid.marriage.year.2012-8-24-19-0-mixed: 2012 8 24 19 0 mixed
fid-record fid.marriage.year.2013-9-22-19-1-mixed: 2013 9 22 19 1 mixed
fid-record fid.marriage.year.2014-7-21-22-1-mixed: 2014 7 21 22 1 mixed
fid-record fid.marriage.year.2015-6-26-19-0-mixed: 2015 6 26 19 0 mixed
fid-record fid.marriage.year.2016-6-25-20-0-mixed: 2016 6 25 20 0 mixed
fid-record fid.marriage.year.2017-8-24-19-0-mixed: 2017 8 24 19 0 mixed
fid-record fid.marriage.year.2018-8-22-21-0-mixed: 2018 8 22 21 0 mixed
fid-record fid.marriage.year.2019-7-28-16-0-mixed: 2019 7 28 16 0 mixed
fid-record fid.marriage.year.2021-8-21-22-0-mixed: 2021 8 21 22 0 mixed
fid-record fid.marriage.year.2022-6-28-17-0-mixed: 2022 6 28 17 0 mixed
fid-record fid.marriage.year.2023-4-31-16-0-mixed: 2023 4 31 16 0 mixed
fid-record fid.marriage.year.2024-0-0-0-51-cannot-tell: 2024 0 0 0 51 cannot tell
fid-record fid.marriage.state.alabama-2-0-11-1-inside-1-05: Alabama 2 0 11 1 inside 1.05
fid-record fid.marriage.state.alaska-0-8-5-1-mixed-0-74: Alaska 0 8 5 1 mixed 0.74
fid-record fid.marriage.state.arizona-0-13-0-1-below-0-83: Arizona 0 13 0 1 below 0.83
fid-record fid.marriage.state.arkansas-10-0-3-1-mixed-1-20: Arkansas 10 0 3 1 mixed 1.20
fid-record fid.marriage.state.california-0-11-2-1-below-0-92: California 0 11 2 1 below 0.92
fid-record fid.marriage.state.colorado-0-11-2-1-below-0-84: Colorado 0 11 2 1 below 0.84
fid-record fid.marriage.state.connecticut-0-3-10-1-mixed-0-94: Connecticut 0 3 10 1 mixed 0.94
fid-record fid.marriage.state.delaware-0-4-9-1-mixed-0-83: Delaware 0 4 9 1 mixed 0.83
fid-record fid.marriage.state.district-of-columbia-2-1-10-1-mixed-0-88: District of Columbia 2 1 10 1 mixed 0.88
fid-record fid.marriage.state.florida-12-0-1-1-above-1-16: Florida 12 0 1 1 above 1.16
fid-record fid.marriage.state.georgia-0-8-3-3-mixed-0-86: Georgia 0 8 3 3 mixed 0.86
fid-record fid.marriage.state.hawaii-13-0-0-1-above-2-11: Hawaii 13 0 0 1 above 2.11
fid-record fid.marriage.state.idaho-0-0-13-1-inside-0-99: Idaho 0 0 13 1 inside 0.99
fid-record fid.marriage.state.illinois-0-9-4-1-mixed-0-90: Illinois 0 9 4 1 mixed 0.90
fid-record fid.marriage.state.indiana-0-11-2-1-below-0-88: Indiana 0 11 2 1 below 0.88
fid-record fid.marriage.state.iowa-0-8-5-1-mixed-0-86: Iowa 0 8 5 1 mixed 0.86
fid-record fid.marriage.state.kansas-0-13-0-1-below-0-76: Kansas 0 13 0 1 below 0.76
fid-record fid.marriage.state.kentucky-0-7-6-1-mixed-0-91: Kentucky 0 7 6 1 mixed 0.91
fid-record fid.marriage.state.louisiana-0-6-7-1-mixed-0-93: Louisiana 0 6 7 1 mixed 0.93
fid-record fid.marriage.state.maine-5-1-7-1-mixed-1-12: Maine 5 1 7 1 mixed 1.12
fid-record fid.marriage.state.maryland-0-8-5-1-mixed-0-85: Maryland 0 8 5 1 mixed 0.85
fid-record fid.marriage.state.massachusetts-0-11-2-1-below-0-90: Massachusetts 0 11 2 1 below 0.90
fid-record fid.marriage.state.michigan-0-9-4-1-mixed-0-87: Michigan 0 9 4 1 mixed 0.87
fid-record fid.marriage.state.minnesota-0-13-0-1-below-0-80: Minnesota 0 13 0 1 below 0.80
fid-record fid.marriage.state.mississippi-0-6-7-1-mixed-0-90: Mississippi 0 6 7 1 mixed 0.90
fid-record fid.marriage.state.missouri-0-9-4-1-mixed-0-86: Missouri 0 9 4 1 mixed 0.86
fid-record fid.marriage.state.montana-4-0-9-1-mixed-1-11: Montana 4 0 9 1 mixed 1.11
fid-record fid.marriage.state.nebraska-0-7-6-1-mixed-0-86: Nebraska 0 7 6 1 mixed 0.86
fid-record fid.marriage.state.nevada-13-0-0-1-above-3-81: Nevada 13 0 0 1 above 3.81
fid-record fid.marriage.state.new-hampshire-1-0-12-1-inside-1-04: New Hampshire 1 0 12 1 inside 1.04
fid-record fid.marriage.state.new-jersey-0-7-6-1-mixed-0-92: New Jersey 0 7 6 1 mixed 0.92
fid-record fid.marriage.state.new-mexico-3-0-10-1-mixed-1-00: New Mexico 3 0 10 1 mixed 1.00
fid-record fid.marriage.state.new-york-10-0-3-1-mixed-1-12: New York 10 0 3 1 mixed 1.12
fid-record fid.marriage.state.north-carolina-0-8-5-1-mixed-0-93: North Carolina 0 8 5 1 mixed 0.93
fid-record fid.marriage.state.north-dakota-0-9-4-1-mixed-0-70: North Dakota 0 9 4 1 mixed 0.70
fid-record fid.marriage.state.ohio-0-13-0-1-below-0-88: Ohio 0 13 0 1 below 0.88
fid-record fid.marriage.state.oklahoma-0-12-1-1-below-0-81: Oklahoma 0 12 1 1 below 0.81
fid-record fid.marriage.state.oregon-0-7-6-1-mixed-0-90: Oregon 0 7 6 1 mixed 0.90
fid-record fid.marriage.state.pennsylvania-0-11-2-1-below-0-88: Pennsylvania 0 11 2 1 below 0.88
fid-record fid.marriage.state.rhode-island-2-0-11-1-inside-1-10: Rhode Island 2 0 11 1 inside 1.10
fid-record fid.marriage.state.south-carolina-2-2-9-1-mixed-1-05: South Carolina 2 2 9 1 mixed 1.05
fid-record fid.marriage.state.south-dakota-0-2-11-1-inside-0-91: South Dakota 0 2 11 1 inside 0.91
fid-record fid.marriage.state.tennessee-6-1-6-1-mixed-1-07: Tennessee 6 1 6 1 mixed 1.07
fid-record fid.marriage.state.texas-0-13-0-1-below-0-89: Texas 0 13 0 1 below 0.89
fid-record fid.marriage.state.utah-2-8-3-1-mixed-0-88: Utah 2 8 3 1 mixed 0.88
fid-record fid.marriage.state.vermont-8-0-5-1-mixed-1-26: Vermont 8 0 5 1 mixed 1.26
fid-record fid.marriage.state.virginia-0-12-1-1-below-0-89: Virginia 0 12 1 1 below 0.89
fid-record fid.marriage.state.washington-0-13-0-1-below-0-80: Washington 0 13 0 1 below 0.80
fid-record fid.marriage.state.west-virginia-0-2-11-1-inside-0-94: West Virginia 0 2 11 1 inside 0.94
fid-record fid.marriage.state.wisconsin-0-12-1-1-below-0-84: Wisconsin 0 12 1 1 below 0.84
fid-record fid.marriage.state.wyoming-0-4-9-1-mixed-0-80: Wyoming 0 4 9 1 mixed 0.80
fid-record fid.marriage.gapbelow.texas-2019-141-149-210-648-10-819-69-499: Texas 2019 141,149 210,648 10,819 69,499
fid-record fid.marriage.gapbelow.texas-2023-178-055-233-654-8-435-55-599: Texas 2023 178,055 233,654 8,435 55,599
fid-record fid.marriage.gapbelow.texas-2022-174-424-229-790-10-804-55-366: Texas 2022 174,424 229,790 10,804 55,366
fid-record fid.marriage.gapbelow.california-2023-215-199-256-586-8-179-41-387: California 2023 215,199 256,586 8,179 41,387
fid-record fid.marriage.gapbelow.california-2022-223-006-254-338-8-005-31-332: California 2022 223,006 254,338 8,005 31,332
fid-record fid.marriage.gapbelow.texas-2018-175-698-206-508-7-909-30-810: Texas 2018 175,698 206,508 7,909 30,810
fid-record fid.marriage.gapabove.nevada-2011-100-529-17-963-2-623-82-566: Nevada 2011 100,529 17,963 2,623 -82,566
fid-record fid.marriage.gapabove.nevada-2010-103-314-21-466-2-623-81-848: Nevada 2010 103,314 21,466 2,623 -81,848
fid-record fid.marriage.gapabove.nevada-2012-96-896-23-158-2-615-73-738: Nevada 2012 96,896 23,158 2,615 -73,738
fid-record fid.marriage.gapabove.nevada-2013-90-066-20-913-2-524-69-153: Nevada 2013 90,066 20,913 2,524 -69,153
fid-record fid.marriage.gapabove.nevada-2015-89-668-22-691-2-319-66-977: Nevada 2015 89,668 22,691 2,319 -66,977
fid-record fid.marriage.gapabove.nevada-2014-90-428-24-277-2-925-66-151: Nevada 2014 90,428 24,277 2,925 -66,151
fid-record fid.headline: 13 of 13 In Texas the CDC count of divorces and annulments sits below the ACS interval in 13 of 13 years, under the women's estimate and under the men's. Georgia, Illinois and Louisiana read below under both sexes as well. These are the jurisdictions where the divorce reading holds whichever sex is used. It says only that the two counts differ by more than the survey's stated margin. It cannot show that any records are missing or that either source is mistaken. Nationally in 2022 the CDC divorce total was 0.80 of the ACS women's total and 0.89 of the men's, so a state reads against that ratio and not against 1.0.
fid-record fid.line.divorce: Divorces and annulments: of 714 rows, 593 are scored. Under the women's estimate, the scored reading, the NCHS count sits above the ACS interval in 25, below it in 265 and inside it in 303. Under the men's estimate it sits above in 78, below in 140 and inside in 375. Both sexes read below in 111 rows, inside in 225 and above in 11. Cannot tell holds 121 (69 state does not report, 51 no stated count, 1 no ACS interval). Without the destination cells the women's reading is 19 above, 265 below and 296 inside.
fid-record fid.line.marriage: Marriages: of 714 rows, 661 are scored. Under the women's estimate, the scored reading, the NCHS count sits above the ACS interval in 95, below it in 313 and inside it in 253. Under the men's estimate it sits above in 95, below in 332 and inside in 234. Both sexes read below in 294 rows, inside in 201 and above in 81. Cannot tell holds 53 (51 no stated count, 2 state does not report). Without the destination cells the women's reading is 69 above, 313 below and 253 inside.
fid-record fid.scored: The women's reading is the scored one and was fixed in the plan before the comparison. The men's counts are shown beside it. For divorces the count below falls from 265 under the women's estimate to 140 under the men's, so the divorce reading depends on which sex is used and the both-sexes line is the part that does not. Marriages move far less, with 313 below under the women's estimate and 332 under the men's.
fid-record fid.holdone: Massachusetts, Iowa and Kansas hold under one sex and not the other. Their divorce counts sit below the women's interval in 13 of 13, 12 of 13 and 12 of 13 of their scored years and below the men's in 4, 9 and 9, so they read below under the women's estimate and not under the men's.
fid-record fid.baseline: In 2022 the NCHS total for the reporting states was 0.80 of the ACS women's total and 0.89 of the men's for divorces, and 0.89 of the women's and 0.85 of the men's for marriages.
fid-record fid.blanks: The blanks in the frame years are California in all frame years, Hawaii in all frame years, Indiana in all frame years, Minnesota in all frame years, Georgia 2010 to 2016, Louisiana 2010 to 2012 and New Mexico 2016 to 2023. Georgia has no marriage count for 2013 and 2014.
fid-record fid.sexsplit: counted apart as sex splits: 246 divorce rows and 85 marriage rows
fid-record fid.scout: A scout of 16 state-year-events had already shown the women's and the men's estimates for Texas, Florida, New York and Pennsylvania, and the plan lists them.
fid-record fid.tolerance: The reader gate's rate tolerance first ran at 0.15 and was reset to the plan's 0.1
fid-record fid.destination: For marriages these destination rows are 26 above and 0 inside or below, and for divorces 6 above and 7 inside. Every other state has some of the same crossing, so the other rows are not free of it. Florida, New York and Arkansas marriages also read above in most scored years (12 of 13, 10 of 13 and 10 of 13), so the destination states are not the only rows above.
fid-record fid.louisiana: The Louisiana divorce count NCHS prints falls from 9,995 in 2021 to 3,393 in 2022 and 4,120 in 2023, and the printed rate falls with it. The Georgia count falls from 36,464 in 2017 to 26,327 in 2018. NCHS prints these counts, so the rows stay scored as printed and none is re-read.
fid-record fid.swap: In 12 divorce state-years of 2016 and 2017 the NCHS count table and the NCHS rate table do not agree to within 0.1 per 1,000 (Illinois 2016, Iowa 2016, Kansas 2016, Maine 2016, Maryland 2016, Massachusetts 2016, Texas 2016, Iowa 2017, Kansas 2017, Louisiana 2017, Maine 2017, Maryland 2017). The counts for Iowa, Kansas, Louisiana, Maine, Maryland and Massachusetts fit both years' printed rates when the 2016 and 2017 counts are swapped. Texas 2016 also differs, and NCHS footnotes the Texas 2016 divorce rate as revised. Illinois 2016 differs as well and is not footnoted for divorces. Every outcome here is read from the count table as printed. Under the swap 3 rows would change reading: Kansas 2017 from inside to below, Maine 2017 from inside to below and Massachusetts 2016 from below to inside. No row has been re-read.
fid-record fid.ratecheck: within 0.1 in 1,183 of 1,242 state-years. The 59 that miss
fid-record fid.join: in 1,020 of 1,020 values for 2022 and 2023
fid-record fid.texas.divorce: Texas, ACS women against the NCHS count: 2021: NCHS 40,107, ACS 89,864, below, 2022: NCHS 56,269, ACS 89,194, below, 2023: NCHS 62,796, ACS 94,986, below.
fid-record fid.texas.marriage: Texas, ACS women against the NCHS count: 2021: NCHS 170,486, ACS 198,733, below, 2022: NCHS 174,424, ACS 229,790, below, 2023: NCHS 178,055, ACS 233,654, below.

## 2026-11-12 10:30 Faults and Guards 2.0 migration of the FIDELITY reasons and counts (PLAN_ADDENDUM_std2.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md and data/plan_seal.json are untouched, the plan hash still matches the seal and the addendum is a new file committed as 46b6b68 before the re-run
- II: n/a: no repeated item and no gap is netted, every row keeps its own outcome and all 1,428 rows were compared before and after the rewrite with outcome and every number equal
- III: holds: ABOVE and BELOW stay separate and every non-reason number of summary_fidelity.json equals the backup summary_fidelity.json.bak-20261112-std2 in every cell, the run date, the seal and the snapshot count were kept as they were by the std2 rewrite flag
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before the rewrite, a row is an exact read of a published count inside a published interval (owner decision O1, K.read_exact, edges inside), the ACS 90 percent margin as published is unchanged and the 95 percent scale and the men's estimate still score nothing
- VI: holds: four outcomes kept, 25 ABOVE 265 BELOW 303 CONSISTENT 121 CANNOT_TELL for divorces unchanged and every cannot tell row now carries NO_INTERVAL_FORMABLE, no share is read so no point figure or both-alternatives test applies
- R: holds: counts are read from summary_fidelity.json and data/fidelity.json rewritten offline from the same raw files with all four gates passed, REQ-13 of the Texas divorce rows reads 0 NOTHING_RETURNED and 1 of 14 CANNOT_TELL
- P1: holds: the NCHS quotations on the page are untouched by this change
- P2: n/a: no new figure is added, every number keeps its label and table
- P3: n/a: no setting label of any source is touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a cannot tell carries and that a row is an exact read
- P5: holds: the margin is still ACS's published one and the page says an exact row read carries no sampling of its own
- P6: holds: the headline sentence is the same as before plus the REQ-13 line, no stronger than the reading, and the jurisdiction labels stay plain summaries
- P7: holds: the 9 changed fid rows are updated with their new source.grep and surface text in one locked pass through ledger.py, the 6 reason texts keep their old ids, the new fid-record lines are in this entry, nothing is deployed from here
- P8: cannot tell: fidelity.html was rebuilt and lint_copy.py reports 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences, no semicolons in the added text, no digit in any heading, lint_copy.py 0 hits
- P10: holds: the addendum is dated 12 Nov 2026 and committed before the rewrite, and no outcome was changed by the migration
fid-record fid.divorce.year.2024-0-0-0-51-cannot-tell: 2024 0 0 0 51 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.divorce.state.california-0-0-0-14-cannot-tell: California 0 0 0 14 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.divorce.state.hawaii-0-0-0-14-cannot-tell: Hawaii 0 0 0 14 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.divorce.state.indiana-0-0-0-14-cannot-tell: Indiana 0 0 0 14 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.divorce.state.minnesota-0-0-0-14-cannot-tell: Minnesota 0 0 0 14 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.marriage.year.2024-0-0-0-51-cannot-tell: 2024 0 0 0 51 cannot tell (NO_INTERVAL_FORMABLE)
fid-record fid.headline: 13 of 13 In Texas the CDC count of divorces and annulments sits below the ACS interval in 13 of 13 years, under the women's estimate and under the men's. Georgia, Illinois and Louisiana read below under both sexes as well. These are the jurisdictions where the divorce reading holds whichever sex is used. It says only that the two counts differ by more than the survey's stated margin. It cannot show that any records are missing or that either source is mistaken. Nationally in 2022 the CDC divorce total was 0.80 of the ACS women's total and 0.89 of the men's, so a state reads against that ratio and not against 1.0. For the Texas rows, 0 NOTHING_RETURNED. CANNOT_TELL 1 of 14 (1 NO_INTERVAL_FORMABLE).
fid-record fid.line.divorce: Divorces and annulments: of 714 rows, 593 are scored. Under the women's estimate, the scored reading, the NCHS count sits above the ACS interval in 25, below it in 265 and inside it in 303. Under the men's estimate it sits above in 78, below in 140 and inside in 375. Both sexes read below in 111 rows, inside in 225 and above in 11. Cannot tell holds 121, 121 NO_INTERVAL_FORMABLE (69 state does not report, 51 no stated count, 1 no ACS interval). Without the destination cells the women's reading is 19 above, 265 below and 296 inside.
fid-record fid.line.marriage: Marriages: of 714 rows, 661 are scored. Under the women's estimate, the scored reading, the NCHS count sits above the ACS interval in 95, below it in 313 and inside it in 253. Under the men's estimate it sits above in 95, below in 332 and inside in 234. Both sexes read below in 294 rows, inside in 201 and above in 81. Cannot tell holds 53, 53 NO_INTERVAL_FORMABLE (51 no stated count, 2 state does not report). Without the destination cells the women's reading is 69 above, 313 below and 253 inside.
