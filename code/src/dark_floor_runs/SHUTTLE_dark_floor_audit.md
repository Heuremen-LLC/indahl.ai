# Dark-floor D metric — offline audit of the existing run data

**Scope:** recomputed from files already on disk — `~/bones-forge/dark_floor.py`, `~/bones-forge/dark_floor_runs/*.json`, the two run logs, and `~/bones-forge/gridsong/biblioteca.md` (for provenance and prior art only). No hardware was contacted. All statistics are computed from the stored `zz` values independently of `dark_floor.py`'s own `analyze()`.

**Provenance.** The quoted results do **not** appear in the JSONs or the run logs — the logs only print Marrakesh t = 0 (+0.00121) and Kingston t = 30 (+0.00832) separately. The combined figure is at `gridsong/biblioteca.md:6135`:

> "COMBINED t=30us (inverse-variance): D = +0.00758 +/- 0.00252, z = 3.01 vs 0, 95% CI [+0.0026, +0.0125] … Sign test over 16 pairs: 12 positive / 3 negative / 1 zero, one-sided p = 0.018."

**Prior art.** A brake-check dated ~19:15Z the same day (`biblioteca.md:6146-6152`) already records several points this audit reaches independently: fixed block order with bell always first ("uncontrolled too", and quantified — "a 2.7 % effective-T1 drift across pubs reproduces the whole 0.0076"); device-level N ≈ 2; the sign test being "the same evidence counted twice"; and corr(D, bell coh) = +0.30 / −0.25. Those are **not** new findings here and are credited below where they arise. What this audit adds is in the *Relationship to the brake check* section at the end.

---

## Headline

**1. Everything reproduces.** t = 0: +0.00121 ± 0.00244 ✅. The reported t = 30 figure is the **inverse-variance combination of the two chip means**, and it reproduces to five significant figures including the CI (+0.007580 ± 0.002520, z = 3.008, CI [+0.00264, +0.01252]). The sign test (12 / 3 / 1, one-sided exact binomial **p = 0.0176**) reproduces exactly. **There is no arithmetic error in the reported result.**

**2. But z = 3.01 is the highest of every defensible aggregation of these same 16 numbers, and it is the one most sensitive to a single chip's luck.**

| Aggregation | mean | SE | z |
|---|---|---|---|
| **cluster-level IV, empirical SEM** ← as reported | +0.00758 | 0.00252 | **3.01** |
| unweighted over all 16 pairs | +0.00685 | 0.00283 | 2.42 |
| **per-pair inverse-variance (shot-noise errors)** | +0.00713 | 0.00324 | **2.20** |
| cluster-level IV, shot-noise SE, excl. the dead pair 16-23 | +0.00765 | 0.00346 | 2.21 |
| cluster-level IV, shot-noise SE, all pairs | +0.00618 | 0.00405 | 1.53 |
| device as the unit (G = 2, 1 dof) | +0.00685 | 0.00146 | t = 4.68, **p = 0.13** |

**The honest central range is z ≈ 2.2 – 2.4, not 3.0.** The two estimators that use the *measurement* errors rather than the empirical scatter agree closely at **z ≈ 2.2**. The 1.53 at the bottom of the table should not be quoted either: it lets one effectively dead pair (Kingston 16-23, σ_D = 0.0511 ≈ 7.5× the effect) dominate Kingston's error, and per-pair IV weighting correctly down-weights that pair instead.

**Why the reported estimator sits highest.** It weights each chip by its **empirical** SEM. Kingston's empirical SEM (0.00291) is **2.67× tighter than its own shot-noise floor** (0.00777) — its eight pairs happened to land close together. That buys Kingston **75 % of the total weight** on a chip whose scatter is 0.37× its noise floor. Marrakesh alone gives z = 1.07; Kingston alone gives z = 2.85.

> **Caveat, stated symmetrically:** Kingston's χ² is 1.93 on 7 dof (p = 0.96). That is equally consistent with the Estimator's *stated* per-pair errors being too large, in which case the empirical SEM is the better choice and 3.01 stands. **These two readings cannot be distinguished from this dataset, because there is no replication anywhere in it.** That is the single most consequential gap.

**Supporting findings:**

