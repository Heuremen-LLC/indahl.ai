#!/bin/sh
# layout.sh: builds work/ with the folder names pairs.py expects, from this release and the Pub #2 release beside it (../pub2).
# Run from this folder: sh layout.sh && python3 -I work/pub3_serving/pairs.py
set -e; cd "$(dirname "$0")"; rm -rf work; mkdir -p work/faultsbench2/out work/pub3_serving
cp mac_builds/score.py mac_builds/items.json mac_builds/items.py work/faultsbench2/
ln -s ../../../pub2_mac_phi4mini work/faultsbench2/out/phi4-mini
ln -s ../../pub2/faultsbench2_mac_cross work/faultsbench2_mac_cross
ln -s ../../pub2/faultsbench2_armature work/faultsbench2_armature
ln -s ../mac_builds work/faultsbench2_mac_builds
ln -s ../armature_slots work/faultsbench2_armature_1slot
cp pairs.py work/pub3_serving/pairs.py
echo "work/ ready"
