# read1 retrain result (5 Nov 2026), read under RULE.md (committed 07657e3 before it ran)

All five files are BIT-IDENTICAL to the original read1 adapters:
- 0000200 37cc2a49..., 0000400 8343c0b0..., 0000600 ae400120..., 0000800 d3df26bb..., final adapters.safetensors d3df26bb...
- The final hash equals the Addendum-4-stamped adapters/read1/adapters.safetensors (d3df26bb...).
- Train loss at 200/400/600/800: 0.054 / 0.047 / 0.043 / 0.028 in both logs.
Reading, by the rule: the stamped adapter vouches for the training input it was trained from, for read1 only:
read/data/train.jsonl d251476e... and valid.jsonl 2b1b3c43... (prompts AND read labels), yr1.yaml, base snapshot 70d244cc,
python 3.12.13 / mlx 0.32.0 / mlx_lm 0.31.3. Any other train.jsonl would have had to produce the same adapter bytes.
The selflabel and shuffled adapters were not retrained; their labels stay pinned by our git (shuffled data also by block 974519).
