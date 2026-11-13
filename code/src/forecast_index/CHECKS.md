# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 12:25 FORECAST: NWS event rule (0.01 inch or more) primary from today by dated PLAN Addendum 2, decided after the data, original committed rule kept beside it
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the original rule on the same periods, bins, leads and dedup. Both are computed in one run of forecast_tick.py from one period set (704 scored periods, 1,912 cell counts each, 0 periods waiting or unscorable under the new rule at 12:10 UTC)
- II: holds: the NWS rule is a strict subset of the original. On 1,715 station periods both scored, 290 wet under both, 152 under the original only, 1,273 under neither, 0 under the NWS rule only
- III: holds: every cell moves the same way, down or unchanged, as the subset requires. The 10 to 20 bin under 12 hours reads 43.9 percent under the original and 16.8 percent under the NWS rule against 14.1 stated
- V: holds: two rulers side by side, the original committed rule and the NWS rule, both tables on the page and in the feed
- VI: holds: four outcomes under both rules with the plan's threshold of 30 periods. Original 12 above, 3 consistent, 3 cannot tell. NWS rule 3 above, 12 consistent, 3 cannot tell, no below
- R: holds: totals read from the Iowa Environmental Mesonet ASOS archive, routine reports only (report_type 3), a trace read as zero. Seven planted cases pass (measurable.py selftest). Seven recent periods matched api.weather.gov totals to within 0.04 inch with the same event reading. The change is labelled decided after the data in the plan, the page and the feed
- P1: holds: the NWS definition is quoted as measurable precipitation, 0.01 inch or more
- P2: holds: the page names both rules, the archive the totals come from, and the plan addendum, and the numbers at adoption are dated 10 November
- P3: holds: the original table is labelled as the original committed rule, the NWS table as the primary reading from 10 November
- P4: holds: no cause is named for the gap between the rules beyond what each rule counts
- P5: holds: every interval on the page says 95 percent, Wilson as the plan names it
- P6: holds: the page states the adoption was after the data and keeps the original reading in full beside it
- P7: holds: ledger rows forecast.adopt.* went in before the page text, release through ledger/ship.sh
- P8: holds: live.js renders both tables from /forecast/live.json, checked on the live page after the release
- P9: holds: plain sentences, no semicolons, no count of our own things in the title, heading or lead
- P10: holds: decided after the data said plainly in the addendum and on the page
- O1: holds: the measurable read runs inside the existing forecast rider on the tick bus (every tick), at most 10 archive requests a round, only for periods that ended 3 hours or more ago
- O2: holds: a failed archive read prints a line and leaves the period waiting, counted in the feed as waiting, never as dry
- O3: n/a: no GPU used, network reads only
- O4: holds: the feed stamp is the round that wrote it
- O5: holds: absolute paths, Python 3.9 compatible, user agent names this site
- O6: n/a: no GPU job, network reads only

## 2026-11-12 10:20 FORECAST: Faults and Guards 2.0 outcome rule by PLAN_ADDENDUM_std2.md (12 Nov 2026), point figure with no tolerance, CONSISTENT removed, reasons and REQ-13 printed
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the earlier outcome rule on the same cells. The new rule was run on the same 18 primary cells and 18 original cells of one period set, and every number other than outcome and reason matched the run before the edit (compared field by field, 0 differences)
- II: holds: flips counted before any net. Primary table: 11 cells CONSISTENT to CANNOT_TELL (STRADDLES_EDGE), 4 ABOVE unchanged, 3 CANNOT_TELL unchanged now with reason TOO_WIDE_TO_RESOLVE. Original table: 3 CONSISTENT to STRADDLES_EDGE, 12 ABOVE unchanged
- III: holds: every cell that read ABOVE under the earlier rule still reads ABOVE, no cell reads BELOW, and no cell moved in sign. Nothing is netted or summed across cells
- V: holds: the ruler is the mean stated chance of each cell as a point figure with no tolerance, named in PLAN_ADDENDUM_std2.md committed as 0b44baa before the new rule was run. The earlier rule is kept in the record as recorded
- VI: holds: four outcomes in the record, CONSISTENT not available for a point figure with no tolerance (standard 6.4). No size that matters is named so the both-alternatives test is not applied, said in the addendum. Under 30 periods is TOO_WIDE_TO_RESOLVE by the owner decision O3
- R: holds: counts read from summary_forecast.json written by forecast_tick.py. Primary table req13 reads 0 NOTHING_RETURNED, CANNOT_TELL 14 of 18 (11 STRADDLES_EDGE, 3 TOO_WIDE_TO_RESOLVE). Original table 6 of 18 (3 STRADDLES_EDGE, 3 TOO_WIDE_TO_RESOLVE). The decision is dated 12 Nov 2026 and said so, not defined after a reading was used to pick it
- P1: holds: the plan wording quoted in PLAN_ADDENDUM_std2.md is the standard 6.4 rule for a point figure, the reason names are the kit's constants STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE, NO_INTERVAL_FORMABLE verbatim
- P2: holds: each figure on the page says which rule it is read under, the NWS rule or the original committed rule, and the dated addendum that sets the outcome rule is named
- P3: holds: table labels match the feed keys, measurable for the NWS rule and cells for the original rule, unchanged from 10 Nov
- P4: holds: no cause is named for why a cell cannot tell beyond the rule, the interval holds the stated chance or the cell has under 30 periods
- P5: holds: every interval on the page is the Wilson 95 percent interval the plan names, unchanged
- P6: holds: the page says a cell that reads cannot tell is not a finding of agreement, and no summary is stronger than the reading
- P7: holds: forecast.adopt.nws_10to20_lt12 changed through ledger.py before the page text with a complete CHECKS.md entry. Release is left to ledger/ship.sh by the owner, nothing deployed
- P8: cannot tell: live.js edited and parsed with node --check but the rendered page was not opened in a browser because no build or deploy was run
- P9: holds: plain sentences, no semicolons, no count of our own things in the title, heading or lead
- P10: holds: the NWS rule adoption stays labelled decided after the data, and the new outcome rule is labelled as an addendum of 12 Nov 2026 written before the read under it
- O1: holds: no new job, the change is inside the existing forecast_tick.py rider on the tick bus. The file was syntax checked and run once offline with the network patched to fail
- O2: holds: failed archive reads still leave a period waiting and are counted as waiting in the feed, never as dry. REQ-13 NOTHING_RETURNED is printed as 0 and no cell is a failed read
- O3: n/a: no GPU used, no network used in the test
- O4: holds: the feed stamp is the round that wrote it and the offline run rewrote summary_forecast.json with an updated stamp and no new rows
- O5: holds: absolute paths used, Python 3.9 compatible, backup forecast_tick.py.bak-20261112-std2 beside the file
- O6: n/a: no GPU job, no training
