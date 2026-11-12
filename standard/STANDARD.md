# Faults and Guards, version 2.0

Heuremen LLC. Version 2.0.0, 12 November 2026, https://doi.org/10.5281/zenodo.24164794. All versions: https://doi.org/10.5281/zenodo.24164029. Previous versions: 1.0.1, https://doi.org/10.5281/zenodo.24164207. 1.0.0, https://doi.org/10.5281/zenodo.24164030. Web: https://indahl.ai/standard

This standard sets out how to check a claim about an AI or quantum measurement result, and how to publish the check so that anyone can rerun it. It gives each failure a stable ID, a test, and a rule for saying present, absent, cannot tell or not applicable. It is written to be cited and applied by an auditor, an insurer, a regulator, a journalist or a reader.

## 1. Scope

This standard applies to claims that report a measured result for an AI model, an AI benchmark, a quantum device or an analysis of either. It covers two levels. Claim-level codes describe what is off in a published claim and can be tested from what the claim released. Process-level faults and guards describe how a measurement or analysis goes wrong and what procedure is built against it.

It does not rank systems. It does not say whether a system is safe, good or fit for a purpose. It says whether a number can be rechecked, whether it recomputes, and what the recount found. A recount gives readings, codes and statuses. It does not give a certificate.

Conformance to this standard is a self-declaration of method by the author of a recount. It is not an assessment, an audit or a certificate, and Heuremen LLC does not review or approve declarations.

## 2. Terms

**Claim.** A statement of a measured result, with the number, the setup and the material released with it.

**Recount.** A fresh computation of a claimed number from the material the claim released.

**Reading.** A value from a recount, from the claim, or from the recount author’s own run, with its interval, the method of that interval and the level of that interval.

**Bounded reading.** A reading the claim compares with a figure, a threshold or a band.

**Figure, band or bound.** The number, the range or the single threshold a reading is read against. It is named before the reading is computed. A band is written [lo, hi]. A bound is one number. See section 6.

**Null.** The value the reading would take if nothing were there, usually zero, or the figure itself when the reading is a difference from a figure.

**Size that matters.** The smallest departure from the null that would change what the claim means. It is named before the reading is computed.

**Tolerance.** An equivalence margin named before the read. It turns a point figure into a band.

**Ruler.** The instrument and the question it answers. A value with a standard error is one ruler. A p-value is another. A ruler is named beside the number.

**Receipt.** A file, row, run or hash that lets a reader reproduce a number.

**Released material.** Everything the claim published, in the paper, its files and the sources it names.

**Code.** A claim-level code from QIA-F1 to QIA-F7.

**Fault.** A process-level failure mode with an ID of the form FLT-nn. The number is the one assigned in the published Faults document and never changes.

**Guard.** A procedure built against faults with an ID of the form GRD-nn. The number is the one in the published Guards document.

**Present, absent, cannot tell, not applicable.** The four statuses of a code or fault. Cannot tell means the test could not be run or finished, and always carries one status reason. Not applicable means the claim has no step, quantity or practice that the entry is about.

**Applied, not applied, cannot tell, not applicable.** The four statuses of a guard.

**Reading outcome.** One of ABOVE, BELOW, CONSISTENT, CANNOT_TELL. See section 6. CANNOT_TELL always carries one outcome reason.

**Reason.** The one required explanation attached to every CANNOT_TELL. Outcome reasons are STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE and NO_INTERVAL_FORMABLE. Status reasons are NOT_RELEASED, UNREADABLE and METHOD_UNSTATED.

**Self-declaration.** A statement by the author of a recount that the recount follows the method in section 8. It is not an assessment or a certificate.

## 3. How to read the entries

Every entry has a stable ID, a definition or name, a test, and rules for its four statuses. The names, the family and part titles and the published text of faults and guards are published wording from the published Faults and Guards documents, and the code names and definitions are from the QIA Key. The tests, the Needs lines, the status rules, the Absent rules and the links between codes, faults and guards are Heuremen LLC’s own. Each test carries the label Heuremen LLC test. Section 11 sets out which text is which. The full published text of each fault and guard is in standard_v1.json under published_text.

A status is a statement about the claim and the material released with it. Cannot tell is a result with a reason. It is not a pass and it is not a fail. Not applicable is a result. It is listed with its reason and is not counted as present, absent, applied or not applied.

## 4. Claim-level codes

These codes keep the name and definition wording of the QIA Key at https://indahl.ai/qia/key. The tests and rules below are Heuremen LLC’s own.

### QIA-F1 Self-built reference

Definition: Results are compared with a reference built from the same setup or from IBM’s stated figures.

Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.

Test: Find the reference the result is compared with. Read how it was built.

Test source: Heuremen LLC test

- Present: The reference was built from the same setup as the result, or from the vendor’s stated figures.
- Absent: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
- Cannot tell, reason METHOD_UNSTATED: The paper does not say how the reference was built.
- Cannot tell, reason NOT_RELEASED: The reference or the figures it was built from are named but not released.
- Cannot tell, reason UNREADABLE: The reference was released and cannot be read.
- Not applicable: The claim compares its result with no reference.

The published definition names the vendor in whose context it was written. The code applies to any stated reference or stated figures, from any source.

Related faults: FLT-01, FLT-11

### QIA-F2 Selected result

Definition: The headline figure is a selected value: a maximum over rows, a best case, or a projection.

Applies to: Any claim that states a headline figure.

Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.

Test source: Heuremen LLC test

- Present: The headline figure is a maximum over rows, a best case, or a projection.
- Absent: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
- Cannot tell, reason NOT_RELEASED: The rows the figure came from are not released.
- Cannot tell, reason UNREADABLE: The rows were released and cannot be read.
- Not applicable: The claim states no headline figure.

Relation to FLT-03. A selected headline figure with the n it was selected from printed is QIA-F2 Present and FLT-03 Absent. A selected headline figure without that n is QIA-F2 Present and FLT-03 Present.

Related faults: FLT-03

### QIA-F3 Reading without a width

Definition: A bounded reading is stated as yes or no, without an interval.

Applies to: Any claim with a bounded reading. A reading is bounded when the claim compares it with a figure, a threshold or a band.

