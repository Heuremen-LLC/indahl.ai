# Prior art 4: mid-circuit readout crosstalk vs the paper (searcher, 23 Oct 2026; arXiv abstract/HTML read)
NO paper reports a per-readout phase kick on untouched qubits against an equal idle on IBM Heron.
MUST CITE + RECONCILE (uncited in main.tex):
- Harper et al. arXiv:2504.07258 (Nat. Commun. 2026, s41467-026-71773-6), Heron r1 + Heron r2 MARRAKESH: r1 'considerable crosstalk'
  from MCM, 'mainly resolved' on r2; on Marrakesh 'In neither case were any significant cross-talk issues noted'; spectator loss put down
  to relaxation during the ~2 us measurement; qubit 90 fidelity 0.998 -> 0.983 per cycle. No phase, no equal idle. TENSION with our
  marrakesh kick: reconcile (they read fidelity/survival, we read phase against an equal idle of the same scheduled length).
- Shirizly, Govia, McKay arXiv:2408.07677 (IBM, Eagle ibm_pinguino1): measured block vs Delay control shows signs of 'measurement-induced
  Z-phase or crosstalk'; pair errors 0.077 no DD -> 0.042 MDD -> 0.032 FFDD. Closest design precedent (delay control + DD fix), no phase number.
- Hashim et al. arXiv:2403.18768 (LBNL ring, appendix E): MCM dephasing of spectators via static ZZ and unresolved resonators. PARTIAL.
- Gicev et al. arXiv:2605.26528 (review, May 2026): 'IBM have characterised measurement crosstalk ... coherent Z[Z] rotations between qubits
  that share readout resonators'; primary reference NOT traced -> TRACE BEFORE SUBMISSION (possible close IBM precedent).
- 2506.11270, 2511.10921, 2605.05256, 2607.12118: DIFFERENT.
ALREADY CITED, check wording: Hothem -- add 'the majority ... remain unexplained'; Govia -- its own Z-phase estimate ~0.05 rad (~3 deg,
  large uncertainty) from eps_IRB 1.7e-3 +- 1.0e-3 is the same order as our 1.7-2.4 deg/readout: the paper should say so plainly.
  Smith2026, Gao2025, Hoyau2026, Kan2026 entries NOT verified by the searcher -> verify.
