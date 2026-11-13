# IBM published-calibration audit. Plan, written before the audit read.

## What is checked (IBM's own record against itself, zero QPU)
For every saved record of every processor (records/*/ *.json.gz), each qubit entry:
A. T2 against 2 x T1 (the physical bound for a single qubit). ratio = T2 / T1.
   ABOVE: ratio > 2.5. CANNOT_TELL: 2.0 < ratio <= 2.5 (IBM publishes no fit uncertainty, so fit noise cannot be excluded). CONSISTENT: ratio <= 2.0.
B. Measurement dates inside one record. For each qubit with both T1 and T2: gap = |date(T1) - date(T2)|. MISMATCH if gap > 24 h.
C. Age of each entry = record stamp minus entry date. Counted by entry name: older than 24 h, older than 7 days.
D. Restamps: consecutive saved records for one processor compared entry by entry (value, date). A restamp is NO_CHANGE if no qubit entry changed in value or date, CHANGED otherwise.
Thresholds are fixed here. Counts are reported per processor and over all saved records, with the record stamp for each.

## Double check
1. Fresh pull of every processor from IBM before the read (mirror run), audit run on the fresh records and on all earlier saved records.
2. An independent recount: the audit is recomputed by a second small script written separately (no shared code), counts must match exactly.
3. Any flagged qubit is printed with its raw entries and dates from the record.
4. The audit repeats on each mirror run. A flag is "persistent" if it appears in 2 or more saved records of that processor, "single record" otherwise.

## Not claimed
Whether any entry was wrong in the device. The audit reads what IBM published against what IBM published. No cause is named.


## Note (29 Oct, from the internal audit)
1. The 2.5 threshold for T2 above T1 was set after the first look at the qubits it flags (boston qubit 85 and fez qubit 148 were seen first). The page says so and this committed plan did not. It does now. The two readings came from before the rule, and every other row was read under it.
2. A flag is called persistent after two saved records, but a restamped record carries unchanged T1 and T2 values, so a qubit seen in 23 of 23 records of fez may rest on one old measurement. The persistence count is a count of saved records and not of new measurements. The page's restamp column (no change or changed) is the check.
3. Open: the mirror counts 24 records for fez and 10 for aachen while the audit reads 23 and 9, because records are saved by stamp name with no overwrite check. Not yet reconciled.
