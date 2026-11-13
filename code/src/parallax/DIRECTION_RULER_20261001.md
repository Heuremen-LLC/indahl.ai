# DIRECTION RULER -- 2026-10-01, Bones's field hand

Task: `CLOCKS_FROM_THREE_PLACES_20261001.md` Sec.5 showed the standard lag1/lag20 reversal
control (clock A: 65.9us forward vs 64.7us reversed) cannot see direction, because reversing
an array preserves pairwise adjacency. Build a ruler that CAN see direction: patterns of
three-or-more, non-stationarity, and the within-shot m0->m1 order (m0 physically precedes m1
inside one shot). No numeric prediction written before running. Script:
`out/the_middle/direction_ruler.py`. Raw output: `out/the_middle/direction_ruler_results.json`,
log `out/the_middle/run_log_direction_ruler.txt`. Data: `out/echo_20260928_122733/`
(ibm_marrakesh, gaps 20/50/100/250/2000us, E0/E1 files = 1500 shots each, shot order = time
order within one file). Geometry: 2000us E0/E1 m1 clouds, cutoff 0.50, same recipe as
`pre_measurement.py`. 74/78 qubits pass SNR>=1.5; 72 after excluding named blinkers q68, q76
per standing instruction. numpy only, single process, <1s runtime. 847 tries counted by the
script itself.

Pipeline check before anything else: direct lag-1 conditional on this exact binarized data at
20us reproduces the known carry exactly -- P(cur=1|prev=1) = 33.40% (n=4117) vs P(cur=1|prev=0)
= 1.30% (n=211,739) -- matching `PLACED_VS_ARISEN_20260930.md` to the decimal. Pipeline correct
before fitting or testing anything new.

## 1. Triple and quad mirror patterns -- pooled across 72 qubits, both E0+E1 files

D1 = f(001)-f(100), D2 = f(011)-f(110); each pair is the other's time-reverse. A stationary
reversible process gives D=0. "rev" = same statistic computed on the independently reversed
per-qubit sequence (not derived algebraically). Raw counts at 20us (n=215,712 windows): 001=2601,
100=2595, 011=637, 110=635 -- the mirror pairs land within single-digit counts of each other.

| gap (us) | D1 fwd | err | D1 rev | D2 fwd | err | D2 rev | verdict |
|---|---|---|---|---|---|---|---|
| 20 | +0.003% | 0.033% | -0.003% | +0.001% | 0.017% | -0.001% | both null |
| 50 | -0.001% | 0.032% | +0.001% | -0.000% | 0.014% | +0.000% | both null |
| 100 | +0.000% | 0.031% | +0.000% | +0.000% | 0.010% | +0.000% | both null |
| 250 | +0.000% | 0.029% | -0.000% | +0.000% | 0.006% | +0.000% | both null |
| 2000 | -0.002% | 0.028% | +0.002% | +0.000% | 0.004% | +0.000% | both null |

Every fwd/rev pair sums to +0.0000% exactly (the flip is a structural identity of reversing a
finite sequence, confirmed here as a sanity check, not itself evidence). **No D1 or D2 exceeds
2x its own error at any gap.** Length-4 mirrors (0001/1000, 0011/1100, 0111/1110) tell the same
story at all 5 gaps: every value is inside 1-2x its error, largest being 0001-1000 at 20us
(+0.004% +/- 0.032%). Full table (15 gap x pair-length rows) in the JSON.

**This null is well-powered, not starved**: raw pattern counts run in the hundreds-to-low-
thousands per cell (n=215,712 total windows), giving relative errors of 5-15% on the pattern
frequencies themselves -- the mirror pairs (2601 vs 2595; 637 vs 635) are symmetric to within
single-digit counts, not merely "within wide error bars." The strong two-point carry (33.4% vs
1.3%, a real and large effect) does not resolve into any three-or-four-point time-asymmetry
this ruler can detect.

## 2. Within-shot order: m0 then m1 (real time order inside one shot)

Pooled 72 qubits, E0+E1, n=216,000 per gap.

| gap (us) | P(m0=1) | P(m1=1) | P(m1=1\|m0=1) | err | P(m0=1\|m1=1) | err | Bayes check (joint both sides) |
|---|---|---|---|---|---|---|---|
| 20 | 1.91% | 49.79% | 75.72% | 0.67% | 2.90% | 0.05% | 1.445% = 1.445% |
| 50 | 1.49% | 49.68% | 73.04% | 0.78% | 2.18% | 0.04% | 1.085% = 1.085% |
| 100 | 1.26% | 49.53% | 67.18% | 0.90% | 1.71% | 0.04% | 0.844% = 0.844% |
| 250 | 0.96% | 49.39% | 64.80% | 1.05% | 1.26% | 0.03% | 0.621% = 0.621% |
| 2000 | 0.89% | 49.44% | 62.27% | 1.10% | 1.13% | 0.03% | 0.557% = 0.557% |

