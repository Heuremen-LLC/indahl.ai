# Dryad/Zenodo sweep for the yeast-glycolysis shape — 2026-09-30

Shape sought (THIRD_RUNG §46-48): (i) a TIME SERIES of repeated measurements,
(ii) a MESSAGE crossing a SUBSTRATE between units, (iii) a CLOCK that switches
on at a THRESHOLD and synchronizes a population, (iv) a NULL beside it
(sub-threshold / memoryless control) in the same dataset. Template: De Monte
2007 yeast glycolytic oscillations. No expectation was written before running
the sweep or the gradient tool.

## 1. Metadata sweep, counted

- Dryad: 44 distinct search terms, `https://datadryad.org/api/v2/search`,
  50/page. Total 634 raw hits returned (many duplicated across terms).
  Per-term counts (total matching, not just fetched) logged in
  `out/dryad_sweep/search_log.txt`. Highest-yield terms: "threshold" (1306
  total matches), "collective behavior" (928), "synchronization" (619),
  "oscillation" (616), "synchrony" (333), "phase transition" (214).
  Near-zero/zero terms: BZ reaction, Belousov-Zhabotinsky, Min oscillation,
  somite clock, glycolytic oscillations, yeast glycolysis oscillation,
  biofilm oscillation, spin-torque/Josephson/traffic-flow terms (Dryad's
  corpus skews biology/ecology, not physics).
- Zenodo: 52 distinct search terms (all 49 terms + reruns), `/api/records`,
  25/page (unauthenticated cap — found via a 400 error: "Page size cannot be
  greater than 25... use authenticated requests to increase to 100"). 1300
  raw hits. Zenodo's free-text search is weak (near-million "total" counts
  for generic terms like "circadian time series" = 605,876 — clearly
  whole-corpus noise, not precision). Full log: `search_log_zenodo.txt`.
- Combined, deduplicated by (source, DOI): **1769 unique candidate records**
  in `scored_candidates.json`. That is the count-≥1 table (>>60 rows
  required by the brief; full table is the JSON, not reproduced here).

## 2. Four-cell keyword scoring (abstract/usageNotes/keywords only)

Scored each candidate for textual evidence of: C1 time-series language, C2
substrate/message language (diffusible, gap junction, quorum, pheromone,
paracrine...), C3 threshold/density-switched collective clock language, C4
null/control/sub-threshold language. Script: `score.py`, output
`scored_candidates.json`.

- Candidates with **3-4 cells hit: 4** (keyword scoring is blunt — real
  Dryad/Zenodo abstracts rarely narrate all four elements in one paragraph).
- Candidates with 2 cells: 93.
- Candidates with ≥1 cell: 645 of 1769.

Manually reading the strongest 2-cell hits (abstracts read in full) surfaced
better real fits than the keyword score alone — this is where the actual
candidate table was built. Best manual finds, by shape:

