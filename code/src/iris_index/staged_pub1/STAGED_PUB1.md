# Pub #1 correction batch: STAGED, NOT DEPLOYED (Ralph item 2, 25 Oct). Live faults.pdf / guards.pdf unchanged (sha 6bd0d808 / 957cad2e).
Files: FAULTS.staged.html, GUARDS.staged.html, faults.staged.pdf, guards.staged.pdf, faults.diff, guards.diff (text diffs),
APPLY_ON_DISCO.sh (ledger rows, then sources, then check_ledger; not executable on purpose; ship.sh by hand after).
Changes, each with its evidence (recounts/seed_faults_guards/RESULT.md + REFEREE_OWN.md; pub2/S1_seat_floor/RESULT.md):
1. Faults 20 + Guards first principle: 32.5% -> 27.5% frames (32.5% kept as "any pushback"); "context cuts it by about two fifths"
   WITHDRAWN to "we cannot tell whether context reduces it" (arms share no length range; logit +0.21 [-0.46, +0.89]). "Does not remove it" kept.
2. Faults 41 + Guards: "every one acknowledged and corrected on the spot" removed (not verifiable from the log); "flagged frames" ->
   "replies flagged for a two-option frame"; scanner precision 20-35% and human-prompt floor 0.28-0.58 per 1k printed beside the level.
3. Guards score table: "+15.4 widths" -> borderline against the bar's own exact interval (Fisher p 0.06 two-sided).
4. Faults 16: "of the coupled cases we have been able to decide" narrowed to the large-cross-term cases.
Ledger coverage gap closed by the script: the 57.1/27.5 pair and scanner precision get rows; guards.widths is withdrawn with evidence.
Open for the referee: the "+5.42" first-twenty figure in the same table row uses the same exact-bar issue.

## Referee on the staged diff (Sonnet, read-only, 25 Oct): applied
- "hand-read" -> "4 or 7 of 20 ... on two readings, both by Claude models" (the reader was not a human).
- Context sentences: added "the two groups barely overlap in length, so a length adjustment cannot separate them".
- Faults 16: now says the count reflects the test's behaviour, not the physics.
- Guards line 176: "96 corrections" -> "96 pushbacks".
- "+5.42 widths" removed; first twenty rows printed as 8 of 20 (40.0%, exact 95% 19-64%), above the bar's interval (Fisher p 0.01).
- APPLY_ON_DISCO.sh: ids added to all three `add` lines (would have aborted under set -e); precision row sourced to REFEREE_OWN.md.
- Open, outside this batch (his call): the "four of five" referee claim and the 0.0005 width are receipt-only or not found; the unaided
  share is not stationary across the ledger (16-47% by 100-row block; rows 609-781 42.8%).
