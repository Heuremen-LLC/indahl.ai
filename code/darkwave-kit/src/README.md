# Darkwave Correction Kit

Heuremen LLC · https://indahl.ai/darkwave

A mid-circuit readout can turn the phase of the untouched qubits next to it. This kit measures that turn on your own IBM Quantum account,
one value per untouched qubit in degrees per readout, and adds the matching virtual-Z correction to your own circuits. The method is the
one in our study "A Readout's Kick Is a Turn" (data and code: https://doi.org/10.5281/zenodo.23843468). The kit names no mechanism for the turn.

## Install

`pip install -r requirements.txt` (qiskit, qiskit-ibm-runtime, numpy, and qiskit-aer for the self-test). Python 3.9 or later.
Save your IBM Quantum account once with `QiskitRuntimeService.save_account(...)` as IBM describes. The kit reads that saved account and
never stores your key.

## 1. Self-test, no account needed

`python darkwave_kit.py selftest`

On the simulator it plants a known turn on five qubits, from 0 to 62 degrees per readout, measures it, applies the correction and measures
again. It passes when every planted value comes back within 1 degree and every corrected value sits within 1 degree of zero.

## 2. Measure your table

`python darkwave_kit.py measure --backend ibm_kingston --readout 5,6,7 --targets 4,8,9 --estimate`

`--readout` is the set of qubits your circuits measure mid-circuit. `--targets` is the untouched qubits you want corrected. `--estimate`
builds and checks the circuits and submits nothing. Run it again with `--yes` to submit one job of 8 circuits (4,000 shots each by
default). The table is written to `kicks/` as JSON with, for each target, the turn per readout with a 95 % band, one of four outcomes
against zero (ABOVE, BELOW, CONSISTENT within plus or minus 0.5 degrees, or CANNOT_TELL) and the coherence kept beside the idle comparison.

How it is measured: the targets go on the equator, then a block of N steps (N = 1 and N = 4) either reads out the readout qubits or
leaves them idle for exactly the readout duration. The targets are then read in the X and Y bases. The phase difference, read out minus
idle, divided by N, is the turn per readout. Both arms take the same time on every target qubit.

## 3. Apply it

`python darkwave_kit.py apply --table kicks/kick_table_ibm_kingston_....json my_circuits.qpy corrected.qpy`

After each group of mid-circuit readouts on the table's readout qubits, the kit adds rz(-turn) to each target qubit. rz is virtual on IBM
hardware and adds no time. Measurements at the very end of a circuit get no correction. Your input file is opened read-only and its
sha256 is printed before and after.

## What a table holds for

A table holds for the readout set, the backend and the calibration it was measured with. In our study a table measured minutes before the
run gave most of the turn back on both chips, and a table ten days old over-corrected on one of them. Measure close to your run and keep the
table with your data. A phase correction cannot give back coherence that was lost. The table prints the coherence kept so you can see it.

## Examples

`examples/` holds the tables from our own 31 October 2026 run on ibm_kingston and ibm_marrakesh, measured minutes before that run. They
show the format and the size of the turn we saw. They are not a table for your run.

## Links

- Darkwave: https://indahl.ai/darkwave
- Data and code of the study: https://doi.org/10.5281/zenodo.23843468
- Code: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/readout-correction
- QIA Research Package, checks on the calibration record before and after a run: https://indahl.ai/qia/package

## Terms

Free to download, run and cite with attribution to Heuremen LLC and https://indahl.ai/darkwave

Your results remain yours. Use of this kit's text or data to train, fine-tune or build AI models is not permitted. See LICENSE.txt.
