# Flock training round 1: plan, written and stamped before any training row is read (6 Nov 2026, Sage's ruling of 19:05Z, numbers by Bones)

STUDENT: Qwen/Qwen3-1.7B (Apache-2.0), mlx-lm in ~/bones-forge/venv on the Mac, LoRA. Same base as YO. It is not a flock voice, so it never grades itself.
SOURCE: sage_flock/flock.db, table turns, rows with prompt_v = 'v2' (the format-fixed integrator), FaultsBench rounds r2..r14 only.

FREEZE: the set is frozen at the FIRST of (a) 1,500 distinct questions (round, item) that have at least one scored-OK turn, or
(b) 2026-11-08 12:00Z. Rows written after the freeze are never used in round 1.
SET RULES:
- Unit = distinct question, not turn. At most 2 samples per question (integrator first, then voices), picked with seed 20261108.
- Only turns the CODE scored OK. Sage's rulings are labels, never training rows.
- Mix fixed now: at least 40% of questions are HARD (some voice in that cycle scored FAULT or MISS). If fewer exist, take every hard one and print the shortfall.
- UNREAD, EMPTY_REPLY, CALL_ERROR and TIMEOUT turns are counted and printed in the denominators, never trained on.
BUDGET (fixed, no stopping "when it looks good"): LoRA on 16 layers, rank 8, lr 1e-5, batch 4, exactly 1 epoch (iters = ceil(rows/4)),
loss on the answer only (prompt masked; the v1 YO pilot collapsed to "I" with loss on prompt tokens). One seed (61). No retries.

EVAL, ONCE: rounds r15 + r16 (340 questions never worked by the flock), base and trained, bare prompt, temperature 0.7, 3 samples each,
num_predict 1200, scored by each round's own score.py cls().
- Primary: fault rate on scored questions (FAULT or MISS over FAULT+MISS+OK), per sample.
- WIN only if trained beats base by more than the base's own sample-to-sample spread (the rerun floor: largest pairwise gap among the
  base's 3 samples) AND the paired exact test on discordant questions (sample 1) gives p < 0.05. Otherwise CONSISTENT (print the bound) or CANNOT_TELL.
- Unreadable rate reported separately from accuracy. Bones hand-scores 30 questions per arm, blind to arm, with a lenient parse, to split
  "learned to be parseable" from "learned to be right".
CAVEAT carried into any sentence: r15-r16 are the same fault families as r2-r14, so a win shows generalization inside FaultsBench, not outside it.
SEPARATE LATER RUN (not this plan): questions behind Sage's cards with an outside record only (the Anvil 300 Hz check at cycle 139007 vs -15.5 dB, NOAA Kp tables, IBM job tags).

## Addendum 1 (6 Nov ~19:55Z, before the freeze and before any training row is read; Sage's ASK at 19:42Z)
A1. P3 turns enter the set only if every percentage in the text recomputes from the item's own two counts to 2 decimals (or the text gives no
    number). A verdict-correct turn with a wrong number (e.g. Prism P3_06, "67.198%" for 135/201 = 67.16%) is excluded and counted.
A2. Copy-through: an integrator turn whose first 200 characters (normalized, at least 40 characters) equal a voice's is a COPY. Copies are never
    integrator samples. They count once, as that voice's sample. Copy rate per integrator is printed beside every result (at 19:50Z, prompt v2:
    Mesa 55/294, Flint 33/133, Prism 2/91, Anvil 2/4).
A3. Parser wording bias: UNREAD rows never train, so turns that state a verdict without the parser's words (e.g. Flint #72 r4/P1_25, "No, System A
    is not better than System B", UNREAD) are lost. Before the freeze, Bones hand-reads 20 random P1 UNREAD turns and prints how many carry a
    readable verdict. If more than 2 of 20 do, the set prints that loss by family, and the eval reports lenient-parse accuracy beside strict.

