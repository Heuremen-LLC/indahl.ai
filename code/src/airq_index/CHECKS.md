
## 2026-11-12 10:32 Faults and Guards 2.0 migration of the AIRQ outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built, the change touches only the outcome word and no count moved. The three summary files were patched from their own n and of values and airq_tie.py was run again offline
- II: n/a: the outcome rule has no repeated item to count against a floor, the headline is one share read once from its own counts
- III: n/a: the share has one direction and nothing is summed across tests, rows or readings
- V: holds: Wilson 95 percent over monitors named in PLAN.md and unchanged. PLAN_ADDENDUM_std2.md names a one-sided bound at 0.50 with a closed edge and no size that matters, committed 49c5eb6 before any reading under it
- VI: holds: ABOVE, BELOW and CANNOT_TELL only. 129 of 139 reads ABOVE, 70 of 139 with [0.4215, 0.5855] reads CANNOT_TELL STRADDLES_EDGE, under 30 monitors reads TOO_WIDE_TO_RESOLVE, none reads NO_INTERVAL_FORMABLE. The both-alternatives test is not applied because the plan names no size that matters, the addendum says why
- R: holds: counts, intervals and reasons are read from the three summary files and the live block. caught: K.wilson gives 6.9e-18 at the lower end for zero events and K.read then misses the null, fixed in the desk by passing exactly 0 for no event and 1 for all events, the kit is not edited
- P1: n/a: no outside source is quoted in the lines changed, only the desk's own rule
- P2: holds: each outcome cell prints the reason beside cannot tell, the other-tie cell does too, and the REQ-13 lines sit under each table, all from the feed
- P3: n/a: no setting labels of an outside source appear in the lines changed here
- P4: n/a: no cause is stated in the changed text, only the rule and the reading
- P5: holds: the share still says 95 percent interval in its column head and the rule text now gives the band, the edge and the size that matters where the plan names one
- P6: holds: the page says an upper end below one half reads BELOW and the word CONSISTENT is not used for it, and no reading in any window has been in that range
- P7: cannot tell: no ledger row of this desk changes outcome in this pass, nothing is built, shipped or verified live. The tick publishes the new fields to the feed at its next run and the owner ships the page with ship.sh later
- P8: cannot tell: build_site.py was not run and no page was rendered, live.js was parsed with node --check and run against the summary in a stub page that printed the outcome cell and the REQ-13 line
- P9: holds: plain sentences, no semicolons and no counts of our things in headings in the lines edited, no emojis
- P10: holds: the band, the edge and the size that matters were chosen in the addendum before the new rule read anything and the page says the rule is in an addendum dated 12 November 2026
- O1: n/a: no new job, the existing tick bus slot is kept
- O2: holds: sensors not read, AQS states not answered and the refused Alaska day are counted as NOTHING_RETURNED beside each window reading (1 for 2026), the live panel counts failed PurpleAir calls
- O3: n/a: no GPU used
- O4: holds: liveness by completed work is unchanged, the updated field of the summary moves on each completed read
- O5: holds: no path was added, the scripts keep their absolute paths from the tick bus
- O6: n/a: no GPU job started
