# Claim codes (Standards 2.0.0, read from standard_v1.json)

Statuses: **PRESENT**: The test finds the pattern in the released material.; **ABSENT**: The test was run on the needed material and the pattern was not found.; **CANNOT_TELL**: The test cannot be run or finished. One reason from the closed status list is required.; **NOT_APPLICABLE**: The claim has no step, quantity or practice that the entry is about. The entry states when this holds.

CANNOT_TELL status reasons (closed list): **NOT_RELEASED**: The material the test needs was not released.; **UNREADABLE**: The material was released and cannot be read.; **METHOD_UNSTATED**: The claim does not state its method well enough for the test to be run. F7 reads an interval, so it also uses the closed list of outcome reasons from STANDARD.md section 6: **STRADDLES_EDGE**, **TOO_WIDE_TO_RESOLVE**, **NO_INTERVAL_FORMABLE**.

## F1 Self-built reference

Results are compared with a reference built from the same setup or from IBM’s stated figures.

- Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
- Test: Find the reference the result is compared with. Read how it was built.
- PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
- ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
- CANNOT_TELL (METHOD_UNSTATED) when: The paper does not say how the reference was built.
- CANNOT_TELL (NOT_RELEASED) when: The reference or the figures it was built from are named but not released.
- CANNOT_TELL (UNREADABLE) when: The reference was released and cannot be read.
- NOT_APPLICABLE when: The claim compares its result with no reference.
- Note: The published definition names the vendor in whose context it was written. The code applies to any stated reference or stated figures, from any source.

## F2 Selected result

The headline figure is a selected value: a maximum over rows, a best case, or a projection.

- Applies to: Any claim that states a headline figure.
- Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
- PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
- ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
- CANNOT_TELL (NOT_RELEASED) when: The rows the figure came from are not released.
- CANNOT_TELL (UNREADABLE) when: The rows were released and cannot be read.
- NOT_APPLICABLE when: The claim states no headline figure.
- Note: Relation to FLT-03. A selected headline figure with the n it was selected from printed is QIA-F2 Present and FLT-03 Absent. A selected headline figure without that n is QIA-F2 Present and FLT-03 Present.

## F3 Reading without a width

A bounded reading is stated as yes or no, without an interval.

- Applies to: Any claim with a bounded reading. A reading is bounded when the claim compares it with a figure, a threshold or a band.
- Test: Find each bounded reading. Check whether it is stated with an interval and the level of that interval.
- PRESENT when: A bounded reading is stated as yes or no with no interval.
- ABSENT when: Each bounded reading carries an interval and its level.
- CANNOT_TELL (NOT_RELEASED) when: The counts needed to form an interval are not released.
- CANNOT_TELL (UNREADABLE) when: The counts were released and cannot be read.
- NOT_APPLICABLE when: The claim has no bounded reading.

## F4 Reading not released

A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.

- Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
- Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
- PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
- ABSENT when: Every needed reading is in the paper or its files.
- CANNOT_TELL (UNREADABLE) when: A released file that may hold a needed reading cannot be read.
- NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
- Note: F4 has no cannot-tell state for an unstated method. An unstated method is Present with a note, so the test does not wait on a list that cannot be made.

## F5 Number recomputes differently

A printed number does not follow from the paper’s own data or arithmetic.

- Applies to: Any claim that prints a number that follows from data or arithmetic.
- Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
- PRESENT when: The rounded recomputed value is not equal to the printed value.
- ABSENT when: The rounded recomputed value is equal to the printed value.
- CANNOT_TELL (NOT_RELEASED) when: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.
- CANNOT_TELL (UNREADABLE) when: The data were released and cannot be read.
- CANNOT_TELL (METHOD_UNSTATED) when: The paper does not state the computation well enough to repeat it.
- NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
- Note: Rounding rule. The printed precision is the place of the last printed digit. Recompute at the full precision of the released data and round half away from zero to the printed precision. If the only released inputs are themselves printed rounded values, recompute with each input at both ends of its rounding range and round each result. The printed value is Absent if it equals any of those rounded results and Present if it equals none. Present and Absent leave no gap.

## F6 Text differs from own table

The text, abstract or caption differs from the paper’s own table, figure or files.

- Applies to: Any claim whose text refers to a table, figure or file.
- Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
- PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
- ABSENT when: Every checked statement and number agrees with its table, figure or file.
- CANNOT_TELL (NOT_RELEASED) when: The table, figure or file is not released.
- CANNOT_TELL (UNREADABLE) when: The table, figure or file was released and cannot be read.
- NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
- Note: An unreadable released file of the claim is CANNOT_TELL with reason UNREADABLE. It is never also recorded as NOTHING_RETURNED. See section 6.