| | |
|---|---|
| **Clustering** | Between-device variance component estimates to **zero** (ICC = −0.103); the chips agree (Welch p = 0.62). So clustering does not *inflate* the error bar. But with G = 2 that estimate carries 1 dof and is uninformative. Device-as-unit: **t = 4.68 on 1 dof, p = 0.134**, CI [−0.012, +0.025], contains zero. |
| **Shot noise** | Observed scatter is **at or below** the shot-noise floor in three of four subsets (0.62× pooled, 0.37× Kingston, 0.73× t = 0); Marrakesh t = 30 is **1.06×**, i.e. right at the floor. **No meaningful excess variance anywhere.** |
| **Time confound** | There is **no t = 0 Kingston run on disk.** t = 0 is Marrakesh-only. The clean paired contrast on the same 8 Marrakesh pairs: **Δ = +0.0042 ± 0.0049, t = 0.86, p = 0.42.** |
| **Circuit order** | Bell runs first in **24 / 24** pair-delay triples. Already on record (`biblioteca:6146`, quantified at `:6152`) and already addressed in the v2 design. |
| **Model premise** | Observed decay at 30 µs is 0.25–2.9× (median 1.5×) the pure-T1 prediction. The channel that guarantees D ≡ 0 is not the channel operating here. |
| **Correlations** | Nothing correlates with anything. 5 of 63 valid Pearson tests reach p < 0.05 where ~3.2 are expected by chance; none survives Bonferroni; none replicates on both chips. **Detuning and ZZ coupling cannot be tested at all** — never recorded. |

---

## Task 1 — Inventory and reconstruction

### What is on disk

| File | Mode | Backend | Job ID | Pairs | Delays | Shots | Circuits |
|---|---|---|---|---|---|---|---|
| `dark_floor_real_20260924_131028.json` | real | `ibm_marrakesh` | `daqlf73t55cs738rtfv0` | 8 | 0, 30 µs | 8192 | bell, null_a, null_b |
| `dark_floor_real_20260924_135201.json` | real | `ibm_kingston` | `daqljjqkqcdc73aau0n0` | 8 | **30 µs only** | 8192 | bell, null_a, null_b |
| `dark_floor_sim_20260924_125931.json` | sim | fake_kingston + fake_marrakesh | 2 UUIDs | 8 + 8 | 0, 30 µs | 8192 | 3-circuit, **different qubit pairs** (see flag 5) |
| `dark_floor_sim_20260924_125847.json` | sim | fake ×2 | 2 UUIDs | 8 + 8 | 0, 20, 60 µs | 8192 | 2-circuit (older design) |
| `dark_floor_sim_20260924_125811.json` | sim | fake ×2 | 2 UUIDs | 6 + 6 | 0, 20, 60 µs | 4096 | 2-circuit (older design) |

**Out of scope —** two files appeared at 14:20, after this audit's data pull: `dark_floor_v2_sim_fake_kingston_20260924_142017.json` and `…_142058.json`. Different protocol (flat schema, no `chips` key; 10 pairs; 13-value θ sweep; XY/YX observables; **`order` fully counterbalanced, 70 `bell_first` / 70 `bell_last`**), simulation-only, fake_kingston only. Excluded from everything below.

**Per-row stored:** `a`, `b`, `t_us`, `kind`, `zz`, `xx`, `yy`, `gap`, `coh`, `gap_std`.
**Per-pair calibration:** `cz_err`, `T1a`, `T1b`, `roa`, `rob`. **Per-chip:** `backend`, `job_id`. **Per-record:** `mode`, `started`, `delays_us`, `shots`.

Physical qubits — Marrakesh: 1-2, 149-150, 141-142, 121-122, 133-134, 47-48, 151-152, 64-65. Kingston: 16-23, 31-32, 114-115, 129-130, 6-7, 76-81, 102-103, 144-145.

### What is NOT stored

> **Only readout-mitigated expectation values are kept. There are no raw counts anywhere.**

- **Raw counts / per-shot bitstrings** — gone. (Partially reverse-engineerable in some cells; see flag 2. Not a substitute for a record.)
- **T2** — computed in `pair_table()` (line 66), used only as a filter (line 73), **discarded before writing** (line 75).
- **Qubit frequencies** — never read. **Pair detuning |f_a − f_b| cannot be computed from these files.**
- **ZZ coupling / crosstalk** — never read.
- **Single-qubit (sx/x) gate errors** — never read.
- **Per-job or per-pub execution timestamps, queue times** — `job.metrics()` never called. `record["started"]` is `datetime.now()` at record creation (line 128), *before* submission.
- **Backend calibration snapshot timestamp / `last_update_date` / version** — not captured, so there is no way to check whether the two chips' calibrations were the same age.
- **TREX mitigation metadata** — discarded.
- **Realized delay duration** (dt granularity as scheduled) — not captured.
- **Any within-pair replication** — each pair/delay/kind measured exactly once. **Zero replication in the dataset.**

### Reproduction

