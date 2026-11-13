# indahl

Heuremen LLC in one install for every Claude surface: check papers and LLM eval claims against the Standards, and query every indahl.ai desk through the indahl.ai data connector. The full set (Python checks, the readcheck commit gate) is indahl-full in the Heuremen-LLC/indahl.ai marketplace.

```
/plugin install indahl --marketplace Heuremen-LLC/indahl.ai
```

Built by build_bundle.py from the plugins beside it; the parts and their versions:

- standards 1.0.1
- eval-check 1.0.0
- indahl-data 1.0.0

## Services this bundle contacts

- indahl.ai (https://indahl.ai/mcp and https://indahl.ai/qia/audit.json): our own public read-only data. Nothing is stored.

Nothing else is contacted. No personal data is read or stored. Fetched text is treated as data, not instructions.

Each part keeps its own license, under licenses/<part>/. Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.
Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins
