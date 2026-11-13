
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

## 2026-11-01 08:20 Darkwave clock second fire, ibm_kingston 1 Nov, after the referee: clock cannot tell by the plan (copy labels differ), pooled inside the margin; ten-day table below by the plan with upper end on zero; plan note corrected; Addendum 4
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same arms in one job, same 117 qubits; nothing dropped; the fresh table finished 5 s before copy A after a 57 min queue wait, same IBM record before C, A, B and after
- II: caught: the plan note said no first-fire label changed at 20,000 draws; my diff had cut the labels; kingston fire 1 R2 CONSISTENT -> CANNOT_TELL; now corrected in the plan and on the page
- III: holds: ten-day table signed residual -0.08 [-0.21, +0.15] printed with its band through zero; no over-correction claimed
- V: holds: plan FINAL at seed 31 beside the pooled seed spread (Addendum 3) and the plan rule per seed (Addendum 4); they disagree for R3 (15 vs 8 of 20 below), so it is printed as a lean
- VI: fixed: R2 cannot tell (copy B past the margin by 0.0005); R3 and R4 below with the upper end on zero, printed with their per-seed counts, not as a change
- R: holds: numbers from results_clock.text, readings_second.text (Addenda 3, 4) and readings_compare.text; job times from job_clock.json timestamps; record stamps from props files
- QA: holds: IBM records the two tables ran under compared per untouched qubit (T1 113/116, T2 115/116, readout error 115/117, length 0/117); latest record 2 h 20 min before copy A
- QB: holds: arms interleaved, equal scheduled durations 4921 dt in the dry run
- QC: holds: known-good PASS -2.912 [-4.205, -1.903], 1.02 of the committed kick
- QD: fixed: copy labels differ for R2 so FINAL is cannot tell; copy bands at the plan draw printed; copy gap +0.031 [-0.034, +0.078] printed
- QE: holds: no mechanism named; Addendum 3 shown as fixed before this fire data; Addendum 4 lines labelled after the data
- QF: fixed: provenance sentence per chip (56 s and 57 s), Addendum 3 time 12:08:49Z (public 292a5e21), job C queue wait from the record; the plan correction dated
- QG: fixed: outside referee (same model family as the writer) read the raw files; all nine flags acted on: R3/R4 plan labels, -0.0505, first-fire wording, post-hoc labels both ways, provenance, over-correction wording, symmetric sizes and floors, copy gap, timing line
- P1: n/a: the page quotes no one, nothing to check verbatim
- P2: holds: every figure names its fire and file
- P3: holds: arms named as the plan names them
- P4: holds: no cause named for the queue wait or record changes
- P5: holds: 99 % bootstrap over qubits as stated above the table; sign test labelled exact two-sided
- P6: fixed: ten-day differences printed as below with the upper end on zero and per-seed counts, never as ageing
- P7: holds: ledger rows before the surface ships; ship.sh only; verified live
- P8: cannot tell: rendered page checked after the ship
- P9: holds: no AI statement, plain sentences, no semicolons in the section
- P10: holds: Addendum 4 lines and the copy bands labelled defined after the data

## 2026-11-02 09:35 Darkwave clock daily fires 2 Nov (kingston 1205, marrakesh 1206): FINAL and second rulers read in full
packs: Q
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same plan, code and arms as the 1 Nov fires (PLAN_CLOCK, Addenda 3 and 4 public before these fires); today table C ran 4 s before copy A
- II: holds: copies A and B read side by side, per-qubit sign counts printed (kingston 64 vs 53, marrakesh 69 vs 48), not netted
- III: holds: signed median residuals printed per arm; marrakesh MC +0.971 deg/readout (puts back more than taken) against M31 and MT near zero
- V: holds: share given back with 99 % qubit bootstrap, copy gap, 20-seed label stability and the exact sign test side by side
- VI: holds: four outcomes per reading; the 31 Oct table vs today stays CANNOT_TELL on both chips (20 of 20 seeds)
- R: holds: times, table ages and job windows from job_clock.json and results files; both known-good checks PASS
- QA: holds: no stated IBM figure compared; tables are our own measurements
- QB: holds: arms inside one job per copy, same 117 untouched qubits, same readout count
- QC: holds: known-good signed kick resolved on both chips (-2.666 and -1.973 deg/readout, 99 %)
- QD: holds: copies compared by their gap with a width (does not resolve on either chip); chips read separately, never pooled
- QE: holds: no mechanism named; the reading is how much of the kick each table puts back
- QF: holds: plan and addenda pushed before these jobs (Addendum 3 at 12:08:49 UTC 1 Nov)
- QG: n/a: read in full here; a referee pass goes with the public post

