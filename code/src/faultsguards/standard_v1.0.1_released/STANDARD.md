# Faults and Guards, version 1.0.1

Heuremen LLC. Released 12 November 2026. Version 1.0.1, https://doi.org/10.5281/zenodo.24164207. All versions: https://doi.org/10.5281/zenodo.24164029. Web: https://indahl.ai/standard

This standard sets out how to check a claim about an AI or quantum measurement result, and how to publish the check so that anyone can rerun it. It gives each failure a stable ID, a test, and a rule for saying present, absent or cannot tell. It is written to be cited and applied by an auditor, an insurer, a regulator, a journalist or a reader.

## 1. Scope

This standard applies to claims that report a measured result for an AI model, an AI benchmark, a quantum device or an analysis of either. It covers two levels. Claim-level codes describe what is off in a published claim and can be tested from what the claim released. Process-level faults and guards describe how a measurement or analysis goes wrong and what procedure is built against it.

It does not rank systems. It does not say whether a system is safe, good or fit for a purpose. It says whether a number can be rechecked, whether it recomputes, and what the recount found. A conforming recount of a claim gives readings and codes. It does not give a certificate.

## 2. Terms

**Claim.** A statement of a measured result, with the number, the setup and the material released with it.

**Recount.** A fresh computation of a claimed number from the material the claim released.

**Reading.** A value from a recount, from the claim, or from a run of our own, with its interval and the level of that interval.

**Figure or band.** The number or range a reading is read against. It is named before the reading is computed.

**Ruler.** The instrument and the question it answers. A value with a standard error is one ruler. A p-value is another. A ruler is named beside the number.

**Receipt.** A file, row, run or hash that lets a reader reproduce a number.

**Released material.** Everything the claim published, in the paper, its files and the sources it names.

**Code.** A claim-level code from QIA-F1 to QIA-F7.

**Fault.** A process-level failure mode with an ID of the form FLT-nn. The number is the one assigned in the published Faults document and never changes.

**Guard.** A procedure built against faults with an ID of the form GRD-nn. The number is the one in the published Guards document.

**Present, absent, cannot tell.** The three statuses of a code or fault. Cannot tell means the material needed for the test was not released or could not be read.

**Applied, not applied, cannot tell.** The three statuses of a guard.

**Outcome.** One of ABOVE, BELOW, CONSISTENT, CANNOT_TELL. See section 6.

## 3. How to read the entries

Every entry has a stable ID, a one-sentence definition, a test, and rules for the three statuses. Faults and guards keep the wording of the published Faults and Guards documents. The full published text of each is in standard_v1.json under published_text.

A status is a statement about the claim and the material released with it. Cannot tell is a result. It is not a pass and it is not a fail.

## 4. Claim-level codes

These codes keep the wording of the QIA Key at https://indahl.ai/qia/key.

### QIA-F1 Self-built reference

Definition: Results are compared with a reference built from the same setup or from IBM’s stated figures.

Test: Find the reference the result is compared with. Read how it was built.

- Present: The reference was built from the same setup as the result, or from the vendor’s stated figures.
- Absent: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
- Cannot tell: The paper does not say how the reference was built.

Related faults: FLT-01, FLT-11

### QIA-F2 Selected result

Definition: The headline figure is a selected value: a maximum over rows, a best case, or a projection.

Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.

- Present: The headline figure is a maximum over rows, a best case, or a projection.
- Absent: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
- Cannot tell: The rows the figure came from are not released.

Related faults: FLT-03

### QIA-F3 Reading without a width

Definition: A bounded reading is stated as yes or no, without an interval.

Test: Find each reading that has a bound. Check whether it is stated with an interval and the level of that interval.

- Present: A bounded reading is stated as yes or no with no interval.
- Absent: Each bounded reading carries an interval and its level.
- Cannot tell: The reading is not bounded, or the counts needed to form an interval are not released.

Related faults: FLT-25

### QIA-F4 Reading not released

Definition: A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.

Test: List the readings the claim depends on. Check each one against the paper and its files.

- Present: At least one needed reading is missing from the paper and its files.
- Absent: Every needed reading is in the paper or its files.
- Cannot tell: The list of needed readings cannot be fixed because the method is not stated well enough to name them.