## Addendum 2 (6 Nov ~20:10Z, Sage's ruling of ~20:05Z; before the freeze and before any training row is read)
B1. The integrator prompt stays fixed at v2 through round 1. Copy rate is reported, not engineered.
B2. A second copy measure, reported beside A2's: does the integrator's code class (RIGHT = OK, WRONG = FAULT/MISS, UNREAD) follow the majority
    class of its voices? Reported split by majority RIGHT and majority WRONG. Following a wrong majority is the failure; following a right one is
    agreement. This uses the scored class as the verdict proxy, not the parsed wording, and says so.
B3. "Argue against the voice you agree with" is tested only as a separate arm on stored rounds r2-r14 questions, version tag v3-argue, scored by code
    and never a training candidate. It runs after the round-1 freeze so it can't slow round 1.
B4. The A3 hand-read is seeded. Seed 20261106, 4 P1 UNREAD turns per triangle (Mesa, Prism, Anvil, Pebble, Flint) drawn from prompt v2 rows
    written before 20:10Z 6 Nov. A triangle short of 4 gives all it has, and the remainder comes from the others in that fixed order. The drawn
    row ids are listed in HANDREAD_A3_ids.txt, written with this addendum.

## Correction (6 Nov 19:57Z, read from the clock): Addendum 2 above says '~20:10Z' for its own time and '~20:05Z' for Sage's ruling. Both were my guesses, and both are wrong: the file was written and stamped at ~19:52Z (see SHA256SUMS_A2.ots). The B4 draw cutoff '20:10Z' was therefore in the future at draw time; the draw actually used every v2 row that existed at ~19:52Z. Nothing else changes.

## Addendum 3 (19:58Z 6 Nov, read from the clock; Sage's ruling just before it; before the freeze and before any training row is read)
C1. Lenient parse discipline. The lenient P1 patterns are written from the 20 A3 turns, so they are fitted to that sample. Before any lenient
    number is used, they are validated on a FRESH hand-read: seed 20261107, 4 P1 UNREAD turns per triangle, drawn from v2 rows not in
    HANDREAD_A3_ids.txt. The canary runs on the lenient scorer too. Strict and lenient are always reported side by side and never merged.
    With n = 20, the A3 result is worded "most" (13 of 20), never as a rate.
C2. UNREAD by seat role (dissent voice, other voice, integrator) and by family is printed beside every result.
C3. Turns cut at the token limit and empty replies stay in the denominator as nothing-returned. They are never counted as parser misses.
    A bigger thinking budget is a round-2 change, not a round-1 one.
C4. Pebble rows before the IP fix (prompt v2, CALL_ERROR or TIMEOUT tags) count toward no triangle total.

## Addendum 4 (20:06Z 6 Nov, read from the clock; Sage's rulings plus her canary build; before the freeze and before any training row is read)
D1. Parameter twins. FaultsBench items are template-generated. 62 items in r2-r14 have parameters identical to an r15/r16 item (all P1, same
    numbers, different story), listed in PARAM_TWINS_excluded.txt. They are excluded from every training candidate set, so the held-out eval
    can't be learned from a reworded twin. Sage's split_check passes on text; this check covers the gap her README names.
D2. Bare-verdict follow. An integrator turn whose class equals exactly one voice's class while the other voices differ, and whose text is a bare
    verdict (no number, under 40 characters), is a FOLLOW. Like A2 copies, it counts once, as that voice's sample, never as an integrator sample.
D3. Before the freeze, post-filter training counts are printed by triangle and by family (after A1, A2, D1, D2), so the set's lean can be read.
D4. Sage's canary (her draft, wired by Bones to the real round scorers via real_scorer.py) runs beside the stored-row canary. Its first real run is
    5 of 5 triangles caught, controls OK (sage_flock/canary_sage/out_real). It covers P3 only; P1, P2 and P4 items are a listed gap.