## 2026-11-03 11:46 Darkwave clock fire 4 (3 Nov, kingston 12:45, marrakesh 12:12): FINAL and second rulers read in full, refereed
packs: Q
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same plan, code and arms as fires 1 to 3; fresh table C ran 4 to 8 s before copy A
- II: holds: per-qubit sign counts printed (kingston 60 vs 57, marrakesh 66 vs 51), copies read side by side
- III: holds: signed residuals per arm printed; kingston leans positive in all three, one band includes zero, said so
- V: holds: 99 % qubit bootstrap, copy gap, 20-seed label stability and exact sign test side by side
- VI: holds: four outcomes; 31 Oct table vs today cannot tell on both chips in 20 of 20 seeds
- R: holds: ages, times and values from results_clock.text, readings_second.text and line (g); referee checked every number
- QA: holds: no IBM stated figure compared
- QB: holds: arms inside one job per copy, same 117 untouched qubits
- QC: holds: known-good kick resolved on both chips
- QD: holds: copies by their gap with a width; chips never pooled
- QE: holds: no mechanism named
- QF: holds: plan and Addenda 3 and 4 public before this fire
- QG: holds: referee pass done before the public post, every flag acted on

## 2026-11-06 19:54 Darkwave clock fires 5 to 7 (4 Nov kingston 13:52 marrakesh 13:39, 5 Nov kingston 13:42 marrakesh 12:33, 6 Nov kingston 17:51 marrakesh 17:48): FINAL and second rulers read in full, refereed
packs: Q, P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same plan, code and arms as fires 1 to 4; FINAL rule (pooled if the copies agree) is in PLAN_CLOCK, committed 31 Oct before any fire
- II: holds: per-qubit sign counts printed for every fire, copies read side by side, no netting across fires
- III: holds: signed residuals per arm; marrakesh ten-day table +0.88, +1.02, +0.90 deg/readout (puts back more than taken), kingston +0.15 with band through zero, said so
- V: holds: 99 % qubit bootstrap, copy gap, 20-seed label stability, the plan's rule per seed, exact sign test side by side
- VI: holds: four outcomes; 31 Oct table vs today cannot tell on both chips at all three fires, 20 of 20 seeds
- R: caught: draft called the 6 Nov kingston ten-day BELOW the first on kingston; the 1 Nov fire read BELOW (-0.028 [-0.064, -0.000]); fixed to "below again as at the 1 November fire" (tp_score row logged)
- QA: holds: no IBM stated figure compared
- QB: holds: arms inside one job per copy, same 117 untouched qubits
- QC: holds: known-good kick resolved on both chips at all three fires
- QD: holds: copies by their gap with a width; chips never pooled; kingston 6 Nov BELOW printed with each copy's own CANNOT_TELL band
- QE: holds: no mechanism named
- QF: holds: plan and Addenda 3 and 4 public 1 Nov, before these fires
- QG: holds: read-only referee checked every new number against results_clock.text, readings_second.text and job_clock.json; one flag, acted on
- P1: holds: no quotation in the new text
- P2: holds: every figure from the day folders named above
- P3: holds: setting labels (31 October table, ten-day table measured 21 October, fresh table) match results_clock.text arm names M31, MC, MT
- P4: holds: no cause named for any difference
- P5: holds: 99 % bootstrap bands, as stated above the table
- P6: holds: kingston 5 Nov sign test p = 0.001 printed beside the share difference that could not tell and the counts the days before and after; one point, no rate
- P7: holds: ledger rows before the surface ships; ship.sh only; verified live after
- P8: cannot tell: rendered page checked after the ship
- P9: holds: no AI statement, plain sentences, no semicolons in the new text
- P10: holds: no reading in the new text was defined after the data; Addenda 3 and 4 were public 1 Nov before these fires

