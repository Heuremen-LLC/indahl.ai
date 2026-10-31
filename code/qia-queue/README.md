# QIA queue ticker

Reads the number of jobs IBM reports pending at each processor our paid instance can see, once per hour of HST ticks, and the waits our own jobs saw (created to running).

- `PLAN.md` was committed before the first read.
- `queue_tick.py` is the reader. It uses [qiskit-ibm-runtime](https://pypi.org/project/qiskit-ibm-runtime/) and uses no QPU time.
- `history.jsonl` holds every read, one row per processor per read. A failed read is saved as NOTHING_RETURNED.
- `summary.json` is the latest reading shown at https://indahl.ai/qia

IBM publishes no wait estimate and this does not make one.
