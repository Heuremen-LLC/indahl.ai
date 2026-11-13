# Public update 1, round 3: is the trained Falcon result a property of one training seed? (28 Oct 2026)
Written and committed before the second seed is trained and before any reply from it exists.

## Question
Rounds 1 and 2 used one training run per arm. A different random seed could change which items the adapter gets right. Train both arms again with a different seed and read all four evaluation sets.

## What changes
Only the training seed: 20280007 becomes 20290007. Same base model, same data folders (data_true, data_mixed), same rank, learning rate, steps and items, same scorer and gates. Adapters are written to adapters_true_s2 and adapters_mixed_s2, models are keyed falcon3_trained_s2 and falcon3_mixed_s2. The seed 1 adapters are not touched.

## Evaluation
Sets A, B, C and D, all three reply arms, temperature 0, 1,500 token budget, bf16 on MLX, exactly as before. The untouched model's replies already exist and are reused.

## Reading (the plan 1 rule, unchanged)
Paired fault difference per family, trained minus untouched and trained minus mixed, bootstrap of 2,000, seed 7, gates as before. A result is called replicated across seeds for a family only where the seed 2 trained model is ahead of the seed 2 mixed-label model in all four sets and the seed 1 reading was ahead in sets A and B. Seed 1 and seed 2 rates are published side by side, never pooled. Parser hand-check on ten replies per family for two models before any score is read.

## Release
The replies, scores, scripts and this plan, with the vendor-response path open. Weights stay unreleased until the license text is quoted in release notes.
