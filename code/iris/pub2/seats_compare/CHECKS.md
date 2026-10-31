
## 2026-10-30 09:18 Two machines, same model files (Pub #2 section): item flips vs repeat floors
packs: L,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is each machine against itself (bare vs bare_copy), same prompts, manifests identical (setups_20261030.json), same v2 scorer gates on both; drops by arm now printed (fixed today): 29 of 420 gated items unread in at least one run, 27 per run on each machine, so the gate drops evenly
- II: holds: item flips counted before any net, across 11 (bare) and 10 (copy) of 391 against repeat floors Mac 1 and CUDA 4; family rates netted only after (results.txt)
- III: holds: direction kept, 8 flips toward a fault on CUDA against 3, exact two-sided p 0.227, so the direction is cannot tell and the paper says so
- V: holds: two rulers side by side, family difference with interval (compare.py) and item flips against the repeat floor (item_flips.py); they disagree in kind (nets hold, items move) and both are printed
- VI: cannot tell: no size that matters was set before the runs; the widest family interval is llama P1 [+0.000, +0.269], so a gap that large is not ruled out; the paper says within widths, never equal; P3 is CANNOT_TELL on both machines (gate failed)
- R: holds: counts read from item_flips.txt and results.txt rerun 30 Oct; Ollama 0.34.2 Mac and 0.34.3 Armature, CUDA driver 610.88, scorer v2 b87a2b08; item flips labelled defined after the data
- L1: holds: faultsbench2_armature/HANDCHECK.md written 12:37:16 UTC, first compare.py run 12:37:21 UTC (session record), replies read by hand in the turns before
- L2: holds: same record, no family rate printed before the hand-check file; the v1 scorer gap was found by that hand-read
- L3: holds: Mac Apple GPU one slot, Armature RTX 3080 NUM_PARALLEL=4 with requests one at a time, both named in the paper
- L4: holds: bare_copy repeat on each machine is the floor; temperature zero and fixed seed per the table caption and setups file
- L5: n/a: our own runs, no released vendor files in this reading
- L6: fixed: unread counts per arm added to item_flips.txt (27 per run each machine); reason is scorer class not FAULT or OK
- L7: holds: scorer v2 is a fixed rule parser with keys written before the runs, not a model labelling its own output
- L8: holds: paired by item id across machines, repeat floor per machine; batch: CUDA server allowed 4 parallel but was sent one request at a time
- L9: holds: same committed bench items on both machines, so any leak is equal on both sides of this comparison
- L10: holds: models matched by file digest in the manifests, not by tag name
- L11: n/a: no dataset or tool substituted for this reading
- L12: holds: REFEREE_SEATS.md header says read-only Claude Sonnet instance, same family as the writer
- P1: n/a: the section quotes no one
- P2: holds: Table tab:seats and the text give counts out of 170 and 391, sources seats_compare/results.txt and item_flips.txt
- P3: holds: bare, bare_copy and guard are the bench's own arm names
- P4: holds: no cause named for the flips, direction stated as cannot tell
- P5: holds: family intervals are the scorer's per-family difference intervals, p is exact two-sided sign test, both named
- P6: holds: abstract says 42 to 71 percent identical bare-arm replies, about 3 percent changed vs floor 0.3 to 1 percent, nets within widths, which matches the files
- P7: n/a: paper not public yet; ledger rows go in before release (pub2 rows exist for other sections)
- P8: cannot tell: PDF not rebuilt since today's two edits; rebuild is on the referee pass list
- P9: fixed: the clause added today used a semicolon, replaced with a comma
- P10: holds: item-level flips and drop counts both say defined after the data
