# Wen-data: the legal chain, all the way down (6 October 2026, Wayfinder and Bones)

Every link, what it is, and the text it rests on. Read live on the dates shown; not legal advice, a record.

## 1. What Wen-data is
A measurement categorizer: given a reading from a quantum processor, its baseline and its recent series, it answers
COMMIT, HOLD or NEXT (name the next ruler). It is not a chatbot and does not generate open-ended text. The one-line verdict
under each answer is written by deterministic code (arithmetic on the numbers), not by the model.

## 2. Anthropic's terms (read live 6 Oct 2026)
- Consumer Terms (effective 8 Oct 2025), "Use of our Services": may not use the Services "To develop any products or services
  that compete with our Services, including to develop or train any artificial intelligence or machine learning algorithms or
  models". https://www.anthropic.com/legal/consumer-terms
- Usage Policy, "Do Not Abuse our Platform": prohibits "Utilization of inputs and outputs to train an AI model (e.g., 'model
  scraping' or 'model distillation') without prior authorization from Anthropic". https://www.anthropic.com/legal/aup
- Support, "Can I use my Outputs to train an AI model?": "You can use Claude's Outputs to train models that don't compete with
  Anthropic's own models." Permitted examples include "Content categorization systems" and "Anomaly detection tools".
  Prohibited examples: "General purpose chatbots", "Models designed for open-ended text generation", "Using Outputs as training
  targets for models". https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model
  (quoted via the 6 Oct model-hunt report; the Consumer Terms and Usage Policy lines were read directly.)

## 3. How Wen-data stays inside them
| Link | What we do | Why it's clean |
|---|---|---|
| Purpose | Narrow categorizer for measurements | Matches "content categorization" / "anomaly detection"; does not compete with a general model |
| Training inputs | The house's own measurement numbers (IBM and Rigetti runs, our ledger and reads) in a fixed field layout | Our data, from our runs on our accounts; not Claude conversations, not model distillation |
| Training targets | The mode label only (COMMIT / HOLD / NEXT), decided by arithmetic | No Claude-written sentence is ever a target; the label is a rule applied to numbers |
| Verdict text | Written at answer time by code from the numbers | Not learned from Claude text |
| Exam | 102 items from 51 of the 74 logged misses (receipts_dataset): make_exam.py drops a miss whose reading or correction is under 25 characters (all 23 have a reading under 25 characters; one also has a short correction; none is empty). That gate is not neutral: it drops 12 of 23 "other" and both "unmeasured_claim" receipts (Sage, 3 Nov). Prose written by Bones | Test set only: never trained on |
| Person side | Stopped 6 Oct. Wayfinder's chats are not in Wen | Removes the "inputs and outputs" question entirely |
| Claude's role | Writes the code and the arithmetic rules, like any engineering tool | The Services are not being distilled into Wen |

Belt and braces, available any time: the Usage Policy names "prior authorization from Anthropic" as the route. A one-paragraph
request describing Wen-data as a measurement categorizer would settle it in writing.

## 4. The base model
Qwen/Qwen3-1.7B (prototype) and Qwen/Qwen3-4B-Instruct-2507 (target): Apache License 2.0, commercial use allowed. Keep the
LICENSE and any NOTICE file with every copy of Wen we ship, and state the modifications (our LoRA adapter).

## 5. The hardware data
Job and task results are from our own IBM Quantum and Amazon Braket accounts. The IBM acknowledgment wording is in the paper.
Vendor calibration data used as a baseline is published by the vendors; cite it where it is used.