`D = (1 − gap_bell) − mean(1 − gap_null_a, 1 − gap_null_b)`, `gap ≡ −zz`.

| Set | n | mean D | sd | SEM | z | pos / neg / zero |
|---|---|---|---|---|---|---|
| **t = 0, all real** (= Marrakesh only) | 8 | **+0.00121** | 0.00691 | **0.00244** | +0.50 | 5 / 3 / 0 |
| t = 30, all 16 pairs, unweighted | 16 | +0.00685 | 0.01132 | 0.00283 | +2.42 | **12 / 3 / 1** |
| t = 30, Marrakesh only | 8 | +0.00539 | 0.01421 | 0.00502 | **+1.07** | 6 / 2 / 0 |
| t = 30, Kingston only | 8 | +0.00832 | 0.00824 | 0.00291 | **+2.85** | 6 / 1 / 1 |
| **t = 30, cluster-level IV** (as reported) | 16 | **+0.00758** | — | **0.00252** | **+3.01** | — |
| t = 30, per-pair IV weighted | 16 | +0.00713 | — | 0.00324 | +2.20 | — |

```
marrakesh  +0.005388 ± 0.005023   (weight 25 %)
kingston   +0.008317 ± 0.002913   (weight 75 %)
IV         +0.007580 ± 0.002520    z = 3.008    95 % CI [+0.00264, +0.01252]
reported   +0.00758  ± 0.00252     z = 3.01     95 % CI [+0.0026,  +0.0125 ]
```

The sign test (p = 0.0176) reproduces, but it is **not independent corroboration** — it is the same 16 numbers as the mean, re-counted. The brake check already makes this point (`biblioteca:6148`).

---

## Task 5 — Shot-noise floor

σ_D = √(σ²_bell + ¼σ²_null_a + ¼σ²_null_b), from the Estimator's own standard errors:

| Set | observed sd | rms shot-noise σ_D | ratio | χ² about the mean | p | excess variance |
|---|---|---|---|---|---|---|
| t = 30 pooled | 0.01132 | 0.01820 | 0.62× | 11.82 / 15 dof | 0.69 | −2.0 × 10⁻⁴ |
| t = 30 Marrakesh | 0.01421 | 0.01341 | **1.06×** | 9.09 / 7 dof | 0.25 | **+2.2 × 10⁻⁵** |
| **t = 30 Kingston** | **0.00824** | **0.02197** | **0.37×** | 1.93 / 7 dof | 0.96 | −4.2 × 10⁻⁴ |
| t = 0 Marrakesh | 0.00691 | 0.00950 | 0.73× | 5.95 / 7 dof | 0.55 | −4.3 × 10⁻⁵ |

**Answer to the question as posed: the scatter does not exceed shot noise.** It is below the floor in three subsets and 1.06× (i.e. right at it) on Marrakesh t = 30. Excess variance is negative in three of four. **There is no variance anomaly to explain.**

### Why this matters for the reported z, and where the argument stops

The cluster-level IV estimator weights each chip by 1/SEM² using the *empirical* SEM:

| Weighting | Marrakesh share | Kingston share | combined | z |
|---|---|---|---|---|
| **empirical SEM** (as reported) | 25 % | **75 %** | +0.00758 ± 0.00252 | **3.01** |
| shot-noise SE, all pairs | **73 %** | 27 % | +0.00618 ± 0.00405 | 1.53 |
| **shot-noise SE, excl. dead pair 16-23** | 53 % | 47 % | +0.00765 ± 0.00346 | **2.21** |

Kingston's low empirical scatter is what earns it three-quarters of the weight. **But the shot-noise route is not clean either:** Kingston's rms σ_D = 0.0220 is dominated entirely by pair **16-23**, whose circuits are essentially flat (bell gap 0.088, null_a 0.078, null_b 0.089 — **all three** equally dead) and whose σ_D = 0.0511; the median of Kingston's other seven is 0.0131. Remove 16-23 and Kingston's shot-noise SE drops from 0.0078 to 0.0051, the weight inversion largely evaporates, and z returns to **2.21** — the same value per-pair inverse-variance weighting gives (2.20), which handles the dead pair correctly without an ad-hoc cut.

**So: z ≈ 2.2 is the number that survives.** 3.01 requires trusting the empirical SEM over the measurement errors on eight unreplicated points; 1.53 requires letting one dead pair set a chip's weight. Neither extreme is defensible; both are reachable from these same 16 numbers, which is itself the finding.

Only **6 of 16** pairs at t = 30 (and 2 of 8 at t = 0) have |D| larger than their own 1σ.

---

## Task 3 — Device clustering

