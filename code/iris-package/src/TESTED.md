# How this package was tested

Heuremen LLC · https://indahl.ai/iris

This page says what was run, on what, and what came out. It also says what was not tested.

## The unit tests

`python tests/test_iris_check.py` runs {TESTS} tests on a synthetic dataset in `tests/data/` where the answers are planted. The planted answers are the flips between repeats, the discordant items between two systems, and the parser errors. The tests check that those answers come back, and they also cover the exact test against a Fraction-based reference, a 1,000,000-item comparison, the row accounting, the tally rules, the CSV handling and the exit codes. The tests passed on Python 3.9, 3.12 and 3.14 on macOS.

## A real-data test

We ran the package on our own two-machine evaluation round of 29 and 30 October 2026. That round ran FaultsBench on five open models, on a Mac and on a CUDA machine, with two same-machine repeats of each (the bare run and its exact copy). We turned the saved replies into one line per item with an id and a correct field, using the scorer from that round. Items the scorer could not read have a null correct field. The ids were joined with the model name, so the five models sit in one file per run.

The repeat command gave these flip counts. The two same-machine pairs were run with `--repeats`, and the two across-machine pairs were run without it, because they are not repeats of one setup. Each pair is compared on the items both runs hold.

- Mac repeats: 1 flip, on 393 matched items
- CUDA repeats: 4 flips, on 393 matched items
- Mac against CUDA, bare runs: 11 flips, on 391 matched items
- Mac against CUDA, copy runs: 10 flips, on 391 matched items

These equal the counts we published from separate code, the script `item_flips.py` and its output `item_flips.txt`, which are in the repository at https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris/pub2/seats_compare and give flips 1, 4, 11 and 10 on the 391 items that all four runs hold. The two same-machine pairs hold 393 items each, and the 2 extra items have no flips. Both programs were written by us. So the agreement shows that the two implementations agree. It is not a check by anyone else.

The comparison command (`--vs`) on the Mac bare run and the CUDA bare run read CANNOT_TELL at the default margin of 0.02, with an exact two-sided McNemar p of 0.2266. The published value is 0.227.

## A reading sheet on real replies

We wrote a reading sheet from real replies of the same round and a reader read 30 of them in full beside what the parser had extracted. 29 of the 30 extractions were correct. The one that was not was an item the scorer excludes by design.

## What was not tested

- Output formats of other harnesses, such as lm-evaluation-harness and HELM. The package reads a JSONL file with the fields you name, and nothing more was tried.
- Files of more than 100,000 items on real data. The speed test with 1,000,000 items uses synthetic data.
- Windows and Linux. The tests ran on macOS.
- `parser-check/replycheck.py` runs a model, and only its `--help` and its argument handling are tested here.
