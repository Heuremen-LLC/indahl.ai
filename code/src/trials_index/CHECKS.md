
## 2026-11-12 10:31 Faults and Guards 2.0 migration of the TRIALS outcome rule (PLAN_ADDENDUM_std2.md, committed 028f279)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built, the change touches only the outcome word. The records and every count are the same before and after: 25 outcome fields differ in data/summary.json and no other number moved, checked by walking both files
- II: n/a: the outcome rule has no repeated item to count against a floor, every group is read once from its own counts and none is netted into another
- III: n/a: the shares are of records with no results and have no sign to compare across cells, nothing is summed across groups
- V: holds: Wilson 95 percent named in PLAN.md and unchanged, the sponsor-clustered interval stays a labelled second interval beside it and the outcome is not read on it. PLAN_ADDENDUM_std2.md names size 0.25, band [0, 0.10), edge open at 0.10, and for the stopped tests size 0.10 and band [0, 0.05), committed 028f279 before any reading under it
- VI: holds: four outcomes through K.read. The headline 4,772 of 22,210 with [0.2095, 0.2203] holds neither 0 nor 0.25 and sits above 0.10 so it reads ABOVE. A group reaching 0 and 0.25 reads TOO_WIDE_TO_RESOLVE and one overlapping 0.10 reads STRADDLES_EDGE, the sponsor table has 97 of 155 STRADDLES_EDGE
- R: holds: every count, interval and reason is read from summary_trials.json built from data/records.jsonl of the read of 12 Nov 13:50 UTC. caught: K.wilson gives 6.9e-18 at the lower end for zero events and K.read then misses the null, fixed by passing exactly 0 for no event and 1 for all events, the kit is not edited
- P1: n/a: no outside source is quoted in the lines changed, only the desk's own rule
- P2: holds: the outcome cells print the reason beside cannot tell and the REQ-13 line sits beside the headline, both from the feed. Earlier outcomes in the ledger stand under the rules they named
- P3: n/a: no setting labels of an outside source appear in the lines changed here
- P4: holds: the page says the headline reads ABOVE the band of 0 to 10 percent and says no cause, the plan's own sentence that a record with no results is not a record of a late result is kept
- P5: holds: every share still says 95 percent interval in its column head, the rule text now gives the band, the size that matters and the edge, and the clustered interval is still labelled as defined after the data
- P6: holds: ABOVE is described as above the band edge of 10 percent, not as above the 25 percent that is the size that matters, and the page says the dead zone is closed by this rule and not by new data
- P7: cannot tell: trials.all.clustered is set to ABOVE before the page text edits, but nothing is built, shipped or verified live in this pass. The tick publishes the new outcome to the feed at its next run and the owner ships the page with ship.sh later
- P8: cannot tell: build_site.py was not run and no page was rendered, live.js was parsed with node --check and run against the new summary in a stub page that printed the outcome cells and the REQ-13 line
- P9: holds: plain sentences, no semicolons and no counts of our things in headings in the lines edited, no emojis
- P10: holds: the band edge and the size that matter were chosen in the addendum before the new rule read anything. The sponsor-clustered interval keeps its label as defined after the data. caught: the page called the registry class Unknown with 3 records cannot tell for having fewer than 30 records, which the code never did, and under the new rule it reads ABOVE, this is left for the owner
- O1: n/a: no new job, trials_tick.py keeps its slot on the tick bus every 48 ticks
- O2: holds: a failed registry read still stops the run and publishes nothing, so a published read has 0 NOTHING_RETURNED and the REQ-13 line says so
- O3: n/a: no GPU used
- O4: holds: liveness by completed work is unchanged, the read time in the summary moves on each completed read
- O5: holds: no path was added, the scripts keep their absolute paths from the tick bus
- O6: n/a: no GPU job started, only trials_summary.py was run once offline
