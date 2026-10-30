# Parser hand-check, round S1 (SmolLM2-1.7B-Instruct), 30 Oct 2026
Done after the S1 outcomes were published (11:12 UTC), not before. The plan order was the other way round, see ROUND_S1.md Addendum 7.
Method: as HANDCHECK_S2.md. handcheck.py regenerates the replies with the settings of the run (run_s1b.sh: batch size 4, seed 20281028, the lm_eval path that mlx_lm evaluate uses, original bf16 weights), limited to the first 10 test questions (GSM8K) or the first question of each of the first 10 subtasks in alphabetical order (BBH). The chat runs used the chat template without the few-shot examples as turns, so those two were regenerated with HC_MULTITURN=0. GSM8K ran with no token cap set (the mlx_lm default), BBH with 256. Replies: handcheck/s1_*.json.
For each reply we read the model's final answer by hand and compared it with what each filter extracted. A reply passes when the two are equal. More than 1 of 10 off makes that variant CANNOT_TELL (parser).

## GSM8K 5-shot, plain prompt (no chat template)
All 10 replies are empty. The model ends its reply at once under the plain prompt, as ROUND_S1.md Addendum 2 found. Both filters extracted nothing and the hand reading finds no answer. Parser agrees on 10 of 10. Hand-read correct: 0 of 10.

## GSM8K 5-shot, chat template (few-shot examples in one message)
Hand-read correct: 4 of 10 (questions 0, 1, 3, 9).
- Strict-match found no answer on 4 of 10 (questions 0, 1, 2, 8). The pattern needs a closing line "#### N" and these replies end another way. Question 0 ends "... = $<<9*2=18>>18 every day." (correct) and question 1 ends "$\boxed{3}$ bolts of fabric" (correct). Question 2 ends "$\boxed{\$120,000}$" and question 8 ends "John is 355 miles from home" (both wrong). Strict-match scored 2 where the hand reading gives 4.
- Flexible-extract scored 4, the same as the hand reading. It took "4" on question 8 (from "those 4 hours", where the model answered 355), on a reply that is wrong either way. Off on 1 of 10.
- Result: strict-match is off on 4 of 10 and is CANNOT_TELL (parser). Flexible-extract passes.

## GSM8K 5-shot, chat template with the few-shot examples as turns
Hand-read correct: 4 of 10 (questions 0, 3, 6, 9). Both filters scored 4.
- Question 8: the reply ends "approximately $\boxed{67.65}$ miles from home" (wrong). Strict-match found no answer and flexible-extract took "4" (from "those 4 hours").
- Every other reply: both filters extracted the hand-read answer, a "#### N" line.
- Result: each filter is off on 1 of 10, on a reply that is wrong either way. Both pass.

## BBH 3-shot, plain prompt (first question of the first 10 subtasks)
The task has no extraction filter. The metric is exact match of the reply with the target, and the reply is used as it comes.
Hand-read correct: 4 of 10. Scored correct: 0 of 10.
- boolean_expressions: the reply is " False" and the target is False. Correct, scored 0.
- date_understanding: " (B)", target (B). Correct, scored 0.
- formal_fallacies: " invalid", target invalid. Correct, scored 0.
- hyperbaton: " (A)", target (A). Correct, scored 0.
- causal_judgement: " Yes", target No. Wrong, scored 0, agrees.
- disambiguation_qa, geometric_shapes, logical_deduction_five_objects and logical_deduction_seven_objects: the reply is empty. No answer, scored 0, agrees.
- dyck_languages: the reply is "[ [ [ ..." repeated to the cap. Wrong, scored 0, agrees.
Every plain reply that has an answer begins with a space, and the exact-match metric does not strip it. The chat run's replies, which have no leading space, score 1 on the same kind of answer.
- Result: off on 4 of 10. Plain is CANNOT_TELL (parser).

## BBH 3-shot, chat template (same 10 questions)
Hand-read correct: 2 of 10 (boolean_expressions "False", date_understanding "(B)"). Scored correct: the same 2.
The other 8 are wrong by hand and scored 0: causal_judgement "Yes" (target No), disambiguation_qa "(C) Ambiguous" (target (A)), dyck_languages "[ [ [ ..." repeated, formal_fallacies "valid" (target invalid), geometric_shapes "(D)" (target (B)), hyperbaton "(B)" (target (A)), logical_deduction_five_objects "(C)" (target (A)), logical_deduction_seven_objects "(E)" (target (D)).
- Result: parser agrees on 10 of 10. Chat passes.

## What it means for the reading
S1-08 (BBH): the plain rate 0.0 is the metric scoring a leading space as wrong on correct answers. It is printed beside the outcome as CANNOT_TELL (parser) and does not count. The counted variant is chat, 28.6 ± 1.1. The stated 32.2 is above it, and the card ran lighteval, so the row stays CANNOT_TELL with its direction beside it.
S1-09 (GSM8K): the plain variants read 0.4 because the replies are empty (10 of 10 in the first 10 questions). Chat strict-match (30.3) is CANNOT_TELL (parser) and does not count. The counted variants are chat flexible-extract, chat-with-turns strict-match and chat-with-turns flexible-extract, and the stated 48.2 sits inside all three intervals. The row stays CONSISTENT, as a bound under our harness.
Every rate in the live block was read before this hand-check. The outcomes in outcomes_s1.json are rescored with the parser flags and no row outcome changed.
