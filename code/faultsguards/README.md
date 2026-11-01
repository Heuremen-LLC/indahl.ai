# faultsguards

The Faults and Guards from Heuremen LLC as a Python package. Faults is the catalogue of failure modes a model commits doing measurement work. Guards is the set of procedures built against them. The PDFs are at https://heuremen.org/faults.pdf and https://heuremen.org/guards.pdf. The text is also a dataset at https://huggingface.co/datasets/indahl/faultsguards. This package makes the same text usable inside an LLM workflow: structured data, prompt and checklist builders, function-calling schemas, and an MCP server.

Live page: https://indahl.ai/iris (the Faults and Guards bench and findings). Dataset: https://huggingface.co/datasets/indahl/faultsguards.

Standard library only. It never calls a model and never touches the network. It builds text and returns it.

## Install

```
pip install git+https://github.com/Heuremen-LLC/faultsguards
```

## Look things up

```
python -m faultsguards faults              # the failure modes by family
python -m faultsguards guards              # the procedures by part
python -m faultsguards show guard 8        # one entry in full
python -m faultsguards search two option   # words in titles and text
```

## Put the guards in front of a model

```python
import faultsguards as fg
system = fg.system_prompt()                 # titles only, short. full=True includes every guard's text
ahead  = fg.preflight("Compare our model against the vendor claim.")   # the guards that run before the work, then your task
review = fg.review_prompt(my_text, numbers=[1, 3, 4])                  # asks a model to review a text against chosen faults
```

Each builder marks its own wrapper sentences with "Package line:" so you can tell them from the published text. The review labels are COMMITS, AVOIDS, CANNOT_TELL, NOT_APPLICABLE.

## Function calling

`fg.tool_schemas()` returns schemas for list, get, search, preflight and review. `fg.call_tool(name, args)` runs a call and returns the result. See examples/03_tool_calling.py.

## MCP

```
python -m faultsguards mcp
```

Newline-delimited JSON-RPC over stdio: initialize, tools/list, tools/call, ping. A client config is in examples/04_mcp_client_config.json.

## What is tested

The data in `src/faultsguards/data` is generated from `source/FAULTS.html` and `source/GUARDS.html` by `tools/extract.py`, and a test regenerates it and requires it to equal what ships. Every extracted paragraph is checked to occur in the source. The MCP server is driven through real stdio. Every example runs offline in the test suite. CI rebuilds both PDFs from the sources with headless Chrome and requires their text to equal the published PDFs, ignoring spacing.

```
python -m unittest discover -s tests
python tools/build_pdfs.py build && python tools/verify_pdfs.py build
```

## What this does not claim

Loading this text into a model is not shown to make the model avoid the faults. The Guards document reports that discipline did not change the rate of the most common failure, and that is carried here unchanged. A model test of the effect needs its own plan and is not part of this release.

## Terms

Free to download, read, run and cite with attribution. Use inside a prompt, tool or retrieval step at answer time is permitted. Use of the text to train, fine-tune or build AI models is not permitted. See LICENSE.txt. Heuremen LLC, https://heuremen.org.
