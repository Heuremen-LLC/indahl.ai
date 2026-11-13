# DDC run: does the echo leave the readout coherence cost unchanged, or remove it?
Pre-registered. Written, SHA-256 hashed (PLAN_DDC.sha256; code in CODE_DDC.sha256) BEFORE any job is submitted. Heuremen LLC, Wayfinder
and Bones, 22 October 2026. Circuits and fire path: ddc.py (dry run against the live chips, nothing submitted). Analysis: analyze_ddc.py.
Synthetic test: synth_ddc.py (synth_output.txt, null_floor.txt, nulls/, power.txt, power/). A coherence-only repeat of the DD run
(../dd_run/, PLAN_DD.md, results_dd.txt).

KNOWN-GOOD: two real-hardware readings whose answer is already known, read in this very job on each chip. (1) R0 coherence: at N = 0 the
'echo on' and 'echo off' circuits are IDENTICAL (no step, no echo), so their coherence difference must read CONSISTENT with 0.
(2) R4, the coherence cost WITHOUT echo, resolved in the DD run (results_dd.txt, [all]): ibm_marrakesh N=2 +0.0047 [+0.0014, +0.0078],
N=8 +0.0122 [+0.0074, +0.0239]; ibm_fez N=8 +0.0044 [+0.0017, +0.0080]. This run must reproduce each within its width:
|R4_new - R4_DDrun| <= 1.96 x sqrt(s_new^2 + s_old^2), s = (95 % interval width) / 3.92. (ibm_fez N=2, +0.0023 [-0.0010, +0.0046], was
not resolved: printed beside, not required.) analyze_ddc.py prints KNOWN-GOOD PASS/FAIL per chip; a chip that FAILS has its decision
printed but NOT counted in the HEADLINE. Plumbing check: run on the DD run's own data the reproduction test passes trivially on all
required cells (posthoc_dd_run_under_ddc_rule.txt).

## What is on the record (the DD run, 22 Oct, before this plan)
A symmetric X-X echo on the 117 untouched qubits removed most of the readout phase kick on all three chips. Whether it changes the
COHERENCE COST could not be told: R6 = R5 - R4 (cost with echo minus cost without) was CONSISTENT at N = 2, 4, 8 on every chip, but its
interval half-width was 0.5 to 1.3 times R4 itself, so 'unchanged', 'removed' and 'doubled' all fit. An outside referee added: the echo
changes the idle arm's own coherence (R7), and a difference R6 cannot separate 'same rate' from 'same absolute amount'.

## The question
At N = 8 readouts: does the echo leave the cost unchanged, or remove it? Designed so the R6 interval half-width is at most about 1/3 of
R4 on the chip where the cost is largest; on the second chip the reachable width is stated (below) and is wider.

## Design: the DD run's circuits, unchanged
ddc.py IMPORTS ../dd_run/dd.py unchanged (sha256 e5363a66..., the hash in ../dd_run/CODE_DD.sha256): dd.build -> dd.dd_circuit and
dd.timing build the circuits, dd.verify checks the transpiled schedule. Only these differ from the DD run:
  N in {0, 2, 8} (was 0, 2, 4, 8, 16); N = 0 kept as the built-in null.
  12000 shots per pub (was 4000).
  chips ibm_marrakesh and ibm_fez (was those two plus ibm_kingston).
  output names job/raw/props_ddc_<chip> in this folder; the job record carries PLAN_DDC.sha256.
The fire path in ddc.py is dd.py's __main__ block line for line with those names changed (dd.py's own __main__ hard-codes its folder),
plus two asserts (chip is pre-registered; N set and shots as stated) and a max_shots check.
Everything else is the DD run: E = the same 39 measured qubits (countwide_roles_<chip>.json), S = the other 117, spectators on the
equator; per step a full barrier, E measured (arm M) or idle exactly L (arm D); S idle (echo off) or delay d1, X, d2, X, d3 filling L
(echo on); arms D/M x echo on/off at N = 2, 8, plus N = 0 under each echo label; settings XX, YY. 20 circuits x 2 copies = 40 pubs,
shuffled (seed 20261022 + 11), optimization level 1, identity layout, ALAP.

