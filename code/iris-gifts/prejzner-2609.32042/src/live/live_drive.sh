#!/bin/bash
# G1 live arm (PLAN Addendum 1): five files, two repeats each, one GPU job, sequential. Name ends in drive.sh so the lab queue sees it as busy.
cd "$(dirname "$0")"; M=../../models; O=runs
for rep in 1 2; do
  ./lcpvenv/bin/python -I run_live.py bielik-11b-v3 Q4_K_M $M/speakleash.Bielik-11B-v3.0-Instruct.Q4_K_M.gguf v3_11b_2026-06-18__q4_no_repair $rep $O
  ./lcpvenv/bin/python -I run_live.py bielik-11b-v3 Q3_K_M $M/speakleash.Bielik-11B-v3.0-Instruct.Q3_K_M.gguf v3_11b_2026-06-18__q3_no_repair $rep $O
  ./lcpvenv/bin/python -I run_live.py bielik-11b-v3 Q2_K $M/speakleash.Bielik-11B-v3.0-Instruct.Q2_K.gguf v3_11b_2026-06-18__q2_no_repair $rep $O
  ./lcpvenv/bin/python -I run_live.py llama-pllum-8b Q3_K_M $M/Llama-PLLuM-8B-instruct.Q3_K_M.gguf v3_pllum_2026-07-29__q3_main_no_repair $rep $O
  ./lcpvenv/bin/python -I run_live.py llama-pllum-8b Q2_K $M/Llama-PLLuM-8B-instruct.Q2_K.gguf v3_pllum_2026-07-29__q2_main_no_repair $rep $O
done
echo "ALL RUNS IN $(date -u +%Y-%m-%dT%H:%M:%SZ)"
