#!/bin/zsh
# TRIPLE PASS seat A: build a sandbox to re-run the frozen release readers on the raw jobs, read-only.
# Inputs are SYMLINKED file by file (run*_meta.json, run*_results.npz only: names no reader writes); every directory a reader
# can write into is a REAL directory inside this sandbox. Reader scripts are COPIED. Nothing outside TRIPLE_PASS_20261003 is written.
set -e
T=/Users/heuremen/bones-forge/parallax/darkwave_disco/internal/TRIPLE_PASS_20261003/rerun
SRC5=/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run
SRC3=/Users/heuremen/bones-forge/parallax/out/qubit_three_runs
REL=/Users/heuremen/bones-forge/parallax/darkwave_disco/for_indahl_ai/data
mkdir -p $T/qubit_fifth_run/data/reads $T/qubit_fifth_run/data/band
for c in ibm_pittsburgh ibm_kingston ibm_marrakesh; do
  mkdir -p $T/qubit_fifth_run/data/fire/$c
  for f in $SRC5/data/fire/$c/run*_meta.json $SRC5/data/fire/$c/run*_results.npz; do
    [ -e "$f" ] && ln -sf "$f" $T/qubit_fifth_run/data/fire/$c/$(basename $f)
  done
done
for c in ibm_kingston ibm_phoenix ibm_pittsburgh; do
  mkdir -p $T/qubit_three_runs/data/fire/$c
  for f in $SRC3/data/fire/$c/run*_meta.json $SRC3/data/fire/$c/run*_results.npz; do
    [ -e "$f" ] && ln -sf "$f" $T/qubit_three_runs/data/fire/$c/$(basename $f)
  done
done
# reader code: copied from the RELEASE (code/), the frozen copy the hashes cover
for f in $REL/code/*.py; do cp "$f" $T/qubit_fifth_run/; done
# input reads the readers need (copied, so any write lands here)
for f in looktime_roles.json pittsburgh_config_timing.json noname_roles.json witness_roles.json layout_156_family.json maker_look_length_pittsburgh.json; do
  cp $REL/reads/$f $T/qubit_fifth_run/data/reads/
done
echo "sandbox ready: $T"
ls $T/qubit_fifth_run/data/fire/*/ | head -5
