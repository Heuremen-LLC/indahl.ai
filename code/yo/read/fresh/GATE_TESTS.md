# yf_gate.py planted tests, run 4 Nov 2026 ~23:25Z (output copied from the run)
- pending-only (the real plan at that moment): "WAIT: PLAN_YO_FRESH.md has no Bitcoin attestation yet (pending only)", rc 2 -> driver refuses
- wrong file (plan bytes changed, old proof kept): "REFUSE: ... is a proof of different bytes (file changed or wrong proof)", rc 1 -> driver refuses
- known-good (shuffled Addendum 2, block 974519): "PASS: ... block 974519 merkle root matches, mined 1793789571 < start", rc 0
- dead API (YF_API=http://127.0.0.1:9) on the known-good file: "WAIT: ... block API unreachable (URLError)", rc 2 -> driver refuses
- start before the block (NOW=1) on the known-good file: "REFUSE: ... not before start 1", rc 1 -> driver refuses
- driver dry run with both fresh proofs pending: gate prints WAIT for both files, driver exits 2 before loading any adapter.
- yf_gate.py now requires mempool.space and blockstream.info to serve the same block hash and merkle root (Sage, optional upgrade taken). Second server dead -> WAIT rc 2; known-good still passes.
