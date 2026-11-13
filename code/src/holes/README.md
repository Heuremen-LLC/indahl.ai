# holes/ -- outside-kept timelines of holes

Companion to the ABSENCE LEDGER (`~/bones-forge/standoff/absence_ledger.jsonl`, our own failed runs).
This folder holds holes recorded by OUTSIDE parties about their own systems: outages, gaps, broken parts.
Free, public or already-held credentials, read-only. Nothing is submitted, nothing is spent.
No interpretation lives here, only the holes.

Output: `outside_holes.jsonl`, one JSON per line, the absence-ledger schema plus `kind`:

    id, provider, device, status, at, ended, shots, reason, kind

It is kept apart from the run ledger on purpose. Both scripts dedup by `id` and only append.

## 1. NIST Randomness Beacon 2.0 -- `nist_beacon.py`

- **Source:** beacon.nist.gov/beacon/2.0. One signed, hash-chained 512-bit pulse every 60 s.
- **How NIST marks holes** (NISTIR 8213 draft, Table 5; bit flags on the pulse AFTER the event):
  1 = randLocal with no matching precommitment, 2 = time gap, 4 = certificate changed, 8 = end of chain.
  Also: `pulseIndex` counts emitted pulses, so a gap is `time(b) - time(a) > (b - a) * 60 s`. Some indices
  inside a chain answer 404. A new `chainIndex` means a restart.
- **Method:** there is no range endpoint, so the script bisects on pulse index. `excess = time(b) - time(a) - (b-a)*period`
  is a sum of per-step gaps, so a clean sub-range (excess 0, same certificate at both ends) is never fetched.
  Split points are aligned to powers of two, so a re-run reuses almost the whole cache. Pacing is about 6 req/s
  with 6 in flight, with backoff on 429/5xx, and every 404 is re-checked once. Raw pulses are cached in `cache/nist/c<chain>/p<index>.json`,
  and confirmed 404s as `p<index>.json.404`.
- **Kinds:** `beacon-gap` (at = first missing minute, ended = resuming pulse, shots = missing pulses),
  `skipped-index` (index answers 404), `cert-change`, `chain-restart`, `status-flag` (non-zero status with no gap; none found).
- **Coverage (2026-09-26 run):** chain 1 2018-07-23T19:26Z .. 2022-04-29T21:24Z (1,801,851 pulses);
  chain 2 2022-09-21T19:32Z .. present (1,958,628+ pulses).
- **Counts:** 3,031 holes. 3,019 beacon-gap (1,444 chain 1, 1,575 chain 2), 7 cert-change, 4 skipped-index
  (chain 2 pulses 301, 40410, 41036, 67129), 1 chain-restart (2022-04-29 -> 2022-09-21, 208,687 missing minutes).
  Missing minutes across all gaps: 332,027. This equals the chain-level excess, so every gap was accounted for.
  Resuming-pulse status on the gaps: 2,989 x status 2, 25 x status 0 (not flagged by NIST), 4 x status 6, 1 x status 3.
- **Not covered:** Beacon 1.0 (2013-09 .. 2018-12-26, `/rest/record/<unix s>`). It has no pulse index, so it can't
  be bisected. Walking it means about 2.8 M single fetches.
- **Blind spot:** a skipped index with no time jump subtracts from excess. It could in principle cancel an equal
  time gap in the same range. No negative excess was seen.

## 2. IBM Quantum calibration history -- `ibm_calibration.py`

- **Source:** `backend.properties(datetime=...)` via qiskit_ibm_runtime 0.49 and the key at `~/bones-forge/.ibm_quantum_key`
  (instance `open-instance`). This is a REST GET of IBM's calibration record. It submits no jobs and uses no runtime seconds.
- **Method:** one snapshot per complete UTC day (as of 23:59:59Z) for every backend the key sees, going back 900 days.
  Snapshots are de-duplicated by `last_update_date`. Condition runs are merged across calibrations:
  `at` = first calibration showing the condition, `ended` = first calibration where it is gone (`''` = still open).
  Cached gzipped in `cache/ibm/<backend>/<YYYY-MM-DD>.json.gz` (404 days stored as `{}`).
- **Kinds and thresholds:**
  `gate-nonoperational` (IBM operational flag 0, or gate_error >= 1, IBM's broken-gate marker),
  `qubit-extreme` (T1 < 10 us, readout_error >= 0.25, or T1/readout missing/NaN),
  `qubit-nonoperational` (IBM operational flag 0 on a qubit),
  `no-calibration` (> 36 h between consecutive calibrations, or a 404 day inside coverage).
  IBM's current properties carry **no qubit `operational` field**, so `qubit-nonoperational` is always 0.
  Missing or NaN T1 is the closest thing IBM exposes.
- **Coverage (2026-09-26 run):** ibm_fez 2024-05-15 .. 2026-09-25 (800 distinct calibrations), ibm_marrakesh 2024-10-07 .. 2026-09-25 (699),
  ibm_kingston 2025-03-15 .. 2026-09-25 (530). Older days return 404 (IBM's retention). No 404 days inside coverage.
  Retired backends are not visible to this key.
- **Counts:** 11,833 holes (through 2026-09-25).
  fez 4,814 (4,214 gate, 575 qubit-extreme, 25 no-calibration),
  marrakesh 4,840 (3,969 gate, 851 qubit-extreme, 20 no-calibration),
  kingston 2,179 (1,779 gate, 382 qubit-extreme, 18 no-calibration).
- **Resolution:** one snapshot per day. A condition that appears and clears within one day is invisible.

## Refresh

    cd ~/bones-forge/holes
    python3 nist_beacon.py                               # new gaps since last run; few hundred requests
    ~/bones-forge/qvenv/bin/python ibm_calibration.py    # fetches only days not yet cached

Both scripts are idempotent. IBM runs that were open and have since closed get their `ended` filled in place.
Logs: `nist_run.log`, `ibm_run.log`.

## 3. LIGO/Virgo/KAGRA (GWOSC) -- `ligo_holes.py`

- **Source:** gwosc.org/timeline/segments/json/<dataset>/<det>_DATA (one call per run/detector, no account). Raw JSON in `cache/gwosc/`.
- **Holes:** `data-off` = run span minus `{det}_DATA`. `cat1-veto` is coded but EMPTY: GWOSC's public `CBC_CAT1` segment list is
  identical to `DATA` for every run/detector (CAT1 is already cut from the public data). Output `ligo_holes.jsonl` (13,035 holes,
  rewritten each run) + `ligo_coverage.json` (run spans). Runs: O3a, O3b (H1/L1/V1), O3GK (K1), O4a (H1/L1), O4b (H1/L1/V1). Nothing
  public after 2025-01-28.

## 4. The lineup -- `lineup.py`, `anomaly_jobs.py`, `anomaly_lineup.py`

Pre-registered in gridsong/biblioteca.md (2026-09-26 THE BIG-SMALL HOLE LINEUP + ADDENDUM). Outputs `lineup_results.json`,
`anomaly_lineup_results.json`, `anomaly_jobs.json` (our 9/24 anomaly jobs' IBM metadata, cache/ibm_jobs/), `lineup.png`.
Run with `~/bones-forge/qvenv/bin/python` (numpy/matplotlib).
