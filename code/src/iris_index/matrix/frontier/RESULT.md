# Frontier columns from released data (plan b88b6b3 committed before computing). Not comparable to the seat's MCQ numbers; compare within a row.
F-M1 NepPlural abstain arm (116 gold No-Persona, 184 persona):
  over-attribution: GPT 0.112 [0.060, 0.172], Gemini 0.164 [0.103, 0.233], Claude 0.267 [0.190, 0.345]
  false abstention: GPT 0.158 [0.109, 0.212], Gemini 0.049 [0.022, 0.082], Claude 0.082 [0.043, 0.125]
  (Each vendor trades the two failures differently; no single "best" without saying which failure costs more.)
F-M2 copy floor, GPT-4.1 pinned, October run1 vs run2: outcome sign 0.211 [0.175, 0.247]; single round-1 verdict 0.155 [0.123, 0.187].
F-M3 option order (answers swapped between round 1 and round 2), share of prompts whose candidate-relative verdict sign flips:
  GPT-4.1 May 0.310 [0.270, 0.351]; GPT-4.1 Oct 0.281 [0.243, 0.321]; Claude Sonnet 4.5 0.313 [0.275, 0.355];
  Gemini 2.5 Flash 0.309 [0.268, 0.351]; Gemini 2.5 Pro 0.217 [0.147, 0.287] (n 129).
  GPT-4.1 order flip minus its own copy floor: +0.125 [+0.080, +0.167] ABOVE (the only judge with a floor).
  Paired between judges: Claude - GPT +0.006 [-0.047, +0.059], Gemini Flash - GPT -0.004 [-0.062, +0.052], Claude - Gemini Flash
  +0.004 [-0.050, +0.058]: all CONSISTENT. About three in ten verdicts flip on position for all three vendors alike.
F-M5 format: UCL Table 1 (recounted CLEAN, booked) is the GPT-4.1 format carrier; not recomputed here.
Seat comparison (same row, different task): gemma3:4b M3 order flip 0.145 above its floor on 2-option MCQ.
