#!/bin/bash
# 8 Oct: BADSTACK only catches an import-level break. A replicate is broken just as badly by a stack that
# imports cleanly and differs from the run it replicates -- same numbers, not comparable, no warning.
cd "$(dirname "$0")"
a=$(cat tick1/stack.txt 2>/dev/null); b=$(cat tick2/stack.txt 2>/dev/null)
[ -z "$b" ] && { echo "tick2 stack not fetched yet"; exit 2; }
echo "tick1: $a"; echo "tick2: $b"
# the GPU name is allowed to differ (tick1 COMMUNITY, tick2 SECURE); the library versions are not
la=$(echo "$a" | awk '{print $1,$2,$3}'); lb=$(echo "$b" | awk '{print $1,$2,$3}')
[ "$la" = "$lb" ] && echo "MATCH on torch/transformers/peft -- the replicate is comparable" \
                  || echo "DIFFER: $la  against  $lb -- tick2 is NOT a clean replicate of tick1"
