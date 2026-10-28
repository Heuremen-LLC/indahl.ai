# Public update 1: a trained Falcon, Faults and Guards (28 Oct 2026, his word)
Written and committed before any training item exists and before any trained-model reply exists. The question: does fine-tuning a small open model on fresh Faults and Guards items change how often it commits the Faults, against a prompt-only Guard and against a model trained the same way on shuffled labels.

## Base and license
Falcon3 3B Instruct (the model behind falcon3:3b on our seat). Weakest on our own bench: guard-arm fault rate 0.927 and an empty reply on every P3 and P4 item in round 11, so the most room to move.
The license text is read in full and quoted in the release notes before anything ships. If it bars the release, the same pipeline runs on Qwen3 1.7B (Apache-2.0, the YO base) and this plan is amended in a dated addendum.

## Data (never the bench items)
Training items come from the same generators as rounds 1 to 13 (items.py families P1 to P4) with seeds from 20270001 upward. None of those seeds, stories or numbers appears in rounds 1 to 13 or in the two evaluation sets. A script checks the overlap of seeds and of full item text before training and prints the count (must be zero).
Targets are written by rule from the item truth, in ten wordings per family so the model cannot learn one template: P1 commits to the stated comparison with the width, P2 gives the figure with its width, P3 checks the arithmetic, P4 gives the mean with the spread and not the best seed.
Evaluation sets: two new sets of the bench's size, built with seeds 20271001 and 20272001 and committed before training starts. Same ten-model bench scorer, same gates, same parser hand-check.

## Arms (all on the same evaluation items, temperature 0)
1. Base.
2. Base with the Guard wording (already measured every round).
3. Trained, true labels.
4. Trained, shuffled labels: same items, same wordings, same length and format, with the outcome assigned at random across items. Anything arm 3 gains that arm 4 also gains is format, not content.
5. Trained, true labels, evaluated with the Guard wording in the prompt.

## Training
LoRA with mlx-lm on this Mac, one worker, nothing else on the machine disturbed (our own model seat only). Rank, learning rate, steps and the number of items per family are fixed here before the run: rank 16, learning rate 1e-4, 600 steps, 400 items per family. One run per arm 3 and 4. No tuning after reading any evaluation reply. A second seed of arm 3 only if the first run fails to train (loss does not fall), declared as an addendum.

## Reading
Per family, the paired fault difference (trained minus base, and trained minus shuffled) with a bootstrap of 2,000. Outcomes AHEAD, BEHIND, CONSISTENT, CANNOT_TELL. A gain is reported only where the interval excludes zero in both evaluation sets and arm 3 beats arm 4. Where a gate fails the family is CANNOT_TELL and says so. Empty and cut-off replies are reported as their own counts, never dropped. No ranking of models. Rates side by side with the earlier rounds, never pooled.

## Release
Notes, the generator, the seeds, the training log, the weights if the license allows, and every reply, with the vendor-response path open on the page. Each release gets its own DOI. The terms on the weights follow the base license.

## ADDENDUM 1 (28 Oct, before any training item was used or any trained-model reply exists)
1. All five arms run through MLX in bf16 with greedy decoding on this Mac, so base and trained models differ only in the adapter. The Ollama copy is not used here. The reply budget is 1,500 tokens, as in the bench.
2. The shuffled-label arm is implemented as a mixed-label arm. Labels in P2 and P4 are constant (always a width, always a mean), so a permutation would change nothing. In the mixed-label set each target is the correct form with probability 0.5, independent of the item, and otherwise the faulty counterpart (a forced verdict on a tie or a refusal on a clear gap, an accuracy with no width, a flipped yes or no, the best seed reported). Same items, same wordings, same lengths.
3. Training stories (12) and evaluation stories (2) are new and none appears in rounds 1 to 13. Training seeds are 20280001 upward in steps of 17, chosen so they cannot meet the evaluation seeds 20271001 and 20272001. A first attempt used spacing 100 from 20270001 and one seed met evaluation set A, caught by the overlap check and replaced before any training. The check compares full prompt text and finds none identical. P1 and P2 draw from small number spaces, so a pair of scores or a (k, n) pair can recur under another story. That count is printed by check_overlap.py and is not a failure.
4. Base license: the Falcon license page (TII) is Apache-2.0 based with an acceptable use policy and a hosting-use clause for offering the model as an API. We would release weights and notes, not an API. The release notes quote the license text and carry the modification notice it requires.
