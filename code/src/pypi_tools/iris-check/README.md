# iris-check

Heuremen LLC · https://indahl.ai/iris

Tools to check the numbers from a language-model evaluation before you trust them and after a run. This applies to benchmark scores, LLM-as-judge scores and fine-tuning studies. IRIS recounts published evaluation studies from their own released output files, and this package puts the same checks in your hands for your own outputs. Your files are opened read-only and never changed. Reports go to a separate folder, and the checker refuses a folder inside the folder that holds an input, so run it from outside your data folder. The checker sends nothing anywhere. Two parts need other software or the network when you run them: `parser-check/replycheck.py` runs a model on your machine, and installing the Faults and Guards package from PyPI downloads it. Python 3.9 or later, standard library only.

## Install

```
pip install iris-check
```

The tool is the command `iris-check`. It is also importable as the module `iris_check`.

## Before a run

1. Read the Guards before the work. Install the package with `pip install faultsguards`, then run `python -m faultsguards guards`
2. Decide how each answer will be extracted from a reply and write that rule down before any reply exists.
3. If you fine-tune or compare systems, plan at least two runs of the same items with the same settings. The difference between those two runs is the repeat floor, and it is the first thing any later difference is read against.
4. Give the plan a check block. The check block and its packs for language-model evaluations (L) and public copy (P) are in the full package at https://indahl.ai/iris/package

## If your file holds raw replies only

`iris-check repeat` needs a correctness field for each item, so score first. A few lines of Python are enough. This one reads a JSONL file of replies and a dictionary of gold answers, and writes the `{"id", "correct"}` lines the checker reads. Replace the comparison with your own extraction rule. Write `"correct": null` for an item you did not score, and it is counted as unscored and kept out of the drop warning.

```
import json
gold = {"q1": "B", "q2": "17"}   # item id -> the right answer
with open("replies.jsonl") as f, open("scored.jsonl", "w") as out:
    for line in f:
        r = json.loads(line)
        correct = r["reply"].strip().split()[-1] == gold[r["id"]]   # your own extraction and comparison
        out.write(json.dumps({"id": r["id"], "correct": correct}) + "\n")
```

## After a run

1. Save the outputs of each run as a JSONL file with one reply per line. Each line needs an item id, the reply, what your parser extracted and whether it was scored correct. Keep these files in one folder and write reports to a different folder.
2. Read a sample of replies beside what your parser extracted:
   `iris-check sample run1.jsonl --reply-field reply --extracted-field pred --label-field family --id-field id -n 10 --seed 1`
   This writes a reading sheet as HTML and CSV with 10 random replies per label. Read each reply. In the CSV, write x in the `read` column for every reply you read. In the `misparsed` column write x, bad, 1, wrong or misparsed where the extracted value is not the answer the reply gives. A parse that is fine takes ok, fine, 0, no, n, false or a blank. Any other entry is an error that names the row. That includes yes and y, which could mean either. Keep the `sample_....json` record beside the CSV. Then run `iris-check sample --tally SHEET.csv`, which prints the result for each label and writes its report to `./heuremen_report_tally` unless you give `--out`. The record is found by the sheet's file name, the same name ending in `.json`, so keep the two files together and do not rename one. If the record has another name or place, add `--record sample_....json`. The CSV is written as UTF-8 with a byte order mark so Excel shows accents. If you save it again from Excel, choose "CSV UTF-8". A file saved in the Windows code page is refused with that instruction.
3. The tally rule, exactly: a label reads "cannot tell (rows missing)" if the sheet holds fewer rows for it than the sample record says. Otherwise it reads "cannot tell (not read)" if any of its rows is unread. Otherwise it reads "cannot tell (parser)" when more than 10% of its read rows are mis-parsed, so 1 of 10 is fine, 2 of 10 is not, and 1 of 9 is not. Otherwise the rate can be read. The default sample is 10 replies per label.
4. Reply text that starts with `=`, `+`, `-` or `@` gets a single quote in front of it in the CSV, so a spreadsheet does not run it as a formula. The `--extracted-field` should hold the extracted answer itself, not a scorer's verdict such as OK or FAULT, because the reader compares it with the reply. Items your scorer excludes by design should be set to JSON null in the extracted field, or left out of the file before you sample, so the reader is not shown them as parse failures. Rows where the reply or extracted field is absent or JSON null, blank lines, and rows with a missing or null label (shown as `(none)`) are counted on the console and in the JSON report. The tally takes the quote off again.
5. Count the flips between repeats of the same items:
   `iris-check repeat run1.jsonl run2.jsonl --id-field id --correct-field correct`
   Item ids are turned into strings first, so 2, 2.0 and "2" are one id. Each pair of runs is compared on the items both runs hold. For every pair the output first gives the flip count, as `flips N: right->wrong a, wrong->right b, of n matched`, and then the share of matched items that flip. The share is called "flip share between these runs". It is called the "repeat floor" only when you add `--repeats`, which says that the runs are repeats of the same setup (same model, same settings, same machine). The net change alone hides flips that cancel. With three or more runs there is no combined figure, you get one row per pair of runs.
   One file should hold one model, or the model should be part of the id. If a file pools several models whose item ids repeat, give every field that makes an item unique, for example `--id-field model id`, and the fields are joined into one id. When repeated ids leave no matched items, the output says so in plain words and names this fix. The command exits with status 1 and says why whenever a comparison matches no items.
