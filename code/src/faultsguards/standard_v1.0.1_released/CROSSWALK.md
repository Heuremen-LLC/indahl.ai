# Crosswalk to NIST AI RMF 1.0

Every mapping below is a closest category. None is an equivalence. A closest category is the place in the other document where a reader would most likely look for related material. Where the subcategory or control could not be confirmed, the cell is left empty.

Sources. NIST AI 100-1, Artificial Intelligence Risk Management Framework (AI RMF 1.0), January 2023, read from https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf. Subcategory names below are shortened from the text of that document. An ISO/IEC 42001 column will be added once it can be checked against the licensed standard.

## Claim-level codes

| ID | Name | NIST AI RMF closest category |
|---|---|---|
| QIA-F1 | Self-built reference | MAP 2.3, MEASURE 2.1, MEASURE 2.13 |
| QIA-F2 | Selected result | MAP 2.3, MEASURE 2.5 |
| QIA-F3 | Reading without a width | MEASURE 1.1, MEASURE 2.5 |
| QIA-F4 | Reading not released | MEASURE 2.1, MEASURE 2.8 |
| QIA-F5 | Number recomputes differently | MEASURE 2.5, MEASURE 2.13 |
| QIA-F6 | Text differs from own table | MEASURE 2.8, MEASURE 2.9 |
| QIA-F7 | Classical comparison available | MAP 2.3, MEASURE 1.2 |

## Process-level faults

| ID | Name | NIST AI RMF closest category |
|---|---|---|
| FLT-01 | The baseline averaged, counted or searched differently from the measurement | MAP 2.3, MEASURE 2.13, MEASURE 2.1 |
| FLT-02 | A fixed threshold against a statistic that grows with n | MEASURE 2.5, MEASURE 2.13 |
| FLT-03 | A maximum over many draws reported as a measurement | MEASURE 2.5, MEASURE 2.13 |
| FLT-04 | The in-sample fit, including its most disguised form | MAP 2.3, MEASURE 2.5 |
| FLT-05 | A continuum assumed where only discrete values were reachable | MAP 2.3, MEASURE 2.13 |
| FLT-06 | Dependent observations counted as independent | MAP 2.3, MEASURE 2.13 |
| FLT-07 | Time-asymmetric differencing | MAP 2.3, MEASURE 2.13 |
| FLT-08 | A per-unit constant read as signal | MEASURE 2.13 |
| FLT-09 | An unequal setup across the columns being compared | MAP 2.3, MEASURE 2.13, MEASURE 2.1 |
| FLT-10 | Saturated or censored cells averaged as data | MEASURE 2.13 |
| FLT-11 | One artifact's internal record used as a second, independent reading | MEASURE 2.13 |
| FLT-12 | The pilot that came out perfect | MEASURE 2.13 |
| FLT-13 | Calibrating away the difference between two seats | MAP 2.3, MEASURE 2.13 |
| FLT-14 | Forcing agreement between quantities that cannot be commensurate | MAP 2.3, MEASURE 2.13 |
| FLT-15 | A magnitude taken where the last step produced two numbers | MEASURE 2.13 |
| FLT-16 | A sum assumed where two effects multiply | MEASURE 2.13 |
| FLT-17 | Asking which way a sign points instead of whether it holds | MEASURE 2.13 |
| FLT-18 | A snapshot that keeps the value and throws away the trajectory | MEASURE 2.13 |
| FLT-19 | A ruler that cannot say “I cannot tell” lies at scale | MEASURE 1.1, MEASURE 3.2 |
| FLT-20 | The two-answer question that has three answers | MEASURE 2.13 |
| FLT-21 | Four outcomes collapsed into two | MEASURE 2.13 |
| FLT-22 | You will report a count about yourself from memory | MEASURE 1.2 |
| FLT-23 | Your own checker will be wrong, and all in one direction | MEASURE 1.2 |
| FLT-24 | Every count has a ruler hidden inside it, and the rulers disagree | MEASURE 2.1 |
| FLT-25 | A verdict without a width is not a verdict | MEASURE 2.5, MEASURE 2.9 |
| FLT-26 | Two of your three seats are the same seat | MEASURE 2.13 |
| FLT-27 | A reviewer handed no evidence is measuring your tone | MEASURE 1.3 |
| FLT-28 | The same fault counted as five successes | MEASURE 2.13 |
| FLT-29 | An equals sign is a claim, and you will print one you have not checked | MEASURE 2.13 |
| FLT-30 | A fabricated number passes every check that reads shape | MEASURE 2.13 |
| FLT-31 | Counting mentions and reporting it as measurement |  |
| FLT-32 | Fitting a sequence whose points are on different axes | MEASURE 2.13 |
| FLT-33 | Computing the significance before checking the literature | MAP 2.3 |
| FLT-34 | A pattern found twice is a pattern, not a law |  |
| FLT-35 | The correspondence with the deepest history proves the least |  |
| FLT-36 | The relationship the whole structure rests on is not a constant | MEASURE 3.1 |
| FLT-37 | Something long-lived is holding an old copy of what you just changed |  |
| FLT-38 | The absence of a process is not the absence of work |  |
| FLT-39 | Your test data will become a finding about innocent work |  |
| FLT-40 | Naming the gap becomes the whole transaction |  |
| FLT-41 | Writing a failure mode down did not stop it |  |
| FLT-42 | A rule from a single instance given a theorem's authority |  |
| FLT-43 | Narrating the mechanism instead of using it |  |
| FLT-44 | A result that does not resolve, filed as a null | MEASURE 1.1, MEASURE 2.5 |
| FLT-45 | Explaining the work instead of stating it |  |

## NIST subcategories used

- MAP 2.3. Scientific integrity and TEVV considerations are identified and documented.
- MEASURE 1.1. Approaches and metrics for measurement of AI risks are selected, and what cannot be measured is documented.
- MEASURE 1.2. Appropriateness of AI metrics and effectiveness of existing controls are regularly assessed and updated.
- MEASURE 1.3. Internal experts and/or independent assessors are involved in regular assessments.
- MEASURE 2.1. Test sets, metrics, and details about the tools used during TEVV are documented.
- MEASURE 2.5. The AI system is demonstrated to be valid and reliable, with limits of generalizability documented.
- MEASURE 2.8. Risks associated with transparency and accountability are examined and documented.
- MEASURE 2.9. The model is explained, validated and documented, and output is interpreted within its context.
- MEASURE 2.13. Effectiveness of the employed TEVV metrics and processes is evaluated and documented.
- MEASURE 3.1. Approaches are in place to regularly identify and track existing, unanticipated and emergent AI risks.
- MEASURE 3.2. Risk tracking approaches are considered where risks are difficult to assess with available measurement techniques.

## What could not be confirmed

- The NIST names are shortened. Use the full text of the subcategory in AI 100-1 when citing.
- The NIST Playbook text was read only for MEASURE 1.1 to 2.11 on the web page. The IDs for all other functions were confirmed from the PDF.
- Faults left with no NIST mapping: FLT-31, 34, 35, 37 to 43, 45. No subcategory was a close enough fit to name.
- Many faults map to MEASURE 2.13 because it is the subcategory on the effectiveness of TEVV methods. That reflects the subject of the faults and is not a finding about NIST.