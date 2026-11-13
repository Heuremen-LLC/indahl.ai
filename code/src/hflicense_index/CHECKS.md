
## 2026-11-12 10:28 HFLICENSE outcome rule under Faults and Guards 2.0: K.read with the size that matters 0.10 and the band [0, 0.05), reasons and REQ-13 beside each group (plan addendum 12 Nov 2026)
packs: O,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline is built in this change, the null is zero disagreement and only the outcome rule changes
- II: n/a: no repeated item in this change, the desk's own re-read cadence is unchanged
- III: n/a: one share that cannot go below zero, so there is no BELOW cell and no cells to compare in sign
- V: holds: size that matters 0.10 and band [0, 0.05) open at the upper edge are the two bounds PLAN.md already named, written in PLAN_ADDENDUM_std2.md committed 401796a before any 2.0 reading
- VI: holds: K.read run on planted shares (0 of 96, 0 of 24, 0 of 29, 0 of 30, 12 of 135, 19 of 144, 3 of 60, 0 of 60, zero denominator, failed gate) gave the reason expected for each, the both-alternatives test fires when the interval holds 0 and 0.10
- R: holds: counts and interval come from the stored data through the desk's own summary step run offline, Models 0 of 96 CONSISTENT and Datasets 0 of 24 CANNOT_TELL, both unchanged, Datasets now with reason TOO_WIDE_TO_RESOLVE and 2 NOTHING_RETURNED (license file not readable), and every number except the reason and req13 fields is unchanged against summary_hflicense.json.bak-20261112-std2
- O1: n/a: no new job, hflicense_tick.py is the same rider on the tick bus and only its outcome lines changed
- O2: holds: the two row reasons file list could not be read and license file not readable are counted as NOTHING_RETURNED per group and stay out of numerator and denominator, Models 0 and Datasets 2, and a failed pass is not turned into an outcome
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the stamp of the feed the ledger already reads, unchanged by this edit
- O5: holds: the tick keeps its absolute paths and PATH, the edit adds a function and fields and the file parses
- O6: n/a: no GPU job in this change
- P1: n/a: no quotation is added to any page, only the outcome word, its reason and the REQ-13 line
- P2: holds: the new paragraph names the plan addendum and the figures come from live.json, none is typed into the page
- P3: n/a: no setting labels are involved in this change
- P4: holds: the page states what the interval is read against and does not state a cause of any disagreement, its existing line that it does not say which side is right stays
- P5: holds: the interval is named as a Wilson interval at 95 percent in the plan addendum and the table column says Share, 95% interval
- P6: holds: the outcome words say only where the whole interval lies against 0.05 and keep their reasons beside them
- P7: holds: no ledger row carries an outcome for this desk and no outcome changed, so no ledger row is set, nothing shipped, release stays with ship.sh
- P8: cannot tell: live.js and build_site.py text edited but not built or rendered in a browser and not deployed, by instruction
- P9: holds: new sentences use plain punctuation with no semicolons, no counts of our own things in a heading, no emoji
- P10: holds: the band and size were taken from the plan before the reading and the outcome did not change, so no post hoc label is needed
