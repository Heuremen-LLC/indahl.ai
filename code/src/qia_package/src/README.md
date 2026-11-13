# QIA Research Package

Heuremen LLC · https://indahl.ai/qia

Tools to check IBM Quantum calibration figures before a run and after it. Your files are opened read-only and never changed. Reports go
to a separate folder. Run on saved files, the checker sends nothing anywhere. Three parts do go online, each only when you run it: the
`--pull` option and step 1 below contact IBM with your own saved account, the YO reader downloads the model from Hugging Face, and
`t1t2-check` submits a job on your IBM account. Python 3.9 or later.

## Install the checker on its own

`pip install qia-check` gives the `qia-check` command (Python 3.9 or later): https://pypi.org/project/qia-check/

Add `[ibm]` to pull records with your own IBM account: `pip install "qia-check[ibm]"`

## Before a run

1. Save the record you are about to run under. This needs `pip install qiskit-ibm-runtime` and a saved IBM Quantum account:
   `python -c "import json; from qiskit_ibm_runtime import QiskitRuntimeService as S; json.dump(S().backend('ibm_kingston').properties().to_dict(), open('record.json','w'), default=str)"`
   or let the checker do it: `python qia_check.py before --pull ibm_kingston`
2. Check it: `python qia_check.py before record.json --qubits 0,1,5`
   Flags: T1 or T2 measured more than 24 hours before the record's stamp, error values of exactly 0, T2 above 2 x T1, and T1 and T2 measured more
   than 24 hours apart.
3. Read the Guards before the work: `pip install faultsguards` (or the wheel in `faultsguards/`), then `python -m faultsguards guards`
4. Check the T1 and T2 pair yourself: `t1t2-check/` measures T1 and a Hahn echo T2 on the same qubit in one job, and `--estimate` prints the QPU seconds first.

## After a run

1. Save the record again after the run, into the same folder as the first. Keep reports in a different folder.
2. `python qia_check.py after records/ --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1,5`
   Times are UTC, written with Z or an offset. The report names the latest record in the folder stamped at or before the start, lists every newer
   record stamped up to the end, and shows each change in the T1, T2 and readout-error figures on your qubits from one record to the next. If IBM
   recalibrated between your last saved record and the run, the record in force is not in the folder, so save one right before you submit.
3. Read your write-up against the Faults: `python -m faultsguards faults`
4. Give each reading a check block before it goes in a paper: `check-block/`

## YO

YO is our small model trained on IBM calibration records. It reads a record and flags stale and zero entries. On each run, the exact answer
computed by code is printed beside YO's, so any disagreement shows. Use the code answer as the record of truth. YO reads eight qubits at a
time and needs at least eight qubits with a T1, a T2 and their dates. Model: https://huggingface.co/indahl/YO

`python yo/yo_audit.py record.json --model indahl/YO` on Apple silicon (mlx-lm), or `--fused indahl/YO` elsewhere (transformers).

## What is here

- `qia_check.py`: before and after checks, standard library only
- `TESTED.md`: how this package was tested, with results
- `START_HERE.html`: this guide as a page
- `yo/`: YO's record reader
- `faultsguards/`: the Standards as a Python package, with the PDFs
- `t1t2-check/`: same-job T1 and T2 measurement on your account
- `check-block/`: the check block and its commit gate
- `papers/`: A Readout Is Not an Idle (the QIA paper)
- `LICENSE.txt`, `CITATION.cff`

## Links

- QIA: https://indahl.ai/qia
- List of studies: https://indahl.ai/qia/list
- Key: https://indahl.ai/qia/key
- Code: https://github.com/Heuremen-LLC/indahl.ai
- Standards on PyPI: https://pypi.org/project/faultsguards/
- YO: https://huggingface.co/indahl/YO

## Terms

Heuremen LLC permits anyone to run, copy and change the code in this package, for any purpose, with attribution to Heuremen LLC and https://indahl.ai/qia

Your results remain yours. The text, papers and data follow LICENSE.txt, and their use to train, fine-tune or build AI models is not permitted. The Standards package keeps its own terms.
