
## 2026-10-31 18:06 Darkwave clock synthetic: planted worlds through clock.py readers, both chips (synth_results_clock.text, FIRST pass kept)
packs: Q
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every arm's none is D in the same job and the same synthetic draw (shared free precession); no qubit is dropped by its kick; the known-good gate drops whole chip-fires only, counted per world (W0 40/40, WA marrakesh 1/20).
- II: holds: the clock reading is a per-qubit paired difference on the same resampled qubits, not a difference of two separate nets; copies A and B read separately before pooling.
- III: holds: shares use |residual| and |kick| (magnitudes, stated); the signed kick is read separately for the known-good (below 0).
- V: holds: ruler = the keystone S7 share given back (unchanged) and its paired difference with a 0.05 equivalence margin; R3/R4 put the 21 Oct table on the same ruler.
- VI: fixed: CONSISTENT only when the whole band sits inside [-0.05, +0.05]; a band reaching both 0 and the margin reads CANNOT_TELL. Planted worlds test both: no change (reads CONSISTENT/CANNOT_TELL) and 1 deg changes (read BELOW).
- R: holds: draw counts and outcomes copied from synth_results_clock.text and synth_results_clock_FIRST.text as written by the script.
- QA: n/a: no vendor figure is compared in this reading; the run saves IBM's record before every job.
- QB: holds: D idles exactly the readout length per look; dry run on both chips shows equal scheduled durations for all five arms (kingston 4,921 dt, marrakesh 6,057 dt).
- QC: caught: the first synthetic pass put a 0.25 deg jitter inside the no-change world and read BELOW in 2 of 10 marrakesh draws; the jitter is now its own probe and its rates are reported as the ruler's resolution. Worlds planted: no change, jitter, aged, moved, null.
- QD: holds: FINAL = pooled if copies agree, else CANNOT_TELL; chips read separately, never combined; units deg per readout and a share.
- QE: holds: no mechanism named; a BELOW says the table no longer matches, not why.
- QF: holds: plan, code hashes and synthetic committed before any job of this run; table ages will be computed from job timestamps.
- QG: n/a: no outside referee on the synthetic; the plan's design is the keystone's (refereed 31 Oct) with arms removed, none added except M31 and MT, both corrections of the same kind as MF.

## 2026-10-31 18:09 Darkwave clock, first fire (31 Oct 22:06 UTC, 31 Oct table 3.0 h old): kingston M31-MT -0.013 [-0.043,+0.031] CONSISTENT; marrakesh -0.021 [-0.104,+0.036] CANNOT_TELL; marrakesh MC-MT -0.504 BELOW
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every arm read against D in the same job; known-good passed on both chips (kingston -2.538 [-3.904,-1.926], marrakesh -1.752 [-2.293,-1.123]); no qubit dropped (n=117 on every reading)
- II: holds: the clock reading is the paired per-qubit difference on the same resampled qubits; copies A and B read apart before pooling (kingston A and B both CONSISTENT; marrakesh both CANNOT_TELL)
- III: holds: shares are magnitudes of residual over magnitude of kick, stated as such; signed kick read only for the known-good
- V: holds: the keystone S7 ruler unchanged; the paired difference with the committed 0.05 margin; MC on the same ruler
- VI: holds: marrakesh's band reaches -0.104, past the margin, so it reads CANNOT_TELL, not CONSISTENT; MC share vs 0.5 on marrakesh reads CONSISTENT under the keystone rule because its pooled band reaches 0.510 (both copies BELOW): reported with its band, never as 'the same as 0.5'
- R: holds: values copied from results_clock.text as written by analyze_clock.py (committed f682ff4 before the jobs finished); table ages from the job records (3.0 h, 239.1 h); seconds from the job records (27 s per chip)
- QA: n/a: no vendor figure in this reading; IBM's record saved before every job (props_before_*.json)
- QB: holds: equal scheduled durations for all five arms (kingston 4,921 dt, marrakesh 6,057 dt) checked in the dry run and again after job C
- QC: holds: known-good on real hardware passed on both chips; synthetic resolution stated in the plan (about 0.25 deg/qubit changes mostly unresolved)
- QD: holds: FINAL = pooled if copies agree; chips read separately, never combined
- QE: holds: no mechanism named; one fire is one point
- QF: holds: plan c37242a and analysis f682ff4 committed before any result was read; jobs C, A, B per chip in the job records
- QG: n/a: no outside referee read this fire yet; the page copy states what the numbers are and links the raw files
- P1: n/a: the page and this entry quote no one, so there is nothing to check verbatim
- P2: holds: page figures say first fire, 31 Oct 22:06 UTC, table age 3 h, and link the run files; paper figures cite the paper
- P3: holds: arms named as in the plan (31 Oct table, table from minutes before, ten-day table)
- P4: holds: no cause named for any change
- P5: holds: bands stated as 99 % bootstrap over qubits on the page
- P6: holds: kingston 'holds at 3 hours within 0.05'; marrakesh 'cannot tell at that margin'; nothing stronger
- P7: holds: ledger rows added before the page surface; release only via ship.sh at midnight, verified live then
- P8: cannot tell: the page is not live yet; checked in the browser after the midnight ship
- P9: holds: no AI statement, no count of our things in headings, plain sentences, byline Wayfinder and Bones
- P10: holds: no post-hoc reading in this entry; the paper's post-hoc readings keep their labels where quoted