## F7 Classical comparison available

A simple classical method on the same instances matches or exceeds the reported result.

- Applies to: Any claim of speed or quality against a classical method, in any field. Claims about quantum or other novel hardware are the usual case.
- Test: Choose the classical method before the comparison and name it. Run it on the same instances. Report its result with its interval and level. Read the classical result against the reported result as set out below.
- PRESENT when: The comparison reads ABOVE or CONSISTENT in favour of the classical method. That is, the difference between the classical result and the reported result, with its interval, lies entirely above the negative of the margin named before the run.
- ABSENT when: The comparison reads BELOW. The difference lies entirely below the negative of that margin.
- CANNOT_TELL (NOT_RELEASED) when: The instances are not released.
- CANNOT_TELL (UNREADABLE) when: The instances or the reported result were released and cannot be read.
- CANNOT_TELL (STRADDLES_EDGE) when: The interval of the difference overlaps the negative of the margin.
- CANNOT_TELL (TOO_WIDE_TO_RESOLVE) when: The interval reaches both the null and the size that matters.
- CANNOT_TELL (NO_INTERVAL_FORMABLE) when: No interval can be formed for the difference.
- NOT_APPLICABLE when: The claim is not about speed or quality against a classical method.
- Note: Choosing the classical method. The recount names the method before the comparison is run. The method is the strongest simple method available for the instances, and the recount publishes why it was chosen, its settings, its result and the interval and level of that result. A weaker method named after seeing the result is not a valid choice.
- Note: Matches or exceeds. Let the difference be the classical result minus the reported result, taken so that a larger value favours the classical method. The recount names a margin before the run. The default margin is zero. The difference is read against the single bound at the negative of the margin under section 6. ABOVE means the classical method matches or exceeds the reported result and the code is Present. CONSISTENT is not available for a single bound. BELOW means it falls short and the code is Absent. Any CANNOT_TELL outcome carries its reason, and the code is CANNOT_TELL with the same reason.
- Note: A classical method that was not run is a code that was not tested. It is listed under REQ-12 and has no status.

# Recount requirements

- **REQ-01 Name the ruler before the number**: The instrument and the question it answers are named in the output, beside the figure, and were chosen before the quantity was computed.
- **REQ-02 Write the baseline down first**: Sample counts, windows, averaging and the number of places examined are written down for every arm before the measurement arm is computed.
- **REQ-03 State the data source**: Each input names where it came from. Raw copies of every source read are kept with their SHA-256 hashes.
- **REQ-04 State the version read**: The version, edition or retrieval date of every source, and the version of this standard, are stated with the date and time of the read.
- **REQ-05 Use reading outcomes**: Every reading is reported as ABOVE, BELOW, CONSISTENT or CANNOT_TELL against a figure, band or bound named in advance, with its edge convention, its tolerance for a point figure, and the size that matters where the reading is a departure from a null. Every CANNOT_TELL carries one reason from the closed list in section 6. A failed read of a source is reported as NOTHING_RETURNED.
- **REQ-06 Give each reading its interval and level**: Every reading carries its interval, the method and the level of that interval, its n, and the n it was selected from where it is a selection. The method and level are named in the plan before the read. A changed level is a new reading and is reported beside the first. Every rate names its denominator.
- **REQ-07 Test the instrument first**: The instrument is run on a case it must pass and a case it must fail before it is pointed at the claim. Both results are recorded.
- **REQ-08 Publish receipts**: Every number in the recount links to the file, row or run it came from, so a reader can rerun it.
- **REQ-09 Name dropped material**: Any run, row or arm that is discarded is named in the output with the reason and what replaced it.
- **REQ-10 Publish corrections beside the first reading**: A reading that is later corrected stays in the record beside the correction and its reason.
- **REQ-11 Keep CANNOT_TELL as its own result**: CANNOT_TELL is never folded into pass or fail, and never counted as agreement or as disagreement. The two guards cited here carry the principle of never folding and nothing else in this standard.
- **REQ-12 State what was not tested**: The recount lists every code, fault and guard that was not tested and why. An entry marked NOT_APPLICABLE was tested for applicability and is listed with its reason.
- **REQ-13 Print the counts beside every headline share**: Beside every headline share the recount prints the count of NOTHING_RETURNED and the share of CANNOT_TELL, split by reason. The reasons are the outcome reasons for readings and the status reasons for statuses.
