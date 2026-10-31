# Chen, Qu and Wang, arXiv 2608.04355: a recount and readings

Our recount of "The Calibration Floor: Format Repair Can Masquerade as Self-Correction at Small-to-Mid Scale" by Mingguang Chen, Bo Qu
and Licheng Wang (arXiv 2608.04355), from their public repository deepgrounding/calibration-floor at 35851b8. The plan was committed before
the readings, with a dated addendum after the referee pass. GIT_LOG.txt lists the commits with their times. This folder holds no prompt or
reply text, only counts.

## What rebuilds

With our own code, the 29-cell decomposition table (total, content, recovery and loss margins, change rate, headroom) rebuilds from the
stage-2 trajectory files to the printed digits, and so does the constrained-decoding table. Their change rate compares answer strings, and
no GSM8K or MATH answer pair that differs as a string is numerically equal, so string and number agree there.

## Readings

- The token cap (readings.text, D2, and readings_b.text, D2b). We re-encoded every first answer with the Qwen3.5 tokenizer at their pinned
  revision. In the 26 Qwen cells, 680 of the 685 unparseable first answers have exactly the cap length or within 3 tokens of it (671
  exactly), against 9 of 6,315 parsed first answers in the text cells. Code cells are counted apart because 48 of their 1,128 parsed replies
  also sit at the cap. Of the 321 format recoveries (first answer unparseable, final answer right), 320 start from a first answer at the cap.
  Of the 81 unparseable final answers, 80 are at the cap. The five unparseable first answers below the cap are short TriviaQA answers with
  no answer marker. Section 4.9 of the paper names truncation before the answer marker as the source of a missing answer. These counts
  measure it in the released runs.
- TriviaQA at 9B (readings_b.text, D1b). The table in section 9.2 and the sentence after it say the content interval excludes zero at
  both 4B and 9B. In stats_tests.json the 4B interval is [+0.0125, +0.050] and the 9B interval is [-0.015, +0.030]. The 9B cell has 13
  helpful against 10 harmful changes (exact McNemar p 0.68).
- Closure (readings.text, D4, and readings_b.text, D4b). The median closure of 71% holds over the six cells that meet the 8% a0-bad rule
  (71.1%, bootstrap [53.4, 82.5] over task ids). The text says eight cells. Closure is undefined on one of the fourteen constrained cells (0.8B
  GSM8K, zero denominator), and over the other thirteen the median is 75.0%.
- Content margins per cell (readings.text, D1, and readings_b.text, D1b) with helpful and harmful counts, an exact paired test, and their own
  bootstrap interval beside it. Most cells have three or fewer discordant rows, so we give counts and tests there, not widths.

Every reading after the first set was defined after the data, as PLAN.md.text records.

## Run it

src/fetch_theirs.py downloads the 44 data files from their repository at the pinned commit and the tokenizer file at the pinned model
revision (FILES.tsv), and checks every hash. Then run src/readings.py and src/readings_b.py with python3, numpy, scipy and tokenizers
from this folder. Nothing of theirs is run. CHECKS.md.text holds our checks and READ_D2.md.text our read of the at-cap replies.

Heuremen LLC
