# Addendum: HOLD -- written 2026-10-24 after job P1 ended, no data read (none returned)

Job P1 dbe84h7sstms73fbkmm0 (ibm_marrakesh): created 10:02:44Z, running 10:20:40Z, ended 22:35:40Z with IBM error 1305
("ran longer than 12h15m0s") while ibm_marrakesh sat in status "maintenance" all day. IBM metrics: quantum_seconds None (nothing billed).
The fire script's job.result() raised RuntimeJobMaxTimeoutError and exited; jobs S1, S2, P2 (and the rest of the plan) were never submitted.
This is the SECOND failure of this run (first: 9703 at P1, 05d68f1). Standing rule: a second failure means HOLD.
Status: HELD. No resubmit without Wayfinder's word. The plan, code and circuits (sha256 ea9bf92a...) stay committed as they are.
