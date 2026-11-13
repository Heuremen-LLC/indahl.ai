# Can non-exponential decay fake a negative gate cost?

Question: the "excited population below its own decay curve, deepening with each X gate" finding
(slope per gate -0.0014 to -0.0020 on fez/kingston/boston) uses a bookkeeping that assumes every
excited qubit decays by the same factor q in each 30 us wait. The same campaign shows decay is NOT
a single exponential (62-92 % of qubits sit below their own 300 us extrapolation at 30 us).
Does the estimator give a negative slope for qubits whose X gates are PERFECT but whose decay is
non-exponential? Run: `/Users/heuremen/bones-forge/venv_quantum/bin/python sim_gate_nonexp.py` (numpy, 4 s, no network, reads the published gate_cost.json only). Output: `results.txt`.

## What was implemented
The exact estimator of readfive_slope.py (checked: it reproduces the published single-run values, e.g. fez -0.00182, kingston run 392 -0.00198, boston 711/712/713 -0.00154/-0.00080/-0.00063).
Circuit: start in |0>, n times [wait 30 us, X], read right after the last X (n = 2, 6, 10), so only n-1 waits act on an excited qubit.
Reference: X, then wait 30 / 90 / 300 us. Expected level: `on <- off + on(1-q); off <- on q`, with q from the qubit's own 30 us survival, or the 90 us or 300 us survival scaled to 30 us.
Synthetic qubits reuse each real run's qubit list, per-qubit 300 us survival as anchor, and per-qubit shot errors as noise. The 9 runs are fez 371, kingston 392/721/722/723, boston 441/711/712/713. All X gates are perfect.

## Why a mixture matters (plain physics)
If each shot has its own T1 (a two-level defect near the qubit switching on a time scale longer than one 300 us circuit but shorter than the 800-shot acquisition), a qubit that survived the first wait is more likely a slow one, so its later waits are better than average. The recursion treats every wait as an independent coin with the average q. The averaged excited population after many gates is then not what the recursion predicts, and the difference is negative and grows with gate count, even though no gate does anything. The same shot-to-shot spread also makes the 30 us survival fall below the 300 us extrapolation, which is the measured non-exponentiality. The two effects share one cause.

## Results (full table in results.txt)
Noise-free (exact expectation, slope per gate, own-interval estimator):
single exponential 0.00000; mixture sigma 0.4 -0.00171; sigma 0.5 -0.00260; sigma 1.2 -0.00964.
Controls: same spread but re-drawn independently at every wait 0.00000 (own interval immune); stretched exponential whose clock restarts at each X 0.00000 (immune).
With the real shot noise, a perfect single exponential gives +0.00018 +- 0.00009 (a small positive bias from noise in q, not zero).

Per-run matched test: for each real run the mixture width was chosen so the synthetic share below the 300 us extrapolation equals that run's real share (sigma 0.33 to 0.50). Perfect gates then give a mean own-interval slope of -0.00177, 90 us ruler -0.00172, one exponential -0.00115, against real -0.00136, -0.00138, -0.00101. Per run, model vs real (own): fez -0.00203 vs -0.00182; kingston 392 -0.00251 vs -0.00198; boston 441 -0.00137 vs -0.00139, 711 -0.00145 vs -0.00154, 712 -0.00101 vs -0.00080, 713 -0.00155 vs -0.00063; kingston 721/722/723 -0.00175/-0.00201/-0.00226 vs -0.00114/-0.00134/-0.00161. The model overshoots the mean by about 30 %.

Stretched exponential (Kohlrausch), hazard keyed to time since circuit start: beta 0.9 gives -0.0041, beta 0.8 -0.0075 (own); fitted per run to the same shares the mean is -0.00182. beta above 1 gives a POSITIVE slope (+0.010 at 1.2). If the clock restarts at each X the own-interval slope is 0 (the 90 us and 300 us rulers then go positive, +0.0005 and +0.0010, for beta<1).
Circuit-to-circuit T1 drift (10-60 %): own-interval slope unchanged from baseline, only wider spread.

Timing: an X gate of 0.035-0.1 us lengthening each excited segment gives +0.00001 to +0.00004 (noise-free), POSITIVE and 30 times too small; even 1 us per gate gives only +0.0005 (noisy run). Timing cannot produce the sign.

## Does the "own interval" estimator escape?
No, not for shot-to-shot (persistent) rate spread: own-interval gives about the same as the other two rulers (-0.00171 vs -0.00157 vs -0.00102 noise-free at sigma 0.4). It is immune only when the rate is re-drawn at every wait or the decay clock restarts at every X, because then the 30 us survival is the whole story. The own interval measures the average 30 us survival; it cannot see that survival is correlated from one wait to the next within a shot.

## Limits of this test
* The mixture is a model, not a measurement. Persistence of T1 over a full 300 us circuit and fluctuation between shots is assumed; this simulation shows what follows if it is true, not that it is true.
* Absolute levels: the mixture predicts the n = 2, 6, 10 populations 0.01-0.03 below the real ones (e.g. fez 0.216/0.408/0.484 vs real 0.235/0.431/0.502). Slopes are matched; levels are not. A level offset common to all n does not change a slope, but it is unexplained.
* One free parameter per run (sigma) was set from the share-below-extrapolation, not from the slope. Slopes were not fitted.
* Per-qubit check (results.txt, "PER-QUBIT"): the real per-qubit slope is more negative for qubits farther below their extrapolation (+0.0015 down to -0.0062), steeper than the perfect-exponential synthetic null, which also shows a mechanical gradient from shared noise. A single common sigma does not reproduce the real spread in non-exponentiality, so this is consistent with, not proof of, the mixture.
* The recursion cannot distinguish a real gate cost from an artifact of non-exponential decay. A direct discriminator: run the train with the same total time but fewer/no gates (idle for 30n us then read), and a train whose gates cancel (X X pairs) at fixed time; a pure non-exponential-decay artifact predicts nothing from gates.