Related faults: none

### QIA-F5 Number recomputes differently

Definition: A printed number does not follow from the paper’s own data or arithmetic.

Test: Recompute the number from what the paper released. Compare it with the printed value at the printed precision.

- Present: The recomputed value differs from the printed value beyond rounding.
- Absent: The recomputed value equals the printed value at the printed precision.
- Cannot tell: What is released does not allow the recomputation. Record F4 beside it.

Related faults: FLT-29

### QIA-F6 Text differs from own table

Definition: The text, abstract or caption differs from the paper’s own table, figure or files.

Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.

- Present: A statement or number in the text differs from the table, figure or file it refers to.
- Absent: Every checked statement and number agrees with its table, figure or file.
- Cannot tell: The table, figure or file is not released or cannot be read.

Related faults: none

### QIA-F7 Classical comparison available

Definition: A simple classical method on the same instances matches or exceeds the reported result.

Test: Run a simple classical method on the same instances. Name the method before the run. Compare its result with the reported one.

- Present: The classical method matches or exceeds the reported result.
- Absent: The classical method falls short of the reported result on the same instances.
- Cannot tell: The instances are not released, or the classical method was not run.

Related faults: FLT-01

## 5. Process-level faults

The family names and fault names are as published in Faults. The IDs are the published numbers and are not in family order.

Every fault uses the same status rules. Present means the test finds the pattern in the released material. Absent means the test was run on the needed material and the pattern was not found. Cannot tell means the material named under Needs is not released or cannot be read. Faults marked process record can usually be tested only from the recount author's own records, so for a third-party claim they will often read cannot tell.

### Family I. Baseline built after the measurement it judges

**FLT-01 The baseline averaged, counted or searched differently from the measurement**

Test: Write down for both arms the sample count, the window, the averaging and how many places were examined. Compare. Needs: Setup details of both arms. Evidence: released material. Guards: GRD-03.

**FLT-02 A fixed threshold against a statistic that grows with n**

Test: Ask what the statistic does under the null as n grows. Check whether the threshold grows with it. Needs: Threshold and the statistic's behaviour under the null. Evidence: released material. Guards: none.

**FLT-03 A maximum over many draws reported as a measurement**

Test: Find any best, maximum or peak figure. Check that the n it was selected from is printed. Needs: The n behind each best figure. Evidence: released material. Guards: GRD-09.

**FLT-04 The in-sample fit, including its most disguised form**

Test: Check the order of events. Was the rule fixed before the cases it is scored on, and was any explanation written after the result and counted as a prediction. Needs: Dated record of when rule and cases were fixed. Evidence: process record. Guards: GRD-14.

**FLT-05 A continuum assumed where only discrete values were reachable**

Test: Enumerate what the setup could produce. Check the baseline was priced against that set. Needs: Description of what the setup can emit. Evidence: released material. Guards: GRD-03.

**FLT-06 Dependent observations counted as independent**

Test: Count the independent units that contributed. Check the width came from units and not rows. Needs: Unit structure of the data. Evidence: released material. Guards: GRD-11.

**FLT-07 Time-asymmetric differencing**

Test: Write the temporal order of every arm. Check that differences were taken in the same direction. Needs: Time order of each arm. Evidence: released material. Guards: none.

**FLT-08 A per-unit constant read as signal**

Test: Remove any constant attached to every unit and measure again. Compare with the first reading. Needs: Per-unit data. Evidence: released material. Guards: GRD-05.

**FLT-09 An unequal setup across the columns being compared**

Test: Check that the instrument is identical across the columns compared. Re-run with it equalised and see whether the ordering holds. Needs: Instrument settings per column. Evidence: released material. Guards: GRD-06.

**FLT-10 Saturated or censored cells averaged as data**

Test: Count cells at a ceiling or floor before aggregation. Check they were excluded or reported. Needs: Cell-level values. Evidence: released material. Guards: GRD-10.

**FLT-11 One artifact's internal record used as a second, independent reading**

Test: For each pair of agreeing readings, name the two physically separate things they came from. Needs: Provenance of each reading. Evidence: released material. Guards: GRD-12.

