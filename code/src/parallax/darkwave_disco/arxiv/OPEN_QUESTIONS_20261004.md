# Open questions for the measurement paper (internal; carried from the 3 October draft, with 4 October notes)

4 October: #6 answered (both methods printed, no matches claimed); #7 partly (4 October job IDs in Section 2.4; processor revision and qubit count for ibm_marrakesh and ibm_kingston read); #11 partly (ibm_kingston start 1 read three times against its own curve).

## OPEN QUESTIONS FOR THE AUTHORS

(Internal; not part of the paper.)

1. **Hold-run qubit-by-qubit numbers** -- park closure "within 0.002", start 0 +0.0217 ± 0.0016, start 1 +0.0014 ± 0.0014 -- exist only in §135. reads/hold_run.txt prints median-qubit values that differ (parked once +0.0054 to +0.0086; start 0 +0.0050 to +0.0154). Which statistic goes in the paper, and where is the code that computed them?
2. **3.5 ± 0.2 us per readout** [§135, §139]: the computation is not in the release. The hold run's qubit-by-qubit times give 3.8 us (3 readouts) and 3.0 us (9 readouts) per readout. Keep 3.5 ± 0.2, or lead with the eight-job range 3.20-4.26 us?
3. **Single-readout cost**: give-back 3.5-4.1 ± 0.9 us (one job near 1 us at all three positions) against the hold run's single readout at 150 us, −0.0007 ± 0.0009 in level. Report both as drafted, or rerun?
4. **reads/stopwatch_triangle.json** has no producing script in code/; §135's spectator closure (−1.4 ± 4.8 deg, contrast 1.02 ± 0.035 / 0.90 ± 0.03, −3.2 deg per X gate) cannot be regenerated from the release.
5. **The 7.5% family-wise**: it reproduces as 1 − (1 − p)^10 with two-sided p at z = 2.66 (7.6% at the unrounded z = 2.656). Confirm the method, and whether the family should include the two emitter-subset rows (one at −2.1σ).
6. **Ratios** (1.087 ± 0.015, 1.61 ± 0.09, 1.48 ± 0.09): widths are propagated in this draft. Print the ratios at all, or only the three durations?
7. **Missing run facts**: job IDs for every IBM job except run 121; per-job freeze hashes; processor revision and qubit count for ibm_marrakesh and ibm_kingston; circuit count for run 10.
8. **IBM third level**: job list, inter-shot gaps, shots and cloud-exclusion threshold for the two-readout counts [§2]; what "2.3% -> 9.4%" compares in §2; the percentages in §21; whether to print the ibm_kingston carried-qubit labels (left out here).
9. **Rigetti**: what the "mirror check" is; the two variables behind ρ = −0.31; what q33's "0.7 us" lifetime is; task counts per result; whether the task records go in the release.
10. **measure_2 / reset_2** appear in ibm_pittsburgh's supported instructions [reads/pittsburgh_config_timing.json]. Could a direct |2> read on IBM replace the indirect leakage bounds?
11. **Open arms**: ibm_kingston's start-1 column and the halfway start stay unaccounted for. The halfway-separation run (between.py) and replication reads 2-3 are frozen and unfired.
12. **Spectator-versus-table results** (§31): which jobs, which dates, which vendor table.
13. **fire_logs/fire_logs_after.txt is empty** (its sha256 is that of an empty file). Intended?
14. **References**: only Karalekas et al. 2020 is in the sources; the T1-fluctuation / TLS, ZZ-spectator, leakage / reset and measurement-induced-transition literature needs adding and checking. Reviewer acknowledgment: name and permission.
15. **7_PUBLIC's Methods line** "qubits run in random groups of three" holds only for the nine-qubit runs; the whole-chip runs drive every qubit. This draft says so.
