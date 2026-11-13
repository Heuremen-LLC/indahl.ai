
## 2026-11-12 10:28 Faults and Guards 2.0 migration of the SEAT rolling outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no baseline is built, the incident definition and the two-probe drift rule are unchanged, the addendum d61e969 names the bound of three and the edge before any reading under the new rule
- II: holds: an incident stays a run of consecutive flagged probes so one standing fault is not counted per probe, as Addendum 1 of the plan says
- III: n/a: one count against one bound, there are no cells whose sign could disagree
- V: holds: the ruler is the plan's own bound of three incidents in 24 probes, an exact count with a zero-width interval by owner decision O1, no tolerance invented
- VI: caught: the rule is one-sided so CONSISTENT is gone and the plan's dead zone of one or two incidents has no closed reason, so zero to two incidents read BELOW the bound of three, the one incident now on the page flips from CANNOT_TELL to BELOW, stated in the addendum and flagged for the owner
- R: holds: the rule block of seat_tick.py was run offline on the local nodes_repo history of 438 rows, 1 incident reading BELOW when the newest probe is fresh and NO_INTERVAL_FORMABLE when stale, and K.read gave BELOW for 0 to 2 and ABOVE for 3 and 4
- P1: n/a: no quotation of any source in this change
- P2: n/a: no new figure on the page, only the reason column and the REQ-13 line read from the summary
- P3: n/a: no setting labels of any source are touched
- P4: holds: the page names no cause, and the note says BELOW says only the incidents stayed under the plan's failure line and not that the site is good
- P5: holds: the page note says the count is exact and is read against one bound of three, no interval is claimed
- P6: holds: BELOW is explained as weaker than good and the count is printed beside the word
- P7: holds: no ledger row of this desk carries an outcome, the pack rows are counts of incidents and feeds and do not move, nothing is shipped from here, the owner ships with ship.sh
- P8: cannot tell: live.js passed a syntax check under node but was not served or rendered in a browser because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text and no count of our own things in any heading
- P10: holds: the addendum is dated 12 Nov 2026 and committed as d61e969 before any reading under the new rule
- O1: n/a: no new job, the existing seat rider on the tick bus runs the changed script at its next round
- O2: holds: a probe whose control failed is called a failed read, NOTHING_RETURNED, 3 of 475 rows, listed apart and outside the probes counted
- O3: n/a: no GPU used
- O4: cannot tell: seat_tick.py dispatches a runner probe and reads the repository, so it was not run here, and the next tick round with the changed rule is not observed from this session
- O5: holds: no path is added, the kit import is the copy already in the desk folder
- O6: n/a: no GPU job of any kind runs in this change
