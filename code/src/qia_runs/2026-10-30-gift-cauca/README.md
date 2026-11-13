# Your Volunteer's Dilemma circuits on ibm_kingston: drift, the twin, and one record entry

For Germán Díaz Agreda, Jhon Alejandro Andrade Hoyos, Carlos A. Durán Paredes, Sebastián Cajas Ordoñez, Noah Dane Hebdon, Siong Thye Goh and Dax Enshan Koh, from Heuremen LLC. A free calibration of arXiv 2605.30676, "Experimental Implementation of the Quantum Volunteer's Dilemma on NISQ Hardware: Noise Analysis and Digital-Twin Validation".

## The lines it answers

Your twin, built from job.properties(), "does not reproduce non-local effects such as crosstalk or temporal calibration drift" (Sec. 2.3), "the discrepancies with hardware are systematic rather than random" (Sec. 5.2), and your four jobs "were carried out in a single experimental session".

## What we ran

On ibm_kingston on 24 October 2026, 03:52 to 04:01 UTC: your submitted circuits, unchanged. Optimization level 2 (A) and level 0 (B), N = 2 to 9 on physical qubits 0 to N-1, 12 of your 20 repetitions per N, 2048 shots. Four jobs in the order A B B A. IBM's calibration record was saved before every job and did not change across the four. Before reading anything of ours, your released counts went through our code and gave your published level 2 and level 0 means exactly. The twin is your paper's twin (Table A1), rebuilt in our own code from the record saved before the first job, with your released notebook's twin beside it.

## What we found

1. Drift over minutes is small. The same level 2 circuits about 7 minutes apart changed by at most 0.0125 at any N, which is at most 10% of your published twin-to-hardware gap at that N.
2. The two compile levels agreed on our day to within 0.016 at N = 4 to 9, where your published level 2 advantage is 0.008 to 0.120. At N = 2 and 3 our job-to-job noise is larger than your published difference, so we cannot tell.
3. The twin built from that day's record sat above our hardware at every N:

| N | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| Hardware, P(target), job 1 | 0.863 | 0.643 | 0.574 | 0.586 | 0.608 | 0.614 | 0.592 | 0.576 |
| Your paper's twin | 0.972 | 0.948 | 0.921 | 0.894 | 0.874 | 0.851 | 0.813 | 0.768 |
| Your notebook's twin | 0.978 | 0.960 | 0.948 | 0.930 | 0.918 | 0.901 | 0.875 | 0.838 |

In your run the gap changed sign between N = 6 and 7. On our day it did not change sign, and the twin was 0.11 to 0.34 above hardware.

4. Looked at after the data: at N = 2, physical qubit 0 read 0 on 10.8% of the shots meant to read 1. The record listed 1.3% for that qubit. Qubit 1 lost 3.4%.

## From your own files, no new runs

- Your level 2 record lists qubit 1 with readout errors of 0.103 (reads 0 when prepared 1) and 0.219 (reads 1 when prepared 0), against 0.001 to 0.042 on every other qubit, while your hardware read the N = 2 target 96.5% of the time. With that one entry set to the median of the other qubits, your paper twin's gap at N = 2 to 4 goes from about -0.10 to about -0.02, and the twin sits above hardware from N = 5 on, as it did at every N on our day. Most of the small-N part of your gap traces to that one record entry.
- Scaling your twin's stated gate errors by what we measure on kingston (medians of three sessions on 23 and 24 Oct 2026: CZ 1.302 to 1.345 times stated, single-qubit 1.306 to 1.366) closes 17 to 20% of your N = 9 gap. (Corrected 30 Oct 2026: an earlier version of this line put interval ends for CZ beside medians for single-qubit gates and read 13 to 21%.) Stated gate error, even scaled to what the device delivers, leaves most of the large-N gap unexplained.

## What this adds to your paper

The drift your twin cannot model is real but small over minutes. The large-N gap is not stated gate error, even scaled up to what kingston delivers. And the small-N gap comes mostly from one readout entry in the record. A twin that checks each record entry against a quick readout run, and hardware jobs interleaved A B B A, would separate these three.

## What we cannot say

- How large the drift was on your dates.
- What makes the large-N gap. Crosstalk, leakage and coherent error all fit.
- Whether qubit 1's record entry was wrong or the qubit changed during your session.

## Files

- results_cauca.text: every reading, the twin checks, with a legend
- known_good.text: your published means recovered from your released counts

The raw counts of all four jobs, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
