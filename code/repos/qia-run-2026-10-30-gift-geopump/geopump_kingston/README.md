# Your heat pump on ibm_kingston: what an ancilla readout costs

For Liliana Arrachea, Gerónimo Caselli, Luis Manuel and Pablo Cornaglia, from Heuremen LLC. A free calibration of arXiv 2610.09062v2, "Geometric heat pumping on a quantum processor".

## The line it answers

Your Supplemental Material: "Adding noise sources cumulatively shows that readout assignment and reset errors alone produce changes below 0.01 T." Your noise model treats each ancilla measurement as its waiting time (relaxation and dephasing) plus an assignment error.

## What we ran

On ibm_kingston on 24 October 2026: your qubits (47, 48, 46), your transpiler settings, delta_B = 0.45, at tau = 20 and tau = 60. Two jobs, the second in reverse order. IBM's calibration record was saved before each job.

- A: your circuits exactly.
- Ap: the incoming ancilla bit drawn at random and prepared as a basis state, then measured, then the collision, then the outgoing measurement.
- Bp: the same as Ap, with the incoming measurement replaced by a delay of its scheduled length (2.18 us on kingston). Ap and Bp share the same random bits, sit next to each other in the job, and their schedules match step for step.

Measuring a basis state ideally changes nothing, so Ap minus Bp is what the incoming readouts (192 per cycle) cost beyond the time they occupy. Heat comes from your estimator, in our own code. Before reading anything of ours, your released raw bits went through that code and gave your published pumped heats for all 12 jobs (to within 4e-11) and your Table 1 even parts (6 of 6).

## What we found

Ap minus Bp, heat per cycle in units of T, 99% bootstrap intervals:

| | tau = 60 | tau = 20 |
|---|---|---|
| Even part, total | +3.60 [+3.27, +3.94] | +2.92 [+2.58, +3.24], the two jobs disagree on the size |
| Even part, left bath | +0.57 [+0.34, +0.80] | +0.48 [+0.30, +0.66] |
| Even part, right bath | +3.03 [+2.78, +3.28] | +2.44 [+2.18, +2.70], the two jobs disagree on the size |
| Odd (pumped) part, both baths | within 0.30 of zero | within 0.30 of zero |

On this day the incoming readouts cost the pump about 3.6 T per cycle beyond their waiting time at tau = 60, against a measured even part of about 14.7 T. Your pumped heat is untouched: the cost is the same in both directions and cancels in your odd-part estimator, as your Supplemental Material says of the noise background.

Where it sits, looked at after the data: almost all of it is on one ancilla. The outgoing bit of the ancilla on qubit 46 changes by +0.03 to +0.04 when its incoming state was measured rather than waited on, for both prepared states. On qubit 48 the change is at most 0.005. A cost on the working qubit would show on both ancillas.

## What this adds to your paper

Assignment error is small, as your model says, but on this device a readout also changes the ancilla's state by a few percent beyond its waiting time. That term (a readout that disturbs the ancilla, about 3 to 4 percent per readout on qubit 46 here) is missing from the noise model and is the next thing to test. On this day the readout cost alone is as large as, or larger than, the part of the even heat your September simulation leaves unexplained. The two numbers come from different dates, so read that as a size, not as a measurement of your run.

## What we cannot say

- Whether the full 3.6 T applies to your exact protocol. Our prepared-bit version runs about 1 T hotter than your circuits in the even part at tau = 60 (A minus Ap scored your way: -0.95 [-1.54, -0.44]). The odd parts agree.
- Which physical process makes the readout disturb the ancilla. Readout-induced transitions, leakage and measurement-pulse heating all fit.
- How large it was on your dates. These three qubits have moved since 22 September: our even part at tau = 60 is 6.35 T above your September job at the same point.

## Files

- results_geopump.text: every reading at both tau, with the job-to-job gap and a legend
- known_good.text: your published numbers recovered from your released bits

The raw bits of both jobs, IBM's records and our code are yours on request.

Heuremen LLC
"We found it."
