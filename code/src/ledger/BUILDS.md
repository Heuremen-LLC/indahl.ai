# Every build, one command each (23 Oct 2026; his: "put it all in there, we have to be consistent from here on out")
All entry points live in ~/bones-forge/ledger/. Each one refuses on failure and verifies its own output. Nothing is ever built by hand.

| What | Command | Builds from | Verifies |
|---|---|---|---|
| Both websites + Faults/Guards PDFs + the bill PDF, deployed | `./ship.sh "what changed"` | heuremen.org repo, indahl-ai/build_site.py, ligera/FAULTS.html + GUARDS.html, indahl-ai/qia_template/QIA-2026-001.json | ledger (check_ledger.py), copies (copies.py), specbook (site_gate.py), then every live URL byte-for-byte |
| Zenodo data release | `./build_zenodo.sh v4` | the site's tracked experiments/, the paper, zenodo_README.md, zenodo_extra/ | secret scan; every live ledger source file inside the zip |
| arXiv submission tar | `./build_arxiv.sh` | arxiv_one_readout/main.tex, refs.bib, figures/ | compiles the tar as arXiv would; same pages and text as the live paper; no unresolved refs |
| Checks only | `python3 check_ledger.py` · `python3 copies.py check` · `python3 copies.py live` · `python3 ../heuremen-specbook/site_gate.py` | | |

Rules: a new kind of deliverable gets its build script here the first time it is made. Forms and messages that go with a build
(ZENODO_v4_FORM.txt, ARXIV_FORM_FINAL_*.txt, ENDORSE_MESSAGES_FINAL_DRAFT.txt) are ledger surfaces: check_ledger.py reads them.
