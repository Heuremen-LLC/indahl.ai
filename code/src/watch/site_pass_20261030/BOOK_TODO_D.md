# Register field changes for lane D (IRIS), 30 Oct 2026. Bones applies by hand.

File: ~/bones-forge/iris_index/IRIS_BOOK_register.json. I did not edit it. After the edits, run `python3 ~/bones-forge/iris_index/matrix_page/iris_list.py` (it also copies list.json to the worker public folder) and ship.
iris_list.py already turns every "; " in `recount` and `priced` into a full stop on the List, so the new text below has no semicolons either way.

Constraints from the ledger: some pub2.* ledger rows grep fragments of this file. Do not touch the `referee` field of 2610.31135 (pub2.s08 greps "st copies identical 9,600/9,60"), and keep `priced` of 2610.25964 starting with `shift 6.13 [4.43, 7.83]` (pub2.s11, pub2.s12). The new texts below respect both.

## D-7 (wrong claim on the live List, do this first): row arXiv:2610.18610v1, field `priced`
The List currently says the "excluding controls reverses the lead" figure CANNOT_TELL. Our own referee rebuild withdrew that.
Support:
- recounts/2610.18610/RESULT.md, last paragraph: "Referee rebuild (25 Oct, our script reversal.py): controls from `category` ... = 920. Excluding controls Jev 69.08 vs GPT-3.5 70.87 (paper exact) ... Our earlier CANNOT_TELL is WITHDRAWN"
- recounts/2610.18610/reversal_out.text: "controls: 920", "excl. controls: jev 69.08 gpt35 70.87", "jev-gpt35 excl. controls -1.79 [-3.54, -0.19] (family_id)", "jev-gpt35 all +1.59 [+0.22, +2.94] (family_id)"
- The register's own `referee` field: "reversal CONFIRMED (69.08 vs 70.87 ...). Our CANNOT_TELL withdrawn."
- Paper text (arXiv 2610.18610v1, Results): "Removing native controls reverses Jev’s lead over GPT-3.5, leaving 69.1% against 70.9%." Table 2 caption: "Excluding controls, Jev scores 69.1% and GPT-3.5 70.9%."

