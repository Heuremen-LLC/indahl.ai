
## 2026-11-12 10:33 Faults and Guards 2.0 migration of the AIRLINE outcome rule and the named seed (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the planted-data known-good still runs first and the 30-flight and 30-route rules are untouched
- II: n/a: no repeated item is counted, routes stay the independent units and no airline outcome is netted into another
- III: holds: change, flown change, route counts and late shares compared equal for all 27 airline readings before and after, only intervals, outcomes, reasons and the pre_std2 fields differ
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md committed as 641c855 before the reading, size that matters 1 minute both directions, band minus 1 to plus 1 closed, percentile bootstrap over routes 2,000 draws seed 20261112, the old stream seeded 20261029 kept beside as a separate reading
- VI: holds: four outcomes kept with the both-alternatives test applied, 2026 against 2025 has 5 ABOVE, 4 CANNOT_TELL (3 TOO_WIDE_TO_RESOLVE, 1 STRADDLES_EDGE) and 4 CONSISTENT of 13, 2025 against 2019 has 12 CANNOT_TELL (11 TOO_WIDE, 1 STRADDLES_EDGE) and 2 CONSISTENT of 14, the pooled count is CANNOT_TELL NO_INTERVAL_FORMABLE
- R: holds: airline_tick.py re-run offline on the 24 cached monthly files, the planted gate returned ABOVE, CONSISTENT, BELOW and CANNOT_TELL TOO_WIDE_TO_RESOLVE, airline_summary.py rebuilt the summary, 5 of 13 airlines ABOVE as before, the new seed moved two readings (Delta 2025 against 2019 to CONSISTENT, SkyWest 2025 against 2019 to TOO_WIDE_TO_RESOLVE), both labelled as a new reading
- P1: n/a: no quotation of any source is added
- P2: holds: the feed names the seed and method for each row and keeps the 29 Oct interval, outcome and method beside it in the pre_std2 fields
- P3: n/a: no setting labels of any source are touched, carrier codes and months are unchanged
- P4: holds: no cause is named, the page still prints the sign and size of the gap and nothing about intent
- P5: holds: every interval says percentile bootstrap over routes, 2,000 draws and its seed, the page says the first read used one shared stream seeded 20261029
- P6: holds: the summary is no stronger than the reading, the count of airlines above is said to read CANNOT_TELL NO_INTERVAL_FORMABLE with the plan's reason
- P7: holds: no static ledger row of this desk exists to change (the live.airline rows are written by ledger/live_headlines.py and the count 5 of 13 did not move), page text edits (live.js, headline builder, build_site.py source note) follow this entry, nothing is built or deployed
- P8: cannot tell: the pages are not rendered in a browser and not served, nothing is deployed from this session, live.js was checked with node --check
- P9: cannot tell: the page sentences are written after this entry and linted by the site gate at the end of the migration, the addendum has plain sentences without semicolons
- P10: holds: the addendum is dated 12 Nov 2026 and written before the reading under it, it says the one minute as the size that matters is a decision the owner can change in a later addendum
- O1: holds: the rider airline_tick.py and airline_summary.py stays on the tick bus at its cadence, edited in place after a backup .bak-20261112-std2, parsed and run once offline offline from the cached files (no download)
- O2: holds: a failed gate exits non-zero and no results are written, a failed FAA snapshot is still stored as NOTHING_RETURNED as a status of the read and is not an outcome, no airline is listed as NOTHING_RETURNED any more
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the summary updated stamp and the FAA snapshot count that nas_tick.py writes each tick, the faa block was carried over into the rebuilt summary and history.jsonl was restored after the test run
- O5: holds: all paths in the rider are absolute or relative to its own folder as before, the KV put keeps PATH and the account id, the publish guard still blocks a non-tick run
- O6: n/a: no GPU job is started by this change
