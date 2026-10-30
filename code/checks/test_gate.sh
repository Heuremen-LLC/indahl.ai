#!/bin/sh
# Builds a throwaway repository and shows the gate refuse and pass, case by case. Leaves nothing behind.
HERE=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); cd "$T" && git init -q && sh "$HERE/install_hook.sh" >/dev/null
C() { git -c user.name=t -c user.email=t@example.invalid commit -q -m t >/dev/null 2>&1; }
say() { if [ "$1" = "$2" ]; then echo "ok    $3"; else echo "FAIL  $3 (exit $1, wanted $2)"; FAILED=1; fi; }
mkdir run1; echo 1 > run1/results_x.txt; git add run1/results_x.txt; C; say $? 1 "a results file with no CHECKS.md is refused"
python3 "$HERE/readcheck.py" new run1 --packs P --what "test reading" >/dev/null; git add run1/CHECKS.md; C; say $? 1 "an unanswered template is refused"
python3 - run1/CHECKS.md <<'PY'
import sys, re
p = sys.argv[1]; t = open(p).read()
t = re.sub(r'(?m)^- ([A-Z]+\d*): TODO \((.*)\)$', lambda m: '- %s: holds: checked %s by hand' % (m.group(1), m.group(2)[:40]), t); open(p, 'w').write(t)
PY
git add run1/CHECKS.md; C; say $? 0 "a complete entry passes"
echo 2 > run1/results_x.txt; git add run1/results_x.txt; C; say $? 1 "a changed reading without a new entry is refused"
READCHECK_SKIP="test" C; say $? 0 "a skip passes and is written to .git/readcheck_skips.jsonl"
echo n > notes.md; git add notes.md; C; say $? 0 "a file that is not a reading is not gated"
cd /; rm -rf "$T"; [ -z "$FAILED" ] && echo "all cases behave"
