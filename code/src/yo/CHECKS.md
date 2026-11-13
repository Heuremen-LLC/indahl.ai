
## 2026-10-31 18:51 YO v2 test reading: Job A 0.957, Job C 0.950, forced-verdict 0.060; ABOVE every null under the plan rule
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every null was scored on the same 800 TEST items before the first training step (nulls committed in the yo repo before training); no item dropped (0 unparsed Job A, 0 unreadable Job C)
- II: holds: per-item scores paired item by item and bootstrapped over records; the Job C confusion table is printed, so the 6 CANNOT_TELL truths given a verdict and the 10 CONSISTENT truths read CANNOT_TELL are visible
- III: holds: differences are signed YO minus null; every one is positive
- V: holds: the plan's mean score with a paired record bootstrap, beside the forced-verdict rate and the full confusion table
- VI: holds: every band sits above 0 by more than 0.15; four outcomes applied as the plan wrote them
- R: holds: numbers from yo2_results.text, written by the committed yo2_eval.py and yo2_compare.py
- L1: holds: 10 replies per job read in full before any rate (all clean JSON or one label; the scorer reads them right)
- L2: holds: liveness read from progress lines only; the rate printed after the replies were read
- L3: holds: one chat template, thinking off, greedy, the same max tokens for the base model and YO
- L4: n/a: one machine, one run; no across-machine claim
- L5: n/a: our own items; answers computed by code from IBM's records
- L6: holds: base Job A unparsed 288 of 400 counted by reason (invalid JSON) and shown with a lenient second reading labelled after the data
- L7: holds: no labeller; the truth is the code's rule, exact (oracle 1.000)
- L8: caught: one training run with one seed, so there is no seed width; said on the page
- L9: holds: by design the prompt states the rule and the record, and the answer follows from them; the code does it exactly, so the reading is that a small model learns the rule, not that it beats the code
- L10: holds: adapter adapters/v2/adapters.safetensors hashed with the run
- L11: n/a: IBM history pulled once for this run (pull_history2.py), hashed into DATA_YO_V2.sha256
- L12: holds: the referee that reads this is the same model family as the writer, and the page will not claim otherwise
- P1: n/a: the page and this entry quote no one, so there is nothing to check verbatim
- P2: holds: every figure on the page names the test set (last month of records) and yo2_results.text
- P3: holds: job names as in the plan
- P4: holds: no cause named
- P5: holds: bands are 95 % paired bootstrap over test records, as the plan says
- P6: fixed: the one-liner says a small model learned to apply the rule, with the code doing it exactly beside it
- P7: holds: ledger rows go in before the surface ships
- P8: cannot tell: checked in the browser after the ship
- P9: holds: no AI-assistance statement, plain sentences, no count of our things in the heading
- P10: holds: the lenient base reading is labelled defined after the data

## 2026-10-31 19:00 YO v2 after the referee (defined after the data): stale recall 0.496 precision 0.927, mostly 2+ calendar days; zeros+2-calendar-day code rule 0.929 vs YO 0.957
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same 400 TEST items, no item dropped
- II: caught: the item mean (0.957) hid that YO finds half the stale qubits; counted qubit by qubit and by gap band
- III: holds: misses and false flags counted apart (231 missed, 18 false)
- V: caught: the plan's flag-nothing ruler was too weak; two code rules written after the data put beside it (0.829, 0.929)
- VI: holds: YO is above every planned baseline; against the after-the-data date rule the gap is 0.028, reported as a gap, not a verdict
- R: holds: numbers printed by posthoc_yo_v2.py from the committed eval files; matches the referee's recount
- L1: holds: replies read before; the stale misses are real answers (valid JSON with fewer qubits), not parser losses
- L2: holds
- L3: holds: same setup as the test reading
- L4: n/a: one machine
- L5: n/a: our own items
- L6: holds: no reply dropped
- L7: holds: truth from code
- L8: holds: one run, one seed, said on the page
- L9: holds: the page says the code does the job exactly and where YO falls short of it
- L10: holds: same adapter hash
- L11: n/a
- L12: holds: the referee is the same model family as the writer
- P1: n/a: the page quotes no one, so there is nothing to check verbatim
- P2: holds: figures name the test set and the files
- P3: holds
- P4: holds: no cause named for the shortcut
- P5: holds: bands are 95 % over test records
- P6: fixed: 'learned the rule' withdrawn; the one-liner says it finds half the stale qubits and a date rule comes within 0.03
- P7: holds: ledger rows before the surface
- P8: cannot tell: checked after the ship
- P9: holds
- P10: holds: every after-the-data reading labelled

## 2026-10-31 19:46 YO v3 on TEST3: plan rule says v3 does not refine YO; YO v2 stays the working model
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: flag-nothing, the date rule and YO v2 were scored on TEST3 and committed (e5ba486, 19:07:15 EDT) before the first v3 training step; TEST3 comes from records no v2 TEST item used; the readability gate dropped 0 of 800 replies for each model
- II: holds: flips counted before any net. Band stale qubits: 44 caught by v3 only, 14 by v2 only, from 11 records against 2 (37 of the 44 sit in 5 records where every qubit was stale). Job A items: v3 higher on 19, v2 higher on 5, 376 equal. Job C items: v3 right and v2 wrong on 9, the reverse on 14. No repeat floor measured (one scoring pass per model, greedy decoding)
- III: holds: signs differ across readings and are printed signed. Band recall +0.083, Job A +0.008, Job C -0.013. v3's Job C misses move toward CANNOT_TELL (17 CONSISTENT items read CANNOT_TELL against 10 for v2), and its forced-verdict rate is 0.000 against 0.020
- V: caught: two rulers disagree on the band. The planned ruler (paired bootstrap over records, 2,000 resamples, seed 31, 95 %) gives +0.083 [-0.021, +0.190]. The exact test on discordant qubits gives 44 against 14, p 0.0001, but it treats qubits as independent and they cluster by record. Counting records (defined after the data): 11 against 2. The disagreement is the clustering, and the planned ruler decides
- VI: holds: band [-0.021, +0.190] reaches both zero and +0.19, CANNOT_TELL. Job C [-0.036, +0.010] reaches past the -0.02 margin, CANNOT_TELL. Job A +0.008 [+0.001, +0.015] ABOVE. v3 minus the date rule on Job A +0.039 [+0.024, +0.055] ABOVE. The rule needs the band ABOVE, so v3 does not refine YO and v2 stays the working model; the rule is not relaxed after the result
- R: caught: the plan header says written about 19:45 EDT, but git records the plan commit d70fcbe at 19:00:54 EDT, before any v3 data; a dated note in the plan corrects it. Counts read from eval3_yo_v3.jsonl, eval3_yo_v2.jsonl and yo3_results.text. Record-count readings are labelled defined after the data
- L1: holds: 10 v3 replies per job read in full with their parsed values, all clean JSON or a clean label; v2's parser on the same scorer was read for v2; 800 of 800 replies parse for each model
- L2: holds: yo3_compare.py wrote to yo3_results.text unopened until the parser read and the drop count were done; the run log tail was not read
- L3: holds: same base, prompt format, chat template, extraction (yo3_eval.py) and max tokens (200 Job A, 8 Job C) for both models
- L4: cannot tell: one machine (the Mac, mlx-lm 0.31.3), greedy decoding, one scoring pass per model; no repeat run, so no measured repeat floor
- L5: n/a: our own items, built by code from IBM records
- L6: holds: unread replies counted per model: 0 of 800 for v3, 0 of 800 for v2
- L7: holds: truth computed by code from the records, not by any model
- L8: cannot tell: paired over records, but one training seed (33) for v3, so the seed width is unknown; said with the result
- L9: holds: the prompt carries the record lines and stamp; the answer is computed by code and is not in the prompt
- L10: holds: v2 scored with adapter sha256 f73c847be9f51dd5, v3 with c9f9d6c6f27d0d8d
- L11: n/a: no dataset or tool substituted
- L12: holds: the referee on this reading will be a Claude model, the same family as the writer; this line discloses it

