# Conformance checklist

For use against any benchmark or paper claim. Faults and Guards version 2.0.0 (https://doi.org/10.5281/zenodo.24164794). Conformance is a self-declaration of method, not an assessment or a certificate.

Claim: ____________________  Version or date read: ____________  Reader: ____________

## How to answer

Part A describes the claim. Mark each line yes, no, cannot tell or N/A. A cannot tell carries one reason, written in the cell. For a claim line the reasons are NOT_RELEASED, UNREADABLE and METHOD_UNSTATED, and for a line that rests on a reading STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE or NO_INTERVAL_FORMABLE. Cannot tell is a result and is never counted as yes or no.

N/A rule. Answer N/A only when the claim has no step, quantity or practice that the line asks about, as stated in the Applies to or Not applicable line of the entry named in brackets. Write the reason in one sentence. N/A is not counted as yes, no or cannot tell.

Part B covers the recount itself. Mark each line yes, no or N/A. The N/A rule for Part B is that the recount contains nothing of the kind the line asks about, such as REQ-07 in a recount that uses no instrument. Write the reason in one sentence. A cannot tell answer is not available in Part B because the recount author knows its own practice.

## Part A. The claim

| Line | Question | Yes | No | Cannot tell (reason) | N/A |
|---|---|---|---|---|---|
| A1 | Is the number being checked named, with the figure or band it is read against (section 6)? | | | | |
| A2 | Was the reference built independently of the setup under test (QIA-F1)? | | | | |
| A3 | Is the headline figure a summary of all rows with its n, and not a maximum, best case or projection (QIA-F2)? | | | | |
| A4 | Does each bounded reading carry an interval and its level (QIA-F3)? | | | | |
| A5 | Is every reading needed to recompute the claim in the paper or its files (QIA-F4)? | | | | |
| A6 | Do the printed numbers recompute from the released data at the printed precision (QIA-F5)? | | | | |
| A7 | Do the text, abstract and captions agree with the tables, figures and files (QIA-F6)? | | | | |
| A8 | Does a simple classical method, named before the run, fall short of the reported result on the same instances (QIA-F7)? | | | | |
| A9 | Were the baseline and the measurement given the same sample count, window, averaging and places examined (FLT-01)? | | | | |
| A10 | Does the width come from independent units and not rows (FLT-06)? | | | | |
| A11 | Were cells at a ceiling or floor counted before aggregation (FLT-10)? | | | | |
| A12 | Can each pair of agreeing readings be traced to two separate things (FLT-11)? | | | | |
| A13 | Can the ruler say it cannot tell, and was a result that did not resolve kept out of the null column (FLT-19, FLT-44)? | | | | |

## Part B. The recount

| Line | Requirement | Question | Yes | No | N/A |
|---|---|---|---|---|---|
| B1 | REQ-01 | Is the ruler named beside each number, and was it chosen before the quantity was computed? | | | |
| B2 | REQ-02 | Were the sample counts, windows, averaging and places examined written down for every arm before the measurement arm was computed? | | | |
| B3 | REQ-03 | Does each input name its source, with raw copies kept and SHA-256 hashes? | | | |
| B4 | REQ-04 | Are the version or date of every source, the version of this standard, and the date and time of the read stated? | | | |
| B5 | REQ-05 | Is every reading one of the four reading outcomes against a figure, band or bound named in advance, with its edge convention, tolerance or size that matters where needed, and does every CANNOT_TELL carry one reason? | | | |
| B6 | REQ-06 | Does every reading carry its interval, the method and the level, named before the read, with its n, its selection n and its denominator? | | | |
| B7 | REQ-07 | Were the instrument’s pass case and fail case run and recorded before it was pointed at the claim? | | | |
| B8 | REQ-08 | Does each number link to a receipt a reader can rerun? | | | |
| B9 | REQ-09 | Are dropped runs, rows or arms named with the reason and what replaced them? | | | |
| B10 | REQ-10 | Is every wrong first reading shown beside its correction? | | | |
| B11 | REQ-11 | Is CANNOT_TELL kept as its own result, never folded into pass or fail? | | | |
| B12 | REQ-12 | Does the recount list every code, fault and guard it did not test, and every NOT_APPLICABLE with its reason? | | | |
| B13 | REQ-13 | Does every headline share print the NOTHING_RETURNED count and the CANNOT_TELL share split by reason? | | | |

## How to read the result

List every no and every cannot tell, with its reason, and every N/A with its reason. A recount may be declared conforming by its author only when every line of Part B is yes or N/A. That declaration is a self-declaration of method. It is not an assessment or a certificate. Part A describes the claim and is reported as found.

Tally for each part: yes ___  no ___  cannot tell ___  N/A ___. Print all four. Never print a single score.
