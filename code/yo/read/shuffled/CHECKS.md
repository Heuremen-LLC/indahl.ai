
## 2026-11-04 16:47 YO Read shuffled-label null: 0 of 3 seeds clear DATES, 0 of 3 clear LINK -> PASS
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: always-NO and the label-shuffle were fixed in PLAN_YO_SHUFFLED before training (block 974519); same 148 papers, same prompts, same frozen eval as YO Read; no gate drops items (0 unread, all arms)
- II: holds: flips counted per seed (b, c printed); DATES b 0 c 0 on all three, LINK 49/62 and 32/39, no netting
- III: holds: LINK seeds 71 and 73 both below always-NO (same sign), neither significant; reported as below, not folded into "no gain"
- V: holds: exact two-sided McNemar on discordant pairs plus accuracy vs always-NO, Holm across 9, as Addendum 1
- VI: holds: zero and the size that matters both checked; YO Read DATES gains were b 18 and 25, shuffled b 0 on every seed, so a YO-Read-sized gain is excluded on DATES; outcome PASS per the plan
- R: holds: counts read from eval_rescore_yo_shuf1-3.jsonl; train/eval times from ys_drive.log; stamps sha-checked OK before scoring
- L1: holds: all 1332 replies parsed, every one a bare YES or NO; 10 per seed printed beside the parse
- L2: holds: parser check ran before ys_score.py; no rate seen first
- L3: holds: same harness both sides (yr_rescore_eval.py frozen, mlx-lm, Qwen3-1.7B, thinking off, greedy)
- L4: n/a: one machine (Mac), one run per seed; seed width shown by the three seeds
- L5: holds: recounted with a copy of the frozen scorer; diff limited to file names, seeds, output path
- L6: holds: 0 unread, 0 dropped in every arm
- L7: n/a: labels are the rescore truth, not built from this model
- L8: holds: paired per paper (McNemar); three seeds reported separately
- L9: holds: prompts unchanged from YO Read; shuffle touched completions only
- L10: holds: base snapshot pinned in Addendum 2 (70d244cc)
- L11: n/a: no dataset substituted
- L12: n/a: no referee or labeller in this reading
- P1: holds: IRIS wording copied verbatim from Addendum 1 item 2
- P2: holds: every figure is from results_shuffled.text in this folder
- P3: holds: seeds 71-73, fields as in the plan
- P4: fixed: "learned the base rate" removed from the results file; we name no mechanism
- P5: n/a: no interval printed; p-values named as exact McNemar, Holm-adjusted
- P6: holds: three seeds are a smoke alarm (Addendum 1); nothing stronger printed
- P7: cannot tell: not on any public page yet; IRIS line waits for the ledger and ship.sh
- P8: n/a: no page touched
- P9: holds: plain sentences, no counts in titles
- P10: holds: the "Shape" lines are descriptive of this run, written after the data, and labelled as read from the replies