## 2026-10-31 19:58 YO v3 readings after the referee: nulls, items with something to flag, band split by item, CANNOT_TELL use, zero flags (defined after the data except the nulls)
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the nulls (flag nothing, the date rule) were scored before v3 trained (e5ba486); the split by item is conditioned on the truth, not on any model's output; no reply dropped for any model
- II: holds: the band split counts qubits per item class (240 in items where all 8 are band-stale, 120 in the rest) before any net; CANNOT_TELL answers counted item by item (v2: 98 right and 11 wrong, not the net 9)
- III: holds: both split differences are positive (+0.042, +0.167), printed signed
- V: holds: the split uses the plan's ruler (paired bootstrap over records, 2,000 resamples, seed 31, 95 %); recount by our own code agrees with the referee's independent code on every count
- VI: holds: all-8 items +0.042 [-0.101, +0.181] CANNOT_TELL; other items +0.167 [+0.043, +0.312] ABOVE, defined after the data
- R: fixed: the plan note now gives git times only; counts read from eval3_*.jsonl and data3/test_items.jsonl
- L1: holds: parser read in the previous entry; 0 unparsed per model
- L2: holds: these readings were computed after the referee, labelled defined after the data
- L3: holds: same scorer for every system
- L4: cannot tell: one scoring pass per model, greedy decoding, no repeat floor
- L5: n/a: our own items
- L6: holds: 0 unread of 800 per model
- L7: holds: truth by code
- L8: cannot tell: one training seed for v3
- L9: holds: answer not in the prompt
- L10: holds: adapter hashes as the previous entry
- L11: n/a: nothing substituted
- L12: holds: the referee was a Claude model, the same family as the writer
- P1: n/a: the readings quote no one, so there is nothing to check verbatim
- P2: holds: each figure names TEST3 and the file
- P3: holds: labels as the files
- P4: holds: no cause named for the split or the CANNOT_TELL use
- P5: holds: intervals are 95 % over test records
- P6: fixed: Job A v3 minus v2 printed as above zero but inside the 0.02 margin, not as a gain that holds
- P7: holds: ledger rows before the surface
- P8: cannot tell: checked after the ship
- P9: holds: no AI statements, no counts in headings
- P10: holds: every after-the-data reading labelled

## 2026-10-31 20:01 YO result table posted on /iris/lab (v2 rows as refereed, v3 rows after the referee's wording fixes)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every comparison in the table was planned and scored before training, or is labelled defined after the data
- II: holds: item and qubit counts are printed beside the nets (360 band qubits, 118 and 109 CANNOT_TELL answers with 18 and 11 wrong, 190 of 400 empty audit items)
- III: holds: differences printed signed, with the Unicode minus for negatives
- V: holds: every interval is the planned paired bootstrap over records, 95 %, named in the table head and the panel note
- VI: holds: outcomes printed as above or cannot tell; the Job A above is marked inside the 0.02 margin
- R: holds: every figure copied from yo2_results.text, yo3_results.text and readings_after_referee.text, each with a ledger row (yo.v2.*, yo.v3.*)
- P1: n/a: the table quotes no one, so there is nothing to check verbatim
- P2: holds: rows name the test set (held-out month, second held-out set) and the files sit in code/yo
- P3: holds: labels match the files (record audit, four-outcome verdict, band 24 to 48 hours)
- P4: holds: no cause named for the split, the CANNOT_TELL use or the shortcut
- P5: holds: the head says 95 % band over test records
- P6: holds: the one-liner says v3 found more but the planned interval reaches zero, no stronger than the reading
- P7: holds: ledger rows added before the ship, live drift 0
- P8: cannot tell: rendered page checked after this entry
- P9: holds: no AI statements, no counts of our things in the heading, plain sentences without semicolons
- P10: holds: every after-the-data row starts with Defined after the data

