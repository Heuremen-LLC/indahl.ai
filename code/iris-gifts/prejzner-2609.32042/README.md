# Prejzner, arXiv 2609.32042: a recount and a live rerun on a second backend

Our recount of "Quantization Thresholds Replicate, Failure Modes Do Not" by Jakub Prejzner (arXiv 2609.32042), from his repository
JakubPrejzner/polagentbench at a816ba4, and a rerun of five of his model files on our Mac. The plan was committed before any model call,
with dated addenda before each reading they change. GIT_LOG.txt lists the commits with their times. This folder holds our pass verdicts, parse
error categories and a SHA-256 of every reply, and no reply text.

## What rebuilds

From per_task_main67.csv with our own code, pass rates per model and quantization and the Q3_K_M to Q2_K paired tables rebuild as printed
(known_good.text). Our own replica of his parser, oracle and tool environment reaches his verdict on all 17,973 logged steps (src/env/BUILD.md).

## The rerun

His five GGUF files that we could match by hash (Bielik-11B Q4_K_M, Q3_K_M, Q2_K and PLLuM-8B Q3_K_M, Q2_K), llama-cpp-python 0.3.19 built from
the PyPI source on an Apple M5 Max, his call arguments (n_ctx 8192, temperature 0, top_p 1, max_tokens 512, seed 42, his chat formats), his 67
main tasks in his run order, repair off, two fresh-process repeats per file. His runs were on an RTX 4090 with a CUDA build. The library's own
prompt formatter matched our rendered prompt on every call.

- His thresholds, reproduced on a second backend (readings.text, P3 and P4). Bielik-11B falls from 47 passes at Q3_K_M to 5 at Q2_K (his 48 to
  3), PLLuM from 14 to 1 (his 15 to 1). The 11B dip reproduces too: Q4_K_M 34 against Q3_K_M 47 (his 36 against 48), exact p 0.029,
  uncorrected and with twins counted. We tested only the Q3_K_M side of his dip.
- Our repeats and his run (P1, P2). Our two repeats of each file were identical in every task outcome and every reply. Against his runs, pass
  counts differ by at most 2 per file, while 22 of 335 task outcomes change, 10 in our favour and 12 in his. Every reply in a task is
  identical to his on 40, 56, 25, 23 and 24 of the 67 tasks of the five files.
- The twins (readings_b.text, T1 and P4b). His ten matched twin pairs send the same prompt twice within a run. On these five files, the two
  members give identical replies throughout on 49 of 50 pairs in our run and 32 of 50 in his. With both members of every pair removed, his
  11B dip reads p 0.143 (his paper's 0.14), and ours reads p 0.019 (23 against 34 passes of 47).

Every reading after the plan's first set was defined after the data, as PLAN.md.text records.

## Run it

src/fetch_theirs.py downloads his task matrix, model manifest and the five trajectory files at the pinned commit (FILES.tsv) and checks their
hashes. Then src/live/read_live.py and src/live/read_live_b.py print readings.text and readings_b.text from the run files in runs/, and
src/known_good.py prints known_good.text (Python standard library). To rerun the models, clone his repository at a816ba4 into theirs/, fetch
the GGUF files with src/live/fetch_gguf.py, build llama-cpp-python 0.3.19, and run src/live/live_drive.sh. CHECKS.md.text holds our checks.

Heuremen LLC
