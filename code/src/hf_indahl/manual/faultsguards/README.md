---
license: other
license_name: heuremen-attribution-no-training
license_link: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards/blob/main/LICENSE.txt
language:
- en
pretty_name: Faults and Guards
tags:
- evaluation
- llm-failure-modes
- measurement
- prompting
size_categories:
- n<1K
---

# Faults and Guards

Faults is the catalogue of failure modes a language model commits doing measurement work. Guards is the set of procedures built against them. Published by Heuremen LLC as PDFs at https://heuremen.org/faults.pdf and https://heuremen.org/guards.pdf.

`entries.jsonl` has one row per fault or guard: `document` (faults or guards), `number`, `title`, `part` (the family or part it sits in), and `text`, exactly as published. `faults.json` and `guards.json` hold the whole documents with their introductions and sections. The numbers are stable identifiers and do not run in family order.

The Python package that loads this text into prompts, function-calling schemas and an MCP server is at https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards. It generates this data from the published sources and tests that it does.

Page on indahl.ai: https://indahl.ai/iris . Package: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/faultsguards and https://pypi.org/project/faultsguards/ .

## Terms

Free to download, read, run and cite with attribution (Heuremen LLC, https://heuremen.org). Use inside a prompt, a tool call, a retrieval step or a review at the time a model answers is permitted. Text and data mining, and use of this text to train, fine-tune or build AI models, are not permitted. This is an express reservation of rights. See LICENSE.txt and https://indahl.ai/terms#ai-training.