## 2026-10-31 21:04 YO v4 on TEST4: plan rule says YO v4 replaces YO v2 as the model at work
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: flag nothing, the date rule, flag every qubit, YO v2 and YO v3 were all scored on TEST4 and committed (c4cd881, 20:16:02 EDT) before the first v4 training step; TEST4 comes from 486 records no v2 TEST or TEST3 item used; 0 of 790 replies dropped for any model
- II: holds: qubit-level counts by gap band read before any net (yo4_posthoc.text): v4 flags 0 of 276 qubits at 23-24 h and 110 of 118 at 24-25 h; flags on qubits under 24 h: v4 2, v2 17. Wrong CANNOT_TELL answers counted item by item: v4 4, v3 25, v2 14. No repeat floor measured (one scoring pass per model, greedy decoding)
- III: holds: every v4 minus v2 difference is positive and printed signed (R1 +0.541, R2 +0.030, R3 +0.029, R4 +0.032); v4 minus v3 positive on R1 and R2
- V: holds: the planned ruler (paired bootstrap over TEST4 records, 2,000 resamples, seed 41, 95 %) and, beside it, the gap-band table defined after the data; both say v4 flags stale qubits at the 24 h line and not below it. The flag-every-qubit null scores R1 1.000 with precision 0.376, so R1 is read only beside R3
- VI: holds: R1 +0.541 [+0.454, +0.630] ABOVE; R2 +0.030 [+0.013, +0.048] ABOVE; R3 +0.029 [+0.001, +0.069] ABOVE (lower end near zero, the rule needs only not BELOW); R4 +0.032 [+0.010, +0.055] ABOVE. Rule met: R1 ABOVE and R2, R3, R4 not BELOW
- R: holds: times from git (plan 8c5a448 20:05:55, code fa7bfad 20:07:08, nulls and v2/v3 c4cd881 20:16:02); counts from eval4_*.jsonl; TEST4 holds 190 whole-window items (the plan said up to 200), 200 general items and 400 verdict items
- L1: holds: 5 whole-window, 5 general and 10 verdict replies of v4 read in full with their parsed values, all clean; 790 of 790 replies parse for each of v4, v3 and v2
- L2: holds: yo4_compare.py wrote to yo4_results.text unopened until the reply read and the drop count were done
- L3: holds: same base, prompt format, chat template, extraction (yo4_eval.py) and max tokens for every model
- L4: cannot tell: one machine (the Mac, mlx-lm 0.31.3), greedy decoding, one scoring pass per model, no repeat run
- L5: n/a: our own items, built by code from IBM records
- L6: holds: unread replies counted per model: 0 of 790 for v4, v3 and v2
- L7: holds: truth computed by code from the records
- L8: cannot tell: paired over records, one training seed (44) for v4, so its seed width is unknown
- L9: holds: the prompt carries the record lines and stamp; the answer is computed by code and is not in the prompt
- L10: holds: v2 adapter sha256 f73c847be9f51dd5, v3 c9f9d6c6f27d0d8d, v4 hash recorded in the commit
- L11: n/a: no dataset or tool substituted
- L12: holds: the referee on this reading is a Claude model, the same family as the writer; this line discloses it

## 2026-10-31 21:18 YO v4 readings after the referee: item-level all-stale, live-mix recall, backend split, zeros, Job C flips, the live pittsburgh record re-read, corrections (426 records, 1 false flag)
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every reading here is defined after the data and labelled so; the comparisons reuse the committed eval files and the committed scorer; no reply dropped
- II: holds: counted item by item before any net: all-8-stale items exactly right v4 130, v3 94, v2 53 of 136 (v4 flags nothing on 3); live-mix stale qubits found v4 193, v3 136, v2 119 of 215; Job C flips 17 for v4 and 4 against
- III: holds: every v4 minus v2 count is in v4's favour except zeros (v4 found 115 of 119 with 4 false, v2 116 with 9 false, v3 116 with 0 false), printed as counts
- V: holds: counts beside the planned bootstrap; the referee's own code and ours agree on every count
- VI: fixed: R3 (precision) is no longer read as ABOVE in public: it reads CANNOT_TELL under day-level clustering, printed as 0.999 against 0.970. Job C reads not worse, not improved by the design
- R: fixed: TEST4 items come from 426 distinct records within the 486 unused; under 24 h v4 has 1 false flag plus 1 correct flag at exactly 24 h 00 min (stamp seconds hidden in the prompt)
- L1: holds: replies read in the previous entry; the pittsburgh re-read output read in full
- L2: holds: readings computed after the referee, labelled defined after the data
- L3: holds: same scorer and extraction for every model; the pittsburgh re-read uses release/yo_audit.py, whose prompts match training byte for byte (20 of 20)
- L4: cannot tell: one scoring pass per model, greedy decoding, no repeat floor
- L5: n/a: our own items, built by code from IBM records
- L6: holds: 0 unread of 790 per model; the pittsburgh re-read had 0 unreadable replies
- L7: holds: truth by code
- L8: cannot tell: one training seed per adapter and no replay-only control, said with the result
- L9: holds: answer not in the prompt
- L10: holds: adapter hashes as committed (v4 4737100d6e008afa)
- L11: n/a: nothing substituted
- L12: holds: the referee was a Claude model, the same family as the writer
- P1: n/a: the readings quote no one, so there is nothing to check verbatim
- P2: holds: each figure names TEST4 or the live record and its file
- P3: holds: labels match the files (whole-window, general items, verdicts)
- P4: holds: no cause named for the backend split, the misses or the Job C change
- P5: holds: intervals are 95 % over test records
- P6: fixed: the one-liner says v4 finds about nine in ten stale qubits on the everyday mix, not the 0.975 headline alone
- P7: holds: ledger rows before the surface
- P8: cannot tell: rendered page checked after this entry
- P9: holds: no AI statements, plain sentences
- P10: holds: every after-the-data reading labelled

## 2026-10-31 21:20 YO v4 table rows posted on /iris/lab and the live reader switched to adapters/v4
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every row is either a planned reading (scored before v4 trained) or labelled defined after the data
- II: holds: counts printed beside every rate (905 of 928, 403 of 928, 130 of 136, 193 of 215, 1,127 of 1,128, 390 of 400)
- III: holds: differences printed signed
- V: holds: intervals are the planned paired bootstrap over records, 95 %, named in the table head
- VI: holds: verdicts printed as above, higher or not worse in the referee's wording; precision printed as counts without an outcome label
- R: holds: every figure from yo4_results.text and yo4_after_referee.text; ledger rows yo.v4.livemix, yo.v4.all8, yo.v2.all8, yo.v4.r1; v2 one-liner rows taken off iris_lab with a reason
- P1: n/a: the table quotes no one, so there is nothing to check verbatim
- P2: holds: rows name TEST4, the everyday mix and the live record
- P3: holds: labels match the files
- P4: holds: no cause named for the misses, the backend split or the verdict change
- P5: holds: the head says 95 % band over test records
- P6: holds: the one-liner leads with the everyday mix (193 of 215), not the 0.975 headline alone
- P7: holds: ledger rows added before the ship, live drift 0
- P8: cannot tell: rendered page checked after this entry
- P9: holds: no AI statements, plain sentences, no counts of our things in the heading
- P10: holds: every after-the-data row starts with Defined after the data

