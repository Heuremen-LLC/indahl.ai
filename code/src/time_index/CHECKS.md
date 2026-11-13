
## 2026-11-12 10:22 Faults and Guards 2.0 migration of the TIME outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the seat's own part stays removed as Addendum 1 says, the raw and seat-removed readings are both kept, the committed 5e6e2f2 addendum names how a disagreement between them is read
- II: n/a: no repeated item, each server is one reading per seat and no outcome changed in either seat
- III: holds: only ABOVE and CONSISTENT are possible for a distance, no BELOW is assigned, offsets keep their sign in the summary and nothing is summed
- V: holds: the band zero to E and the size that matters E are named in PLAN_ADDENDUM_std2.md before the read, and the interval is named as the half round trip, a worst-case bound with no probability level
- VI: holds: four outcomes kept, reference seat 34 CANNOT_TELL of 34 (33 TOO_WIDE_TO_RESOLVE, 1 STRADDLES_EDGE), runner seat 3 CONSISTENT and 31 CANNOT_TELL, both-alternatives test applied with the stated bound as the size that matters
- R: holds: check_time_t1.py re-run offline on data/probe_roll.jsonl and data/probe_azure.jsonl in a scratch folder, every offset, half-delay, bound, stratum, refid and count equal to summary_time_pi.json, outcome words unchanged
- P1: n/a: no quotation of a provider page in this change
- P2: n/a: no new figure on the page, only reason words and the REQ-13 line read from the summary
- P3: n/a: no setting labels of any source are touched
- P4: holds: the page names no cause for any server, only which closed reason a CANNOT_TELL carries
- P5: holds: the page note says the path uncertainty is half the round trip of the kept reply, a worst-case bound and not a probability interval
- P6: holds: the page says cannot tell with its reason, and a failed read is listed apart and outside every count of outcomes
- P7: holds: no ledger row exists for this desk, nothing is shipped from here, the owner ships with ship.sh and the site builder text and live.js are edited in place only
- P8: cannot tell: live.js was run under node with a stubbed page against merged scratch data and printed the reasons and REQ-13 lines, but it was not served or rendered in a browser because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, no count of our own things in any heading
- P10: holds: the addendum is dated 12 Nov 2026 and committed as 5e6e2f2 before any reading under the new rule
- O1: n/a: no new job, the existing time rider on the tick bus runs the changed scripts at its next round
- O2: holds: a server that returns nothing is now recorded as a failed read with its status, listed apart in failed_reads and counted in the NOTHING_RETURNED figure, not folded into an outcome
- O3: n/a: no GPU used
- O4: cannot tell: liveness of the next tick round with the changed scripts is not observed from this session because time_tick.py reaches the Pi and GitHub and was not run here
- O5: holds: the kit path is built from the script file location, so it does not depend on the cwd that time_tick.py sets
- O6: n/a: no GPU job of any kind runs in this change
