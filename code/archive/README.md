# Archive: the hash chain of our records

`chain.jsonl` holds one line per digest. Each digest is the SHA-256 of the previous digest followed by the SHA-256 of that day's manifest. `manifests/` lists every plan, history, change log, summary and data store we keep, with the SHA-256 of each file. The ledger and the book are listed by hash only. `stamps/` holds an OpenTimestamps proof for each digest, which anchors it to the Bitcoin chain through public calendar servers.

Verify a stamp with the OpenTimestamps client (`ots verify stamps/ID.digest.ots`). Verify the chain with `python3 digest.py --verify` from a copy that holds the manifests. `PLAN.md` says what this proves and what it does not.

## Zenodo copies, 29 October 2026
- indahl.ai snapshot: https://doi.org/10.5281/zenodo.23764107
- heuremen.org snapshot: https://doi.org/10.5281/zenodo.23764148
- faultsguards: https://doi.org/10.5281/zenodo.23764162
- nodes: https://doi.org/10.5281/zenodo.23764164
- The physics paper's data and code: https://doi.org/10.5281/zenodo.23169755