## 2026-10-31 21:27 /tp on the YO v4 post: planned readings lead, after-the-data readings labelled, four-outcome words only, both rulers on precision
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: fixed: the one-liner, the table and the card led with readings defined after the data; the planned R1 (905 of 928 against 403) now leads and every after-the-data row starts with Defined after the data
- II: holds: counts printed beside every rate; R1 and R3 counts committed in yo4_counts.text
- III: holds: differences printed signed
- V: fixed: precision now prints both rulers, by record +0.029 [+0.001, +0.069] and by calendar day +0.029 [+0.000, +0.066] (our recount, defined after the data); they disagree, so the row reads cannot tell
- VI: fixed: the outcome column used higher and not worse; R2 and R4 now read above with the caveats in the text, R3 cannot tell
- R: holds: counts from yo4_counts.text and yo4_after_referee.text; ledger rows yo.v4.r1count and yo.v2.r1count on iris_lab, the after-the-data rows taken off with a reason
- L1: holds: replies read in the earlier entry
- L2: holds: no new rate was read before a check
- L3: holds: same scorer for all
- L4: cannot tell: one scoring pass, no repeat floor
- L5: n/a: our own items, built by code from IBM records
- L6: holds: 0 unread of 790 per model
- L7: holds: truth by code
- L8: cannot tell: one training seed, said in the table and the card
- L9: holds: answer not in the prompt
- L10: holds: adapter hashes as committed
- L11: n/a: nothing substituted
- L12: holds: the referee was a Claude model, the same family as the writer
- P1: n/a: the table and the card quote no one, so there is nothing to check verbatim
- P2: holds: each figure names TEST4, the everyday mix or the live record
- P3: fixed: the card's backend line now names the items as records whose 8 qubits all sit 20 to 50 hours from their stamp
- P4: holds: no cause named for the misses, the backend split or the verdict change
- P5: holds: intervals say 95 % over records, and the day ruler is named
- P6: fixed: the one-liner says only what the planned reading says
- P7: holds: ledger rows before the surface
- P8: cannot tell: rendered page checked after this entry
- P9: holds: no AI statements, plain sentences
- P10: fixed: every after-the-data reading on the page and the card is labelled

## 2026-10-31 22:20 YO v4 second seed (PLAN_YO_V4B): the seed gap; the audit holds across seeds, the verdicts and precision do not
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the plan (f80660b) and the comparison (2681511) were committed before training; same data4 files (hashes checked OK by the driver), same scorer, v4 outputs fixed since ddd7a07; 0 of 790 replies dropped
- II: holds: flips counted before any net: Job A items whose stale list differs 8 of 390 (5 favour v4b, 3 favour v4); Job C verdicts that differ 25 of 400 (20 favour v4, 5 favour v4b). This is the repeat floor between seeds
- III: holds: signs printed: R1 +0.025, R2 -0.001, R4 -0.037; the seeds trade in opposite directions (v4b finds more stale qubits and makes more false flags)
- V: holds: the planned paired bootstrap over records (2,000 resamples, seed 51, 95 %) beside the item flip counts and the false-flag counts (v4b 25 false of 1,190 flagged, v4 1 of 1,128)
- VI: holds: R1 +0.025 [+0.000, +0.057] CANNOT_TELL; R2 -0.001 [-0.011, +0.009] CONSISTENT (bound 0.011); R4 -0.037 [-0.062, -0.014] BELOW; v4b minus v2 on R1 +0.566 [+0.479, +0.649] ABOVE
- R: holds: counts from eval4_yo_v4b.jsonl and yo4b_counts.text; v4b forced a verdict on 24 of 100 CANNOT_TELL items against 5 for v4
- L1: holds: 5 whole-window, 5 general and 10 verdict replies of v4b read in full, all clean; 790 of 790 parse
- L2: holds: yo4b_compare.py wrote to yo4b_results.text unopened until the replies were read and the drops counted
- L3: holds: same base, template, extraction and max tokens as v4
- L4: caught: this run IS the repeat floor across seeds; across scoring passes it is still unmeasured (greedy decoding, one pass)
- L5: n/a: our own items, built by code from IBM records
- L6: holds: 0 unread of 790
- L7: holds: truth by code
- L8: caught: two seeds now; v4's precision (1 false flag) and verdict score (390 of 400) did not repeat on seed 45 (25 false flags, 375 of 400)
- L9: holds: answer not in the prompt
- L10: holds: v4b adapter recorded in the commit
- L11: n/a: nothing substituted
- L12: holds: no referee yet on this reading; when one reads it, it will be a Claude model, the same family as the writer

## 2026-10-31 22:30 YO table and card: the one-seed line replaced (seed 44 of a planned series; seed 45 scored; seed 46 added after)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no reading changes, only a sentence that stopped being true when seed 45 was scored
- II: n/a: no numbers added in this edit; the seed readings post together after seed 46 is read and refereed
- III: n/a: no signed values in the edited sentence
- V: n/a: no ruler used in this edit, it states the run history only
- VI: n/a: no outcome labels in the edited sentence
- R: holds: seeds and order from git (plan f80660b, results 1065a57, addendum 1 3bfcc2c)
- P1: n/a: the sentence quotes no one, so there is nothing to check verbatim
- P2: holds: names the plan and the seeds
- P3: holds: seed numbers match the configs (yo4.yaml 44, yo4b.yaml 45, yo4c.yaml 46)
- P4: holds: no cause named
- P5: n/a: no interval in the edited sentence
- P6: fixed: the old line (one training run, one seed) was stronger than the record after seed 45
- P7: n/a: no ledger number touched, the table is a feed and the card lives on Hugging Face
- P8: cannot tell: the panel feed republished; the rendered page is checked with the seed post
- P9: holds: plain sentences, no AI statements
- P10: holds: the seed 46 addendum is stated as added after the seed 45 readings

