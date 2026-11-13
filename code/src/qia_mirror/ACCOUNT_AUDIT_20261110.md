# IBM Quantum account audit, 10 Nov 2026 (read-only)

Read on 10 Nov 2026 about 11:00 to 11:15 UTC with qiskit-ibm-runtime 0.49.0 (qvenv). The audit only listed and read. No job was sent, no instance or setting was changed and no key was printed. Raw pulls: scratchpad `probe.json` and `probe_dw.json` (job ids, backends and charged seconds only).

## 1. Keys, instances, plans

How we authenticate: there is no saved account (`~/.qiskit/qiskit-ibm.json` is `{}`) and no IBM environment variable. Scripts read key files in `~/bones-forge/` and pass the key to `QiskitRuntimeService(channel='ibm_quantum_platform', token=<KEY>)`. The `ibmcloud` CLI is not installed, so we have no IBM Cloud billing view. Costs below are worked out from charged seconds at $1.60 per QPU second, the Pay-As-You-Go rate in our records. The API's resource units agree: 232.3 RU for 14,567 s works out to about $96 a minute.

| Key file | What it sees |
|---|---|
| `.ibm_quantum_key` | no instances (old account) |
| `.ibm_quantum_key_2` | no instances |
| `.ibm_quantum_key_4` | no instances |
| `.ibm_quantum_key_3` | the 3 instances below |
| `.ibm_quantum_key_parallax` | the same 3 instances (same account, a/5aff3207…) |

| Instance | CRN id (tail) | Region | Plan | Billing |
|---|---|---|---|---|
| **Darkwave Disco** | e09bf202 | us-east | **pay-as-you-go** | **PAID** |
| **Quaker Instance** | a463f88e | eu-de | **pay-as-you-go** | **PAID** |
| open-instance | 864a532f | us-east | open | free |

The CRN `a/c7786c07…` hard-coded in `quantum_archive/quantum/*.py` belongs to an older account that none of the current keys reach.

### Which instance each live script uses by default

| Script | Instance by default | Runs on its own? | Bills? |
|---|---|---|---|
| `arxiv_one_readout/sweep_run/sweep.py` `service()` (`KEYFILE, INSTANCE = '.ibm_quantum_key_3', 'Darkwave Disco'`). Used by `the_show/runs/2026-10-31-darkwave-clock/fire_clock.py` and `darkwave_daily/daily_table.py` | Darkwave Disco | YES: tick bus `clock_daily.py` and `table_daily.py` (every 6 ticks, gates `DAILY_ON` and `TABLE_ON` present) | **PAID** |
| `qia_cal/cal.py --send` (US: `channel='ibm_cloud'`, instance = `.ibm_quantum_instance_crn` = e09bf202) | Darkwave Disco | YES: tick bus every 11 ticks, last sends 10 Nov 10:10 UTC | **PAID** |
| `qia_cal/cal.py --send --eu` (first `:eu-de:` CRN on the parallax key) | Quaker | YES: tick bus every 11 ticks | **PAID** |
| `qia_queue/queue_probe.py` (default and `--eu`) | Darkwave / Quaker | sending riders stopped 30 Oct, only `--collect` runs | PAID if run by hand |
| `queue_probe.py --open` | open-instance | stopped | free |
| `qia_mirror/ibm_mirror.py` | none pinned (first instance) | yes, every 5 ticks | no: it reads backend properties only, 0 QPU seconds |
| `fire_sweep_inst.py`, scripts with `INSTANCE = '.ibm_quantum_key_3', 'open-instance'` | open-instance | by hand | free |
| 176 calls to bare `QiskitRuntimeService()` | none (saved account empty) | they fail | no |

**Flag:** all four tick-bus senders above default to a paid instance. Their only stops are the usage floors: `RESERVE`/`FLOOR` = 60 s for the darkwave pair, `KEEP_S` = 100 s (US) and 50 s (EU) for cal.py. Until those floors are reached, they keep spending the paid caps.

## 2. Usage, limits, cost

