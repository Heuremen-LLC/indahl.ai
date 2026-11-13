
## 2026-11-02 09:44 YO Read seeds 61, 62, 63 vs REGEX by PLAN_YO_READ (yr_results.text)
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: arms and candidates fixed in PLAN_YO_READ before items were built; same candidates for every arm; no item dropped (444 per arm)
- II: holds: flips counted per question against REGEX before the net (DATES seed 61: 68 right-only, 13 regex-only)
- III: holds: false YES and false NO printed separately per arm; signs per seed printed
- V: holds: paired bootstrap over 148 TEST papers, 2,000 resamples, seed 41, 95 %, margin 0.02; MAJORITY and BASE printed beside
- VI: holds: four outcomes; all three seeds pass the written rule; REQUEST cannot tell for all three
- R: holds: every number from yr_results.text; comparison committed before it ran
- L1: holds: every reply parsed (0 unread for the seeds, 1 for BASE) and 10 per question read in full
- L2: holds: no .out score file opened before the parse read
- L3: holds: same prompt and candidates for BASE and the seeds; REGEX reads the same candidates
- L4: n/a: one machine, one run per seed; seed spread is reported
- L5: holds: truth is the published List entry, matched by arXiv id or DOI
- L6: holds: unread counted per arm and scored wrong (BASE 1)
- L7: cannot tell: the List labels came from Sonnet reads of the same papers; YO is scored against them, not against a fresh human read
- L8: holds: paired over the same papers; three seeds shown, seed 61 fixed in the plan
- L9: holds: prompts carry candidate sentences only, the answer is not in them by construction
- L10: holds: adapters pinned by sha256 in ADAPTERS_YO_READ.sha256
- L11: n/a: no dataset substituted
- L12: holds: the List labels were made by the same model family as the writer; any public post says so

## 2026-11-02 09:55 YO Read post (yr_post_draft.md draft 2): IRIS lab rows and sentence
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: same arms and readings as yr_results.text; no new comparison
- II: holds: per-seed values and seed 61 false YES and false NO printed, not netted
- III: holds: signs per seed in the bands
- V: holds: 95 % paired bootstrap over 148 test papers beside every difference
- VI: holds: four outcome words; REQUEST cannot tell for all three
- R: holds: the referee recomputed every number from the raw replies and agreed within 0.007
- P1: holds: no paraphrase in quotation marks
- P2: holds: each figure names its question, set and seed
- P3: holds: seeds 61, 62, 63 and the 148 held-out papers match the plan
- P4: holds: no cause named
- P5: holds: every band is the 95 % paired bootstrap
- P6: fixed: the one-liner quoted the best seed and left out the always-no score; now 0.818 to 0.892 against 0.520 and 0.804
- P7: holds: ledger rows yo.read.rule and yo.read.rd added before the surfaces
- P8: holds: checked on the rendered page after ship
- P9: fixed: a model-family sentence replaced with a neutral one; no semicolons
- P10: n/a: no post-hoc reading

## 2026-11-03 19:50 YO Read hold: IRIS lab score sentence replaced by a held line (Sage MOVES, HOLD_VERIFY_20261103.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no new comparison; the held line reports faults counted on the build-time List (pre-removal-20261102, 688 papers, 148 TEST)
- II: holds: wrong text counted per paper by split (TEST 22 of 148); not netted against anything
- III: n/a: no difference or sign is printed in the held line
- V: n/a: no interval printed; the 0.818 to 0.892 range is taken off the page
- VI: holds: the score is held, not called above or below; rescore outcome left open
- R: holds: every count in the line from HOLD_VERIFY_20261103.md, scripts in verify_20261103/; referee time 3 Nov 19:36 EST
- P1: holds: no quotation of anyone; the referee is named only as an outside read
- P2: holds: counts name the set (test papers) and the question (data-link)
- P3: holds: 148 test papers and the build-time List match the plan and the committed data hash
- P4: holds: no cause named for the score, only the two faults found
- P5: n/a: no interval in the line
- P6: fixed: the draft's 17 of 142 was counted on today's List; the line uses 22 of 148, the set that was scored
- P7: holds: ledger rows yo.read.rd and yo.read.rule set to held and yo.read.hold added before build_site.py was edited
- P8: cannot tell: not shipped by this pass; check the rendered page after ship
- P9: holds: plain sentences, no semicolons, no counts in headings
- P10: n/a: no post-hoc reading in the line

