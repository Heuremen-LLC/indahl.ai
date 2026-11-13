# BLOCKED -- arXiv:2507.06361 (Ahsan, UET Lahore; ibm_marrakesh). 23 Oct 2026. No build, no job, no QPU seconds spent.

Gate: KNOWN-GOOD (step 2) -- his published Table 3 marrakesh row must reproduce from his raw logs. It does not.

Published (paper Table III, marrakesh): Actual -115.12 +/- 0.24 | Ref ODR -100.23 +/- 2.12 | Noise mitigated -168.84 (= 147/100.23 * 115.12; arithmetic is consistent).
Download: github.com/ahsan-quantum/Kagome-Lattice-VQE (cloned to scratchpad dl_uet/repo, nothing executed). Only ONE marrakesh 13-pub + ancilla log exists
in "Raw Data/" (Last day.txt, session 0517bd88..., three passes of pubs 0-12 plus pub 13 = ancilla). Every other marrakesh log is a different
experiment (parameter-set comparisons at -100 to -107, Table IV style). Recomputed from that one log:
  Ref ODR (pub 13, 3 passes): -100.240 +/- 2.128 (sample sd)     vs published -100.23 +/- 2.12   -> reproduces to ~0.01
  Actual (pubs 0-12, 3 passes, 39 values): -114.593; sd of 13 pub means / sqrt(13) = 0.245 (his 0.24 matches this definition)
                                                                  vs published -115.12            -> OFF by 0.53 (2.2 x his own +/-)
  Mitigated 147/(-100.240) * (-114.593) = -168.05             vs published -168.84            -> OFF by 0.79
The only way to get -115.12 from the log is to pick a 2-pub slice of 2 of the 3 passes (-115.118): a fitted subset, not a reproduction.
The gate demands 1e-4 to printed precision (here 0.01); the Actual and Mitigated cells fail it.

Also, the repo cannot support an exact re-run of the Table III estimator job as published:
 - the notebook ("Qiskit_100_qubit Kagome VQE.ipynb", 92 cells) is a scratch pile: obsolete builders, commented-out switches, and several incompatible
   estimator option sets (ZNE noise_factors (1,1.01..1.05) vs (1,2,3), default_shots 512 vs 256, Batch vs plain mode, ancilla job separate from ansatz job
   in the live cell although the paper says ratio is maximised "within the same Qiskit job");
 - the marrakesh log labels no job id for the Table III numbers (the "d029hvd1r6vs73diq6tg" id in Paper.txt is the Table IV comparison, mean ~ -106).
Per the DROP RULE (method described two ways: same-job in the paper, separate ansatz/ancilla estimator.run calls in the notebook; no reproduction of the
published row): OFF. No reconstruction, no free run, no ask-the-author.
