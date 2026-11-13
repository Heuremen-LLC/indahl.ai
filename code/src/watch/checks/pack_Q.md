## A. THE VENDOR'S NUMBER — is IBM's figure the same quantity we read? (the bill dies here first)
1. **Name what the stated figure IS before comparing.** gate_error = randomized-benchmarking AVERAGE infidelity, not per-gate
   P(1); T1 = IBM's own single-exponential fit over IBM's window; readout_error = assignment; prob_meas0_prep1 already contains
   decay DURING one readout; zz has a convention. *(22 Oct: 7 gate-train rows compared n gates with n × stated error.)*
2. **Coherent error stacks LINEARLY.** An over-rotation δ has infidelity (2/3)sin²(δ/2) but n back-to-back gates give
   P = sin²(nδ/2). Before any train-vs-stated line, compute the P the stated r ALLOWS if all of it is coherent; a deviation must
   exceed that. *(22 Oct: rows 1–3, 17–20 removed.)*
3. **Match the record the job RAN UNDER**, not the noon median or the nearest day. IBM recalibrates several times a day; if only
   a proxy record exists, the line says so and clears the whole range of neighbouring records. *(22 Oct older rows.)*
4. **A model built from IBM's numbers is not IBM's number.** qiskit-aer `NoiseModel.from_backend` makes SYMMETRIC readout error
   and no coherent/crosstalk terms; Fake* backends are stale snapshots; one 8192-shot draw is not a model value — compute exact.
   *(22 Oct three-box: "IBM's own noise model" withdrawn.)*
