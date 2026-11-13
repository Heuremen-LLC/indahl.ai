# read1 retrain (Sage custody upgrade 2, 5 Nov 2026), rule written BEFORE it runs

Retrain YO Read seed 61 from the git-pinned training files (read/data/train.jsonl d251476e..., valid.jsonl 2b1b3c43...) with yr1.yaml,
changing only adapter_path (to retrain_read1/adapters), on the base snapshot 70d244cc, HF_HUB_OFFLINE=1.
Compare the final adapters.safetensors with the Addendum-4-stamped adapters/read1/adapters.safetensors (d3df26bb...).
- Bit-identical: the stamped adapter vouches for the training file (for read1 only).
- Any other hash: CANNOT TELL. Not a failure. LoRA training on Metal is not promised to be deterministic. A near-miss (similar loss
  curve, small weight difference) is not read as either outcome.
The 200/400/600 checkpoints are compared too, and reported, under the same rule.
