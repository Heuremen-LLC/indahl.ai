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
2. Check it: `qia-check before record.json --qubits 0,1,5`
   Flags: T1 or T2 measured more than 24 hours before the record's stamp, error values of exactly 0, T2 above 2 x T1, and T1 and T2 measured more than 24 hours apart.
3. Read the Guards before the work: `pip install faultsguards`, then `python -m faultsguards guards`

## After a run

1. Save the record again after the run, into the same folder as the first. Keep reports in a different folder.
2. `qia-check after records/ --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1,5`
   Times are UTC, written with Z or an offset. The report names the latest record in the folder stamped at or before the start, lists every newer record stamped up to the end, and shows each change in the T1, T2 and readout-error figures on your qubits from one record to the next. If IBM recalibrated between your last saved record and the run, the record in force is not in the folder, so save one right before you submit.
3. Read your write-up against the Faults: `python -m faultsguards faults`

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
