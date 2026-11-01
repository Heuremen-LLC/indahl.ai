# faultsguards: the Faults and Guards as a Python package for LLM use. Plan, written before the code.

## What it is
Faults is a catalogue of the failure modes a model commits doing measurement work. Guards is the set of procedures built against them. Both are published as PDFs at heuremen.org. This package makes the same text usable inside an LLM workflow: as structured data, as prompt and checklist builders, and as a stdio MCP server a client can load.

## Rules (fixed now)
1. The data is generated from the published sources (source/FAULTS.html and source/GUARDS.html) by tools/extract.py. Nothing is retyped. A test regenerates the data and requires it to equal the shipped data, and requires every extracted paragraph to occur in the source text.
2. No figure, name or example is added, trimmed or reworded. Figures appear as printed. Where a document gives a score, the full text of that passage is kept. Public copy cites all examples or none: the package never selects a subset to quote as a statistic.
3. The package never calls a model and never touches the network at run time. It builds text and returns it.
4. Use inside a prompt, tool or retrieval step is permitted. Use of the text as training data is not (LICENSE.txt).
5. The PDFs are rebuilt from the same sources in CI and the extracted text must equal the published PDFs' text ignoring spacing.
6. Four outcomes only in anything the package prints about results: ABOVE, BELOW, CONSISTENT, CANNOT_TELL, plus NOTHING_RETURNED for a failed read.
## v0.1 contents
Data: faults.json, guards.json (number, title, family or part, plain text, and the original inline html). API: load, search, get, preflight checklist, system prompt, review prompt. CLI. MCP server over stdio (initialize, tools/list, tools/call). Tests. Reproducible PDF build and verifier.
## Not in v0.1 (the live-builds list)
The Faults/Guards bench runner for local models (it lives in the iris code folder and needs its own plan), a PyPI release (needs the account sign-in), and any scoring of a user's model.
## Not claimed
That loading the text into a model makes the model avoid the faults. The Guards document says discipline does not improve the rate; the package carries that statement unchanged.
