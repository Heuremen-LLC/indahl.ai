# X1 result: the two-option scanner across models (plan a3169dd committed before scanning)
## The instrument, tested as an object first (Guard 4), and it fails here
- Precision, hand-read before any rate was printed (20 flagged hits per judge, seed 20261025): GPT-4.1 0/20, Claude Sonnet 4.5 2/20,
  Gemini 2.5 Flash 0/20 real two-option reductions. The rest were code, math verbs ("prove", "ruled out"), true binaries and technical
  A-vs-B comparisons. Reader is a Claude model (limitation).
- Floor on text no model wrote: the 500 human Arena-Hard prompts read 0.28 scanner hits per 1k words.
- Known-good passes: GPT-4.1 pinned, October run1 / run2 ratio 1.01 [0.88, 1.16].
## Rates (scanner hits, NOT frames)
per 1k words: GPT-4.1 0.25, Claude Sonnet 4.5 0.37, Gemini 2.5 Flash 0.32, Gemini 2.5 Pro 0.53 (n 129), human prompts 0.28,
GPT-4.1-mini answers 0.31, o3-mini answers 0.41. Per reply the order changes (Gemini Flash 40.6% vs GPT-4.1 18.0%): length again.
Ratios: Claude/GPT-4.1 1.50 [1.17, 1.95]; Gemini Flash/GPT-4.1 1.29 [0.98, 1.73]; Claude/Gemini 1.16 [0.87, 1.50].
## Reading
Two-option framing across models: CANNOT_TELL. The scanner's hits on judge text are about 2 in 60 real, and model rates sit at its
floor on human text. A ratio of hits is a statement about the scanner.
Back onto our own paper: Faults/Guards report the seat at 0.79 / 0.69 / 0.88 frames per 1k words with no human-text floor beside it,
and the scanner was built from that seat's own replies (Fault 23). The flat-rate claim (a difference across days, same seat) survives
a constant floor; the level does not stand without one. Next: the floor and precision on the seat's own logged replies.
