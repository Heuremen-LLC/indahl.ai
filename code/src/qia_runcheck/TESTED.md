# Check a Run: tested against qia_check.py

Tested 1 November 2026 (records through 2 November 01:23 UTC). The test is `tests/run_compare.py`. It copies the mirror's records, builds the index from the copy with `build_index.py`, runs `qia_check.py` from the QIA Research Package on those same records, runs `runcheck.js` in node against the index, and compares the two outputs exactly. Run it again with `python3 -I tests/run_compare.py`. It prints ALL IDENTICAL or MISMATCH and writes `tests/last_result.json`.

## How the two were run

For each run window the package was run twice through its own command line. `qia_check.py after RECORD_DIR --start --end` gives the record in force at the start, the records stamped during the run and every change in T1, T2 and the readout figures. `qia_check.py before RECORD.json` on the record in force gives the flags. The page code was run through the same loader the page uses, which reads the manifest, then only the day files it needs. The two outputs were compared field by field as text: the record file name, its stamp, the stamps during the run, every flag row (qubit, check, figure, detail, outcome), every change row (record, qubit, figure, before, after, both measurement dates as IBM wrote them) and the list of qubits missing from the record.

## Run windows (UTC)

| Processor | Window | Qubits | Record in force | Stamped during | Flag rows | Change rows | Result |
|---|---|---|---|---|---|---|---|
| ibm_fez | 2026-10-30 11:00 to 12:30 | 0,1,5,70,155 | 2026-10-30 10:50:53 | 3 | 0 | 0 | identical |
| ibm_marrakesh | 2026-10-30 21:55 to 23:10 | 0,1,5,70,155,200 | 2026-10-30 21:50:55 | 3 | 6 | 0 | identical (qubit 200 not in the record, listed by both) |
| ibm_kingston | 2026-10-30 14:00 to 14:30 | 0,1,2,3,100 | 2026-10-30 13:56:41 | 0 | 0 | 0 | identical |
| ibm_boston | 2026-10-31 06:00 to 18:00 | every qubit | 2026-10-31 03:48:35 | 10 | 325 | 927 | identical |
| ibm_phoenix | 2026-10-30 08:00 to 20:00 | 0-9,119,120 | 2026-10-30 02:45:59 | 8 | 1 | 32 | identical (qubit 120 not in the record) |
| ibm_pittsburgh | 2026-10-30 22:00 to 2026-10-31 03:00 | every qubit | 2026-10-30 21:17:06 | 6 | 10 | 0 | identical (the run crosses midnight UTC, so two day files are read) |
| ibm_aachen | 2026-10-20 08:00 to 09:00 | 0,1 | none | 0 | 0 | 0 | identical (both report that no record is stamped at or before the start) |

Five of the seven windows have records stamped during the run, including the one that crosses midnight UTC. Boston and phoenix also have changes in the figures on the chosen qubits during the run.

## Whole history of every processor

For each of the seven processors the test also compared every saved record on every qubit, and the whole history as one run window.

| Processor | Records read | Flag rows over all records | Records after the first | Change rows | Result |
|---|---|---|---|---|---|
| ibm_aachen | 98 | 4445 | 97 | 7682 | identical |
| ibm_boston | 34 | 7030 | 33 | 1232 | identical |
| ibm_fez | 175 | 5603 | 174 | 3813 | identical |
| ibm_kingston | 137 | 3771 | 136 | 9514 | identical |
| ibm_marrakesh | 161 | 10752 | 160 | 2522 | identical |
| ibm_phoenix | 50 | 825 | 49 | 4153 | identical |
| ibm_pittsburgh | 76 | 3592 | 75 | 5996 | identical |

The flag rows were compared against `check_record` of `qia_check.py` called directly on each record. The change rows were compared against the package's `after` report.

## What makes the numbers agree

The index stores IBM's figures as published, with IBM's own date strings, and computes nothing. The page code follows `check_record` and the `after` loop of `qia_check.py` line by line. Numbers are written the way Python writes them, including `.4g`, `.3f` and `.1f` with ties rounded to even (a ratio of 2.0625 reads 2.062 in both). Files that carry the same stamp as an earlier file are dropped by the same rule the package uses, the first in file-name order. The build lists them in each manifest under `not_read_same_stamp`.

## Page behavior checked in a browser

The form was filled and sent in a browser for ibm_phoenix with the window above. The page showed the record in force, the flag on qubit 3, the eight records stamped during the run, the changes with both measurement dates in UTC, and the note for qubit 120.

## Limits

The index keeps the last 30 days of each processor. A run that began before the first record we hold gets the answer that the record in force is not in our mirror. The mirror begins on 28 October 2026. Times with fractions of a second are read to the millisecond. No such time appears in the records now. IBM publishes no fit width with T1 and T2, and the T2 band edge of 2.5 is the package's.

## Sizes

All seven processors together: about 10.3 MB as written, about 0.5 MB gzipped as one archive. One day file for one processor is at most 0.67 MB as written. The page reads the processor list and one manifest first, then one day file for each UTC day the run touches, plus the day of the record in force if that is earlier.
