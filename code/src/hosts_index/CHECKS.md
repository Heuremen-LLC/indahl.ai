
## 2026-11-12 10:32 Faults and Guards 2.0 migration of the HOSTS outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built, the change touches only the outcome word, the endpoint parser, the 2 point agreement test and the 100 poll limit are unchanged and the counts did not move
- II: n/a: the outcome rule has no repeated item to count against a floor, the headline is one share read once from its own counts
- III: n/a: the share has one direction and nothing is summed across tests, rows or readings
- V: holds: Wilson 95 percent named in PLAN.md and unchanged. PLAN_ADDENDUM_std2.md names size 0.05, band [0, 0.15), edge open at 0.15, committed 7716a9d before any reading under it
- VI: holds: four outcomes through K.read. 27 of 831 with [0.0224, 0.0469] holds neither 0 nor 0.05 and sits inside the band so it reads CONSISTENT as before. No comparable endpoint reads CANNOT_TELL NO_INTERVAL_FORMABLE, never NOTHING_RETURNED
- R: holds: counts and the interval come from summary_hosts.json of the poll. caught: K.wilson gives 6.9e-18 at the lower end for zero events and K.read then misses the null, fixed in the desk by passing exactly 0 for no event and 1 for all events, the kit is not edited
- P1: n/a: no outside source is quoted in the lines changed, only the desk's own rule
- P2: holds: the outcome cell prints the reason beside cannot tell and the REQ-13 line sits under the table, both from the feed
- P3: n/a: no setting labels of an outside source appear in the lines changed here
- P4: n/a: no cause is stated in the changed text, only the rule and the reading
- P5: holds: the share still says 95 percent interval in its column head and the rule text now gives the band, the edge and the size that matters where the plan names one
- P6: holds: the page says it reads cannot tell (NO_INTERVAL_FORMABLE) until a span of 100 polls exists, not that hosts agree
- P7: cannot tell: no ledger row of this desk changes outcome in this pass, nothing is built, shipped or verified live. The tick publishes the new fields to the feed at its next run and the owner ships the page with ship.sh later
- P8: cannot tell: build_site.py was not run and no page was rendered, live.js was parsed with node --check and run against the summary in a stub page that printed the outcome cell and the REQ-13 line
- P9: holds: plain sentences, no semicolons and no counts of our things in headings in the lines edited, no emojis
- P10: holds: the band, the edge and the size that matters were chosen in the addendum before the new rule read anything and the page says the rule is in an addendum dated 12 November 2026
- O1: n/a: no new job, the existing tick bus slot is kept
- O2: holds: a model whose endpoint list failed stays in the poll's failed list, is counted as NOTHING_RETURNED beside the headline and is not an outcome
- O3: n/a: no GPU used
- O4: holds: liveness by completed work is unchanged, the updated field of the summary moves on each completed read
- O5: holds: no path was added, the scripts keep their absolute paths from the tick bus
- O6: n/a: no GPU job started