**FLT-12 The pilot that came out perfect**

Test: Treat clean zero-overlap separation as a prompt to run the asymmetry checks for Faults 1 to 11 on the same data. Needs: Setup details for the asymmetry checks. Evidence: released material. Guards: GRD-04.

### Family II. Zeroing a gap that was itself the reading

**FLT-13 Calibrating away the difference between two seats**

Test: Check whether two instruments were aligned to agree and the agreement was reported as accuracy. Needs: Calibration history of the instruments. Evidence: released material. Guards: GRD-12.

**FLT-14 Forcing agreement between quantities that cannot be commensurate**

Test: Ask whether an exact match is arithmetically possible. Check that the gap was not tuned toward an impossible match. Needs: The quantities and their units. Evidence: released material. Guards: GRD-12.

### Family III. The fold that erases the discarded half

**FLT-15 A magnitude taken where the last step produced two numbers**

Test: Find each correlation, lock-in or demodulation output. Check whether amplitude and phase were both kept before any comparison. Needs: The processing steps. Evidence: released material. Guards: GRD-01.

**FLT-16 A sum assumed where two effects multiply**

Test: Check whether a cross term was tested before an additive model was used. Needs: Model and data. Evidence: released material. Guards: GRD-01.

**FLT-17 Asking which way a sign points instead of whether it holds**

Test: Check whether the stability of a sign was measured, as well as its direction. Needs: Repeated runs. Evidence: released material. Guards: none.

**FLT-18 A snapshot that keeps the value and throws away the trajectory**

Test: Check whether the residual was measured at two or more precisions and how it moved. Needs: Readings at more than one precision. Evidence: released material. Guards: none.

### Family IV. The forced verdict, and the answer that was never offered

**FLT-19 A ruler that cannot say “I cannot tell” lies at scale**

Test: Check whether the ruler can return a decline. Re-run with a third verdict if it cannot. Needs: The ruler's verdict set and the cell data. Evidence: released material. Guards: GRD-01, GRD-08, GRD-38.

**FLT-20 The two-answer question that has three answers**

Test: Check whether a situation with three states was reduced to two options. Needs: The question as asked. Evidence: released material. Guards: GRD-37.

**FLT-21 Four outcomes collapsed into two**

Test: Check whether distinct outcomes were collapsed into fewer bins. Each bin needs a single positive definition. Needs: Outcome definitions and the raw rows. Evidence: released material. Guards: GRD-08, GRD-35.

### Family V. The instrument that is wrong about itself

**FLT-22 You will report a count about yourself from memory**

Test: Read the count from the record. Compare with any count stated from memory. Needs: The record the count refers to. Evidence: process record. Guards: GRD-21.

**FLT-23 Your own checker will be wrong, and all in one direction**

Test: Score the checker against cases a person labelled after reading each in full. Check the direction of its errors. Needs: Hand-labelled cases and checker output. Evidence: process record. Guards: GRD-04.

**FLT-24 Every count has a ruler hidden inside it, and the rulers disagree**

Test: Check that each rate names its denominator and that the conclusion survives the other denominators. Needs: Denominators and the underlying counts. Evidence: released material. Guards: GRD-22.

**FLT-25 A verdict without a width is not a verdict**

Test: Check that each verdict is stated with its width. Needs: Verdicts and their stated uncertainty. Evidence: released material. Guards: GRD-38.

**FLT-26 Two of your three seats are the same seat**

Test: For each third reading, name what it would do if the hypothesis were false. Needs: How the third reading was derived. Evidence: released material. Guards: GRD-24.

**FLT-27 A reviewer handed no evidence is measuring your tone**

Test: Check that any outside reviewer was handed the evidence and not only the prose. Needs: Reviewer inputs. Evidence: process record. Guards: GRD-25.

**FLT-28 The same fault counted as five successes**

Test: Check whether one standing fault was counted more than once. Needs: Detector log. Evidence: process record. Guards: GRD-23.

### Family VI. The claim that was never checked

**FLT-29 An equals sign is a claim, and you will print one you have not checked**

Test: Evaluate both sides of every printed equality. Needs: The printed relations and their inputs. Evidence: released material. Guards: GRD-27.

