# BIGQUERY: our public tables, loaded from the files already in our public repository. Plan, written before the first load.

## What it does
Every few hours a script loads the trend history of each live page, the current rows of STACK, the hash chain of our records and the queue readings into one public BigQuery dataset, so anyone with a Google account can query our data with SQL. Nothing is loaded that is not already in the public repository at github.com/Heuremen-LLC/indahl.ai. The loader changes no number. Column names are made legal for BigQuery by turning each dot in a name into two underscores, and every other illegal character into one underscore. Nothing else about a row is changed.

## Tables (fixed now)
- history_SLUG: one table per live page, read from code/SLUG/history.jsonl in the public repository, replaced whole at each load.
- tests_history: one row per test per load, from the STACK feed (page, test, compared, failed, share, interval, outcome, load time). Appended. Rows already loaded are never rewritten.
- archive_chain: the hash chain of our records (code/archive/chain.jsonl), replaced whole.
- qia_queue_history: the hourly pending counts per IBM processor, replaced whole.
Each table has a description that names its source file and plan. The dataset description carries our terms: free to read, run and cite with attribution; use to train machine learning models is not permitted.

## Access
The dataset is readable by any signed-in Google account. A reader's own queries are billed to the reader's own project, within Google's free tier for most uses. Nothing in the dataset is writable by anyone but us.

## Known-good
After each load the row count of every table is read back and compared with the line count of its source file (history and chain tables) or with the number of tests in the STACK feed (appended rows for that load). A table that does not match is reported and the load is marked failed. The first load must make the table history_time have the same rows as code/time/history.jsonl.

## Limits stated
The BigQuery sandbox, which needs no card, expires tables after 60 days unless billing is enabled. Replaced tables are refreshed at each load. The appended table tests_history carries rows for 60 days in the sandbox. The dataset mirrors files that already exist in public, and the repository stays the record.

## Not claimed
That the dataset is complete for every number on the site. It holds trend history, current tests, the chain and the queue readings. A page's full tables are on the page and in its feed.

## Addendum 1 (29 Oct, after the first load)
- Setup: the project heuremen-llc-data sits inside the heuremen.com organization, whose default rule allows only organization accounts in access lists. Public read by any signed-in Google account was refused until that rule was set to allow all on this one project (the organization rule is unchanged). The project holds only data already public in the repository.
- The queue table is named history_qia_queue (from code/qia-queue/history.jsonl), not qia_queue_history. All other table names are as above.
- First load result: 22 tables, every row count read back equal to its source file, tests_history appended 20 rows for the load. Check passed.
- The loader runs on the tick bus every 36 ticks.
- Dataset address: heuremen-llc-data.heuremen_public.
