# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## What the error fields are (pinned 11 Nov 2026 before any width entered a reading)

Sales and residential construction (EITS ressales and resconst, fields E_TOTAL, E_SINGLE, E_MULTI, E_UNDERC and so on).
- The release table row is labelled "Average RSE (%)" with the footnote "Average relative standard error for the latest 6-month period". Source: New Residential Sales release of 27 Oct 2026, https://www.census.gov/construction/nrs/pdf/newressales.pdf (footnote 3), and New Residential Construction release of 20 Oct 2026, https://www.census.gov/construction/nrc/pdf/newresconst.pdf (footnote 1).
- Match against the API: the 27 Oct sales release prints Average RSE 8 for the US total and 32, 18, 10 and 16 for the other columns of that table (the regions among them, order as printed). The API served E_TOTAL ASOLD US = 8 for 2026-09 and 8 for 2026-08, with Northeast 33 for 2026-08. The construction release prints Average RSE rows of the same kind (whole numbers such as 5, 8, 12, 17, 29 across its columns) and the API serves E_TOTAL ASTARTS US = 6. That starts column was not matched cell by cell, the sales match was. So E_ is a relative standard error in percent, whole number.
- The release text says "Estimated average relative standard errors of the preliminary data are shown in the tables" (sales) and "Estimated relative standard errors of the most recent data are shown in the tables" (construction). Whether E_ for an old month is the figure printed with that month or a later average is not documented. Hence the label "as served 2026".
- Method note, https://www.census.gov/construction/soc/methodology.html (fetched 11 Nov 2026): "The relative standard error equals the standard error divided by the estimated value to which it refers." The 90 percent interval uses the multiplier 1.645: "this is called a 90-percent confidence interval), multiply 4,000 by 1.645". The page does not mention 1.753.
- Explanatory notes in both releases: "All ranges given for percent changes are 90-percent confidence intervals and account only for sampling variability." Revision policy (same methodology page): sales "Three months of data are revised along with the release of each month's preliminary estimates", starts and completions "two months of data are revised along with the release of each month's preliminary estimates" and "are not revised again after the second revision of each estimate", annual estimates finalized with the release of data for February of the following year. Average revision (releases): sales "revised about 6.7 percent", permits, starts and completions "revised 3.8 percent or less".
- Resolution of the three open meanings: E_ is a relative standard error in percent (not a coefficient of variation of the change, not a 90 percent half-width), the 90 percent interval is 1.645 times it for housing, and the API serves E_ for regions only for sales. For starts and completions only the US cell has E_ (checked in the snapshot of 11 Nov: resconst errors hold geo US only), so regional starts are CANNOT_TELL no width.

Advance monthly retail (EITS marts, E_SM and E_MPCSM).
- https://www.census.gov/retail/marts/how_surveys_are_collected.html: "Standard errors and coefficients of variation (CV) are estimated measures of sampling variation." "The margin of sampling error gives a range about the estimate which is a 90 percent confidence interval." "The resulting confidence interval is the estimated value +/-1.753 x CV x (the estimated monthly total)." The page does not contain 1.645.
- E_SM is the CV of the level in percent (served with one decimal, 0.8 to 1.0 for the US total). E_MPCSM is the standard error of the month to month percent change in points and is not used.
- Same page on the universe: "As of the April 2025 annual revision report, nonemployers are no longer included in the estimates" and "have been removed from the time series to be aligned with the Annual Integrated Economic Survey (AIES)." The page gives no month for the first advance report that carries the change.
- Not pinned: the retail E_SM for an old month is assumed to be the CV for that month's estimate as served now. Not documented either way.

Other series copied by the snapshot job: advm3 (EITS returns no error data for it), vip (E_V served), international trade (imports end-use timed out on the first pull, retried on the next 6 hour pull, exports copied).

