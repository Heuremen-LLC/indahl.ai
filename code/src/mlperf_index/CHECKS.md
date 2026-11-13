
## 2026-10-30 10:42 Site pass E-16 and E-17: eight MODEL outcome words recounted from their own files (RR12, AR2, BV1, GV2 to ABOVE; RR19, KV1, Y4, FU1 to CANNOT_TELL)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each row compares the vendor's statement with the same quantity in the MLCommons file named in the row, unchanged by this edit
- II: holds: a row with two counts in opposite directions (RR19) keeps both in its note instead of netting to one word
- III: fixed: the page defines ABOVE as the file showing more than the statement; RR12 (18.218 against 18.02), AR2, BV1 and GV2 read BELOW in the old direction and now read ABOVE
- V: holds: the ruler is the file value against the printed value, rounding stated in the note where it matters (BV1 34301 against 34301.9)
- VI: fixed: rows whose notes do not support a verdict (FU1, KV1, KV2, Y4) and a two-direction row (RR19) now read CANNOT_TELL
- R: holds: values read from claims_redhat_v60.json and claims_broadcom_v51.json by hand for RR12, RR19, BV1, the rest from the lane E recount of every claim file
- P1: holds: statement columns keep the vendor's words, quotation marks restored on the AMD Training rows (E-14)
- P2: holds: each row names its source page and MLCommons round
- P3: holds: labels match the source rows after the Apple M3 description fix (E-13)
- P4: holds: no cause is named for any difference
- P5: holds: the live block now says what the plus-minus width is (1.96 harness standard errors plus the card's rounding)
- P6: fixed: the papers-table heading said the papers check out over rows with a post-hoc rule and unreleased keys (E-26), now it names what the table shows
- P7: holds: ledger rows set with this entry before the build
- P8: cannot tell: the rendered MODEL pages are checked after the release build
- P9: holds: semicolons and code reprs removed from 194 cells, read in full wording
- P10: n/a: no reading in this batch was defined after the data beyond what the rows already state

## 2026-11-12 10:24 Faults and Guards 2.0 migration of the MODEL outcome rule (PLAN_ADDENDUM_std2.md): reasons on every CANNOT_TELL and a REQ-13 line beside each source tally
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, every statement is still read against the same MLCommons file entry it named, and no statement was added or dropped
- II: n/a: no repeated item, the 531 statements stay one row each and their recorded outcomes are byte identical before and after the rebuild of sad_claims.json
- III: holds: ABOVE and BELOW stay separate and no sum is made, only the reason field was added beside outcome, and a diff of all claim fields other than reason showed 0 differences
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before any reading under it, the readings are exact row-level reads of zero width, the band is the rounding of the printed figure with closed edges, no new tolerance invented
- VI: holds: four outcomes kept, all 104 CANNOT_TELL carry NO_INTERVAL_FORMABLE and the addendum says why neither other reason can arise on a zero-width reading, 0 NOTHING_RETURNED
- R: holds: counts and REQ-13 lines are read from sad_summary.json after re-running build_sad.py offline, 531 claims, 371 CONSISTENT, 104 CANNOT_TELL, 48 BELOW, 8 ABOVE unchanged, the tally grep strings still match
- P1: n/a: no quotation of any source is added or changed by this edit
- P2: n/a: no new figure, each count line names its source tally and the file sad_summary.json it is read from
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added page text says only which closed reason a CANNOT_TELL carries and the notes keep the specific cause
- P5: holds: the rule text says the readings are exact and carry no interval, so no interval method or level is claimed for them
- P6: holds: the added line is the REQ-13 sentence read from the summary, no stronger than the reading, and the rule sentence says the file does not hold the quantity
- P7: holds: ledger rows for the new count lines are added before the build and nothing is shipped from here, the owner ships with ship.sh
- P8: cannot tell: build_site.py was edited but not run and the page was not rendered in a browser, because nothing is built or deployed from this session
- P9: holds: plain sentences without semicolons in the added page text and no count of our own things in any heading
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, no rule is set after seeing outcomes because no outcome moved