| Instance | Consumed | Limit | Remaining | Cost at $1.60/s |
|---|---|---|---|---|
| Darkwave Disco | 14,567 s | 18,000 s | 3,433 s | ≈ $23,300 consumed, ≈ $5,500 more possible before the cap |
| Quaker | 643 s | 900 s | 257 s | ≈ $1,030 consumed, ≈ $410 more possible |
| open-instance | 519 s in the rolling 28 days | 600 s | **81 s free now** | $0 |

The paid instances' counters do not reset monthly. Darkwave's 14,567 s equals the sum of every job since its first one on 2 Oct. The cap was raised several times: 625 s on 4 Oct, then 12,000, then 14,000 (around 2 Nov), then 18,000 (between 3 and 6 Nov).

The open-instance window rolls. 508 of its 519 s were 19 jobs on 22 Oct (fez 266, marrakesh 142, kingston 100), so about 508 s free up around 19 Nov.

### Where the ~$20k charge came from

October's Pay-As-You-Go usage is billed in arrears in early November:

- Darkwave Disco, jobs created in October: **11,991 s** (1,095 jobs pulled, 7 with no usage, all cancelled or queued).
- Quaker in October: 643 − 220 (November) = **≈ 423 s**.
- **Total ≈ 12,414 s × $1.60 ≈ $19,860.** That matches the ~$20k charge.

The heaviest October days on Darkwave were:

| Day | Seconds |
|---|---|
| 24 Oct | 2,548 |
| 22 Oct | 1,794 |
| 23 Oct | 1,493 |
| 7 Oct | 1,477 |
| 21 Oct | 1,213 |
| 31 Oct | 738 |
| 4 Oct | 446 |

Most October seconds (8,321 of 14,567 overall) came from untagged sweep, ladder and Hahn jobs for the paper runs. The single largest job was 477 s on ibm_fez on 22 Oct (`dbcura0c77vs73873bo0`).

October seconds by backend (all months): kingston 4,622, fez 3,918, marrakesh 3,157, pittsburgh 1,463, phoenix 762, boston 521, chicago 124.

**November so far, already owed and billed next cycle:** Darkwave 2,576 s plus Quaker 220 s = **2,796 s ≈ $4,470**. The 7 to 9 Nov weekend alone used 540 s on Darkwave.

The daily November load is about 160 to 250 s per day, about $250 to $400 a day:

| Source | Seconds a day |
|---|---|
| qia_cal hourly calibration, US (4 s per processor) | ≈ 120 |
| qia_cal, EU | ≈ 24 |
| darkwave clock and table | ≈ 78 |
| one-off fires (3 Nov "carriers" / addendum1b 2 × 278 s, r121 162 s) | spikes on single days |

**Two jobs are still queued on Darkwave and will be charged when they run:** `dbperadt7fqc7389ai2g` (ibm_chicago, 10 Nov) and `dbn5ia44148s7390bve0` (ibm_boston, 6 Nov). Both are tagged qia-calibration.

### Jobs over the last 14 days per instance (charged seconds)

- **Darkwave Disco, 27 Oct to 10 Nov:**
  - About 470 jobs: 494 DONE, 3 ERROR, 1 CANCELLED, 2 QUEUED in the 21-day pull.
  - By day:

| Day | Seconds |
|---|---|
| 28 Oct | 120 |
| 29 Oct | 441 |
| 30 Oct | 252 |
| 31 Oct | 738 |
| 1 Nov | 254 |
| 2 Nov | 170 |
| 3 Nov | 996 |
| 4 Nov | 158 |
| 5 Nov | 206 |
| 6 Nov | 232 |
| 7 Nov | 212 |
| 8 Nov | 172 |
| 9 Nov | 156 |
| 10 Nov | 20 |

  - By tag (29 Oct onward): qia-calibration 1,540, untagged (darkwave clock and table) 1,066, carriers/addendum1b 556, kumar-abba 232, r121 162, qia-repeat-lums 86, nsweep 58, queue probes 30.
  - By backend (29 Oct onward): marrakesh 1,783, kingston 839, fez 368, pittsburgh 268, phoenix 238, chicago 124, boston 110.
- **Quaker:** 81 jobs since 24 Oct, all DONE, all ibm_aachen, 350 s (qia-calibration-eu 308). About 24 s a day.
- **open-instance:** no jobs in the last 14 days. The last ones were 19 jobs on 22 Oct.

## 3. Backends

