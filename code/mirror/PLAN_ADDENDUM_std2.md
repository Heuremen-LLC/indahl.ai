# Addendum for Faults and Guards 2.0 to the IBM published-calibration audit plan, 12 Nov 2026

Written before any new reading under the new outcome rule. AUDIT_PLAN.md is not edited. This file is a new addendum.

## What changes
Only the outcome rule of check A (T2 against 2 x T1). Data, sources, the saved records, the thresholds as counts, and checks B, C and D are unchanged.

## Check A under Faults and Guards 2.0
The plan's own text says IBM publishes no fit uncertainty, so fit noise cannot be excluded. Every record entry holds one T1 value and one T2 value, each with a date and no width. The ratio T2 over T1 is therefore a point ratio with no interval, and no interval method was named before the read. Under section 6.5 a ratio needs an interval on a scale the plan names or by resampling.

The desk holds no data from which an interval of this ratio could be formed without a new read. Repeated saved records of one qubit show how the published value moved between calibrations. That is drift between calibrations, it is not the fit uncertainty of one entry, and naming it as the interval now would be a method written after the data.

So every T2 over T1 entry, in every saved record of every processor, reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. This is the decision the addendum makes: the planned quantity cannot be given a width.

- Size that matters: not named. The old thresholds 2.0 (the physical bound of 2 x T1) and 2.5 stay in the plan as descriptive cut points for the count of point ratios. They no longer produce an outcome word.
- Band: none. Bound for the descriptive count: 2.0, one-sided, closed at the cut, so a ratio above 2.0 is counted in the count of point ratios above 2.0.
- Interval method and level: none. No draws, no seed.
- Edge convention: closed.

## What the page prints
- The count of qubits with a point ratio above 2.5 and the count between 2.0 and 2.5, as counts of point ratios. They are not outcomes and the word ABOVE is not used for them.
- Beside them the headline reading: every entry is CANNOT_TELL (NO_INTERVAL_FORMABLE), with the REQ-13 line. NOTHING_RETURNED is 0 unless a saved record cannot be parsed. A record that cannot be parsed is listed apart and is outside the count.
- The flagged qubit table is renamed to qubits whose point ratio is above 2.5, with their raw entries as before.

## Checks B, C and D
B (T1 and T2 dated over 24 hours apart), C (entry age) and D (restamps) are exact counts of published dates and values against fixed cut points. They are exact row-level reads with no sampling and no tolerance named. They print the counts and no outcome word. The word MISMATCH in the stored flag records stays as the plan's own descriptive label.

## Earlier recorded outcomes
Every outcome recorded before 12 Nov 2026 stands under the rule the plan named then (ABOVE above 2.5, CANNOT_TELL between 2.0 and 2.5, CONSISTENT at or below 2.0). They are kept in the saved audit history and are read here as point-ratio counts. Under 2.0 they would all have read CANNOT_TELL with NO_INTERVAL_FORMABLE.
