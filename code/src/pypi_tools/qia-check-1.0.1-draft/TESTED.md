# How this package was tested

Heuremen LLC, 2 November 2026, on the package as published at https://indahl.ai/qia/qia-research-package.zip

1. Against our mirror's audit code. For the latest published calibration record of each of seven IBM processors (ibm_aachen, ibm_boston,
   ibm_fez, ibm_kingston, ibm_marrakesh, ibm_phoenix, ibm_pittsburgh), `qia_check.py before` was compared with the separate audit code that
   runs our public IBM mirror (https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/mirror). The T2 above 2 x T1 flags, with their
   outcomes, and the T1 and T2 date-gap flags agreed qubit for qubit on all seven. Both were written by us to the same rules, so this shows
   the two implementations agree. It does not test the rules themselves.
2. Against 362 saved ibm_kingston records. The before checks were recounted with separate code, and every count agreed on every record.
3. On a real run. Our Darkwave kit test jobs ran on ibm_kingston from 01:11 to 01:17 UTC on 2 November 2026, and each job saved the
   calibration record it ran under. `qia_check.py after`, given the six records our mirror saved that evening, named the same record
   (stamped 00:39 UTC) and reported no record stamped during the run. No record was stamped in that window, so the part of the check that
   lists records stamped during a run was exercised on test files only, not on this run.
4. The pull path. `qia_check.py before --pull ibm_kingston` saved the live record from IBM and checked it. The saved file was unchanged
   after the check (sha256 before and after equal). Our test passed our own IBM connection in place of a saved account. The saved-account
   step itself (QiskitRuntimeService with no arguments) is IBM's own code.

Not yet tested inside this package: the YO reader (`yo/yo_audit.py`) against the model. YO itself is scored against the exact code
answer on held-out IBM records at https://indahl.ai/iris/lab

## Version 1.0.1 (DRAFT, not published)

How 1.0.1 was tested, from the record:

1. An outside break of the published 1.0.0. A referee installed qia-check 1.0.0 from PyPI in a clean environment, read the source, and ran 27
   fixtures and 16 short reproducers against it. 1.0.0 scored 5 HOLDS, 20 HOLE and 2 CANNOT TELL. The holes came from 16 causes.
2. The same referee scored each 1.0.1 draft by what its output says about each fixture, raw and with the run time pinned to the fixtures' stamp.
   The scores went 22/2/3, then 24/0/3, and held at 24 HOLDS, 0 HOLE, 3 CANNOT TELL through every later draft. The 3 CANNOT TELL are cases the
   package does not read (gates and zz) or cannot exercise.
3. Against real records. 577 saved ibm_kingston records (362 in the package test set and 215 from our mirror on 4 Nov) were checked with the 1.0.1 code. No FUTURE row fired on any of them. The only UNKNOWN rows
   on real data are qubits IBM publishes with no T1 or T2 at all (qubit 146 in every one of the 362 test records, and further T2 gaps). 1.0.0 passed
   those qubits silently. The referee checked 8 of these records on a separate machine and reconciled every count.
4. Behaviour changes between drafts are listed in FIXES_1.0.1_DRAFT.md, each with the reproducer or fixture that shows it.
