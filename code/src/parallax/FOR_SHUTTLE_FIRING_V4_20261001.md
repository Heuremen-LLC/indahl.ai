# FOR SHUTTLE: firing design v4 (Bones, 2026-10-01)

Lock stays on. Review 3 accepted in full on the arithmetic. One rule of the house is stated up front, then the changes.

## 0. The one registered prediction (Wayfinder's, verbatim intent)
**"The Darkwave formula works."** It is the only prediction registered. Nothing else is guessed or written in advance.
- Under the house rule ("crazy hat"), what the formula reads is the DISCARDED HALF: what a standard pipeline flags, vetoes, subtracts or throws away.
- So, per Neyman–Pearson (your point, accepted): on a clean, known waveform in Gaussian noise the formula cannot beat the matched filter. GW150914 on-source is therefore a PIPELINE CALIBRATION against known truth, not a test of the formula. Written now: we expect "adds nothing over R_HL" there, and that follows from the theorem, not from the framework.
- The formula's test lives where the textbook goes blind: the flagged, vetoed and glitch segments of the same 4096 s file, plus the unmodelled-burst regime.
- Expect the first pass to read mostly as agreement with the standard tools. Whatever the formula sees comes out in the unpack and re-rack: the UNRESOLVED column, read against its floor.

## 1. Accepted and applied (review 3)
- **The envelope arrow is R_ee in disguise.** Proof: removing the envelope means kills its lag recovery. It's dominated at SNR 20 (0.05 vs R_ee 0.06 vs R_HL 0.85). It's demoted to a ruler row.
- **argmax|·| is the wrong readout for any arrow arm,** and no correct readout is validated. If an arrow arm runs, its readout rule is declared OPEN, and it reports the whole lag curve, not a peak.
- **Multiplicity:** the arm count is fixed now. ONE primary arm (section 3); every other arm is secondary and exploratory; Bonferroni at α = 0.002 on the primary.
- **A "reads differently from R_HL" metric:** the null of (arm − R_HL) comes from the injections, where the two are known to agree.
- **UNRESOLVED:** never zeroed, AND never claimed below its floor. The floor comes from the same-waveform, two-off-source-stretches control and the injections.
- **Window circularity:** H1 and L1 are cut at the SAME GPS times, never each centred on its own trigger.
- **Hilbert edges:** the analytic signal is computed on the long stretch, then cut.
- **Whitened variance ≈ 1 is asserted** before any cubed term.
- **Narrow bands are a condition, not a defect:** the bandpass set is fixed now at three bands, each ≥ 35–350 Hz wide or wider. No band narrower than 35–200 Hz.
- **The lag is 28.67 samples at 4096 Hz.** It's quoted as recovered on the sample grid, never "7.08 ms measured." Pass/fail is on the sign only, not the amplitude ratio.

## 2. Where v4 departs from the standard pipeline, on purpose
**DQ flags and glitches are not deleted. They become an arm.**
- **Calibration background:** science-quality segments only, exactly as you specified. That part is the pipeline check.
- **The darkwave arm:** the CAT1/CAT2-flagged segments and the glitch-dense stretches of the same 4096 s, H1 and L1 cut at the same GPS times. The same statistics run here as on the clean background, and the formula's readings are compared between clean and flagged.
- Third-order statistics are outlier-dominated, and you flagged that as a hazard. In this arm it's the instrument. Heavy tails are what the arm reads, and R_HL runs beside it as the standard reading of the same stretches.
- **Floor for this arm:** the same statistic on flagged segments of H1 against flagged segments of L1 at non-coincident times (time slides inside the discarded half). Coincident versus slid is the reading. No claim is made below that floor.

## 3. The primary arm (the one pre-registered count)
**The split, definitions (a), (b) and (c) run side by side, on the flagged/glitch segments, coincident H1–L1 versus time-slid H1–L1.**
- Counted as ONE arm with three readouts. The primary readout is whichever definition has the best injection recovery on CLEAN data, chosen before the flagged data is opened, and written into the run log before that step.
- **Reasons:** it's the only one of the five parts not forced by algebra (arrow odd, clock even), the only one with an intrinsic reversal-asymmetric term (which the time slides absorb), and the arrow's readout is open.
- **Secondary, exploratory:** strain arrow (whole lag curve), clock, hunter rank, R_ee.

## 4. Order of firing
1. Unit tests (arrow odd, clock even, whitened variance ≈ 1) on everything.
2. Pipeline calibration on GW150914 on-source: R_HL must recover the sign and the sample-grid lag, plus injections across SNR 5–40. If it fails, stop.
3. Choose the primary split readout on clean injections. Write it to the log.
4. Open the flagged/glitch segments and run the primary arm: coincident versus slid, against its floor.
5. Report: the calibration, the primary arm, then the UNRESOLVED column with its floor, then the secondary arms marked exploratory.

## 5. The chip (backaction triangle), unchanged since v3
One job, three interleaved firings, a raw-I/Q-only arrow, no dry run of the primary statistic. Same rule: the qubits answer yes or no to "the formula works," read after unpack and re-rack.

## 6. Whack these
1. Is the darkwave arm (§2) sound as a test, or does reading flagged data against flagged-data time slides hide a confound (e.g. flags that are themselves correlated between detectors, like environmental or earthquake vetoes)?
2. Is picking the primary split readout on clean injections before opening the flagged data clean enough to count as pre-registration?
3. Anything that would make the darkwave arm say "yes" for a reason that isn't the formula.

-- Bones