## 2026-10-31 23:06 YO v4 third seed (addendum 1) and the three-seed range: recall and audit repeat; false flags 1/25/8 and forced verdicts 5/24/11 vary; seed 44 cleanest
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: addendum 1 (3bfcc2c) and the seed 46 config, driver and comparison were committed before training; same data4 (hashes checked OK), same scorer; the addendum is stated as written after the seed 45 readings; 0 of 790 replies dropped
- II: holds: flips counted before any net: Job A 10 of 390 differ (7 favour seed 46, 3 favour seed 44); Job C 15 of 400 differ (10 favour seed 44, 5 favour seed 46)
- III: holds: signs printed: R1 +0.016, R2 +0.002, R4 -0.012 for seed 46 minus seed 44
- V: holds: the planned paired bootstrap over records (seed 52) beside the counts per seed (false flags 1/25/8, forced verdicts 5/24/11)
- VI: holds: R1 +0.016 [-0.017, +0.048] CANNOT_TELL; R2 +0.002 [-0.009, +0.013] CONSISTENT (bound 0.013); R4 -0.012 [-0.031, +0.005] CANNOT_TELL; seed 46 minus v2 on R1 +0.557 [+0.473, +0.642] ABOVE
- R: holds: counts from yo4c_counts.text (three seeds and v2 on the same items)
- L1: holds: 5 whole-window, 5 general and 10 verdict replies of seed 46 read in full, all clean; 790 of 790 parse
- L2: holds: yo4c_compare.py wrote to yo4c_results.text unopened until the replies were read and the drops counted
- L3: holds: same base, template, extraction and max tokens for every seed
- L4: holds: three seeds are now the repeat floor across training; scoring passes stay one each, greedy
- L5: n/a: our own items, built by code from IBM records
- L6: holds: 0 unread of 790 per seed
- L7: holds: truth by code
- L8: holds: three seeds; the range is printed, not one seed's point
- L9: holds: answer not in the prompt
- L10: holds: seed 46 adapter hash recorded in the commit
- L11: n/a: nothing substituted
- L12: holds: a referee on this reading will be a Claude model, the same family as the writer

## 2026-10-31 23:56 YO three-seed post: table rows and model card section for seeds 44, 45, 46 in the referee's wording, every count from yo4_seeds.py
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: seed 44 fixed in PLAN_YO_V4 before any data; seed 45 planned (f80660b) before training; seed 46 added in addendum 1 (3bfcc2c) after the seed 45 readings, said in the first row and the card; 0 of 790 replies dropped per seed
- II: holds: item flips printed before any net (stale list 8 and 10 of 390, verdict 25 and 15 of 400), and false flags in items (1, 4, 2) beside qubits
- III: holds: every difference printed signed with the Unicode minus
- V: holds: planned record bootstrap for the planned readings; the day ruler and the seed-vs-v2 verdict intervals printed as defined after the data (yo4_seeds.py, seed 53)
- VI: holds: four-outcome words only; recall gaps between seeds read cannot tell, only the audit reads consistent; precision between seeds cannot tell (seed 46 minus 44 sits on the 0.02 margin, read cannot tell by the committed rule where the referee read consistent)
- R: holds: every count from yo4_seeds.text, yo4_results.text, yo4b_results.text, yo4c_results.text and yo4_after_referee.text; our recount matches the referee's on every count
- L1: holds: replies read in full for each seed in earlier entries
- L2: holds: no new rate read before a check
- L3: holds: same scorer for every seed
- L4: holds: three seeds are the training repeat floor, scoring passes one each
- L5: n/a: our own items, built by code from IBM records
- L6: holds: 0 unread of 790 per seed
- L7: holds: truth by code
- L8: holds: three seeds, the range printed, and the card says a fourth could fall outside it
- L9: holds: answer not in the prompt
- L10: holds: adapter hashes in the commits (44 4737100d, 45 1ac8c658, 46 321cf71f)
- L11: n/a: nothing substituted
- L12: holds: both referees were Claude models, the same family as the writer
- P1: n/a: the table and the card quote no one, so there is nothing to check verbatim
- P2: holds: rows name TEST4, the seeds, the everyday mix and the live record
- P3: holds: seed numbers and item labels match the configs and the files
- P4: holds: no cause named for the seed differences, the misses or the verdict change
- P5: holds: intervals are 95 % over records, the day ruler named where used
- P6: fixed: 'cleanest' and 'one seed' removed; seed-44-only rows labelled; seed 44 also shown as the one finding the fewest stale qubits
- P7: n/a: the table is a feed and the card lives on Hugging Face; the lab one-liner (seed 44, 905 of 928 against 403) is unchanged and its ledger rows stand
- P8: cannot tell: rendered page checked after this entry
- P9: holds: plain sentences, no semicolons, no AI statements
- P10: holds: every after-the-data row starts with Defined after the data

## 2026-11-01 08:23 YO v5 (seeds 47, 48) read under PLAN_YO_V5: YO v4 stays at work; same-date gain above for seed 47, cannot tell for seed 48; seed 47 below on flag precision, seed 48 below on verdicts; posted after the referee
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: TEST4 and TEST5 and the nulls built and committed before the first v5 step (eb36e3f); no test record in training (cut 2 Oct, asserted); nothing dropped (0 unparsed replies in every set)
- II: caught: net rates hid where the losses sit; counted item by item: seed 47 25 false flags in 5 items, seed 48 45 forced verdicts, all false flags of every model in young same-date items; flips printed both ways for both seeds
- III: holds: the gain on the target and the loss on precision and verdicts printed side by side with their signs, never netted
- V: holds: paired bootstrap over records (plan) beside exact item counts and the repeat floor of YO v4 own three seeds (1, 25 and 8 false flags)
- VI: holds: four outcomes per reading; seed 48 target gain printed as cannot tell, R5b band of zero width said so
- R: holds: every count from yo5_results.text, yo5_counts.text and yo5_counts2.text, recounted by our code after the referee; FUTURE stamps from the items
- L1: holds: every reply read as a bare answer before any rate: 0 of 790, 590 and 15 per model carried extra text; scorer reads all
- L2: holds: no rate read before the reply check; liveness read from progress lines only
- L3: holds: same prompt format, chat template, decoding and max tokens as YO v4; base and adapters named
- L4: holds: one machine, YO v4 own seed spread (1, 25, 8 false flags; 5, 24, 11 forced) used as the repeat floor
- L5: n/a: our own model and data, no released files to recount from
- L6: holds: no truncation, echo or refusal; 0 unparsed in every set
- L7: n/a: no gold set from a labeller; answers computed by code
- L8: holds: paired over records; two seeds reported, neither picked
- L9: holds: the prompt holds the record and the rule, never the answer
- L10: holds: base Qwen3-1.7B and adapter hashes recorded (ADAPTERS_YO_V5.sha256)
- L11: n/a: IBM records from our own history pull, row counts printed by the builder
- L12: holds: the outside referee is the same model family as the writer and it is said in its report; disclosure stays in the CHECKS text
- P1: n/a: the post quotes no one, nothing verbatim to check
- P2: holds: each figure names its test set (YO v4 test records, same-date items, FUTURE)
- P3: holds: readings named as the plan names them
- P4: holds: no cause given for the false flags, only where they sit
- P5: holds: 95 % paired bootstrap over test records, as in the table header
- P6: fixed: one-liner and card no longer read as two wins; seed 48 gain said cannot tell; the rule failure stated for both seeds
- P7: holds: ledger rows for the one-liner numbers before the ship; ship.sh only
- P8: cannot tell: rendered IRIS lab page and live panel checked after the ship
- P9: holds: no AI statement, plain sentences, no semicolons
- P10: holds: every count not in the plan labelled defined after the data

