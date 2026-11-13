#!/bin/bash
# run_petrol.sh: the whole PETROL refresh. Fetch (cached files are never re-fetched), parse, targets gate, analysis, page body, copy lint.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python
$PY fetch_momr.py 2020-05 "$(date +%Y-%m)"
$PY fetch_statements.py
$PY fetch_eia.py ${1:-}          # pass --refresh to re-pull the two EIA files
$PY parse_momr.py
$PY make_targets.py
$PY analyze_petrol.py
$PY build_page.py
$PY lint_copy.py
