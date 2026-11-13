# BLOCKED: fill_knust (arXiv:2605.24166), 23 Oct 2026

Nothing built, nothing fired, no circuits invented. Reason: the circuits behind Table 2 exist nowhere we can reach.

## What the paper gives
- Sec. 10.1: "All experiments use the qml-security Python package (v0.1.0)." No URL, DOI or repository anywhere in the arXiv PDF text, the arXiv HTML (v2), or main.tex (also searched for github / zenodo / data availability: none).
- Eq. 33 / Sec. 10.2 gives the 4-qubit family: |psi(x)> = [prod RY(alpha_i x_i)] [prod CZ_{i,i+1}] [prod RZ(0.5 alpha_i x_i)] |0>, alpha = [3.0, 1.0, 0.3, 0.1].
- Table 2 gives only T_ideal = sqrt(1-F) (0.640, 0.900, 0.931, 0.980, 0.974) and d_H (0.032, 0.035, 0.043, 0.049, 0.053) per pair.

## What is missing
The five input pairs (x_a, x_b in R^4 for each pair) are not printed. T_ideal fixes only |<a|b>|^2 for each pair, which leaves a continuum of (x_a, x_b); matching T_ideal would be inventing the circuits.

## Where I looked (all in /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_knust/)
- arXiv abs page and HTML v2: no code/data link.
- arXiv e-print (arXiv-2605.24166v2.tar.gz, 212 KB): contains only main.tex, main.bbl, 00README.json and 11 figure PDFs (figures/fig9_ibm_circuit.pdf is a drawing of ONE transpiled circuit, not five pairs; not executed, not parsed for inputs). No data files, no scripts.
- PyPI qml-security: /simple/ and /pypi/.../json return 404 (page itself sits behind a bot challenge; no package index entry found).
- GitHub repository search (qml-security, quantum Fisher differential privacy qiskit): no match. Zenodo search (qml-security, QFI differential privacy ibm_fez): no match.
- Not tried: contacting the authors (forbidden: nobody is contacted).

## Further observation (not acted on)
The paper's descriptions of the hardware circuit disagree with each other: Sec. 12.3 says "Hadamard + RZ(pi x_i) rotations followed by a nearest-neighbor CZ ladder"; Eq. 33 is RZ, CZ chain, RY; Fig. 1 lists 8-bit outcomes (2 classical bits per qubit) while the audit's floor arithmetic assumed 16 outcomes. Even the circuit structure is not pinned without the package.

## What would unblock
Any one of: (a) the qml-security v0.1.0 source or the script that produced Table 2 (the five x pairs), (b) the job d7s2kscf3ras73b7h4ug inputs/results, (c) Wayfinder's decision to build a clearly-labelled reconstruction (five self-chosen pairs matching the printed T_ideal under Eq. 33), which would test the same question (shot floor, drift, fidelity by protocol) but would NOT reproduce their Table 2, so KNOWN-GOOD against their published d_H could not be claimed.
