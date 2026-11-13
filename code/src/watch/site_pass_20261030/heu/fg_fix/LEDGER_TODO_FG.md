# LEDGER_TODO_FG: ledger commands for the Faults and Guards revision of 30 Oct 2026 (HEU2-10 to HEU2-19, HEU2-22)

Written by the fix agent as TEXT. Nothing below has been run. Run from `~/bones-forge/ledger/`, after Bones has read the edited
sources (ligera/FAULTS.html, ligera/GUARDS.html). Every `--grep` string was checked to be in its `--source`, and every `--on`
snippet was checked to be in the edited surface file, by `fg_fix/gen_ledger_todo.py` (it printed `all greps and snippets present`).
`--checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md` passes `watch/readcheck.py check` (core + pack P).

## 1. Existing rows on surfaces faults and guards: no change needed

All six rows on these surfaces were checked against the edited files. The five live rows still find their snippet verbatim:
`faults.frame_pair` ("27.5 per cent of 295 replies" on faults, "27.5 per cent" on guards), `faults.plato_years`, `faults.scanner_precision`
("20 to 35 per cent"), `guards.exact_bar` ("borderline against the bar"), `guards.untagged_hedge`. `guards.widths` was withdrawn on 25 Oct and
its snippet was already off the page. No printed number held by an existing row changed value, so no `set`, `off` or `on` lines are needed.

The old entry-24 figures (27.3/27.4/47.4% as a frame series, +3.02 "resolved", +0.97 "nothing happened") had no ledger row, so nothing to
withdraw. The pushback series is still printed, now labelled as the earlier mixed-numerator reading, and gets its own row below.

Note for `faults.frame_pair`: its claim text says "Fresh one-shot agents". The page now says "one-shot sessions" (Faults) and "fresh sessions"
(Guards). Optional claim wording fix (the claim field is internal):

```
python3 ledger.py set faults.frame_pair --field claim --to 'Fresh one-shot sessions 57.1% (44 of 77) vs seated 27.5% (81 of 295) of replies flagged for a two-option frame; context effect not resolved once length is modelled' \
    --why 'HEU2-14: page wording is sessions, not agents' --evidence watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out
```

## 2. New rows for the figures this revision changed or added (HEU2-10, HEU2-13, HEU2-14)

