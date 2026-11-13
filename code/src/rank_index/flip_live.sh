#!/bin/bash
set -e
cd ~/bones-forge
for k in hs elem middle nu nlac mba law eng edu med; do
  python3 ledger/ledger.py set rank.list.$k --field status --to live --why "RANK page in build_site.py, shipped in this ship step" --evidence rank_index/CHECKS.md
done