5. **Write IBM's one-sentence rebuttal for every line before it goes on the bill — then TEST THE REBUTTAL, not just the line.**
   A rebuttal that only SOUNDS right is a hypothesis, not a verdict. Before cutting, ask what data would answer it and whether
   that data is on disk or free to pull (IBM properties history per qubit, saved records, raw jobs: zero QPU seconds). Only a
   rebuttal that SURVIVES its own test kills the line; one that can't be tested makes the line CANNOT_TELL, never deleted.
   Lines that hold for IBM (favourable to them) don't go on a bill; lines the paper's own caveat contradicts don't either.
   *(22 Oct: spaced-gate row contradicted the paper. 22 Oct night: row 5 cut on "the record restamps on any recalibration";
   Wayfinder said pull the per-qubit records; 2,417 of 2,417 T1/T2 entries unchanged under 8 new stamps; row restored.
   A rule that only ever tests one side is a baseline built in the vendor's favour — Faults family I.)*
6. **Coincidence is not a copied record.** Equal medians of two figures prove nothing — check per qubit before calling a value
   stale or copied. *(22 Oct: measure/measure_2 kingston medians, 155 of 156 qubits differ.)*
7. **Within the stated figure is not a deviation**, however big it looks in our units. *(22 Oct: measured-qubit loss 0.0057
   vs stated asymmetry 0.0066.)*

## B. THE NONE — built before, like for like
8. **Equal idle of the STATED length, same qubits, same job** — and ask whether the compiled schedule really equals it.
   Save or recompute the transpiled durations; "equal elapsed time" rests on them. *(11 Oct fez; 22 Oct two-length.)*
9. **Two instruments differ in more than the variable you named.** measure vs measure_2: different thresholds and errors,
   not just length. List every known difference in the plan. *(22 Oct.)*
10. **Heralded vs unheralded, selected vs all shots — same in both arms.** *(22 Oct flip run 1 known-good failed on it.)*
11. **The comparison idle must hold the same state** (measured qubits in |1⟩ against an idle in |1⟩). *(21 Oct static ZZ read
    as a kick.)*
12. **Selection biases:** dropping qubits at the floor biases T1 up; idle concurrence > 0 biases loss up; clipped concurrence
    max(0,·) censors; dead-qubit guard counts reported. *(21–22 Oct.)*
13. **Sequential is drift, simultaneous is the thing.** Compare arms inside one job; across jobs/days is a drift reading.

## C. THE INSTRUMENT FIRST — known-good, floor, ceiling
14. **KNOWN-GOOD seat on real hardware** where the answer is already known, run through the committed code before the new data.
    plan_gate.py refuses a folder without it. *(22 Oct flat-beat: fez is not a known-good for phoenix — unequal apparatus.)*
15. **Synthetic test plants EVERY alternative:** null, each hypothesis, BOTH, NEITHER, and the apparatus artefact. A test that
    only plants the two you expect cannot say both or neither. *(22 Oct three-box sign/corner.)*
16. **Measure the FLOOR, not just the ceiling:** how many ABOVE/BELOW does a null world produce over N readings? Multiplicity
    is ~5% per reading; ~100 bins means ~5 false resolutions. *(21 Oct deciding runs.)*
17. **Sign convention checked twice:** gate algebra AND recomputing a committed value through the same code. Magnitudes and signed
    values never in one sentence without saying which. *(21–22 Oct, three times.)*
18. **The known-good rule is the rule.** If it fails by a hair, the chip is "not decided" — never relax it after the result.
    *(22 Oct kingston copy gap [+0.003, +0.091].)*

## D. FOUR OUTCOMES, COPIES, COMBINING
19. **ABOVE / BELOW / CONSISTENT / CANNOT_TELL.** Never fold CANNOT_TELL into a disproof; CONSISTENT is a bound — print the bound,
    never "the same". *(21 Oct, many.)*
20. **Copies compared by their GAP with a width, not by their labels.** *(21 Oct check G/H.)*
21. **Combine chips by values and widths; quote a combined value only if chi2/dof < 2.** Counting chip LABELS is the binary.
    A one-chip reading is not a finding when the plan says two. *(21–22 Oct.)*
22. **Pooled shots, repeated qubits, duplicate jobs are not independent units.** Processors are the units. *(22 Oct 7 Oct arms.)*
23. **Median of differences, not difference of medians.** *(21 Oct concurrence.)*
24. **Censored cells near the floor** (coherence < 5× shot noise) are not readings; ratios near a floor drift to 1.

## E. THE QUESTION ITSELF
25. **Every mechanism question has more than two answers.** Per-readout could be frame update, ring-down after the pulse, or
    pulse edges; "proportional" could be length or amplitude. Name what a result rules OUT, never what it "is". *(22 Oct.)*
26. **Post-hoc is labelled post-hoc** — every reading not in the plan says "defined after the data", including ratios whose
    direction we didn't like. *(22 Oct pre-registered ratio above 1 hidden.)*
27. **THE SPLIT for anything with a strength or length:** fit S (common offset) + P (scales) before reading a ratio; an
    offset divided by a strength manufactures a trend. *(22 Oct three-box eps sweep.)*
28. **No mechanism named in print, no framework words in papers or bills.** Close the ordinary doors with numbers; leave the
    cliffhanger factual.

## F. THE RECORD — count from the witness
29. **History from the record, not the session.** Every run since 24 Sep, every key, every instance (`ibm_jobs_all_keys`
    re-pull), Rigetti task ledger, the 4 Oct paper, parallax/out. *(22 Oct "first run" error.)*
30. **Times, counts and dates from job records,** never memory ("about an hour" was 3 minutes). *(22 Oct.)*
31. **Plans pushed BEFORE jobs; addenda BEFORE results are read;** a fire command checked for its arguments (--chip) before
    sending. *(21–22 Oct.)*
32. **Never fire while a referee on the same question is out.** *(22 Oct three-box.)*
33. **Check the budget per instance before planning:** open-instance refills on a rolling window; paid instances have hard
    caps (`usage_remaining_seconds`).

## G. THE OUTSIDE SEAT
34. **Referees get the RAW files, never our own source map** — the writer's SOURCES.md is the same seat. *(22 Oct.)*
35. **A referee flag is acted on, not relabelled** ("pending" is not a fix). *(22 Oct 160-gate rows.)*
36. **Literature from papers read, never search summaries;** no "known effect" without the paper's own number.
37. **Paper, site and bill agree number for number** — one batch edit, one push, after the referee.

