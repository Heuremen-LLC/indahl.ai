#!/bin/bash
# post_result.sh -- after the referee clears YO's test reading: panel result, LAB one-liner + collapse, ledger rows, open the reader gate, ship.
set -euo pipefail
Y="$HOME/bones-forge/yo"; B="$HOME/bones-forge"
mv "$Y/yo2_result.pending.json" "$Y/yo2_result.json"
python3 "$Y/yo2_publish.py"
echo "adapters/v2 $(shasum -a 256 $Y/adapters/v2/adapters.safetensors | cut -c1-16)" > "$Y/LIVE_READER_ON"
echo "YO result posted; reader gate open"
