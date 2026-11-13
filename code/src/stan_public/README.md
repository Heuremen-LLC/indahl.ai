# STAN v1

A small open model (Qwen3 1.7B base, Apache-2.0, LoRA) that reads a title and abstract and drafts the seven claim-level codes of Faults and Guards 2.0. It sorts for a person to confirm. It is never a gate or a certificate. Read PLAN.md and PLAN_ADDENDUM_1.md first.

Result in one line: v1 is not kept. Pooled agreement difference against the base on gold test is +0.017 with a 95 percent paired bootstrap interval of [0.000, 0.035]. The interval does not exclude zero. STAN also answers CANNOT_TELL on every code of every item, so it sorts nothing.

- data/ gold split, gold and pool abstracts, slices, twins, silver_v1 (frozen training set)
- teachers/ round 1 and round 2 labels per teacher, config
- review_queue/ two-of-three and all-differ pairs for people, spot_check_40.md for a person to mark
- runs/ base and STAN outputs, training run (stan_v1/, weights private)
- results/ baseline_dev, paired_test, stan_dev_stratified, silver_summary_v1, contamination_wall, public_rows
- scripts/ everything, gate.py checks plan committed and stamp submitted
