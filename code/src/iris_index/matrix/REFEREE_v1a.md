# Referee on Matrix v1, first four models (Sonnet, read-only, raw replies), 25 Oct. Arithmetic reproduced; verdicts acted on.
1 M1 rule undefined in the plan: gemma sets no_persona=true and still fills labels (137/300); mistral sets no_persona=false and leaves
  fields null (188/300). Rule now stated (flag only, after the referee); a cell whose scorer rule differs by > 0.10 is CANNOT_TELL
  (mistral 0.552 flag vs 0.181 scorer; llama3.1 0.397 vs 0.284). Phi4 and qwen3 schema-consistent: HOLD.
2 M3 at 2 options = letter fallback, inseparable from order sensitivity; flips land on the preferred letter (gemma 27/29 A, mistral 39/43 B,
  phi4 13/15 B). Renamed; v2 separates. ToMi flips more than BigToM (0.20/0.30/0.11 vs 0.09/0.15/0.04).
3 Exact repeats identical by construction: a determinism check, not a noise floor; ABOVE = non-zero.
4 qwen3 M1 HOLDS (300/300 well-formed). Its MCQ failure is template-A specific (template B: 186/200 parsed, 77% accurate).
5 M6b partly our v1 prompt (N not stated; numbered story lines inside items); v2 prompt states N. Reported as prompt-and-model.
6 Carrier cells resolved: 6 at four models (not 9/12); expected false calls 0.3. M1 has no floor. Mixed ToMi/BigToM pooling noted.
