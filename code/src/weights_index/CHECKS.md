
## 2026-11-12 10:32 Faults and Guards 2.0 migration of the WEIGHTS outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built, the change touches only the outcome word. WEIGHTS_SUMMARY_ONLY=1 rebuilt the summary from the stored passes offline and only the headline block differed from the file before
- II: n/a: the outcome rule has no repeated item to count against a floor, the headline is one share read once from its own counts
- III: n/a: the share has one direction and nothing is summed across tests, rows or readings
- V: holds: Wilson 95 percent named in PLAN.md and unchanged. PLAN_ADDENDUM_std2.md names size 0.01, band [0, 0.01), edge open at 0.01, committed 89c358e before any reading under it
- VI: holds: four outcomes through K.read. 1 of 1,033 with [0.0002, 0.0055] holds neither 0.01 nor reaches it and sits inside the band so it reads CONSISTENT as before. The first pass reads CANNOT_TELL NO_INTERVAL_FORMABLE, never NOTHING_RETURNED
- R: holds: counts and the interval come from summary_weights.json of pass 114. caught: K.wilson gives 6.9e-18 at the lower end for zero events and K.read then misses the null, fixed in the desk by passing exactly 0 for no event and 1 for all events, the kit is not edited
- P1: n/a: no outside source is quoted in the lines changed, only the desk's own rule
- P2: holds: the outcome cell prints the reason beside cannot tell and the REQ-13 line sits under the table, both from the feed
- P3: n/a: no setting labels of an outside source appear in the lines changed here
- P4: n/a: no cause is stated in the changed text, only the rule and the reading
- P5: holds: the share still says 95 percent interval in its column head and the rule text now gives the band, the edge and the size that matters where the plan names one
- P6: holds: the page says the first pass reads cannot tell (NO_INTERVAL_FORMABLE) and does not say the weights are stable beyond the counts
- P7: cannot tell: no ledger row of this desk changes outcome in this pass, nothing is built, shipped or verified live. The tick publishes the new fields to the feed at its next run and the owner ships the page with ship.sh later
- P8: cannot tell: build_site.py was not run and no page was rendered, live.js was parsed with node --check and run against the summary in a stub page that printed the outcome cell and the REQ-13 line
- P9: holds: plain sentences, no semicolons and no counts of our things in headings in the lines edited, no emojis
- P10: holds: the band, the edge and the size that matters were chosen in the addendum before the new rule read anything and the page says the rule is in an addendum dated 12 November 2026
- O1: n/a: no new job, the existing tick bus slot is kept
- O2: holds: the 6 UNREADABLE models are counted as NOTHING_RETURNED beside the headline and are outside the numerator and the denominator
- O3: n/a: no GPU used
- O4: holds: liveness by completed work is unchanged, the updated field of the summary moves on each completed read
- O5: holds: no path was added, the scripts keep their absolute paths from the tick bus
- O6: n/a: no GPU job started
