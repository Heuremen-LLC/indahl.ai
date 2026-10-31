# X1 plan: the two-option frame across models on one shared task (zero model calls). Committed before any scan.
Source: UCL release (2610.30512), Arena-Hard v2.0 hard split, default judge instructions (C1F1D1), raw judge text, both answer orders.
Scanner: triangle.py (internal, not released) exor_scan, sha256 34e57ef53dd4d795..., a frame = a hit whose x[3] is true
(the same rule audit_guard.py uses). Words = whitespace tokens of the judge text.
## Arms
JUDGES, same task: GPT-4.1 (full_factorial May, 500), Claude Sonnet 4.5 (L1_swap, 498), Gemini 2.5 Flash (L1_swap_v2_flash_16k, 500).
  Gemini 2.5 Pro (129 prompts) reported but CANNOT_TELL for comparisons if n < 200.
ANSWERERS, a different task, compared only with each other: GPT-4.1-mini (candidate_response) vs o3-mini (baseline_response), same prompts.
HUMAN FLOOR: the 500 human-written Arena-Hard prompts (the scanner's rate on text no model wrote).
## Rulers (both, Fault 24): share of judge calls with >= 1 frame; frames per 1k words. Unit = prompt (both rounds pooled per prompt).
## Known-good: GPT-4.1 pinned, October run1 vs run2, same setup: ratio of frames/1k must be CONSISTENT with 1; its interval is the floor.
## Comparisons: paired bootstrap over shared prompts (20,000, seed 20261025) of the per-1k-words ratio for each judge pair and the
   answerer pair; ABOVE / BELOW / CONSISTENT; CANNOT_TELL if n < 200 or the known-good fails.
## Precision check (Fault 23, the scanner was written from Claude's own replies): Bones reads 20 flagged frames per judge model,
   drawn with seed 20261025, and marks each as a real two-option reduction or not, BEFORE seeing that model's rate in print.
   Any judge whose precision differs from another's by more than its own width makes that pair's comparison CANNOT_TELL.
   The reader is a Claude model: stated as a limitation, not removed.
