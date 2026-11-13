# PETROL rider: how the desk refreshes

One command: `~/bones-forge/petrol_index/run_petrol.sh` (add `--refresh` to re-pull the two EIA files). Standard library plus the desk venv (.venv, pymupdf and xlrd). No key, no login. Cached raw files are never re-fetched, so a run with nothing new costs seconds.

## Cadence on the tick bus
- Weekly rider, Thursday after the Wednesday EIA release: `run_petrol.sh --refresh`. This re-pulls the weekly and monthly EIA files (about 200 KB) and rebuilds Part 2. EIA updates the monthly file near the end of each month, the weekly file every Wednesday.
- Monthly rider, 13th to 16th of each month (MOMR lands in the middle of the month): `run_petrol.sh`. fetch_momr.py tries the current month and logs the answer in data/raw/momr_fetch_log.json. A 403 or 404 means the issue is not out yet. No retry loop. Try again on the next tick of the same rider, at most once a day, and stop after the issue is in.
- Output the rider reads: summary_petrol.json (field "updated"), petrol_headline.json (big and line), petrol_body.html, petrol_part1_rows.csv, petrol_part2_rows.csv. The run exits non-zero if any gate fails or the PLAN.md hash differs from data/plan_seal.json, and in that case no page is written.

## Headline rider (for watch/headlines.py, written in the style of census())
```
def petrol():
    import sys as _s; _s.path.insert(0, B + '/petrol_index'); from petrol_headline import headline
    import json; big, line = headline(json.load(open(B + '/petrol_index/summary_petrol.json'))); add('petrol', big, line)
```
(headline.py owns nothing here, this is a draft for whoever edits it.)

## What does not refresh by itself
1. Required production tables. They are images in OPEC statements. New monthly tables must be read by eye into make_targets.py (dict T) and the slug and image id added to fetch_statements.py, then the arithmetic gate in make_targets.py must pass. Until then those months read CANNOT_TELL, no target table transcribed. fetch_statements.py lists the pages to look at.
2. The window. PLAN.md fixes November 2024 to October 2026 for Part 1. A new month needs a dated amendment to PLAN.md, a new seal (data/plan_seal.json) and a change of MON in analyze_petrol.py. The same goes for any change to the rulers. A changed plan with an old seal stops the run on purpose.
3. The width baseline (revisions up to the October 2024 issue, EIA 2015 to 2019) is fixed by the plan and does not move.
4. The January 2027 OPEC+ levels will need the next ministerial table. The 42nd ONOMM is on 29 November 2026.
