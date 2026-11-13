# The measured qubit's own loss, as a multiple of the stated readout time

Package of one finding from the Oct 2026 IBM Quantum campaign (`2026-10-04-three-positions`). Everything in the table below is recomputed from `data/` by
`verify_measured_qubit.py` (Python standard library only, no account, no network):

    python3 verify_measured_qubit.py

## What the number is

When a qubit is measured, the readout is meant to leave the other qubits alone and take about the chip's *stated* readout duration. We read the same qubit
k times in a row (k = 1, 2, 3, 4, 6, 9) and ask how much excitation the measured qubit itself has lost. To turn that loss into a time, we look up how long
the same qubit, left alone with no readouts, takes to lose that much on its own decay curve (a straight line in log-population against waiting time, fitted
through 0, 10, 20 and 40 microseconds). That time is the qubit's *T1-equivalent time* for k readouts. The slope of that time against k is the
time-equivalent of one readout. Dividing by the stated readout duration gives "qubit / stated": a value of 1.5 means each readout costs the measured
qubit as much as 1.5 times the stated duration of free decay.

Two estimators of that slope are used: the **3-and-9** two-point slope, (time after 9 - time after 3) / 6, and the **1-9 fit**, a least-squares line over all six k.
Both are medians over qubits within a read (about 28 to 31 qubits per read pass the cut that the |ground - excited| separation exceeds 3 widths).
The table gives the mean over 3 reads of each chip and the sample standard deviation (n-1) of those 3 reads. This is read-to-read spread, not a
confidence interval; 3 reads cannot give a good one.

"Spectators" are phase-clock qubits held half-way: they are not measured, and their phase turns as the measured qubits are read. Their per-readout time is
read the same two ways off their own phase-versus-time curve (quadratic through 10, 20, 30 microseconds). "qubit / spectators" is the measured-qubit median over
the spectator median. (The reader labels this corner WITNESS; I use "spectators" because that is the word in the request. No values for this ratio were supplied, so it is printed with NO CLAIM.)

## Reproduced table (qubit / stated; computed by the script, mean +- sd over 3 reads)

| chip | stated readout (us) | 3-and-9 | supplied | 1-9 fit | supplied | verdict |
|---|---|---|---|---|---|---|
| kingston | 2.180 | 1.661 +- 0.086 | 1.661 +- 0.086 | 1.677 +- 0.078 | 1.677 +- 0.078 | OK |
| marrakesh | 2.684 | 1.516 +- 0.070 | 1.516 +- 0.070 | 1.509 +- 0.024 | 1.509 +- 0.024 | OK |
| fez | 1.660 | 1.540 +- 0.224 | 1.540 +- 0.224 | 1.600 +- 0.186 | 1.600 +- 0.186 | OK |
| pittsburgh | 2.180 | 1.340 +- 0.063 | 1.340 +- 0.063 | 1.360 +- 0.087 | 1.360 +- 0.087 | OK |
| boston | 2.180 | 1.348 +- 0.136 | 1.348 +- 0.136 | 1.333 +- 0.124 | 1.333 +- 0.124 | OK |
| phoenix | 1.940 | 1.351 +- 0.124 | 1.351 +- 0.124 | 1.323 +- 0.056 | 1.323 +- 0.056 | OK |
| aachen | 2.180 | 1.371 +- 0.115 | none | 1.351 +- 0.057 | none | computed only |

24 of 24 supplied numbers reproduce at 3-decimal precision. Aachen data exist (runs 801-803) and are included; no earlier value existed to compare. The script also
prints the qubit / spectator ratios and every individual read.

The data were also run through the published reader `readlook_3and9.py`, unchanged, on the private raw data. The per-read values it prints agree with the
script's (the script is an independent stdlib re-implementation, not a wrapper).

## The assumption, and where it fails

Converting a loss into a time assumes the plain decay is a single exponential. The same campaign shows it is not exact. In the ruler copies of the
time-wide runs (ON state, waited 30 and 300 microseconds), the survival after 30 us sits *below* the single-exponential line drawn through the 300 us point
(S300^(30/300)) for a large share of qubit-copies. The script recomputes this share per read from `data/ruler_check.json`:
marrakesh 80.2-84.1 %, kingston 72.4-77.9 %, pittsburgh 62.4-64.7 %, fez 83.6-85.3 % (12 reads, range 62.4-85.3 %).

