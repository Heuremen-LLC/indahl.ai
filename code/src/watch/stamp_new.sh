#!/bin/zsh
# stamp_new.sh NAME FILE... (8 Nov, after the A3/A4/A5 name collision): writes SHA256SUMS_<NAME> over FILE... and OTS-stamps it.
# REFUSES if SHA256SUMS_<NAME> or its .ots already exists (never overwrite a stamped record), and exits non-zero if the stamp fails.
set -e; N=SHA256SUMS_$1; shift
[ -e $N ] && { echo "REFUSED: $N exists (pick a new name)" >&2; exit 3; }
[ -e $N.ots ] && { echo "REFUSED: $N.ots exists (pick a new name)" >&2; exit 3; }
shasum -a 256 "$@" > $N
# 13 Nov 2026 (Wayfinder): no OpenTimestamps, no Bitcoin. The SHA256SUMS file is the record; commit and push it for an outside witness.
echo "$N written $(date -u +%H:%M:%SZ) (sha256 $(shasum -a 256 $N | cut -c1-16))"
