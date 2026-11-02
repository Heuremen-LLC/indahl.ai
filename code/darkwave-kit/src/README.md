# Darkwave Correction Kit

Heuremen LLC · https://indahl.ai/darkwave

A mid-circuit readout can turn the phase of the untouched qubits next to it. This kit measures that turn on your own IBM Quantum account,
one value per untouched qubit in degrees per readout, and adds the matching virtual-Z correction to your own circuits. The method is the
one in our study "A Readout's Kick Is a Turn" (data and code: https://doi.org/10.5281/zenodo.23843468). The kit names no mechanism for the turn.

## Install

`pip install -r requirements.txt` (qiskit, qiskit-ibm-runtime, numpy, and qiskit-aer for the self-test). Python 3.10 or later.
Save your IBM Quantum account once with `QiskitRuntimeService.save_account(...)` as IBM describes. The kit reads that saved account and
never stores your key.

## 1. Self-test, no account needed

`python darkwave_kit.py selftest`

On the simulator it plants a known turn on five qubits, from 0 to 62 degrees per readout, measures it, applies the correction and measures
again. It passes when every planted value comes back within 1 degree and every corrected value sits within 1 degree of zero. It tests the
analysis, the bit order of the simulator's counts and the placement of the correction. It does not test hardware noise, real readout timing
or your IBM account.

## Tested on IBM hardware

We tested the kit on ibm_kingston on 2 November 2026 under plans committed and public before each job. The study's 39-qubit readout pack and its
117 untouched qubits were used, with the study's own calibration code running in the same job as the reference.

- Version 1.0 read the same turn as the study's code (kit minus study +0.025 [-0.063, +0.143] degrees per readout) but its correction gave back
  only 0.264 [0.248, 0.285] of the turn, and it failed the test. Its apply step merged readouts separated by barriers into one group, so a
  circuit with four readouts got one correction instead of four.
- Version 1.1, this one, read the same turn as the study's code (kit minus study -0.041 [-0.231, +0.101] degrees per readout) and its correction
  gave back 1.012 [0.993, 1.027] of the turn over 113 targets. The turn left after the correction was +0.086 [-0.007, +0.180] degrees per readout,
  against -3.223 uncorrected. It passed the test, on one chip and one calibration snapshot, on the second attempt after the fix.
- The share given back is a median over the targets. A tail keeps part of the turn: 12 % of targets kept more than 1 degree per readout,
  mostly targets with low idle coherence, and one high-coherence target kept +9.47 of a -22.1 degree turn. Check the coherence the table
  prints before you trust a target's value.

Brackets are 95 % bootstrap bands over the target qubits. Every number was recomputed from the raw arrays with separate code. Both runs, with their plans, raw data and code, are in `hardware-check/` and at
https://github.com/Heuremen-LLC/heuremen.org/tree/main/experiments

## 2. Measure your table

`python darkwave_kit.py measure --backend ibm_kingston --readout 5,6,7 --targets 4,8,9 --check`

`--readout` is the set of qubits your circuits measure mid-circuit. `--targets` is the untouched qubits you want corrected. `--check`
builds the circuits, checks that the layout is unmoved and that the idle and readout arms take the same time on every target, and submits
nothing. Run it again with `--yes` to submit one job of 8 circuits (4,000 shots each by default). IBM bills the job by its quantum seconds,
which your plan shows after the job. The table is written to `kicks/` as JSON with, for each target, the turn per readout with a 95 % band, one of four outcomes
against zero (ABOVE, BELOW, CONSISTENT within plus or minus 0.5 degrees, or CANNOT_TELL) and the coherence kept beside the idle comparison.

How it is measured: the targets go on the equator, then a block of N steps (N = 1 and N = 4) either reads out the readout qubits or
leaves them idle for exactly the readout duration. The targets are then read in the X and Y bases. The phase difference, read out minus
idle, divided by N, is the turn per readout. The kit reads turns up to 180 degrees per readout. A target whose idle coherence is close to zero
gives no usable turn, and its band shows it.

## 3. Apply it

`python darkwave_kit.py apply --table kicks/kick_table_ibm_kingston_....json my_circuits.qpy corrected.qpy`

After each group of mid-circuit readouts on the table's readout qubits, the kit adds rz(-turn) to each target qubit. rz is virtual on IBM
hardware and adds no time. Measurements at the very end of a circuit get no correction.

- Your circuits must be on physical qubit numbers, transpiled with the layout the table was measured on.
- The table assumes the whole readout set is read together in each group, as when it was measured. The kit warns when a group reads only part of it.
- Readouts inside if/else or loop blocks are not corrected. The kit counts them in a warning.
- Every target in the table is corrected with its measured value, including targets whose turn read CANNOT_TELL, and the kit names them. Add `--only-resolved` to correct only targets that read ABOVE or BELOW.
- Your input file is opened read-only and its full sha256 is printed before and after. The output must be a new file. Add `--force` to replace an existing one.

## What a table holds for

A table holds for the readout set, the backend and the calibration it was measured with. In our study a table measured minutes before the
run gave most of the turn back on both chips. A table ten days old did so on ibm_kingston. On ibm_marrakesh it over-corrected: its values
were larger than the turn measured that day (median 1.5 times, our computation from the two public tables, defined after the data), it gave back less than half of
the spectators' turn, and the clock came out worse than with no correction. Measure close to your run and keep the
table with your data. A phase correction cannot give back coherence that was lost. The table prints the coherence kept so you can see it.

## Examples

`hardware-check/kick_table_ibm_kingston_2nov2026.json` is a table this kit measured on ibm_kingston on 2 November 2026, in the kit's own format.
`examples/` holds the tables from our own 31 October 2026 run on ibm_kingston and ibm_marrakesh, measured minutes before that run. They
are in the study's own format, show the size of the turn we saw, and cannot be used with `apply`. They are not a table for your run.

## Links

- Darkwave: https://indahl.ai/darkwave
- Data and code of the study: https://doi.org/10.5281/zenodo.23843468
- Code: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/readout-correction
- QIA Research Package, checks on the calibration record before and after a run: https://indahl.ai/qia/package

## Terms

Heuremen LLC permits anyone to run, copy and change the code in this kit, for any purpose, with attribution to Heuremen LLC and https://indahl.ai/darkwave

Your results remain yours. The text and the example data follow LICENSE.txt, and their use to train, fine-tune or build AI models is not permitted.