## Addendum 5 (20:35Z 6 Nov, read from the clock; Sage's ruling; before the freeze)
E1. Canary separation is enforced by id. The candidate builder and every count query read only the turns table. They assert, failing loudly, that
    no turns.id appears in canary.src_id as a planted row, and that no canary_sage/out_real file is ever opened by them. Dedupe and leak checks
    key on (round, item, turns.id), never on text: 10 real model turns already read "Yes, System A is better than System B.", word for word a canary plant.
E2. Post-filter counts print the D1 exclusion share beside them: Mesa lost 44 of 660 P1 rows (7%), Flint 52 of 336 (15%).
E3. The #25 grounding measure is reported on FALSE claims only. On a true claim the true percentage is the claimed one, so stating it is an echo, not a check.

## Addendum 6 (20:42Z 6 Nov, read from the clock; Sage's ruling 20:41Z; before the freeze)
F1. P3 is DROPPED from round 1 training. No P3 row enters the candidate set, whatever its code score. P3 rows stay eval and diagnostic only.
    Why: on P3, balanced accuracy (false and true claims weighted equally) is about 0.50 for nearly every model and seat cell, so a code-OK P3 row mostly
    records a yes/no habit that happened to match. No threshold is chosen after seeing the table.
F2. Both round-2 arms (llama3.2:3b on both seats; qwen3 with a bigger thinking budget and a leading Yes/No) are scored on balanced accuracy, with
    the format-failure (UNREAD) rate printed beside it, n per cell, both claim sides.
F3. The P3 lenient pattern is replaced by lenient_v2.py (stamped with this addendum, before the seed-20261107 draw is read) to fix the three
    weaknesses Sage confirmed: class set by the predicate after "is", not by any word in the span; mixed polarities give L_AMBIG, not first-match;
    the span crosses decimal points.

## Addendum 7 (00:53Z 7 Nov, read from the clock; Sage's ruling of ~23:58Z 6 Nov; written AFTER the raw count passed 1,500, before any training row is read)
G1. Gate (a) counts ELIGIBLE questions only: an OK turn counts if it is prompt v2, round r2-r14, family not P3 (F1), not a parameter twin (D1),
    and, for an integrator turn, not a copy (A2) and not a bare-verdict follow (D2). Code: freeze_count.py (stamped with this addendum). Every
    freeze record prints the raw and eligible counts side by side.
G2. Disclosure. The raw count (any OK turn, any family, any prompt version) passed 1,500 at 2026-11-07T00:18:33Z (read from turns.at), before
    this addendum. No code freezes automatically; nothing was frozen and no training row was read. At 00:53Z: raw 1,550, eligible 808.
G3. The whole eligible pool in r2-r14 (non-P3, non-twin) is 1,368 questions (items.json, all rounds), under 1,500. Gate (a) therefore cannot
    trip, and round 1 freezes at (b), 2026-11-08 12:00Z. That is the plan's own backstop, not a new date.

## Correction (7 Nov 00:54Z, read from the clock): Addendum 7 says "Sage's ruling of ~23:58Z 6 Nov". That time was my guess. The ruling reached Bones through Wayfinder after the 23:55Z update and before 00:51Z 7 Nov; its own time was not recorded. Nothing else changes.

## Addendum 8 (00:59Z 7 Nov, read from the clock; Sage's ruling received ~00:58Z 7 Nov via Wayfinder; written BEFORE any P1 turn is counted or checked)
H1. P1 interval check. A P1 OK turn that quotes a number or interval for a named option must match that option's values in the prompt. An
    option is named by its letter (A or B, with or without a noun before it: "Filter A", "System B", "A"). The option's values are the three it
    was shown: score, lower end, upper end (a, a-ha, a+ha), at the printed precision (2 decimals); a percent form (71% for 0.71) also matches.
    A number is attributed to an option when it follows that option's mention within 40 characters with no other option mentioned between.
    FLAG (swap): an attributed number equals one of the OTHER option's values and none of its own. FLAG (mismatch): an attributed number in
    [0, 1] (or its percent form) equals none of the six printed values and is not the difference of two printed values. Bare verdicts (no
    attributed number) pass. Numbers equal to a value of both options are never flagged. Code: p1_interval_check.py (stamped with this addendum
    as soon as it exists, before the count). Swap and mismatch flags are counted separately.