## 2026-11-06 19:57 Darkwave page /tp pass on fires 5 to 7: two lines narrowed after the ship
packs: Q, P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no comparison changed, only how two readings are worded
- II: caught: the 5 Nov kingston sign test (p = 0.0008) was printed as the first at the 99 % level without the 12 counts on file; chance any of 12 is this low under no change 0.0096, now printed (signtest_family_20261107.text)
- III: holds: signs unchanged
- V: holds: share difference and sign test still printed side by side
- VI: caught: kingston 6 Nov ten-day BELOW printed without saying the size against the 0.05 margin cannot be told (band 0.01 to 0.10); now said
- R: holds: counts read from readings_second.text line (b) on every day folder
- QA: holds: no IBM figure
- QB: holds: arms inside one job per copy, same 117 untouched qubits, no arm changed by this pass
- QC: holds: known-good kick resolved on both chips at all three fires, as read before
- QD: holds: copies still printed with their own bands, chips never pooled, the family count spans both chips as counts only
- QE: holds: no mechanism named
- QF: holds: the family count is labelled defined after the data
- QG: holds: both flags are self-caught on the /tp pass; tp_score rows logged
- P1: holds: no quotation
- P2: holds: the new figures live in signtest_family_20261107.text
- P3: holds: labels unchanged
- P4: holds: no cause named
- P5: holds: 99 % level named
- P6: holds: the summary is weaker than before, not stronger
- P7: holds: ledger row before ship, ship.sh only, verify live after
- P8: cannot tell: rendered page checked after the ship
- P9: holds: no semicolons, plain sentences
- P10: holds: family count labelled defined after the data

## 2026-11-07 15:10 Darkwave clock fire 8 (7 Nov, marrakesh job A 12:26, kingston job A 13:27): FINAL and second rulers read in full, refereed
packs: Q, P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same plan, code and arms as fires 1 to 7; FINAL rule (pooled if the copies agree) in PLAN_CLOCK, committed 31 Oct; kingston read by analyze_clock.py and post_clock.py, the rider's own code, run by hand at ~14:55Z because the rider had not reached it
- II: holds: per-qubit sign counts printed for both chips (kingston 67 vs 50 p 0.139, marrakesh 71 vs 46 p 0.026); family rebuilt to 14 counts from readings_second.text line (b), smallest p 0.0008, chance any of 14 this low 0.0111 (signtest_family_20261107b.text)
- III: holds: signed residuals per arm; marrakesh ten-day +1.031 [+0.561, +1.550] deg/readout, kingston ten-day +0.168 [+0.038, +0.305]
- V: holds: 99 % qubit bootstrap, copy gap, 20-seed label stability, the plan's rule per seed, exact sign test side by side
- VI: caught: kingston ten-day vs 31 Oct table reads CONSISTENT by the plan (copies both cannot tell, pooled -0.014 [-0.050, +0.016]) but only 4 of 20 seeds agree and the lower end sits on the margin: printed as one point with the seed count, never as "the same"; kingston 31 Oct vs fresh pooled band inside the margin in 17 of 20 seeds but the copies' labels differ (A BELOW, B CANNOT_TELL), so cannot tell by the plan in 20 of 20
- R: holds: every figure read from results_clock.text and readings_second.text of day_20261107_1258_ibm_kingston and day_20261107_1223_ibm_marrakesh; ages from the "Table ages at job A" lines (161.3 h, 162.3 h)
- QA: holds: no IBM stated figure compared
- QB: holds: arms inside one job per copy, same 117 untouched qubits
- QC: holds: known-good kick resolved on both chips (kingston -2.729 [-3.925, -1.718], marrakesh -1.697 [-2.191, -1.094])
- QD: holds: copies by their gap with a width; chips never pooled
- QE: holds: no mechanism named
- QF: holds: plan and Addenda 3 and 4 public 1 Nov, before this fire
- QG: caught: read-only referee checked every new number against the day folders; one flag: "the first consistent reading on either chip" was false (kingston MC minus M31 was FINAL CONSISTENT on 4 Nov, kingston M31 minus MT on 31 Oct); clause cut before the ship
- P1: holds: no quotation in the new text
- P2: holds: every figure from the day folders named above
- P3: holds: arm labels (31 October table, ten-day table measured 21 October, fresh table) match M31, MC, MT
- P4: holds: no cause named
- P5: holds: 99 % bootstrap bands, as stated above the table
- P6: holds: one fire per chip, no rate claimed; the CONSISTENT is one point with its seed count
- P7: holds: ledger rows before the surface ships; ship.sh only; verified live after
- P8: cannot tell: rendered page checked after the ship
- P9: holds: no AI statement, plain sentences, no semicolons in the new text
- P10: holds: the sign-test family figure is labelled defined after the data
- note: this entry's header time 15:10 is wrong; written ~14:50Z by the clock (date -u). Fixed in the READ files and night log.

