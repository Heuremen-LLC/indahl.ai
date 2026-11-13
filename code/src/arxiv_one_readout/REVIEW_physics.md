# Referee report (hostile but fair): "One Readout, Three Clocks" (main.tex)

Line numbers refer to /Users/heuremen/bones-forge/arxiv_one_readout/main.tex. "T/" is the 2026-10-04-three-positions directory. Items marked (checked) were verified by me against T/data/clocks/*.json; the rest are read from the text and scripts.

Overall verdict: not acceptable as it stands. The headline 4.0 sigma comes from a post-hoc one-sided truncation of a noisy estimator. The injection test does not test the main competing explanation. The "three positions" are not all traceable. Items 1-5 are the ones that matter.

## FATAL

1. FATAL. The headline 1.0331 +/- 0.0083 (abstract l.22, Sec. Results l.69, Limitations l.155) is produced by a one-sided truncation, which biases a median upward. (checked)
   - The 30 "negative elapsed time" readings are not a separate physical population. They are the left tail of a noisy per-spectator estimator. Per-chip q10 of the ratio is -0.29 (phoenix), -0.26 (pittsburgh), -0.17 (marrakesh). Deleting only the lower tail raises the median by construction.
   - Check on the released rows: if instead I remove the same number of readings from the TOP of each chip's distribution (a symmetric trim), the median ratios are aachen 1.016, boston 1.022, fez 1.000, kingston 1.042, marrakesh 0.990, phoenix 0.963, pittsburgh 0.912. Three of seven are below 1, so the "effect" is entirely a function of which tail is cut.
   - The argument "a duration cannot be negative" (l.53) is wrong for a noisy estimator whose output is an inferred quantity, not a duration. Negative values are expected noise.
   - The pre-specified number is 1.0207 +/- 0.0092 (2.2 sigma, "not separable from 1" in T/results.json). The paper leads with the post-hoc number.
   - Fix: lead with the pre-specified cut-only value. Replace the median by an estimator that is unbiased under symmetric noise, or fit the full distribution with a censored or mixture model. Report the symmetric-trim result. State that the effect is not established at the 2.2 sigma level. Remove "4.0 standard errors" from the abstract.

2. FATAL. The "slope is insensitive to additive overhead" claim (abstract l.22, Methods l.59, Results l.118) tests the wrong overhead.
   - The injection test plants an additive constant S (per job). The physics a referee will raise is a per-measurement overhead: acquisition-window padding, resonator ringdown, alignment or buffer latency, the gap between back-to-back measures. That cost scales with k and lands in the slope P, not the intercept S. The test is blind to it.
   - The effect size is 3% of 2.18 us = about 70 ns per readout. That is within control-electronics alignment and buffer granularity. The Rigetti result (fixed offset 0.04-0.10 us per tone, l.142-144) has the same size and the same interpretation.
   - Fix: plant a per-measure overhead d (P = 1 + d/L) and show it is recovered as P not S. Then state plainly that the method measures "wall-clock time per measure instruction as seen by an idle neighbour", which includes hardware padding. Identify exactly what the "specification" counts (see item 8). Without this the paper has no claim beyond "a spectator sees the measure instruction last about 3% longer than the target says".

3. FATAL. The abstract rests on numbers the manuscript says it cannot trace.
   - The abstract (l.22) opens with 2.32 us (spectator) and 3.79 us (measured qubit) and the ordering "seven of seven". Results l.94 and l.167 say the derivation of both numbers is not in the released files, and the measured-qubit clock is missing for aachen and not re-derived for any chip (Methods l.50: "taken from the project record").
   - The Table 2 "others" row is empty, and the pittsburgh row in Table 2 (2.27 / 3.06 / 1.40 / 1.35) conflicts with the project trail for 4 Oct (1.04 / 1.34 / 1.29, i.e. qubit/maker 1.34, not 1.40; trail/index.html).
   - Fix: delete 2.32 / 3.79 from the abstract and title-level claims, or derive them from raw data. Either re-derive the measured-qubit position for all seven chips with one estimator, or rescope the title and abstract to the spectator-versus-specification result. Remove "[TODO]" macros (l.94) before submission.

## MAJOR

4. MAJOR. Dependence is not treated, so the quoted uncertainty is too small.
   - The 284 (or 254) spectators are not independent. They share chip, calibration epoch, job, shots, the same measured qubits, and the same k ladder. They are nested in 21 runs (3 reads per chip). The bootstrap (l.56) resamples spectators i.i.d. within a chip.
   - The paper's own evidence that widths are understated: the earlier two-point estimator had read-to-read scatter 2.4 times the printed width (l.158). Pittsburgh's spectator/maker ratio moved 1.087 to 1.04 between 2 and 4 Oct (trail), more than twice the quoted per-chip width (0.0187).
   - Inflating the pooled width by 2-2.4 gives +/- 0.017-0.020, i.e. 1.7-2.0 sigma even for the post-hoc value, and about 1 sigma for the pre-specified value.
   - chi2/dof of 0.52 (l.69, flagged as under-dispersed) is itself a symptom of correlated or mis-sized errors.
   - The across-chip combination assumes seven independent measurements. The chip-independence test "cannot resolve overlap below 0.8" (l.167), which the paper admits is absence of a verdict.
   - Fix: cluster bootstrap by run (job), then by chip. Report a random-effects pooled value. Use the run-to-run scatter as the width.

5. MAJOR. Post-hoc analysis choices are not corrected for, and the claim "pre-registered" is overstated.
   - Choices made after seeing data: the 4 deg/us detuning cut (introduced after aachen looked like an outlier, l.158), the 0.15 phase floor, the 3-width separation, the root window (-5, 60), nearest-root selection, fitting only delays 10/20/30 us, the negative-time cut, the median as estimator, and a switch from the two-point to the 1-9 fit.
   - The Methods say scripts are hashed, but T/verify.py (with a .bak-predark file) was changed on 11 Oct, after data of 2-7 Oct.
   - Only numerical "calls" were hashed, and 12 of 21 missed. No effect-size, cut, or estimator was pre-registered.
   - Many other tests were run (12/11, 13/12, n/(12 pi) rungs, Spearman +0.893 at n=7, p=0.0123, 1/r^2 ordering, stretched-exponential exponents). No look-elsewhere correction is stated.
   - Fix: say "exploratory" throughout. Give the full list of analyses run. Show R as a function of every choice (cut 2/3/4/5/6/8 deg/us, delay window, linear versus quadratic, root window) as a robustness figure. Remove or shrink p-values from non-prespecified tests.

6. MAJOR. The spectator "clock" assumes the spectator's precession rate during readout equals its idle rate. The paper concedes this in one sentence (l.170) and then treats ratio > 1 as a duration.
   - Measurement-induced AC-Stark shift of the spectator from photons leaking through the shared bus and neighbouring resonators, a second-order dispersive shift, and ZZ with a measured qubit all change the rate. The measured qubits are collapsed by the readout and the control arms have no measurement, so ZZ (tens of kHz, i.e. up to roughly 10-30 deg/us) is comparable to the spectators' own residual detuning of 3-30 deg/us.
   - A 3% rate change is therefore the expected scale. The slope method does not cancel it: a rate change is multiplicative in the same way a duration is, and the two are degenerate.
   - Fix: separate duration from rate. (a) Compare against a control arm with the same measured-qubit states prepared but no measurement. (b) Vary readout amplitude or length if hardware allows (this changes photon number and AC-Stark but not duration). (c) Repeat with spectators in |0> versus |1>, or with echoed (dynamically decoupled) spectators, which cancels static shifts. (d) Cite Schuster et al. 2005 and Gambetta 2006 on the shift and quantify the expected size from chip parameters.

7. MAJOR. The quadratic "equivalent elapsed time" is calibrated on 10-30 us delays and used at 2-20 us (k = 1..9). The phase is wrapped (900 degrees at 30 deg/us over 30 us).
   - The extrapolation below the fit range, the unwrapping procedure, and the rule "real root nearest a_k/c1 in (-5, 60)" are not justified. Control delays of 0 and 60-240 us exist but are not used.
   - The author's own data show the estimator is rate-dependent (Spearman -0.17 to -0.56, l.53). Thus the conversion is biased at low rate, and it is not shown that the bias vanishes above 4 deg/us rather than just shrinking. The cut statement "removes it" is not demonstrated. Different parts of the paper quote different ranges (-0.17 to -0.56 here, -0.20 to -0.34 in T/results.json, a -0.60 to -0.10 test band in verify.py).
   - The phase-wrap exclusion for the negatives rests on one Spearman of -0.067 (n=30), a weak test.
   - Fix: show R versus detuning in bins above the cut. Include the 0 us delay and the full delay set. Give the unwrapping rule and test on synthetic data with realistic dephasing, with a planted k-dependent rate shift as well as a planted duration.

8. MAJOR. "Specification" is not defined with enough precision to be falsifiable.
   - Methods l.48: "the stated readout duration read from the backend target (median over qubits)". The code reads `measure_duration_s` (split_seven_chips.py l.59). The target instruction duration is not the same as the property "readout_length" (probe-pulse length), and neither includes ringdown, the acquisition margin, or control-system latency.
   - Four chips have an identical 2.18 us, which looks like a default rather than a per-chip calibration. A median over the whole chip is compared with the qubits actually used.
   - Fix: say which field is read, from which backend call, with date and calibration timestamp. Use the per-qubit value for the measured qubits. State which interval ("pulse", "acquisition", "instruction", "instruction + inter-measure gap") the spectator is expected to see, and say the ratio measures the last of these.

9. MAJOR. The abstract and conclusions overstate the ordering.
   - "Seven of seven processors" (l.22): spectator > specification is individually 0.1-2.4 sigma per chip with fez at 1.0046 +/- 0.016 consistent with 1 (l.69, l.114). The spectator < measured-qubit comparison exists for six chips (aachen missing) and mixes estimators (l.94).
   - "Ordering ... reported on seven of seven" cannot be supported chip by chip. It rests on a pooled constant that is itself 2.2 sigma pre-specified.
   - The spectator clock (phase accumulation) and the measured-qubit "idle-equivalent time for population loss" are different observables. Their numerical order is not an ordering of one "duration", and the second is expected to exceed the first from T1 and readout-induced transitions (l.170 concedes this). This weakens the novelty claimed in l.36.
   - Fix: restate the abstract as "pooled spectator/specification ratio 1.02 +/- 0.01-0.02 (about 2 sigma)" and describe the measured-qubit comparison as a separate, illustrative observation.

10. MAJOR. Internal inconsistency of the two reductions.
    - Table 1 gives R = 1.0331 (median of per-spectator ratios, 284 or 254 spectators). Table 3 gives P = 1.047 (per-spectator least-squares, 767 spectators, 21 runs), which is 5.6 widths from 1 on the paper's own widths.
    - The text says "we have not reconciled the two beyond noting that both exceed 1" (l.120). Four different spectator counts appear (524 total, 284, 254, 767) and two unreconciled no-cut results (chi2/dof 2.93 with p 0.0074 versus 2.22 with p 0.0384, l.158).
    - Table 3 reports S with chi2/dof 0.18 and then states the widths are over-estimated, but still uses +/- 0.038 as the limit on S.
    - A paper cannot publish two headline numbers from the same data, with different significances, that the authors have not reconciled. This is a required fix before submission.
    - Fix: pick one estimator, define it, and reproduce the other as a stated cross-check with a quantitative explanation of the difference.

11. MAJOR. The second-vendor data do not support, and partly undercut, the IBM claim.
    - The Rigetti slope depends on an analysis definition by 0.0552 (1.0114 versus 0.9561), which is larger than the IBM effect being claimed (0.033).
    - The same sensitivity to the rate definition has not been tested on IBM. The Rigetti negative fraction is 35% and the clocks turn at -24.8 deg/us against a designed 36 (T/.../THE_SECOND_VENDOR_20261011.txt), so the clock calibration there is itself not understood.
    - A previously published 1.035 was withdrawn on 11 Oct. Including it, even as a withdrawal, in the abstract invites the question of how many other numbers are under review.
    - Fix: either drop the Rigetti section to an appendix or supplement, or apply one fixed pre-stated estimator to both. Move the withdrawn-value discussion out of the abstract, keep a one-line erratum note in the text.

12. MAJOR. Reproducibility from the text alone is not possible.
    - Missing from Methods: shots per circuit and number of circuits, rep_delay (500 us, in common.py only), meas_type kerneled, which nine physical qubits and their coupling geometry (how are spectators "fenced"), spectator state preparation (sx? what about phase reference), the readout mitigation status, SDK and runtime versions, calibration timestamps of each job, how many measured qubits per job, transpilation (the code builds ISA circuits directly with realize_wait delay quantisation, not described), the actual circuit diagram, the measured-qubit preparation for the decay clock, and the definition of k = measures per qubit versus per job.
    - verify.py reproduces the table only from 524 extracted rows. The extractors (readlook_*.py) need the 22 GB of raw data "on request". The Zenodo DOI could not be checked online by the preparer (NUMBERS.md).
    - Fix: add a table of all runtime options and versions, a circuit figure, and the extraction code with the raw counts for at least one chip. Deposit the raw shot data on Zenodo or other public storage, not on request.

13. MAJOR. The "Related observations" subsection (l.146-149) states results not derived in the paper: dose cost 0.99-1.03 and 1.16-1.18, stretched-exponential exponents 0.823 and 1.381, and a 1/r^2 ordering.
    - These are exactly the claims a referee will attack. They have no methods, no fit definition, and no uncertainties in context. They are given "from the project's summary page; not re-analysed".
    - Fix: delete this subsection, or support each with the same standard as the main result.

## MINOR

14. MINOR. The Limitations paragraph on the 12/11 call (l.164) and the "12 of 21 missed" discussion in the abstract use project jargon ("landed", "on the edge of their width", "every ruler counted") and refer to a prediction (12/11, 13/12, n/(12 pi)) whose origin is nowhere explained in the paper. To a physicist this reads as numerology (a rational-number prediction of an instrument ratio). Fix: either explain the model that predicts 12/11, or delete the pre-registered-calls material from the abstract and Limitations.

15. MINOR. Tone and moderation risk.
    - Discussion l.174: "The authors read this as time being a relational quantity" is a metaphysical statement unrelated to the data and is the sentence most likely to trigger moderator reclassification (physics.gen-ph or general physics) or a rejection. Delete it. The previous sentence ("three correct answers to three different questions") is sufficient.
    - Terms like "dark spaghetti", "dark matter" (project docs), "witness", "look", "hand" (the paper uses "hand" in l.142), "Bones", and "ruler" appear. The paper itself should use only standard terms: spectator phase, measurement-induced dephasing, readout duration. Replace "witness" and "look" throughout with standard terms.
    - The "project page" / "project record" / "project summary" are cited as sources in the text (l.94, l.149, l.164). A journal-standard paper cites data, not a website.

16. MINOR. Author and disclosure issues.
    - \author{AUTHOR NAME} placeholder (l.16). \date{\today}. Plural "the authors" is used with one human author. No e-mail or ORCID.
    - Disclosure: "Made with inorganic intelligence assistance." (l.180) is cute and not a plain-language disclosure. arXiv's policy requires the human author(s) to take full responsibility and does not allow AI as an author (which the paper correctly follows). Suggested replacement in Acknowledgements: "Analysis code, data reduction and drafting were assisted by an AI system (Claude, Anthropic). The author reviewed the results and takes full responsibility for the content."
    - arXiv endorsement for quant-ph is needed for a first-time submitter with no institutional email. Allow time for this.

17. MINOR. Data-count slips and cross-checks.
    - The abstract says "305 jobs" while the spectator analysis uses 21 runs (l.120) and 524 readings. Say which jobs feed which table.
    - "Seven of the eight processors are from one vendor" (l.167) is correct but note that 7 IBM chips share a calibration pipeline, a target-defaulting convention, and a time window of 6 days (2-7 Oct), so they are not independent samples of "superconducting processors".
    - `ibm_phoenix` is described as a square lattice in the limitation but as heavy-hex in the title, abstract and Methods l.42. Fix the title ("seven IBM processors") and mark phoenix explicitly.
    - The Methods give the cut as |c1| <= 4 but verify.py uses the signed detuning > 4. Every detuning in the released rows is positive (checked), so there is no numerical effect, but the definitions should agree.
    - The 3 ledger entries with no submission time (l.167) should be explained or fixed.

18. MINOR. Table 1: the cut-only and non-negative widths are not comparable (pittsburgh +/-0.0495 versus +/-0.0187, a factor 2.6 narrower after deleting 8 of 43 readings). That should be a warning sign about the stability of the bootstrap of a median with a heavy tail. Report the bootstrap CI (percentile) and the number of effective spectators. The table caption should say that the non-negative column is the post-hoc one.

19. MINOR. Table 2 mixes the two-point estimator, the 1-9 fit, and two dates. A column of mixed estimators is not interpretable. Either present one estimator with uncertainty, or remove the table from the main text. Add uncertainties (all rows lack them) and the number of qubits.

20. MINOR. The statement l.36 "As far as we are aware, previous work does not report the following together" is a priority claim and should be softened further, or replaced with a list of what is new in a single sentence. The three-positions framing is, as the paper itself says, expected from known physics, so the novelty is the specific number only.

## Prior art (item 6 of the brief)

21. MAJOR (missing classics). The following are not cited and a referee will expect them.
    - Blais et al., PRA 69, 062320 (2004) and Blais, Grimsmo, Girvin, Wallraff, RMP 93, 025005 (2021): circuit QED and dispersive readout reviews.
    - Schuster et al., PRL 94, 123602 (2005): AC Stark shift and dephasing of a transmon-like qubit by cavity photons. This is the most directly relevant reference for the spectator-frequency-shift explanation in item 6.
    - Koch et al. 2007 (transmon) and Krantz et al. 2019 (engineer's guide).
    - Sheldon et al., PRA 93, 060302 (2016), and Magesan & Gambetta, PRA 101, 052308 (2020), for crosstalk and effective Hamiltonians in IBM fixed-frequency devices. Sarovar et al., Quantum 4, 321 (2020), on crosstalk detection.
    - Gambetta, Blais, Boissonneault et al. (2008), quantum-trajectory treatment of readout and the Zeno effect.
    - On measurement-induced transitions, besides Sank 2016: Khezri et al., PRApplied 2023 (RWA), Dumas et al. 2024 (transmon ionization), Lescanne et al. 2019. The paper cites only one.
    - On ring-down and cavity reset: Jeffrey et al. 2014 (Purcell filter), McClure 2016 (cited), Bultink 2016 (cited), Magnard et al. 2018 (fast reset), and Heinsoo 2018 (cited).
    - Mid-circuit measurement on IBM: Corcoles 2021, Rudinger 2022 and Govia 2023 are cited and characterised correctly in outline. Add Gaebler et al. only if trapped-ion comparison is wanted. A reference for IBM scheduling and timing: the OpenQASM 3 / Qiskit scheduling documentation (Cross et al. 2022) and the Qiskit Runtime docs on measure durations and alignment constraints.
    - Vallesa2026 is cited for "spectator effects during readout with tunable couplers". I could not verify this reference offline. Check the title, year, and that it says what is claimed. NUMBERS.md says all references were looked up on arXiv on 2026-10-21; make sure the bib has arXiv IDs.

22. MINOR. Characterisation of cited work is generally fair, but the sentence l.30 attributes "relax or excite the measured qubit and its neighbours" to Gambetta/Boissonneault/Sank. Those papers concern the measured qubit; the effect on neighbours is the subject of Heinsoo/Malekakhlagh/Vallesa. Fix the citation grouping.

## Internal consistency (item 8 of the brief)

23. MINOR. Abstract versus body:
    - Abstract: "(seven chips; 254 spectators ... after removing 30)". Body Table 1: pooled n = 284 for the cut-only column and 254 for non-neg. Make the abstract state both numbers and which comes first.
    - Abstract "values differ from chip to chip" versus chi2/dof 0.52-0.88 "one constant". These two statements pull in different directions; say which is meant.
    - Abstract says the Rigetti device "reads an honest clock plus a fixed offset of about 0.04 us", while the body gives 0.04-0.10 us depending on the rate definition.
    - Abstract: "12 of 21 missed" versus l.164 "(11 missed before one call was re-read ...; an independent summary also lists 11)". Give one number.
    - Pooled fit with p = 0.79 (l.69) is quoted as evidence of one constant, but the same file describes it as suspicious under-dispersion.

## Summary counts

FATAL 3, MAJOR 10 (items 4-13) plus item 21 (missing references) = 11, MINOR 10 (items 14-20, 22, 23, and the sub-items counted inside 15-17 not separately). Total 23 numbered items.

Top required actions, in order: (1) drop the one-sided negative cut as the headline and lead with the pre-specified 1.0207 at about 2 sigma, then do the cluster bootstrap; (2) repeat the injection test with a per-measurement overhead and a rate shift; (3) remove the untraceable 2.32 / 3.79 / "seven of seven" from the abstract; (4) pick one estimator and reconcile R = 1.033 with P = 1.047; (5) delete the "time as relational" sentence and add the missing circuit-QED references.
