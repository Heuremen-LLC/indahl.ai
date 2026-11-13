#!/bin/bash
# push_manifests.sh (13 Nov 2026): stampwatch blind-feed manifests (file, sha256, read time, counts only) and collector hashes pushed to
# the public plugins repo, so the series is outside-witnessed as it grows (plan v3). No snapshot content is pushed.
set -e
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
S=/Users/heuremen/bones-forge/stampwatch_blind; R=/Users/heuremen/bones-forge/claude-plugins; M=$R/plans/stampwatch/manifests
mkdir -p $M
cp $S/manifest.jsonl $M/hf_manifest.jsonl; cp $S/manifest_ckan.jsonl $M/ckan_manifest.jsonl 2>/dev/null || true
cp $S/models.json $M/hf_models.json; cp $S/ckan_datasets.json $M/ckan_datasets.json; cp $S/ckan_frame.json $M/ckan_frame.json 2>/dev/null || true
( cd $S && shasum -a 256 snap_hf.py snap_ckan.py push_manifests.sh ) > $M/collector_sha256.txt
cd $R
git add plans/stampwatch/manifests
git diff --cached --quiet && exit 0
git -c user.name="Heuremen LLC" -c user.email="noreply@indahl.ai" commit -qm "stampwatch: blind-feed manifests $(date -u +%Y-%m-%dT%H:%MZ)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q
