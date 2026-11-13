# Recount result: arXiv 2610.25964v2 (POPE token-set readout). Plan 05d69da committed before reading.
## A. CLEAN
- 8-token F1 0.8221 / 0.8498 / 0.8713 (adversarial / popular / random); adversarial 2-token F1 0.7608, precision 0.6307,
  recall 0.9587, yes-rate 0.760; shift 6.13 points. T 1,174, G 1,318, rho 660/1,318, phi 264/326; popular T 1,191, G 1,388,
  567/1,388, 250/309. Top-token ids across 9,000 questions: only 1939 and 3869; 3582 and 1217 never appear. 3,893 ' Yes'
  emissions, 0 read as no by the 2-token rule. All rebuild to the printed digit.
## B. Priced
B1 width on the shift (paired bootstrap over questions, 20,000): adversarial 6.13 [4.43, 7.83]; popular 5.37 [3.70, 7.03];
   random 3.15 [1.50, 4.80]. All ABOVE zero. Known-good: readout against itself, shift 0 on every draw.
B2 "exceeds the adversarial gain reported by five of the six papers": as a point, 5 of 6 holds. Against the interval,
   4 of 6 gains sit below 4.43 (+0.70, +0.80, +0.96, +1.60), +5.76 sits inside [4.43, 7.83] (CANNOT_TELL), +10.81 above.
   So the resolved count is four of six, with one undecided.