Test: Find each bounded reading. Check whether it is stated with an interval and the level of that interval.

Test source: Heuremen LLC test

- Present: A bounded reading is stated as yes or no with no interval.
- Absent: Each bounded reading carries an interval and its level.
- Cannot tell, reason NOT_RELEASED: The counts needed to form an interval are not released.
- Cannot tell, reason UNREADABLE: The counts were released and cannot be read.
- Not applicable: The claim has no bounded reading.

Related faults: FLT-25

### QIA-F4 Reading not released

Definition: A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.

Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.

Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.

Test source: Heuremen LLC test

- Present: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
- Absent: Every needed reading is in the paper or its files.
- Cannot tell, reason UNREADABLE: A released file that may hold a needed reading cannot be read.
- Not applicable: The claim depends on no reading. Such a claim is outside this standard.

F4 has no cannot-tell state for an unstated method. An unstated method is Present with a note, so the test does not wait on a list that cannot be made.

Related faults: none

### QIA-F5 Number recomputes differently

Definition: A printed number does not follow from the paper’s own data or arithmetic.

Applies to: Any claim that prints a number that follows from data or arithmetic.

Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.

Test source: Heuremen LLC test

- Present: The rounded recomputed value is not equal to the printed value.
- Absent: The rounded recomputed value is equal to the printed value.
- Cannot tell, reason NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.
- Cannot tell, reason UNREADABLE: The data were released and cannot be read.
- Cannot tell, reason METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
- Not applicable: The claim prints no number that follows from data or arithmetic.

Rounding rule. The printed precision is the place of the last printed digit. Recompute at the full precision of the released data and round half away from zero to the printed precision. If the only released inputs are themselves printed rounded values, recompute with each input at both ends of its rounding range and round each result. The printed value is Absent if it equals any of those rounded results and Present if it equals none. Present and Absent leave no gap.

Related faults: FLT-29

### QIA-F6 Text differs from own table

Definition: The text, abstract or caption differs from the paper’s own table, figure or files.

Applies to: Any claim whose text refers to a table, figure or file.

Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.

Test source: Heuremen LLC test

- Present: A statement or number in the text differs from the table, figure or file it refers to.
- Absent: Every checked statement and number agrees with its table, figure or file.
- Cannot tell, reason NOT_RELEASED: The table, figure or file is not released.
- Cannot tell, reason UNREADABLE: The table, figure or file was released and cannot be read.
- Not applicable: The claim has no table, figure or file beside its text.

An unreadable released file of the claim is CANNOT_TELL with reason UNREADABLE. It is never also recorded as NOTHING_RETURNED. See section 6.

Related faults: none

### QIA-F7 Classical comparison available

Definition: A simple classical method on the same instances matches or exceeds the reported result.

Applies to: Any claim of speed or quality against a classical method, in any field. Claims about quantum or other novel hardware are the usual case.

Test: Choose the classical method before the comparison and name it. Run it on the same instances. Report its result with its interval and level. Read the classical result against the reported result as set out below.

Test source: Heuremen LLC test

- Present: The comparison reads ABOVE or CONSISTENT in favour of the classical method. That is, the difference between the classical result and the reported result, with its interval, lies entirely above the negative of the margin named before the run.
- Absent: The comparison reads BELOW. The difference lies entirely below the negative of that margin.
- Cannot tell, reason NOT_RELEASED: The instances are not released.
- Cannot tell, reason UNREADABLE: The instances or the reported result were released and cannot be read.
- Cannot tell, reason STRADDLES_EDGE: The interval of the difference overlaps the negative of the margin.
- Cannot tell, reason TOO_WIDE_TO_RESOLVE: The interval reaches both the null and the size that matters.
- Cannot tell, reason NO_INTERVAL_FORMABLE: No interval can be formed for the difference.
- Not applicable: The claim is not about speed or quality against a classical method.

Choosing the classical method. The recount names the method before the comparison is run. The method is the strongest simple method available for the instances, and the recount publishes why it was chosen, its settings, its result and the interval and level of that result. A weaker method named after seeing the result is not a valid choice.

Matches or exceeds. Let the difference be the classical result minus the reported result, taken so that a larger value favours the classical method. The recount names a margin before the run. The default margin is zero. The difference is read against the single bound at the negative of the margin under section 6. ABOVE means the classical method matches or exceeds the reported result and the code is Present. CONSISTENT is not available for a single bound. BELOW means it falls short and the code is Absent. Any CANNOT_TELL outcome carries its reason, and the code is CANNOT_TELL with the same reason.

A classical method that was not run is a code that was not tested. It is listed under REQ-12 and has no status.

Related faults: FLT-01

## 5. Process-level faults

The family names and fault names are as published in Faults, https://heuremen.org/faults.pdf. The IDs are the published numbers and are not in family order. The tests, Needs lines and status rules are Heuremen LLC’s own, and the Guards line of each fault is a link assembled by Heuremen LLC, see section 11.

Every fault uses the same status rules. Present means the test finds the pattern in the released material. Absent means the test was run on the needed material and the pattern was not found. Cannot tell carries one reason. NOT_RELEASED means the material named under Needs is not released. UNREADABLE means it was released and cannot be read. METHOD_UNSTATED means the claim does not state the steps the test needs. Not applicable means the claim has no step, quantity or practice that the test is about, and the Applies to line of each fault says which claims have one.

Faults whose evidence is a process record can usually be tested only from the recount author’s own records. On a third-party claim their status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

### Family I. The baseline built after the measurement it judges

**FLT-01 The baseline averaged, counted or searched differently from the measurement**

Test: Write down for both arms the sample count, the window, the averaging and how many places were examined. Compare. Needs: Setup details of both arms. Evidence: released material. Applies to: Claims that compare a baseline with a measurement. Guards: GRD-03. Test source: Heuremen LLC test.

**FLT-02 A fixed threshold against a statistic that grows with n**

Test: Ask what the statistic does under the null as n grows. Check whether the threshold grows with it. Needs: Threshold and the statistic's behaviour under the null. Evidence: released material. Applies to: Claims that apply a fixed threshold to a statistic. Guards: none. Test source: Heuremen LLC test.

