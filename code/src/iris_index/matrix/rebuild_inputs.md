# Rebuilding the Matrix inputs (not redistributed)
- inputs/nep_gold.csv and nep_prompt_*.txt: from github.com/iriis-research/NepPlural (data/pools/sample/step3/gold_final.csv;
  results/{forced_single,abstention_baseline}/system_prompt_used.txt).
- inputs/mcq_200.json, mcq4_200.json: from github.com/HKUST-KnowComp/Jev-ToM data/primary/{tomi,bigtom,tomato,tombench-en,cogtom},
  sampled with the seeds in the commit that froze them (20261025 v1, 20261026 v2); script in the freeze commit message context.
- inputs/mcq4_poscontrol.json is ours (generated; included).
