# Data for Chu et al. (arXiv 2606.00433, PRL 137, 180601)

## The question in your paper

The learned instrument model treats other degrees of freedom, spectator qubits among them, as "assumed to be either negligible or effectively absorbed" into a stationary single-qubit description. A single-qubit instrument description has no term for a coherent phase on the neighbours. The question here is what the neighbours do while the targets are read.

## What was run

On 24 October 2026 on ibm_kingston, your three-repeated-readout protocol was implemented from the text on 20 nonadjacent targets (arm A), on the targets plus all their neighbours (arm Bhi), and on four targets alone (arm Blo). In arm C the 37 neighbours sat in |+> and were read in X and Y while the targets ran the protocol or idled. Jobs dbe9uhnpc3tc739lb2n0 and dbea3bvsstms73fbn80g, 50 s each. On 31 October 2026 a 39-qubit pack was read out 8 times beside 117 untouched qubits on kingston and marrakesh, jobs dbj3p3onceqs73aj79k0, dbj3prt6p51s73ck1v30, dbj3p4hffo6c73b8sc5g, dbj3pthkdqps738vqbqg.

## What it shows

From RESULT_BALL.md.text. Known-good check of your printed reading, a12 = Pr(10) - Pr(01), median +0.00882 [+0.00826, +0.00939] ABOVE, positive on 20 of 20 targets. Reading more qubits at once, Bhi minus A, is CONSISTENT on all seven instrument quantities, for example da12 within [-0.00058, +0.00048]. Blo minus A is CONSISTENT on all seven, da12 within [-0.00414, +0.00061]. Neighbour phase during the arm A readouts, readout minus idle: -0.561 [-0.914, -0.498] degrees per readout BELOW, 36 of 37 neighbours kept. Target qubit 0 gives p0 = 0.218 [0.214, 0.222] where the other 19 give 0.499 to 0.563, an observation made after the data.
From the 31 October results files, 117 untouched qubits, readout minus equal idle: kingston -2.4240 [-3.9835, -1.9317] BELOW, marrakesh -1.6830 [-2.3377, -1.0173] BELOW. Share given back by a per-qubit virtual-Z from a table measured minutes earlier, against 0.5: kingston +0.9281 [+0.8738, +0.9538] ABOVE, marrakesh +0.7952 [+0.6656, +0.8764] ABOVE.

## What it does not show

Whether single targets move with the number of readouts is CANNOT_TELL from this run. The neighbour phase is one chip on one day and says nothing about why it appears.

## Files

- Run of your protocol: [result](../earlier_runs/2026-10-24-uchicago-instrument/RESULT_BALL.md.text), [full output](../earlier_runs/2026-10-24-uchicago-instrument/RESULTS_BALL_raw.text), [raw_ball_J1.npz](../earlier_runs/2026-10-24-uchicago-instrument/raw_ball_J1.npz), [raw_ball_J2.npz](../earlier_runs/2026-10-24-uchicago-instrument/raw_ball_J2.npz), [circuits_ball.qpy](../earlier_runs/2026-10-24-uchicago-instrument/circuits_ball.qpy), [job_ball.json](../earlier_runs/2026-10-24-uchicago-instrument/job_ball.json)
- 31 October: [kingston](../run/results/results_keystone_ibm_kingston.text) and [marrakesh](../run/results/results_keystone_ibm_marrakesh.text) results, raw arrays in [run/data](../run/data/)
- Loading: the earlier .npz arrays are boolean with shots by bits, keys m1_i to m3_i and fin_i, column k is bit k, meta[i] in job_ball.json gives arm, input and instance. The run/data .npz arrays are IBM BitArray bytes, bit k at byte nby-1-k//8, position k%8. Circuits load with qiskit.qpy.

Heuremen LLC
