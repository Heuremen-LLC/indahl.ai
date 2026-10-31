# Ovcharov, arXiv 2608.15428: a recount and a two-setup rerun

Our recount of "Gated Against One Model, Open to the Next" by Volodymyr Ovcharov (arXiv 2608.15428), from his Hugging Face release
overthelex/ua-judge-exam at 337cad5. The plan was committed before any run, with dated addenda before each reading it changes. GIT_LOG.txt
lists the commits with their times. This folder holds each reply's parsed letter and the reason class of any reply with no letter, and no
reply text.

## What rebuilds

From scenario_a.jsonl with our own code, the twelve complete rows of Table 4 rebuild to the printed digits (blind accuracy, interval,
letter shares, n), with the habit taken over each model's parsed items (known_good.text).

## The rerun

Llama 3.1 8B and Ministral 3 8B as Ollama's 4-bit (Q4_K_M) files, the same file digest on two setups of ours: Armature (RTX 3080, Ollama
0.34.3, four server slots) and a Mac (M5 Max, Ollama 0.34.2, one slot). Temperature 0, seed 1, his prompts, his parser, his ids: all
8,128 accepted items blind (arm B) and his 600-item sample in the full condition (arm F), two repeats per setup. Bedrock serves its own
weights format, so these readings are about this model file on our setups.

- The letter habit (rates_both_20261031.text, R3 and R5). Llama 3.1 8B answers the blind items A 0.17, B 0.10, C 0.66, D 0.07 on Armature
  and A 0.18, B 0.10, C 0.66, D 0.07 on the Mac, against A 0.92 in his Bedrock run. Blind accuracy is 0.250 [0.241, 0.260] and 0.249
  [0.240, 0.258], against his 0.292. Ministral 3 8B's blind accuracy is 0.239 [0.230, 0.249] on Armature, his printed 0.239, while its
  letter shares are A 0.00, B 0.43, C 0.42, D 0.15 against his A 0.02, B 0.25, C 0.45, D 0.29.
- Unparsed replies (R4). In the full condition Llama 3.1 8B leaves 12 of 600 replies without a letter on Armature and 11 on the Mac (9 and 8
  of the 400 accepted items), and every one is a single Cyrillic letter. His Bedrock run leaves 285 of 600 (198 of the 400 accepted).
- Repeats and setups (R1, R2b). Each setup repeats itself closely: Armature changes the letter on 15 of 8,128 (llama, blind) and 20 of 600
  (llama, full) items between repeats, the Mac on none (upper bounds 0.045% and 0.61%), and Ministral changes none on either. Between the two
  setups 470 of 8,128, 27 of 600, 349 of 8,128 and 24 of 600 items change letter (4.0% to 5.8%). That is above both repeat floors except for
  Llama in the full condition, where Armature's own floor of 20 is as large (Fisher p 0.37). Accuracy moves by 0.12 to 0.26 points between
  setups (exact McNemar p 0.13 to 1), and for Ministral's blind arm the letter shares themselves shift (Stuart-Maxwell p 1.3e-13). The two
  setups differ in Ollama version, server slots and GPU backend, so this reads the pair as a whole.
- His own reruns (readings_b.text, R8). Between his 600-item blind run and his full blind run, on the 400 items both hold, the letter
  changes on 2 (Gemma 3 12B), 11 (Llama 3.1 8B), 17 (Ministral 8B), 34 (Nova Micro) and 55 (Qwen3 32B) items, while each model's accuracy on
  those items moves by at most one point. His Llama 3.1 8B full-condition runs at 2,048 and 4,096 tokens differ on 43 of 600.
- The parser (READ notes, CHECKS.md.text). It reads every Latin-letter reply we read in full. It misses a reply's final answer in one Mac
  reply of 600, where the answer is written "Відповідь (за загальним правилом): B" and the parser takes the leading C instead. The only
  replies with no letter are single Cyrillic letters (А to Д).

Every reading after the plan's first set was defined after the data, as PLAN.md.text records.

## Run it

src/fetch_theirs.py downloads his seven files at the pinned revision (FILES.tsv) and checks their hashes. Then src/read_gift.py --rates
prints rates_both_20261031.text from the run files in runs/, and src/readings_b.py prints readings_b.text (Python with numpy and scipy).
src/run_gift.py reran the models through Ollama. It reads his prompt strings and parser patterns from his code with Python's ast module,
without running his code. CHECKS.md.text holds our checks.

Heuremen LLC
