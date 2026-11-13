# qia-check

Heuremen LLC · https://indahl.ai/qia

Checks on IBM Quantum calibration figures before a run and after it. Your files are opened read-only and never changed. Reports go to a separate folder. Run on saved files, the checker sends nothing anywhere. Only the `--pull` option contacts IBM, with your own saved account, and only when you run it. Python 3.9 or later, standard library only.

## Install

```
pip install qia-check
```

For the `--pull` option, which saves the live record from IBM, add the optional IBM client:

```
pip install "qia-check[ibm]"
```

The tool is then the command `qia-check`. It is also importable as the module `qia_check`.

## Before a run

1. Save the record you are about to run under. This needs the IBM client (`pip install "qia-check[ibm]"`) and a saved IBM Quantum account. Let the checker do it:
   `qia-check before --pull ibm_kingston`
   Or save it yourself with `QiskitRuntimeService().backend('ibm_kingston').properties().to_dict()` written out as JSON.
2. Check it: `qia-check before record.json --at 2026-11-01T12:00:00Z --qubits 0,1,5`
   `--at` is your run time. Without it, the time of the check is used. Every figure the checker reads is aged against both the record's stamp and the run time.
   Flags: STALE (T1, T2, readout_error, prob_meas0_prep1, prob_meas1_prep0 or init_error measured more than 24 hours before the stamp or the run), ZERO (an error value of 0), TINY (a nonzero error value below 1e-6), FUTURE (a figure dated after its record's stamp), T2>2T1, and PAIR (T1 and T2 measured more than 24 hours apart).
   UNKNOWN marks anything that cannot be read: an absent, null, NaN, zero or negative T1 or T2, a negative error value, an unknown unit, an unreadable date, a date with no zone, conflicting duplicate entries, or a qubit with no figures. UNKNOWN is never a pass.
   The page opens with the number of flag rows and UNKNOWN rows. A page where nothing was checked says so, and the command exits with code 2. A record stamp with no zone is refused.
   Gates and zz are not read.
3. Read the Guards before the work: `pip install faultsguards`, then `python -m faultsguards guards`

## After a run

1. Save the record again after the run, into the same folder as the first. Keep reports in a different folder.
2. `qia-check after records/ --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1,5`
   Times are UTC, written with Z or an offset. The report names the latest record in the folder stamped at or before the start, checks it and every record stamped during the run with the same checks as before mode, and lists each change in the figures from one record to the next.
   A folder that mixes backends is refused unless `--backend NAME` picks one. Two files with the same stamp whose figures differ (value, date or unit of a field the package reads) are both checked and their differences are listed as a conflict. Files that differ only in other content are read once. If no record precedes the start, the records stamped during the run are still checked and the page says the record in force is missing.
3. Read your write-up against the Faults: `python -m faultsguards faults`

## Two categories

Every flag and change carries a category: **T1 and T2** (STALE on T1 or T2, T2>2T1, PAIR, and T1/T2 changes) or **Error figures**
(ZERO, TINY, STALE on readout or initialisation errors, and their changes). The before page shows them as two tables.

## The rest of the QIA package

The full package adds the YO record reader, the same-job T1 and T2 measurement, the check block and the paper. It is at https://indahl.ai/qia/package

## How this was tested

See TESTED.md in the source distribution, installed under `share/doc/qia-check/`, and published at https://indahl.ai/qia/package

## Links

- QIA: https://indahl.ai/qia
- Package page: https://indahl.ai/qia/package
- List of studies: https://indahl.ai/qia/list
- Key: https://indahl.ai/qia/key
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Faults and Guards on PyPI: https://pypi.org/project/faultsguards/
- YO: https://huggingface.co/indahl/YO

## Terms

Heuremen LLC permits anyone to run, copy and change the code in this package, for any purpose, with attribution to Heuremen LLC and https://indahl.ai/qia

Your results remain yours. The text and data follow LICENSE, and their use to train, fine-tune or build AI models is not permitted.

## Exit codes and folders

The command exits with code 0 when it wrote a report that checked at least one qubit. It exits with code 2 when nothing was checked (no qubit
asked for is in the record, or no record of the backend covers the run). It exits with code 1 when it refuses: a record file that is missing or
cannot be read, a record stamp with no zone (before mode), a folder that mixes backends without `--backend`, a time it cannot read, or an `--out`
folder that is the record's own folder (before mode) or the records folder itself (after mode). A subfolder is allowed. In after mode, a file in
the folder that cannot be read as a record (including one whose stamp has no zone, an unopenable file or a bad .gz) is skipped and named on the
page, and the rest are read. A skipped file is not a pass, even when the page shows no flag and the exit code is 0. In before mode the same problems with the one record file are a refusal (exit 1).
`--pull` is ignored, with a note, when a record file is also given.

## What a clean page means

A clean page has 0 flag rows, 0 UNKNOWN rows and no skipped file. It means no flag fired in the fields the package reads: T1, T2, readout_error,
prob_meas0_prep1, prob_meas1_prep0 and init_error, per qubit, with their dates and units. A page with UNKNOWN rows is not clean and says so,
even when its exit code is 0. A clean page says nothing about gates, zz couplings, other fields, or your results. Notes on the page (records not used, a conflict) are
worth reading even when no flag fired. The "unit only, same value" label allows a relative difference up to 1e-9, so a value exactly at that
edge can fall either side of it.