Dry run, 22 Oct 2026 (dryrun_ibm_marrakesh.log, dryrun_ibm_fez.log): timing identical to the DD run
  ibm_marrakesh  L 671 dt, X 9 dt -> echo 163 / X / 327 / X / 163 dt; circuits 2.8 / 8.1 / 24.2 us (N = 0, 2, 8)
  ibm_fez        L 415 dt, X 6 dt -> echo 100 / X / 203 / X / 100 dt; circuits 1.7 / 5.0 / 15.0 us
  VERIFIED on both (dd.verify, raises on failure): 2N X per spectator with echo, 0 without, none on a measured qubit; every step exactly
  L; step block and total scheduled duration identical echo on vs off for every (arm, N, setting, copy). max_shots 100000.

## Seconds (dry run; per-shot model of the deciding runs, shots x (duration + 290 us))
  ibm_marrakesh 146 s, ibm_fez 143 s. TOTAL 289 s (budget ~300). Remaining at writing: 780 s. (DD run: fez estimated 87 s, billed 80 s.)

## Chips, chosen from results_dd.txt BEFORE any new data
  ibm_marrakesh: the largest cost and the most stable. R4 ABOVE at every N (+0.0047, +0.0064, +0.0122, +0.0166 at N = 2, 4, 8, 16),
    growing with N; no copies shifted on any R4, R5 or R6 reading; R5 ABOVE at every N; R7 ABOVE and steady (+0.030 to +0.041).
  ibm_fez: second. R4 ABOVE at N = 4, 8, 16 (+0.0043, +0.0044, +0.0036); one copies-shifted reading in its 66 (1.5 %), none on R4-R6.
  ibm_kingston NOT chosen although its R4 at N = 8 (+0.0052) is a little larger than fez's: its copies shifted on 5 of 66 readings, 4 of
    them R6 (N = 4 unwired, N = 8 all, N = 16 all and wired), i.e. exactly the reading this run decides on, at the deciding N; under this
    plan's rule that is CANNOT TELL before any width question.
  (fez's R7 changes sign across N, +0.019 at N = 2, -0.017 at N = 8: noted, not a reason to exclude it; R7 is printed.)

## Sizing (the arithmetic)
Readings are medians over the 117 spectators with a 2000-resample bootstrap. For a median, 95 % half-width ~= 1.96 x 1.2533 x sigma /
sqrt(117) = 0.227 sigma, sigma = the per-spectator spread (robust: 1.4826 x MAD). Check on the DD run: fez R6 N=8 MAD-sigma 0.0205 ->
0.0047 predicted, 0.0045 observed.
Per-spectator spread of R6 at N = 8 in the DD run (4000 shots), split into shot/copy noise and spectator-to-spectator spread:
  noise  = MAD-sigma of (copy0 - copy1) / 2   (the pooled value's noise)
  spread = sqrt(total^2 - noise^2)             (does NOT shrink with shots)
                  total    noise(4000)   spread    R4 (N=8)
  ibm_marrakesh   0.0223   0.0182        0.0129    0.0122
  ibm_fez         0.0205   0.0176        0.0105    0.0044
  (ibm_kingston   0.0169   0.0141        0.0093    0.0052)
Projected half-width h(shots) = 0.227 x sqrt(spread^2 + noise^2 x 4000/shots):
  marrakesh: target h <= 0.0122/3 = 0.0041 -> needs noise <= 0.0126 -> shots >= 4000 x (0.0182/0.0126)^2 = 8400.
             At 12000: noise 0.0105, sigma 0.0167, h = 0.0038 = 0.31 x R4. MEETS the target.
  fez:       target h <= 0.0044/3 = 0.0015 needs sigma <= 0.0065, below the spread alone (0.0105): NOT reachable at any shot count
             (floor 0.227 x 0.0105 = 0.0024 = 0.54 x R4). At 12000: noise 0.0102, sigma 0.0146, h = 0.0033 = 0.75 x R4. That still
             separates 0 from -R4 when the truth is at either end (h < R4), but not reliably; fez is the replication, marrakesh the test.
  Budget: equal 12000 shots on both = 289 s. Shifting shots to marrakesh buys little (16000 -> h 0.29 x R4) and costs fez more.
The spread is estimated as a difference of two noisy MADs; it is uncertain by perhaps +-30 %. The new run measures R4 afresh, so the
achieved ratio is printed by the analysis ('R6 half-width = x R4').

## The ruler (unchanged)
analyze_ddc.py imports ../dd_run/analyze_dd.py unchanged (and through it deciding_runs/analyze.py), sets its NSTEP to (2, 8), and prints
every DD-run reading R0-R8 at N = 2, 8 (with two N the phase slope R1-R3 is the line through the two points; phase readings are context
here). Every reading: per spectator, median, 95 % bootstrap, ABOVE / BELOW / CONSISTENT / CANNOT TELL; copies compared per spectator
(interval of copy0 - copy1 excludes 0 -> CANNOT TELL); chips combined only by inverse variance with chi2/dof. Printed [all], [wired],
[unwired]; the decision uses [all] only.
Added after the DD readings (nothing before them changes):
  R9   R6 as a FRACTION of R4: median(R6)/median(R4), paired bootstrap over spectators. 0 = unchanged, -1 = removed, +1 = doubled.
  R10  RATE form: per spectator, per-readout loss -ln(coh_M/coh_D)/N with echo minus without (spectators with both arms above the R8
       floor). CONSISTENT = the echo leaves the per-readout RATE unchanged.
  R11  What 'same rate' predicts for R6: R4 x (coh_D,on/coh_D,off - 1), per spectator, median and interval, NO outcome, not in the tally.
       'Same absolute amount' predicts R6 = 0. The two differ by about R4 x R7/coh: on the DD run, R11 at N=8 was +0.0002 [-0.0001,
       +0.0010] on marrakesh; far below any reachable R6 width (~0.004). This run can NOT tell 'same rate' from 'same amount'; R10 and
       R11 are printed so the reader sees how far apart they are.
  R7   (from the DD readings) the echo's own effect on the idle arm, printed at N = 2, 8.

## DECISION RULE (N = 8, per chip; [all]; written before data)
Let R4, R5, R6 be the pooled readings at N = 8, h = R6 half-width.
  0. CANNOT TELL if copies shifted on R4, R5 or R6; if R4 is not ABOVE ('no cost resolved'); if h > R4 ('too wide for a cost this small').
  1. THE ECHO DOES NOT REMOVE THE COST: R6 CONSISTENT with 0 AND the R6 interval EXCLUDES -R4 AND R5 ABOVE.
  2. THE ECHO REMOVES THE COST: R6 BELOW 0 AND the R6 interval CONTAINS -R4 AND R5 CONSISTENT.
  3. THE ECHO REDUCES THE COST, PART REMAINS: R6 BELOW, interval excludes -R4, R5 ABOVE.
  4. THE ECHO OVER-REMOVES: R6 BELOW, interval excludes -R4, R5 BELOW (readout arm ends MORE coherent than idle).
  5. THE ECHO INCREASES THE COST: R6 ABOVE.
  6. CANNOT TELL (too wide): R6 CONSISTENT and the interval contains -R4 (the DD run's situation).
  7. CANNOT TELL (forms disagree): anything else.
'-R4' is tested twice: LITERALLY (the R6 interval against the R4 point value) and PAIRED (R5 = R6 + R4 spectator by spectator, so
'R6 = -R4' is 'R5 = 0', which carries R4's own uncertainty). Both must agree. R9 (ratio) is printed beside every decision.
HEADLINE (from the per-chip decisions of chips that PASS KNOWN-GOOD): the same verdict on both -> that verdict, both chips; a verdict on
one and CANNOT TELL on the other -> that verdict on ONE chip, named; different verdicts -> CHIPS DISAGREE; none -> CANNOT TELL.
The inverse-variance combination of the two chips is run through the same rule and printed as CONTEXT, not the headline (in the power
test below it gave one wrong verdict in 12; the per-chip rule gave none).
R0 or KNOWN-GOOD failing on a chip removes that chip from the headline; the readings are still printed.

## FLOOR AND POWER (measured on the analysis before any job)
Synthetic data in the job's own schema (synth_ddc.py): ddc.py's real circuit list built on FakeMarrakesh and FakeFez, 12000 shots, two
copies, both chips in one folder; synth_dd.py's world (per-spectator coherence 0.55-0.95, 6 dead clocks, decay 0.4 %/step, own phase and
drift, the echo with no effect of its own) PLUS the measured per-spectator spread: cost_off = 0.008 + N(0, 0.027 marrakesh / 0.012 fez);
the echo's change per spectator N(0, 0.013 marrakesh / 0.0105 fez), mean 0. No kick planted. Planted cost 0.008 is SMALLER than
marrakesh's real 0.012, so the synthetic ratios on marrakesh are worse than the projection for the real chip.
 - Seed 5 (synth_output.txt; the three cases share one world and its draws):
     UNCHANGED: fez R4 +0.0082 [+0.0059, +0.0109] ABOVE, R5 +0.0079 ABOVE, R6 +0.0001 [-0.0028, +0.0018] CONSISTENT (h = 0.28 x R4),
       R9 +0.01 [-0.34, +0.29] -> DOES NOT REMOVE. marrakesh: R0 and R4 copies shifted -> CANNOT TELL, KNOWN-GOOD FAIL.
       HEADLINE: DOES NOT REMOVE, on ibm_fez. Correct.
     REMOVED: fez R5 +0.0011 CONSISTENT, R6 -0.0075 [-0.0110, -0.0045] BELOW containing -R4 = -0.0082, R9 -0.91 [-1.32, -0.64] ->
       REMOVES. marrakesh CANNOT TELL (copies shifted, same draws). HEADLINE: REMOVES, on ibm_fez. Correct.
     NULL: R4 CONSISTENT on both -> CANNOT TELL. Correct.
 - Power, seeds 21-26 each (power.txt): HEADLINE correct in 12 of 12 (unchanged 6/6, removed 6/6), wrong in 0.
     Per chip: fez decided correctly 10 of 12 (2 copies shifted); marrakesh 8 of 12 (3 forms-disagree, 1 too wide), 0 wrong verdicts.
     Achieved R6 half-width 0.21-0.63 x R4 in 29 of the 32 decided-or-printed lines (per chip and combined); the others 0.85, 0.88, 1.19.
 - NULL floor, six seeds (11-16; null_floor.txt, nulls/): 528 readings of truth 0, 32 resolved (6.1 %; 17 ABOVE, 15 BELOW), 454
   CONSISTENT, 42 CANNOT TELL. DECISIONS: 0 verdicts in 18 (12 per chip + 6 combined); HEADLINE CANNOT TELL in 6 of 6. (Before the
   'h > R4' clause was added, one null seed on fez read REMOVES at R4 = +0.0012 with h = 2.5 x R4 and one combined null read REMOVES;
   that is why clause 0 has it. R11 was taken out of the tally because, being a product of two noisy terms, it resolved 22 times in the
   nulls; it is a prediction, not a test.)
 - The rule, applied AFTER the fact to the DD run's own data (posthoc_dd_run_under_ddc_rule.txt): marrakesh N=8 reads DOES NOT REMOVE
   (h = 0.33 x R4, R9 +0.25 [-0.13, +0.77]); fez CANNOT TELL (h = 1.02 x R4); kingston CANNOT TELL (copies shifted). This is disclosed
   because the rule was written after seeing that data; it is NOT counted. This run is the out-of-sample test.

## What would change the reading
Kingston's copy instability on R6 is a warning that a time-varying effect inside a job can shift the copies; on either chip here it
reads CANNOT TELL, never a verdict. Fez's R6 width is spread-limited, not shot-limited: a fez verdict is weaker than a marrakesh one.

## Not in this run
No phase-kick question (answered by the DD run); no other DD sequence, no echo on the measured qubits, no N beyond 8, no kingston.