**FLT-30 A fabricated number passes every check that reads shape**

Test: Verify each number against its source, separately from any check of structure. Needs: Source of each number. Evidence: released material. Guards: GRD-26.

**FLT-31 Counting mentions and reporting it as measurement**

Test: Check whether a count of mentions was reported as a measurement. Needs: How the count was produced. Evidence: released material. Guards: none.

**FLT-32 Fitting a sequence whose points are on different axes**

Test: Check units across every point before any fit. Needs: Units of each point. Evidence: released material. Guards: GRD-29.

**FLT-33 Computing the significance before checking the literature**

Test: Check whether the literature check came before the significance calculation. Needs: Dated record of the two steps. Evidence: process record. Guards: GRD-28.

**FLT-34 A pattern found twice is a pattern, not a law**

Test: Check whether a pattern found twice was written into further structures as a law. Needs: Record of where the pattern was applied. Evidence: process record. Guards: none.

**FLT-35 The correspondence with the deepest history proves the least**

Test: Check whether a correspondence is offered as evidence by its history. Closest test only, see NOTES. Needs: The claimed correspondence. Evidence: released material. Guards: none.

**FLT-36 The relationship the whole structure rests on is not a constant**

Test: Re-read the load-bearing relationship live. Compare with the value the structure was built on. Needs: Live access to the relationship. Evidence: process record. Guards: GRD-30.

### Family VII. State, staleness, and work you cannot see

**FLT-37 Something long-lived is holding an old copy of what you just changed**

Test: Re-read the changed value through the path that consumes it. Needs: Access to the consuming path. Evidence: process record. Guards: GRD-31.

**FLT-38 The absence of a process is not the absence of work**

Test: Check liveness by recent completed work and not by a running process. Needs: Job records. Evidence: process record. Guards: GRD-32.

**FLT-39 Your test data will become a finding about innocent work**

Test: Check that test writes go somewhere the live path does not read. Needs: Log destinations. Evidence: process record. Guards: GRD-33.

### Family VIII. When the guard becomes the deliverable

**FLT-40 Naming the gap becomes the whole transaction**

Test: Price the fix of any named gap. Check whether a cheaper fix was left undone. Needs: Gap statements and their cost. Evidence: process record. Guards: GRD-34.

**FLT-41 Writing a failure mode down did not stop it**

Test: Check whether a written-down failure mode recurred after publication. Needs: Dated record. Evidence: process record. Guards: GRD-36.

**FLT-42 A rule from a single instance given a theorem's authority**

Test: Check what each retained rule rests on. A single-instance rule may not be cited as a count. Needs: Basis tags of rules. Evidence: process record. Guards: GRD-20.

**FLT-43 Narrating the mechanism instead of using it**

Test: For each claimed capability, find the line that executes it and confirm it ran. Needs: Code or run log. Evidence: process record. Guards: none.

### Family IV. The forced verdict, and the answer that was never offered

**FLT-44 A result that does not resolve, filed as a null**

Test: Check whether a result that did not resolve was filed as a null. Check whether the reach of the ruler was stated. Needs: Sample size and the width the ruler can resolve. Evidence: released material. Guards: GRD-13.

### Family VIII. When the guard becomes the deliverable

**FLT-45 Explaining the work instead of stating it**

Test: Check whether business copy states offer, receipt and terms or explains and persuades. Needs: The copy. Evidence: released material. Guards: GRD-39.

## 6. The four outcomes

Every reading is reported against a figure or band that was named before the reading was computed. It has one of four outcomes.

- **ABOVE.** The whole interval of the reading lies above the figure or band it is read against.
- **BELOW.** The whole interval of the reading lies below the figure or band it is read against.
- **CONSISTENT.** The interval of the reading lies inside the figure or band it is read against, at a width small enough to say so.
- **CANNOT_TELL.** The interval overlaps an edge of the figure or band, or no interval can be formed from what was released.

The four outcomes are never folded into pass and fail. CANNOT_TELL is never counted with the readings that agree and never counted with those that disagree. A share of CANNOT_TELL is printed beside every headline share.

