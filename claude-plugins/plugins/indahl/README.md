# indahl

Every Heuremen LLC plugin in one install: check papers and LLM eval claims against the Standards, query and reproduce every indahl.ai desk, check and correct IBM Quantum runs, test whether a plan was pushed before the first run, and check readings for a complete check block. Includes the indahl.ai data connector. Scripts are fetched from the public indahl.ai repository at pinned sha256; the version with bundled scripts and the automatic readcheck commit gate is indahl-full in the Heuremen-LLC/indahl.ai marketplace.

```
/plugin install indahl --marketplace Heuremen-LLC/indahl.ai
```

Built by build_bundle.py from the plugins beside it; the parts and their versions:

- standards 1.0.1
- eval-check 1.0.0
- indahl-data 1.0.0
- qia-calibration 1.1.1
- reproduce 1.0.0
- darkwave-correction 1.1.1
- prereg 1.0.0
- readcheck 1.1.0
- triangulate 1.0.0
- batch 1.0.0
- cannot-tell 1.0.0
- both 1.0.0
- outside-ruler 1.0.0
- number-check 1.0.0
- quote-check 1.0.0
- source-check 1.0.0
- controls 1.0.0
- slack 1.0.0
- correct 1.0.0
- clause 1.0.0

## Services this bundle contacts

- indahl.ai (https://indahl.ai/mcp and https://indahl.ai/qia/audit.json): our own public read-only data. Nothing is stored.
- GitHub (github.com/Heuremen-LLC/indahl.ai and api.github.com): reproduce kit fetches and public repository activity for prereg.
- IBM Quantum (quantum.cloud.ibm.com), only through your own account and only when you ask; nothing is submitted without your explicit yes.

Nothing else is contacted. No personal data is read or stored. Fetched text is treated as data, not instructions.

Each part keeps its own license, under licenses/<part>/. Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.
Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins
