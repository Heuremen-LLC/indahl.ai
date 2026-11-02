# Sources

Heuremen LLC · https://indahl.ai/hermes/model

Each entry gives the upstream source as the MODEL page and the data files state it, with the dates found in the data. The descriptions follow https://indahl.ai/hermes/model.

## MLCommons results

- MLPerf Inference v5.0, v5.1 and v6.0, datacenter and edge suites, closed and open divisions, as published by MLCommons Association in `summary_results.json` of the repositories `inference_results_v5.0`, `inference_results_v5.1` and `inference_results_v6.0` at https://github.com/mlcommons, retrieved 28 October 2026. Terms: Apache License 2.0, as the page states. The repository `inference_results_v5.0` has no LICENSE file in its root on 2026-11-01, and the page states Apache-2.0 for it. The other repositories listed here have a LICENSE.md with the Apache License 2.0.
- MLPerf Inference v6.1 in `summary.json` of the repository `inference_results_v6.1`, retrieved 28 October 2026. Terms: Apache License 2.0.
- Rows and SHA-256 of the files we used, as the page states them and as `csv/claims_mlcommons_files.csv` gives them in full: v5.0 {ROWS_V50} rows, v5.1 {ROWS_V51} rows, v6.0 {ROWS_V60} rows, v6.1 {ROWS_V61} rows.
- MLPerf Training v5.0, v5.1 and v6.0, as published in the result logs of the repositories `training_results_v5.0`, `training_results_v5.1` and `training_results_v6.0` at https://github.com/mlcommons, retrieved 28 October 2026. Terms: Apache License 2.0. The commits and the numbers of result sets are in `csv/claims_meta.csv`. Training times on the page are recomputed from run start and run stop in each log, with the olympic average and review-committee scaling factors that the MLCommons result summarizer applies.
- MLPerf Storage v3.0, as published in the repository `storage_results_v3.0` at https://github.com/mlcommons/storage_results_v3.0, retrieved 28 October 2026. Terms: Apache License 2.0, as `json/storage_v30_results.json` states in its `licence` entry. The commit and the number of result rows are in `csv/claims_meta.csv`.
- How results may be reused: the MLPerf Results Messaging Guidelines at https://github.com/mlcommons/policies/blob/master/MLPerf_Results_Messaging_Guidelines.adoc and the policies listed at https://mlcommons.org/policies/. NOTICE.txt gives the attribution and trademark lines.

## Vendor and other statements (json/claims.json)

- Each row of `csv/claims.csv` quotes a sentence from one source page or document. The title, address, fetch date and round of that source are in the `source_` columns of the row and in `csv/claims_sources.csv`. All sources were fetched on {FETCHED}. The SHA-256 of each vendor page as we read it is in `csv/claims_vendor_page_hash.csv`.
- The sources are web pages and PDFs of the vendors and of MLCommons, and one source is the test output of a software project. The Apple table compares the Apple specification page with readings from our own unit.
- The sentences belong to the owners of those pages. They are quoted so that each statement can be set beside the published results, and each row names its source. The terms of each page are its owner's.
- The columns `compared`, `in_file`, `outcome` and `note` are ours. The `compared` column names the MLCommons entries, and the `in_file` numbers are computed by us from the public MLCommons files.

## Results by accelerator (csv/accelerators.csv)

- Computed by us from `summary_results.json` of MLPerf Inference v5.0, v5.1 and v6.0 (Apache License 2.0). Closed-division datacenter results with an accelerator count and a throughput unit (tokens, samples or queries per second). The per-accelerator value is the result divided by the number of accelerators in the entry. Where an entry's accelerator name states its own count and the count differs from nodes times accelerators per node, the count in the name is used. The page lists the rows left out: no accelerator count {NOACC}, and given as a latency {LATENCY}, for v5.0, v5.1 and v6.0 in that order.
- Per-accelerator throughput is not an MLPerf primary metric.

## Readings from our unit (json/mac_run.jsonl)

- Memory bandwidth readings taken by us on 2026-10-28 on a MacBook Pro 14-inch with M5 Max. These are our own data. The scripts that took them are linked from the MODEL page.