| | n | mean D | sd | SEM | z |
|---|---|---|---|---|---|
| `ibm_marrakesh`, t = 30 | 8 | +0.00539 | 0.01421 | 0.00502 | **+1.07** |
| `ibm_kingston`, t = 30 | 8 | +0.00832 | 0.00824 | 0.00291 | **+2.85** |

**Do the chips agree?** Yes — Welch **t = −0.504, p = 0.624**. (Also on record at `biblioteca:6148`.)

**Variance components** (one-way random effects, G = 2, m = 8): MSB = 3.43 × 10⁻⁵, MSW = 1.35 × 10⁻⁴, between-device component = **−1.26 × 10⁻⁵**, **ICC = −0.103**, design effect 1.00, **effective n = 16** (ICC clipped at 0).

**Clustering does not inflate the error bar in this dataset** — the chips agree better than independent sampling would predict. That is worth stating plainly, and it means the naive pooled z = 2.42 is not an artifact of treating 16 correlated pairs as independent. But it is not reassurance: with G = 2 the between-device variance is estimated from **one degree of freedom** and cannot exclude a device-level common-mode offset the size of the effect.

Device as the unit of analysis:

> mean of chip means = +0.00685, cluster SE = 0.00146, **t = 4.68 on 1 dof → p = 0.134**, 95 % CI (t\* = 12.706) = **[−0.0118, +0.0255] — contains zero.**

**Plain statement:** the significance does not survive at 3σ, but *not* because clustering inflates the SE. It fails because (a) the 3.01 depends on empirical-SEM weighting of eight unreplicated points per chip, and (b) with two devices there is no way to establish a device-independent effect at all.

---

## Task 4 — Time, job and order structure

**Job composition.** `build_pubs()` assembles every pub for a chip into one list and `run()` submits it in a single `est.run(pubs)` call:

- `ibm_marrakesh` → job `daqlf73t55cs738rtfv0`, **48 pubs** (8 pairs × 2 delays × 3 kinds).
- `ibm_kingston` → job `daqljjqkqcdc73aau0n0`, **24 pubs** (8 pairs × 1 delay × 3 kinds).

**All three circuits for a given pair ran in the same job.** Order is pair-major → delay → kind, `KINDS = (bell, null_b, null_a)`. Pair *i* occupies pubs 6*i* … 6*i*+5 on Marrakesh, 3*i* … 3*i*+2 on Kingston.

> ✅ The three circuits forming one D are *consecutive* pubs, so drift between pairs is largely differenced out within a pair.
>
> 🚩 **Bell is first in all 24 triples** — no reversed arm, no interleaving, no randomisation, so any monotone within-triple positional effect maps into D with a fixed sign. **Already on record** (`biblioteca:6146`) and already quantified there (`:6152`: "bell always first = coldest TLS bath; a 2.7 % effective-T1 drift across pubs reproduces the whole 0.0076"). The v2 files on disk already counterbalance this 70/70. Confirmed here, not discovered here.

**Timestamps: essentially absent.** `job.metrics()` is never called — no per-pub timings, no queue times, no execution start/stop. The only timing on disk:

- Marrakesh record created 17:02:19 UTC; file written 13:10:28 local (~8 min end-to-end).
- Kingston record created 17:11:42 UTC; file written 13:52:01 local (~40 min, almost all queue).
- **Submissions are 9 min 23 s apart.** The gap between *executions* is unknown. (Two separate jobs, not a Runtime `Session`.)

**Drift test — D vs position in the run sequence:**

| Set | Pearson r | p | Spearman ρ | p | lag-1 autocorr |
|---|---|---|---|---|---|
| Marrakesh t = 30 | −0.261 | 0.53 | −0.238 | 0.57 | **−0.718** |
| Kingston t = 30 | −0.062 | 0.88 | −0.119 | 0.78 | +0.205 |
| Marrakesh t = 0 | −0.327 | 0.43 | −0.238 | 0.57 | −0.235 |
| Pooled, true pub index | −0.252 | 0.35 | — | — | — |
| Pooled, pair index within chip | −0.180 | 0.50 | — | — | — |

**No monotone trend across the session in any subset** — so *between-pair* calibration drift being absorbed into D is not supported. Note this does **not** test the within-triple order effect above, which is invisible to a between-pair trend test. And with n = 8 per chip the power is almost nil either way.

**Time-adjacency (quasiparticle bursts):** lag-1 autocorrelation is **−0.718 on Marrakesh** (*alternating* — the opposite of a time-correlated disturbance) and **+0.205 on Kingston**. Opposite signs, neither distinguishable from noise at n = 8. **No evidence of a device-wide time-correlated disturbance, and no power to exclude one.**

