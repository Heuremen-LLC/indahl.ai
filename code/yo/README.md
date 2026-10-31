# YO

YO is Qwen3-1.7B (Apache-2.0) trained with LoRA to read IBM's published calibration records the way an auditor does. It has two jobs:
flag stale or zero entries in a record, and give one of four verdicts (ABOVE, BELOW, CONSISTENT, CANNOT_TELL) on a measured value against
a stated one. The plan (PLAN_YO_V2.md) was committed before any data was built, and the training runs live at https://indahl.ai/iris/lab

- `pull_history2.py` pulls IBM's calibration history (backend properties at 2-hour steps, 180 days, read only, no QPU time).
  It imports `service()` from our own login helper, which is not published. Any `QiskitRuntimeService()` login works in its place.
- `yo2_data.py` builds the items. Every answer is computed by code from the record. It refuses to write data if an item would be cut
  by the trainer's maximum length.
- `yo2_eval.py` scores the test items for the model and for each baseline. `yo2_compare.py` applies the plan's four-outcome rule.
- `yo2_publish.py` sends the live status (step, loss, baselines, and the test reading once it exists) to the page.

Training: `mlx_lm lora` (mlx-lm 0.31.3) with completions data and `mask_prompt: true`. Libraries: [mlx-lm (git)](https://github.com/ml-explore/mlx-lm), [mlx-lm (PyPI)](https://pypi.org/project/mlx-lm/), [qiskit-ibm-runtime (git)](https://github.com/Qiskit/qiskit-ibm-runtime), [qiskit-ibm-runtime (PyPI)](https://pypi.org/project/qiskit-ibm-runtime/).
