
## 2026-11-04 17:27 SELF-LABEL arm: YO Read beats self-label 2/3 DATES, 0/3 LINK, 3/3 REQUEST -> FAIL on DATES and LINK; combined sentence not allowed
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: comparison (YO Read vs self-label, same 148 papers, same frozen eval) and PASS/FAIL fixed in Addendum 2, block 974519; scorer committed 8af4e22 before replies; 0 dropped in either arm
- II: holds: b and c printed per pair, nothing netted; YO Read ahead in 9 of 9 pairs is reported beside the stamped FAIL
- III: holds: all 9 pairs same sign (YO Read ahead); REQUEST self-label adapters below always-NO printed with its direction
- V: holds: exact two-sided McNemar on discordant pairs, Holm across 9, plus accuracy, as Addendum 2
- VI: holds: DATES and LINK read FAIL per the stamp (not shown), never as "no gain" and never as "self-sharpening proven"; three seeds may be underpowered, said
- R: holds: counts from eval_rescore_yo_read1-3 and eval_rescore_yo_self1-3; times from sl_drive.log; stamps sha-checked by the driver
- L1: holds: 1332 of 1332 replies bare YES/NO before any rate
- L2: holds: parser count ran before sl_score.py
- L3: holds: same frozen harness both arms (yr_rescore_eval.py, Qwen3-1.7B, thinking off, greedy)
- L4: n/a: one machine, three seeds reported
- L5: holds: scored by the committed script, unchanged
- L6: holds: 0 off-format in base-rate generation, 0 unread at test
- L7: holds: self-labels come from the base model and are scored against rescore truth, not against themselves
- L8: holds: paired per paper, seeds separate
- L9: holds: prompts unchanged
- L10: holds: base snapshot 70d244cc, weight hashes matched Addendum 2 before generation
- L11: n/a: no dataset or tool substituted; same rescore items (DATA_YO_RESCORE sha checked)
- L12: n/a: no referee or labeller beyond the base model, which is the thing tested
- P1: holds: page wording copied from Addendum 2 ("NOT SHOWN to need the real labels")
- P2: holds: figures from results_selflabel.text
- P3: holds: seeds 61-63 vs 74-76
- P4: holds: no mechanism named
- P5: n/a: p-values named as exact McNemar, Holm
- P6: holds: combined sentence withheld because one arm failed
- P7: cannot tell: nothing public yet; IRIS line waits for our word and ship.sh
- P8: n/a: no page rendered or changed tonight
- P9: holds: plain sentences, no counts in titles, no AI statements
- P10: holds: READING block labelled "written after the data"
