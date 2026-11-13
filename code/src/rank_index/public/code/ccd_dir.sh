#!/bin/sh
# Download CCD directory (Urban Institute Education Data API) per state and year
UA="HeuremenRANK/0.1 (+https://indahl.ai/oy)"
OUT=$HOME/bones-forge/rank_index/public/files/nces
mkdir -p $OUT
for y in 2023 2024; do for f in 47 18 42 32 11 51 13 48 53 6; do
  url="https://educationdata.urban.org/api/v1/schools/ccd/directory/$y/?fips=$f"
  i=1
  while [ -n "$url" ] && [ "$url" != "null" ]; do
    curl -s -A "$UA" -m 300 -o $OUT/dir_${y}_fips${f}_p$i.json "$url"
    url=$(python3 -I -c "import json,sys;d=json.load(open(sys.argv[1]));print(d.get('next') or '')" $OUT/dir_${y}_fips${f}_p$i.json 2>/dev/null)
    i=$((i+1))
  done
done; done
