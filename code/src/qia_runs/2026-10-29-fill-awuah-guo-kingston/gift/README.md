# Your SWAP chain on ibm_kingston, run again on 29 October 2026

For Priscilla Awuah and Krystal Guo, from Heuremen LLC. A free calibration of Section 9 and Table 18 of arXiv 2610.20855 ("Perfect and peak state transfer on IBM quantum hardware").

## What we ran

Your SWAP-chain circuits as your scripts build them: X on the first qubit, then SWAP(k, k+1), n = 2 to 21, optimization level 0, seed_transpiler 0, 4096 shots, SamplerV2 with dynamical decoupling off. We read your code as text and rebuilt the circuits and the line search ourselves. Your search on kingston's coupling map returns this line today:

0, 1, 2, 3, 16, 23, 24, 25, 26, 27, 17, 7, 8, 9, 10, 11, 18, 31, 32, 33, 34

In the same minute we ran randomized benchmarking of the single-qubit pulse and of the CZ layer on that line, plus readout circuits. IBM published one calibration record (stamped 2026-10-29 17:58:10 EDT) over the whole run, checked at the start and end of each job. A repeat on one edge followed nine minutes later under the same record.

## What we found

1. Up to n = 14 the chain holds up better than your 27 May table. P(target) runs from 0.957 at n = 2 to 0.753 at n = 14. Yours runs from 0.754 to 0.604.

2. At n = 15 the chain crosses physical edge (9, 10) and P(target) falls from 0.753 to 0.246. It then stays near 0.25 out to n = 21 (0.249). The repeat gave 0.761 and 0.264, a step ratio of 0.347 [0.328, 0.366]. The model built from IBM's own figure for that edge predicts a step of 0.985.

3. Three different measurements agree on that edge.
   - Two-qubit randomized benchmarking: survival 0.303 after a single two-qubit Clifford. Its neighbours (8, 9) and (10, 11) read 0.972 and 0.989.
   - CZ framed as a CNOT, all four inputs: 0.625 [0.615, 0.636] correct. The same circuit on the neighbours: 0.964 and 0.989. The wrong shots land on qubit 9's output, at a similar rate (0.33 to 0.41) for every input.
   - The chain step above.

4. IBM's record lists the CZ error on (9, 10) as 0.00496, dated 19 October 12:10 EDT. Every other edge on your line carries a figure dated 28 October 23:15. All 41 kingston records we hold from 23 to 29 October show that same figure and date. In the September records we hold (26 to 28 September), the figure for this edge was re-dated every day, at 0.0031 to 0.0036. Our own kingston runs on 23 and 24 October saw the same edge at 0.58 to 0.61 survival after one Clifford.

5. This is our second run on your paper. On 24 October we ran your SWAP chains at n = 11 and n = 21 on this same line, four jobs in three minutes. P(target) was 0.20 to 0.23 at n = 11 and 0.07 to 0.08 at n = 21. The largest loss that day sat at the start of the line. With no gate applied, physical qubit 0 read 1 in 0.747 [0.742, 0.752] of 32,768 shots, while IBM's record listed its chance of reading 1 from 0 as 0.0095. Edge (9, 10) was already failing in that run's benchmarking too (survival 0.661 after one Clifford). Tonight qubit 0 is clean (P(target) 0.957 at n = 2).

So on the same line the device lost the excitation in a different place on each day we can see: qubit 0 on 24 October, edge (9, 10) on 29 October, and on 27 May (your table) an offset already present at n = 2 plus two SWAPs further down.

## What this says about your Table 18

This section was worked out after seeing our data, from your numbers and your model.

- On 27 May the step across (9, 10) was 0.995. The edge was fine then, so it does not touch your result.
- Your model gives 0.718 at n = 21. You measured 0.389, a factor 0.542. Split by where it happens:
  - 42 percent of that gap (in log terms) is already there at n = 2 (0.754 against a model 0.974). P(target) then rises at n = 3, which fits a loss tied to the n = 2 circuit's target rather than to the gates.
  - 24 percent sits in the n = 18 step (0.851 [0.814, 0.887] against a model step 0.984). That SWAP crosses edge (18, 31).
  - 15 percent sits in the n = 19 step (0.897 [0.854, 0.941]). That SWAP crosses edge (31, 32).
  - The other 17 steps together hold the remaining 19 percent.
- Tonight those two steps read 0.961 and 1.032.
- A straight-line fit of log P(target) over n = 2 to 14 gives a survival per SWAP of 0.978 [0.977, 0.980] for your table and 0.982 [0.982, 0.983] for ours. The difference between the two days is mostly in the offset (0.849 yours, 1.006 ours), not in the per-SWAP loss.

So the distance between your model and your measurement is not spread evenly over the 60 CZs the model counts. Most of it sits in a few places, and those places move from day to day with the device.

## What we cannot say

Why edge (9, 10) fails, or when between 19 and 23 October it started. Why your n = 2, 18 and 19 points were low on 27 May. We hold no kingston record for that day. A failure like qubit 0 on 24 October would show up as an offset at n = 2, but we cannot say that is what happened. Whether your May run used exactly this line: your search is fixed by the coupling map, so it should, but we did not see your job's layout.

## Cost and files

Tonight's three jobs used 41 QPU seconds (chain 24, benchmarking 15, repeat 2). The 24 October run used 52. In data/:

- raw_chain.json: counts for every n
- repeat_job.json: the repeat's counts and timestamps
- ibm_record_at_chain_start.json: IBM's record in force during the run
- readings_first_run.json, readings_repeat.json: every number above
- results_first_run.text, results_repeat.text: the printed readings
- line_run.py, repeat.py, sweep.py: our code
- PLAN_AWUAH_GUO.md.text, PLAN_REPEAT.md.text: the plans, committed before each job, with the tests on simulated data
- oct24/: the 24 October run (plan, results, raw counts, IBM records before each job)

Heuremen LLC
"We found it."