## 2026-11-11 07:41 CENSUS desk first read: Census first prints with stated 90 percent widths against second print, third print and current value, sales, starts, completions, permits and retail, 2016 to 2026
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same quantity both sides: ALFRED values of one series, first print against later print of the same month, widths from EITS for that month (PLAN.md af6caae 07:23:14 -05:00, sha256 c07faa25, data/plan_seal.json, first comparison 12:41:15Z). Gate drops counted by series and step in summary_census.json cells. US sales S1: 129 rows, 117 scored, 11 annual revision in window, 1 missing vintage. Regional starts, all permits: no width (counted, 128 or 129 each). Retail S3: 128 universe break. Nothing dropped silently
- II: n/a: a revision is one later value, not a re-read item. Repeat floor is that ALFRED vintages are immutable files and the same vintage was not pulled twice with different values (cache read, one fetch each). No net of flips is claimed
- III: holds: above and below printed apart in every cell, never a net. Over all scored rows 44 above, 4 below, 2621 inside of 2669. Later values leave the interval on the upper side far more often than the lower. Cells agree in sign where they have outside rows (sales regions above only, retail above only). Cannot tell never folded in
- V: holds: ruler is the first print's stated 90 percent half-width from the served relative standard error (1.645) or CV (1.753), against the later value. Second ruler computed and displayed only: served width moved by its own rounding (half a point housing, 0.05 retail). Retail US S1 share 96.5 to 97.4, sales 99.1 to 100. The reading does not flip on it. The reading against 90 percent is our reading, not Census's
- VI: holds: four outcomes kept, both alternatives in PLAN.md. Cells read against 90 percent. US sales S1 117 of 117 (95% Wilson 96.8 to 100.0, ABOVE), starts S1 117 of 117 (ABOVE), completions S1 115 of 117 (ABOVE), retail S1 112 of 115 (ABOVE, 92.6 to 99.1), retail S2 99 of 104 (CONSISTENT, 89.2 to 97.9), sales North S2 97 of 105 (CONSISTENT). Cell intervals are narrower than honest, months overlap, said on the page
- R: holds: counts from summary_census.json and data/census.json of the run at 12:41 plus the later rerun (display only fix). 5031 rows, 2016-01 to 2026-09, 18 snapshot files on 11 Nov, 0 rows with width as printed. Hand read rows: HSN1F vintage 2026-10-27 Sep 676, Aug 680, Sep 2025 714 from the Census sales release of 27 Oct 2026. HOUST vintage 2026-10-20 Sep 1,221, Aug 1,288, Sep 2025 1,319, completions Sep 1,192 Aug 1,166, permits Sep 1,400 Aug 1,403 from the construction release of 20 Oct 2026. All 10 equal the parsed rows. Join gate: 60 of 60 US series-months of the last 12 equal between newest ALFRED vintage and EITS. ALFRED vintage dates match the release dates for those two releases. Not hand read: retail (release text not read), open
- P1: holds: quotes in the section above copied from the fetched Census pages and PDFs (text extracted from the release PDFs of 20 and 27 Oct 2026), URLs given. The page quotes none and paraphrases the definitions
- P2: holds: page names ALFRED series codes, the Census API and the run date, figures live in summary_census.json (cells, rows, gates, snapshots) and data/census.json (every row)
- P3: holds: SA series, thousands SAAR for housing and millions of dollars for retail, ALFRED vintage dates labelled as stand-ins for release dates, width basis column on every cell
- P4: holds: the page says the later value is inside or outside the interval and names no cause for any revision. The retail break paragraph says the plan's rule found the break at 2026-09-28 and that Census documents April 2025, names no cause
- P5: holds: 95 percent Wilson on every share, the stated interval labelled 90 percent with the multiplier, the sensitivity labelled display only, independence caveat printed
- P6: holds: the page reports shares above 90 percent for sales, starts and completions and does not claim Census intervals are too wide. The page says a later revised value is not the quantity the 90 percent is stated for. Width is as served 2026 on all rows, so the reading is about the served width and not the printed one
- P7: n/a: not shipped by this agent. No ledger line, no site edit, no ship.sh. Draft census_revisions.html is git-ignored and goes to the outside referee first
- P8: cannot tell: draft built and tags read in the text dump, it uses /style.css from the site and was not rendered in a browser here
- P9: holds: lint_copy.py on census_revisions.html gives 0 hits. The lint treats the Census terms standard error and sampling error as technical terms and does not count them as the judgement word error, read and cleared here. No semicolons, no digits in headings, no AI statements, we and our reading
- P10: caught: two display fixes after the data and after the first run, labelled here. The sensitivity first moved the retail width by half a point, which is ten times its rounding, and showed 56.5 percent. Fixed to 0.05 for retail. The headline sentence first read inside (above) and now says share above 90 percent. No rule, cell or outcome changed. Also the plan text says starts E_TOTAL for the same geographies, in fact only US has E_ for starts and completions, so regional starts read no width as the plan's rule says. The scout table gave first print 664 for HSN1F 2024-12, a stand-in vintage a month early, the desk's first print is 698 (vintage 2025-01-27, the Census release)
- O1: holds: rider added to watch/tick_bus.py beside the other desk riders, every 60 ticks, census_snap.py, backup tick_bus.py.bak-20261111-census, py_compile passes. Not confirmed running on a live tick yet, the bus was not restarted by this agent. census_tick.py is not on the bus
- O2: holds: a failed fetch is logged in data/snapshots/pull_log.jsonl with its error name (trade imports timed out once) and the run goes on. A failed gate turns every scored outcome into cannot tell and keeps the original
- O3: n/a: no GPU, network reads and arithmetic on the CPU
- O4: holds: summary carries generated time and the snapshot count, data/census_history.jsonl gets one line per run, last_pull.json holds the last pull time
- O5: holds: scripts chdir to their own folder, paths under it, key read from the owner's accounts folder at call time only and stripped from saved URLs. A search of the repo for the key text finds nothing. Standard library only
- O6: n/a: no GPU job runs in this desk

