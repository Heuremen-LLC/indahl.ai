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