**The one clean time contrast.** t = 0 exists **only** on Marrakesh:

> **D(30 µs) − D(0 µs) = +0.00418 ± 0.00488, t = 0.86, p = 0.42.**
> Per-pair, by qubit index (1-2, 47-48, 64-65, 121-122, 133-134, 141-142, 149-150, 151-152): +0.0117, +0.0190, +0.0159, +0.0125, −0.0173, −0.0016, +0.0078, −0.0145.

**The "D grows with idle time" claim rests on a comparison in which the delay and the chip change together.** t = 0 is Marrakesh (z = 0.50); t = 30 is dominated by Kingston (75 % of the weight), which has no t = 0 measurement at all. De-confounded to within-Marrakesh, p = 0.42.

---

## Task 2 — Per-pair correlation scan

### Properties available vs missing

| Requested | Available? |
|---|---|
| T1_a, T1_b, mean T1, \|T1_a − T1_b\| | ✅ stored |
| Readout assignment error, each qubit | ✅ stored (`roa`, `rob`) |
| Two-qubit (CZ) gate error | ✅ stored (`cz_err`) |
| Physical qubit index | ✅ stored |
| Coherence `coh` = −(⟨XX⟩+⟨YY⟩)/2 | ✅ stored per row (not a device property, but the most physically informative stored quantity) |
| **T2_a, T2_b** | ❌ computed then discarded |
| **Qubit frequencies → detuning \|f_a − f_b\|** | ❌ never read — **the exchange-coupling hypothesis cannot be tested from this data at all** |
| **ZZ coupling** | ❌ never read |
| **Single-qubit gate errors** | ❌ never read |

### t = 30, pooled (n = 16, both chips)

The **13 device/derived properties** below constitute the pre-planned scan (16 properties × 4 subsets = 64 cells, 63 valid; `min qubit index` duplicates `qubit index a` exactly and is not shown). The last three rows — `coh`, `|coh|`, `pub position` — are **additional diagnostics outside that scan** and are excluded from the multiplicity count.

| Property | Pearson r | 95 % CI | p | Spearman ρ | p |
|---|---|---|---|---|---|
| **T1_a** | **−0.589** | [−0.839, −0.131] | **0.016** | −0.394 | 0.131 |
| T1_b | +0.038 | [−0.466, +0.524] | 0.889 | +0.159 | 0.557 |
| mean T1 | −0.435 | [−0.766, +0.077] | 0.092 | −0.356 | 0.176 |
| **\|T1_a − T1_b\|** | **−0.036** | [−0.523, +0.468] | **0.894** | +0.141 | 0.602 |
| readout err a | +0.305 | [−0.225, +0.696] | 0.251 | +0.135 | 0.617 |
| readout err b | +0.232 | [−0.298, +0.653] | 0.387 | +0.215 | 0.424 |
| mean readout err | +0.445 | [−0.065, +0.771] | 0.084 | +0.379 | 0.147 |
| \|Δ readout\| | +0.352 | [−0.174, +0.722] | 0.181 | +0.344 | 0.192 |
| CZ two-qubit error | −0.324 | [−0.706, +0.205] | 0.221 | −0.238 | 0.374 |
| qubit index a | −0.320 | [−0.704, +0.208] | 0.226 | −0.362 | 0.169 |
| qubit index b | −0.329 | [−0.709, +0.200] | 0.214 | −0.362 | 0.169 |
| predicted null asym \|2p_a − 2p_b\| | +0.334 | [−0.194, +0.712] | 0.207 | +0.212 | 0.431 |
| observed null asym \|gap_a − gap_b\| | −0.096 | [−0.565, +0.419] | 0.722 | −0.009 | 0.974 |
| bell gap remaining | +0.007 | [−0.490, +0.501] | 0.978 | +0.129 | 0.633 |
| shot-noise σ_D | −0.259 | [−0.669, +0.272] | 0.334 | −0.135 | 0.617 |
| *bell coherence `coh`* (diagnostic) | +0.303 | [−0.228, +0.695] | 0.254 | — | — |
| *\|bell coherence\|* (diagnostic) | −0.253 | [−0.665, +0.278] | 0.345 | — | — |
| *pub position within job* (diagnostic) | −0.252 | [−0.666, +0.279] | 0.346 | — | — |

The coherence numbers match the brake check's own (+0.30 / −0.25, `biblioteca:6153`). Per-chip and t = 0 tables are in `analysis_full.txt`.

### Read of the scan

