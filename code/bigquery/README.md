# BigQuery dataset

Our trend histories, the hash chain and the STACK rows as SQL tables. Dataset: `heuremen-llc-data.heuremen_public`, readable by any signed-in Google account. Queries bill to your own project.

    bq query --project_id=YOUR_PROJECT --use_legacy_sql=false 'SELECT * FROM `heuremen-llc-data.heuremen_public.tests_history` LIMIT 10'

Free to read, run and cite with attribution. Use to train machine learning models is not permitted. Plan and loader: this folder.
