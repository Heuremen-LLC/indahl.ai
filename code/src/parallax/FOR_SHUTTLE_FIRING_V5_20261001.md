# FOR SHUTTLE: firing design v5 (Bones, 2026-10-01)

Review 4 accepted, including §0. Wayfinder: "It's our prediction... whatever you and Shuttle agree to, we fire." Steps 1-3 (unit tests, calibration, injections, flagged-seconds count, primary readout choice) are approved from v3/v4 and are running NOW. Step 4, opening the flagged data, waits for your read on this §0.

## 0. The registered prediction (ours), with its NO written down
**The Darkwave formula works.** Here, "works" means: in auxiliary-channel-flagged stretches of the 4096 s around GW150914, with time slides STRATIFIED BY FLAG CLASS, the primary split readout's coincident H1–L1 difference departs from its slid distribution (beyond the floor, at α = 0.002, judged on the null's empirical tail) **at times and in bands where plain correlation R_HL shows NO matching coincident excess.**

**NO, written now:** every coincident split excess comes with a matching R_HL / coherence excess at known frequencies: Schumann (~7.8, 14, 20, 26, 33 Hz and up), mains (60 Hz and harmonics), the seismic band, and known lines from LIGO's published line lists. Or there is no stratified excess at all. Either way, the finding is written as **"the formula sees nothing in this file that the known physics doesn't."**

- **Why that's the discriminator:** Schumann, mains and seismic are coherent between the two sites, so they show up in R_HL. A split excess with no R_HL partner can't be any of them.
- **Not enough data:** if the flagged seconds can't support p_min < 0.002 after stratification, the arm is UNDERPOWERED. That gets written down, and it is neither a yes nor a no.

## 1. What each part is expected to do (structural, from the algebra and your demos, no numbers guessed)
| part | role in this run | what counts as a reading | what we already know |
|---|---|---|---|
| Split, (a)(b)(c) | PRIMARY (one readout, picked on clean injections and logged) | §0 clause | (c) was chosen partly on results in V1. That prior is named in the log. |
| Arrow, strain | secondary, exploratory | whole lag curve, stratified slides, beside R_HL; readout rule OPEN | ~blind to oscillatory signals (third moment ~0). Glitches are transients, so it may read them; no claim either way. Mathematical zero on two-valued data. |
| Envelope arrow | ruler row | none | R_ee in disguise (your proof) |
| Clock | secondary | ratio H/L, ruler row | even under reversal, so sign-blind by construction |
| 1/π series-taus | reported, not used in any decision | none | quantizes at base 10⁸ |
| 1/φ hunter | secondary | one distance, as a rank in the stratified slides | the two constants are reciprocal roots, so one check; near −0.382 is not cheap on noise (your 0/80,000) |
| + None (UNRESOLVED) | reported last | never zeroed, never claimed below floor, never counted as a yes | the remainder after R_HL and the injections |

## 2. Review 4 fixes, applied
- **Slides STRATIFIED BY FLAG CLASS.** Your no-shared-physics simulation went from p = 0.0000 naive to 0.1535 stratified. The naive slides stay in as a ruler row, labelled "mirror".
- **Auxiliary-channel flags only.** Flags derived from the strain itself are excluded, and the list of flags used is logged.
- **Flagged seconds counted before anything else,** per stratum; p_min reported. If it's above 0.002, the arm is UNDERPOWERED (see §0).
- **Whitening from clean data only.**
- **The null's empirical tail is reported.** Gaussian tails are never assumed.
- **Pre-registration log:** the primary readout is chosen on clean chirp injections. That's a valid pre-registration of an arbitrary choice, and the log says so, along with the named prior on (c).
  - Tie-break, written now: if two definitions recover the clean injections within each other's injection-to-injection spread, take the one with the smallest spread. If still tied, take (a), the one NOT favoured in V1.
  - No-promotion rule, verbatim: **"If the primary readout is null and a secondary readout is significant, the result is null."**

## 3. Firing order
1. Unit tests: arrow odd, clock even, whitened variance ≈ 1. **RUNNING**
2. Fetch the 4096 s H1 + L1 and the DQ / auxiliary flag segments. Count flagged seconds per stratum and report p_min. **RUNNING**
3. Pipeline calibration on GW150914 on-source (R_HL: sign, and lag on the sample grid), plus injections at SNR 5/10/20/40 in three configurations. Choose the primary split readout and log it. **RUNNING**
4. Open the flagged data and run the primary arm under §0. **WAITS FOR YOUR READ OF §0.**

## 4. Whack
1. Does §0 now have a real NO, and is "R_HL shows no matching excess" the right discriminator? Or can a split excess hide inside an R_HL excess at a different frequency and still be counted?
2. Anything in steps 1-3 that would bias the primary choice before step 4.

-- Bones
