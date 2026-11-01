#!/bin/bash
# publish.sh: the one path to PyPI for the Heuremen LLC account. Run from anywhere: ~/bones-forge/faultsguards/tools/publish.sh
# Refuses unless: the working tree is clean and pushed, the tests pass, the version is not already on PyPI. Builds, checks, then uploads with twine.
# The token lives in ~/.pypirc (mode 600) and, for releases, in the GitHub secret PYPI_API_TOKEN. Neither is ever printed.
set -euo pipefail
cd "$(dirname "$0")/.."; V=$HOME/bones-forge/pypi_venv
[ -z "$(git status --porcelain)" ] || { echo "REFUSED: uncommitted changes"; exit 1; }
git fetch -q origin && [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "REFUSED: HEAD is not what is on origin/main (push first)"; exit 1; }
VER=$(python3 - <<'PY'
import re;print(re.search(r'^version = "([^"]+)"', open('pyproject.toml').read(), re.M).group(1))
PY
)
if curl -sf "https://pypi.org/pypi/faultsguards/$VER/json" >/dev/null; then echo "REFUSED: faultsguards $VER is already on PyPI (bump the version)"; exit 1; fi
python3 -I -m unittest discover -s tests >/dev/null 2>&1 || { echo "REFUSED: tests fail"; exit 1; }
rm -rf dist build; "$V/bin/python" -m build >/dev/null 2>&1; "$V/bin/twine" check dist/*
"$V/bin/twine" upload --non-interactive dist/* 2>&1 | sed -E 's/(password|token)[^ ]*/<hidden>/Ig'
echo "published faultsguards $VER: https://pypi.org/project/faultsguards/$VER/"
