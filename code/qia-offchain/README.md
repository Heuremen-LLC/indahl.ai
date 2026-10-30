# QIA off-record chain

Every time one of our own jobs measured a qubit or a gate against the calibration IBM published for it, and found IBM's figure outside what the
device delivered, the reading is added here as one entry. Each entry carries the processor, the qubits, the quantity, IBM's figure and the date IBM
attached to it, what we measured with its interval, the job's running window from IBM's own job record, the job id, and the rule that decided it.

Rules
- Append only. An entry is never edited or removed. A correction is a new entry that names the entry it corrects (field "corrects").
- Each entry's hash is sha256 of the canonical JSON of the entry with its "prev" field (the previous entry's hash; 64 zeros for the first) and without
  its own "hash". Canonical = keys sorted, separators "," and ":", UTF-8. verify.py checks the whole chain.
- Only a stated figure against a measurement of the same quantity, or against a bound that holds for every definition of it (T2 at most 2 x T1).
- Only from our committed runs with a job id. Entries are recounted by hand before they are added (book rule).
- Order in the chain is the order added. Each entry also carries its measurement window, so older readings can be added later (backfill) and still be
  found by time.
- Calibration-run entries are added by qia_cal/cal.py under qia_cal/PLAN.md, by its rule and not recounted by hand; each carries the sha256 of its full per-qubit file.
