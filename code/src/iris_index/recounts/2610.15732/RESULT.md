# Recount result: arXiv 2610.15732v1 (NepPlural). Plan e4508b4 + addendum committed before reading.
## A. CLEAN: Table 4 Forced and Abstain rows rebuild against gold_final (300): forced GPT 0.49, Gemini 0.48, Claude 0.47, majority 0.50;
   abstain 0.70, 0.75, 0.67, 0.74; No-Persona F1 0.83 / 0.87 / 0.79; false abstention 15.8 / 4.9 / 8.2% of 184.
## B. Priced (comment bootstrap, 2,000 draws)
B1 widths: forced cells about +-0.03; abstain cells about +-0.04 (e.g. Gemini 0.75 [0.71, 0.78]).
B2 abstain minus forced, paired: GPT +0.21 [+0.17, +0.25], Gemini +0.27 [+0.24, +0.30], Claude +0.20 [+0.16, +0.24], majority +0.24
   [+0.21, +0.28]: ABOVE for every model. Giving the labeller a "none" outcome is worth a fifth of macro-F1 on every vendor tested.
B3 abstain ranking: Gemini - GPT +0.052 [+0.011, +0.096] ABOVE; Gemini - Claude +0.077 [+0.036, +0.119] ABOVE;
   GPT - Claude +0.025 [-0.027, +0.078] CONSISTENT. Table 4's order GPT > Claude is not resolved.