## 2026-11-07 15:05 Darkwave fire 8 page wording, Sage's ruling (keep FINAL, show the step): kingston CONSISTENT explained, unrounded bound, inversion disclosed
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no rule changed; FINAL kept at the plan's draw (Sage: switching to seed majority now would pick a rule after the number)
- II: holds: both kingston comparisons printed with their seed counts side by side (17 of 20 and 4 of 20)
- III: holds: signs unchanged
- V: fixed: unrounded pooled band REPRODUCED (not read from the original run) with analyze_clock.py's own code, same rng seed 31: -0.01413 [-0.04982, +0.01575]; saved to day_20261107_1258_ibm_kingston/unrounded_bands.text; matches results_clock.text to 3 decimals
- VI: fixed: CONSISTENT now says how it arose (each copy cannot tell, pooled when labels agree) and what it means (this fire cannot separate the tables, not the same table); inversion against the 31 Oct vs fresh reading disclosed, not fixed
- R: holds: every figure from results_clock.text, readings_second.text and unrounded_bands.text
- P1: holds: no quotation
- P2: holds: unrounded figure names its file
- P3: holds: arm labels unchanged
- P4: holds: no cause named
- P5: holds: 99 % bootstrap band
- P6: holds: one point, no rate
- P7: holds: ledger first, ship.sh, verified live
- P8: cannot tell: rendered page checked after the ship
- P9: holds: plain sentences, no semicolons
- P10: holds: the 1 in 90 family figure stays labelled defined after the data
- precedent (Sage's question): clock.py final() (committed 1 Nov 07:30, from the keystone run) sets FINAL = pooled when a == b, so two CANNOT_TELLs agree by code; day_20261104_1345_ibm_kingston MC minus M31 went CT+CT -> FINAL CONSISTENT, and one earlier fire went CT+CT -> FINAL BELOW. Not applied here for the first time.
- Sage VERDICT 15:04Z STANDS. Her DIG reproduced -0.014126 [-0.049819, +0.015749] from the raw npz; seeds 1, 10, 12, 15 CONSISTENT (lower ends -0.04999, -0.04930, -0.04995, -0.04950), 16 CANNOT_TELL, every seed CT+CT; the lower bound is within 0.001 of -0.05 in every seed (seeds 6 and 20 miss by under 0.0002). So the 4-of-20 split is resampling noise at the margin, not a tendency toward CONSISTENT; the page stays as is.
- Comparison, said once: the 4 Nov kingston MC minus M31 CONSISTENT, +0.002 [-0.030, +0.034], sat well inside +/-0.05 and was the sturdier reading; fire 8's sits on the margin. "First consistent" appears nowhere on the live page (checked 15:06Z); it survives only in this file as the logged catch.

## 2026-11-09 21:20 Darkwave clock fires 9 and 10 (8 Nov marrakesh job A 12:44, kingston 13:29; 9 Nov marrakesh 20:23, kingston 20:50): FINAL and second rulers read in full, refereed
packs: Q, P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same plan, code and arms as fires 1 to 8; FINAL rule (pooled only if the copies' labels agree) from PLAN_CLOCK, committed 31 Oct; all four chip-fires read by analyze_clock.py and post_clock.py through clock_daily.py (9 Nov kingston read by the rider pass run at ~20:53Z after its copy B finished)
- II: holds: per-qubit sign counts printed for all four (8 Nov kingston 67 vs 50 p 0.139, marrakesh 65 vs 52 p 0.267; 9 Nov kingston 62 vs 55 p 0.579, marrakesh 59 vs 58 p 1.000); family rebuilt to 18 from readings_second.text line (b), smallest p 0.0008, chance any of 18 this low 0.0143, about 1 in 70 (signtest_family_20261109.text)
- III: holds: signed residuals per arm; marrakesh ten-day +0.755 [+0.557, +1.286] and +1.028 [+0.509, +1.498] deg/readout, kingston ten-day +0.138 [+0.026, +0.309] and +0.094 [-0.070, +0.242]
- V: holds: 99 % qubit bootstrap, copy gap (none resolves), 20-seed label stability, the plan's rule per seed, exact sign test side by side
- VI: caught: 9 Nov kingston M31 minus MT: both copies CANNOT_TELL so pooled is read, -0.012 [-0.050, +0.027], unrounded lower end -0.05026 (unrounded_bands.text), CANNOT_TELL at the plan's draw, CONSISTENT in 7 of 20 seeds by the plan's rule: printed as one point, never as consistent; 8 Nov kingston MC minus M31 pooled -0.004 [-0.049, +0.049] inside the margin in 20 of 20 seeds but copies A CONSISTENT / B CANNOT_TELL, so CANNOT_TELL by the plan in 20 of 20, printed that way; no outcome folded
- R: holds: every figure read from results_clock.text, readings_second.text, unrounded_bands.text of day_20261108_1230_ibm_marrakesh, day_20261108_1303_ibm_kingston, day_20261109_2022_ibm_marrakesh, day_20261109_2047_ibm_kingston; ages from "Table ages at job A" (185.6, 186.4, 217.3, 217.7 h); fire times from job A submitted_utc in job_clock.json
- QA: holds: no IBM stated figure compared
- QB: holds: arms inside one job per copy, same 117 untouched qubits
- QC: holds: known-good PASS on all four (8 Nov kingston -2.784 [-3.909, -1.709], marrakesh -1.655 [-2.074, -0.952]; 9 Nov kingston -2.839 [-3.846, -1.767], marrakesh -1.471 [-1.953, -1.122])
- QD: holds: copies by their gap with a width; chips never pooled
- QE: holds: no mechanism named; the unrounded lower end is labelled recomputed after the data
- QF: holds: plan and Addenda 3 and 4 public 1 Nov, before these fires; 8 Nov kingston copies ran 27 min apart (copy A 7 min after job C), stated on the page
- QG: caught: read-only referee checked every new number, label, seed count, age, time and the family arithmetic against the day folders; one flag: the 0.0003 past the margin figure comes from a file written after the data and was unlabelled; label added before the ship. No other flags
- P1: holds: no quotation in the new text
- P2: holds: every figure from the day folders named above
- P3: holds: arm labels (31 October table, ten-day table, fresh table) match M31, MC, MT
- P4: holds: no cause named
- P5: holds: 99 % bootstrap bands, as stated above the table
- P6: holds: each fire one point, no rate claimed
- P7: holds: ledger rows before the surface ships; ship.sh only; verified live after
- P8: cannot tell: rendered page checked after the ship
- P9: holds: no AI statement, plain sentences, no semicolons in the new text, no count in a heading
- P10: holds: the sign-test family figure and the unrounded bound are labelled after the data
