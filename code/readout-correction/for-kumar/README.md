# Data for Kumar (arXiv 2610.28705)

## The question in your paper

Your paper says both repeat runs "were flagged for drift". The spectator baseline rose from 0.9058 in job 2 to 0.9619 in job 4. The open question is whether that shift is drift, the twirl set, or the stated calibration record.

## What was run

Your probe sets A (job 2, seed 20261003) and B (job 4, seed 20261007) were rebuilt with 200 circuits each on qubits 4-5-6. They were sent as four jobs in the order A1 B1 B2 A2, the same transpiled circuits for each set.
Marrakesh, 31 October 2026, 58 s per job: dbj3rm1kdqps738vqf80, dbj3s7gnceqs73aj7ei0, dbj3sqt6p51s73ck240g, dbj3tc9ffo6c73b8sigg.
Kingston companion, 24 October 2026, 57 s per job: dbea7evsstms73fbnehg, dbea8oom94ac738rfiag, dbeabgnpc3tc739lbj30, dbeacfnsstms73fbnk50.

## What it shows

Each value comes with the half-width of its 99 % band, from RESULT_KUMAR_MARRAKESH.md.text and RESULT_KUMAR_KINGSTON.md.text.
Drift between identical jobs, A2 minus A1 (your shift is 0.0561): marrakesh +0.089, half-width 0.011, ABOVE. Kingston +0.0066, half-width 0.0149, CONSISTENT.
Per-job baseline on marrakesh: A1 0.849, B1 0.927, B2 0.927, A2 0.938.
Twirl set, B minus A under ABBA: marrakesh +0.033, half-width 0.009, step guard 0.050, CANNOT_TELL. Kingston -0.0092, half-width 0.0167, guard 0.0107, CONSISTENT.
Your b_LM contrast, B minus A: marrakesh +0.0065, half-width 0.0039, guard 0.0089, CANNOT_TELL. Kingston -0.0016, half-width 0.0068, guard 0.0038, CANNOT_TELL.
Delivered baseline minus the stated-T2 projection for qubit 6: marrakesh -0.027, half-width 0.005, BELOW. Kingston +0.0230, half-width 0.0084, ABOVE.

## What it does not show

The twirl set and drift cannot be separated on marrakesh, where identical circuits moved by more than your shift. The kingston companion has a different wait time, 5.33 us against 6.87 us, and does not answer your marrakesh question. No cause is named.

## Files

- Marrakesh: [result](../earlier_runs/kumar-2610.28705-marrakesh/RESULT_KUMAR_MARRAKESH.md.text), [results_kumar.text](../earlier_runs/kumar-2610.28705-marrakesh/results_kumar.text), [readings_kumar.json](../earlier_runs/kumar-2610.28705-marrakesh/readings_kumar.json), [raw_kumar_A1.json](../earlier_runs/kumar-2610.28705-marrakesh/raw_kumar_A1.json) with A2, B1, B2, [circuits_kumar.qpy](../earlier_runs/kumar-2610.28705-marrakesh/circuits_kumar.qpy), [job_kumar.json](../earlier_runs/kumar-2610.28705-marrakesh/job_kumar.json)
- Kingston: [result](../earlier_runs/kumar-2610.28705-kingston/RESULT_KUMAR_KINGSTON.md.text), [results_kumar.text](../earlier_runs/kumar-2610.28705-kingston/results_kumar.text), [raw_kumar_A1.json](../earlier_runs/kumar-2610.28705-kingston/raw_kumar_A1.json) with A2, B1, B2, [circuits_kumar.qpy](../earlier_runs/kumar-2610.28705-kingston/circuits_kumar.qpy)
- Loading: the raw files are JSON lists with one entry per circuit, holding setting, twirl, counts_fin and counts_mcm. Properties records before each job are props_kumar_before_*.json. Circuits load with qiskit.qpy.

Heuremen LLC