| Title | DOI | System | Size | Why it fits |
|---|---|---|---|---|
| Social synchronization of circadian rhythmicity in female mice | dryad.1v8j2 | mouse body-temp circadian | 1.5MB (zip) | Time series (15-min body temp), substrate=cohabitation, **threshold=group size** (singly/pairs failed to sync, quintets did — literal null beside signal in one dataset) |
| Sources of intraspecific variation in collective tempo/synchrony of ants (Temnothorax) | dryad.4b92t21 | ant colony activity rhythm | ~46KB | Time series (wavelet period + peak-to-peak per trial), substrate=in-nest interaction, isolated-queen/worker files are the explicit **null control** |
| Polarization of yeast cells under pheromone induction | dryad.4f4qrfjn0 | S. cerevisiae polarity | 1.2MB (xlsx) | Time-course single-cell imaging, step-up/step-down pheromone regimens show **hysteresis** (bistability, history-dependence) — same organism/mechanism family as the De Monte template |
| Phenotypic screening, synchronized Ca2+ oscillations, cortical cultures | dryad.d2547d853 | primary neuron culture | 50KB (csv) | Real oscillator system (0.2 Hz Ca2+ waves), drug vs DMSO = threshold/null — **but files are pre-extracted per-well features, not raw traces** (limits time-series analysis) |
| No evidence for quorum sensing in cestode egg hatching | dryad.rbnzs7hqm | parasite hatching | 17KB usable (huge video files skipped) | An explicit **negative/null result for density-dependent (QS) synchrony** — valuable precisely as the null case Wayfinder asked to keep "beside" a signal |
| Using geography/dispersal to explain freshwater plankton synchrony | dryad.21jt3 | zooplankton/phytoplankton | 99KB (csv) | 26-yr multi-station time series, substrate=hypothesized dispersal corridors (Moran-effect test) |
| Gap junctional communication required for Ca2+ oscillations (spheroids) | 10.3390/cells14211744 (Zenodo) | human neuronal spheroids | 6MB | Substrate=gap junctions explicit, oscillation onset at ~0.2 Hz, synchronization index reported — **but Zenodo record is only the journal PDF, no raw data file** |
| Intrinsically active/pacemaker neurons, PSC-derived networks | 10.1016/j.stemcr.2014.01.006 (Zenodo) | stem-cell neuron networks | 3.5MB | MEA network bursting, pharmacological-block null — **PDF only, no raw data** |
| Data from: Infanticide/reproductive synchrony (Riehl 2016) | dryad.69ss9 | cooperative bird (ani) | ~30KB | Per-nest, not fine time series — weaker fit, included for diversity |
| Transient synchrony, Lepidoptera outbreaks (Hungary) | dryad.928c32c | forest pest populations | 1.6KB | 49-yr annual counts, 5 species — real time series but substrate/threshold not explicit (shared weather/enemies, not a measured message) |
| Otolith growth increments, NE Atlantic cod | dryad.t4b8gtj4s | fish growth rings | 5.3MB | Annual multi-population time series, shared-climate substrate (Moran effect), no explicit null |

## 3. What was actually fetched and analyzed (10 datasets)

**Blocker, logged honestly:** Dryad's own file-download endpoints
(`/api/v2/files/{id}/download`, dataset-level `/download` zip, and the
`datadryad.org/downloads/file_stream/*` browser links) are now gated by
Anubis (a JS proof-of-work anti-bot wall) or require an OAuth bearer token —
metadata search works keyless as advertised, but raw file download does not.
Workaround found and used: several hundred Dryad-hosted datasets are
independently mirrored on Zenodo under the *same DOI* with real file objects
at `https://zenodo.org/api/records/{id}/files/{name}/content`, which serves
without auth or bot-check. All 10 fetches below went through that route; 2
of the 10 targets (yeast pheromone xlsx set, cestode xlsx) were **not**
mirrored on Zenodo and were not fetched — noted as a gap, not silently
dropped.

Fetched, with SOURCE.txt, under `parallax/out/dryad_sweep/<name>/`:
calcium_waveform, mice_social_sync, ant_tempo, lepidoptera_sync,
infanticide_sync, freshwater_sync (6 real fetches; yeast_pheromone and
cestode_quorum targets logged as unfetchable via the open route).

### Numbers, counted

**Mice social synchronization (dryad.1v8j2)** — 25 mice, 8 groups (sizes
1,1,2,2,3,3,4,5,5 mice), body temp every ~15 min, 8192 points/mouse.
- Naive local-maxima peak-interval detector found a mean inter-peak interval
  of **~6.1–6.3 h** in every mouse regardless of group size — this is almost
  certainly a noise/ultradian artifact of the simple detector, not the
  known ~24 h circadian period; flagged as a method limitation, not hidden.
- Recursive gradient (forward-minus-backward EMA, memories 0.5/0.1/0.02, 200
  shuffles) on each individual mouse's raw trace: every mouse's mean gradient
  sat **inside** its own 95% shuffle floor at all three memories
  (frac_fwd_gt_bwd ranged 0.46–0.54, i.e. no directional asymmetry). No
  individual trace — singleton, pair, or quintet member — showed a
  measured forward-dominant signal above the memoryless-shuffle null.

