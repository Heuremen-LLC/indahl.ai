# Copper crossing-node check, round 3 — 2026-09-30 (n=226, ~3.75 hours)

Follows `COPPER_NODES_2_20260930.md` (n=26, 26 minutes). Collector
(`~/copper_spectra/` on the laptop, `c-train-express`, user `ctrai`) has run
continuously since round 2 with no changes — same `systemd-run --user`
unit, same `GET /spectrum?lo=0&hi=1200` once per 60s against the
already-running `sdr_reader_service.py`. Nothing on the laptop was touched
for this task beyond `scp`-pulling `data.jsonl` and `freqs.json` read-only.
Analysis script: `~/bones-forge/parallax/out/copper_nodes/analyze_spectrum_v3.py`
(adapted from the round-2 script; same core functions, same bin definitions,
same local-background window of 3-8 Hz either side, same 6 unrelated
comparison bins, plus a bootstrap CI on the flagged 12 Hz correlation and a
new autocorrelation section (f)). No expectation was written before running
it.

## Collector health

- 226 rows loaded, all parse cleanly (`db` array length matches `freqs.json`
  on every row).
- Span: `ts` 1790767390.4 → 1790780888.5 = 13,498 s ≈ 3h 45m.
- Gaps between consecutive timestamps > 90s: **zero**. Every row landed on
  schedule, one per ~60s, for the full run.
- `systemctl --user is-active copper-spectra` → active at time of pull.
- No `errors.log` file exists on the laptop (never created — no failed
  calls logged), consistent with round 2.
- Collector is healthy: no restarts, no dropouts, no missing rows.

## (a) Crossing/parent level vs local background — median dB, n=226 each

| Hz (actual bin) | median | local bg median | diff |
|---|---|---|---|
| 12 (12.40) | +14.50 | +15.45 | **-0.95** |
| 88 (87.74) | +7.45 | +7.67 | **-0.22** |
| 100 (100.14) | +7.00 | +7.57 | **-0.57** |
| 412 (411.99) | +3.70 | +3.55 | **+0.15** |
| 500 (499.73) | +3.55 | +2.73 | **+0.82** |
| 512 (512.12) | +2.40 | +2.60 | **-0.20** |
| 200 (200.27) | +5.70 | +5.38 | +0.33 |
| 212 (211.72) | +4.90 | +5.20 | -0.30 |
| 300 (300.41) | +5.20 | +4.12 | +1.08 |

At n=226 every crossing's excess over local background is smaller than it
was at n=26 (500 Hz: +3.05 → +0.82; 512 Hz: +2.70 → -0.20). More data
shrank the differences toward zero across the board — the opposite of what
a real signal would do. 12, 88, 100, 512 Hz are all still below or at their
own local background.

## (b) Crossing vs sum-in-dB of its two parents, correlation

Unrelated background bins: 37.0, 383.0, 556.0 Hz (same as round 2).

| crossing | parents | r (real, n=226) | r (3 random bins) |
|---|---|---|---|
| 12 | 200+212 | **+0.011** | -0.046, -0.077, +0.012 |
| 88 | 212+300 | -0.054 | +0.054, +0.052, +0.024 |
| 100 | 200+300 | +0.082 | -0.029, +0.028, +0.022 |
| 412 | 200+212 | -0.004 | -0.128, +0.019, +0.131 |
| 500 | 200+300 | +0.017 | +0.030, -0.091, -0.005 |
| 512 | 212+300 | +0.019 | -0.010, +0.044, +0.078 |

Every crossing correlation is now indistinguishable from its own random-bin
comparisons — all clustered within about ±0.13 of zero, real and random
alike.

## The 12 Hz flag, re-tested

Round 2 (n=26): r(12 Hz, 200+212 sum) = **+0.461**.
Round 3 (n=226): r(12 Hz, 200+212 sum) = **+0.011**.
95% bootstrap CI (resample rows, 5000 draws): **[-0.113, +0.134]**.

The flag did not survive. It collapsed toward zero as data accumulated, and
the 95% CI now brackets zero comfortably. This is exactly the look-elsewhere
pattern named in round 2: one number out of two dozen correlational tries,
picked because it was the biggest at low n, regressing to nothing once the
sample grew ~9x.

## (c) Mains split: R² vs 60+120 Hz, and leftover-vs-leftover correlation

| Hz | r(60) | r(120) | R² |
|---|---|---|---|
| 12 | +0.035 | -0.002 | 0.001 |
| 88 | +0.014 | +0.016 | 0.000 |
| 100 | -0.054 | +0.047 | 0.006 |
| 412 | -0.022 | -0.001 | 0.000 |
| 500 | -0.067 | -0.089 | 0.011 |
| 512 | -0.072 | +0.041 | 0.008 |
| 200 | +0.053 | -0.042 | 0.005 |
| 212 | -0.014 | -0.106 | 0.011 |
| 300 | -0.070 | -0.033 | 0.006 |

No bin shares more than 1.1% of its variance with the 60/120 Hz comb at this
n — even weaker than round 2's already-weak numbers (max was 12.2% at
n=26, now the max is 1.1%). Leftover-vs-leftover:

| crossing | leftover r |
|---|---|
| 12 | +0.010 |
| 88 | -0.052 |
| 100 | +0.084 |
| 412 | -0.003 |
| 500 | +0.012 |
| 512 | +0.019 |

Removing mains changes nothing because mains was never carrying meaningful
variance in any of these bins. Same conclusion as round 2, more firmly.

## (d) 12 Hz vs (200, 212) tercile 3x3 table — now populated, n=226

200 Hz terciles: ≤3.20 (low) / ≤7.80 (mid) / >7.80 (high)
212 Hz terciles: ≤2.20 (low) / ≤6.60 (mid) / >6.60 (high)

| 200 \ 212 | low | mid | high |
|---|---|---|---|
| low | +13.70 (n=24) | +14.50 (n=28) | +15.90 (n=26) |
| mid | +12.80 (n=31) | +14.50 (n=21) | +14.30 (n=23) |
| high | +14.20 (n=21) | +15.55 (n=26) | +14.15 (n=26) |

All nine cells are now well-populated (n=21-31), unlike round 2's n=1-6
sparse table. The pattern is not monotonic in either direction: 12 Hz does
not rise cleanly with 200 or 212 Hz level. The (low,low) cell that round 2
flagged as "consistent with the idea" (n=1, +5.80 dB, lowest in the table)
is now n=24 at +13.70 dB — squarely in the middle of the table's range, not
the low corner the small-n table suggested. The apparent structure at n=26
was sampling noise.

## (e) Full-spectrum scan, 5-1200 Hz, >6 dB above local background in >half of rows

1253 bins scanned. **Zero bins flagged** — same as round 2, now at nearly 9x
the row count. Still nothing clears this bar anywhere in the spectrum,
including the 60 Hz mains harmonics that have a real physical source. This
continues to say more about the bar (6 dB, strict per-row, >50% of rows)
than about absence of any lines — but it is now a much steadier null.

## (f) NEW — time structure: autocorrelation of level series (minutes)

Autocorrelation at lags 1-20 minutes, real row order vs a shuffled-row null
(500 shuffles per bin, 95th percentile of max|autocorrelation| across lags
1-20 as the threshold):

| Hz | lag1 | lag2 | lag5 | lag10 | lag20 | max\|ac\| (lag) | null 95th pct | verdict |
|---|---|---|---|---|---|---|---|---|
| 200 | +0.005 | +0.084 | -0.004 | -0.088 | -0.007 | 0.138 (lag 11) | 0.191 | within null |
| 212 | -0.053 | +0.040 | -0.010 | -0.038 | +0.024 | 0.125 (lag 3) | 0.199 | within null |
| 300 | -0.020 | -0.094 | +0.204 | -0.095 | +0.117 | 0.204 (lag 5) | 0.189 | **above null** |
| 12 | +0.034 | +0.091 | -0.144 | -0.144 → -0.144 | +0.040 | 0.144 (lag 5) | 0.190 | within null |

Only 300 Hz's lag-5 autocorrelation (r=+0.204) sits just above its own
shuffled-null 95th-percentile threshold (0.189) — a 5-minute periodicity
would be an odd thing for a stray RF line to have, and this is one hit out
of 4 bins × 20 lags = 80 lag-values tested (plus the max-stat summary itself
makes multiple comparisons within each bin). It is barely above threshold
(0.204 vs 0.189) and not corroborated by any neighboring lag (lag 4 and
lag 6 aren't reported here but the shape around lag 5 is a single spike, not
a decaying pattern). Flagging it exactly as weakly as it deserves: a
one-off crossing of a noisy line, not evidence of periodic breathing in any
of the four series. 200, 212, and 12 Hz show no autocorrelation structure
beyond what shuffling produces at any lag out to 20 minutes.

## Tries, total: 1414

(a) 9×2=18. (b) 6×4=24. (b-flag bootstrap) 1. (c) 9×3 + 6 leftover = 33.
(d) 1 table (9 cells) = 1. (e) 1253 bins scanned = 1253. (f) 4 bins × 20
lags + 4 max-stat summaries = 84. Total = 1414.

## Bottom line

The single flag carried forward from round 2 — 12 Hz tracking (200+212) at
r=+0.46 — **did not survive**. At n=226 it sits at r=+0.011, 95% CI
[-0.113, +0.134], indistinguishable from the random-bin comparisons and
squarely consistent with zero. This is what look-elsewhere predicts for a
number that was the largest of ~24 correlational tries at n=26: it
regresses to nothing as data accumulates. Every other measure moved the
same direction — level-vs-background gaps shrank (a), mains-shared-variance
shrank further (c), the tercile table filled in and showed no monotonic
structure (d), and the whole-spectrum scan stayed at zero flags (e). The
one new thing that came up positive, 300 Hz's lag-5 autocorrelation just
clearing a shuffled-null threshold (f), is weak and uncorroborated —
noted, not claimed. Four hours of clean, gapless collection turned one
promising-looking correlation into a null result. Collector remains active
and unattended; more rows would settle 300 Hz's autocorrelation the same
way this run settled the 12 Hz flag.
