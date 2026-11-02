# Tested

Heuremen LLC · https://indahl.ai/hermes/model

On 2026-11-01 the zip was unzipped into an empty folder and every CSV was opened with pandas 3.1.0 on Python 3.14 at default settings. The live MODEL page and its 74 source pages were fetched the same day and read with lxml 6.1 and Beautiful Soup 4. Every count and number below was compared with the live pages and matched, except the one note named further down.

- Live files: claims.json, accelerators_summary.json, storage_v30_results.json, mac_run.jsonl and accelerators.csv are byte for byte the files in the pack
- Statements: 531 rows in 74 sources, with 8 ABOVE, 51 BELOW, 368 CONSISTENT and 104 CANNOT_TELL, which are the sums of the source table on the page
- Source table: vendor, round and the four outcome counts of all 74 rows equal `claims.csv` recounted with pandas and `claims_tally.csv`
- Source pages: the sentence, compared, stated, in the file, outcome and note of all 531 statements, and the line N statements checked of each of the 74 pages
- Results by accelerator: 1,727 rows in 569 groups, 814 in v5.0, 493 in v5.1 and 420 in v6.0, and `per_accelerator` equals `result` divided by `total` in every row
- Left out rows: no accelerator count 49, 61 and 24, and latency units 6, 0 and 7, for v5.0, v5.1 and v6.0
- MLCommons files: rows 17,454, 1,448, 520 and 492 for v5.0, v5.1, v6.0 and v6.1, with the first 16 characters of each SHA-256 as the page prints them
- Training and storage: result sets 229, 201 and 185 with commits eabf23a07b2a, d7e703fccc1c and 441d65f4445c, and 144 storage result rows with commit 802035fe6580
- Known answer: entry 5.0-0001, llama2-70b-99, Offline, 33,928.1 tokens per second on 8 accelerators is 4,241.0125 per accelerator
- Known answer: the statement NVIDIA v5.1 C1 reads +45.2% and CONSISTENT, and 5.1-0072 over 5.1-0071 for DeepSeek-R1 Offline recomputes from `accelerators.csv` as 1.452

The id column repeats between sources, with 500 different values over 531 rows, so a row is named by `source_key` and `id` together, and that pair is unique.

The test found one note, Nebius Storage v3.0 with `id` NB11, worded differently in the published `claims.json` than on the page. The published file was corrected on 2 November 2026 to match the page, and this pack carries the corrected file.

For the rows with `label_mismatch` true, the page adds the sentence The entry named in the post is listed in the file with a different accelerator or model. to the note. The pack does not repeat it in the note column.

At default settings pandas reads a blank cell as missing. In `csv/claims_tally.csv` a blank means no statement with that outcome. No cell in any file is text that pandas reads as missing, such as NA or None.

The file `verify.py` compares every CSV cell with the JSON, recomputes the outcome counts of each source from the statements, and recomputes every group of `accelerators_summary.json` from `accelerators.csv`.

Not tested: Excel or LibreOffice, the scripts that recompute the rows from the MLCommons files, and a new download of the MLCommons files. The page prints the first 16 characters of each SHA-256 and the pack holds the full values, and those were compared, but the files were not downloaded again.
