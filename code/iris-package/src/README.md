# IRIS Research Package

Heuremen LLC · https://indahl.ai/iris

Tools to check the numbers from a language-model evaluation before you trust them and after a run. This applies to benchmark scores, LLM-as-judge scores and fine-tuning studies. IRIS recounts published evaluation studies from their own released output files, and this package puts the same checks in your hands for your own outputs. Your files are opened read-only and never changed. Reports go to a separate folder. The checker sends nothing anywhere. Two parts need other software or the network when you run them: `parser-check/handcheck.py` runs a model on your machine, and installing the Faults and Guards package from PyPI downloads it. Python 3.9 or later.

## Before a run

1. Read the Guards before the work. Install the package with `pip install faultsguards` or from the wheel in `faultsguards/`, then run `python -m faultsguards guards`
2. Decide how each answer will be extracted from a reply and write that rule down before any reply exists.
3. If you fine-tune or compare systems, plan at least two runs of the same items with the same settings. The difference between those two runs is the repeat floor, and it is the first thing any later difference is read against.
4. Give the plan a check block: `check-block/`. The packs for language-model evaluations and public copy are in `check-block/SPEC.md`.

## After a run

1. Save the outputs of each run as a JSONL file with one reply per line. Each line needs an item id, the reply, what your parser extracted and whether it was scored correct. Keep these files in one folder and write reports to a different folder.
2. Read a sample of replies beside what your parser extracted:
   `python iris_check.py sample run1.jsonl --reply-field reply --extracted-field pred --label-field family --id-field id -n 10 --seed 1`
   This writes a reading sheet as HTML and CSV with 10 random replies per label. Read the replies. Write x in the misparsed column of the CSV for each reply where the extracted value is not the answer the reply gives. Then run `python iris_check.py sample --tally SHEET.csv`. Our rule: if more than 1 of 10 is mis-parsed, that label's rate is "cannot tell (parser)".
3. Count the flips between repeats of the same items:
   `python iris_check.py repeat run1.jsonl run2.jsonl --id-field id --correct-field correct`
   The report counts items that went right to wrong and items that went wrong to right, between every pair of runs, and gives the repeat floor as the share of items that flip. The net change alone hides flips that cancel.
4. Compare two systems on the same items:
   `python iris_check.py repeat a_run1.jsonl a_run2.jsonl --vs b_run1.jsonl b_run2.jsonl --id-field id --correct-field correct --margin 0.02`
   Runs are paired by item id. Each pair of runs gets an exact two-sided McNemar test on the discordant items and a bootstrap 95% interval for the accuracy difference A minus B. The outcome is one of four. ABOVE if the low end of the interval is above 0. BELOW if the high end is below 0. CONSISTENT if the whole interval is within plus or minus the margin. CANNOT_TELL otherwise.
5. Read your write-up against the Faults: `python -m faultsguards faults`
6. Give each reading a check block before it goes in a paper or a page: `check-block/`

## Test the checker

`python tests/make_synthetic.py` writes a synthetic dataset where the answers are planted. These are the flips between repeats, the discordant items between systems and the parser errors. `python tests/test_iris_check.py` runs the checker on it and asserts that the planted answers come back.

## What is here

- `iris_check.py`: the sample and repeat checks, standard library only
- `START_HERE.html`: this guide as a page
- `tests/`: the synthetic dataset and the tests
- `faultsguards/`: the Faults and Guards as a Python package, with the PDFs
- `check-block/`: the check block and its commit gate
- `faultsbench/`: the scorer and the planted items of our Faults and Guards bench, with the synthetic check that runs the scorer on planted worlds. The prompts and the runner are in the repository: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris/faultsbench
- `parser-check/`: `handcheck.py` regenerates replies from an lm-evaluation-harness task and writes each reply beside what each filter extracted, so the replies can be read in full. It needs `pip install mlx-lm lm-eval` on Apple silicon.
- `LICENSE.txt`, `CITATION.cff`

Our other IRIS code, such as the round scorers, the training scripts and the run drivers, is in the repository at https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris and is not copied here because it depends on our own folders and data.

## Links

- IRIS: https://indahl.ai/iris
- List of studies: https://indahl.ai/iris/list
- Key: https://indahl.ai/iris/key
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Faults and Guards on PyPI: https://pypi.org/project/faultsguards/
- Data and models: https://huggingface.co/indahl

## Terms

Free to download, run and cite with attribution to Heuremen LLC and https://indahl.ai/iris

Your results remain yours. Use of this package's text or data to train, fine-tune or build AI models is not permitted. See LICENSE.txt.