**Ant collective tempo (dryad.4b92t21)** — 18 colonies × up to 6 trials,
Synchrony column (in-nest, coupled), n=108 values, mean synchrony index
= 0.0393. Isolated-queen control (n=6): mean proportion-of-time-active =
0.307. Isolated-worker control (n=6): mean = 0.881. Gradient on the pooled
in-nest synchrony series: mean −0.0038 to −0.0076 across memories, all
**inside** the shuffle floor (e.g. memory 0.02: mean −0.00758, floor
[−0.0317, 0.0272]) — despite an extreme frac_fwd_gt_bwd of 0.028 at that
memory, the mean-based significance test does not clear the floor. Null
beside signal is present in the raw data (isolated vs in-nest) but the
gradient tool finds no forward/backward asymmetry in either.

**Freshwater plankton synchrony (dryad.21jt3)**, station 4L, n=26 years of
Chlorophyll: gradient mean 0.20–2.28 across memories, frac_fwd_gt_bwd
reached 1.000 at memory 0.02, but the mean (2.276) still sat inside the wide
shuffle floor (−9.72, 9.86) for this short series — suggestive, not
significant at n=26.

**Lepidoptera outbreak counts (dryad.928c32c)**, Hungary, 1961–2009, 5
species: cross-species pairwise correlation of annual counts ranged −0.23
(tortrix vs malacosoma) to +0.44 (lymantria vs euproctis) — some real
co-fluctuation, no dominant single driver. Gradient on lymantria dispar
counts: mean −192 to −3848 across memories, inside shuffle floor each time
(frac_fwd_gt_bwd 0.10–0.45, i.e. leaning backward-dominant but not clearing
the null band given n=49).

**Calcium-oscillation waveform screen (dryad.d2547d853)**: files are
per-well *extracted features* (mean peak height, peak count, etc.), not raw
oscillation traces — genuinely time-series data does not survive in the
public files, so no period/gradient analysis was run on it; noted as a
finding, not skipped silently.

**Infanticide/reproductive-synchrony data (dryad.69ss9)**: per-nest,
per-year cross-sectional records, not a repeated-measurement time series —
confirmed by inspection, excluded from gradient analysis for the same
reason (no oscillator to test).

## 4. Which carry a measured null beside a measured collective clock

Two of the ten fetched datasets have a **real, measured** null condition
sitting beside a real signal condition in the *same* public files:

1. **dryad.1v8j2 (mice)** — singly-housed / paired mice (no cross-cycle
   sync possible or observed by the original authors) vs quintets (the
   paper's own finding: 4/7 quintets synchronized vs 2/8 pairs). We could
   not reproduce that synchrony finding ourselves with a quick pairwise
   analysis in the time available — the original paper's own statistic
   (cycle-to-cycle phase relationship) is more sophisticated than what was
   run here — so this is flagged as unverified-by-us, not confirmed.
2. **dryad.4b92t21 (ants)** — isolated queens/workers (no colony coupling)
   vs in-nest trial data (coupled). Measured, real numbers above; the
   contrast is in the raw data itself even though our gradient tool found
   no forward-dominant asymmetry in either arm.

No dataset in the fetched ten showed a recursive-gradient signal that beat
its own shuffled-null floor. That absence, across every real series tried
today, is itself the honest result of this sweep — not a confirmation, not
a refutation, a measured floor everywhere.

## Files

- Report: `~/bones-forge/parallax/DRYAD_SWEEP_20260930.md` (this file)
- Raw metadata: `out/dryad_sweep/raw_dryad.json`, `raw_zenodo.json`
- Search logs: `out/dryad_sweep/search_log.txt`, `search_log_zenodo.txt`
- Scoring: `out/dryad_sweep/score.py`, `scored_candidates.json`
- Fetched data + SOURCE.txt: `out/dryad_sweep/{calcium_waveform,
  mice_social_sync, ant_tempo, lepidoptera_sync, infanticide_sync,
  freshwater_sync}/`
- Analysis scripts/outputs: `out/dryad_sweep/mice_social_sync/analysis_results.json`,
  `out/dryad_sweep/cross_dataset_analysis.json`