Both conditionals equal the same joint by Bayes' theorem exactly (verified to 3 decimals at
every gap) -- the huge gap between 75.72% and 2.90% is **arithmetic**, driven entirely by
P(m1=1)=~50% being ~25-50x P(m0=1): the second look almost always reads 1 regardless of the
first look (measurement-induced heating from the first look itself, the "look leaves heat"
effect already on record in THIRD_RUNG Sec.17), not a direction signal. The 36d "93%" line
(carried-1 reads 1 again at the second look) is a *different* statistic -- it conditions on the
*previous shot's* m0, not on the *same shot's* m0 -- and was already reported both ways in
`PLACED_VS_ARISEN_20260930.md` Sec.1e (92.7% carried vs 67.2% baseline at 20us); it is not
re-derived here since it isn't a same-shot Bayes pair. Per-qubit numbers in the JSON (15 of 360
qubit-gap cells failed: no m0=1 or no m1=1 in that qubit's 3000 shots, mostly at 2000us where
base rates are lowest).

## 3. Non-stationarity: first/middle/last third of shots

Pooled rate (72 qubits, E0+E1, n=72,000/third) and pooled D by third (n~71,712 windows/third).

| gap (us) | first rate | mid rate | last rate | drift (last-first) | D1 first/mid/last | D2 first/mid/last |
|---|---|---|---|---|---|---|
| 20 | 1.78%+/-0.05% | 1.93%+/-0.05% | 2.01%+/-0.05% | **+0.229%+/-0.072%** | +0.003/+0.001/+0.007% | +0.001/+0.000/+0.003% |
| 50 | 1.40%+/-0.04% | 1.48%+/-0.04% | 1.57%+/-0.05% | **+0.174%+/-0.064%** | -0.004/-0.004/-0.001% | -0.001/-0.001/+0.000% |
| 100 | 1.29%+/-0.04% | 1.23%+/-0.04% | 1.26%+/-0.04% | -0.031%+/-0.059% (noise) | +0.001/+0.004/+0.000% | +0.001/+0.000/+0.000% |
| 250 | 0.92%+/-0.04% | 0.94%+/-0.04% | 1.02%+/-0.04% | +0.106%+/-0.052% (~2 sigma) | +0.001/+0.003/+0.000% | +0.000/+0.000/+0.000% |
| 2000 | 0.90%+/-0.04% | 0.90%+/-0.04% | 0.89%+/-0.03% | -0.011%+/-0.050% (noise) | -0.008/+0.000/+0.000% | +0.000/+0.000/+0.000% |

A real, if slow, first-look 1-rate drift exists at the fastest two gaps (20us: +0.229pp,
3.2 sigma; 50us: +0.174pp, 2.7 sigma) -- the qubit population runs slightly hotter as each
run/job progresses. But **the drift does not translate into any triple-pattern D**: D1/D2 stay
inside 1x error in every third at every gap, no trend across thirds anywhere in this table.
Drift is real; it isn't of the shape this ruler measures.

## 4. The verdict

Per qubit (72 tested): **0/72 qubits show a significant (|D|>2x error) triple-pattern D1 or D2
at 20us gap** -- so there is nothing to check for fading with larger gap (0/1, moot). Pooled:
D1 and D2 are non-significant at every one of the 5 gaps (table in Sec.1). **By the triple/quad
mirror-pattern ruler and the within-shot Bayes ruler, this qubit population's arisen memory
shows no detectable direction, at any gap, pooled or per-qubit.** The non-stationarity ruler
finds a real (not moot) drift at 20/50us but it doesn't carry a triple-pattern signature either.

## 5. Plain words

The ~64us clock (the arisen carry from `PLACED_VS_ARISEN_20260930.md`) is a **symmetric
clustering** (ordinary bursty/telegraph autocorrelation), not a forward memory, by every ruler
built here that can actually see direction (mirror triples/quads, well-powered with hundreds-
to-thousands of counts per cell) as well as by the pair-reversal control already on record in
`CLOCKS_FROM_THREE_PLACES_20261001.md` Sec.5. The one place a large, real asymmetry does show
(P(m1=1|m0=1)=76% vs P(m0=1|m1=1)=3% at 20us) is fully accounted for by Bayes' theorem and the
qubit population's own base rates (P(m1=1)~50% from look-induced heating) -- it is arithmetic,
not a physical arrow. A real slow drift exists in the population's 1-rate at the two fastest
gaps, but no ruler here ties that drift to a triple-pattern direction. Net: **no ruler in this
set finds an arrow in this data; the carry is fully described as symmetric-in-time**, and gap
does not matter to that verdict because there was no direction at any gap to lose.

## Tries counted

847, printed by the script itself: 2 (fwd+rev) x 5 gaps x 2 pattern lengths = 20 pooled pattern
computations; 72 qubits x 5 gaps = 360 per-qubit length-3 computations; 5 gaps x 1 pooled +
72 qubits x 5 gaps = 365 within-shot computations; 5 gaps x 3 thirds x 2 (rate+pattern) = 30
non-stationarity computations; 72 qubits x 1 verdict pass = 72. Failed rows: 15 (qubit,gap)
within-shot cells where a qubit had zero m0=1 or zero m1=1 in its 3000 pooled shots (mostly at
2000us, lowest base rate) -- listed implicitly by absence from `sec2_per_qubit` in the JSON
(69/70/70/70/66 of 72 present at 20/50/100/250/2000us respectively). No other failures: every
qubit resolves in every pooled and per-qubit pattern/rate cell.
