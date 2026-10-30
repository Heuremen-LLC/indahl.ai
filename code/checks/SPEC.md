# The check block: specification

Heuremen LLC, 30 October 2026. Tools: readcheck.py, readcheck_hook.py, install_hook.sh, test_gate.sh (this folder).

An entry is a dated section in a CHECKS.md file beside the reading it covers:

```
## 2026-10-30 14:05 what the reading is
packs: L,P
- I: holds: <what was checked>
- II: fixed: <what was wrong and what changed>
- L6: cannot tell: <why it cannot be decided here>
- P1: n/a: <why the line does not apply>
```

Every core field and every field of each named pack must be answered. An answer starts with holds:, fixed:, caught:, n/a: or
cannot tell:, followed by at least a short sentence. Entries are appended, never edited after they are committed.

Each pack line below comes from a mistake we made while measuring, with its date. There is no field IV. That item on our working
list is a note, not a check.

## The core
Required in every entry, in every domain. "holds: <what you checked>" is a legal answer. A blank is not.

**I — THE NONE.** Was the comparison built BEFORE the reading, like for like (same averaging, count, search freedom, moment)? Is the
denominator built from the numerator: does the gate that decides which items count contain the thing being counted (an exclusion that
depends on the effect, a readability filter that one arm fails more often)? *Count what the gate drops, by arm.*

**II — THE GAP.** Did a net, a mean, a median or a "consistent" zero out a difference that was the reading? Count item by item
(flips in each direction) before you net, and compare against the REPEAT FLOOR of the same setup. A spread between runs is a reading,
not noise to average away. *(30 Oct: net rates "no difference" hid 11 cross-machine flips against floors of 1 and 4.)*

**III — THE SIGN.** Did a per-cell verdict fold the sign? When several cells each read "consistent", do their signs agree? Is the
effect a product or a sum? Magnitudes and signed values never in one sentence without saying which.

**V — THE RULER.** Name the ruler before the number, and run two side by side when they can disagree: value ± width, an exact test on
discordant pairs, the split (S = what every run shares, such as the repeat floor, and P = what moves with the change under test), and a bound
(CONSISTENT is a bound, so print it).

**VI — FOUR OUTCOMES, BOTH ALTERNATIVES.** ABOVE / BELOW / CONSISTENT / CANNOT_TELL, never folded. Test BOTH live alternatives (zero
AND the size that would matter): if the interval reaches both, it is CANNOT_TELL on the question that matters, whatever the label says.

**R — THE RECORD.** Every count, date, time and version read from the file, job record or log, with its seat named, never from memory.
Post-hoc readings say "defined after the data".

## Pack Q: quantum hardware (sections A to G are fields QA to QG)

### A. The vendor's number: is IBM's figure the same quantity we read?
1. **Name what the stated figure IS before comparing.** gate_error = randomized-benchmarking AVERAGE infidelity, not per-gate
   P(1). T1 = IBM's own single-exponential fit over IBM's window. readout_error = assignment, prob_meas0_prep1 already contains
   decay DURING one readout, and zz has a convention. *(22 Oct: 7 gate-train rows compared n gates with n × stated error.)*
2. **Coherent error stacks LINEARLY.** An over-rotation δ has infidelity (2/3)sin²(δ/2) but n back-to-back gates give
   P = sin²(nδ/2). Before any train-vs-stated line, compute the P the stated r ALLOWS if all of it is coherent. A deviation must
   exceed that. *(22 Oct: rows 1–3, 17–20 removed.)*
3. **Match the record the job RAN UNDER**, not the noon median or the nearest day. IBM recalibrates several times a day. If only
   a proxy record exists, the line says so and clears the whole range of neighbouring records. *(22 Oct older rows.)*
4. **A model built from IBM's numbers is not IBM's number.** qiskit-aer `NoiseModel.from_backend` makes SYMMETRIC readout error
   and no coherent/crosstalk terms. Fake* backends are stale snapshots, and one 8192-shot draw is not a model value — compute exact.
   *(22 Oct three-box: "IBM's own noise model" withdrawn.)*