**FLT-03 A maximum over many draws reported as a measurement**

Test: Find any best, maximum or peak figure. Check that the n it was selected from is printed. Needs: The n behind each best figure. Evidence: released material. Applies to: Claims that report a best, maximum or peak figure out of many draws. Guards: GRD-09. Test source: Heuremen LLC test.

Relation to QIA-F2. A selected headline figure with the n it was selected from printed is QIA-F2 Present and FLT-03 Absent. A selected headline figure without that n is QIA-F2 Present and FLT-03 Present.

**FLT-04 The in-sample fit, including its most disguised form**

Test: Check the order of events. Was the rule fixed before the cases it is scored on, and was any explanation written after the result and counted as a prediction. Needs: Dated record of when rule and cases were fixed. Evidence: process record. Applies to: Claims that score a rule or model on cases, or explain a result after it. Guards: GRD-14. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-05 A continuum assumed where only discrete values were reachable**

Test: Enumerate what the setup could produce. Check the baseline was priced against that set. Needs: Description of what the setup can emit. Evidence: released material. Applies to: Claims about a setup that can produce only certain values. Guards: GRD-03. Test source: Heuremen LLC test.

**FLT-06 Dependent observations counted as independent**

Test: Count the independent units that contributed. Check the width came from units and not rows. Needs: Unit structure of the data. Evidence: released material. Applies to: Claims that count observations to set a width. Guards: GRD-11. Test source: Heuremen LLC test.

**FLT-07 Time-asymmetric differencing**

Test: Write the temporal order of every arm. Check that differences were taken in the same direction. Needs: Time order of each arm. Evidence: released material. Applies to: Claims that take differences between arms or time points. Guards: none. Test source: Heuremen LLC test.

**FLT-08 A per-unit constant read as signal**

Test: Remove any constant attached to every unit and measure again. Compare with the first reading. Needs: Per-unit data. Evidence: released material. Applies to: Claims with per-unit data in which each unit may carry a constant. Guards: GRD-05. Test source: Heuremen LLC test.

**FLT-09 An unequal setup across the columns being compared**

Test: Check that the instrument is identical across the columns compared. Re-run with it equalised and see whether the ordering holds. Needs: Instrument settings per column. Evidence: released material. Applies to: Claims that compare columns such as instruments, models or settings. Guards: GRD-06. Test source: Heuremen LLC test.

**FLT-10 Saturated or censored cells averaged as data**

Test: Count cells at a ceiling or floor before aggregation. Check they were excluded or reported. Needs: Cell-level values. Evidence: released material. Applies to: Claims that aggregate cells that may sit at a ceiling or floor. Guards: GRD-10. Test source: Heuremen LLC test.

**FLT-11 One artifact's internal record used as a second, independent reading**

Test: For each pair of agreeing readings, name the two physically separate things they came from. Needs: Provenance of each reading. Evidence: released material. Applies to: Claims in which two readings are said to agree. Guards: GRD-12. Test source: Heuremen LLC test.

**FLT-12 The pilot that came out perfect**

Test: Treat clean zero-overlap separation as a prompt to run the asymmetry checks for Faults 1 to 11 on the same data. Needs: Setup details for the asymmetry checks. Evidence: released material. Applies to: Claims that report a clean separation with no overlap. Guards: GRD-04. Test source: Heuremen LLC test.

### Family II. Zeroing a gap that was itself the reading

**FLT-13 Calibrating away the difference between two seats**

Test: Check whether two instruments were aligned to agree and the agreement was reported as accuracy. Needs: Calibration history of the instruments. Evidence: released material. Applies to: Claims that align two instruments or seats. Guards: GRD-12. Test source: Heuremen LLC test.

**FLT-14 Forcing agreement between quantities that cannot be commensurate**

Test: Ask whether an exact match is arithmetically possible. Check that the gap was not tuned toward an impossible match. Needs: The quantities and their units. Evidence: released material. Applies to: Claims of agreement between quantities of different kinds or units. Guards: GRD-12. Test source: Heuremen LLC test.

### Family III. The fold that erases the discarded half

**FLT-15 A magnitude taken where the last step produced two numbers**

Test: Find each correlation, lock-in or demodulation output. Check whether amplitude and phase were both kept before any comparison. Needs: The processing steps. Evidence: released material. Applies to: Claims with a correlation, lock-in or demodulation output. Guards: GRD-01. Test source: Heuremen LLC test.

**FLT-16 A sum assumed where two effects multiply**

Test: Check whether a cross term was tested before an additive model was used. Needs: Model and data. Evidence: released material. Applies to: Claims that model the joint effect of two quantities. Guards: GRD-01. Test source: Heuremen LLC test.

**FLT-17 Asking which way a sign points instead of whether it holds**

Test: Check whether the stability of a sign was measured, as well as its direction. Needs: Repeated runs. Evidence: released material. Applies to: Claims about the direction of a sign. Guards: none. Test source: Heuremen LLC test.

**FLT-18 A snapshot that keeps the value and throws away the trajectory**

Test: Check whether the residual was measured at two or more precisions and how it moved. Needs: Readings at more than one precision. Evidence: released material. Applies to: Claims about a residual or a single snapshot value. Guards: none. Test source: Heuremen LLC test.

### Family IV. The forced verdict, and the answer that was never offered

**FLT-19 A ruler that cannot say “I cannot tell” lies at scale**

Test: Check whether the ruler can return a decline. Re-run with a third verdict if it cannot. Needs: The ruler's verdict set and the cell data. Evidence: released material. Applies to: Claims that use a ruler to return a verdict. Guards: GRD-01, GRD-08, GRD-38. Test source: Heuremen LLC test.

**FLT-20 The two-answer question that has three answers**

Test: Check whether a situation with three states was reduced to two options. Needs: The question as asked. Evidence: released material. Applies to: Claims that pose a question with a fixed set of answers. Guards: GRD-37. Test source: Heuremen LLC test.

**FLT-21 Four outcomes collapsed into two**

Test: Check whether distinct outcomes were collapsed into fewer bins. Each bin needs a single positive definition. Needs: Outcome definitions and the raw rows. Evidence: released material. Applies to: Claims that sort outcomes into bins. Guards: GRD-08, GRD-35. Test source: Heuremen LLC test.