6. The report lists, for each run, how many rows were left out and why, with up to 5 example ids. Each row is counted once, under the first reason that applies, in this order: id missing, correctness field missing, correctness field explicitly null (unscored), correctness value not accepted, duplicate id. Unscored rows (null correct) are reported on their own and are not counted as errors in the 5% warning. A duplicate id leaves out every row that holds it, and duplicate rows and duplicate ids are counted separately. The console prints rows read = usable + the reasons. The correctness value is accepted as true or false, as the numbers 1 and 0 (1.0 and 0.0 too), or as text in any case: true, t, yes, y, correct, 1 or false, f, no, n, incorrect, 0. The report also lists the items present in one run of a pair and not the other. If more than 5% of a run is left out of a comparison, a warning is printed on the console and shown at the top of the report. It always names the count of ids not in the other run, next to the in-file reasons.
7. Compare two systems on the same items:
   `iris-check repeat a_run1.jsonl a_run2.jsonl --vs b_run1.jsonl b_run2.jsonl --id-field id --correct-field correct --margin 0.02`
   Run k of A is paired with run k of B, in the order given on the command line. Each pair gets an exact two-sided McNemar test on the discordant items and a bootstrap 95% interval for the accuracy difference A minus B. The number of matched items and the discordant counts are always printed. Both the interval and the McNemar p are used, in this order. ABOVE if the low end of the interval is above 0 and p is below 0.05. BELOW if the high end is below 0 and p is below 0.05. If only one of the two says different, CANNOT_TELL. Then CONSISTENT if the whole interval is within plus or minus the margin, but only with at least 20 matched items and at least 1 discordant item. Otherwise CANNOT_TELL. Because ABOVE and BELOW are checked before CONSISTENT, a small difference that is resolved reads ABOVE or BELOW even when it is inside the margin. Above 5000 matched items the interval uses count draws (two binomial draws per resample) instead of resampling items one by one. It is approximate and can differ slightly by Python version, because before Python 3.12 it uses a normal approximation. A p below 1e-300 is printed as <1e-300.
8. Read your write-up against the Faults: `python -m faultsguards faults`
9. Give each reading a check block before it goes in a paper or a page. The check block is in the full package.

## Test the checker

The source distribution holds `tests/` with a synthetic dataset where the answers are planted. These are the flips between repeats, the discordant items between systems and the parser errors. Unpack the source distribution and run `python tests/make_synthetic.py` and then `python tests/test_iris_check.py`, with `iris_check.py` and `tests/replycheck.py` copied into the folder that holds `tests`. How the package was tested is in TESTED.md, installed under `share/doc/iris-check/`.

## The rest of the IRIS package

The full package adds the Faults and Guards package, the check block, FaultsBench and the parser-check script. It is at https://indahl.ai/iris/package

## Links

- IRIS: https://indahl.ai/iris
- List of studies: https://indahl.ai/iris/list
- Key: https://indahl.ai/iris/key
- Package page: https://indahl.ai/iris/package
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Faults and Guards on PyPI: https://pypi.org/project/faultsguards/
- Data and models: https://huggingface.co/indahl

## Terms

Heuremen LLC permits anyone to run, copy and change the code in this package, for any purpose, with attribution to Heuremen LLC and https://indahl.ai/iris

Your results remain yours. The text and data follow LICENSE, and their use to train, fine-tune or build AI models is not permitted. The Faults and Guards package and its PDFs keep their own terms. LICENSE covers only the files in this package.
