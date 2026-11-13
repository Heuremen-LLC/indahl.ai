# Prior art 1: independent measurement of IBM processors vs IBM's stated figures (searcher, 23 Oct 2026; papers read unless marked)
VERDICT: none of (sx 1.31-1.45x; per-qubit T2 spread vs record age; init_error) is published as such.
- IBM tutorial "Refresh backend properties with real-time benchmarking" (quantum.cloud.ibm.com/docs/en/tutorials/refresh-backend-properties-with-real-time-benchmarking),
  ibm_kingston: 2Q measured above reported, IBM attributes to simultaneous (layer fidelity) vs isolated -> 'not directly comparable'.
  Our CZ RB is ISOLATED per IBM's own recipe, so that attribution does not cover it. T2 median 142 us reported vs 53 us (echo), 56 us
  (8-echo CPMG), 'methodology differences'. 1Q/readout 'track reported for most qubits' (no numbers). MUST CITE.
- Ketterer & Wellens arXiv:2303.14103 (Falcon ibmq_ehningen): reported RB underestimates simultaneous error (qualitative). PARTIAL.
- McKay et al. arXiv:2311.05933 (Heron r1 montecarlo, Eagle sherbrooke): layered vs isolated 2Q errors; Heron 'greatly alleviated'. PARTIAL.
- Proctor et al. arXiv:2112.09853 (Quito): mirror RB vs calibration prediction; NOT READ (PDF failed) -> CANNOT_TELL.
- Metriq arXiv:2603.08680; arXiv:2608.05202; arXiv:2603.04377; arXiv:2507.06941 (casablanca T2 52.5 vs 57.58/48.31): DIFFERENT / weak.
- Research Square rs-10394517 (marrakesh, T2 vs GHZ, July 2026): NOT READ -> CANNOT_TELL.
