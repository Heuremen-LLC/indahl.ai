# Moderna/IBM mRNA folding: the classical baseline (23 Oct 2026; zero IBM seconds)
Papers: Alevras et al., arXiv:2405.20328 (IEEE QCE 2024): hardware CVaR-VQE runs at 26, 40, 50, 80 qubits 'match the results of the
classical solver CPLEX'; Kumar et al., arXiv:2505.05782 (2025): 133/150-qubit runs on ibm_marrakesh 'find the optimal solution after
post-processing'. Neither publishes sequences, code, or the penalty values r, p, t of its QUBO.
What we did: the papers' quartet QUBO (2405.20328 Eq. 3) built from the Turner 2004 stacking energies (NNDB file, sha256 in
nndb/SHA256.txt), r = 0, p = +0.45 kcal/mol (Turner terminal AU/GU), t = 1 + sum|e| (disclosed: theirs unpublished); random sequences sized
to the papers' hardware instances; exact optimum by HiGHS MILP (checked against brute force). Then the baseline neither paper ran.
Results (none_test.text, none_starts.text): uniform random sampling with the papers' own sample budgets found the optimum in 0 of 48
instances (26-80 variables). Plain single-bit-flip descent from random starts found the exact optimum in 12 of 12 instances at every size:
median starts 6 (26 vars), 8 (40), 14 (50), 47 (80), 248 (133), 562 (150); worst 6,293; laptop time under 0.7 s per instance.
Status: the scripts were written before they ran but NOT pushed before (not pre-registered). none_starts.py was defined after
none_test.text was read. Instances are ours (theirs are unpublished); rerunning on their instances is one command.
Reading: at the sizes run on IBM hardware, matching the exact optimum is met by a trivial classical heuristic in under a second, so it is
not evidence that the quantum computer contributed. It does not show their hardware failed.