5. **Write IBM's one-sentence rebuttal for every line before it goes on the bill — then TEST THE REBUTTAL, not just the line.**
   A rebuttal that only SOUNDS right is a hypothesis, not a verdict. Before cutting, ask what data would answer it and whether
   that data is on disk or free to pull (IBM properties history per qubit, saved records, raw jobs: zero QPU seconds). Only a
   rebuttal that SURVIVES its own test kills the line. One that can't be tested makes the line CANNOT_TELL, never deleted.
   Lines that hold for IBM (favourable to them) don't go on a bill. Lines the paper's own caveat contradicts don't either.
   *(22 Oct: spaced-gate row contradicted the paper. 22 Oct night: row 5 cut on "the record restamps on any recalibration",
   pulling the per-qubit records showed 2,417 of 2,417 T1/T2 entries unchanged under 8 new stamps, row restored.
   A rule that only ever tests one side is a baseline built in the vendor's favour — Faults family I.)*
6. **Coincidence is not a copied record.** Equal medians of two figures prove nothing — check per qubit before calling a value
   stale or copied. *(22 Oct: measure/measure_2 kingston medians, 155 of 156 qubits differ.)*
7. **Within the stated figure is not a deviation**, however big it looks in our units. *(22 Oct: measured-qubit loss 0.0057
   vs stated asymmetry 0.0066.)*

### B. The none: built before, like for like
8. **Equal idle of the STATED length, same qubits, same job** — and ask whether the compiled schedule really equals it.
   Save or recompute the transpiled durations. "equal elapsed time" rests on them. *(11 Oct fez, 22 Oct two-length.)*
9. **Two instruments differ in more than the variable you named.** measure vs measure_2: different thresholds and errors,
   not just length. List every known difference in the plan. *(22 Oct.)*
10. **Heralded vs unheralded, selected vs all shots — same in both arms.** *(22 Oct flip run 1 known-good failed on it.)*
11. **The comparison idle must hold the same state** (measured qubits in |1⟩ against an idle in |1⟩). *(21 Oct static ZZ read
    as a kick.)*
12. **Selection biases:** dropping qubits at the floor biases T1 up, idle concurrence > 0 biases loss up, clipped concurrence
    max(0,·) censors, and dead-qubit guard counts reported. *(21–22 Oct.)*
13. **Sequential is drift, simultaneous is the thing.** Compare arms inside one job. Across jobs/days is a drift reading.

### C. The instrument first: known-good, floor, ceiling
14. **KNOWN-GOOD seat on real hardware** where the answer is already known, run through the committed code before the new data.
    Our plan gate refuses a run folder without it. *(22 Oct flat-beat: fez is not a known-good for phoenix — unequal apparatus.)*
15. **Synthetic test plants EVERY alternative:** null, each hypothesis, BOTH, NEITHER, and the apparatus artefact. A test that
    only plants the two you expect cannot say both or neither. *(22 Oct three-box sign/corner.)*
16. **Measure the FLOOR, not just the ceiling:** how many ABOVE/BELOW does a null world produce over N readings? Multiplicity
    is ~5% per reading, so ~100 bins means ~5 false resolutions. *(21 Oct deciding runs.)*
17. **Sign convention checked twice:** gate algebra AND recomputing a committed value through the same code. Magnitudes and signed
    values never in one sentence without saying which. *(21–22 Oct, three times.)*
18. **The known-good rule is the rule.** If it fails by a hair, the chip is "not decided" — never relax it after the result.
    *(22 Oct kingston copy gap [+0.003, +0.091].)*

### D. Four outcomes, copies, combining
19. **ABOVE / BELOW / CONSISTENT / CANNOT_TELL.** Never fold CANNOT_TELL into a disproof. CONSISTENT is a bound — print the bound,
    never "the same". *(21 Oct, many.)*
20. **Copies compared by their GAP with a width, not by their labels.** *(21 Oct check G/H.)*
21. **Combine chips by values and widths. Quote a combined value only if chi2/dof < 2.** Counting chip LABELS is the binary.
    A one-chip reading is not a finding when the plan says two. *(21–22 Oct.)*
22. **Pooled shots, repeated qubits, duplicate jobs are not independent units.** Processors are the units. *(22 Oct 7 Oct arms.)*
23. **Median of differences, not difference of medians.** *(21 Oct concurrence.)*
24. **Censored cells near the floor** (coherence < 5× shot noise) are not readings. Ratios near a floor drift to 1.

### E. The question itself
25. **Every mechanism question has more than two answers.** Per-readout could be frame update, ring-down after the pulse, or
    pulse edges. "proportional" could be length or amplitude. Name what a result rules OUT, never what it "is". *(22 Oct.)*
26. **Post-hoc is labelled post-hoc** — every reading not in the plan says "defined after the data", including ratios whose
    direction we didn't like. *(22 Oct pre-registered ratio above 1 hidden.)*
27. **THE SPLIT for anything with a strength or length:** fit S (common offset) + P (scales) before reading a ratio. An
    offset divided by a strength manufactures a trend. *(22 Oct three-box eps sweep.)*
28. **No mechanism named in print.** Close the ordinary explanations with numbers and state the open question as a fact.

### F. The record
29. **History from the record, not the session.** Every run, every account and instance, every earlier paper.
    *(22 Oct "first run" error.)*
30. **Times, counts and dates from job records,** never memory ("about an hour" was 3 minutes). *(22 Oct.)*
31. **Plans pushed BEFORE jobs, addenda BEFORE results are read,** and a fire command checked for its arguments (--chip) before
    sending. *(21–22 Oct.)*
32. **Never fire while a referee on the same question is out.** *(22 Oct three-box.)*
33. **Check the budget per instance before planning:** open-instance refills on a rolling window. Paid instances have hard
    caps (`usage_remaining_seconds`).

### G. The outside seat
34. **Referees get the RAW files, never our own source map** — the writer's SOURCES.md is the same seat. *(22 Oct.)*
35. **A referee flag is acted on, not relabelled** ("pending" is not a fix). *(22 Oct 160-gate rows.)*
36. **Literature from papers read, never search summaries.** No "known effect" without the paper's own number.
37. **Paper, site and bill agree number for number** — one batch edit, one push, after the referee.

## Pack L: language-model evaluations, model claims, benches
1. **Parser read by hand before any rate.** 10 replies per family, two models. More than 1 of 10 off → that family CANNOT_TELL (parser).
   *(25 Oct first letter read as the answer, 27 Oct LaTeX and "confidence interval" words read as a width, last number read as the figure,
   30 Oct v1 scorer dropped "equivalent" and read "not better" as a verdict.)*
2. **No rate seen before the hand-check.** Liveness reads progress lines only. Never cat a results file or a log tail first. *(30 Oct, two model-claims rounds.)*
3. **The setup is a carrier.** Harness, prompt format, chat template, extraction rule, shots, max tokens, stop sequences: name both
   sides' setup. If the vendor's differs or is unnamed, a value outside the interval reads CANNOT_TELL with its direction beside it.
   *(30 Oct, two model-card rows.)* Test the rebuttal by running their setup where it is public.
4. **Repeat floor per machine before any across-machine, backend or seed claim**, and item flips counted, not only net rates. Record
   server version, build, parallel slots, flags at run time, on every machine. *(30 Oct two-machine reading, CUDA settings unrecorded.)*
5. **Recount from the released files first, with our code**, keys matched exactly. *(25 Oct 'EvoKD-Adapted' vs 'EvoKD', merged prompt
   templates overwrote each other.)*
6. **The apparatus answering for the model.** JSON mode, think flags, truncation at the length limit, echoed input, refusals: count
   unread and dropped items BY REASON, per arm. *(25 Oct qwen3 echo 193/200, deepseek truncation dropped silently, gemma3 batches dropped.)*
7. **A gold set reviewed from a labeller cannot score that labeller.** A judge's validity is per contrast, not per judge.
8. **Paired, not unpaired. Seed width, not point wins. Position swaps against their copy floor. Batch size as a carrier.**
9. **The prompt must not contain the answer.**
10. **Pinned name is not pinned behaviour.** Backend fingerprint, server, GPU and host are carriers. Same-host repeats are the known-good.
11. **Datasets and tools age.** A pinned dataset or URL that no longer loads is substituted only with row counts checked and an addendum
   written before any result. *(30 Oct HellaSwag source gone, IFEval card unreadable.)*
12. **A referee or labeller from the same model family as the model under test is not an outside seat.** Say so wherever one is used.

## Pack P: public copy (pages, papers, emails, READMEs, lists)
1. **Quotes are verbatim**, checked against the source text. A paraphrase never sits inside quotation marks. *(30 Oct: 8 rows.)*
2. **Every figure says where it lives**: paper text, a table or figure, released data, arithmetic on printed values, a translation, and
   which version. *(30 Oct: flagship figures in paper v1, 12 rows whose figure was in released data.)*
3. **Setting labels match the source.** *(30 Oct: our label read resilience 0 for a resilience-2 figure.)*
4. **No cause named where only a rule-out was measured**, and "we name no mechanism" must be true of the whole text. *(30 Oct: a calibration note named gate
   noise as the cause, and a key line named "the September calibration".)*
5. **Every interval says what it is** (95%? 99%? standard error?). *(29 Oct, two calibration notes.)*
6. **A summary line is no stronger than the committed reading.** *(30 Oct: a summary line said "the exact circuits stay put".)*
7. **The ledger first, the page after, one release path, verified on the live page.**
8. **Check the rendered page, not just the feed**: every script the page loads answers 200 and the section fills. *(30 Oct cal.js, offchain.js.)*
9. **House style rules are written down and checked like any other line** (ours: plain sentences, neutral wording, no count of our own
   work in a title or heading).
10. **Post-hoc labels** on every reading defined after the data (papers and pages).

## Pack O: operations and live feeds
1. **A new scheduled job is registered with the scheduler and with the watch that alarms when it stops.** *(30 Oct live tags.)*
2. **A failure is called a failure**: queues mark a run that printed FAILED as failed, never done. *(30 Oct, a model-card rerun.)*
3. **A GPU budget is set before a GPU job shares a machine**: batch size fixed, memory pool capped. *(30 Oct: automatic batch sizing asked for 63 GB.)*
4. **Liveness by recent completed work**, never by a process existing.
5. **Paths absolute** in hooks, queues and launchd jobs, with PATH set for launchd. *(29 Oct queue path, gh not on PATH.)*
6. **One GPU job per machine**, and "busy" checks know which machine a process uses. *(30 Oct.)*
