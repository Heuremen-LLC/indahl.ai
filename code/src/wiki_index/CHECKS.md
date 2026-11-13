
## 2026-11-09 22:16 WIKI desk first reading: Section 1 cited figures against World Bank and UIS releases; Section 2 Foundation figures against the Analytics API and DSA tables
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 49250d0 (21:53 EST 9 Nov) and addendum 9dd1754 before any cited value met a source value; the scout's earlier proof readings are disclosed in the plan. The frame is decided by the reference (stated in World Bank or UIS, or a source link naming the series), never by the outcome. The gate's drops are counted by reason per group (deprecated 1, no point in time 4, more than one point in time 36, reference naming another series 0, unit 0) and none are scored. Fixed on the page: the all-figures row mixes the World Bank's 142-release history with UIS's two-year API history (5,069 of its 5,093 no-release figures are UIS), and a note now says so beside the row.
- II: holds: every figure gets its own bin and its own size outcome. Nothing is netted. Above and below are counted apart in every group. Repeat floor: two reads of the same 29 World Bank releases (ours and the scout's) agree value for value, so the read floor is zero disagreements. Ten seeded figures read again through the query service and the single-country source call: 10 of 10 agree. All 218 listed rows read again the same way before listing.
- III: holds: the gap column is signed (cited minus current over current). The median gap is labelled absolute. In Section 2 the orientation is stated (the stated band relative to the delivered values) and above and below are never folded.
- V: holds: two intervals side by side on every share, Wilson 95% over figures and a 95% interval from resampling countries (2,000 draws, seed 7), because the figures of one country share an import. Section 2 runs the monthly-range ruler and the 12-month-mean ruler side by side.
- VI: holds: ABOVE, BELOW, CONSISTENT, CANNOT_TELL in both sections. The size reading tests zero against the size that matters (1 percent): within 1 percent is printed as a bound. Section 2 definitions that disagree give CANNOT_TELL. Volunteers are CANNOT_TELL by rule with both bounds printed. The DSA rounding count is printed with no fifth label.
- R: holds: every count on the page is rendered from data/wiki_live.json, which is built from the raw API responses kept under data/raw with their read times; release names come from the World Bank and UIS version lists; capture dates from the Wayback index. Readings not in the plan (code aliases, the volunteers placement against the bounds) say defined after the data on the page and in Note 1.
- P1: holds: each stated figure is the regex match on the text of the page as read on 10 Nov 2026, HTML kept with its SHA-256. The DSA rounding sentence is quoted from the wikitext.
- P2: holds: each listed row links the Wikidata statement, the source's current record and the archived release; each stated figure links its page and the Wayback captures; sources and licences are listed with links.
- P3: holds: series codes are named as the sources name them (SP.POP.TOTL, NY.GDP.MKTP.CD, SI.POV.GINI, SL.UEM.TOTL.ZS, UIS SP.DYN.LE00.IN and SP.DYN.TFRT.IN); release labels are the World Bank's own (2019 Apr).
- P4: fixed: the draft said a figure matching an older release 'is a copy of that release', which asserts provenance from a match; it now says the figure carries that release's value. No cause is named for any gap: revisions are described as the source's figure for that year changing between releases, which the releases themselves show. No sentence characterises Wikidata editors.
- P5: holds: every interval cell says Wilson 95% or countries 95%, and the note says what each is.
- P6: holds: the headline says population figures match a World Bank release at the precision they are written in, which is what the bins show; it does not say they are correct or wrong.
- P7: n/a: Bones writes the ledger and ships through ship.sh. This agent published nothing; summary_wiki.json is the source for the ledger rows.
- P8: cannot tell: the draft was rendered locally against the site's CSS and fonts; the live scripts and the /wiki route are not served until Bones places the page.
- P9: holds: lint_copy.py over the visible text: no semicolons, no AI statements, no counts in headings, no 'by hand', no 'apparatus', no judgement words.
- P10: holds: the alias reading and the volunteers placement are labelled defined after the data on the page and in PLAN Note 1.
- O1: n/a: no rider or timer installed by this agent (instruction). wiki_tick.py is rerunnable by hand or from the tick bus; registration is Bones's call.
- O2: holds: a failed known-good prints FAILED and turns every outcome to CANNOT_TELL with the original kept; failed requests are logged in data/raw/http.log and retried after Retry-After.
- O3: n/a: this desk uses no GPU, only HTTP reads and Python scoring.
- O4: fixed: a pgrep liveness check matched the watcher's own command line; liveness is now read from data/state.json step completion times (logged with tp_score).
- O5: holds: the script resolves every path from its own directory; the venv python is named in the docstring and the plan.
- O6: n/a: this desk uses no GPU, only HTTP reads and Python scoring.

## 2026-11-10 00:01 WIKI desk after the outside referee (FIX THEN SHIP): B1 annual report counts at three moments, B2 page count, F1 to F9 and notes, plan note 2
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: fixed: the annual report counts were read today, 16 months after the report's year, and the moment reversed their outcome (referee B1). They are now read at three moments from the Commons statistics table's revisions in force then, defined after the data in plan note 2.1, and the three count rows are CANNOT_TELL. The UIS rows now say they cite UIS.Stat (pre-API) and that their non-matching figures equal World Bank releases (referee F2), so they no longer sit unexplained beside World Bank rows read against 142 releases.
- II: fixed: no chance floor existed for a release match (referee F3). Wrong-year tries now give that floor per figure: population 0.1%, GDP under 0.1%, life expectancy 0.2%, fertility 4.2%, Gini 8.0%, unemployment 43.8% (61% for whole percents), printed for unemployment and labelled defined after the data. Each figure still gets its own bin, nothing is netted, and above and below stay apart.
- III: fixed: the median column now says absolute, as the earlier block claimed it did (referee F4). Signed gaps stay in the gap column. The Section 2 orientation (the stated band relative to the delivered values) is unchanged.
- V: fixed: the page now names the matching ruler exactly, half a written unit, at least three significant digits, plus about 6 in 100 million of the release value, and prints the GDP sensitivity to that term (395 bins, 357 cut decimals, 38 small revisions, half-unit bins 421/624/360/2). The size interval now follows the plan with no 2^-24 widening (three outcomes changed). Two intervals still sit beside every share.
- VI: holds: four outcomes throughout. Disagreeing candidates give CANNOT_TELL, now including the three moments for the report counts. Volunteers stay CANNOT_TELL by rule, each placed against its own scope and window. The views outcome uses the scope the figures name, and the all-projects rows are shown for reference.
- R: holds: every page number is rendered from data/wiki_live.json. B2 was a page counting bug (a prefix test), now fixed: 2,303 of 2,320 and 2,749 of 2,749. The moment counts carry their table revision ids and times. The referee's own scripts were rerun from a scratch copy against the same raw files, and the comparison is in the report. Readings added after the data say so on the page and in note 2.
- P1: fixed: 'numbering more than 250,000' is now its full sentence. The homepage article sentence is quoted to its end. Figure cards (9 of 16 quotes join a lead-in, a number and a caption) are labelled as such. The languages row quotes '300+ languages' alone.
- P2: fixed: the data feed /wiki/live.json is linked in the text. Moment readings link the statistics table revisions. UIS listing rows link the World Bank release their value equals.
- P3: holds: series codes, release labels and UIS version ids are as the sources write them. The statistics table is named by its page title and revision id.
- P4: fixed: the Finland closing line that read as a hint is replaced by the DSA page's own revision (2,961,000 to 2,960,000, 15 January 2026) and its note on that column. No cause is named for any gap. No sentence characterises Wikidata editors or the Foundation.
- P5: holds: every share says Wilson 95% or countries 95%. Delivered ranges say monthly low to high. Bounds say monthly mean.
- P6: holds: the headline now scopes itself to countries and territories (referee F7) and says match at the written precision, nothing stronger.
- P7: n/a: Bones writes the ledger and ships through ship.sh. Nothing was published or pushed. summary_wiki.json is the source for the ledger rows.
- P8: cannot tell: the draft rendered locally against the site's CSS and fonts at 1280 and 390 pixels (no horizontal page scroll). The live scripts, the /wiki route and /wiki/live.json are not served until Bones places them.
- P9: holds: no semicolons, no AI statements, no counts in headings, no 'by hand', no 'apparatus'. lint_copy.py prints 14 review prompts and exits 1, none a breach (12 for 'editor' inside definition names and counts, 2 for 'because' in method sentences). The earlier block called this holds without saying so.
- P10: holds: the moments reading, the tolerance sensitivity, the wrong-year floor, the UIS citation counts, the volunteer placement, the alias reading, the whole-percent count, the two UIS value sets and the All-row UIS share are labelled defined after the data.
- O1: n/a: no rider or timer installed by this agent. The steps list now runs s1_score twice, around the planned hand check, and adds s2_moments. Registering a rider is Bones's call.
- O2: holds: a failed known-good prints FAILED and turns outcomes to CANNOT_TELL. A precedence bug in the figure-card check raised on the first offline run and was fixed before any output was written.
- O3: n/a: this desk uses no GPU, only HTTP reads and Python scoring.
- O4: holds: step completion is read from data/state.json and from the files each step writes, not from process lists.
- O5: fixed: one pacer now covers every Wikimedia host at no less than 0.31 s (under 200 a minute), after the first run peaked at 203 in a minute across hosts with steps in parallel (referee N9). Paths stay absolute.
- O6: n/a: this desk uses no GPU, only HTTP reads and Python scoring.

## 2026-11-10 04:50 WIKI ship: ledger rows for the population headline, the GDP and all-figure counts, the UIS equal-to-World-Bank counts and the Section 2 outcomes, page at /wiki under HERMES, feed /wiki/live.json
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no new reading. The page and feed are the referee-cleared reading of 10 Nov 2026 05:04 UTC (commit after FIX THEN SHIP). data/wiki_live.json equals data/shipped_20261110_wiki_live.json byte for byte, summary_wiki.json is frozen as data/shipped_20261110_summary_wiki.json, and build_page.py rerun from the feed gives wiki.html byte for byte
- II: holds: every ledger row is one count or one outcome as the page prints it. Nothing is netted, the above and below counts and the per-bin counts stay apart
- III: holds: the ledger rows carry no signed gap. The page's signed gap column and absolute median are as in the referee pass
- V: holds: both intervals (Wilson 95% over figures, countries 95%) stay beside every share on the page. The ledger rows are counts and outcomes, not shares, so they carry no interval
- VI: holds: Section 2 rows carry the four outcomes as scored (CONSISTENT or CANNOT_TELL here), the population and GDP rows are COUNT rows. No outcome was changed at ship
- R: holds: every ledger value is read from the frozen feed or the frozen summary by an exact grep string, and every snippet is the built page's own text. The reading time 10 Nov 2026 05:04 UTC is on the page
- P1: holds: the Foundation quotes on the ledger snippets are copied from the built page, which quotes the pages as read on 10 Nov 2026
- P2: holds: the page links /wiki/live.json and code/wiki (PLAN.md, wiki_tick.py, build_page.py, lint_copy.py, heuremen_kit.py and a README written for this desk). The page says its numbers come from the 05:04 UTC reading and that the feed can be newer
- P3: holds: series codes, release labels and the statistics table revision ids are as the referee pass left them
- P4: holds: no cause is named on the page or in any ledger claim
- P5: holds: every share on the page names Wilson 95% or countries 95%
- P6: holds: the headline is the build_page.py headline, built with the page from the same reading, so it cannot run ahead of the body. It is not taken from the weekly feed
- P7: cannot tell: ledger rows go in before the page carries the numbers, and the release goes only through ledger/ship.sh. The live check after ship is the next entry
- P8: holds: indahl-ai/build_site.py takes the body and headline block of wiki.html and wraps them with page() (nav, division line, footer, reference code). The menu entry WIKI is under HERMES after LINKROT, the division list line is "Cited figures against their source". The rendered live page is checked in the next entry
- P9: holds: plain sentences, no semicolons, no counts of our own things in headings, no AI statements, we pronouns. lint_copy.py prints the same 14 review prompts as the referee pass, none a breach. The site gate reads the built page
- P10: holds: every reading defined after the data keeps its label from the referee pass
- O1: cannot tell: the rider (every 36 ticks, venv python -I wiki_tick.py --publish --due-days 7, a new reading once the last is 7 days old, a run lock against overlap) is handed to Bones to add to the tick bus. WIKI is added to nodes_repo/drift/targets.json (page wiki, feed wiki/live.json, limit 180 h: 7 days plus three times 36 ticks at 6.5 minutes), to the STACK running table, the LIVE tag list and the API and MCP list
- O2: holds: a failed publish prints publish FAILED, and a failed known-good turns outcomes to CANNOT_TELL with the original kept
- O3: n/a: no GPU used, the desk is HTTP reads and Python scoring on the CPU
- O4: holds: the feed stamp is YYYY-MM-DD HH:MM UTC (the time the reading was scored), the form the drift seat and the LIVE tags parse
- O5: holds: the rider calls the venv python by absolute path, wiki_tick.py puts its own folder on sys.path (so -I is safe), npx by path with PATH set
- O6: n/a: no GPU job, CPU and network only

## 2026-11-10 04:45 WIKI live check after the release (ship.sh, indahl-ai e059c6b7)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: https://indahl.ai/wiki/live.json equals data/wiki_live.json and data/shipped_20261110_wiki_live.json byte for byte (stamp 2026-11-10 05:04 UTC)
- II: holds: every group's rows and four bin counts in summary_wiki.json (six series and the all-figures row) are printed on the live page, above and below kept apart
- III: holds: the live page is byte for byte the built indahl-ai/wiki.html, so the signed gaps and absolute medians are as built from the referee-cleared feed
- V: holds: both intervals stand beside every share on the live page, as built
- VI: holds: the Section 2 outcomes on the live page match the ledger rows (cannot tell for the views, edits and annual report counts read at three moments, consistent for the articles, languages and Commons figures read today)
- R: holds: the live page carries reference code HLC-A27EEF07 and the reading time 10 Nov 2026 05:04 UTC, and copies.py live read drift 0 after the release
- P1: holds: the Foundation quotes on the live page are the built text. Both Section 2 quote sites are now marked span class quote, the text unchanged
- P2: holds: the live page links /wiki/live.json and code/wiki, and the public repository serves PLAN.md, wiki_tick.py, build_page.py, lint_copy.py, heuremen_kit.py and the desk README
- P3: holds: menu entry WIKI under HERMES after LINKROT on every page's dropdown, the HERMES division list line "Cited figures against their source", and the home page HERMES card lists WIKI
- P4: holds: no cause is named on the live page
- P5: holds: every share on the live page says Wilson 95% or countries 95%
- P6: holds: the live headline is the build_page.py headline, 8,936 of 8,967, built with the page from the same reading
- P7: holds: ledger rows went in before the page carried the numbers (16 rows, added then put on the wiki surface after the build), the release went through ledger/ship.sh with every gate at 0 (ledger drift 0, copies drift 0, site gate 0 breaches, source gate 0 fail) and live was read after it
- P8: caught: the site gate's tone scan first read "trusted" inside the Foundation homepage sentence quoted verbatim as a stated figure. The quote was not reworded. Both quote sites are marked span class quote and tone_scan.py ARGUE skips only that span (backup tone_scan.py.bak-20261110-wikiship). The live page renders, the respond link answers 200, and /api/v1/wiki returns the feed
- P9: holds: the site gate read the shipped build with no breach
- P10: holds: the defined-after-the-data labels on the live page are as in the referee pass
- O1: cannot tell: the rider waits for Bones to add it to the tick bus. Drift targets are on Heuremen-LLC/nodes (335d87f5), the STACK running table, the LIVE tag list and the API and MCP list carry wiki
- O2: holds: a failed publish prints publish FAILED, as in the ship entry
- O3: n/a: no GPU used, CPU and network only
- O4: holds: the live stamp 2026-11-10 05:04 UTC is in the form the drift seat and the LIVE tag reader parse
- O5: holds: the KV put ran with the account id and PATH set and npx by path
- O6: n/a: no GPU job, CPU and network only

## 2026-11-12 10:38 Faults and Guards 2.0 migration of the WIKI outcome rule (PLAN_ADDENDUM_std2.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md and its addenda are untouched and the addendum is a new file committed as 3c5fa47 before the rewrite, the sealed releases and the cached raw files are the ones the 10 Nov reading used
- II: holds: the Section 1 size outcome counts for all 17,429 figures equal the 10 Nov reading in every group (4,292 above, 5,695 below, 7,087 within 1 percent, 355 cannot tell for all figures), no gap is netted, and the bins and every share are unchanged apart from float noise of 1.7e-18 in a Wilson lower end
- III: holds: above and below stay separate in every count, the 10 Nov wiki_live.json and the rewrite agree on every number except the outcome and reason fields listed in the addendum, and the reading stamp 2026-11-10 05:04 UTC was kept by the std2 rewrite flag
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before the rewrite, K.read with band minus 1 to plus 1 percent and the same 1 percent as the size that matters, closed edges, no resampling for any outcome, the Wilson and country-resampled intervals on shares stay descriptive
- VI: holds: four outcomes kept, the size cannot tell for all figures is 103 STRADDLES_EDGE, 228 TOO_WIDE_TO_RESOLVE and 24 NO_INTERVAL_FORMABLE, and the both-alternatives test changed no decided row
- R: holds: counts are read from data/wiki_live.json and summary_wiki.json of the offline rewrite with the known-good checks passed, REQ-13 for population reads 15 NOTHING_RETURNED and 2 of 8,952 CANNOT_TELL, all figures 19 NOTHING_RETURNED and 336 of 17,410 CANNOT_TELL
- P1: n/a: no quotation of any source is added or changed by this migration
- P2: n/a: no new figure is added, every number keeps its group label and table
- P3: n/a: no setting label of any source is touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a cannot tell carries and how a floor reads
- P5: holds: the page says the size interval comes from the written precision and the shares keep their two named intervals
- P6: holds: the headline sentence keeps its numbers and adds that its denominator holds the figures the source returned nothing for, then the REQ-13 line, no stronger than the reading
- P7: holds: the 8 wiki.s2 rows are updated with new surface text and a new frozen source data/std2_20261112_summary_wiki.json in one locked pass through ledger.py, three outcomes CONSISTENT to BELOW (floors) and five CANNOT_TELL with reasons, nothing is deployed from here and the published feed stays the 10 Nov reading until the tick bus publishes
- P8: cannot tell: wiki.html was rebuilt from the rewritten feed and lint_copy.py reports the same 14 hits as the 10 Nov page, all read and cleared before, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences, no semicolons in the added text, no digit in any heading, lint_copy.py hits equal the earlier 14
- P10: holds: the addendum is dated 12 Nov 2026 and committed before the rewrite, the three flips follow from the one-sided rule and no rule was tuned after the data
wiki-record wiki.s2.ar_articles: “66 million Wikipedia articles” Stated band 65.5 million to 66.5 million, three moments. Outcome: cannot tell (STRADDLES_EDGE). | source "ar_articles": "CANNOT_TELL"
wiki-record wiki.s2.ar_commons: “135 million freely usable media files on Wikimedia Commons” Stated band 134.5 million to 135.5 million, three moments. Outcome: cannot tell (STRADDLES_EDGE). | source "ar_commons": "CANNOT_TELL"
wiki-record wiki.s2.ar_edits: “324 edits to Wikipedia every minute” Stated band 323.5 to 324.5, July 2024 to June 2025. Outcome: cannot tell (STRADDLES_EDGE). | source "ar_edits": "CANNOT_TELL"
wiki-record wiki.s2.home_articles: Stated band above 67 million, read today. Outcome: below. | source "home_articles": "BELOW"
wiki-record wiki.s2.home_edits: “Every minute 324 new edits are made to Wikipedia.” Stated band 323.5 to 324.5, last 12 months. Outcome: cannot tell (STRADDLES_EDGE). | source "home_edits": "CANNOT_TELL"
wiki-record wiki.s2.home_languages: “300+ languages” Stated band 300 or more, read today. Outcome: below. | source "home_languages": "BELOW"
wiki-record wiki.s2.home_views: “Wikipedia receives nearly 15 billion views each month.” Stated band 13.5 billion to 15 billion, last 12 months. Outcome: cannot tell (STRADDLES_EDGE). | source "home_views": "CANNOT_TELL"
wiki-record wiki.s2.projects_commons: “114 million images, photographs, videos and music files and counting” Stated band 114 million or more, read today. Outcome: below. | source "projects_commons": "BELOW"
