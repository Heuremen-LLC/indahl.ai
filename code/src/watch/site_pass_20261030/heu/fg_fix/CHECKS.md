# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-10-30 12:10 HEU2-10/13/14 recount of the guard's three-day series and the cold/seated frame rates (Faults 20, 24, 41; Guards first principle, 22, 36)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: both rulers read the same rows of one log (hook_fires.log rows 1-374, seated session only) with one scanner; the none for "no change" is the same ruler on the earlier days. The cold and seated arms are not like for like in length, and both documents now say so with the middle halves (689-1,246 vs 268-428 words).
- II: n/a: no paired item flips or repeat floor apply; the reading is a daily rate over three days and two arm rates, not a flip count.
- III: holds: day 3 against day 2 is positive on both rulers (+2.64 per reply, +0.97 per 1,000 words, frames), and positive for pushbacks too (+3.02, +1.02); the sign agrees, only the size against the width differs.
- V: fixed: two rulers printed side by side on ONE numerator (frames) in Faults 24 and Guards 22; the width rule is printed, reproduced from triangulation/triangle/audit_guard.py lines 92-106 (+3.02 and +0.97 reproduce exactly from it).
- VI: fixed: per reply ABOVE (+2.64), per 1,000 words CONSISTENT (+0.97), context effect CANNOT_TELL (kept); "no change" now carries its bound: day 3 / days 1-2 = 1.24, exact 95% 0.76 to 1.99, so a fall over 24% is outside.
- R: fixed: every count read from the log by recount_heu2_10.py and recount_heu2_14_lengths.py (outputs beside this file); the log is the 8 Oct record. Scanner changes on record: the numeric-vs exemption went in after 6 Oct 21:30:42 (triangle.py.bak-preNumVs lacks it), before the first seated row (5 earlier rows, none seated), and the false-positive fix after 8 Oct 16:36 (bak-preFalsePositive), after the 374-row cut; no backup exists between them, so a 7 Oct change cannot be ruled out. Noted for Bones in FIXLOG_FG.md.
- P1: holds: no quotation added or changed; the quoted line in Faults 45 was held by HEU2 (watch/tp_score.jsonl row 658).
- P2: cannot tell: the documents print no file paths by their own rule (footer: no instance is reported with its run); each changed figure has its file and line in FIXLOG_FG.md and a ledger command in LEDGER_TODO_FG.md.
- P3: holds: "flagged for a two-option frame" = rows with "Two-lane" in hook_fires.log; "pushback of any kind" = rows with "PUSHED BACK"; audit_guard's frame count equals the Two-lane row count on every day (9/42/30).
- P4: fixed: the compression mechanism is gone from the Faults 20 heading and text and from Guards; only the two measured rates, the length rule-out and "context did not remove it" remain.
- P5: fixed: the interval says what it is (exact 95 per cent, conditional binomial on the rate ratio) and the widths say what they are (root-sum-square of binomial or Poisson standard errors, day against previous day).
- P6: fixed: "not at all", "does not work", "does not improve", "nothing happened", "a collapse", "Flat" replaced with the reading and its bound.
- P7: caught: ledger rows for every changed figure are written as commands in LEDGER_TODO_FG.md; nothing run, shipped or committed from this lane.
- P8: holds: both PDFs rendered by ligera/render.sh into fg_fix (glyph gate and post-render codepoint check passed); Faults pp. 6, 8, 13 and Guards p. 1 viewed as page images.
- P9: fixed: 0 semicolons in both PDFs' text, no "apparatus", no hand wording, "Heuremen LLC" in byline and footer, no counts in leads; count_scan 0 hits, site_rules forbid patterns 0 hits.
- P10: fixed: the pooled day-3 comparison was chosen today after the data and both documents say "a comparison chosen after the data"; the day-against-previous-day width rule is the one written on 8 Oct.

## 2026-10-30 12:11 Bones' second pass on Faults and Guards: heading 41 and its line to the reading, at least four times, a stated practice in place of an unmeasured cause, dated-note labels, consistent in place of borderline, the dependence sentence in entry 24
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no new comparison; the wording now matches readings already printed
- II: holds: the dependence sentence names why the three days are not independent samples instead of netting them
- III: n/a: no sign changes
- V: holds: same rule as entry 24 (audit_guard.py); the score-table cell keeps the exact interval and Fisher p
- VI: fixed: borderline is not one of the four outcomes; the cell now reads consistent, as ledger row guards.exact_bar records
- R: holds: 36 seated rewrites and the 374-row tuning set from REFEREE_OWN.md line 18; four listed instances counted in both entries; dated notes named by the fix log (tone_scan.py lines 5-6, EL_NINGUNO_FOLDED_INTO_FALLAS.html line 52)
- P1: n/a: no quotes changed
- P2: holds: figures kept from notes are labelled as notes with the raw output not kept
- P3: holds: four outcome words only
- P4: fixed: the mechanical-reason sentence named a cause with no measurement; it now states the practice and the reason we use it
- P5: holds: the exact 95 per cent interval is printed beside consistent
- P6: fixed: heading 41 and its line said a failure mode is never prevented by knowing it; they now say it did not here
- P7: holds: guards.exact_bar moved to the new text; the 36 rewrites get a row
- P8: cannot tell: the PDFs render in the next ship and are read live then
- P9: holds: plain sentences, no semicolons added
- P10: holds: the pooled comparison is still labelled as chosen after the data
