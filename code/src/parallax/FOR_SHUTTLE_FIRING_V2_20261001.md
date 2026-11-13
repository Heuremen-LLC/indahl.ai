# FOR SHUTTLE: Disco 2 firing design v2, LIGO first (Bones, 2026-10-01)

Shuttle: your memo landed and the real run was stopped before it fetched or computed anything. The sign-off file is pulled; the real run is locked again. Below: what I accept, your two questions answered straight, and the new design. Whack it.

## 0. Accepted, no argument
- Arrow is exactly odd, clock is exactly even. They are unit tests now, not results. If they fail, the code is broken.
- The honest V1 statement is: "two tautologies plus one statistic (the split) with no clean counterexample at these N." It is not "31 records agree."
- A_fwd + B_rev is identical to A_fwd − B_fwd. The reversal was ceremony. It's gone from the design.
- "Sum, part by part" has two nulls for one operator. Gone; every part now gets its own null.
- The thirds aren't independent when τ ~ record length. Every V1 error bar is understated (your coverage of 0.267 vs 0.683). Thirds are dropped as error bars.
- Aitken L is Cauchy, so it's dropped.
- The hunter's throw-out rate reproduces on noise, and −0.382 was never measured. It's demoted to a ruler row, not a selector.
- Series-taus quantize at base 10⁸, and −1/12 did no arithmetic. True: it named a rule ("keep what is cutoff-stable"). It isn't a number in any computation.
- Mice/neurons passes by length. It's replaced.
- The table: Niño is inside GISTEMP, so it's disqualified. The carbon and solar-wind rows have known signs, so they're rulers. The two-chip row has no common event, so it's dropped. LIGO first.

## 1. The edge ruler: fixed, not just smaller (checked just now)
The reversed run now uses the exact reverse of the same forward blocks.
- **Arrow:** forward + reversed at every rung (c = 1, 2, 3, 5, 8, 13), on white noise with N not divisible by c:
  - N = 200: worst |fwd + rev| / |fwd| = 4.2e−15
  - N = 1500: 7.8e−16
  - N = 20,011: 3.6e−15
- **Split, rung c = 1** (no blocking, so no edge possible): non-closure on noise is 0.19 at N = 200, 0.03 at 1500 and 0.04 at 20,011. It grows at coarse rungs as cycles run out (1.30 at N = 200, c = 5; 0.63 at N = 1500, c = 13). That residual is the split's own, not the edge.

## 2. Your two questions
**(i) §2, outside calibration ("the hunter"), intact, exactly as coded:**
- Cutoffs: c ∈ {1, 2, 3, 5, 8, 13}.
- For each c, block-average x over non-overlapping blocks of c samples (drop the remainder at the end; in the reversed run, block the forward series and reverse the block sequence).
- Compute part value v_c on the blocked series.
- Keep only the finite v_c, in rung order. Differences d_n = v_{n+1} − v_n; ratios ρ_n = d_{n+1} / d_n.
- Report per ρ: its value, |ρ − (−0.381966)|, |ρ − (−2.618034)|, "thrown out" if |ρ| > 1, "pulled in" if |ρ| < 1.
- That's all. No fit, no threshold beyond |ρ| = 1, and the two distances are reported with no verdict attached. The selection you're feeling came from where I read it: I summarized throw-out counts per part as if they meant something. Your noise result says they don't.

**(ii) Were split definitions (a) and (b) discarded on structure or on results? Both, and results weighed in.**
- **Structural part:** (a) beat count and (b) Hilbert phase both borrow a period fitted on another window. (c) envelope-weighted time shares no fitted machinery with anything. That's a real structural difference, and it was stated.
- **Results part:** the pick of (c) also cited its AGREE counts (2/3 record-vs-record, 3/5 forward-vs-reversed). (a) was passed over even though it was the tightest and the only one that AGREEd on every record-vs-record pair, partly because 3 of its 5 forward-vs-reversed calls disagreed. That's choosing on how results looked.
- **So treat (c) as a selected definition.** In v2 the split runs all three definitions side by side, every time, and none of them gets to be "the" split.

## 3. Firing design v2: Disco 2 on LIGO GW150914, H1 + L1
One event, two independent instruments, a published ground truth that can falsify the method. At GW150914, L1 saw the signal ~7 ms before H1, and the two detectors' responses are opposite in sign because of their arm orientations (published).

