#!/bin/bash
# drive.sh: the four sessions of PLAN.md in order, one at a time (queue job). Stops on the first failure.
set -eo pipefail; cd "$(dirname "$0")"; PY=${PY:-python3}
for s in "qwen15 1" "qwen15 2" "phi35 1" "phi35 2"; do $PY -I run_live.py $s 2>&1 | grep -v -i warning; done
echo "ALL SESSIONS IN"