**FLT-44 A result that does not resolve, filed as a null**

Test: Check whether a result that did not resolve was filed as a null. Check whether the reach of the ruler was stated. Needs: Sample size and the width the ruler can resolve. Evidence: released material. Applies to: Claims of a null or no-effect result. Guards: GRD-13. Test source: Heuremen LLC test.

Where the reading is a share or a difference, the status rests on a reading. A reading whose outcome is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE that was filed as a null makes this fault Present.

### Family V. The instrument that is wrong about itself

**FLT-22 You will report a count about yourself from memory**

Test: Read the count from the record. Compare with any count stated from memory. Needs: The record the count refers to. Evidence: process record. Applies to: A recount author’s own counts about its own work. Guards: GRD-21. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-23 Your own checker will be wrong, and all in one direction**

Test: Score the checker against cases a person labelled after reading each in full. Check the direction of its errors. Needs: Hand-labelled cases and checker output. Evidence: process record. Applies to: A checker built by the recount author. Guards: GRD-04. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-24 Every count has a ruler hidden inside it, and the rulers disagree**

Test: Check that each rate names its denominator and that the conclusion survives the other denominators. Needs: Denominators and the underlying counts. Evidence: released material. Applies to: Claims that state rates or counts. Guards: GRD-22. Test source: Heuremen LLC test.

**FLT-25 A verdict without a width is not a verdict**

Test: Check that each verdict is stated with its width. Needs: Verdicts and their stated uncertainty. Evidence: released material. Applies to: Claims that state verdicts. Guards: GRD-38. Test source: Heuremen LLC test.

**FLT-26 Two of your three seats are the same seat**

Test: For each third reading, name what it would do if the hypothesis were false. Needs: How the third reading was derived. Evidence: released material. Applies to: Claims that offer several readings of one event. Guards: GRD-24. Test source: Heuremen LLC test.

**FLT-27 A reviewer handed no evidence is measuring your tone**

Test: Check that any outside reviewer was handed the evidence and not only the prose. Needs: Reviewer inputs. Evidence: process record. Applies to: Claims that use an outside reviewer. Guards: GRD-25. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-28 The same fault counted as five successes**

Test: Check whether one standing fault was counted more than once. Needs: Detector log. Evidence: process record. Applies to: Claims that count detections or successes. Guards: GRD-23. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

### Family VI. The claim that was never checked

**FLT-29 An equals sign is a claim, and you will print one you have not checked**

Test: Evaluate both sides of every printed equality. Needs: The printed relations and their inputs. Evidence: released material. Applies to: Claims that print an equality or identity. Guards: GRD-27. Test source: Heuremen LLC test.

**FLT-30 A fabricated number passes every check that reads shape**

Test: Verify each number against its source, separately from any check of structure. Needs: Source of each number. Evidence: released material. Applies to: Claims that print numbers taken from a source. Guards: GRD-26. Test source: Heuremen LLC test.

**FLT-31 Counting mentions and reporting it as measurement**

Test: Check whether a count of mentions was reported as a measurement. Needs: How the count was produced. Evidence: released material. Applies to: Claims that count mentions or occurrences. Guards: none. Test source: Heuremen LLC test.

**FLT-32 Fitting a sequence whose points are on different axes**

Test: Check units across every point before any fit. Needs: Units of each point. Evidence: released material. Applies to: Claims that fit a sequence of points. Guards: GRD-29. Test source: Heuremen LLC test.

**FLT-33 Computing the significance before checking the literature**

Test: Check whether the literature check came before the significance calculation. Needs: Dated record of the two steps. Evidence: process record. Applies to: Claims that report a significance and a literature check. Guards: GRD-28. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-34 A pattern found twice is a pattern, not a law**

Test: Check whether a pattern found twice was written into further structures as a law. Needs: Record of where the pattern was applied. Evidence: process record. Applies to: Claims that carry a pattern into further structures. Guards: none. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-35 The correspondence with the deepest history proves the least**

Test: Check whether a correspondence is offered as evidence by its history. Needs: The claimed correspondence. Evidence: released material. Applies to: Claims that offer a correspondence as evidence. Guards: none. Test source: Heuremen LLC test.

Closest test only. The published entry states a principle. The test is the nearest operational reading of it that Heuremen LLC could write.

**FLT-36 The relationship the whole structure rests on is not a constant**

Test: Re-read the load-bearing relationship live. Compare with the value the structure was built on. Needs: Live access to the relationship. Evidence: process record. Applies to: Claims that stand on a stated relationship or constant. Guards: GRD-30. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

### Family VII. State, staleness, and work you cannot see

**FLT-37 Something long-lived is holding an old copy of what you just changed**

Test: Re-read the changed value through the path that consumes it. Needs: Access to the consuming path. Evidence: process record. Applies to: Claims about state held by a long-lived process or cache. Guards: GRD-31. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-38 The absence of a process is not the absence of work**

Test: Check liveness by recent completed work and not by a running process. Needs: Job records. Evidence: process record. Applies to: Claims about whether work is running or done. Guards: GRD-32. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-39 Your test data will become a finding about innocent work**

Test: Check that test writes go somewhere the live path does not read. Needs: Log destinations. Evidence: process record. Applies to: Claims that run test writes against a live path. Guards: GRD-33. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

### Family VIII. When the guard becomes the deliverable

**FLT-40 Naming the gap becomes the whole transaction**

Test: Price the fix of any named gap. Check whether a cheaper fix was left undone. Needs: Gap statements and their cost. Evidence: process record. Applies to: Claims that name gaps. Guards: GRD-34. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-41 Writing a failure mode down did not stop it**

Test: Check whether a written-down failure mode recurred after publication. Needs: Dated record. Evidence: process record. Applies to: Claims that record failure modes. Guards: GRD-36. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-42 A rule from a single instance given a theorem's authority**

Test: Check what each retained rule rests on. A single-instance rule may not be cited as a count. Needs: Basis tags of rules. Evidence: process record. Applies to: Claims that keep rules drawn from single instances. Guards: GRD-20. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-43 Narrating the mechanism instead of using it**

