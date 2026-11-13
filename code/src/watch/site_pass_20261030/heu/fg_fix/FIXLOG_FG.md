# FIXLOG_FG: Faults and Guards, HEU2-10 to HEU2-19 (and HEU2-22), 30 Oct 2026

Fix agent for Bones. Review acted on: `watch/site_pass_20261030/heu/HEU2.md` (Faults and Guards section, HEU2-22, HOLDS).
Nothing was shipped, committed, copied to a served folder or written to the ledger.

## Files

| what | path | sha256 |
|---|---|---|
| edited source | `~/bones-forge/ligera/FAULTS.html` | 62489b7d8331e126… |
| edited source | `~/bones-forge/ligera/GUARDS.html` | 3c995bbc28dadb98… |
| backup (pre-edit, byte-identical to the 25 Oct sources) | `ligera/FAULTS.pre-heu2-20261030.html`, `ligera/GUARDS.pre-heu2-20261030.html` | 90d47afe…, 490d0fa5… |
| test render (ligera/render.sh, not served) | `fg_fix/faults.pdf` (14 pp), `fg_fix/guards.pdf` (12 pp, was 11) | 3c4e1e5a…, 0521ad85… |
| extracted text | `fg_fix/faults_pdf.txt`, `fg_fix/guards_pdf.txt` | |
| page images checked by eye | `fg_fix/pages/faults_p6.png`, `faults_p8.png`, `faults_p13.png`, `guards_p1.png` | |
| edit script (exact-once anchors, all or nothing; later passes logged at its foot) | `fg_fix/apply_edits.py` | |
| recounts | `fg_fix/recount_heu2_10.py` → `.out`, `recount_heu2_14_lengths.py` → `.out`, `recount_heu2_15_tone.py` → `.out`, `recount_heu2_15_words.py` → `.out` | |
| checks | `fg_fix/check_pdfs.py` → `check_pdfs.out`, `fg_fix/run_gates.py` → `run_gates.out`, `fg_fix/semis.py`, `fg_fix/CHECKS.md` | |
| ledger commands (text only) | `fg_fix/LEDGER_TODO_FG.md`, built and verified by `fg_fix/gen_ledger_todo.py` | |
| 23 Oct business pages read from git (evidence for HEU2-15) | `fg_fix/git_show_indahl_20261023/` | |

`fg_fix/` = `~/bones-forge/watch/site_pass_20261030/heu/fg_fix/`.

## HEU2-10: entry 24 (Faults) and item 22 (Guards) mixed numerators

- **Was.** Faults 24: "per reply it read 27.3% → 27.4% → 47.4%, a collapse on the third day at +3.02 widths, resolved. Per thousand words it read 0.79 → 0.69 → 0.88 — +0.97 widths, nothing happened. The replies on the third day were simply longer." Guards 22: "read as a collapse on the third day at +3.02 widths, resolved, measured per reply — and as nothing happened, +0.97 widths".
- **Record.** `triangulation/triangle/runs/hook_fires.log` rows 1 to 374 (row 374 = 2026-10-08T16:31:51, seated session 1fecc2b7), recounted by `fg_fix/recount_heu2_10.py`:

  | seated, by day | replies | pushbacks (any) | frames ("Two-lane") | words |
  |---|---|---|---|---|
  | 6 Oct | 33 | 9 | 9 | 11,349 |
  | 7 Oct | 186 | 51 | 42 | 60,678 |
  | 8 Oct | 76 | 36 | 30 | 34,113 |

  Pushbacks per reply 27.3 / 27.4 / 47.4%. Frames per reply 27.3 / 22.6 / 39.5%. Frames per 1,000 words 0.79 / 0.69 / 0.88. Pushbacks per 1,000 words 0.79 / 0.84 / 1.06. The reviewer's figures reproduce.
