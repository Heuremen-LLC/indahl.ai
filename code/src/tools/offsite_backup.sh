#!/bin/bash
# Encrypted off-site copy: git bundles of every repo + ledger, book, notes, memory -> private release on Heuremen-LLC/backup-private. Key: ACCOUNTS/offsite-backup-key (never printed).
set -e; export PATH=/opt/homebrew/bin:/usr/bin:/bin; T=$(mktemp -d); D=$(date +%Y%m%d); cd ~/bones-forge; mkdir $T/bk
for g in $(ls -d */.git | sed 's#/.git##'); do git -C $g bundle create $T/bk/$g.bundle --all >/dev/null 2>&1 || true; done
tar -czf $T/bk/internal_$D.tar.gz ledger qia_leads ligera watch 2>/dev/null || true
tar -czf $T/bk/memory_$D.tar.gz -C ~/.claude/projects/-Users-heuremen memory 2>/dev/null || true
K=~/Documents/"Heuremen LLC"/ACCOUNTS/offsite-backup-key; cd $T; tar -czf bk.tar.gz bk
openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -pass file:"$K" -in bk.tar.gz -out bk_$D.tar.gz.enc
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$K" -in bk_$D.tar.gz.enc | gzip -t
gh release create backup-$D bk_$D.tar.gz.enc --repo Heuremen-LLC/backup-private --title "Encrypted backup $D" --notes "AES-256, key held offline." >/dev/null
# keep the newest 4 releases
gh release list --repo Heuremen-LLC/backup-private --limit 20 --json tagName --jq '.[].tagName' | tail -n +5 | while read t; do gh release delete "$t" --repo Heuremen-LLC/backup-private --cleanup-tag -y >/dev/null; done
echo "offsite: backup-$D uploaded"; rm -rf $T
