
## 2026-11-12 10:24 HFSIZE outcome rule under Faults and Guards 2.0: K.read with the size that matters 0.10 and the band [0, 0.05), reasons and REQ-13 beside the headline (plan addendum 12 Nov 2026)
packs: O,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline is built in this change, the null is zero disagreement and the rule only changes how an unchanged 12 of 135 is read against it
- II: n/a: no repeated item in this change, the desk's own re-read every 6.2 hours is unchanged and a flip of the outcome word is a new reading shown beside the old one
- III: n/a: one share of disagreements that cannot go below zero, so there is no BELOW cell and no cells to compare in sign
- V: holds: size that matters 0.10 and band [0, 0.05) open at the upper edge are the two bounds PLAN.md already named (ABOVE above 0.10, CONSISTENT below 0.05), written in PLAN_ADDENDUM_std2.md committed e3541d9 before any 2.0 reading
- VI: holds: K.read run on planted shares (0 of 96, 0 of 24, 12 of 135, 19 of 144, 3 of 60, 0 of 60, 0 of 29, 0 of 30, zero denominator, failed gate) gave the reason expected for each, the both-alternatives test fires when the interval holds 0 and 0.10
- R: holds: counts and interval come from data/repos.json through the desk's own summary step, run offline on the stored 10 Nov read, and every number except the outcome, reason and req13 fields is unchanged against summary_hfsize.json.bak-20261112-std2
- O1: n/a: no new job, hfsize_tick.py is the same rider on the tick bus every 64 ticks and only its outcome lines changed
- O2: holds: a failed list request still stops the pass and publishes nothing, no row is a failed read, so the page prints 0 NOTHING_RETURNED and a failed pass is not turned into an outcome
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the stamp of the feed the ledger already reads (live.hfsize.headline), unchanged by this edit
- O5: holds: the tick keeps its absolute paths and its PATH, the edit adds only a function and two fields and the file parses
- O6: n/a: no GPU job in this change
- P1: n/a: no quotation is added to any page, only the outcome word, its reason and the REQ-13 line
- P2: holds: the rule sentence names PLAN.md and its dated addendum, and the figures come from live.json, none is typed into the page
- P3: n/a: no setting labels are involved, the desk reads one public API list
- P4: holds: the page says a share of 12 of 135 lies above 0.05 and does not say why names differ, the existing sentence that the page does not say the name is wrong stays
- P5: holds: the interval is named as a Wilson interval at 95 percent in the plan addendum and the table column already says Share, 95% interval
- P6: holds: ABOVE says only that the whole interval lies at or above 0.05, the page keeps its line that most rows are a name stating one part of a model
- P7: holds: ledger row live.hfsize.v20261110T120408Z set before any page text changes, nothing shipped, release stays with ship.sh
- P8: cannot tell: live.js and build_site.py text edited but not built or rendered in a browser and not deployed, by instruction
- P9: holds: new sentences use plain punctuation with no semicolons, no counts of our own things in a heading, no emoji
- P10: holds: the band and size were taken from the plan before the reading, the flip to ABOVE is labelled as a reading under the new rule beside the earlier CANNOT_TELL
