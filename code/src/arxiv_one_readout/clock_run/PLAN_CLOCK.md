# The Clock: does a fixed circuit's output on IBM hardware reveal when it ran?
Pre-registered; hashed with the code before any job. Heuremen LLC, 23 Oct 2026. Code: clock.py; planted worlds: synth_clock.text.
Why: HSBC + IBM arXiv:2509.17715 reports out-of-sample AUC 0.95-0.98 from hardware-transformed features (noiseless simulation 0.58-0.61),
keeps the gain when the two-qubit operations are replaced by idles, and writes "we cannot exclude that the order of processing these
quantum circuits on hardware ... would yield some form of non-trivial information leakage with respect to the RFQ outcome labels".
Design: ibm_fez (one of the paper's repeat chips), Darkwave Disco. One fixed 156-qubit circuit (RX layer, 2 Heisenberg blocks RZZ/RXX/RYY
0.2 rad on all couplers, seed 0), SamplerV2 4096 shots, Pauli twirling on (as the paper). 16 sequential jobs, each sent when the previous
returns. Per-qubit <Z> per job, and from two half-shot splits.
KNOWN-GOOD: none possible on hardware -- no qubit is known NOT to drift, so there is no real-hardware case with a known answer. Stand-ins:
the planted worlds (synth_clock.text, 3 seeds each: no-drift R1 0.6-1.3 % of qubits against 1 %, R2 CONSISTENT 3 of 3; planted drift R2 ABOVE
3 of 3), and on hardware the within-job half-split differences, printed against binomial shot noise.
NOTE: a first fire was started at 18:4x EDT before this plan was committed (the gate refused it) and was killed before any job was
submitted (IBM job list checked); this plan is committed before the run that counts.
READINGS: R1 DRIFT -- share of qubits whose between-job variance exceeds shot noise (F test (J-1, J), p < 0.01); R2 CLOCK --
leave-one-job-out ridge regression features -> run time, R^2 against 2000 time-shuffled refits; ABOVE if R^2 > the null's 95th pct.
Use: QIA portfolio (HSBC lead) and the mechanism note; CONSISTENT is printed as such.