## 2026-11-04 00:36 YO rescore under PREREG_YO_RESCORE (fe751109): DATES cleared by seeds 61, 62, not 63; LINK all three; REQUEST none
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: always-NO baseline on the same 444 items, frozen in the prereg before any reply; the 22-paper text correction was set by the 3 Nov size rule (verify_20261103/texts.py), not by any reply; no item dropped; unread counted wrong (0 unread in every arm)
- II: holds: every seed and field printed with discordant pairs (b, c) beside the rates; nothing pooled into a headline; seed 63 failing DATES is reported, not netted away
- III: holds: accuracy is signed against always-NO (above/below) and the clear needs above AND Holm p < 0.05; REQUEST seeds are above always-NO but do not clear, said so
- V: holds: exact two-sided McNemar on discordant pairs per seed x field, Holm across the 9, as frozen; raw counts beside every rate
- VI: holds: per test two outcomes plus the frozen 'does not clear'; DATES reads CLEARS for 61/62 and does not clear for 63, reported as a split, not as 'YO clears'
- R: holds: counts read from results_rescore.text written by yr_rescore_score.py; prereg hash fe751109 Bitcoin-attested block 974471 (03:42Z) before the 05:32Z run; items 132a3b0f; replies committed unread in d0f6f53
- L1: cannot tell: the parse is the plan's fixed uppercase YES/NO first-token rule (known-good pins it); replies were not hand-read for parser misses beyond 0 unread; Sage is asked to read them
- L2: holds: no rate was looked at before the replies were committed unread (drive script commits, then scores)
- L3: holds: same harness, prompt render, max_tokens 8 and adapters as the first YO Read (hash-checked ADAPTERS_YO_READ.sha256); only the 66 rebuilt prompts differ
- L4: n/a: one machine, one backend, the same seeds as the first read; no cross-machine claim
- L5: holds: recounted with our own scorer from the committed reply files; ids matched exactly to the item file
- L6: holds: 0 unread replies in every arm; no truncation drops (max_tokens 8, YES/NO answers)
- L7: n/a: labels come from the List (pre-removal snapshot), not from any YO output
- L8: holds: paired McNemar on the same items; three seeds reported, no best-seed pick
- L9: holds: prompts carry candidate sentences, not the label; unchanged builder (yr_data candidates/prompt)
- L10: n/a: no claim across hosts or backends
- L11: holds: the List snapshot list.json.pre-removal-20261102 is the frozen label source, hash-identical per the prereg
- L12: holds: Sage (same model family as Bones) is the referee and is named as such

## 2026-11-05 00:47 read1 retrain bit-identical to the A4-stamped adapter (d3df26bb) at all checkpoints; stamped adapter vouches for read1 training files
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the comparison (bit-identical vs not) and its reading were written in retrain_read1/RULE.md and committed (07657e3) before the run; nothing dropped
- II: holds: every checkpoint compared, not only the final (200/400/600/800 and final, all identical); train-loss lines at each checkpoint agree to 3 decimals
- III: n/a: a byte comparison has no sign
- V: holds: ruler = sha256 equality of the safetensors files, with the training-loss log beside it as a second reading; both agree
- VI: holds: the rule had two outcomes written first (bit-identical vouches; anything else CANNOT TELL, never failure); the result is the first
- R: holds: hashes from shasum on the files (retrain_read1/HASHES.text, MANIFEST.txt); versions python 3.12.13 / mlx 0.32.0 / mlx_lm 0.31.3 read live; stamped hash d3df26bb from Addendum 4
- L1: n/a: no model replies are parsed here
- L2: n/a: no rate computed
- L3: holds: same yr1.yaml except adapter_path (diff shown), same data hashes, same base snapshot 70d244cc offline, same package versions as installed since August
- L4: n/a: one machine; the result is identity on the same Mac, not a cross-machine claim
- L5: n/a: no released file is recounted in this reading
- L6: n/a: no model replies exist in this reading, so nothing is unread or dropped
- L7: n/a: no gold set
- L8: n/a: one seed (61), as in the original
- L9: n/a: no evaluation prompt
- L10: holds: this pins behaviour for read1 on this host and these versions only; said so in RESULT.md
- L11: n/a: no substituted dataset
- L12: n/a: no referee or labeller in this reading (Sage set the rule; same model family, named elsewhere)
