# Recount plan: arXiv 2610.25964v2 (Jayakumar, Thilak; Sri Krishna College of Technology / Sri Eshwar College), committed before reading
Ack read: "This work received no external funding." Eligible free row.
Data: github.com/Kesav2k04/ugaa-research experiments/pope_{adversarial,popular,random}_2tok_vs_8tok.json (per-question label, both readouts, top token id).
## A. Recount (our code on their per-item records)
- F1 / precision / recall / yes-rate under each readout per split: abstract 0.8221 / 0.8498 / 0.8713 (8-token); Table 2 adversarial
  2-token recall 0.9587, precision 0.6307, yes-rate 0.760, F1_2 0.7608; shift 6.13 points.
- "neither ID 3582 nor 1217 generated once in 9,000"; "zero Yes -> no transitions among 3,893 ' Yes' emissions";
  adversarial T 1,174, G 1,318, rho 660/1,318, phi 264/326; popular T 1,191, G 1,388, 567/1,388, 250/309.
- Outcome per number: CLEAN / ABOVE / BELOW / CANNOT_TELL.
## B. Pricing (zero model calls)
B1 WIDTH ON THE SHIFT. Paired bootstrap over questions (20,000, seed 20261025), each split: F1_8 - F1_2 with 95% interval.
   Known-good: a readout against itself gives shift 0 with zero width.
B2 THE SHIFT AGAINST THE GAINS THEY SURVEY. Their claim "exceeds the adversarial gain reported by five of the six papers":
   count, from their Table 3, the adversarial gains that fall below the LOWER bound of B1's interval (strictly), and those inside it.