## 2026-11-11 10:29 CENSUS desk ship after the outside referee: referee fixes R-1 to R-6 (copy only), post-data readings computed in code, division page /census, desk page /census/revisions, feed /census/live.json, rider, data pack
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: unchanged from the first read block (07:41, PLAN.md af6caae sealed 07:23:14 -05:00). Rerun of census_tick.py --dry on the same cache gives 0 differences in inside, above, below and cannot tell counts over all 39 cells. The referee recount (census_index_referee/REFEREE.md) also found 0 differences. Nothing dropped silently, drops counted by reason on every cell
- II: n/a: a revision is one later value, not a re-read item. Vintages are immutable files, one fetch each
- III: holds: above and below printed apart in every cell, never netted, cannot tell in its own column. 44 above and 4 below over all scored rows, unchanged
- V: holds: ruler is the stated 90 percent half-width of the first print (1.645 times the relative standard error, 1.753 times the CV times the value). Second rulers displayed and not scored: the rounding of the served width, a width cut to two thirds, a width cut to half
- VI: holds: four outcomes kept, the alternatives in PLAN.md. The reading of the national cells is above 90 percent for sales, starts and completions at the second and third print, and retail second print. Retail third print and Northeast sales third print read consistent. The reading says revisions are small against the stated sampling interval. It does not say the interval is too wide or too narrow and it does not say Census is wrong
- R: holds: counts from summary_census.json of the run at 2026-11-11T15:27:53Z. POST-DATA ADDITIONS after the outside referee, each computed in census_tick.py and labelled on the page as computed after the data, no rule, cell or outcome changed. R-1 retail break paragraph: both vintages named. 2025-04-25 changed 159 months by a median of 1.8 percent and at most 2.2 percent (nonemployers removed, Census April 2025 annual revision). 2026-09-28 changed 140 months by a median of 0.09 percent and at most 4.7 percent (Census notice in the advance retail release of 15 Oct 2026, CB26-165, quoted: Monthly retail sales estimates were revised on September 28, 2026 based on historical corrections and the results of the 2023 and 2024 Annual Integrated Economic Survey). The referee note said at most 4.6 percent over 138 months, the code gives 4.7 percent over 140 changed months and 4.1 percent over the 162 months at least 14 months older than the newest, the page uses the code. The sealed 3 percent rule flags only 2026-09-28. R-2 E_SM: the Census release says For a monthly total, the median estimated coefficient of variation is given (text read from the 15 Oct 2026 release PDF). R-3 sentence that the stated width is sampling error of the level and that inside is not a test of the width: added. R-4 90th percentile of the miss in half-widths per series and step, computed with statistics.quantiles inclusive: sales 0.54 and 0.65, starts 0.40 and 0.49, completions 0.46 and 0.47, retail 0.46 and 0.57. The referee line said the shares stay at or above 90 percent with every half-width cut to about half. THE CODE DOES NOT SHOW THAT: at half the national cells give 75.2 to 94.9 percent inside (sales second print 85.5, third print 75.2, retail third print 85.6). At two thirds of the width every national cell is at or above 90.5 percent. The page states the code. R-5 annual revision rows counted in: retail second print 124 of 128 (92.2 to 98.8, above), third print 118 of 127 (87.1 to 96.2, consistent), national housing cells read the same. R-6 lead now gives completions, the same-release months (September 2025, November 2025 and February 2026, 3 rows per S1 cell for sales, starts and completions) and the counts without them (sales 114 of 114, starts 114 of 114, completions 112 of 114), and the reading column says share above 90
- P1: holds: the page quotes two Census texts verbatim. Notice of revision from the 15 Oct 2026 advance retail release (CB26-165) and the E_SM phrase, both read from the release PDF text and matched here
- P2: holds: every figure says where it lives, the run date, the ALFRED series codes and the Census API, the live feed /census/live.json carries the same summary
- P3: holds: seasonally adjusted series, thousands SAAR for housing, millions of dollars for retail, ALFRED vintage dates labelled as stand-ins for release dates, width basis column on every cell
- P4: holds: no cause named for any revision or gap. The retail revisions section names what Census itself says (nonemployers removed, the annual revision notice) and no cause of our own. lint_copy.py caught my own draft sentence naming a cause (shares read above because the interval is large), removed
- P5: holds: 95 percent Wilson on every share, the Census interval labelled 90 percent with its multiplier, independence caveat printed, the p90 and scaled-width lines labelled described and not scored
- P6: holds: the lead says revisions are small next to the stated sampling interval and that inside is not a test of the stated width. It never says the intervals are validated, too wide or too narrow, and never that Census is wrong
- P7: holds: ledger rows first (ledger/ledger.jsonl, check block here), then build_site.py, then ledger/site_lock.py run with ledger/ship.sh, gates read from the ship output
- P8: holds: page body is taken by indahl-ai/build_site.py from census_index/census_revisions.html, rendered by the site build, checked live after the ship (see the ship report). Required Census API line on the desk page, the division page and the sources line
- P9: holds: lint_copy.py gives 0 hits on census_revisions.html, no semicolons in prose, no digits in headings, no AI statements, we and our, Heuremen LLC. The name CENSUS is the division and never the agency, every page credits the U.S. Census Bureau and ALFRED
- P10: caught: the two referee statements the code did not bear out are listed under R-1 (4.6 over 138 months) and R-4 (halving). Both corrected to the code. The referee note also said the plan states the 3 percent rule was set above the April 2025 move, the plan file is not edited and the page says only that the rule caught the second vintage
- O1: holds: census_tick.py gains --publish (KV census_live, same namespace as the other desks, publish guard: a run without --publish or from the bus does not touch the site KV) and a run lock (.census_tick.lock, exit 0 when held). Rider census_tick.py --pull --publish added to watch/tick_bus.py, every 264 ticks (about a day), backup kept. census_snap.py rider unchanged every 60 ticks
- O2: holds: a failed pull is printed and the run goes on from the cache, a failed gate turns every scored outcome into cannot tell, a failed KV put prints publish FAILED
- O3: n/a: no GPU, network reads and arithmetic on the CPU
- O4: holds: summary carries generated time, data/census_live.json carries updated, data/census_history.jsonl gets one line per run
- O5: holds: paths absolute under the desk folder, PATH set for wrangler, no key text in the repo
- O6: n/a: no GPU job runs in this desk

