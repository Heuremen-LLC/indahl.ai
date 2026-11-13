# Newsletter edition 1: QIA and IRIS number audit (10 Nov 2026)

Read-only. Nothing in the forge, the ledger or the site was edited. Each number was recounted from raw files with our own short scripts in
/private/tmp/claude-501/-Users-heuremen/ba08385b-5844-4963-b441-21052a55d90b/scratchpad/nl_audit/qia_iris/
(q17_recount.py, q6_recount.py, q6_mirror.py, q2_recount.py, braket_recount.py, braket_b2oct.py, iris_recount.py, hfsize_recount.py, q148_recount.py).
No desk code was imported. Live pages were fetched 10 Nov from indahl.ai/qia, /iris, /hfsize, /media, /qia/t1t2.json, /qia/audit.json and /hfsize/live.json.

## Fix first (mismatches and serious desk findings)

1. **Q17 "every gate-error run" undercounts the runs.** Two more full-chip sweeps on ibm_kingston from 24 Oct (`kingston_usp_pre` dbea907p..., `kingston_usp_post` dbeads7g..., same sweep design, raw files in arxiv_one_readout/sweep_run/) are left out of the 14. Both also read ABOVE: sx 1.348 [1.277, 1.472] and 1.383 [1.268, 1.517], CZ 1.324 [1.220, 1.432] and 1.318 [1.215, 1.409]. The true count is 32 of 32 readings over 16 runs, not 28 of 28 over 14. The ranges and the 1.098 low edge do not change. The /media claim "every gate-error run" is wrong as worded with 14. Run 17 (marrakesh_r2) failed at IBM (error 8299) and has no data.
2. **Braket B2 stated T2 median for 7 Oct: page and ledger say 10.2 µs, the record says 10.1 µs.** The snapshot's median over all 107 qubits is 10.1 µs. The desk's own hand count (09_hand_count.text) also says 10.10. 10.2 is the median over only the 94 qubits that were fitted. Off by 0.1 µs on the page and ledger surface.
3. **Braket B1 "three later sets" are not later than the record they are set against.** The 1.15×, 1.14× and 1.19× readout ratios come from data taken 4 and 5 Oct, 39 to 59 hours *before* the 7 Oct snapshot, with one or two recalibrations in between (desk's own gap notes in 02_readout.py). Only the 28 Sep set (1.07×) is same-epoch. The "1.07× to 1.19×" range mixes one matched reading with three mismatched ones, and the page does not say so.
4. **Braket B2 7 Oct T2 (0.647×) comes from a dose run with ten qubits driven to |1>.** "All clocks" includes neighbours of the emitter qubits. Clocks at least two links from any emitter read 0.680 [0.593, 0.749] (desk's own 0.678). Still BELOW, but the page does not say the 7 Oct T2 data were taken during an experiment that excited ten qubits.
5. **Self-audit fez q148 "T1 0.82 µs against 5.86 published" is stale and depends on the fit model.** (a) IBM's newest record (5 Nov) now publishes T1 = 3.78 µs for fez q148 (live /qia/audit.json), not 5.86. (b) The qubit prepares |1> only 63 to 65% of the time, and its decay is not single-exponential. A free-offset fit gives 0.82 and 1.05 µs (matches). With no offset it gives 9.9 and 3.7 µs. A two-exponential fit gives a fast part of 0.4 to 0.6 µs and a slow part of 3 to 14 µs. (c) The first run's results.json still says "printed CONSISTENT" beside "reading CANNOT_TELL" (Note 3 explains it, but the field pair invites misreading). (d) No ledger row.
6. **Q2 "the other 142 qubits are CONSISTENT" is printed nowhere live and its ledger row has no interval.** bill.other142 has lo/hi null and no surfaces (taken off the bill 23 Oct as an after-the-data reading). Our recount gives median delivered/stated 1.065 [0.768, 1.331] and 0.971 [0.757, 1.459]. Those intervals are too wide to call CONSISTENT under a ±10% margin. Do not print this line.
7. **Q6 restamp (4,204 of 4,204) is accurate for its window but the pairs were chosen as the identical ones.** 17 consecutive record pairs exist in the folder. 14 are identical and 3 were remeasured. The page discloses the 3. The number is also stale: our mirror holds 2,377 newer consecutive record pairs (28 Oct to 10 Nov), and 2,292 of them left every T1 and T2 entry unchanged. The /qia audit panel itself now reports 1,808 restamps that changed no qubit entry and 614 that did. That newer panel number has no ledger row.

## One row per number

### 1. QIA Q17 gate error (28 of 28, sx 1.17 to 1.93×, CZ 1.18 to 1.62×, lowest edge 1.098)
- **Outcome:** MATCH on every cell. The run count is understated (see Fix 1).
- **Recount:** Simultaneous 1q RB and isolated 2q RB refit from raw bits (raw_sweep_*.npz, job meta, props at submission). All 28 medians are equal to the ledger to 3 decimals. sx goes from 1.173 (pittsburgh) to 1.931 (phoenix). CZ goes from 1.179 (boston) to 1.616 (marrakesh). The lowest bootstrap edge is 1.098 (pittsburgh sx). Other bootstrap edges differ from the ledger by at most 0.02 because of the resampling seed.
- **Ledger:** 28 rows qia.gate.* plus media.gate_runs/sx/cz. All match.
- **Live:** The /qia#gates table and /media both match the ledger.
- **Desk audit:**
  - Fixed before reading: yes. PLAN_SWEEP.md was hashed before submission.
  - Selection gate: per-qubit fits need amplitude A > 0.2, and edges IBM states as 0 or 1 are dropped. These gates do not depend on the effect. Dropping the A gate moves no median by more than 0.007.
  - Net hiding flips: yes, in part. Each figure is a median. In every run 8% to 34% of qubits or edges read *below* stated (sx above 1 on 66% to 92% of qubits, CZ on 66% to 86% of edges). "Every run measured above" is true of the medians, not of every qubit.
  - Independence: four pairs share one IBM record and were fired minutes apart (fez×2, phoenix×2, pittsburgh×2, and kingston_r3 with the two usp sweeps). Those are repeats inside one calibration, not 14 independent calibrations.
  - Four outcomes with intervals: yes.
  - Caveat: "two days only" is right.
  - Stale: the newest run is from 24 Oct. The hourly mirror runs read readout and T1, not gates, so there is no newer gate data.
- **Newsletter wording:** In 16 randomized-benchmarking runs on seven IBM processors on 23 and 24 October, the median gate error we measured was above the figure IBM publishes in every run. The single-qubit median ran 1.17 to 1.93 times the stated figure, and the two-qubit median ran 1.18 to 1.62 times. The 95 percent interval on each median excludes 1. These are medians over qubits and edges, and in each run some qubits did better than stated.
  (If the newsletter must keep 14 runs and 28 readings, drop the word "every" and say "in each of the 14 runs in our table".)

### 2. QIA Q6 restamp (4,204 of 4,204)
- **Outcome:** MATCH.
- **Recount:** Read all 30 snapshots in heuremen.org/experiments/calibration-records/restamp_check/. Two boston files repeat a stamp and were skipped. That leaves 17 consecutive pairs with distinct stamps. 14 pairs are identical in every T1 and T2 value and date, which is 4,204 of 4,204 entries. The other 3 pairs are 2 of 312, 2 of 312 and 1 of 306 identical (71.1 to 764.9 h apart). The largest gap among the identical pairs is 49.7 h (boston).
- **Ledger:** bill.r5.restamp 4204, _maxgap 49.7, _other_pairs 3, calrec.restamp_oct23 1549. All match.
- **Live:** /qia#L6 and /media match.
- **Desk audit:**
  - Selection: the 14 pairs are defined by having no change, so "of 4,204" is true by construction. The fair denominator is 14 of 17 pairs, and the page does disclose the 3.
  - Caveat: the page quotes IBM saying the stamp is independent of per-property dates. That is the right caveat. It also means the finding is that the stamp is not a T1/T2 date, which IBM documents. It is not a hidden practice.
  - Stale: yes. Our mirror (qia_mirror/records, 28 Oct to 10 Nov, 8 processors) has 2,377 newer consecutive pairs, and in 2,292 of them every T1 and T2 entry is unchanged (692,118 of 692,118 entries in those pairs). The live audit panel reports 1,808 restamps with no qubit-entry change against 614 with a change. Neither newer number has a ledger row.
- **Newsletter wording:** Across 14 pairs of IBM calibration records from 16 September to 23 October, the "last calibration" stamp moved while all 4,204 T1 and T2 entries kept their values and dates. In the 3 other consecutive pairs we hold, the entries were remeasured. IBM's documentation says the stamp is independent of each property's own date, so the date to trust is the one beside each figure.

### 3. QIA Q2 marrakesh stated zeros (9 of 14 isolated, 11 of 14 all-qubit, medians 0.56 to 0.73%)
- **Outcome:** MATCH for 9 of 14, 11 of 14, 11 of 14, and the medians 0.56%, 0.73% and 0.66%. The add-on "other 142 CONSISTENT" is not printed anywhere live and has no interval in the ledger (see Fix 6).
- **Recount:** raw_ro_ibm_marrakesh, raw_ro_..._run2 and raw_iso_ibm_marrakesh, 20,000 shots per state. Wilson 95% lower bound against 0.292% (0 of 1024). The counts are the same at z = 1.96 and z = 1.645. The 14 stated-zero qubits are the same in both IBM records (19:23 and 20:14).
- **Ledger:** bill.zeros_v2 and bill.zeros.iso_median/allq_run1/allq_repeat. All match. bill.other142: value 0.97 to 1.07, CONSISTENT, lo/hi null.
- **Live:** /qia#L2 matches.
- **Desk audit:**
  - Threshold: the plan fixed 3/4096 (0.073%). The published line uses 0.29% (0 of 1024), switched after the record was found to sit on a 1/1024 grid. This is a post-data change, but in the strict direction (counts drop from 11/14/13 to 9/11/11), and the page discloses it.
  - Flips: per-qubit readings move a lot between jobs minutes apart. For example, q45 reads 2.60%, then 0.02%, then 0.04%. Only 7 of the 14 are above the bound in all three reads. Every one of the 14 is above it in at least one read.
  - Stale: one session on 22 Oct. The hourly mirror runs since 30 Oct read every qubit at rest and could refresh this. We did not check them for stated zeros.
- **Newsletter wording:** On 22 October IBM's record for ibm_marrakesh stated a zero readout error from |0> on 14 qubits. Read alone with 20,000 shots each, 9 of the 14 measured above 0.29 percent, the smallest value a zero on IBM's grid can hide. Read with every qubit at once in two jobs, 11 of 14 did, with medians of 0.56 to 0.73 percent. This was one calibration session on one processor.

### 4. QIA Amazon Braket, Rigetti Cepheus-1-108Q: T2 0.80× and 0.65×, readout 1.07 to 1.19×
- **Outcome:**
  - T2 ratios: MATCH. 28 Sep is 0.805 [0.724, 0.870] against the desk's 0.804 [0.725, 0.874]. 7 Oct is 0.649 [0.581, 0.704] against the desk's 0.647 [0.580, 0.704]. Our own weighted fit differs only in method.
  - Readout ratios: MATCH (1.073, 1.146, 1.143, 1.192).
  - Stated T2 median for 7 Oct: MISMATCH. Page and ledger say 10.2 µs, the record says 10.1 µs (see Fix 2).
- **Recount:** standoff/chip/wchip.npz (28 Sep Ramsey), standoff/time20261004/lookDose_r1full, _r2full and _r3 (7 Oct), chip/run.npz and time20261004/* (readout). Device snapshots: cepheus_props_20260928.json and cepheus_props_live_20261007.json.
- **Ledger:** qia.braket.B1 and B2 (value "text", numbers in the surfaces). They match the page, including the 10.2.
- **Live:** /qia Braket table matches the ledger.
- **Desk audit:**
  - Epoch mismatch: 3 of the 4 readout ratios compare pre-recalibration data with a later record (see Fix 3).
  - Perturbed run: the 7 Oct T2 was measured during a dose experiment with 10 qubits excited (see Fix 4).
  - Window: the 28 Sep Ramsey window reaches only 6 µs, about 0.6 of the stated median T2. The desk notes this internally, but the page does not.
  - Selection gates: fits on bounds or with A ≤ 0.5 were dropped, and emitters were excluded. These gates do not depend on the effect.
  - Four outcomes with intervals: yes (BELOW).
  - Stale: Braket was closed 21 Oct, so no newer data can exist. Say the dates.
  - Folder flag: qia_leads/audits/PRIVATE_aws_braket/README.txt still says "PRIVATE: do not publish until Wayfinder clears it" while the numbers are live. Probably cleared, but the flag is stale.
- **Newsletter wording:** On Amazon Braket's Rigetti Cepheus-1-108Q, the T2 we measured on 28 September was 0.80 times the stated figure, median over 106 qubits, interval 0.72 to 0.87. On 7 October it was 0.65 times, interval 0.58 to 0.70. The 7 October run excited ten qubits on purpose, and qubits away from them read 0.68 times. Readout error measured in the same hour as the record was 1.07 times the stated figure.

### 5. IRIS option order (27% to 50% of answers change, 4 ABOVE and 6 CANNOT_TELL)
- **Outcome:** MATCH within one parsed reply per model.
- **Recount:** Raw replies in iris_index/matrix/results_v2/<model>/mcq4_A and mcq4_rev .jsonl, scored with our own JSON parser and mapped through `order` to the option content. The ABOVE models:
  - mistral 27.4% [21.3, 34.0] (desk 27.3%)
  - phi4-mini 27.8% [21.7, 33.8] (desk 27.8%)
  - falcon3 43.0% before the copy floor and 42.5% after it (desk 42.5%)
  - smollm2 50.0% [42.7, 57.3] (desk 50.0%)

  The first-option control fails for gemma3 (0.60), granite3.3 (0.25/0.45), llama3.1 (0.75/0.90) and olmo2 (0.35/0.53). deepseek-r1 and qwen3 are truncated (108 and 191 of 200 replies). That makes 6 CANNOT_TELL. Score changes on reversal: every interval contains 0.
- **Ledger:** iris.r2.* (10 rows) match the page.
- **Live:** /iris matches.
- **Desk audit:**
  - Fixed before reading: yes. The positive control and the 80% bar are in PLAN_v2.md, written before any v2 call.
  - Gate vs effect: the control uses separate items, so it does not depend on the flip. But it decides the range. llama3.1 (control 0.75, just under 80%) has the lowest flip, 24.0% [18.0, 30.0]. Without the gate the range is 24% to 50%.
  - Low end: the headline sweep file names phi4-mini 27.8% as the low end. The real low end is mistral at 27.3%. The site's "27%" is right.
  - "Consistent with zero": the page says the score change is "consistent with zero for every model read", but the intervals reach 8 to 11 points. Under the four outcomes that is CANNOT_TELL, not CONSISTENT. The page does print the 8 to 11 point reach.
  - Scope: 200 items, one benchmark release, our own server, temperature 0. Data from 25 Oct, and no newer option-order round exists. FaultsBench r12 to r16 test something else.
- **Newsletter wording:** We reversed the order of the four options on 200 theory-of-mind questions. For the four open models that passed our check that they can follow option order, 27 to 50 percent of answers changed. Their scores did not move by a measurable amount, and the intervals still allow moves of up to 8 to 11 points. The other six models could not be read on this test.

### 6. HFSIZE (12 of 135, Prompt-Guard-86M at 279M)
- **Outcome:** MATCH, on today's data.
- **Recount:** We pulled the Hugging Face API ourselves on 10 Nov (top 1,000 by downloads, with safetensors and tags) and applied PLAN.md as amended. The result is AGREE 123, DISAGREE 12, NOT_COMPARABLE 865. The share is 0.0889 [0.0516, 0.1489], which is CANNOT_TELL. Prompt-Guard-86M holds 278,811,651 parameters, ratio 3.24.
- **Ledger:** live.hfsize.v20261110T120408Z: 0.0889 [0.0516, 0.1489], CANNOT_TELL. Match.
- **Live:** /hfsize and live.json: 12 of 135, CANNOT_TELL, 7 organizations, 1 awaiting. Match.
- **Desk audit:**
  - Fixed before reading: the band and thresholds were fixed before the first read. Addenda 1 and 2 changed the token and packing rules after reads, and the whole read was rerun each time. Disclosed.
  - Hand check before showing: the 12th row, openbmb/MiniCPM-V-4.7-1B (ratio 1.554), is counted in the headline but has not been hand-checked. PLAN.md says every DISAGREE row is opened by hand "before it is shown".
  - Tag gate: the packed-or-quantized rule matches tags such as `base_model:quantized:...`, which excludes full-weight repos like all-MiniLM-L6-v2. Matching the name only gives 12 of 143, 0.084 [0.049, 0.141], also CANNOT_TELL. So the gate does not drive the outcome.
  - Clustering: 5 of the 12 are Qwen. The interval treats repos as independent.
  - Caveat: "most mismatches have an architectural reason" is supported by the hand-check notes.
- **Newsletter wording:** Among the 135 most-downloaded Hugging Face models whose name states one size and whose weights can be counted, 12 hold a parameter count outside the band we fixed for that size. Most of the 12 bundle extra parts, such as an audio encoder, or are draft models named after the model they pair with. Meta's Prompt-Guard-86M holds 279 million parameters.

### 7. QIA self-audit, fez q148 T1 0.82 µs against 5.86 µs published
- **Outcome:** NO_LEDGER_ROW. The recount matches the two published fits, but the comparison is stale against IBM's newest record (see Fix 5).
- **Recount:** t1t2_check/runs/results_ibm_fez.json and results_ibm_fez_rerun1.json, 1,000 shots per delay.
  - Free-offset single-exponential fit: 0.818 [0.678, 0.970] µs and 1.052 [0.887, 1.252] µs. These match the published values.
  - Prepared |1> population is 0.63 and 0.65, and the fitted offset is 0.15 and 0.20.
  - With no offset the fits give 9.9 and 3.7 µs.
  - A two-exponential fit gives a fast part of 0.63 and 0.42 µs and a slow part of 13.6 and 3.3 µs.
  - T2 sits on its fit bound in both runs, so CANNOT_TELL is the right reading.
- **Ledger:** none. Zero ledger lines mention q148. Only qia.panel.t1t2.notes_after_results exists.
- **Live:** /qia/t1t2.json carries t1 0.818 and 1.052 and pub_t1 5.863, from the record of 28 Oct. /qia/audit.json now lists fez q148 with published T1 3.784 µs (dated 5 Nov) and T2 15.469 µs (still dated 25 Oct), ratio 4.09.
- **Desk audit:**
  - The 2.5× threshold was set after a first look at boston q85 and fez q148. The page discloses it.
  - Notes 3, 4 and 6 were written after results were read. Disclosed.
  - The rerun's delay grid was sized from the first result, which is effect-dependent. Disclosed in Note 5.
  - The "T1 0.82" figure depends on the fit model for a qubit with a two-part decay and poor state preparation.
  - The published side has moved from 5.86 to 3.78 µs.
  - Do not print this as a headline number until a ledger row exists and the comparison is redone against the current record.
- **Newsletter wording (only if it must run):** IBM's record for ibm_fez qubit 148 lists a T2 of 15.5 microseconds, more than four times the 3.8 microsecond T1 listed beside it. A single qubit's T2 cannot exceed twice its T1. When we measured that qubit on 29 October, it prepared its excited state only about two times in three, and most of its decay happened within about a microsecond.

## Scripts and data used
- Q17: arxiv_one_readout/sweep_run/{raw,job,props}_sweep_ibm_*.npz/json (16 runs including both usp sweeps). failed_20261023/ holds marrakesh_r2.
- Q6: heuremen.org/experiments/calibration-records/restamp_check/*.json.gz and qia_mirror/records/*/ (2,426 files).
- Q2: heuremen.org/experiments/2026-10-22-readout-audit/{raw,job,props}_{ro,iso}_ibm_marrakesh*.
- Braket: standoff/chip/{wchip,run}.npz, standoff/time20261004/*.npz, standoff/cepheus_props_*.json.
- IRIS: iris_index/matrix/results_v2/*/{mcq4_A,mcq4_A_copy,mcq4_rev,pc_A,pc_rev}.jsonl and inputs/.
- HFSIZE: a fresh Hugging Face API read (scratchpad hf_top1000.json) and hfsize_index/PLAN.md.
- q148: t1t2_check/runs/results_ibm_fez*.json and live /qia/audit.json.
