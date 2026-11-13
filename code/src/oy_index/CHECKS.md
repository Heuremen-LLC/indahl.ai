# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 09:40 OY S0 refiling after the newsletter audit: two readings (rule written before the read, rule set after 41 schools), one filing rule for tools, UNREACHED bin, counts from the rows
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the 25 Oct table itself, rebuilt by the same script with no refiling, which gives the old bins 3/3/47/74/21 exactly, so the only moves are the seven listed in S0_REFILE_20261110.json (umd, cmu, msu to MEASURED-POLICY, four to UNREACHED)
- II: holds: every moved row is named with its reason and its quote, and the counts are recomputed from the rows by build_matrix_page.py, never typed. 3 of the 7 moves raise the policy count and 4 move rows out of None found
- III: n/a: no sign or product is read. These are counts of rows under stated rules
- V: holds: two rulers side by side, the rule written at about 10:10 on 25 Oct before any row (10 of 148) and the rule set at 11:35 after 41 rows (3 of 148). Both are printed and the page says when each was written
- VI: holds: each count can be zero, and the earlier zero is shown to depend on the later rule. The original-rule items each carry a quote with n and comparison in S0_REFILE_20261110.json, and the items not counted carry their reason
- R: holds: 41 is the number of rows/*.md files added before commit ecb90f3 (git log --until 2026-10-25 11:35:42), the PLAN addendum time is from its own heading, every grep in the refile file was found in its row file on 10 Nov
- P1: holds: every quote in the refile file was matched by script against its row file
- P2: holds: each count names its source file (WALL_S0.md addendum, written by script from the builder counts) and the date of the read, 25 Oct 2026
- P3: holds: bin labels now say policy level and that pilots are counted in their own row, the first-document column says it is the first link in our notes
- P4: holds: no cause is named for any outcome. Measured means a grade or learning outcome was measured, not that it moved
- P5: n/a: no interval is printed with these counts
- P6: holds: the headline leads with the larger count under the earlier rule and prints the narrower rule beside it with its timing, no stronger than the rows
- P7: holds: ledger rows are edited before the page ships, through ledger/ship.sh only
- P8: cannot tell: the rendered live page is checked after the ship, not before. The built oy.html was read back locally
- P9: holds: plain sentences, no semicolons in the new public text (asserted in the builder for the headline), no counts of our things in headings
- P10: holds: the later rule is labelled as set after the first 41 schools were read, on the page and in every ledger row that carries it

## 2026-11-10 09:55 OY S0 refiling, referee recount folded in: Georgia Tech cannot tell under the later rule, so that count is printed as 3 to 4
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the 25 Oct table itself, rebuilt by the same script with no refiling, which gives the old bins 3/3/47/74/21 exactly, so the only moves are the seven listed in S0_REFILE_20261110.json (umd, cmu, msu to MEASURED-POLICY, four to UNREACHED)
- II: holds: every moved row is named with its reason and its quote, and the counts are recomputed from the rows by build_matrix_page.py, never typed. 3 of the 7 moves raise the policy count and 4 move rows out of None found
- III: n/a: no sign or product is read. These are counts of rows under stated rules
- V: holds: two rulers side by side, the rule written at about 10:10 on 25 Oct before any row (10 of 148) and the rule set at 11:35 after 41 rows (3 to 4 of 148, Georgia Tech cannot tell). Both are printed and the page says when each was written
- VI: holds: each count can be zero, and the earlier zero is shown to depend on the later rule. The original-rule items each carry a quote with n and comparison in S0_REFILE_20261110.json, and the items not counted carry their reason
- R: holds: 41 is the number of rows/*.md files added before commit ecb90f3 (git log --until 2026-10-25 11:35:42), the PLAN addendum time is from its own heading, every grep in the refile file was found in its row file on 10 Nov
- P1: holds: every quote in the refile file was matched by script against its row file
- P2: holds: each count names its source file (WALL_S0.md addendum, written by script from the builder counts) and the date of the read, 25 Oct 2026
- P3: holds: bin labels now say policy level and that pilots are counted in their own row, the first-document column says it is the first link in our notes
- P4: holds: no cause is named for any outcome. Measured means a grade or learning outcome was measured, not that it moved
- P5: n/a: no interval is printed with these counts
- P6: holds: the headline leads with the larger count under the earlier rule and prints the narrower rule beside it with its timing, no stronger than the rows
- P7: holds: ledger rows are edited before the page ships, through ledger/ship.sh only
- P8: cannot tell: the rendered live page is checked after the ship, not before. The built oy.html was read back locally
- P9: holds: plain sentences, no semicolons in the new public text (asserted in the builder for the headline), no counts of our things in headings
- P10: holds: the later rule is labelled as set after the first 41 schools were read, on the page and in every ledger row that carries it

## 2026-11-10 13:40 OY browser re-read of blocked schools and documents: Williams, Haverford and Mississippi State read, back to NONE FOUND, unreached 4 to 1, 89 private baccalaureate schools read in a browser
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the 10 Nov morning refiling rebuilt by the same builder with no new read (UNREACHED 4, NONE FOUND 17), and the only moves are the three rows whose pages opened in the browser, listed in S0_REFILE_20261110.json reached_in_browser
- II: holds: three rows move from UNREACHED to NONE FOUND and none moves into or out of any measured bin, so both headline counts stay 10 and 3 to 4. Each move names its saved page texts
- III: n/a: no sign or product is read. These are counts of rows under the sealed rules
- V: holds: both sealed rules applied unchanged, the rule written before any row and the policy rule set after 41 rows. Neither count changes
- VI: holds: each read page could have shown a measured outcome and the reading would then have moved the row to a measured bin. None of the 18 MSU letters, 4 Williams pages, 4 Haverford pages or 89 baccalaureate rows states an outcome measure with n and a comparison. Wellesley stays not reached, a login page is not read as none found
- R: holds: counts computed by build_matrix_page.py on a copy before the ship (NONE FOUND 20, UNREACHED 1, original 10, policy 3 to 4). Read times are in each saved file. The 89 come from schools.json site_read reached
- P1: holds: quotes in the row addenda and in the 89 notes are checked against the saved page text by a referee subagent before the ship
- P2: holds: each count names its source, oy_index/BROWSER_REREAD_20261110.md and WALL_S0.md addendum of 10 Nov, and the rows say read 10 Nov 2026
- P3: holds: the bacc column now says Read by us and each browser-read school page says Read in a browser with the date, not read in full
- P4: holds: no cause is named. A none found is a page read with no measured outcome on it
- P5: n/a: no interval is printed with these counts
- P6: holds: the headline says three schools were read again in a browser and one still needs a login, no stronger than the saved pages
- P7: holds: ledger rows staged before the edit, flipped to live and the old rows withdrawn with history inside the one site_lock command that ships
- P8: cannot tell: the rendered live page is checked after the ship. The built oy.html is read back locally first
- P9: holds: plain sentences, no semicolons in new public text, no counts of our things in headings, no AI statements
- P10: n/a: no rule was set after this read. Both rules are the sealed ones

## 2026-11-12 10:28 Faults and Guards 2.0 migration of the OY headline (PLAN_ADDENDUM_std2.md): the two rule counts out of the rows read, REQ-13 line, reasons on cannot tell
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the rows, the two filing rules and every numerator are untouched, only the denominator of the two rule counts and the added reason text changed
- II: n/a: no repeated item, each school stays one row and the 148 rows are all still listed, the one not-reached row is listed apart and still appears in the table
- III: n/a: no signed gap is read here, the two rule counts stay side by side, 10 and 3 to 4, and are not summed
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before this build, the not-reached school is NOTHING_RETURNED per standard 6.6 and sits outside numerator and denominator, no interval is claimed for a count of rows
- VI: holds: the one row the later rule cannot settle (Georgia Tech) is CANNOT_TELL with NO_INTERVAL_FORMABLE, the same word is beside each pilot cannot tell, 1 NOTHING_RETURNED and CANNOT_TELL 1 of 147 are printed beside the headline
- R: holds: counts read from oy_headline.json after re-running build_matrix_page.py offline, read 147, original rule 10, policy rule 3 to 4, unreached 1, rows 148, the category counts of the table unchanged
- P1: n/a: no quotation of any source is added or changed by this edit
- P2: holds: the new counts name their source in oy_headline.json and the page says the shares are out of the rows that were read
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the reason text says only which closed reason a cannot tell carries and the Georgia Tech row keeps its own plain explanation
- P5: n/a: no interval is printed with these counts
- P6: holds: the headline says one school is listed apart as not reached and the shares are out of the rest, no stronger than the saved rows
- P7: holds: ledger rows are updated before any page text ships, oy.pilot_rochester moves from CONSISTENT to CANNOT_TELL because its paper is unread, and nothing is shipped from here, the owner ships with ship.sh
- P8: cannot tell: oy_body.html was rebuilt and diffed against its backup, but the page was not rendered in a browser because nothing is built or deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, the build asserts no semicolon in the headline line, no count of our own things in a heading
- P10: holds: the not-reached exclusion is the standard's own rule 6.6 and the addendum is dated 12 Nov 2026 before this build, no numerator moved, only the denominator went from 148 to 147