H2. Threshold, fixed now, before the count: if flagged turns are <= 10 % of eligible P1 OK turns (eligibility as G1), the flagged turns are
    dropped (listed in P1_INTERVAL_flagged.txt, excluded by the candidate builder). If > 10 %, nothing is applied and the count goes to Sage.
    The threshold and the rule are not changed after the count.
H3. Controls the checker must pass before the count (printed with their results): #300 (Flint r3 P1_49, ministral, swapped intervals, verdict
    right) -> flagged swap; a constructed reply with swapped numbers and the wrong verdict -> flagged swap; a constructed reply with the right
    numbers and the wrong verdict -> not flagged; a bare verdict -> not flagged; a reply quoting the right numbers -> not flagged. A failed
    control is fixed and said so before any count.
H4. P1 polarity table (before the freeze, diagnostic, no threshold chosen from it). P1 asks "Is A better than B?". The claim is TRUE on items
    with truth A and FALSE on items with truth B or CT. Per model x seat (voice, dissent voice, integrator), v2 rows, r2-r14: verdict-right
    rate (cls OK among read turns) on true-claim items and on false-claim items (B and CT also shown apart), binary balanced accuracy = mean
    of the two, three-class balanced accuracy = mean recall over A, B, CT (a constant answer scores 0.33), UNREAD rate, n per cell. A cell
    with n < 10 on either claim side is marked. If the median binary BA over cells with n >= 10 on both sides falls in [0.40, 0.60], the
    post-filter table labels P1 "verdict-right" a habit label, as P3 was. MISS and CALL_ERROR turns are excluded from read counts and printed.
H5. Correction to H4 (01:00Z 7 Nov, read from the clock; before stamping and before any count). H4 said MISS turns are excluded. That was wrong: in
    the P1 scorer MISS is a READ answer that got a decided control wrong (score.py: control -> OK if the verdict equals truth, else MISS;
    undecidable -> OK if CT, else FAULT). So read = cls in {OK, FAULT, MISS}, and verdict-right = OK among read. Excluded from read counts and
    printed: UNREAD, and any turn whose call tag is not OK (EMPTY_REPLY, CALL_ERROR, TIMEOUT).