## 2026-11-01 12:55 YO v6 reading (yo6_results.text from yo6_compare.py) and its counts (yo6_counts.text, defined after the data)
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: both seeds and YO v4 scored on the same TEST6 and TEST4 items with the same code; nulls scored with it before training
- II: holds: item flips counted per set against YO v4 (seed 49: 6 up and 22 down on audit items; seed 50: 8 and 10) beside every net share
- III: holds: false-flag shares fall for both seeds (below = fewer), stale-found shares fall for seed 50 and whole-window recall for seed 49; direction said per row
- V: holds: paired bootstrap over records, 95 %, with counts printed beside every share
- VI: holds: four outcomes per reading; R6c CANNOT_TELL for both seeds is printed as such and is one of the reasons the rule fails
- R: holds: counts from yo6_counts.py on the eval files; FUTURE6 15 records 13:28 to 15:00 UTC 1 Nov read from the item ids; 9,000 training items counted
- L1: holds: every FUTURE6 miss read in full (4 replies); parser is yo4/yo6_compare's, unchanged since v4
- L2: holds: no rate read before the replies; the v6 rates were read after the driver's reply pass
- L3: holds: same prompt format, chat template and extraction for YO v4 and both seeds
- L4: n/a: one machine (this Mac), one GPU job at a time; no across-machine claim
- L5: holds: counts recomputed from our own eval files with our code
- L6: holds: unparsed replies count as no flags (flagged() returns empty), the same for every model
- L7: holds: answers come from timestamp arithmetic in code, not from a labeller
- L8: holds: paired over records; two seeds each reported, no point win claimed
- L9: holds: the prompt shows dates and stamps only; the answer is computed, never shown
- L10: holds: adapter files hashed by the drivers; base model unchanged
- L11: n/a: no dataset or tool aged out
- L12: n/a: no model referee or labeller in the reading itself; the post referee will be a same-family model and is said so in the checks
- P1: holds: no quotes in the post rows except our own plan words
- P2: holds: each row names its test set (new set, YO v4's test records, new IBM records)
- P3: holds: seed numbers 49 and 50 as in the plan
- P4: holds: no cause named for the recall loss
- P5: holds: every band is a 95 % bootstrap band over records
- P6: holds: the one-liner says YO v4 stays at work
- P7: n/a: ledger and ship after the referee
- P8: n/a: page checked after ship
- P9: holds: plain sentences, no AI statement, no counts of our things in headings
- P10: holds: rows 14 to 16 say defined after the data

## 2026-11-01 15:20 YO v6 referee flags acted on (yo6_counts2.text, our own recount of each new number); post draft 2
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the off-record count uses the same eval files and items for all three models
- II: holds: off-record numbers counted per model and set (seed 49: 4 on YO v4's items; seed 50: 1 and 1; YO v4: 0) before any share
- III: holds: both seeds' all-flags R3 differences are negative; seed 49's band excludes zero
- V: holds: two rulers side by side for R3, the planned in-record count (consistent) and every flagged number (seed 49 below), both printed
- VI: fixed: row 16 adds the all-flags reading with its band and label; nothing in the plan rule changes
- R: holds: 662 records, 168 shared with TEST4, 280 with TEST5, 890 items, read by yo6_counts2.py
- L1: holds: the four off-record numbers read in the replies with their shown qubits printed
- L2: holds: no new rate seen before the recount
- L3: holds: same scorer as planned for the planned rows
- L4: n/a: one machine, no cross-machine claim in the post
- L5: holds: every referee number recounted with our own code before the draft used it
- L6: fixed: replies whose flagged numbers fall outside the record are now counted and named, per model
- L7: holds: answers from code
- L8: holds: paired over records, seeds reported separately
- L9: holds: prompts carry no answers
- L10: n/a: no backend change between the three models
- L11: n/a: nothing aged
- L12: holds: the referee was a same-family model, recorded here
- P1: holds: the plan's own words quoted in the erratum
- P2: fixed: each row now names its test set (new set or YO v4's test records)
- P3: fixed: R1 row restores "qubits stale by 24 to 48 hours"
- P4: holds: row 19 describes the data counts and says it is not a cause
- P5: holds: bands are 95 % bootstrap over records
- P6: fixed: one-liner and card say "was below" and add the unclear older same-date gain
- P7: n/a: ledger and ship next
- P8: n/a: page after ship
- P9: fixed: semicolon removed (row 19), "training now" removed
- P10: fixed: the FUTURE detail moved to its own defined-after-the-data row (14)

## 2026-11-01 16:05 YO v6 post placed: results table block (19 rows), yo6_result.json, card section, plan erratum, IRIS lab one-liner
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every row is the referee-checked draft 2 text, parsed from yo6_post_draft.md by the publish script, no retyping
- II: holds: item flips and off-record counts printed beside the net shares (rows 16 and 18)
- III: holds: "below (fewer flagged, the wanted direction)" says which way each below points
- V: holds: two R3 rulers (in-record and every flagged number) both printed
- VI: holds: four outcomes per row as in yo6_results.text and yo6_counts2.text
- R: holds: counts from yo6_counts.text and yo6_counts2.text; ledger rows yo.v6.r6b.counts and yo.v6.rule cite them
- L1: holds: FUTURE misses read in full before the post (yo6_counts.text)
- L2: holds: no new rate in this step
- L3: holds: setup unchanged across the three models
- L4: n/a: single machine
- L5: holds: every number recounted with our code
- L6: holds: off-record flags counted and named per model
- L7: holds: answers from code
- L8: holds: paired over records
- L9: holds: prompts carry no answers
- L10: n/a: no backend change
- L11: n/a: nothing aged
- L12: holds: same-family referee recorded in the 15:20 entry
- P1: holds: the plan's words quoted exactly in the erratum
- P2: holds: rows name their test set
- P3: holds: seed numbers as in the plan
- P4: holds: row 19 says description, not cause
- P5: holds: bands are 95 % bootstrap over records
- P6: holds: one-liner and card say YO v4 stays at work and name both failing readings and the unclear gain
- P7: holds: ledger rows added before ship
- P8: n/a: page checked after ship
- P9: holds: plain sentences, no semicolons, no AI statement
- P10: holds: rows 14 to 18 say defined after the data

## 2026-11-01 12:50 correction note (not a reading)
The 1 Nov 2026 entry headers above were typed by hand and their times are wrong (written before 12:50 EST); the git commit time of each entry is the record. From here on headers take their time from the clock.

## 2026-11-01 13:34 YO v7 reading (yo7_results.text from yo7_compare.py): seed 51 passes, seed 52 fails, YO v4 stays
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: both seeds and YO v4 on the same TEST4 and TEST6 items with the planned scorer; nulls as committed
- II: holds: the two seeds disagree sharply (R6c +0.031 against -0.118); the spread between seeds is reported as the reading, not averaged
- III: holds: signs per reading printed per seed; seed 51 all non-negative where it matters, seed 52 negative on R6c, R6b found
- V: holds: paired bootstrap over records, 95 %, both seeds side by side
- VI: holds: four outcomes per reading; the rule needs both seeds, so YO v4 stays
- R: holds: counts and intervals from yo7_results.text; reply read committed first (yo7_replies.text)
- L1: holds: replies read structurally and 10 per kind in full before the comparison (yo7_replies.text, committed first)
- L2: caught: a progress tail printed seed 52's TEST6 aggregate before the reply read (logged in tp_score); no other rate seen first
- L3: holds: same prompt format, template and extraction as v4 to v6
- L4: n/a: one machine
- L5: holds: our own scorer on our own eval files
- L6: holds: unparsed 0 and off-record 0 for both seeds (yo7_replies.text)
- L7: holds: answers from code
- L8: holds: paired over records; two seeds reported separately, no point win claimed
- L9: holds: prompts carry no answers
- L10: n/a: no backend change
- L11: n/a: nothing aged
- L12: n/a: no model labeller in this reading; the post referee comes next and is same-family

## 2026-11-01 17:12 YO v7 seed retest (PLAN_YO_V7S): seeds 53, 54, 55 each pass the PLAN_YO_V7 rule against YO v4; YO v7 seed 51 replaces YO v4
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: three new seeds and YO v4 on the same TEST4 and TEST6 items with the planned scorer; same data, base, adapter start and settings as v7 (yaml differs only in seed and path, referee diff)
- II: holds: seeds compared item by item where it mattered (seed 51 vs 53 replies differ on 25 of 890 TEST6, none changes R6c); per-seed values and the five-seed spread reported, not averaged
- III: holds: R6c positive for all three (+0.031, +0.027, +0.024), R6b_false negative or CANNOT_TELL for all three, R3 negative for all three (-0.007), sign stated in the write-up
- V: holds: paired bootstrap over records, 95 %, seed 41 as planned; referee re-ran seeds 1, 2, 3 and twenty more for R3 with the same outcome words
- VI: holds: four outcomes per reading; R3 for seeds 54 and 55 has an upper bound at +0.00005 and +0.0001, so the wording is 'not shown worse on R3', never 'equal'
- R: holds: values from yo7s_results.text, recomputed independently by the referee (REFEREE_YO_V7S.md); plan 13:35:39 and known-good 13:35:40 committed before training
- L1: holds: replies read structurally and 10 per kind in full before the comparison (yo7s_replies.text, committed before yo7s_compare.py)
- L2: caught: the copied reply reader printed the old v7 seeds in its sample section; fixed and committed before any reply or rate was read (logged)
- L3: holds: same prompt format, template and extraction as v4 to v7
- L4: n/a: one machine, one GPU job at a time
- L5: holds: our own scorer on our own eval files; referee recomputed with its own code
- L6: holds: v7d has one unparsed TEST4 reply (a runaway repetition cut at the length limit) scored 0 as the rule fixes; off-record flags 2 (v7d) and 2 (v7e) counted
- L7: holds: answers from code
- L8: holds: paired over records; three seeds reported separately and each must pass, no point win claimed
- L9: holds: prompts carry no answers
- L10: n/a: no backend change
- L11: n/a: nothing aged
- L12: holds: the referee is the same model family as the writer and the write-up says so

## 2026-11-01 17:17 YO v7 post placed (draft 2, every flag in REFEREE_YO_V7_POST.md acted on); live reader gate to adapters/v7
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same readings and nulls as the committed results; no new comparison in the post
- II: holds: per-seed values printed, seed 52's failure kept in the table and the card
- III: holds: signs printed per seed; R3 and the verdict dips are stated as lower, not as gains
- V: holds: 95 % paired bootstrap bands printed beside every difference
- VI: holds: four outcome words per seed; 'not shown worse' used where the band reaches zero, never 'equal'
- R: holds: every number from yo7_results.text and yo7s_results.text; the referee checked each row against them
- P1: holds: no quotation marks around paraphrase; plan names quoted as written
- P2: holds: each figure says which test set and which seed it comes from
- P3: holds: setting labels (seeds, sets, margin) match the plans
- P4: holds: no cause named for any difference
- P5: holds: every band is the 95 % paired bootstrap over records, stated in the column header
- P6: fixed: B and C said 'without flagging more' and 'none flagged more' where seed 55 reads 0.003 against 0.000; now 'without being shown to flag more'
- P7: holds: ledger rows yo.v7.rule and yo.v7.r6c added before the surfaces; ship.sh next, then checked live
- P8: holds: checked on the rendered pages after ship
- P9: fixed: the referee line in row 13 named the model family (an AI statement on a public page); replaced with 'recomputed with separate code from the raw reply files'
- P10: n/a: no post-hoc reading in this post

## 2026-11-02 05:58 YO v8 seeds 56, 57, 58 vs YO v7 seed 51 by PLAN_YO_V8 (yo8_results.text)
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: comparison to YO v7 seed 51 and nulls fixed in PLAN_YO_V8 before training; same test items for every arm, no reply dropped (800/890/790 per arm)
- II: holds: per-seed values and per-kind R8 printed, no pooling across seeds; seed 56 R6c drop (0.852) kept, not averaged with 57 and 58
- III: holds: signs printed per seed; R8 gains and the R6b false-flag rises (+0.026, +0.047) read as opposite directions, not netted
- V: holds: paired bootstrap over records, 2,000 resamples, seed 41, 95 % band beside every difference, margin 0.02
- VI: holds: four outcome words per reading; the rule needed all three seeds and none passed, so YO v7 stays
- R: holds: every number from yo8_results.text (comparison commit 1655f66 before the run); TEST6 and TEST4 were read before, said so
- L1: holds: every reply checked against its parsed label (TEST8C out equals pred on 2,400 of 2,400) plus 10 per kind per seed read in full
- L2: holds: the .out score files were not opened; the first rates seen are in yo8_results.text, after the parser read
- L3: holds: same base, prompt format, chat template and settings for every seed and for v7, from PLAN_YO_V8
- L4: n/a: one machine (Mac mlx), one run per seed; seed spread is the floor reported, no cross-machine claim
- L5: holds: R8 recomputed from reply text against the item answers; agrees with the scorer on 800 of 800 per arm
- L6: holds: unreadable replies counted: none on TEST8C, none unparseable JSON on TEST6 and TEST4, for every seed
- L7: holds: answers computed by code from the printed numbers (yo2_data.truth), not from any model
- L8: holds: paired over the same records; three seeds shown, none chosen by score
- L9: holds: prompts carry the interval and reference only; the verdict is computed, the oracle check gives 1.000
- L10: holds: adapters pinned by sha256 in ADAPTERS_YO_V8.sha256; no hosted model involved
- L11: n/a: no dataset or tool substituted
- L12: n/a: no referee or labeller used for this reading; any public post gets its referee line then

## 2026-11-02 06:15 YO v8 post (yo8_post_draft.md draft 2): results table rows, IRIS lab sentence, model card section
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same readings and nulls as yo8_results.text; no new comparison in the post
- II: holds: per-seed values printed, every seed failure kept in the table, B and C
- III: holds: signs per seed; R8 gains and the R6b false-flag rises stated in their own directions
- V: holds: 95 % paired bootstrap bands beside every difference in the table
- VI: holds: four outcome words per seed; two margin-edge labels said to change with the resampling stream
- R: holds: every number from yo8_results.text; the referee recomputed each from the raw reply files and agreed
- P1: holds: no quotation marks around paraphrase; plan names as written
- P2: holds: each figure names its test set and seed
- P3: holds: seeds 56, 57, 58, sets and margin match PLAN_YO_V8
- P4: holds: no cause named for any difference
- P5: holds: every band is the 95 % paired bootstrap over records
- P6: fixed: B said more exact border verdicts as a win for all seeds; now says one seed band reaches zero, C the same
- P7: holds: ledger rows yo.v8.rule and yo.v8.r8 added before the surfaces; ship.sh then checked live
- P8: holds: checked on the rendered page after ship
- P9: holds: no AI statement, plain sentences, no semicolons, no counts in headings
- P10: holds: the margin-out reading is labelled defined after the data in row 13

## 2026-11-02 09:55 yo2_result.json gains the refereed YO Read rows (read/yr_post_draft.md draft 2)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- II: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- III: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- V: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- VI: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- R: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P1: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P2: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P3: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P4: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P5: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P6: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P7: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P8: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P9: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code
- P10: holds: same entry as read/CHECKS.md for the YO Read post; rows copied from the refereed draft 2 by code

## 2026-11-04 04:03 YO Read rescore public sentence (YO_READ_PUBLIC_SENTENCE_20261104.md) for IRIS lab: DATES/LINK/REQUEST per seed vs always-NO
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the comparison (always-NO, McNemar per field, Holm across 9) was fixed in PREREG_YO_RESCORE.md (fe751109, Bitcoin 974471, 03:42Z) before the 05:32Z run; the 22 rebuilt papers were chosen by a mechanical size rule, labels unchanged; 0 unread in every arm
- II: holds: per-item discordant counts (b, c) printed for every seed and field; seed 63 DATES b 28 c 24 carried in the sentence instead of netted
- III: caught: REQUEST was first written as "no seed beats always-NO" while seeds score 0.980/0.959/0.966 > 0.912; reworded to "no lead is clear" (tp_score row)
- V: holds: ruler is exact McNemar on discordant pairs with Holm; rates printed beside raw counts
- VI: holds: DATES seeds 61/62 ABOVE, 63 CONSISTENT-not-cleared; LINK all ABOVE; REQUEST CANNOT_TELL (underpowered, 13 YES), said as too small, not negative
- R: holds: every figure read off yo/read/results_rescore.text lines 2-10 on 4 Nov; data hash 132a3b0f now in Bitcoin 974489/974491 (merkle checked)
- L1: holds: YES/NO answers parsed by the frozen scorer; 0 unread
- L2: holds: rates seen only after the prereg was stamped
- L3: holds: same sentences and items for every seed; baseline always-NO named
- L4: n/a: one machine (Mac), one run; no cross-machine claim
- L5: holds: recount from data/test_items_rescore.jsonl with yr_rescore_score.py
- L6: holds: 0 unread, 0 dropped, per seed
- L7: holds: gold = QIA List entries, not built from YO
- L8: holds: paired McNemar per paper; three seeds reported as a count
- L9: holds: prompts hold the paper sentences, not the label
- L10: holds: adapters hashed (ADAPTERS_YO_READ.sha256)
- L11: n/a: no dataset or tool was substituted; items are data/test_items_rescore.jsonl, hash 132a3b0f
- L12: holds: disclosed internally that the referee (Sage) is the same model family as the writer; no labeller model used
- P1: holds: the sentence contains no quotation of any source text
- P2: holds: figures from results_rescore.text (rescore, 4 Nov)
- P3: holds: field names as in the prereg
- P4: holds: seed 63 described by its counts, no mechanism named
- P5: holds: no interval printed; counts only
- P6: holds: Sage VERDICT MOVES then swap applied (09:03Z); every number read off the file by Bones
- P7: holds: ledger rows yo.read.rescore.dates/link/request added before the surface edit, release via ship.sh only
- P8: holds: rendered iris/lab page fetched live after ship and the sentence found (checked by ship.sh verify and a curl grep)
- P9: holds: plain sentences, no AI statement, no count in a heading
- P10: holds: rescore rule set before the run; the decision to rescore was made after viewing old outputs, stated in RESCORE_NOTE

## 11 Nov 2026: rows withheld at the author's request
The fresh-read eval files (yo/read/fresh/eval_fresh_yo_*.jsonl) no longer carry the rows for arXiv 2405.17230 and 2310.09826, removed from the QIA list at the author's request. Originals kept privately. Scores over the remaining rows are not recomputed in published text.