```
python3 ledger.py add faults.frame_reply_width \
    --claim 'Seated replies flagged for a two-option frame, per reply, 6/7/8 Oct (hook_fires.log rows 1-374): 27.3% (9/33), 22.6% (42/186), 39.5% (30/76). Day 3 against day 2: +2.64 widths (difference over root-sum-square of binomial SEs, audit_guard.py rule)' \
    --value=+2.64 \
    --unit widths \
    --outcome ABOVE \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'frames    10-08 vs 10-07:  per reply +2.64' \
    --on faults '27.3% &rarr; 22.6% &rarr; 39.5% (9 of 33, 42 of 186, 30 of 76)' \
    --on faults 'above the second at +2.64 widths' \
    --on guards '22.6% to 39.5%' \
    --on guards 'above the second day at +2.64 widths' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.frame_words_width \
    --claim 'Same seated rows, frames per 1,000 words: 0.79 (9/11,349), 0.69 (42/60,678), 0.88 (30/34,113). Day 3 against day 2: +0.97 widths (Poisson SEs, audit_guard.py rule); each day within one width of the day before' \
    --value=+0.97 \
    --unit widths \
    --outcome CONSISTENT \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'frames    10-08 vs 10-07:  per reply +2.64   per 1k words +0.97' \
    --on faults '0.79 &rarr; 0.69 &rarr; 0.88' \
    --on faults 'consistent with the second at +0.97 widths' \
    --on faults '0.79, 0.69, 0.88 per thousand words' \
    --on guards '0.79, 0.69, 0.88 per thousand words' \
    --on guards '0.69 to 0.88' \
    --on guards '+0.97 widths' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.pushback_reply_width \
    --claim 'Seated pushbacks of any kind per reply 27.3% (9/33), 27.4% (51/186), 47.4% (36/76); day 3 against day 2 +3.02 widths. Printed in Faults 24 as the earlier, mixed-numerator reading' \
    --value=+3.02 \
    --unit widths \
    --outcome ABOVE \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'pushbacks 10-08 vs 10-07:  per reply +3.02' \
    --on faults '27.3% &rarr; 27.4% &rarr; 47.4%, +3.02 widths' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.frame_rate_ratio \
    --claim 'Frames per 1,000 words, day 3 (30/34,113) against days 1-2 pooled (51/72,027): rate ratio 1.24, exact 95% (conditional binomial) 0.76 to 1.99; a fall over 24% is outside. Comparison chosen after the data' \
    --value=1.24 \
    --lo=0.76 --hi=1.99 \
    --unit 'rate ratio, day 3 / days 1-2' \
    --outcome CONSISTENT \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'exact 95% (conditional binomial, Clopper-Pearson) rate ratio day3/days1-2: [0.764, 1.987]' \
    --on faults 'the third day ran at 1.24 times the rate, exact 95 per cent interval 0.76 to 1.99' \
    --on faults 'a fall of more than 24 per cent' \
    --on guards 'the third day ran at 1.24 times the rate, exact 95 per cent interval 0.76 to 1.99' \
    --on guards 'a fall of more than 24 per cent' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.day3_longer \
    --claim 'Seated replies on day 3 were 38% longer on average than on day 2 (448.9 vs 326.2 words per reply)' \
    --value=38 \
    --unit % \
    --outcome LEVEL \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'day3 vs day2 longer by 38%' \
    --on faults '38 per cent longer on average than the second day' \
    --on guards '38 per cent longer on average' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.cold_frame_rate \
    --claim 'Cold one-shot sessions flagged for a two-option frame: 44 of 77 = 57.1% (hook_fires.log rows 1-374)' \
    --value=57.1 \
    --unit % \
    --outcome LEVEL \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'cold   rows 77  two-lane 44  = 57.1%' \
    --on faults '57.1 per cent of long replies (44 of 77)' \
    --on guards '57.1 per cent of long replies from fresh sessions with no context (44 of 77)' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.seated_frame_rate \
    --claim 'Seated replies flagged for a two-option frame: 81 of 295 = 27.5%; pushbacks of any kind 96 of 295 = 32.5% (hook_fires.log rows 1-374)' \
    --value=27.5 \
    --unit % \
    --outcome LEVEL \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'seated rows 295  two-lane 81  = 27.5%   pushbacks 96 = 32.5%' \
    --on faults '(81 of them), and 32.5 per cent drew a pushback of any kind (96 of them)' \
    --on guards '(81 of 295)' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.arm_lengths \
    --claim 'Words per reply, middle half (25th to 75th percentile, numpy linear, half-up): cold 689 to 1,246 (median 1,052, n 77), seated 268 to 428 (median 342, n 295); no seated reply reaches the cold median' \
    --value='689-1246 vs 268-428' \
    --unit words \
    --outcome LEVEL \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_14_lengths.out \
    --grep 'cold n 77 words: min 297 p10 308 p25 689 median 1052 p75 1246' \
    --on faults '689 to 1,246 words for the cold replies (median 1,052) and 268 to 428 for the seated ones (median 342)' \
    --on guards '689 to 1,246 words for the fresh replies, 268 to 428 for the seated ones' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

## 3. Rows the review asked for (HEU2-22) on figures this revision kept, receipts found this pass (optional, Bones decides)

Figures unchanged on the page. Sources are the recounts or the dated notes named in FIXLOG_FG.md (HEU2-15).

```
python3 ledger.py add guards.tone_scan_23 \
    --claim 'tone_scan.py (last written 23 Oct 13:25) on indahl-ai at e32f834c (23 Oct 12:02, 12 top-level pages): 23 hits; at de2ea72f (13:22): 0 hits' \
    --value=23 \
    --unit hits \
    --outcome COUNT \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_15_tone.out \
    --grep 'e32f834c: 12 top-level html, words 3130, tone hits 23' \
    --on guards 'catches that morning&rsquo;s version 23 times' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add guards.tone_repeat_11 \
    --claim 'Page-wide repeat check fired on 11 lines of the approved site (dated note in the tool written 23 Oct; the check itself was narrowed and cannot be re-run)' \
    --value=11 \
    --unit lines \
    --outcome RECORD \
    --source heuremen-specbook/tone_scan.py \
    --grep 'fired on 11 lines of the approved site' \
    --on guards 'fired on 11 lines of the approved site' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.none_band_ps \
    --claim 'Sloped none, 0.6T-1.8T pool: median none amplitude 14.5 ps in the shortest band, 20.9 ps in the longest (dated note, 10 Oct; also watch/tonight_on_K.py line 75; raw script not found)' \
    --value=14.5-20.9 \
    --unit ps \
    --outcome RECORD \
    --source ligera/EL_NINGUNO_FOLDED_INTO_FALLAS.html \
    --grep 'rose from 14.5 ps in the shortest band to 20.9 ps in the longest' \
    --on faults 'rose from 14.5 ps in the shortest band to 20.9 ps in the longest' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.none_slopes \
    --claim 'Red noise in that span: fitted log-power slopes against log-frequency from -1.8 to -2.9 (dated note, 10 Oct; raw script not found)' \
    --value='-1.8 to -2.9' \
    --unit slope \
    --outcome RECORD \
    --source ligera/EL_NINGUNO_FOLDED_INTO_FALLAS.html \
    --grep 'run from &minus;1.8 to &minus;2.9' \
    --on faults 'of &minus;1.8 to &minus;2.9' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add guards.family_217 \
    --claim 'Prospective ledger rows 1-608 tagged with one of the first three families: I 217, II 44, III 55 (217 of 316)' \
    --value=217 \
    --unit 'rows of 316' \
    --outcome COUNT \
    --source iris_index/recounts/seed_faults_guards/RESULT.md \
    --grep 'families I 217 / II 44 / III 55' \
    --on guards '217 of the 316 rows tagged' \
    --on faults '217 of the 316 ledger rows' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add guards.human_216 \
    --claim 'Prospective ledger rows 1-608: 216 catches by the human partner (35.5%)' \
    --value=216 \
    --unit 'of 608' \
    --outcome COUNT \
    --source iris_index/recounts/seed_faults_guards/RESULT.md \
    --grep '216 by Wayfinder (35.5%)' \
    --on guards '216 of the 608 catches' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

```
python3 ledger.py add faults.pushbacks_96 \
    --claim 'Seated pushbacks of any kind over three days: 96 of 295 replies (hook_fires.log rows 1-374)' \
    --value=96 \
    --unit pushbacks \
    --outcome COUNT \
    --source watch/site_pass_20261030/heu/fg_fix/recount_heu2_10.out \
    --grep 'seated rows 295  two-lane 81  = 27.5%   pushbacks 96' \
    --on faults 'Over three days, <b>96 pushbacks.</b>' \
    --on guards 'Over three days, <b>96 pushbacks</b>' \
    --on guards 'over three days and 96 pushbacks' \
    --checks watch/site_pass_20261030/heu/fg_fix/CHECKS.md
```

## 4. Not in this file

- HEU2-22 also asks that `ledger.py SURFACES['zenodo']` point at the v5 form. That is an edit to ledger.py, outside this lane.
- After the rows are in: `check_ledger.py --coverage` for faults and guards to see what is still outside the ledger.
