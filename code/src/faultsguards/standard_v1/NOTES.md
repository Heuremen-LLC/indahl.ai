# Notes on the draft (internal)

Working notes for the owner. Not part of the standard. Draft of 12 November 2026.

## What was left out
- No new faults, codes or guards were added.
- Published texts of Faults and Guards were not reproduced in STANDARD.md beyond names. Full text sits in standard_v1.json under published_text, verbatim from src/faultsguards/data.
- The Faults and Guards sections on the ledger score (26 in-sample instances, 4 caught, 7.7 percent, prospective ledger to row 608), the removed guards, the "what is not guarded" list and "how to argue with these documents" were not made into entries. They are statements about the method, not tests. They could go in an appendix.
- The Q codes (Q1 to Q23, IBM and Braket calibration problems) were left out. Only F codes were requested. Q codes are a candidate for a quantum-specific annex.
- Clause-level ISO/IEC 42001 mapping (clauses 4 to 10) was left out, see CROSSWALK.md.

## Gaps seen, not filled
- No published guard addresses faults 2, 7, 17, 18, 31, 34, 35, 43. They show as "none" in the guards field.
- Guards 2, 7, 15, 16, 17, 18, 19 have no clear fault they address in the published text. Several (16, 17, 18, 19) are working-practice guards.
- No claim-level code covers a result with no stated figure to read against, or a claim that moves after publication (a changed score or silent edit). Faults 37 and the "published scores kept" test in the example desk are the nearest.
- No code for a comparison made after the data without saying so, other than fault 4. F2 and F1 cover part of it.
- F4 and F5 overlap. A number that cannot recompute because data is missing is both. The standard says record F4 beside cannot tell on F5.
- The faults marked process record (22 to 28, 33 to 43) can rarely be tested from a third party's released material. They will read cannot tell for most outside claims. Option for v1.1: split them into a separate "own-process" part of the conformance statement.

## Decisions I made that need your call
1. Fault-to-guard links and code-to-fault links are assembled by me by topic. The published documents do not cross-reference each other, except Guard 22 naming Fault 24 and Guard 39 naming Fault 45. All links are marked as assembled in STANDARD.md section 7.
2. The per-fault tests are my wording, built from the repair sentence in each published entry. The definition field of each fault is its published title, because many first sentences are anecdotes with figures from the day.
3. Interval rule for the four outcomes (section 6) generalises the rule in the example desk plan: ABOVE when the lower end clears a bound, CONSISTENT when the upper end is below a bound, CANNOT_TELL otherwise. I wrote ABOVE, BELOW and CONSISTENT as whole-interval-versus-band statements. The Key says only "above, below, consistent or cannot tell against the figure it is read against". The exact CONSISTENT rule for a point figure is not published anywhere I found.
4. NOTHING_RETURNED is kept as a status of a read, not a fifth outcome, since you described four outcomes. The package PLAN lists it beside the four.
5. Checklist: conformance is lines 14 to 23, claim findings are lines 1 to 13. No total score is printed, by design.
6. Licence. The package licence allows reading and citing but forbids use of the text to train or build models. A standard meant to be applied by third parties may need an explicit statement on whether applying it inside a prompt or tool is permitted, as the package README says. I did not draft licence text.
7. No DOI or address exists yet. STANDARD.md section 10 has a placeholder. Zenodo new-version flow would give one.
8. Repository naming. IDs are QIA-F1 to QIA-F7, FLT-nn, GRD-nn. The Key calls them F1 to F7, which collides visually with fault numbers. Short form F1 to F7 is kept in the code field.

## Wording conflicts between sources
- Four outcomes. Faults entry 21 and Guards 8 use committed, held open, refused, nothing-returned for model replies. The QIA Key and package PLAN use ABOVE, BELOW, CONSISTENT, CANNOT_TELL for readings. Both are published as "four outcomes". The standard uses the second set and does not use the first. A reader of the Faults PDF may be confused. Suggest naming the first set "reply states" in the next revision of Faults.
- Faults intro says the catalogue is of failure modes "a language model" commits. The Guards intro says the same. The task is wider (analysts, quantum measurement). The standard says "measurement or analysis" without changing the published names.
- The Key defines F1 as a reference "built from the same setup or from IBM's stated figures". The vendor name is kept as published in the code definition. A neutral rewording ("a vendor's stated figures") would be a major-version-neutral patch if you want it.
- Faults Part VIII is titled "When the guard becomes the deliverable" and Guards Part IV is titled "Procedures against the instrument being wrong about itself". Part numbering differs (eight families against four parts). The standard keeps both and labels them family and part.
- Date in the published documents is "revised 30 October 2026". The IDs 44 and 45 sit out of family order, consistent with the stated rule that numbers are stable.
- The Key page says "Quantum Idle Audit". The standard uses the code names only.

## Open questions
- Should v1.0 carry a worked example, one recount from start to receipts, in an appendix. The example desk plan is the natural candidate.
- Should the standard define a short claim record format (JSON) for a recount, beyond the schema for the standard itself.
- Should CANNOT_TELL on a code carry a reason code (not released, unreadable, method unclear). It would help auditors.
- Who may declare a recount conforming. As drafted anyone may, and the recount carries its own receipts.

## Checks run
- standard_v1.json validates against standard_v1.schema.json (jsonschema, draft 2020-12).
- STANDARD.md, CHECKLIST.md and CROSSWALK.md contain no semicolons. They do not name any benchmark body.
- Counts in the crosswalk are in the report to the owner and not in any heading.