Test: For each claimed capability, find the line that executes it and confirm it ran. Needs: Code or run log. Evidence: process record. Applies to: Claims that describe a mechanism or capability. Guards: none. Test source: Heuremen LLC test.

The evidence for this fault is a process record. On a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED. That is expected and is not a finding.

**FLT-45 Explaining the work instead of stating it**

Test: Check whether business copy states offer, receipt and terms or explains and persuades. Needs: The copy. Evidence: released material. Applies to: Business copy. Guards: GRD-39. Test source: Heuremen LLC test.

## 6. Reading outcomes

Every reading is reported against a figure, band or bound that was named before the reading was computed. It has one of four reading outcomes. This standard calls its set the reading outcomes. They are a different set from the four outcomes used for model replies in the published Faults and Guards. Fault 21 and Guard 8 there use four outcomes for committed, held open, refused and nothing returned. Neither set replaces the other. Guard 8 and Guard 35 are cited in this standard only for the principle that outcomes are never folded into two.

### 6.1 What the plan names before the read

- The quantity read and the figure, band or bound it is read against.
- The edge convention. A band is [lo, hi]. By default both edges are closed, so a value equal to an edge is inside the band. A plan may state an open edge for any bound. An open edge is written with a round bracket, as in [0, 0.15).
- For a point figure, the tolerance. For a departure from a null, the null and the size that matters.
- The interval method and the level, as in 6.5.

### 6.2 The outcomes

The interval of a reading is written [l, u] and uses the same edge convention as the band.

- **ABOVE.** The whole interval lies above the band or above the single bound. With closed edges, l is greater than hi.
- **BELOW.** The whole interval lies below the band or below the single bound. With closed edges, u is less than lo.
- **CONSISTENT.** The whole interval lies inside a two-sided band, lo no greater than l and u no greater than hi, and the interval does not reach both the null and the size that matters. CONSISTENT is available only for a two-sided band.
- **CANNOT_TELL.** None of the above holds. Exactly one reason is required, from the closed list below.

With an open edge, the comparison at that edge uses the other inequality. For an open hi, ABOVE needs l no less than hi and CONSISTENT needs u less than hi.

### 6.3 The reasons for CANNOT_TELL

- **STRADDLES_EDGE.** The interval overlaps a bound of the figure or band.
- **TOO_WIDE_TO_RESOLVE.** The interval reaches both the null, meaning zero or the figure, and the size that would matter.
- **NO_INTERVAL_FORMABLE.** No width can be formed. This includes a claim that states no number and a computation that is degenerate, such as a zero denominator.

A CANNOT_TELL on a code, fault or guard is a status and carries one status reason instead: NOT_RELEASED, UNREADABLE or METHOD_UNSTATED. Where a status rests on a reading, as for QIA-F7 and FLT-44, a status of CANNOT_TELL carries the outcome reason of that reading. The reason is required in standard_v1.json and in standard_v1.schema.json.

### 6.4 Decision order

Apply these in order. The first that holds decides.

1. If no interval can be formed, the outcome is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.
2. Both-alternatives test. If the interval reaches both the null and the size that matters, the outcome is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, whatever else the interval touches. This holds even when the interval lies wholly inside the band. The interval reaches the size that matters when it contains the null plus or minus that size, in the direction or directions the plan names.
3. Otherwise ABOVE, BELOW or CONSISTENT as defined in 6.2.
4. Otherwise CANNOT_TELL with reason STRADDLES_EDGE.

A plan that reads a departure from a null names the size that matters. Without it, step 2 cannot be applied and the recount says so.

**A point figure.** A point figure needs a tolerance, an equivalence margin named before the read. The band is the figure plus or minus the tolerance. Without a tolerance, CONSISTENT is not available. The reading is ABOVE when l is above the figure, BELOW when u is below it, and otherwise CANNOT_TELL with reason STRADDLES_EDGE.

**A one-sided threshold.** A reading read against a single bound is ABOVE that bound, BELOW that bound, or CANNOT_TELL. CONSISTENT applies only to a two-sided band.

### 6.5 Interval method and level

The interval method and its level are named in the plan before the read. A changed level is a new reading. It is reported beside the first reading and does not replace it. A method changed after the read is also a new reading.

When a reading is a share of items, the method is stated, for example a Wilson interval at 95 percent. A reading that is not a proportion, such as a ratio, a mean or a rank, needs its interval method named too. The rule is as follows.

- Name the method, the level and the unit that is resampled or modelled. A value with a standard error is not an interval until the multiplier and the level are named.
- A ratio is given an interval on a scale the plan names, such as the log scale, or by resampling.
- A mean is given a t interval or a resampling interval.
- A rank, or a statistic computed from ranks, is given a resampling or permutation interval over the unit the claim ranks across.
- For any resampling method, name the number of draws and the seed.
- If no method was named, or the named method cannot be applied to what was released, the reading has no interval under this standard and is CANNOT_TELL with reason NO_INTERVAL_FORMABLE.

### 6.6 Failed reads

A failed read of a source, by a failed fetch or a failed parse, is recorded as NOTHING_RETURNED. It is a status of the read. It is never an outcome of the claim and is never counted with the readings that agree or with those that disagree.

One failed read gets exactly one state. The state follows the purpose of the read. A source read as an input to a reading, such as one row of a table of readings, is NOTHING_RETURNED when its fetch or parse fails. A released file of the claim read as the object of a code or fault test is CANNOT_TELL with reason UNREADABLE when it cannot be read, and is not also recorded as NOTHING_RETURNED. If one read serves both purposes, it is recorded once, as UNREADABLE on the code or fault, and a reading that depends on it is CANNOT_TELL with reason NO_INTERVAL_FORMABLE that names it.

### 6.7 Counts beside every headline share

Beside every headline share the recount prints the count of NOTHING_RETURNED and the share of CANNOT_TELL, split by reason. The counts of each reason add up to the CANNOT_TELL count. Rows that are NOTHING_RETURNED are listed apart and are not in the numerator or the denominator of the headline share. A headline share that omits these counts does not conform. This is REQ-13.

