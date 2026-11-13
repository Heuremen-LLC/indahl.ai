# Issue 1 checks (draft, 10 Nov 2026, for the Tuesday 17 Nov send)

DRAFT ONLY. Nothing sent, nothing published. The issue is ~/bones-forge/newsletter/issue_1.md.

## Before the real send (open items)

- **The postal address footer is still empty.** newsletter_send.py compose() prints "Heuremen LLC", the reason line, the unsubscribe link and the privacy link, and no postal address. It must be filled before the real send.
- **The web copy does not exist yet.** The email text says "On the web: https://indahl.ai/newsletter/1". Build the page (newsletter_pages.py, through ledger/ship.sh) before sending, or that link is dead.
- **Re-run the recount on the morning of 17 Nov.** Several desks re-read on the tick bus (tornado, quake, flu, steo, seasonal, solar, credit, rank, linkrot). If a headline moves, the issue line moves with its ledger row. Script: /private/tmp/claude-501/-Users-heuremen/ba08385b-5844-4963-b441-21052a55d90b/scratchpad/recount_nl1.py (copy it beside this file if it should be kept). It reads each desk summary, the ledger row and the live page text.
- **Corrections section covers rows through c20261110-90.** Anything logged 11 to 16 Nov is not in it yet.
- Dry run done 10 Nov: `python3 -I newsletter_send.py --edition newsletter/issue_1.md` from ~/bones-forge/indahl-ai. Exit 0. Subject "Heuremen LLC weekly, Issue 1", 0 subscribers, 0 not yet sent, "DRY RUN: nothing sent, nothing logged". No send.log or sent.progress was written.

## Method

Each number was recounted from the desk's own summary file (not the page builder, not an agent report), compared with the live ledger row in ~/bones-forge/ledger/ledger.jsonl (status live), and searched for as text on the live page fetched from https://indahl.ai on 10 Nov 2026 (about 19:40 UTC). Match = live row, recount equals ledger value at the precision printed, and the string is on the live page.