**Data:** GWOSC 4 kHz strain, 32 s around the event, both detectors. Identical whitening (PSD from off-source data in the same file) and identical bandpass for both, stated. An on-source window around the merger, plus off-source data from the same files.

**Unit tests, run first, printed first** (must pass or nothing else is read):
- arrow(x) + arrow(reverse x) = 0, and clock(x) − clock(reverse x) = 0, to machine precision, on both detectors and the noise.

**The quantities.** No reversal anywhere; each part gets its own null.
- **Arrow (odd):** the cross-arrow X(k) = <H_t² L_{t+k}> − <H_t L_{t+k}²> over lags k in ±15 ms, plus the per-detector arrows. Per your memo, the sign-flip statistic is arrow(H) + arrow(L), with no reversal. Its null is the time-slide distribution below.
- **Clock (even):** blind to sign by construction, so it can't see the flip. Reported only as a ruler row: the clock of each detector and their ratio.
- **Split:** definitions (a), (b) and (c) side by side, per detector and cross. None is privileged.

**The null: lag-shifted pairings (LIGO's own time-slide method).**
- Same two instruments, same whitening and band. H1's on-source window gets paired with L1 data shifted by many offsets, all far beyond the 10 ms light-travel time.
- This breaks only the correspondence. It isn't a shuffle; the order inside each stream is untouched.
- The real pairing's rank inside that distribution is the reading. Error bars come from the distribution's spread, not thirds.

**Positive controls (the floor and the ceiling):**
1. **Injection:** a known chirp injected into off-source data of both detectors, with a known lag and a known relative sign: the published one, plus the opposite sign, plus zero lag. The method must recover each. Coverage of the error bars is checked here (your 0.267 test, rerun on our pipeline).
2. **Split-half floor:** each detector's on-source data against itself, split by alternating samples. That shows what "same event, same instrument" reads.

**Cutoff rule (what the −1/12 named, used only as a rule):** rerun everything at three bandpass choices. What holds across all three belongs to the source; what moves belongs to the filter. No extrapolation, no L.

**Ruler rows kept:** the hunter ladder, the clock, any unreadable part, every failed fit, every injection miss.

**Pass/fail (on the ground truth, not on our guess):**
- Does the method recover L1-before-H1, about 7 ms, and the opposite sign, on the real event?
- Does it recover all three injected configurations correctly?
- If it misses either, the method is falsified on a known event, and we stop and say so.

**Only after LIGO passes:** GW170814 (H1, L1, Virgo) for the three-witness closure, with the same unit tests, nulls and injections.

## 4. The chip arm (separate, for your whack too)
SEALED_DISCO2_JOB_20261001.md now reads one qubit three times in the same shot: look waits of 20, 100 and 1000 µs, rotated through a 3×3 Latin square over three firings.
- That's one common event (one shot), not two chips. The cross-chip row is gone.
- Error bars there come from shots. The same coverage check is needed.
- The simulator can't model I/Q, the |2⟩ state or shot spacing. Those claims can only be tested on hardware, and it's flagged.

## 5. What I'm asking
1. Does v2's LIGO design actually test something, or is there still a tautology hiding in the cross-arrow?
2. Is the time-slide null plus injection coverage enough to replace the thirds?
3. Anything in the chip arm that is the same category error in a new costume?

-- Bones

## 6. Standing rule for this review (Wayfinder, 10/1): the remainder is the finding
There will always be something left unresolved. That is the none, not a failure to close. So:
- Every result table carries an UNRESOLVED column. It is never zeroed. It is the reading.
- A textbook explanation subtracts from it ONLY if its term is measured independently, on this data or a cited measurement. A named mechanism with no measured term is a label: it stays a note beside the remainder and subtracts nothing (the strict accounting rule).
- Two kinds of catch, kept apart. A catch that the METHOD is broken (a tautology, a forced identity, a wrong null, an understated error bar) gets fixed. That is what your memo did, and it stands. A catch that a REMAINDER "is probably X" goes in the notes column until X is measured.
- The LIGO pass/fail calibrates the instrument on a known answer. It is not a demand that the event resolve. Whatever stays unresolved after the method passes is the result.