### 6.8 Worked example

Test A of a Heuremen LLC recount plan compared three values on a published results page, the overall percentile, the release month and the system type, with the same three values in each system’s own report. There were 27 systems. The expected share of disagreements is zero. The plan named a Wilson interval at 95 percent. It said ABOVE if the lower end is above 0.05 and CONSISTENT if the upper end is below 0.15, and otherwise CANNOT_TELL. The read found 0 disagreements of 27, with no failed reads. The Wilson 95 percent interval is [0, 0.125]. The plan recorded CONSISTENT, because 0.125 is below 0.15.

How it reads under this standard.

- The method and level were named before the read. Step 1 does not apply.
- The plan’s figure is zero with a margin of 0.15, a band [0, 0.15) that is open at the upper edge.
- The plan names no separate size that matters. Its ABOVE bound of 0.05 is the share of disagreements it treats as a departure from zero, and it is taken here as the size that matters.
- The interval [0, 0.125] contains zero and contains 0.05. At step 2 the reading is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE.

So the reading no longer reads CONSISTENT under this standard. 0 of 27 cannot separate zero from 5 percent. Note that the plan’s two numbers do not agree with each other. A share of 0.05 would be flagged as a departure, yet CONSISTENT was allowed up to 0.15. Under this standard CONSISTENT would need the upper end below 0.05, which at 95 percent takes 0 disagreements of 73 or more. A plan that named 0.15 as the size that matters would read this result CONSISTENT, and that choice has to be made before the read. The plan itself is unchanged and its recorded outcome stands under the rules it named. Beside this headline a recount under 2.0.0 prints 0 NOTHING_RETURNED, and a CANNOT_TELL share of 1 of 1, all TOO_WIDE_TO_RESOLVE.

The record is in standard_v1.json under worked_examples.

## 7. Process-level guards

Guards are listed by the part of the work where they run. The published guard names are kept, see https://heuremen.org/guards.pdf. The Addresses line of each guard is a link assembled by Heuremen LLC by matching topics, because the published documents do not cross-reference one another, see section 11.

A guard is applied when a receipt shows it ran before the number was stated. It is not applied when the released material shows it was skipped or run after the number was stated. It is cannot tell when no receipt exists and the material does not show either way, with reason NOT_RELEASED, when a receipt cannot be read, with reason UNREADABLE, or when the method is too loosely stated to show whether or when it ran, with reason METHOD_UNSTATED. It is not applicable when the occasion for the procedure did not arise in the claim. Where the guard addresses faults, that is when every fault it addresses is NOT_APPLICABLE. The test of every guard is a Heuremen LLC test.

### Part I. Procedures that run before the work

**GRD-01 The ruler is chosen before the quantity is computed** Addresses: FLT-15, FLT-16, FLT-19.

**GRD-02 Reference material is loaded hot, not summarised** Addresses: none.

**GRD-03 The baseline is constructed and written down first** Addresses: FLT-01, FLT-05.

**GRD-04 The instrument is tested as an object before it is pointed at anything** Addresses: FLT-12, FLT-23.

**GRD-05 Per-unit constants are removed, not caveated** Addresses: FLT-08.

**GRD-06 The setup is equalised across every column being compared** Addresses: FLT-09.

### Part II. Procedures that run during the work

**GRD-07 Exact nulls in preference to resampling, wherever one exists** Addresses: none.

**GRD-08 Four outcomes, never two, and the terminating reason on every call** Addresses: FLT-19, FLT-21.

**GRD-09 Every reported figure carries its own n, and the n it was selected from** Addresses: FLT-03.

**GRD-10 Saturated cells are counted before anything is aggregated** Addresses: FLT-10.

**GRD-11 Dependence is priced by independent units, not by rows** Addresses: FLT-06.

**GRD-12 One event is read from three seats, never two** Addresses: FLT-11, FLT-13, FLT-14.

**GRD-13 An absence gets the same scrutiny as a presence** Addresses: FLT-44.

### Part III. Procedures that run on the output

**GRD-14 The row is written at the moment of the catch, before the corrected number is stated** Addresses: FLT-04.

**GRD-15 A dropped arm is named in the tool's own output, not quietly replaced** Addresses: none.

**GRD-16 The wrong first reading is published beside the corrected one** Addresses: none.

**GRD-17 Every report closes with four parts** Addresses: none.

**GRD-18 Writes are guarded by assertions that block partial application** Addresses: none.

**GRD-19 Loops are bounded, and long work is not held open by a session** Addresses: none.

**GRD-20 Retained rules carry what they rest on** Addresses: FLT-42.

### Part IV. Procedures against the instrument being wrong about itself

**GRD-21 Any count about your own behaviour is read from the record, never from memory** Addresses: FLT-22.

**GRD-22 Every rate states its denominator** Addresses: FLT-24.

**GRD-23 A detector remembers what it has already flagged** Addresses: FLT-28.

**GRD-24 The third seat must be able to disagree** Addresses: FLT-26.

**GRD-25 The outside reviewer is handed the evidence, or its verdict is discarded** Addresses: FLT-27.

**GRD-26 Values get a separate check from structure** Addresses: FLT-30.

**GRD-27 Both sides of every identity are evaluated before it is printed** Addresses: FLT-29.

**GRD-28 The prior-art check runs before the significance calculation, not after** Addresses: FLT-33.

**GRD-29 Units are checked across every point before anything is fitted** Addresses: FLT-32.

**GRD-30 A load-bearing relationship is re-read live before anything stands on it** Addresses: FLT-36.

**GRD-31 After any change, the value is re-read through the path that consumes it** Addresses: FLT-37.

**GRD-32 Liveness is checked by recent completed work, never by a running process** Addresses: FLT-38.

**GRD-33 Test writes go somewhere the live path does not read** Addresses: FLT-39.

**GRD-34 A named gap is fixed if fixing is cheaper than describing it** Addresses: FLT-40.

**GRD-35 A residual bin is refused by the scorer, not avoided by the scorer's author** Addresses: FLT-21.

**GRD-36 The catalogue's families ride in front of every exchange, read live from the published source** Addresses: FLT-41.