At n = 16, |r| must exceed **0.497** to reach p = 0.05 (n = 8: **0.707**). **Every CI in the table is about 1.0 wide** — this scan cannot distinguish "no relationship" from "a strong relationship" for most properties.

- **Differential decay (|T1_a − T1_b|):** **r = −0.036, CI [−0.52, +0.47], p = 0.89.** No signature. Note the trap: at **t = 0** the same property gives **r = +0.803, p = 0.016 (n = 8)** — but at zero idle there is no decay to differentiate. A textbook spurious correlation, and a direct calibration of how much noise n = 8 generates. The property that "works" at t = 0 is flat at t = 30.
- **Exchange coupling (detuning):** **untestable.** Frequencies were never recorded. No weight should be assigned in either direction.
- **Measurement artifact (readout error):** mean readout error r = +0.445, CI [−0.065, +0.771], p = 0.084. Largest of the three named candidates and correctly signed, but not significant and does not replicate (Marrakesh +0.512, Kingston +0.200).

**Strongest single hit is T1_a** — pooled r = −0.589, CI [−0.839, −0.131] (excludes zero), p = 0.016; Marrakesh r = −0.770, p = 0.025 — with T1_**b** showing nothing (r = +0.038). **But Kingston gives r = −0.053, p = 0.90.** No replication, no survival of multiplicity.

**Multiplicity:** 63 valid tests; expected at p < 0.05 by chance ≈ **3.15**; **observed 5**. Bonferroni within one subset (16 tests) is p < 0.0031; across all 63 it is p < 0.00079. **The smallest p anywhere is 0.016.** Nothing comes close to either threshold.

> **"Nothing correlates with anything" is the honest result — but at n = 16 that is a statement about the experiment's power, not about the device.**

---

## Task 6 — Sign and magnitude sanity

**Internal consistency:** `gap == −zz` and `coh == −(xx + yy)/2` hold float-exactly in all **72 rows** (144 identity checks). ✅

**Convention verified analytically** (2-qubit density matrices, Kraus amplitude damping):

| p_a, p_b | bell gap / deficit | null_a gap / deficit | null_b gap / deficit | D |
|---|---|---|---|---|
| 0.00, 0.00 | +1.0000 / 0.0000 | +1.0000 / 0.0000 | +1.0000 / 0.0000 | 2 × 10⁻¹⁶ |
| 0.20, 0.09 | +0.7100 / 0.2900 | +0.6000 / 0.4000 | +0.8200 / 0.1800 | 3 × 10⁻¹⁶ |
| 0.40, 0.05 | +0.5500 / 0.4500 | +0.2000 / 0.8000 | +0.9000 / 0.1000 | 1 × 10⁻¹⁶ |

**Confirmed:** gap = −⟨ZZ⟩ = +1 ideally for all three circuits; bell deficit = mean null deficit = p_a + p_b; **D ≡ 0** under independent amplitude damping. **A positive D means the bell circuit lost MORE gap than the averaged nulls.** The convention is correct throughout; there is no sign inversion anywhere in the pipeline.

> **Caveat:** verified from the *stored expectation values* and from theory. It **cannot** be verified against a stored counts record, because none exists.

---

## Data-quality flags

### 🚩 1. 16 of 216 stored expectation values lie outside [−1, +1]

All 16 on `ibm_marrakesh`; **5 of 24** pair × delay cells have |⟨ZZ⟩| > 1. Largest by magnitude:

| Pair | t | Circuit | Observable | value |
|---|---|---|---|---|
| 141-142 | 0 | bell | ⟨XX⟩ | **−1.3796** |
| 141-142 | 0 | null_b | ⟨ZZ⟩ | **−1.3179** |
| 141-142 | 0 | bell | ⟨ZZ⟩ | **−1.3106** |
| 141-142 | 0 | bell | ⟨YY⟩ | −1.3102 |
| 141-142 | 0 | null_a | ⟨ZZ⟩ | −1.3095 |
| 141-142 | 30 | null_a | ⟨ZZ⟩ | −1.0610 |
| 133-134 | 0 | null_b | ⟨ZZ⟩ | −1.0492 |
| 1-2 | 0 | null_b | ⟨ZZ⟩ | −1.0472 |

TREX rescaling (`resilience_level = 1`) pushes point estimates past the physical bound. For 141-142 at t = 0 the "deficit" is **−0.31** — the circuit reported as having *more* than perfect signal. For those pairs D is a difference between two out-of-range numbers.

### ⚠️ 2. Kingston 102-103's exact zero is a shot-noise coincidence, not a pipeline artifact