| Number in the issue | Page | Ledger row | Ledger value | Recount from summary | On live page | Match |
|---|---|---|---|---|---|---|
| Atlantic whole path share | /cone | `cone.path.al` | 53.0 | 53.0 | yes | yes |
| Atlantic whole path interval low | /cone | `cone.path.al` | 45.1 | 45.1 | yes | yes |
| Atlantic whole path interval high | /cone | `cone.path.al.edge` | 60.4 | 60.4 | yes | yes |
| Atlantic forecasts scored | /cone | `cone.path.al.selection` | 1315 | 1315 | yes | yes |
| Atlantic forecasts not in share | /cone | `cone.path.al.selection` | 1692 | 1692 | yes | yes |
| Atlantic whole path outcome | /cone | `cone.path.al` | CANNOT_TELL | CANNOT_TELL | yes | yes |
| Lowest single-lead share | /cone | `cone.circle.al.120` | 68.6 | 68.6 | yes | yes |
| Highest single-lead share | /cone | `cone.circle.ep.48` | 72.6 | 72.6 | yes | yes |
| US 10-15 band share | /tornado | `tornado.us.band10_15` | 17.6 | 17.6 | yes | yes |
| US 10-15 band outcome | /tornado | `tornado.us.band10_15` | ABOVE | ABOVE | yes | yes |
| Warning detection | /tornado | `tornado.warn.pod` | 62.7 | 62.7 | yes | yes |
| Warning detection outcome | /tornado | `tornado.warn.pod` | BELOW | BELOW | yes | yes |
| Warning lead time (min) | /tornado | `tornado.warn.lead` | 9.8 | 9.8 | yes | yes |
| Warning lead outcome | /tornado | `tornado.warn.lead` | BELOW | BELOW | yes | yes |
| Warning false alarm ratio | /tornado | `tornado.warn.far` | 71.2 | 71.2 | yes | yes |
| False alarm outcome | /tornado | `tornado.warn.far` | CANNOT_TELL | CANNOT_TELL | yes | yes |
| M-class bins consistent | /solar | `solar.m1.bins` | 4 of 8 | 4 of 8 | yes | yes |
| Aftershock counts inside range | /quake | `quake.cover.m3` | 30,761 of 31,950 | 30,761 of 31,950 | yes | yes |
| Aftershock share | /quake | `quake.cover.m3` | 96.3 | 96.3 | yes | yes |
| Aftershock outcome | /quake | `quake.cover.m3` | CANNOT_TELL | CANNOT_TELL | yes | yes |
| One-year window share | /quake | `quake.cover.m3.year` | 86.5 | 86.5 | yes | yes |
| One-year outcome | /quake | `quake.cover.m3.year` | BELOW | BELOW | yes | yes |
| Flu 95% interval share | /flu | `flu.cell.all95` | 88.5 | 88.5 | yes | yes |
| Flu outcome | /flu | `flu.cell.all95` | BELOW | BELOW | yes | yes |
| WTI inside 95% interval | /steo | `steo.cell.wti.all` | 86.7 | 86.7 | yes | yes |
| WTI outcome | /steo | `steo.cell.wti.all` | CANNOT_TELL | CANNOT_TELL | yes | yes |
| Henry Hub inside | /steo | `steo.cell.hh.all` | 93.9 | 93.9 | yes | yes |
| Henry Hub outcome | /steo | `steo.cell.hh.all` | CONSISTENT | CONSISTENT | yes | yes |
| Temp stated mean | /seasonal | `seasonal.lean.temp` | 48.2 | 48.2 | yes | yes |
| Temp observed | /seasonal | `seasonal.lean.temp` | 60.1 | 60.1 | yes | yes |
| Temp outcome | /seasonal | `seasonal.lean.temp` | ABOVE | ABOVE | yes | yes |
| Predictions read | /predictions | `now.binary.right` | 42 | 42 | yes | yes |
| Predictions right | /predictions | `now.binary.right` | 11 | 11 | yes | yes |
| Predictions wrong | /predictions | `now.binary.wrong` | 15 | 15 | yes | yes |
| Predictions cannot tell | /predictions | `now.binary.cannot_tell` | 16 | 16 | yes | yes |
| Fortune lines read | /predictions | `fortune.count` | 22 | 22 | yes | yes |
| Complaints flagged timely 2025 | /credit | `credit.timely.2025` | 99.55 | 99.55 | yes | yes |
| Credit 2025 outcome | /credit | `credit.timely.2025` | CANNOT_TELL | CANNOT_TELL | yes | yes |
| EQUIFAX, not timely of rows | /credit | `credit.bureau.equifax.2025` | 0 of 1,680,537 | 0 of 1,680,537 | yes | yes |
| EXPERIAN not timely of rows | /credit | `credit.bureau.experian.2025` | 32 of 1,388,821 | 32 of 1,388,821 | yes | yes |
| TRANSUNION not timely of rows | /credit | `credit.bureau.transunion.2025` | 0 of 1,601,849 | 0 of 1,601,849 | yes | yes |
| National elementary list | /rank | `rank.list.elem` | 0 | 0 | yes | yes |
| National middle list | /rank | `rank.list.middle` | 0 | 0 | yes | yes |
| NJ high schools match/mismatch/ct | /rank | `rank.checks.nj_hs` | 70/0/10 | 70/0/10 | yes | yes |
| NJ colleges match/mismatch/ct | /rank | `rank.checks.nj_col` | 4/1/79 | 4/1/79 | yes | yes |
| Bacc schools read in browser | /oy | `oy.bacc_browser_89` | 89 | 89 | yes | yes |
| Bacc guidance pages | /oy | `oy.bacc_guidance_48` | 48 | 48 | yes | yes |
| Bacc measured outcome | /oy | `oy.bacc_measured_0` | 0 | 0 | yes | yes |
| NCSA addresses read | /linkrot | `linkrot.samples.20261110a.early.003` | 500 | 500 | yes | yes |
| NCSA same as first capture | /linkrot | `linkrot.samples.20261110a.early.004` | 3 (0.6%) | 3 (0.6%) | yes | yes |
| NCSA name no longer resolves | /linkrot | `linkrot.samples.20261110a.early.010` | 165 (33.0%) | 165 (33.0%) | yes | yes |
| CFPB printed timely share (stated) 99.6% | /credit | `credit.timely.2025` | in claim: "against the CFPB printed 99.6%" | stated figure, not recounted | yes | yes |
| NWS warning goals (stated) 72 percent, 13 minutes, 71 percent | /tornado | `tornado.warn.pod`, `tornado.warn.lead`, `tornado.warn.far` | in claims | stated figures | yes | yes |
| CPC threshold 40 percent or more (stated rule) | /seasonal | `seasonal.lean.temp` | in claim | rule, not a count | yes | yes |
| Cone quotes ("two-thirds of historical official forecast errors", "will remain within the cone about 60-70% of the time") | /cone | `cone_index/summary_cone.json` claim.circle, claim.whole_path | quotes | quotes | yes | yes |
| "There is no national ranking" | /rank | `rank.list.elem`, `rank.list.middle` (grep in source) | quote | quote | yes | yes |
| "This is not a ranking of agencies." | /forecasters | none (page copy, not a number) | quote | quote | yes | n/a |