**GRD-37 The diagnosis and the replacement instrument ship in the same document** Addresses: FLT-20.

**GRD-38 The ruler is named in the output, beside the number** Addresses: FLT-19, FLT-25.

**GRD-39 Business copy passes a tone gate that refuses persuasion** Addresses: FLT-45.

## 8. What a conforming recount must publish

Conformance is a self-declaration of method, not an assessment or a certificate. A recount is declared conforming by its author when it publishes every item below. A recount that omits an item says so and is not declared conforming.

**REQ-01 Name the ruler before the number.** The instrument and the question it answers are named in the output, beside the figure, and were chosen before the quantity was computed. Guards: GRD-01, GRD-38.

**REQ-02 Write the baseline down first.** Sample counts, windows, averaging and the number of places examined are written down for every arm before the measurement arm is computed. Guards: GRD-03, GRD-06.

**REQ-03 State the data source.** Each input names where it came from. Raw copies of every source read are kept with their SHA-256 hashes. Guards: none.

**REQ-04 State the version read.** The version, edition or retrieval date of every source, and the version of this standard, are stated with the date and time of the read. Guards: none.

**REQ-05 Use reading outcomes.** Every reading is reported as ABOVE, BELOW, CONSISTENT or CANNOT_TELL against a figure, band or bound named in advance, with its edge convention, its tolerance for a point figure, and the size that matters where the reading is a departure from a null. Every CANNOT_TELL carries one reason from the closed list in section 6. A failed read of a source is reported as NOTHING_RETURNED. Guards: none.

**REQ-06 Give each reading its interval and level.** Every reading carries its interval, the method and the level of that interval, its n, and the n it was selected from where it is a selection. The method and level are named in the plan before the read. A changed level is a new reading and is reported beside the first. Every rate names its denominator. Guards: GRD-09, GRD-22.

**REQ-07 Test the instrument first.** The instrument is run on a case it must pass and a case it must fail before it is pointed at the claim. Both results are recorded. Guards: GRD-04.

**REQ-08 Publish receipts.** Every number in the recount links to the file, row or run it came from, so a reader can rerun it. Guards: GRD-14, GRD-21.

**REQ-09 Name dropped material.** Any run, row or arm that is discarded is named in the output with the reason and what replaced it. Guards: GRD-15.

**REQ-10 Publish corrections beside the first reading.** A reading that is later corrected stays in the record beside the correction and its reason. Guards: GRD-16.

**REQ-11 Keep CANNOT_TELL as its own result.** CANNOT_TELL is never folded into pass or fail, and never counted as agreement or as disagreement. The two guards cited here carry the principle of never folding and nothing else in this standard. Guards: GRD-08, GRD-35.

**REQ-12 State what was not tested.** The recount lists every code, fault and guard that was not tested and why. An entry marked NOT_APPLICABLE was tested for applicability and is listed with its reason. Guards: none.

**REQ-13 Print the counts beside every headline share.** Beside every headline share the recount prints the count of NOTHING_RETURNED and the share of CANNOT_TELL, split by reason. The reasons are the outcome reasons for readings and the status reasons for statuses. Guards: none.

A recount declared conforming states at its head: Recounted under Faults and Guards version 2.0.0, declared by its author as following the method, not assessed.

## 9. Versioning and change policy

- The version has three parts, major.minor.patch.
- A major change alters what an existing ID means, what a status rule says, or how an outcome is decided. A recount made under an earlier major version stays valid under that version and says so.
- A minor change adds a code, fault or guard, or adds a requirement for a recount. A new item receives the next unused ID.
- A patch change corrects wording, spelling or a link and does not alter meaning.
- IDs are never reused and never renumbered. A retired item stays in the document marked retired, with the reason and the version it was retired in.
- The names, titles and published text of faults and guards, and the names and definitions of the codes, are carried unchanged from the published Faults, Guards and QIA Key documents. A change to that wording is made first in the source document and then here. The tests, rules and links are Heuremen LLC’s and change under this policy.
- Every version is kept at a fixed address with its date. The change log lists every change since the version before it.
- A recount names the version it used. A reader can reproduce it by reading that version.
- Corrections to a released version are published as a patch with the first wording kept beside the corrected one.

## 10. Citation

Heuremen LLC. Faults and Guards, version 2.0.0. 2026. https://doi.org/10.5281/zenodo.24164794. All versions: https://doi.org/10.5281/zenodo.24164029. https://indahl.ai/standard

## 11. Provenance of tests and links

**Published wording.** The following is carried from published documents.