D is bit-exactly 0.0 in float64, which looks alarming. It is not. TREX for ⟨ZZ⟩ on a pair depends only on those two qubits' readout calibration, so **all three circuits share one mitigation factor**. Inverting it recovers integer counts over 8192 shots:

```
common γ = 0.917419   (naive (1−2e_a)(1−2e_b) from stored readout errors = 0.917817 — 0.04 % match)
k_bell = −2794,  k_null_a = −5726,  k_null_b = +138
(−5726 + 138)/2 = −2794   ← exact integer midpoint
```

The count-space difference has sd ≈ 200 with step 2, so an exact midpoint hit has probability ≈ **1 in 255 per cell**, ≈ **0.10 expected across the ~20 cells where the inversion is computable**. A mild coincidence, nothing more. **No pipeline defect is indicated.** (This inversion works cleanly in about **8 of 24** cells — enough to demonstrate the mechanism, not enough to substitute for storing counts.)

### 🚩 3. The pure-T1 model does not describe the t = 30 data

Observed / predicted bell deficit: **median 1.48×, range 0.25× – 2.93×**.

| Pair | T1_a | T1_b | predicted | observed bell | ratio |
|---|---|---|---|---|---|
| kingston 16-23 | 165.7 | 189.9 | 0.3117 | 0.9117 | **2.93** |
| marrakesh 151-152 | 197.7 | 307.2 | 0.2338 | 0.6616 | **2.83** |
| marrakesh 47-48 | 195.6 | 223.7 | 0.2677 | 0.7149 | 2.67 |
| kingston 102-103 | 197.8 | 271.1 | 0.2455 | 0.6282 | 2.56 |
| … | | | | | |
| kingston 114-115 | 214.4 | 286.8 | 0.2299 | 0.1734 | 0.75 |
| marrakesh 141-142 | 299.1 | 151.0 | 0.2756 | 0.0687 | **0.25** |

**The "D should be identically zero" argument is conditioned on independent amplitude damping with p = 1 − exp(−t/T1).** At 30 µs this data loses up to 3× what that channel predicts, and one pair loses 4× *less*.

### 🚩 4. The two nulls diverge by up to 0.78 in gap

| Pair | gap_null_a | gap_null_b | \|difference\| | D |
|---|---|---|---|---|
| kingston 102-103 | +0.7619 | **−0.0184** | **0.7803** | +0.00000 |
| marrakesh 47-48 | **−0.0503** | +0.6478 | 0.6981 | +0.01367 |
| marrakesh 121-122 | +0.4569 | **−0.1000** | 0.5568 | +0.02526 |
| marrakesh 151-152 | +0.5757 | +0.0796 | 0.4961 | −0.01073 |

Median |gap_a − gap_b| at t = 30 is **0.138** — about **13×** the median |D| of 0.0107. Three cells have a *negative* null gap. Some asymmetry is expected (2p_a vs 2p_b), but D is a ~0.007 residual riding on the midpoint of two numbers routinely half a unit apart, and that midpoint is the right reference only if the channel is linear in exactly the way flag 3 shows it is not.

### ⚠️ 5. The "simulated control" is not a matched control

`dark_floor_sim_20260924_125931.json` uses the same protocol but **different qubit pairs**: **0 of 8** overlap with the real Marrakesh set, **1 of 8** (129-130) with the real Kingston set. Any per-chip comparison below is across disjoint qubits and should be read as "same protocol on the same chip model", not "same experiment without the physics".

| Set | n | mean D | SEM | z |
|---|---|---|---|---|
| sim t = 0 pooled | 16 | −0.00090 | 0.00103 | −0.88 |
| sim t = 30 pooled | 16 | +0.00181 | 0.00193 | **+0.94** |
| sim t = 30, fake_marrakesh | 8 | +0.00462 | 0.00316 | +1.46 |
| sim t = 30, fake_kingston | 8 | **−0.00101** | 0.00193 | −0.52 |

Read honestly: the pooled sim t = 30 is **not distinguishable from zero** (z = 0.94), so this is **not** a demonstration that noise alone produces the effect. The fake_marrakesh model gives +0.00462 against real Marrakesh's +0.00539 (real/sim = 1.17), while **fake_kingston is negative** and real Kingston is the chip driving the real result. On different qubits, with no TREX (`resilience_level = 1` is set only under `if mode == "real"`, line 134-135), this comparison is **suggestive at best and cannot settle anything either way.**

---

## What the existing data supports