| Backend | Family | Qubits | open-instance (free) | Darkwave (paid) | Quaker (paid) | Queue at read | Our coverage |
|---|---|---|---|---|---|---|---|
| ibm_fez | Heron r2 | 156 | yes | yes | | 8 | mirror; qia_cal; sweeps (not in the daily clock) |
| ibm_kingston | Heron r2 | 156 | yes | yes | | 4 | mirror; qia_cal; darkwave clock + table daily |
| ibm_marrakesh | Heron r2 | 156 | yes | yes | | 0 | mirror; qia_cal; darkwave clock + table daily |
| ibm_boston | Heron r3 | 156 | | yes | | ~650 | mirror; qia_cal |
| ibm_pittsburgh | Heron r3 | 156 | | yes | | 14 | mirror; qia_cal |
| ibm_phoenix | Nighthawk r2 | 120 | | yes | | ~1,020 | mirror; qia_cal |
| ibm_chicago | Nighthawk r2 | 120 | | yes | | ~1,080 | mirror since 5 Nov; qia_cal (32 jobs, 124 s) |
| ibm_aachen | Heron r3 | 156 | | | yes | 5 to 7 | mirror; qia_cal --eu |

- **Every reachable backend is already in the mirror and in qia_cal. None is fully uncalibrated.**
- ibm_chicago is the hardware that opened most recently: first mirror read 5 Nov, first jobs that week. It may be the "more hardware" the bill mentioned. It has the thinnest record and is **paid-only**.
- **On the free instance only fez, kingston and marrakesh are reachable.** Of those, only **ibm_fez** is missing from the darkwave daily clock and table.
- boston, pittsburgh, phoenix, chicago and aachen are reachable **only** through Pay-As-You-Go. Under a free-only rule we cannot fire on them. The mirror's free property reads keep covering them.

## 4. Recommendations (nothing below has been changed)

1. **Safe instance:** `open-instance` (CRN tail 864a532f, us-east, plan open) is the only one. Free seconds: **81 now**, about 508 more freeing up around 19 Nov (rolling 28 days, capped at 600).
2. **What 81 s buys:** about one darkwave clock calibration job C on **ibm_fez** (≈ 11 s), or one full clock on one chip (≈ 27 s), plus a table (≈ 12 s). That is the one uncovered free backend for the daily clock. Nothing else free is uncovered.
3. **Stop the paid riders first.** They bill on every tick until the floors:
   - In `watch/tick_bus.py`, the lines for `clock_daily.py`, `table_daily.py`, `qia_cal/cal.py --send` and `qia_cal/cal.py --send --eu`.
   - Or remove the gates `the_show/runs/2026-10-31-darkwave-clock/DAILY_ON` and `darkwave_daily/TABLE_ON`. cal.py has no gate file, so its tick-bus lines must be commented out.
   - Cancel the 2 queued Darkwave jobs (chicago `dbperadt7fqc7389ai2g`, boston `dbn5ia44148s7390bve0`) before they run.
4. **Repoint the defaults to the free CRN** before any rider comes back:
   - `sweep.py` line 16: `'Darkwave Disco'` → `'open-instance'`.
   - The US path in `cal.py` reads `.ibm_quantum_instance_crn`, which holds the Darkwave CRN.
   - The EU path has no free option at all, so EU stays off.
5. **Make paid billing impossible.** These are account settings for the owner to change in IBM Quantum Platform or IBM Cloud:
   - Set the usage limit of **Darkwave Disco** and **Quaker** to 0, or to their consumed seconds, or delete both Pay-As-You-Go instances.
   - Either way, both API keys (key_3 and parallax) are account-wide and reach the paid instances, so the safeguard has to be on the instance or the account, not in our scripts.
   - Deleting the instances or setting the limit to 0 does not cancel the ≈ $4,470 November usage already run.
6. **Open plan terms:** our records already note that the Open plan's terms on commercial use should be read before any paid engagement. Client and QIA work on the open instance should be checked against them.
7. **Memory conflict:** `~/.claude/projects/-Users-heuremen/memory/feedback-ibm-time-is-investment.md` says to default to Darkwave Disco and ask for cap raises. That now contradicts the free-only rule and should be retired or rewritten.
