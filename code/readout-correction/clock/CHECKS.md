
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

## 2026-10-31 18:31 Darkwave clock first fire, after the referee: kingston clock reading CANNOT_TELL across bootstrap draws (18 of 20); copy gaps unresolved; IBM restamp between tables
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same arms, same job, same qubits as the committed reading; nothing dropped (n=117)
- II: caught: the committed label at one seed hid that copy B's band sits at the margin; reading the label across 20 seeds shows CANNOT_TELL in 18
- III: holds: the copy gap is reported signed; marrakesh copies differ in sign and it is said
- V: holds: same share ruler; the seed spread of the label is the second ruler and it disagrees with the single-seed label, so the reading goes out as CANNOT_TELL
- VI: fixed: kingston goes out as CANNOT_TELL (pooled band inside the margin, one copy at its edge), never as holds
- R: holds: seed counts, edges and record stamps printed by the scripts and read from props_before_C files
- QA: holds: IBM's stated T1, T2, readout length and readout_error compared per qubit between the two records the jobs ran under
- QB: holds: unchanged from the committed reading
- QC: holds: the synthetic resolution (about 0.25 deg per qubit mostly unseen) is now stated on the page
- QD: caught: FINAL compared copy labels; the copy gap with its width is now printed (addendum 1) and both copies' edges are reported
- QE: holds: no mechanism named; the IBM restamp is reported without a cause
- QF: fixed: the plan's written times corrected by addendum 2 from the git and job records
- QG: fixed: outside referee (same model family as the writer) read the raw files; every flag acted on in the page before publish
- P1: n/a: the page quotes no one, so there is nothing to check verbatim
- P2: holds: page figures name the paper (31 Oct run) or the first fire and link the files
- P3: holds: arms named as the paper and plan name them
- P4: holds: no cause named
- P5: holds: bands described per setup (qubits, pairs, shots)
- P6: fixed: 'holds' removed for kingston; 'less than a minute before'; one point, no rate claimed
- P7: holds: ledger rows go in with the release before the surface goes live
- P8: cannot tell: page not live yet; rendered check after the midnight ship
- P9: holds: no AI statement, no count of our things in headings, plain sentences
- P10: fixed: 'more than ten degrees' and 'two that moved' labelled defined after the data

## 2026-11-01 07:28 Darkwave clock second fire, ibm_marrakesh 1 Nov, after the referee: clock reading BELOW by the plan with the upper end on zero, below in 3 of 20 other seeds, printed as a lean; difference widened because the fresh table's residual fell
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same arms in the same job, same 117 qubits as the committed reading; nothing dropped (n=117 in every arm)
- II: caught: the widened difference (-0.02 -> -0.06) came from the fresh table residual falling 0.302 -> 0.245 while the 31 Oct table stayed 0.344 -> 0.349; per-qubit counts 71/46 pooled, 68/49 and 65/52 per copy, 64/53 at the first fire
- III: caught: the share folds the residual sign; signed medians printed (MC +0.932, M31 +0.169 with its band through zero); over-correction counted per qubit (64 of 117)
- V: holds: committed share ruler at the plan seed, then the seed spread (3 of 20 BELOW) and the exact sign test beside it; they disagree, so the page prints a lean
- VI: fixed: zero barely excluded at one seed and not at 17 of 20; the 0.05 size inside the band; printed as a lean with the upper end at 0.00, never as a change
- R: holds: every number from results_clock.text, readings_second.text and readings_compare.text, recounted by our code after the referee; table age 16.9 h from the job record; post hoc labelled
- QA: holds: IBM records the two tables ran under compared per untouched qubit (T1 103/115, T2 110/115, readout error 115/117, readout length 0/117); no cause named
- QB: holds: arms interleaved in one job, equal scheduled durations 6057 dt in the dry run
- QC: holds: known-good PASS (-1.474, 0.62 of the committed kick, inside the 0.5x-2x window); shot-noise scale printed (0.17, 0.19); synthetic resolution unchanged
- QD: holds: copies agree (both CANNOT_TELL) so FINAL takes the pooled label by the rule; copy gap -0.000 [-0.127, +0.114] reported; one chip, no combined claim
- QE: holds: no mechanism named; every second ruler labelled defined after the data (Addendum 3, readings_compare)
- QF: fixed: code change public 57 s before the first job (ae912152 11:58:19Z, job C 11:59:16Z); Addendum 3 after the fire, said on the page; run repo commit of the second-fire files made with this entry
- QG: fixed: outside referee (same model family as the writer) read the raw files; every flag acted on: lean wording, post-hoc placement, either-direction wording, 0.24 not 0.25, IBM record sentence, first-fire paragraph rescoped, kingston not yet read, provenance sentence
- P1: n/a: the page quotes no one
- P2: holds: each figure names its fire and the files link from the page
- P3: holds: 21 October table called the ten-day table as elsewhere on the page, 31 October table and fresh table as the plan names them
- P4: holds: no cause named for the shrinking kick or the IBM record changes
- P5: holds: bands are 99 % bootstrap over qubits as the page says above the table; the sign test says exact two-sided and not at 99 %
- P6: fixed: below by the rule with the upper end on zero and below in 3 of 20 other seeds, printed as a lean
- P7: holds: ledger rows added before the surface edit, ship.sh only, verified live after the ship
- P8: cannot tell: checked in the rendered page after the ship
- P9: holds: no AI statement, no count of our things in headings, plain sentences, no semicolons
- P10: holds: Addendum 3 and readings_compare lines labelled defined after the data on the page