1. **The reported arithmetic is correct.** t = 0 null and t = 30 (+0.00758 ± 0.00252, z = 3.01, sign test p = 0.018) both reproduce exactly.
2. **z = 3.01 is the top of a 1.5 – 3.0 range reachable from these same 16 numbers.** The estimators that use measurement errors rather than empirical scatter converge on **z ≈ 2.2**; the unweighted mean is 2.42.
3. **The 3.01 depends on Kingston's empirical SEM being 2.67× tighter than its own shot-noise floor,** on 8 unreplicated points. Whether that reflects luck or conservative Estimator errors **cannot be determined without replication**, which the dataset has none of.
4. **Marrakesh alone gives z = 1.07; Kingston alone gives z = 2.85; device-as-unit gives p = 0.13.** No device-independent effect is established.
5. **There is no excess variance.** Scatter is at or below pure shot noise in three of four subsets and 1.06× in the fourth.
6. **The time dependence is confounded with device.** There is no Kingston t = 0. De-confounded within Marrakesh: p = 0.42.
7. **No stored device property correlates with D.** Detuning and ZZ coupling cannot be tested at all.
8. **The amplitude-damping premise that makes D ≡ 0 is not satisfied** by the t = 30 data.

## Relationship to the existing brake check (`biblioteca:6146-6153`)

**Already on record there, confirmed here:** fixed block order with bell always first; device-level N ≈ 2 and the two chips agreeing; the sign test being the same evidence counted twice; corr(D, coh) = +0.30 / −0.25.

**What this audit adds:**
- The **weight-inversion mechanism** — the specific reason z = 3.01 rather than ≈ 2.2, traced to Kingston's empirical SEM sitting 2.67× inside its own shot-noise floor, and the demonstration that the shot-noise-weighted alternative is itself distorted by one dead pair.
- The **shot-noise floor comparison per subset** (ratios, χ², excess variance) establishing there is no variance anomaly.
- The **t = 0 / device confound** — no Kingston t = 0 exists, so the time claim rests on a comparison where delay and chip change together; de-confounded p = 0.42.
- The **full correlation scan** with CIs, multiplicity bookkeeping, and the explicit finding that detuning and ZZ coupling are untestable from these files.
- **16 of 216 out-of-range mitigated values** and the T1-model failure (0.25–2.9×).
- **Resolution of the exact-zero** as benign, with the TREX inversion that recovers counts.

## What it would take to settle it

- **Replicate each pair** (interleaved repeats within a session). This is the gap that makes the central question — is Kingston's tight scatter luck or are the stated errors conservative? — currently unanswerable, and it is what turns a fragile 3σ into a real one or kills it.
- **Run t = 0 and t = 30 on both chips in the same job.** Removes the confound currently carrying the time claim.
- **Store raw counts** (or run `resilience_level = 0` alongside) so ⟨ZZ⟩ can be audited and the out-of-range estimates diagnosed directly rather than reverse-engineered in a third of cells.
- **Store the full calibration snapshot at run time**: T2, frequencies, anharmonicities, 1q errors, ZZ terms, calibration timestamp. Two missing fields make three of the requested correlations untestable.
- **Call `job.metrics()`** and store per-pub timing, so drift and time-adjacency can be tested rather than assumed.
- **Match the simulated control to the real qubit pairs**, and run it with TREX on, so it is actually a control.
- **n = 16 is far too small** for the correlation scan: power to detect |r| = 0.4 is ~33 %, and |r| must exceed 0.497 to register at all.

*(Circuit-order counterbalancing is already implemented in the v2 files on disk, 70 `bell_first` / 70 `bell_last`.)*

---

### Files

| File | Contents |
|---|---|
| `dark_floor_audit_report.md` | this report |
| `01_correlation_grid_t30.png` | D vs all stored/derived properties, t = 30, both chips |
| `02_per_pair_forest.png` | per-pair D with shot-noise error bars, t = 0 and t = 30 |
| `03_shot_noise_and_error_bars.png` | scatter vs shot-noise floor; the weight inversion; five aggregations |
| `04_clustering_and_time.png` | per-device D, run-order structure, paired time contrast |
| `05_data_quality_and_sim.png` | out-of-range values, T1-model failure, simulated control |
| `analysis_full.txt` | full numeric output including per-chip and t = 0 correlation tables |
| `reconstruction_log.txt` | row-by-row reconstruction of D from stored `zz` |
| `integrity_checks.txt` | sign verification, out-of-range audit, exact-zero forensics |
| `per_pair_data.json` | every reconstructed per-pair record used above |

*Superseded in the supporting files: `integrity_checks.txt` frames the Kingston 102-103 exact zero as a "1 in 2⁵²" event. That was wrong — see flag 2 (≈1 in 255 per cell). The rest of that file stands.*
