# IBM calibration stability index. Plan, written before the first stability table.

## What it is
A descriptive table, per processor, built from every saved record in records/. No claim is tested, so no ABOVE or BELOW is assigned. Shares carry Wilson 95% intervals. A table row is labelled "too few records" until 20 records and 14 days are held for that processor.

## Columns (fixed now)
- Records held, first and last stamp, days spanned.
- Qubits in the newest record.
- Re-measured: of qubits present in the first and the newest record, the share whose T1 measurement date changed, and the same for T2.
- Dates apart: in the newest record, the share of qubits whose T1 and T2 measurement dates are more than a day apart.
- Median age of T1 and of T2 in the newest record, in hours.
- Flagged ever: qubits that had T2 / T1 above 2 in at least one saved record, and the subset above 2.5 (the audit's two bands).
- Clean throughout: qubits that were never above 2 in any saved record and never had T1 and T2 dated more than a day apart.
## Not claimed
Why a qubit is flagged or clean. That a clean qubit performs better. The index describes what IBM published about itself.
## Output
KV qia_stability, a block under the audit on /qia, and a history row per day in the public repo (the existing trend rider).
