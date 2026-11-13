
## 2026-11-12 10:26 Faults and Guards 2.0 migration of the UPTIME outcome rule (PLAN_ADDENDUM_std2.md)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the control floor, the seats and the episodes rule are unchanged, and the threshold is the plan's own count rule expressed as a share, committed in the addendum 3944c80 before any vendor read BELOW or ABOVE
- II: holds: consecutive disagreement rounds stay one episode and a would-be BELOW with fewer than two episodes reads CANNOT_TELL TOO_WIDE_TO_RESOLVE
- III: n/a: no cells to compare in sign, each vendor is one reading against one bound
- V: holds: the ruler is the control floor, the Wilson 95 percent upper end of the control rate, measured not assumed, and the interval of each vendor is a Wilson 95 percent interval named in the addendum
- VI: holds: the rule is one-sided so CONSISTENT is gone, all 20 vendors read CANNOT_TELL as before, 19 TOO_WIDE_TO_RESOLVE (61 rounds under the 300 minimum) and 1 NO_INTERVAL_FORMABLE (Datadog, zero rounds), the both-alternatives test is skipped because the plan names no size that matters and the addendum says so
- R: holds: uptime_summary.py re-run on the live probe files and every number of every vendor equal to the summary before, only reason, agreement interval and bound added, plus a synthetic run in a scratch folder giving ABOVE, BELOW, one-episode CANNOT_TELL and zero-round CANNOT_TELL as designed
- P1: n/a: no quotation of a vendor page in this change
- P2: n/a: no new figure on the page, only reason words and the REQ-13 line read from the summary
- P3: n/a: no setting labels of any source are touched
- P4: holds: the page names no cause for any disagreement, only the closed reason of a CANNOT_TELL
- P5: holds: the page note says each vendor is read as an agreement share with a 95 percent interval against one threshold set by the floor
- P6: holds: Datadog status page unread in 61 rounds is printed as a failed read, listed apart, and no summary is stronger than the readings
- P7: holds: no ledger row of this desk carries an outcome, the pack rows are counts of rows and incidents and do not change, nothing is shipped from here, the owner ships with ship.sh
- P8: cannot tell: live.js passed a syntax check under node but was not served or rendered in a browser because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text and no count of our own things in any heading
- P10: holds: the addendum is dated 12 Nov 2026 and committed as 3944c80 before any reading under the new rule, and the one-sided ABOVE replacing CONSISTENT is stated in it
- O1: n/a: no new job, the existing uptime rider on the tick bus runs the changed summary at its next round
- O2: caught: the old code skipped rounds where the status page could not be read without counting them, Datadog 61 rounds, now counted as NOTHING_RETURNED in failed_reads and in the REQ-13 line
- O3: n/a: no GPU used
- O4: holds: uptime_summary.py completed on the live data and rewrote summary_uptime.json, though the next full tick round is not observed from this session
- O5: holds: the kit path is built from the script folder so it does not depend on the cwd
- O6: n/a: no GPU job of any kind runs in this change