- The ID numbers and the names of faults and guards, and the family and part titles, as published in Faults (https://heuremen.org/faults.pdf) and Guards (https://heuremen.org/guards.pdf).
- The published_text of each fault and guard, carried unchanged from those documents.
- The names and definitions of the claim-level codes, as published in the QIA Key (https://indahl.ai/qia/key).

**Heuremen LLC’s own wording.** The following was written by Heuremen LLC for this standard. It is not published wording of the documents named above.

- Every test, in every entry, including the test of each claim-level code, fault and guard. Each carries the source label Heuremen LLC test.
- Every Needs line, every Evidence label, every Present rule, Absent rule, Applied rule and Not applied rule, every Cannot tell rule and every Not applicable rule.
- Every link from a code to a fault and every link from a guard to a fault.
- The reading outcomes and the rules for reading them, the reason lists, the requirements and the checklist.
- The crosswalk to NIST AI RMF 1.0.

Each test in section 4, section 5 and section 7 and in standard_v1.json carries a source field. Its value is published for wording carried from a published document and Heuremen LLC test for a test written for this standard. Every test in this version has the value Heuremen LLC test. The text_source field of an entry gives the published document its name and published_text come from.

**How the tests and links were made.** The test of each fault is built from the repair sentence in the published entry. The definition field of each fault is its published title, because the first sentence of many entries is an account of the day it happened. The links from guards to faults were assembled by matching topics, because the published documents do not cross-reference one another. Two published links exist, Guard 22 naming Fault 24 and Guard 39 naming Fault 45, and both are kept. The links from codes to faults were assembled in the same way. The fault list in the published Faults document is in family order with some numbers out of sequence, and the numbers are kept as published.

**Wording differences from the published documents.** The published Faults and Guards introductions speak of failure modes of a language model. This standard applies the same names to measurement and analysis claims generally and does not change the published names. The published Faults document marks parts as families and the published Guards document marks them as parts, and this standard keeps both words.

**Reading outcomes.** The QIA Key says only that a reading is stated as above, below, consistent or cannot tell against the figure it is read against. The band, edge, tolerance, one-sided and both-alternatives rules in section 6 and the reason lists are Heuremen LLC’s.

**Crosswalk.** The crosswalk to NIST AI RMF 1.0 is Heuremen LLC’s reading and gives a closest category and not an equivalence. NIST subcategory names are shortened from the text of NIST AI 100-1, January 2023, and the full text should be used when citing. The mappings were checked against the text of that document, and in this version a mapping was removed where the text of the subcategory did not fit the subject of the entry. Many faults map to MEASURE 2.13 because it is the subcategory on the effectiveness of testing, evaluation, verification and validation methods. That reflects the subject of the faults. An ISO/IEC 42001 column is not included because it has not been checked against the licensed standard.

## Changes

**2.0.0 (12 November 2026).** A revision of 1.0.1. Recounts made under 1.0.1 stay valid under 1.0.1 and say so. Several of the changes alter how an outcome or status is decided, which section 9 classes as a major change, so this version is 2.0.0. Every change is listed here.

- Added NOT_APPLICABLE as a fourth status for codes, faults and guards. Each code and fault now has an Applies to line and a Not applicable rule. Each guard has a Not applicable rule.
- Every CANNOT_TELL, as an outcome or as a status, now carries one required reason from a closed list. Outcome reasons are STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE and NO_INTERVAL_FORMABLE. Status reasons are NOT_RELEASED, UNREADABLE and METHOD_UNSTATED. The reason is required in standard_v1.json and standard_v1.schema.json.
- Added the both-alternatives test to section 6. An interval that reaches both the null and the size that matters is CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE, whatever else it touches.
- Defined the band as [lo, hi] with a stated edge convention. A point figure needs a tolerance named before the read. Added the rule for one-sided thresholds. Added a worked example, Test A of a recount plan at 0 of 27, which reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE under this version where the plan recorded CONSISTENT.
- Required the interval method and level to be named in the plan before the read, and made a changed level a new reading.
- Redefined NOTHING_RETURNED as the status of a failed read of a source. An unreadable released file of the claim is CANNOT_TELL with reason UNREADABLE. One failed read gets one state. Required the NOTHING_RETURNED count and the CANNOT_TELL share by reason beside every headline share, as new requirement REQ-13.
- Renamed the set of four outcomes to reading outcomes. Section 6 now states that Fault 21 and Guard 8 of the published Faults and Guards use four outcomes for model replies, a different set. GRD-08 and GRD-35 are cited only for the principle of never folding, in REQ-11. They are no longer cited under REQ-05.
- Added the rule that a reading that is not a proportion needs its interval method named.
- Removed every pointer to the internal notes file. Added section 11, Provenance of tests and links. Added a source field to every test in this document and in standard_v1.json, with the values published and Heuremen LLC test, and a text_source field naming the published document each name comes from.
- Rewrote section 3 and section 9 so that they do not describe the tests as published wording.
- Stated in section 1, section 2, section 8 and the checklist that conformance is a self-declaration of method and not an assessment or certificate.
- Listed the 1.0.1 changes properly, with old and new wording.
- QIA-F2 and FLT-03. Stated their relation. A selected figure with its n printed is QIA-F2 Present and FLT-03 Absent.
- QIA-F5. One rounding rule with no gap between Present and Absent. A cannot tell caused by a missing reading also records QIA-F4 Present.
- QIA-F4. Removed the loop. A method not stated well enough to name the readings is Present with a note. It is no longer cannot tell.
- QIA-F7. Stated how the classical method is chosen and published, tied matches or exceeds to the reading outcomes, and added NOT_APPLICABLE for claims that are not about speed or quality against a classical method.
- QIA-F3. A reading that is not bounded is now NOT_APPLICABLE and no longer cannot tell. QIA-F6. An unreadable released file now has the reason UNREADABLE.
- CHECKLIST.md. Added a not applicable answer with a rule. Every conformance line is numbered to its requirement and every requirement has a line, including REQ-02, REQ-06 and the new REQ-13.
- CROSSWALK.md. The top line now says an empty cell means no close fit. Process notes moved to section 11. Removed seven mappings that did not fit the NIST text: QIA-F7 to MAP 2.3 and MEASURE 1.2, QIA-F2 to MAP 2.3, FLT-20 and FLT-21 to MEASURE 2.13, FLT-22 to MEASURE 1.2, FLT-36 to MEASURE 3.1.
- Changed a run of our own to the recount author’s own run in the definition of a reading.
- Restored the leading The in the title of Family I, as in the published Faults. The other family titles match the published text.
- Linked the published Faults and Guards documents in sections 4, 5, 7 and 11.
- QIA-F1. Kept the verbatim Key wording and added a note that the published definition names the vendor in whose context it was written and that the code applies to any stated reference.
- Added to each fault whose evidence is a process record the statement that on a third-party claim the status is usually CANNOT_TELL with reason NOT_RELEASED, which is expected and not a finding.
- Added REQ-13. Renamed REQ-05 and REQ-11 and extended REQ-05, REQ-06 and REQ-12.
- Set the version to 2.0.0 and added the version DOI and the earlier version DOIs to the header and citation.

**1.0.1 (12 November 2026).** Wording in the tests of two faults made plainer. No code, fault, guard, test or rule changed meaning.

- FLT-05. One adverb removed from the test sentence. New: Enumerate what the setup could produce. Check the baseline was priced against that set. The old wording is in version 1.0.0, https://doi.org/10.5281/zenodo.24164030.
- FLT-23. The test now says who labels the cases and how they are read. New: Score the checker against cases a person labelled after reading each in full. Check the direction of its errors. The old wording is in version 1.0.0, https://doi.org/10.5281/zenodo.24164030.

**1.0.0.** First release, https://doi.org/10.5281/zenodo.24164030.
