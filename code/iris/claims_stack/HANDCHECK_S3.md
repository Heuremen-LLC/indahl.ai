# Parser hand-check, round S3 (Granite 4.1 3B), 30 Oct 2026
Method: ROUND_S3.md Addendum 2 (handcheck.py, the run's settings). Replies: handcheck/s3_*.json.

## GSM8K 8-shot, plain prompt (task gsm8k, "#### N" answers)
Hand-read correct: 8 of 10. Strict-match and flexible-extract both extracted the hand-read answer on 10 of 10 and scored 8.

## GSM8K CoT 8-shot, chat template
Hand-read correct: 7 of 10 (questions 0, 1, 3, 4, 5, 6, 9).
- Question 5: the model answered $64 (correct) in a closing sentence. Strict-match found no answer and flexible-extract took "16"
  (from "for 16 glasses", the last number). Both filters scored it wrong. Both scored 6 where the hand reading gives 7.
- Question 8: strict-match found no answer, flexible-extract took 315, which is the model's (wrong) answer.
- Every other reply: both filters extracted the hand-read answer.

## BBH CoT 3-shot, chat template (first question of the first 10 subtasks, alphabetical)
Filter: "the answer is (...)". Hand-read correct: 8 of 10 have an answer, 7 of them correct.
- formal_fallacies: the model ended "Therefore, the argument is invalid." (correct). The filter found no answer, so it scored wrong.
- geometric_shapes: the reply reached our 512-token cap before giving an answer. No answer, scored wrong, the filter agrees.
- logical_deduction_seven_objects: the reply stopped after 107 tokens at the task's blank-line stop sequence, partway through its reasoning.
  No answer, scored wrong, the filter agrees. The task stops generation at a blank line, and chat replies use blank lines between steps.
- The other 7: the filter extracted the hand-read answer.

## What it means for the reading
The plain GSM8K read is clean. Both chat GSM8K filters missed one correct answer in 10. On BBH chat the filter missed one correct answer
in 10, and two replies ended without an answer: one at our 512-token cap, one at the task's blank-line stop. All of these push the measured
rate down, never up. They are printed beside the outcome.
