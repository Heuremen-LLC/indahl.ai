
## 2026-11-12 14:45 Drift tests F and H, first ship (PLAN_ADDENDUM_drift.md committed 3f671fc before any second label)
- I: holds: tests and rulers fixed in the addendum and committed in git before a second label exists, the label is read from each report's Technical labels line
- II: holds: G counts up, down and same per system and category item by item and never nets. It returns nothing until a second label exists
- III: holds: F and H are shares of systems with a change, unsigned, no sum across tests
- V: holds: Wilson 95 percent interval printed with the count (0 of 27, upper end 12.5 percent), same rule as Test B
- VI: holds: four outcomes. G and I return NOTHING_RETURNED and say why
- R: holds: numbers read from ailuminate_index/summary_drift.json at build, not typed. Known-good gate on planted histories passed on the run
- not claimed: that any change is an error, anything about the safety of a system

## 2026-11-12 10:20 Faults and Guards 2.0 migration of the AILUMINATE outcome rule (PLAN_ADDENDUM_std2.md, committed 0c6841f)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built by this desk. The rule change touches only the outcome word. A planted history of 80 systems read twice under one label returns F and H with no change and the two readings of 27 systems return TOO_WIDE_TO_RESOLVE, both in the drift_tick.py gate
- II: n/a: the outcome rule has no repeated item to count against a floor, drift tests G and H still count up, down and same per system and are not netted
- III: holds: G still counts UP and DOWN apart and the share up is read against 0.5 with a band of 0.35 to 0.65, nothing is summed across tests
- V: holds: Wilson 95 percent named in PLAN.md and unchanged. PLAN_ADDENDUM_std2.md names size 0.05, band [0, 0.15), edge open at 0.15, G band [0.35, 0.65] with size 0.15 either way, committed in git as 0c6841f before any reading under the new rule
- VI: holds: K.read returns the four outcomes. 0 of 27 gives [0, 0.1246] which holds 0 and 0.05 and reads CANNOT_TELL TOO_WIDE_TO_RESOLVE, 0 of 73 reads CONSISTENT, 6 of 27 reads STRADDLES_EDGE, 10 of 27 reads ABOVE, all run on the kit
- R: holds: the counts, intervals and reasons come from summary_ailuminate.json and summary_drift.json. caught: K.wilson(0, 27) returns a lower end of 6.9e-18, not 0, so K.read missed the null at zero and printed CONSISTENT. fixed: the desk passes exactly 0 for k = 0 and exactly 1 for k = n. The kit is not edited and the owner is told
- P1: n/a: the page text states the desk's own rule and quotes no outside source in the lines changed by this migration
- P2: holds: each outcome cell prints its reason beside the word and the REQ-13 line sits under the table, both read from the feed. The old outcomes stand as recorded in the ledger under the rules they named
- P3: n/a: no setting labels of an outside source appear in the lines changed here
- P4: n/a: no cause is stated anywhere in the changed text, only the rule and the reading
- P5: holds: every share still says Wilson 95 percent interval in the column head, the rule text now says the band, the size that matters and the edge
- P6: holds: the summary says cannot tell with the reason, and does not say the pages agree with their reports more strongly than 0 of 27 allows
- P7: cannot tell: the ledger rows ailuminate.drift.F and .H are set before the page text edits, but nothing is built, shipped or verified live in this pass. The owner ships later with ship.sh
- P8: cannot tell: build_site.py was not run and no page was rendered in this pass, the live.js edit was read back and parsed with node --check only
- P9: holds: plain sentences, no semicolons and no counts of our things in headings in the lines edited, no emojis
- P10: holds: the band, the size that matters and the edge were chosen in the addendum before the new rule read anything, and the page says so. Nothing is labelled post hoc because nothing was chosen after a reading
- O1: n/a: no new job, drift_tick.py and ailuminate_tick.py keep their existing slots on the tick bus
- O2: holds: a failed read of a report or page row stays NOTHING_RETURNED as a row status, is listed apart as failed_reads, and no outcome word NOTHING_RETURNED is printed any more
- O3: n/a: no GPU used, the desk runs on the CPU only
- O4: holds: liveness by completed work is unchanged, the summary updated field and the reads count move on every tick
- O5: holds: the scripts keep their absolute paths from the tick bus, nothing was added
- O6: n/a: no GPU job started, no job at all beyond drift_tick.py run once offline