Sources recounted: cone_index/summary_cone.json (cells), tornado_index/summary_tornado.json (cells[United States] band 10 to 15, warnings.pooled), solar_index/summary_solar.json (headline), quake_index/summary_quake.json (headline_cell, cover_by_window), flu_index/summary_flu.json (cells all horizons 95 final), steo_index/summary_steo.json (cells all leads), seasonal_index/summary_seasonal.json (temperature, leaning), now_index/summary_now.json (binary.all, fortune), credit_index/summary_credit.json (ruler1 2025, companies 2025 bureaus), rank_index/data/checks_nj.json, oy_index/BROWSER_REREAD_20261110.md, linkrot_index/summary_early.json (ncsa 1993-1996).

## Cut or flagged (not in the issue)

- **Rain rule numbers (43.9 and 16.8 percent).** Live rows forecast.adopt.original_10to20_lt12 and forecast.adopt.nws_10to20_lt12 hold them as frozen values at adoption on 10 Nov. The current forecast_index/summary_forecast.json no longer gives them (it reads 44.1 and 17.1 for the same cell now). The correction is described without numbers.
- **WTI "never above the interval".** Summary has above 0 and the page says it, but no ledger row carries it. Cut.
- **FORTUNE "Said: 13" and the other FORTUNE bins.** Only fortune.count (22) has its own row. 13 sits in that row's surface text only. Cut.
- **Stevens undergraduate enrollment (4,185 vs 4,206).** The one NJ college mismatch. No ledger row for either figure. The count (1 mismatch) is in rank.checks.nj_col and is kept.
- **Solar Brier skill 0.27, NCSA HTTP errors 138, NJ K-8 0/48, OY 3 re-read and 1 not reached, credit 115 companies (84/15/16), East Pacific cone 58.8.** All recounted and matched (live rows solar.m1.skill, linkrot.samples.20261110a.early.012, rank.checks.nj_k8, oy.s0_browser_reread, oy.s0_unreached_b, credit.companies.2025, cone.path.ep) and cut for length only.
- **Corrections bullets carry no counts.** The quantum row (c20261110-62) and the college row (c20261110-90) are paraphrased from the log. "Two times in three" and the former count of 4 unreached (row oy.s0_unreached, now withdrawn) were left out.
- **The forecasters page does not yet carry CONE, TORNADO, SOLAR or QUAKE.** Its members on 10 Nov: FEDSEP, FLU, FORECAST, NEO, NOW, REVISE, SEASONAL, STEO, WATER. The issue names only what it shows. Issue 0 said the page "puts every forecaster we score on one chart". That is not yet true for the four new ATLAS/HERMES desks.

## Style checks

- No semicolons (grep count 0). No AI statements. No counts of our own things in any heading. Byline Wayfinder and Bones. Quotes, not characterisation, for each stated figure.
- About 800 words of prose (855 with links stripped of paths, before the WTI cut).
