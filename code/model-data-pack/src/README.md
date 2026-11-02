# MODEL Data Pack

Heuremen LLC · https://indahl.ai/hermes/model

The data behind the MODEL page at https://indahl.ai/hermes/model, as files you can open in a spreadsheet or Python. MODEL sets what AI hardware vendors state about their systems next to the results MLCommons publishes. Each file comes as the page publishes it, and each JSON file also comes as CSV with one row per record. The statements were fetched and compared on {FETCHED}, the files were built on {BUILT}, and the MLCommons files were retrieved on 28 October 2026. Vendor pages and MLCommons files change, so a later read can differ.

## What is in each file

Statements and outcomes (`json/claims.json`): {N_CLAIMS} statements from {N_SOURCES} sources, each with an outcome of ABOVE, BELOW, CONSISTENT or CANNOT_TELL. The file has a `summary` entry and a `claims` list. The rows come as `csv/claims.csv`. The columns are `id`, `vendor`, `source_key`, `statement`, `verbatim`, `compared`, `stated`, `in_file`, `outcome`, `note`, `label_mismatch` and four columns that start with `source_`, which hold the title, address, fetch date and round of the page the sentence comes from. The `id` repeats between sources, so a row is named by `source_key` and `id` together. The `statement` column holds the sentence as published, without quotation marks. The page puts it in quotation marks when `verbatim` is true. The `compared` column names the MLCommons entries the statement points to, such as 5.1-0072, and the `in_file` column gives what the files show. In {N_LABEL} rows `label_mismatch` is true, and the `in_file` text of those rows says how the label in the file differs from the label in the statement. For those rows the page adds one sentence to the note, which reads: The entry named in the post is listed in the file with a different accelerator or model.

The summary comes as five more files. `csv/claims_sources.csv` has one row per source with its vendor, title, address and round. `csv/claims_tally.csv` has the number of statements per source and outcome, and a blank means none. `csv/claims_vendor_page_hash.csv` has the SHA-256 of the vendor page as we read it. `csv/claims_mlcommons_files.csv` has the address, SHA-256 and row count of each MLCommons inference file we used. `csv/claims_meta.csv` has the remaining summary fields as key and value, such as the build date and the commits of the training and storage repositories.

Results by accelerator (`csv/accelerators.csv` and `json/accelerators_summary.json`): {N_ACC_ROWS} closed-division datacenter throughput results from MLPerf Inference v5.0, v5.1 and v6.0 that have an accelerator count, in {N_GROUPS} groups of version, model, scenario and accelerator. The `per_accelerator` column is `result` divided by `total`, which is our own computation and not an MLPerf primary metric. The summary file gives the number of submissions and submitters, the minimum, median and maximum, and the entry with the highest value for each group. `csv/accelerators_summary.csv` holds the same groups as CSV. The page states which rows are left out and why.

Storage results (`json/storage_v30_results.json`): {N_STORAGE} rows that aggregate the MLPerf Storage v3.0 result files into one row per system and workload, where for training the value is the mean of the runs after the first, as `csv/storage_v30_rows.csv`, with the source and licence in `csv/storage_v30_meta.csv`. Rows for different workloads have different measurement columns, so a column is blank where the workload has no such measurement.

Readings from our unit (`json/mac_run.jsonl`): {N_MAC} lines of memory bandwidth readings from the MacBook Pro 14-inch with M5 Max that the Apple table on the page uses. Each line has a `kind`. They come as `csv/mac_run.csv`, where a column is blank for a line of another kind.

## Sources and dates

SOURCES.md lists the upstream sources, their links, their terms and the dates found in the data. NOTICE.txt carries the MLCommons attribution and trademark lines. The statements were fetched on {FETCHED}. The MLCommons files were retrieved on 28 October 2026. Every row of `csv/claims.csv` carries the address of the page its sentence comes from and the date it was fetched.

## How to open the files

Spreadsheet: open any file in `csv/`. The files are UTF-8, and the ones we wrote carry a byte order mark so Excel reads names correctly. Empty text and missing values are both shown as blank cells. The file `csv/accelerators.csv` is the published file without a byte order mark.

Python, standard library only:

```
import json, csv
claims = json.load(open("json/claims.json", encoding="utf-8"))["claims"]
rows = list(csv.DictReader(open("csv/claims.csv", encoding="utf-8-sig")))
acc = list(csv.DictReader(open("csv/accelerators.csv", encoding="utf-8-sig")))
```

Check the pack with `python verify.py`. It recounts the rows of every file, compares every CSV cell with the JSON, recomputes the outcome counts of each source from the statements, and recomputes every group in `accelerators_summary.json` from the rows of `accelerators.csv`.

## What is here

- `json/`: the original files from the MODEL data folder, unchanged
- `csv/`: one CSV for each table, plus the `_meta.csv` files, and the published `accelerators.csv`
- `SOURCES.md`: upstream sources, links, terms and dates
- `TESTED.md`: what the files were opened with and what was compared
- `NOTICE.txt`: MLCommons attribution and trademark lines, and the terms of each source
- `LICENSE.txt`: terms by file
- `APACHE-2.0.txt`: the Apache License 2.0, which covers the MLCommons results
- `verify.py`: recounts and compares the files
- `START_HERE.html`: this guide as a page
- `CITATION.cff`

## Links

- MODEL: https://indahl.ai/hermes/model
- Papers table: https://indahl.ai/hermes/model/papers
- Code: https://github.com/Heuremen-LLC/indahl.ai
- MLCommons: https://mlcommons.org
- MLPerf results messaging guidelines: https://github.com/mlcommons/policies/blob/master/MLPerf_Results_Messaging_Guidelines.adoc
- Correction or removal form: https://indahl.ai/correction

## Notes on the data

The files in `json/` are the files the MODEL page links, unchanged. The page also links the scripts that recompute each row from the MLCommons files, and those scripts are not in this pack. They are in the code folder at https://github.com/Heuremen-LLC/indahl.ai.

The papers table on the MODEL papers page and the live model-claim rounds are not in this pack. The papers table has no data file, and the live rounds are a feed that the page reloads every 30 seconds.



## Terms

Each part of this pack keeps the terms of its source, and LICENSE.txt gives them by file. The MLCommons results are published by MLCommons Association under the Apache License 2.0, and the Apache text is included. MLPerf and MLCOMMONS are trademarks of MLCommons Association. The per-accelerator values, ratios and percentages here are our own computations and are not verified by MLCommons Association. The sentences quoted from vendor pages belong to the pages named in each row. To correct or remove a row, use https://indahl.ai/correction. It is open to anyone, and we acknowledge every request within three business days.

Heuremen LLC permits anyone to use, copy and change its own parts with attribution to Heuremen LLC and https://indahl.ai/hermes/model. For its own text (the README, SOURCES.md, NOTICE.txt, LICENSE.txt, TESTED.md, START_HERE.html and the `compared`, `in_file`, `outcome` and `note` columns of the claims files) that permission does not include use as AI training data. Its reservation against text and data mining and AI training covers that text only and does not apply to the MLCommons results or to the sentences quoted from the sources.
