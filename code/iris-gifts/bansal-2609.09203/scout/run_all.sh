#!/bin/zsh
# Reproduces every recount number in the README. Reads JSON as data only. Nothing from the authors is executed.
# Needs numpy for the first three and numpy+scipy+scikit-learn for rebuild_baselines.py.
cd "$(dirname "$0")"
PY=${PY:-python3}
HF=../theirs/hf_at_b112204c
mkdir -p out
python3 -I extract_pdf.py ../theirs/paper/2609.09203.pdf paper_text.txt
python3 -I survey_schema.py $HF            > out/survey_schema.txt
python3 -I survey_outcomes.py $HF          > out/survey_outcomes.txt
python3 -I compare_data_vs_trajectories.py $HF > out/compare_data_vs_trajectories.txt
$PY -I rebuild_frontier.py $HF             > out/rebuild_frontier.txt
$PY -I rebuild_open_live.py $HF            > out/rebuild_open_live.txt
$PY -I rebuild_baselines.py $HF            > out/rebuild_baselines.txt
python3 -I model_revisions.py              > out/model_revisions.txt   # public model metadata, read-only