When a reading is a share of items, the interval is stated with its method and level. A Wilson interval at 95 percent is an example. Bounds for ABOVE and CONSISTENT are written into the plan before the read.

A failed read of a source is recorded as NOTHING_RETURNED. It is a status of the read and is never counted as an outcome of the claim.

Codes and faults use the statuses present, absent and cannot tell. Where a status rests on a numeric reading, the reading is reported with its outcome beside it.

## 7. Process-level guards

Guards are listed by the part of the work where they run. The published guard names are kept. The column of faults addressed was assembled for this standard by matching topics, because the published documents do not cross-reference one another. See NOTES.md.

A guard is applied when a receipt shows it ran before the number was stated. It is not applied when the released material shows it was skipped or run after the number was stated. It is cannot tell when no receipt exists and the material does not show either way.

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

A recount conforms to this standard when it publishes every item below. A recount that omits an item says so and is not conforming.

**REQ-01 Name the ruler before the number.** The instrument and the question it answers are named in the output, beside the figure, and were chosen before the quantity was computed. Guards: GRD-01, GRD-38.

**REQ-02 Write the baseline down first.** Sample counts, windows, averaging and the number of places examined are written down for every arm before the measurement arm is computed. Guards: GRD-03, GRD-06.

**REQ-03 State the data source.** Each input names where it came from. Raw copies of every source read are kept with their SHA-256 hashes. Guards: none.

**REQ-04 State the version read.** The version, edition or retrieval date of every source, and the version of this standard, are stated with the date and time of the read. Guards: none.

**REQ-05 Use four outcomes.** Every reading is reported as ABOVE, BELOW, CONSISTENT or CANNOT_TELL against a figure or band named in advance. A failed read is reported as NOTHING_RETURNED. Guards: GRD-08, GRD-35.

**REQ-06 Give each reading its interval and level.** Every reading carries its interval and the level of that interval, its n, and the n it was selected from where it is a selection. Every rate names its denominator. Guards: GRD-09, GRD-22.

**REQ-07 Test the instrument first.** The instrument is run on a case it must pass and a case it must fail before it is pointed at the claim. Both results are recorded. Guards: GRD-04.

**REQ-08 Publish receipts.** Every number in the recount links to the file, row or run it came from, so a reader can rerun it. Guards: GRD-14, GRD-21.

**REQ-09 Name dropped material.** Any run, row or arm that is discarded is named in the output with the reason and what replaced it. Guards: GRD-15.

**REQ-10 Publish corrections beside the first reading.** A reading that is later corrected stays in the record beside the correction and its reason. Guards: GRD-16.

**REQ-11 Keep CANNOT_TELL as an outcome.** CANNOT_TELL is never folded into pass or fail, and never counted as agreement or as disagreement. Guards: GRD-08.

**REQ-12 State what was not tested.** The recount lists every code and fault that was not tested and why. Guards: none.

A conforming recount states at its head: Recounted under Faults and Guards version 1.0.1.

## 9. Versioning and change policy

- The version has three parts, major.minor.patch.
- A major change alters what an existing ID means, what a status rule says, or how an outcome is decided. A recount made under an earlier major version stays valid under that version and says so.
- A minor change adds a code, fault or guard, or adds a requirement for a recount. A new item receives the next unused ID.
- A patch change corrects wording, spelling or a link and does not alter meaning.
- IDs are never reused and never renumbered. A retired item stays in the document marked retired, with the reason and the version it was retired in.
- Wording from the published Faults, Guards and QIA Key documents is carried unchanged. A change to that wording is made first in the source document and then here.
- Every version is kept at a fixed address with its date. The change log lists every change since the version before it.
- A recount names the version it used. A reader can reproduce it by reading that version.
- Corrections to a released version are published as a patch with the first wording kept beside the corrected one.

## 10. Citation

Heuremen LLC. Faults and Guards, version 1.0.1. 2026. https://doi.org/10.5281/zenodo.24164207. https://indahl.ai/standard


## Changes

1.0.1 (12 November 2026). Wording in the tests of two faults made plainer. No code, fault, guard, test or rule changed meaning. 1.0.0 is https://doi.org/10.5281/zenodo.24164030.
