# Darkwave clock

How long a readout-phase correction table keeps giving back the phase that a 39-qubit mid-circuit readout puts on the 117 untouched qubits
next to it. Each fire reads a fixed table (measured 31 October 2026) against a table measured minutes before, on ibm_kingston and
ibm_marrakesh, with the circuits of the main run (`../run/keystone.py`, copied unchanged). The plan (`PLAN_CLOCK.md.text`), code and
synthetic tests were committed before the first job. Each `day_*` folder holds one chip-fire: the job record, IBM's calibration record
before every job, the raw per-shot registers (`raw_*.npz`), today's table, and `results_clock.text`.

Run the analysis on a fire: `python analyze_clock.py day_<stamp>_<chip>` (needs `keystone.py`, `analyze_keystone.py` and `pooters.py`
from `../run`, plus [qiskit (git)](https://github.com/Qiskit/qiskit), [qiskit (PyPI)](https://pypi.org/project/qiskit/)).
