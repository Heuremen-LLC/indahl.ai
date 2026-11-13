#!/bin/zsh
# Build the IRIS Zenodo bundle: our plans, code, outputs and referee reports. No third-party data (inputs are rebuilt from the
# authors' releases by matrix/rebuild_inputs.md instructions); no blind-sheet key; no model weights.
set -e; cd ~/bones-forge/iris_index; OUT=launch/zenodo_iris/iris_recount_bundle.zip; rm -f $OUT
zip -q -r $OUT PLAN_IRIS_INDEX.md SWEEP_20261025.md SCAN_register.json IRIS_BOOK_register.json PUB2_IRIS.md book_gate.py \
  recounts pub2 matrix/PLAN.md matrix/PLAN_v2.md matrix/run_matrix.py matrix/run_matrix_v2.py matrix/score_matrix.py matrix/score_matrix_v2.py \
  matrix/build_matrix_md.py matrix/synth_matrix.py matrix/synth_matrix_v2.py matrix/synth_results.text matrix/synth_v2_results.text \
  matrix/MATRIX.md matrix/MATRIX.pre-add3.md matrix/REFEREE_v1a.md matrix/REFEREE_v1b.md matrix/CODE.sha256 matrix/CODE_v2.sha256 matrix/results matrix/frontier \
  seats/serve.sh matrix/drive.sh matrix/inputs/mcq4_poscontrol.json matrix/rebuild_inputs.md \
  -x '*/referee/*' -x 'pub2/X1_cross_model/samples_all.json' -x 'pub2/X1_cross_model/precision_sample.json' -x '*.pdf.*candidate' -x '*/__pycache__/*' -x 'pub2/paper/*.tex.bak'
unzip -l $OUT | tail -1