- **Width definition, found and reproduced.** `triangulation/triangle/audit_guard.py` lines 78 to 106 (8 Oct, the script that first printed both numbers). Per reply: p = k/n, se = sqrt(p(1−p)/n). Per 1,000 words: r = 1000k/w, se = 1000·sqrt(max(k,1))/w. Width count = (day − previous day) / sqrt(se_day² + se_prev²). Its frame count (occurrences of `frame(s): "`) equals the Two-lane row count on every day (9/42/30). With this rule, day 3 against day 2: **pushbacks per reply +3.02** (the printed +3.02), **frames per 1,000 words +0.97** (the printed +0.97). So the printed pair mixed numerators, as the review said. `recount_heu2_10.out`, block "widths, audit_guard.py rule".
- **Same numerator (frames), same rule.** Per reply, day 3 against day 2 is **+2.64** (ABOVE at the script's two-width line). Per 1,000 words it is **+0.97** (CONSISTENT). So the lesson still holds on one numerator: the per-reply ruler reads a rise and the per-word ruler does not. The plain cross-check (day 3 against days 1 and 2 pooled; two-proportion z, Poisson z) gives the same picture: frames +2.72 per reply, +0.91 per 1,000 words. Pushbacks give +3.20 and +1.08.
- **Now.** Faults 24 (line 126): frames per reply 27.3% → 22.6% → 39.5% (9 of 33, 42 of 186, 30 of 76), "above the second at +2.64 widths". Per thousand words 0.79 → 0.69 → 0.88, "consistent with the second at +0.97 widths". "38 per cent longer on average than the second day's" replaces "simply longer" (mean words per reply 448.9 against 326.2, `recount_heu2_10.out` "day3 vs day2 longer by 38%"). The width definition and the two-width line are printed. Following Guards 16 (the wrong first reading is published beside the corrected one), one sentence keeps the earlier pushback series as what it was: "An earlier version of this entry printed pushbacks of any kind per reply (27.3% → 27.4% → 47.4%, +3.02 widths) beside frames per thousand words, two different numerators. Both rows now count frames." Bones can cut that sentence if he does not want the erratum on the page. Guards 22 (line 116) gives the same two readings and points to Faults 24 for the width. "Collapse" is gone. The third day rose.

## HEU2-11: "thirty-eight separate checks"

- Guards has **39** numbered items, 1 to 39 each once (parsed from `<h3>N.` in GUARDS.html, and 39 in the rendered PDF once pypdf's split digits are joined).
- **Now** (line 25): "So the guards are not a list of separate checks. They are mostly one check, …". The count is dropped because this is lead copy (HEU2-18).

## HEU2-12: item 36 "forty-four modes"

- Faults has **45** numbered modes, 1 to 45 each once (44 sits after 21 and 45 at the end, by design). There are 8 families.
- **Now** (line 172): "The eight family headings — not the individual modes — are injected". I dropped the number instead of writing "forty-five" because `heuremen-specbook/site_rules.json` rule 0b.4 says "Faults is a running list: no fixed count of modes in prose". If Bones prefers the number, "forty-five" is the count.

## HEU2-13: "not at all", "does not work", "does not improve", "nothing happened"

- **Reading.** Frames per 1,000 words 0.79, 0.69, 0.88. Under the 8 Oct width rule each day is within one width of the day before (−0.35, then +0.97). Day 3 against days 1 and 2 pooled (30/34,113 against 51/72,027): rate ratio **1.24**, exact 95% interval **0.76 to 1.99** (conditional binomial, Clopper-Pearson). So a fall of more than 24% by day 3 is outside the interval. CONSISTENT with no change. `recount_heu2_10.out`, block "HEU2-13 bound". The pooled comparison was chosen today after the data, and the page says so (P10).
- **Now.**
  - Faults 41 (line 186): "Flat." and "No improvement that clears its own width. The corrections landed individually and changed the rate not at all." became "each day within one width of the day before (widths as in entry 24). Against the first two days pooled, a comparison chosen after the data, the third day ran at 1.24 times the rate, exact 95 per cent interval 0.76 to 1.99, so a fall of more than 24 per cent by the third day is outside what was measured … The corrections landed one at a time, and the rate shows no change that clears its own width." "The flat trend holds" became "the comparison across days assumes the precision held steady across them". The 20 to 35 per cent precision figure and its ledger snippet are unchanged. "both by Claude models" was dropped while that sentence was rewritten to remove its semicolon (no statements about AI in text we write). It is now "on two separate readings".
  - Guards heading (line 27): "structure, because discipline was measured and it does not improve" became "structure rather than discipline". In line 28, "That was measured and it does not work … Flat. … changed the rate not at all" became the same reading and bound as Faults 41.
  - Guards line 32: "and the flat rate above is the evidence that it never had it" was dropped. The sentence now ends at "a job it never had."
  - Guards 36 (line 177): "moved the underlying rate not at all" became "over three days and 96 pushbacks, the underlying rate showed no change that clears its own width."
  - "nothing happened" in Faults 24 and Guards 22 became "consistent … +0.97 widths" (HEU2-10).

## HEU2-14: compression named as the cause

- **Record.** `recount_heu2_10.out` and `recount_heu2_14_lengths.out`: cold 44 of 77 = 57.1% (77 separate sessions), seated 81 of 295 = 27.5%, seated pushbacks 96 of 295 = 32.5%. Lengths: cold min 297, middle half 689 to 1,246, median 1,052, max 1,631. Seated min 151, middle half 268 to 428 (25th percentile 267.5, half-up), median 342, max 1,012. No seated reply reaches the cold median (0 of 295).
- **One correction to the brief.** "The arms do not share a length range" is not true as written. The full ranges overlap from 297 to 1,012 words: 15 of the 77 cold replies sit at or below the seated median, and 190 seated replies are 297 words or longer. What holds is that the **middle halves** do not overlap. The page says that, with the numbers.
- **Now.** The Faults 20 heading (line 94) is "The two-answer question that has three answers", with no count and no mechanism. The text (line 95) gives the two rates with their counts, the 32.5% pushback rate with its count, the middle-half lengths and medians, "we cannot tell whether context reduces the rate", and "Context did not remove it." "This is not a knowledge failure" and the compression sentence are gone. "one-shot agents" is now "one-shot sessions". In Guards, "And it is not ignorance … because reducing three states to two is what compression does, and knowing better does not stop it" (line 29) became "Context did not remove it either", followed by the two rates with counts, the middle halves, and "we cannot tell whether context reduces the rate". "fresh instances" is now "fresh sessions". The CANNOT_TELL row `faults.frame_pair` still matches.

## HEU2-15: unreceipted figures

| figure | where | search result | action |
|---|---|---|---|
| "four times in five" | Guards 25 | Not found (RESULT.md line 42 "NOT FOUND"; Faults 27 dropped it on 25 Oct, `ligera/FAULTS.pre-drop2-20261025.html` line 136 against FAULTS.html) | **Removed** like Faults 27: "An independent reviewer that rejects deliberate faults with the evidence in hand inverted both of its verdicts …" (line 125) |
| "about 1,805 words of copy before, 542 after" | Faults 45 | **Not reproduced.** Re-read the six business pages (index, qia, iris, approach, about, contact) at every 23 Oct commit in the indahl-ai git history, three ways (`recount_heu2_15_words.out`). 1,805 appears once, by the count that leaves out nav, header and footer, at commit 92110db0 (09:09, before the afternoon catches). 542 appears at no commit (nearest 529 at e6b9e6d8 and 544 at 4de8313e). Before the first afternoon edit (e32f834c, 12:02) to the last (de2ea72f, 13:22): 1,859 → 522 by that count, 1,752 → 446 by the tone gate's visible-text count. Either way more than 70% was cut. | **Removed the figure.** Line 196 now reads "On the same six pages, with the same offer and the same form, most of the copy was cut." If Bones wants a number back, 1,859 → 522 (commits e32f834c → de2ea72f, words outside nav/header/footer) is reproducible from git |
| "catches that morning's version 23 times" | Guards 39 | **Reproduced.** `heuremen-specbook/tone_scan.py` was last written 23 Oct 13:25:48, so it is the 23 Oct scanner. Run on the 12 top-level indahl-ai pages at e32f834c (23 Oct 12:02) and efcef4c6 (12:58): 23 hits. At de2ea72f (13:22): 0 hits, which also bears out "passes the corrected site with no hits". `recount_heu2_15_tone.out` | **Kept** (line 204) |
| "fired on 11 lines of the approved site" | Guards 39 | Found as a dated note written at the time: `heuremen-specbook/tone_scan.py` lines 5 to 6. The page-wide check itself was narrowed and cannot be re-run | **Kept** (receipt only, same class as RESULT.md's "matches a dated receipt only") |
| "14.5 ps … 20.9 ps" | Faults 1 | Found as dated notes: `ligera/EL_NINGUNO_FOLDED_INTO_FALLAS.html` line 52 (mtime 10 Oct 20:32) and `watch/tonight_on_K.py` line 75 (10 Oct 21:06, "(20.9 - 14.5) / 14.5 … median none amplitude, shortest band against longest, over a 0.6T-1.8T pool"). No script or raw output found | **Kept** (receipt only) |
| slopes "−1.8 to −2.9" | Faults 1 | Found as a dated note: `ligera/EL_NINGUNO_FOLDED_INTO_FALLAS.html` line 52 ("fitted log-power slopes against log-frequency run from −1.8 to −2.9"). No script or raw output found | **Kept** (receipt only) |

The reviewer reported no record for the last four. The two ligera/watch notes were missed by that grep. Bones decides whether "dated note, raw rows not kept" is enough for a public figure. RESULT.md has already kept others on that basis.

## HEU2-16: dates

Header and footer of both documents now read "10 October 2026, revised 30 October 2026" (Faults lines 21 and 203, Guards lines 21 and 240). Dates inside the text that name the ledger window (10 to 22 October 2026) are unchanged.

## HEU2-17: company name

"Heurémen" (`Heur&eacute;men`) became "Heuremen LLC" in both bylines and both footer lines. The bylines stay "Wayfinder and Bones". The separate "Heuremen LLC / We found it." footer block is unchanged, so the name now appears twice in each footer area.

## HEU2-18: counts in lead copy

- Faults lead (line 23): "This document replaces three earlier ones — …" became "This document replaces earlier ones: a trail of numbered lessons, a document about two-answer framing, and a shorter version of this catalogue." Also "the only thing that makes any of it checkable" became "what makes any of it checkable".
- Faults footer (line 203): "in eight families" became "grouped in families", and "the three earlier ones" became "the earlier ones".
- Guards lead (line 23): "two of them are recorded as having been removed" became "the guards we removed for making things worse are recorded in the last part", and "replace three earlier ones" became "replace earlier ones".
- Guards organising principle (line 25): "thirty-eight separate checks" dropped (HEU2-11).
- `heuremen-specbook/count_scan.py` (the 0b.5 gate site_gate.py calls on these two files) reports **0 hits** (`run_gates.out`).

## HEU2-19: semicolons, "apparatus", "hand-labelled"

- Semicolons in visible text: Faults 17 → **0**, Guards 20 → **0** (`semis.py` on the sources). Both rendered PDFs extract with 0 semicolons (`check_pdfs.out`). Each was rewritten as two sentences or a comma list. In the Guards score table cell, "above the point bar; borderline … 25.1%; Fisher p" became commas. The ledger snippet "borderline against the bar" is kept.
- "apparatus": Faults 3 → 0, Guards 7 → 0. Each became "setup", including the Faults 9 heading "An unequal setup across the columns being compared" and the Guards 6 heading "The setup is equalised across every column being compared".
- Faults 23: "hand-labelled cases" became "cases labelled after reading each one in full". There is no "by hand", "hand-checked" or "hand-read" in either file (site_gate 0b.9 regex, `run_gates.out`).

## Render and gates

- Render method: `ligera/render.sh` (glyph gate, then headless Chrome `--print-to-pdf --no-pdf-header-footer`, then a check that every source codepoint is in the PDF font map). This is how the 25 Oct PDFs were made. Both passed: Faults 13 codepoints, Guards 6, 0 unvetted, all present. Output is in fg_fix only.
- Text checks (`check_pdfs.py`): 0 semicolons. None of the removed phrases remain (apparatus, Heurémen, by hand, hand-, compression, ignorance, not at all, does not work, does not improve, nothing happened, a collapse, four times in five, 1,805, 542, forty-four, thirty-eight, three earlier, eight families, "Flat.", revised 22 October, Claude). Every changed figure is present. Three bold figures ("+0.97 widths" twice, "27.5 per cent of 295 replies") extract with a space inside a number ("+0.9 7", "29 5"). That is pypdf splitting kerned bold digits, and the page images show them whole. The old PDFs extracted those cleanly, so a text-layer reader of the new PDF may see the split. Worth one look in Preview before ship.
- Numbered headings in the PDFs: Faults 45 (1 to 45), Guards 39 (1 to 39).
- Gates (`run_gates.py`, the way site_gate.py calls them): count_scan 0 hits, site_rules forbid patterns 0 hits (including 0b.4 "4N modes"), 0b.9 hand wording 0 hits, glyph_scan 0 unvetted. tone_scan is scoped to the indahl.ai business pages only. Run here for information, it gives Faults 9 and Guards 12 hits, **identical to the pre-edit backups** (the quoted phrase list in Guards 39, "honest", "actually" and so on).

## Not fixed, or left for Bones (found while reading, outside the brief's list)

1. **Faults 41 heading** "The guard will not teach you, and that is not a reason to remove it", and in its text "Knowing a failure mode does not prevent it." Both are stronger than the reading under them (CONSISTENT with no change, bound printed). The same kind of claim as HEU2-13, but not on the brief's phrase list.
2. **Guards line 28** "The most common failure — reducing a situation with three states to two options". The same document (line 25) and Faults I say family I (baseline built afterwards, 217 of 316) is the largest. Two-option framing is mode 20 in family IV. Internal inconsistency.
3. **Guards line 31** "a deterministic check beat repeated instruction … for a mechanical reason". Verdict word with no figure, and a mechanism named.
4. **Statements about AI in existing text** I did not write: Guards lead "a language model doing measurement work", Faults 45 "It is the assistant's default register", Guards 1 "placed in front of the model". I removed only "both by Claude models" (Faults 41), because that sentence had to be rewritten anyway.
5. **Faults 37 and Guards 31** say "five times" and list four instances.
6. **Guards score table** "borderline" is not one of the four outcomes. Ledger row `guards.exact_bar` records it as CONSISTENT (Fisher p 0.058). Left as is, because the reviewer listed the table under HOLDS.
7. **Referee notes on the three-day series** (`iris_index/recounts/seed_faults_guards/REFEREE_OWN.md` lines 8 and 18) are not on the page. (a) The 20 to 35% precision was measured on 8 to 9 Oct rows, after a scanner fix, so it prices a later scanner. (b) 36 seated rows are rewrites within 3 minutes of a pushback (dependence, Faults 6). (c) The 374 rows were the scanner's tuning set. On "the scanner rule changed on 7 Oct inside the window": the record shows the numeric-"vs" exemption went in after 6 Oct 21:30:42 (`triangulation/triangle/triangle.py.bak-preNumVs` lacks it), before the first seated row (5 earlier rows, none seated). The false-positive fix went in after 8 Oct 16:36 (`bak-preFalsePositive`), after the 374-row cut. No backup exists between those two times, so a 7 Oct change can be neither confirmed nor ruled out.
8. **Erratum sentence in Faults 24.** I added it per Guards 16. It is Bones' call whether it stays.
9. **"An independent reviewer"** (Faults 27, Guards 25) is unchanged. The house note against "independent reviewer" is for business pages. These are the science documents.
10. **HEU2-22, zenodo surface**: `ledger.py SURFACES['zenodo']` still points at the v4 form. That is a ledger.py edit, outside this lane.
11. **Nothing copied or shipped.** `ligera/FAULTS.pdf`, `ligera/GUARDS.pdf`, heuremen.org/*.pdf and public_mirror are untouched. Release goes through `ledger/ship.sh` once the ledger rows in `LEDGER_TODO_FG.md` are in.
