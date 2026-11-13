
## 2026-11-12 10:33 Faults and Guards 2.0 migration of the FEDSEP outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the 0.30 figure, the September pages, the scoring of inside and outside and the gate are untouched and the gate passed on the planted cases and the 2016 minutes parser case
- II: n/a: no repeated item is counted and nothing is netted, each year stays one unit of the bootstrap and the Wilson rows
- III: holds: the signed mean errors, largest misses and every count of every row compared equal before and after the migration, only outcome fields moved and reason and req13 fields were added
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md committed as 98fee8c before any reading under it, bound 0.30 with no band and a closed edge, bootstrap over years with 4,000 draws and seed 7, Wilson 95 percent per variable, no tolerance invented
- VI: holds: four outcomes kept, CONSISTENT is no longer available for the point figure 0.30, CANNOT_TELL carries STRADDLES_EDGE in 10 of 12 readings, the both-alternatives test is not applied since the plan names no size that matters and the addendum says so
- R: holds: fedsep_tick.py re-run offline on the stored projections and the outcomes_day.json of 12 Nov, five rows moved from CONSISTENT to CANNOT_TELL STRADDLES_EDGE (pooled next year 10 of 37, sensitivity next year, GDP, PCE inflation and funds rate this year), 0 NOTHING_RETURNED, 6 triples not comparable listed apart, every other number identical
- P1: n/a: no quotation of any source is added, medians and ranges are the stored parse of the September pages
- P2: holds: the feed names the rule and interval method beside each row, and the addendum, the sources are unchanged from the 9 Nov agency addendum
- P3: n/a: no setting labels of any source are touched, the variable and horizon names are unchanged
- P4: holds: no cause is named, the added fields say only which closed reason a CANNOT_TELL carries and the REQ-13 count line
- P5: holds: each pooled row says its interval is a bootstrap over September years with 4,000 draws and seed 7 and each per variable row says Wilson 95 percent over years, in the feed field interval
- P6: holds: the summary is the same counts with the 2.0 reading in place of the recorded outcome, no stronger than before, and the old outcome stays in the 10 Nov ledger record
- P7: holds: no static ledger row of this desk changes outcome (fedsep.thisyear stays BELOW), the live value row for the next-year headline is written by ledger/live_headlines.py when the feed flips, the surface text edits (live.js, headline builder, build_site.py note) follow this entry, nothing is built or deployed
- P8: cannot tell: the pages are not rendered in a browser and not served, nothing is deployed from this session, live.js was checked with node --check and the headline builder was run against the new summary
- P9: cannot tell: the page sentences are written after this entry and linted for semicolons and counts in headings by the site gate at the end of the migration, the addendum has plain sentences
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, the sensitivity rows keep their label as defined after the first read
- O1: holds: the rider fedsep_tick.py stays on the tick bus at its cadence, edited in place after a backup fedsep_tick.py.bak-20261112-std2, parsed and run once offline through the revise venv python with the day cache of agency series
- O2: holds: a failed gate prints and exits so no outcome is published, triples that cannot be scored are listed apart as not comparable (6) and are outside every share, failed reads are 0 and counted in req13
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the updated stamp of summary_fedsep.json and the daily outcomes_day.json, the offline run reused today's cache and read no network
- O5: holds: all paths in the rider are absolute or relative to its own folder as before, the KV put keeps PATH and the account id, the publish guard still blocks a non-tick run
- O6: n/a: no GPU job is started by this change