**Discrepancy:** the supplied range is 62-84 %. The recomputed range is 62.4-85.3 %; the top is fez read 2 (85.3 %) and fez read 1 (84.6 %). The lower end and the other chips agree. The check can only be recomputed for marrakesh, kingston, pittsburgh and fez: for phoenix, boston and aachen
the ruler runs found in the raw folder are in different register formats (or a single copy), and were not reduced here. So "62-84 %" should be quoted as
"62-85 % on the four chips with time-wide ruler copies". The estimator here fits a log-linear curve through 0-40 us, which is shorter than 300 us, so the
non-exponential shape matters for the *level* of the absolute numbers; the cross-chip ordering is a separate question this package does not test.

## What is in the folder

- `verify_measured_qubit.py`: the verifier (stdlib only).
- `data/measured_qubit.json` (0.9 MB): per chip, per read, per qubit: separation, levels after 10/20/40 us of waiting, levels after each of 6 readout counts, and for the spectator clocks the X/Y levels at 0/10/20/30 us and after each readout count; plus the stated readout duration.
- `data/ruler_check.json` (0.2 MB): per qubit and ruler copy, the ON survival at 30 and 300 us.
- `extract_measured_qubit.py`: how the JSON was cut from the private raw I/Q (needs numpy and the private data; readers do not need it).

## Runs and IBM job IDs

Look-wide reads (three per chip, used for the table). Stated readout duration is the median of `measure_duration_s` in `ibm_<chip>_maker_look_length_20261004.json`, read 4 Oct 2026.

| chip | stated (us) | runs and job IDs |
|---|---|---|
| ibm_marrakesh | 2.684 | 311 `db1644jid5ic73eqn2g0` ; 312 `db1657megvvc73bh72q0` ; 313 `db1661avog1s73fhn6e0` |
| ibm_kingston | 2.180 | 331 `db16b22vog1s73fhnefg` ; 332 `db16ctuegvvc73bh7f10` ; 333 `db16ff9b694s73drsdag` |
| ibm_pittsburgh | 2.180 | 351 `db16oh6egvvc73bh7r90` ; 352 `db1air9b694s73ds1jcg` ; 353 `db1aj93id5ic73eqsomg` |
| ibm_fez | 1.660 | 411 `db1ct8avog1s73fhvl00` ; 412 `db1ctkbid5ic73eqvm2g` ; 413 `db1ctvhb694s73ds4hi0` |
| ibm_boston | 2.180 | 431 `db1d5bjid5ic73eqvtf0` ; 432 `db1gqc2vog1s73fi3tpg` ; 433 `db1gqnavog1s73fi3u7g` |
| ibm_phoenix | 1.940 | 541 `db1ots9b694s73dsk0k0` ; 542 `db1oujivog1s73fif5og` ; 543 `db1ouv6egvvc73bhv5q0` |
| ibm_aachen | 2.180 | 801 `db2qqercqljs73cln870` ; 802 `db2qvj5v86ts73dhjv3g` ; 803 `db2r4ltv86ts73dhk3mg` |

Ruler reads (time-wide runs, used only for the single-exponential check): ibm_marrakesh 301 `db15r4bid5ic73eqmhs0`; ibm_marrakesh 302 `db15s4pb694s73drrg10`; ibm_marrakesh 303 `db15skrid5ic73eqmkvg`; ibm_kingston 301 `db15t52vog1s73fhmo3g`; ibm_kingston 302 `db15u31b694s73drrjvg`; ibm_kingston 303 `db161j6egvvc73bh6u50`; ibm_pittsburgh 361 `db16p5hb694s73drsna0`; ibm_pittsburgh 362 `db1ak0qvog1s73fhspdg`; ibm_pittsburgh 363 `db1akdeegvvc73bhcoh0`; ibm_fez 401 `db1cs81b694s73ds4fs0`; ibm_fez 402 `db1csj3id5ic73eqvl20`; ibm_fez 403 `db1cstmegvvc73bhfing`

Submission times and code hashes for every run are in `runs.json` of `experiments/2026-10-04-three-positions`.

## Caveats

- Three reads per chip: the +- is a spread of three numbers. Fez shows the widest spread (read 2 is 1.80 on the 3-and-9 estimator against 1.40 and 1.43 for the other two).
- The reads of a chip were not all taken at the same time of day (for pittsburgh and boston, read 1 was submitted hours before reads 2 and 3).
- Both estimators share the same qubits, the same waiting-curve fit and the same single-exponential assumption, so agreement between them is not independent confirmation.
