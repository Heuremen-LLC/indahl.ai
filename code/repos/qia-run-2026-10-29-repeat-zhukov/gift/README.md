# Your DM-triangle circuits on ibm_kingston, 24 and 29 October 2026

For Andrey Zhukov, from Heuremen LLC. A free calibration of arXiv 2609.15411v2, "Exact quantum circuits for a Heisenberg triangle with Dzyaloshinskii-Moriya interaction".

## What we ran

Your 76 circuits from your Zenodo record (the raw/003 controls and the raw/005 chain-C circuits), unchanged, on your physical qubits (lanes 16-3-2, 21-36-41, 96-103-104, 69-68-67, 129-118-109, 38-49-50), plus 10 of ours on qubit 16 (two reads back to back, and a 100 microsecond delay before the read) with a matching control on qubit 3. 1024 shots, four jobs in A B B A order each night, no twirling and no dynamical decoupling. IBM's calibration record was saved before every job. The same circuit file ran both nights (sha256 checked). We read your code as text and never ran it.

## What we found

1. Your exact circuits hold and the Trotter circuit moves. Chain C at Jt = 4/3, signed phase error of C1, in degrees:

   | | 16-17 Sep (yours) | 24 Oct (ours) | 29 Oct (ours) |
   |---|---|---|---|
   | Exact circuit | +2.9 | -1.2 +- 3.1 | +0.5 +- 1.7 |
   | Strang r = 8 | +46.3 | -46.8 +- 4.1 | -9.3 +- 3.8 |

   Intervals are 99 percent and include the job-to-job spread. The Strang shift between our two nights is +37.4 +- 5.6. On simulated pairs of nights with nothing changed, the same reading never called a shift (0 of 200), and a planted 25 degree shift was found every time (40 of 40). Your exact circuit stays within 3 degrees of zero on all three dates. The second-order Trotter circuit lands in a different place each date.

2. The qubit-16 anomaly is absent on both nights. In your raw/003 solo controls qubit 16 read 1 after a preparation in 0 in 0.766 of shots (6,273 of 8,192). Ours: 0.0123 [0.0101, 0.0146] on 24 October and 0.0082 [0.0060, 0.0104] on 29 October. IBM's record listed 0.0093 and 0.0132 to 0.0159 on those nights. The double-read and delay arms found nothing to separate on either night.

3. Your 24 control circuits: the smallest correct-outcome probability per chain, averaged over the five science chains, is 0.964 in your data, 0.897 on 24 October and 0.949 on 29 October.

4. Jobs minutes apart agree within shot noise on both nights.

## What this adds to your paper

Your comparison of exact and Trotter circuits now has a time axis. The Trotter distortion is not a fixed offset that one calibration could remove, while the exact circuits stay near zero across three dates. The same circuits read qubit 16 clean now, so the September anomaly is not built into the circuits.

## What we cannot say

Why the Trotter phase moves between dates, or what happened to qubit 16 in September.

## Files

- README.md (this file)
- results_24oct.text, results_29oct.text: every reading of each night, with the four outcomes
- date_reading_29oct.text, readings_date.json: the three-date phase comparison
- synth_date_floor.text: the test on simulated nights

The raw shot codes for both nights (eight jobs), IBM's records before every job, our code and the plans committed before each run are about 1 MB and yours on request. The two nights used 104 QPU seconds each.

Heuremen LLC
"We found it."
