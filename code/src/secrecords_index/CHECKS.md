
## 2026-11-12 10:31 SECRECORDS outcome rule under Faults and Guards 2.0: K.read with the size that matters 0.10 and the band [0, 0.05), reasons and REQ-13 beside each claim (plan addendum 12 Nov 2026)
packs: O,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline is built in this change, the null is zero disagreement and only the outcome rule changes
- II: n/a: no repeated item in this change, the desk's own re-read cadence and the full reread in progress are unchanged
- III: n/a: two shares that cannot go below zero, so there is no BELOW cell and no cells to compare in sign
- V: holds: size that matters 0.10 and band [0, 0.05) open at the upper edge are the two bounds PLAN.md already named, written in PLAN_ADDENDUM_std2.md committed 153123e before any 2.0 reading, one choice for both claims
- VI: holds: K.read run on planted shares (0 of 96, 0 of 24, 7 of 704, 12 of 135, 19 of 144, 20 of 764, 3 of 60, 0 of 60, 0 of 29, 0 of 30, zero denominator, failed gate) gave the reason expected for each, the stored 10 Nov HSTS row 0.0911 to 0.2035 reads ABOVE and the SPF row reads CONSISTENT
- R: holds: counts and intervals come from data/domains.json through the desk's own summary step run offline, HSTS and SPF numbers are compared with summary_secrecords.json.bak-20261112-std2 and only the outcome, reason, req13 and failed_reads fields move
- O1: n/a: no new job, secrecords_tick.py is the same rider on the tick bus and only its outcome lines changed
- O2: holds: the failed reads HTTPS request failed for HSTS and DNS read failed and count cut short for SPF are counted as NOTHING_RETURNED per claim, listed apart and kept out of numerator and denominator, a failed pass is not turned into an outcome
- O3: n/a: no GPU is used by this desk or by this change
- O4: holds: liveness is the stamp of the feed the ledger already reads (live.secrecords.headline), unchanged by this edit
- O5: holds: the tick keeps its absolute paths and PATH, the edit adds a function and fields and the file parses
- O6: n/a: no GPU job in this change
- P1: n/a: no quotation is added to any page, only the outcome word, its reason and the REQ-13 line
- P2: holds: the new paragraph names the plan addendum and the figures come from live.json, none is typed into the page
- P3: n/a: no setting labels are involved in this change
- P4: holds: the page says where the interval lies against 0.05 and does not say why a header fails, its existing line that it does not say whether a domain is on a preload list stays
- P5: holds: the interval is named as a Wilson interval at 95 percent in the plan addendum and the table column says Share, 95% interval
- P6: holds: ABOVE says only that the whole interval lies at or above 0.05 and the reasons stay beside each CANNOT_TELL
- P7: holds: ledger row live.secrecords.v20261110T120408Z set before any page text changes, nothing shipped, release stays with ship.sh
- P8: cannot tell: live.js and build_site.py text edited but not built or rendered in a browser and not deployed, by instruction
- P9: holds: new sentences use plain punctuation with no semicolons, no counts of our own things in a heading, no emoji
- P10: holds: the band and size were taken from the plan before the reading, the HSTS flip to ABOVE is labelled as a reading under the new rule beside the earlier CANNOT_TELL
