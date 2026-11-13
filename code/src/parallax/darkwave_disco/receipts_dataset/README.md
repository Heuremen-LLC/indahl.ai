---
license: cc-by-4.0
language:
- en
pretty_name: "Receipts, Not Verdicts"
tags:
- corrections
- scientific-method
- preference
- dpo
- measurement
- quantum-computing
- ai-assisted-research
size_categories:
- n<1K
configs:
- config_name: receipts
  data_files: data/receipts.jsonl
- config_name: pairs
  data_files: data/pairs.jsonl
---

# Receipts, Not Verdicts

Seventy-four logged misses from a working research collaboration between Wayfinder and Bones, kept in the order they were made, each with the wrong read, what the record actually showed, and what changed.

Most of these misses are Bones's, caught by Bones, by Wayfinder, or by a reviewer named Shuttle. The research behind them is a set of superconducting-qubit runs on IBM and Rigetti hardware and the statements built on them: [Seven](https://heuremen.org/7.pdf), with every correction published on [the trail](https://thetrailtothepast.com). For an earlier essay from the same collaboration, see [Consent All the Way Down](https://huggingface.co/datasets/Wayfinder6/consent-all-the-way-down).

## What the misses have in common

Most of them are one move: turning an open measurement into a yes/no verdict too early. Calling a result "unexplained" before running the working equation at it. Scoring a call with a ruler it was not built on. Naming a number "near" a constant after looking. Judging structure with a shuffle (a floor proving a floor). Counting from one account key and calling it all of them. The fix is the same every time. Triangulate with time in the triangle, print every ruler beside the others, keep the misses, and write the call down and hash it before the data exists.

## Configs

**receipts** (74 rows): one row per miss.

| field | meaning |
|---|---|
| `id` | R001 ... |
| `source` | `trail correction log` (public corrections, 25), `fuckups list` (35), `run ledger` (owned fuckups, 14) |
| `date` | the day or ledger entry it was logged under |
| `title` | the miss, in a line |
| `failure_mode` | `binary_verdict`, `wrong_ruler`, `after_the_fact_label`, `floor_as_judge`, `miscount_or_scope`, `instrument_not_testing_the_claim`, `unmeasured_claim`, `wrong_statistic`, `overclaim`, `skipped_the_bonefish`, `other` (assigned by keyword; read the text) |
| `wrong_read` | what was said |
| `record_showed` | what the record showed |
| `right_read` | what changed (filled for the 25 trail corrections) |
| `receipt` | where it is logged |

**pairs** (25 rows): the trail corrections as preference pairs. `prompt` names the result, `rejected` is the wrong read, `chosen` is what the record showed plus what changed.

## How it was made

`build.py` (in this repo) reads the three logs and writes both files; nothing is hand-edited after. The logs were written as the work happened, between 28 September and 5 October 2026, and the ledger entries carry their own section numbers. Personal details were never in these logs, and the files were scanned before upload.

## Attribution

Wayfinder and Bones, Heuremen. This work was done with AI assistance. CC BY 4.0.