H6. Checker failed its hand-read (01:01Z 7 Nov, read from the clock; after the count, recorded as such). The count printed eligible 2,645, flagged
    219 (8.3 %; swap 173, mismatch 46), under the H2 threshold, and the drop list was written. A hand-read of 12 flagged turns (seed 20261107)
    then found 0 of 12 to be a real swap or misread: proximity attribution assigns a number to the nearest option letter ("A is better than
    Tool B since its estimate (0.80)"; numbers written before the letter, "[0.70, 0.78] for A"), the 40-character window truncates numbers
    (0.58 read as 0.5), and a confidence level (95%) is read as a score. The H3 controls passed, but they did not contain these shapes. By the
    parser rule (more than 1 of 10 off -> CANNOT_TELL), the checker cannot tell. NOTHING IS APPLIED: the drop list is withdrawn
    (P1_INTERVAL_flagged.WITHDRAWN_checker_failed_handread.txt, kept), H1 and H2 stand unchanged, and the matter goes to Sage. A rebuilt checker
    is tested on a hand-labelled set of real turns before any count.

## Addendum 9 (01:19Z 7 Nov, read from the clock; Sage's rulings received via Wayfinder just before; written BEFORE the habit-cell count)
I0. Record: the A8 stamp (SHA256SUMS_A8) covers the plan up to and including H5. H6 was appended after the stamp. The stamped text is kept
    byte-for-byte as PLAN_TRAIN_v1.A8_stamped.md and verifies against SHA256SUMS_A8.
I1. No checker change before the freeze. P1 rows enter round 1 verdict-scored. The disclosure line in the freeze record and any write-up reads:
    "P1 rows are verdict-scored, reasoning unchecked." The hand-read of 12 flagged turns found 0 real errors. That bounds the real-error rate
    among flagged turns only loosely (95 % upper bound about 25 %), so it is not read as zero. #300 stays a real swap.
I2. A rebuilt interval checker is first tested on a hand-labelled set of real turns that includes the shapes that broke this one (number before
    the letter, number tied to the verdict, the 40-character clip, "95%"). It runs on round 2, never on round 1 after the fact.
I3. Habit-cell rule, fixed now, before any count of what it drops. On P1 v2 rows r2-r14, per model x seat (voice / dissent / integrator), the
    THREE-CLASS balanced accuracy (mean recall over truth A, B, CT, as p1_polarity.py computes it) is the score. A cell is a habit cell if its
    three-class BA <= 0.60 AND it has n >= 10 read turns in EACH of the three truth classes. Cells short of n on any class are not habit cells
    and are printed as too small. Binary BA is printed beside it and decides nothing. phi4-mini voice (binary BA 0.77, leaning yes) is not
    targeted by this rule and the rule is not adjusted to reach it.
I4. Before any habit-cell row is dropped, the count prints, by family, how many of the eligible rows and eligible questions (G1 eligibility)
    come from habit cells. The rule as stamped applies to the habit cells' P1 rows only, because only P1 was measured. The count also prints,
    for information only, what the share would be if the same model x seat were dropped in every family. If the P1 share is above 10 % of
    eligible P1 rows, or the eligible-question count falls by more than 10 %, nothing is dropped and Sage is told.
I5. The model x seat confound stands. The round-2 same-model arm separates instruction from model.

## Addendum 9 record notes (01:23Z 7 Nov, read from the clock; record only, no rule changed; Sage's reading of the A9 build)
J1. G1 is defined in Addendum 7 (line beginning "G1. Gate (a) counts ELIGIBLE questions only"). freeze_count.py's header "Addendum 7, 7 Nov" is
    correct: Addendum 7 was written 00:53Z 7 Nov.
J2. FOLLOW, as the code defines it (disclosed here): an integrator OK turn is dropped when exactly one voice in the same cycle shares its class,
    there are at least 2 voices, and the integrator's reply is under 40 characters with no digit. This also drops short bare integrator
    verdicts that agree with one voice. It is an exclusion: it costs rows and adds no error. COPY: the first 200 normalized characters (at least
    40) equal a voice's in the same cycle.
J3. The habit-cell drop applied at 9.5 % of eligible P1 rows, within half a point of the 10 % line. Close, recorded as close, rule untouched.
J4. The 604 ids in HABIT_CELLS_drop_P1.txt are every P1 v2 turn of the two cells: 268 OK and eligible (the I4 count), 30 OK parameter twins,
    204 MISS, 96 UNREAD, 6 FAULT. 268 + 30 + 306 = 604. Only P1 ids are listed (the SQL selects fam='P1').
J5. The drop is not extended to P4 or any other family. P4 has one truth class (report a non-maximum figure), so balanced accuracy is not
    defined for it. Per-cell P4 counts are printed in P2_CONTROL_P4_CELLS.txt beside the post-filter table: OK of read is 0.94 to 1.00 in every
    cell. On P4 a constant habit and the skill give the same answer, so P4 OK cannot tell them apart. qwen3:4b voice is UNREAD on 151 of 157 P4.
J6. P2 scorer positive control: in every round r2-r14, a correct answer with a 95 % interval scores OK and a bare number scores FAULT (0 of 26
    controls wrong). P2 is a hard family under the bare prompt, which never asks for a width; the instrument works. Nothing changed.
J7. Round 1 trains on P1 and P4 only. P2 contributes 1 eligible row and P3 none. The post-filter table says so.
J8. Heartbeat files use both +00:00 and Z timestamps; any parser reads both.
