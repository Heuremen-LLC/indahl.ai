
## 2026-11-04 17:50 Fresh test planned: 288 unused List papers, nine existing adapters, plan stamped before any answer
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: comparisons and rules written in PLAN_YO_FRESH.md and stamped before any adapter answers; no result exists yet
- II: n/a: no result yet; scorer prints b and c per pair
- III: n/a: no result yet
- V: holds: exact McNemar + accuracy, Holm per family, named in the plan
- VI: holds: plan names REPLICATES / does not, PASS / not shown; never "as good"
- R: holds: 288 papers and 864 items counted by yf_build.py output; stamp time from STAMPED_AT.txt
- L1: n/a: no replies yet; parser read is in the plan before scoring
- L2: holds: no rate exists
- L3: holds: yf_eval.py is yr_rescore_eval.py with paths changed (diff checked)
- L4: n/a: one machine
- L5: holds: items built by yr_data.py functions unchanged
- L6: holds: 0 empty texts left out, counted
- L7: holds: labels from the List, not from any adapter
- L8: holds: paired per paper
- L9: holds: prompts built as YO Read; known-good truth 1.000, flipped 0.000
- L10: holds: adapters hash-checked by the driver
- L11: n/a: no dataset substituted
- L12: n/a: no referee or labeller used
- P1: n/a: the page sentence quotes no source text
- P2: holds: 288 is in PLAN_YO_FRESH.md and yf_build.py output
- P3: holds: arms and seeds as in the plan
- P4: holds: no cause named
- P5: n/a: no interval printed
- P6: holds: page says planned, not run
- P7: holds: ledger row, then ship.sh
- P8: cannot tell: checked after ship
- P9: holds: plain sentences, no counts in headings
- P10: holds: base-rate shift said as a property of the papers

CORRECTION (4 Nov ~23:12Z, Sage VERDICT 23:08Z): P10 above ("base-rate shift said as a property of the papers") was wrong. The plan never said it, and
the shift tracks labels that default to YES where the reader wrote no F4 note (98 of 288). L9 cited a known-good output that was not saved; it is now
saved in KNOWN_GOOD.text. Fixed by Addendum 2 (primary set of 88 papers, verdicts read there; the 288 are secondary).

## 2026-11-04 18:10 Fresh test Addendum 2: primary set 88 papers (F4-noted, exact Full text, same-work removed), underpowered, verdicts on primary; 288 secondary
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: primary set chosen on label provenance (read label, F4 note, same-work) before any model answer; none exists
- II: n/a: no result yet; scorer prints b, c per pair
- III: n/a: no result yet
- V: holds: exact McNemar + accuracy, Holm 9 per family, A and A2 conjunction
- VI: holds: B PASS read as needing real answers only if the field replicates (item 8)
- R: holds: 88/264 and drop counts from yf_primary.py output (PRIMARY_SET.text); 688 rebuilt from list.json.pre-removal-20261102
- L1: n/a: no replies yet
- L2: holds: no rate exists
- L3: holds: yf_eval.py unchanged from Addendum 1
- L4: n/a: one machine
- L5: holds: labels by yr_data.truth unchanged; selection now matches yr_data (exact Full text)
- L6: holds: drops counted by reason in PRIMARY_SET.text
- L7: holds: labels from the List reader, disclosed as the same pass that saved the texts
- L8: holds: paired per paper
- L9: holds: KNOWN_GOOD.text saved, truth 1.000 / flipped 0.000 on both sets
- L10: holds: adapter hashes checked by the driver
- L11: n/a: no dataset substituted
- L12: holds: Sage (same model family as the writer) refereed; disclosed
- P1: n/a: the page quotes no source text
- P2: holds: 88 in PLAN_YO_FRESH_ADDENDUM2.md and PRIMARY_SET.text
- P3: holds: arms and seeds unchanged
- P4: holds: no cause named
- P5: n/a: no interval printed
- P6: holds: page says underpowered and planned, not run
- P7: holds: ledger, then ship.sh
- P8: cannot tell: checked after ship
- P9: holds: plain sentences
- P10: holds: the YES shares are stated as label counts, not as what the papers print

## 2026-11-05 02:55 YO fresh test read: REQUEST replicates (primary+sensitivity, 3/3) and needs the real labels (B 3/3); DATES depends on 4 labels; LINK not shown
packs: L
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: comparators (always-NO, best constant from the fresh labels themselves, self-label, shuffled) and all sets fixed in A3-A12 before the read; unread 0 in every arm, so the gate drops nothing
- II: holds: b/c per seed printed, no pooling; REQUEST b 10-11 c 0 vs always-NO each seed; DATES seeds split (seed 63 vs always-NO Holm 0.068 on sensitivity), printed as depends on 4 labels
- III: holds: REQUEST positive in A, A2, B on all 3 seeds; LINK vs best constant straddles zero (-0.034 to +0.024), no sign claimed
- V: holds: stamped exact McNemar + Holm beside post-hoc Clopper-Pearson paired widths in BOUNDS_POSTHOC.text, labelled defined after the data
- VI: holds: REQUEST ABOVE (lower bound +0.044 vs best constant, +0.108 vs self-label); LINK CONSISTENT bound [-0.126,+0.106], reaches the size that matters so CANNOT_TELL on usefulness; DATES CANNOT_TELL (depends on 4 labels); REQUEST rests on 12 YES items of 88
- R: holds: counts from results_fresh_*.json via stamped scorer sha 26194d1a; A8-A12 block 974635 07:19:14Z from preflight GO
- L1: holds: parse() read; all 7776 replies across 9 arms are exactly YES or NO, at most 2 distinct strings per arm, parser maps each correctly
- L2: holds: distinct-reply table run before any scorer; no log tail or results file opened before it
- L3: holds: one prompt format, one harness (yf_eval.py), one extraction rule for all 9 adapters; comparators are constants with no setup
- L4: n/a: one machine, one run per adapter; the three seeds are the spread and are printed separately
- L5: holds: scored by our stamped scorer on our files, keys paper|q matched by id
- L6: holds: unread 0 of 864 per arm; shuffled 72 answered NO to all 864, a constant reader counted as is
- L7: holds: gold is the List reader F4 notes and YO trained on that reader's labels; claim worded as agreement with that reader as parsed, not truth
- L8: holds: paired exact McNemar per seed, three seeds reported apart, no batch or position effects in a single-token reply
- L9: holds: prompts are numbered paper sentences plus the question; 0 of 264 primary prompts carry an answer line
- L10: holds: adapters pinned by sha in RUN_MANIFEST.txt, base Qwen3-1.7B local, one mlx build
- L11: n/a: no dataset or tool substituted; items fixed and stamped in Addendum 3
- L12: holds: List reader labels and referee Sage are the same model family as the writer; disclosed on the page