old:
```
Jev lead +1.59 [+0.25, +2.89] over GPT-3.5 and +2.36 [+0.98, +3.75] over GPT-5.6-Luna, ABOVE; the "excluding controls reverses the lead" figure (69.1 vs 70.9) does not rebuild from the released control marks: CANNOT_TELL
```
new (quote is the paper's own sentence, apostrophe as printed):
```
Jev lead +1.59 [+0.25, +2.89] over GPT-3.5 and +2.36 [+0.98, +3.75] over GPT-5.6-Luna, ABOVE. The paper says "Removing native controls reverses Jev’s lead over GPT-3.5, leaving 69.1% against 70.9%." This rebuilds when the 920 control items are identified from the released category field: 69.08 vs 70.87, difference -1.79 [-3.54, -0.19] by family_id. Our earlier CANNOT_TELL is withdrawn.
```

Optional, same row, field `referee` (typos, not printed on any page): "-1.79 [-3.54, -0.09]" should read "-1.79 [-3.54, -0.19]" (reversal_out.text), and "overall lead +1.59 [+0.23, +2.92]" should read "+1.59 [+0.22, +2.94] by family_id" (reversal_out.text) while the printed [+0.25, +2.89] is the planned question-resampled interval (RESULT.md B1). Three different intervals for the same lead sit in the register and RESULT.md.

## D-11: row arXiv:2610.31135v1, field `priced`
Support: recounts/2610.31135/recount.py line 37 (`agree=np.nanmean(A==B)` over a matrix of 800 questions by 10 positions, so 8,000 cells), recount_out.text lines 12 to 15 ("n 800 item agreement 1.0000" same host, "item agreement 0.9905" A40 against A10G, primacy copy gap +0.0019 [-0.0050, +0.0088] CONSISTENT), RESULT.md B1. 0.0095 x 8,000 = 76 cells. "800 of 800" counted questions and "0.95% items" counted cells, so one line used two units.

old:
```
known-good: separate same-GPU runs identical 800/800; cross-GPU copy 0.95% items change, primacy gap +0.0019 [-0.0050, +0.0088] CONSISTENT; family gap ABOVE on 2 of 5 prompt variants, CONSISTENT on 3; prompt variants also changed GPU (T4/L40S): GPU share CANNOT_TELL
```
new:
```
known-good: separate same-host runs identical on 8,000 of 8,000 question-position cells; cross-GPU copy (A40 against A10G) changes 76 of 8,000 cells (0.95%), primacy gap +0.0019 [-0.0050, +0.0088] CONSISTENT, so it did not move the score; family gap ABOVE on 2 of 5 prompt variants, CONSISTENT on 3; prompt variants also changed GPU (T4/L40S): GPU share CANNOT_TELL
```
Leave `referee` as it is ("same-host copies identical 9,600/9,600; cross-host 0.95% items (8.8% texts) change") because of the pub2.s08 grep. It uses a third unit (records), and the pub2 paper has the same wording (iris_index/pub2/paper/main.tex lines 60 to 61, "9,600 records", "8,000 position items"), which is outside lane D.

## D-18: three receipt lines with quotation marks around paraphrases
Rule: quotes are verbatim or not in quotation marks.

1. Row arXiv:2610.31256v1, field `priced`.
Paper (arXiv 2610.31256v1 text): "frontier GPT-4o (F1 = 50.33) is matched by the smaller Llama-3.1-8B-Instruct (55.55) under five-shot prompting (overlapping CIs; Section 6.4)". The verbatim clause has a semicolon, so the proposal drops the quotation marks. Paired over the same 137 items and the intervals: pub2 paper (main.tex, "Paired over the same 137 items, Llama leads by 5.24 F1 [0.91, 9.81]") and the register's own `referee` (+5.24 [+0.91, +9.81], item wins 55/52/30 ties).
old:
```
5-shot gain ABOVE for all 8 LLMs, paired; "GPT-4o matched by Llama-3.1-8B (overlapping CIs)" -> paired +5.24 [+0.91, +9.81] ABOVE; post-hoc labelled: Llama vs MedGemma CONSISTENT, MedGemma vs GPT-4o ABOVE
```
new:
```
5-shot gain ABOVE for all 8 LLMs, paired. The paper reads GPT-4o as matched by Llama-3.1-8B-Instruct under five-shot prompting because the confidence intervals overlap. Paired over the same items, Llama leads by +5.24 [+0.91, +9.81] ABOVE. Post-hoc labelled: Llama vs MedGemma CONSISTENT, MedGemma vs GPT-4o ABOVE
```

2. Row arXiv:2610.18610v1, field `priced`: covered by the D-7 text above (the quoted sentence is now verbatim).

3. Row arXiv:2610.25964v2, field `priced`.
Abstract (arXiv 2610.25964v2): "That 6.13-point adversarial shift exceeds the adversarial gain reported by five of the six papers we surveyed." The quoted clause below is the paper's words verbatim. The start of the field stays `shift 6.13 [4.43, 7.83] ...` for pub2.s11 and pub2.s12.
old:
```
shift 6.13 [4.43, 7.83] adversarial, 5.37 [3.70, 7.03] popular, 3.15 [1.50, 4.80] random, ABOVE; "exceeds five of six" -> four of six resolved below the interval, one (+5.76) inside, CANNOT_TELL
```
new:
```
shift 6.13 [4.43, 7.83] adversarial, 5.37 [3.70, 7.03] popular, 3.15 [1.50, 4.80] random, ABOVE. The paper says the shift "exceeds the adversarial gain reported by five of the six papers we surveyed". Against our interval four of six gains lie below the lower bound, one (+5.76) inside and one above, so the resolved count is four of six with one undecided. One 4-bit model, so CANNOT_TELL for a matched evaluation
```
(The old text said "exceeds five of six" -> "...CANNOT_TELL". RESULT.md B2 gives "the resolved count is four of six, with one undecided" and the abstract says the comparison "stays unresolved until readout and precision are matched".)
