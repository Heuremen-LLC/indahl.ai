
## 2026-11-12 10:33 IBM published-calibration audit under Faults and Guards 2.0: every T2 over T1 entry reads CANNOT_TELL (NO_INTERVAL_FORMABLE), point-ratio counts kept as counts
packs: P,Q
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline is built, the audit reads IBM's published entries against IBM's own bound of 2 x T1, and only the outcome word changed
- II: n/a: no gap between two readings, the A counts are unchanged from the pre-change run (recount.py matches audit.py on all 8 processors after the label rename)
- III: n/a: no cells and no sign, one reading per qubit entry with no interval, so no sum or product
- V: holds: one ruler, IBM's published T1 and T2 values, with no width published, PLAN_ADDENDUM_std2.md says the repeated records give drift between calibrations and not fit uncertainty
- VI: fixed: K.read(None, None, bound=2.0) gives CANNOT_TELL NO_INTERVAL_FORMABLE for every entry, no size that matters is named so the both-alternatives test is skipped and the addendum says so
- R: holds: counts read from records/*/*.json.gz by audit.py, 1166 of 1166 newest-record entries CANNOT_TELL, 0 NOTHING_RETURNED, the earlier ABOVE and CANNOT_TELL counts kept as ratio_above_2_5 and ratio_2_to_2_5
- P1: n/a: no quote is added by this change, the page text carries no quoted words
- P2: holds: the build_site.py paragraph and audit.js both say the reading is per entry from the newest saved record and name the addendum rule
- P3: n/a: no setting labels are involved, the labels are IBM's T1 and T2 as published
- P4: holds: no cause named, the paragraph says only that IBM publishes no fit uncertainty so the ratio has no interval
- P5: holds: the page says the ratio has no interval and that the counts are of point ratios, no interval is printed
- P6: holds: the summary line says CANNOT_TELL for every entry and the REQ-13 line prints 0 NOTHING_RETURNED and the split by reason
- P7: cannot tell: no ledger row carries these audit counts, release is through ledger/ship.sh by the owner, the KV already carries the new summary from the mirror cycle
- P8: cannot tell: the rendered page is checked after the next ship, audit.js passes a syntax check and the old script still reads the legacy keys
- P9: holds: plain sentences, no semicolons added, no counts of our own things in headings
- P10: holds: the 2.5 cut is still labelled as set after the first look, the new rule is dated 12 Nov 2026 in the addendum
- QA: n/a: the vendor's number is IBM's own published T1 and T2, same quantity both sides, no job of ours is involved
- QB: n/a: no idle or none arm, the audit is a zero-QPU read of saved records
- QC: holds: kit self-test passes and K.read with no interval returns NO_INTERVAL_FORMABLE, the independent recount.py matches audit.py line for line
- QD: fixed: ABOVE and the earlier CANNOT_TELL words are retired for point ratios, the table columns now read as counts of point ratios and the reading line says CANNOT_TELL (NO_INTERVAL_FORMABLE)
- QE: holds: no cause named, a count of point ratios above 2.5 is a count and nothing more, the 2.5 cut stays labelled as set after a first look
- QF: holds: times and stamps come from the saved records, PLAN_ADDENDUM_std2.md committed in qia_mirror before the new rule ran
- QG: cannot tell: the page is checked after the next ship, the paper and the bill do not print these counts as outcomes