## 2026-11-11 10:35 CENSUS desk ship record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-11T15:29:48Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-11T15:29:48Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CONSISTENT
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CONSISTENT
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CONSISTENT
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, consistent)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed


## 2026-11-11 16:15 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-11T20:53:41Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-11T20:53:41Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CONSISTENT
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CONSISTENT
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CONSISTENT
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, consistent)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-12 01:52 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-12T06:37:20Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-12T06:37:20Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CONSISTENT
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CONSISTENT
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CONSISTENT
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, consistent)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-12 10:22 Faults and Guards 2.0 migration of the CENSUS cell outcome rule (PLAN_ADDENDUM_std2.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md and data/plan_seal.json are untouched and the plan hash still matches, the addendum is a new file committed as 2e39d96 before the re-run
- II: n/a: no repeated item flipped by a rule of ours, every row keeps its own outcome and the 5,031 rows were compared before and after the re-run with the outcome field equal in each
- III: holds: ABOVE and BELOW stay separate columns and every non-outcome number of summary_census.json equals the backup summary_census.json.bak-20261112-std2 in all 39 cells, only outcome and the new reason and req13 fields differ
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before the re-run, 0.90 is a point figure with no tolerance read with K.read(bound=0.90), the Wilson 95 percent interval is unchanged, no size that matters is invented
- VI: holds: four outcomes kept, the cell cannot tell now carries one reason, 20 ABOVE, 3 STRADDLES_EDGE, 16 NO_INTERVAL_FORMABLE, the both-alternatives test is not applied because the plan names no size and the page and the addendum say so
- R: holds: counts are read from summary_census.json of the offline re-run at 2026-11-12T15:21Z with gates passed, headline REQ-13 reads 0 NOTHING_RETURNED and 50 of 516 CANNOT_TELL all NO_INTERVAL_FORMABLE
- P1: n/a: no quotation of any source is added or changed by this migration
- P2: n/a: no new figure is added, every number already names its series, geography and step in the table and in the ledger rows
- P3: n/a: no setting label of any source is touched by this change
- P4: holds: no cause is named, the added page text says only which closed reason a cannot tell carries and that 90 percent has no tolerance
- P5: holds: every share still carries its 95 percent Wilson interval, the page now says a cell holding 90 percent reads cannot tell with STRADDLES_EDGE and that a row compares one value with one stated interval
- P6: holds: the headline sentence says each national second print cell reads above 90 percent as before and adds the REQ-13 line, no stronger than the reading
- P7: holds: ledger rows census.cell.retail.us.s2, census.cell.sales.northeast.s2 and census.cell.sales.northeast.s3 are set first through ledger.py, refresh_page.py rewrites the remaining surface texts at the next ship, nothing is deployed from here
- P8: cannot tell: census_revisions.html was rebuilt and lint_copy.py reports 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences, no semicolons in the added text, no digit in any heading, lint_copy.py 0 hits
- P10: holds: the addendum is dated 12 Nov 2026 and committed before any reading under the new rule, the three flips are reported as they fall out of the rule and nothing was tuned after the data

## 2026-11-12 11:04 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-12T15:21:02Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-12T15:21:02Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CANNOT_TELL STRADDLES_EDGE
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, straddles)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-12 11:19 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-12T16:17:45Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-12T16:17:45Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CANNOT_TELL STRADDLES_EDGE
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, straddles)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-12 21:19 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-13T01:43:41Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-13T01:43:41Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CANNOT_TELL STRADDLES_EDGE
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, straddles)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-13 08:11 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-13T11:07:49Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-13T11:07:49Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CANNOT_TELL STRADDLES_EDGE
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, straddles)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed

## 2026-11-13 15:58 CENSUS desk refresh record: the cell table and the other printed numbers as shipped (durable source for the census.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_census.json of the run at 2026-11-13T20:52:22Z, the same run census_revisions.html prints, and equals the table row on the page (make_rows.py asserts the 39 rows against the 39 cells)
- II: n/a: no comparison between two runs, a table copied as shipped
- III: holds: above and below are separate columns in every line, cannot tell never in a share
- V: holds: one ruler, the stated 90 percent half-width of the first print, with the outcome against 90 percent read on a 95 percent Wilson interval
- VI: holds: outcomes as the plan states them, the page holds the four outcomes and each cell's cannot tell count beside it
- R: holds: counts from the summary of 2026-11-13T20:52:22Z, no number typed by hand, post-data additions are listed in the entry before this one
- P1: n/a: no quoted text in this record
- P2: holds: each line names series, geography and step, the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged, flipped to live in the ship's own lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
cell-record: cell SALES US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES US S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell STARTS US S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell STARTS US S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell STARTS US S3: 127 of 128 inside, 1 above, 0 below, 1 cannot tell, share 0.9922, interval 0.9571 to 0.9986, ABOVE
cell-record: cell COMPLETIONS US S1: 115 of 117 inside, 1 above, 1 below, 12 cannot tell, share 0.9829, interval 0.9398 to 0.9953, ABOVE
cell-record: cell COMPLETIONS US S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell COMPLETIONS US S3: 124 of 128 inside, 3 above, 1 below, 1 cannot tell, share 0.9688, interval 0.9224 to 0.9878, ABOVE
cell-record: cell RETAIL US S1: 112 of 115 inside, 3 above, 0 below, 14 cannot tell, share 0.9739, interval 0.9261 to 0.9911, ABOVE
cell-record: cell RETAIL US S2: 99 of 104 inside, 5 above, 0 below, 25 cannot tell, share 0.9519, interval 0.8924 to 0.9793, CANNOT_TELL STRADDLES_EDGE
cell-record: cell RETAIL US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell SALES Northeast S1: 113 of 117 inside, 4 above, 0 below, 12 cannot tell, share 0.9658, interval 0.9154 to 0.9866, ABOVE
cell-record: cell SALES Northeast S2: 97 of 105 inside, 8 above, 0 below, 24 cannot tell, share 0.9238, interval 0.8568 to 0.9609, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Northeast S3: 119 of 128 inside, 9 above, 0 below, 1 cannot tell, share 0.9297, interval 0.8718 to 0.9626, CANNOT_TELL STRADDLES_EDGE
cell-record: cell SALES Midwest S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES Midwest S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES Midwest S3: 126 of 128 inside, 2 above, 0 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES South S1: 117 of 117 inside, 0 above, 0 below, 12 cannot tell, share 1.0000, interval 0.9682 to 1.0000, ABOVE
cell-record: cell SALES South S2: 104 of 105 inside, 1 above, 0 below, 24 cannot tell, share 0.9905, interval 0.9480 to 0.9983, ABOVE
cell-record: cell SALES South S3: 126 of 128 inside, 1 above, 1 below, 1 cannot tell, share 0.9844, interval 0.9448 to 0.9957, ABOVE
cell-record: cell SALES West S1: 116 of 117 inside, 1 above, 0 below, 12 cannot tell, share 0.9915, interval 0.9532 to 0.9985, ABOVE
cell-record: cell SALES West S2: 105 of 105 inside, 0 above, 0 below, 24 cannot tell, share 1.0000, interval 0.9647 to 1.0000, ABOVE
cell-record: cell SALES West S3: 125 of 128 inside, 3 above, 0 below, 1 cannot tell, share 0.9766, interval 0.9334 to 0.9920, ABOVE
cell-record: cell STARTS Northeast S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Northeast S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS Midwest S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS South S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell STARTS West S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S1: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S2: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
cell-record: cell PERMITS US S3: 0 of 0 inside, 0 above, 0 below, 129 cannot tell, share 0.0000, interval 0.0000 to 1.0000, CANNOT_TELL NO_INTERVAL_FORMABLE
number-record census.revision.median: new residential sales 3.1 percent of the first print, or 0.22 stated half-widths, housing starts 1.2 percent of the first print, or 0.14 stated half-widths, housing completions 1.5 percent of the first print, or 0.16 stated half-widths, advance retail and food services 0.2 percent of the first print, or 0.19 stated half-widths
number-record census.revision.sensitivity: new residential sales 100.0 to 99.1, housing starts 100.0 to 100.0, housing completions 99.1 to 98.3, advance retail and food services 97.4 to 96.5 percent
number-record census.revision.p90: new residential sales 0.54 and 0.65, housing starts 0.40 and 0.49, housing completions 0.46 and 0.47, advance retail and food services 0.46 and 0.57.
number-record census.revision.scaled: Cutting every stated half-width to two thirds would leave the national cells at 90.5 to 99.1 percent inside. Cutting them to half would take them to 75.2 to 94.9 percent
number-record census.retail.apr2025: It changed 159 months by a median of 1.8 percent and at most 2.2 percent
number-record census.retail.sep2026: It changed 140 months by a median of 0.1 percent and at most 4.7 percent. The sealed rule
number-record census.retail.countedin: Counted in, advance retail would read second print 124 of 128 inside (92.2 to 98.8 percent, above) and third print 118 of 127 inside (87.1 to 96.2 percent, straddles)
number-record census.samerelease: In three months the second print came in the same release as the first (September 2025, November 2025 and February 2026), so those rows show no revision. With them left out, sales read 114 of 114, starts 114 of 114 and completions 112 of 114
number-record census.frame: The frame has 5,031 rows from 2016-01 to 2026-09
number-record census.widths: began on 2026-11-11. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. 0 rows have a width as printed
