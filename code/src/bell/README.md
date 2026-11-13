# Bell test raw data -- the holes, with the settings

Fetched 2026-09-26. Read-only, free, no sign-ups. Question: is what gets thrown away (or never clicks)
dependent on the setting chosen? Python env: `~/bones-forge/bell/venv` (numpy, scipy, h5py).

## What exists

| Lab | Paper | Public data | Got it? | Holes WITH settings? |
|---|---|---|---|---|
| Delft run 1 | Hensen et al., Nature 526, 682 (2015) | 4TU `doi:10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31` (153 KB zip) | yes, `raw/delft/` | YES, for candidate heralds |
| Delft run 2 | Hensen et al., Sci Rep 6, 30289 (2016) | 4TU `doi:10.4121/uuid:53644d31-d862-4f9f-9ad2-0b571874b829` (131 KB zip) | yes, `raw/delft2/` | YES, same format |
| NIST | Shalm et al., PRL 115, 250401 (2015) | S3 bucket `s3.amazonaws.com/nist-belltestdata/belldata/` (~85 GB total) | one run (03_43, 737 MB) + diagnostics, `raw/nist/` | YES, every trial |
| Vienna | Giustina et al., PRL 115, 250401 (2015) | none found. Paper only points to an arXiv ancillary supplement (aggregate counts). | no | unknown -- would have to ask the authors |
| Munich (bonus, 2017) | Rosenfeld et al., PRL 119, 010402 | Zenodo 22936124 (re-deposited 9/2026) | yes, `raw/munich/` | YES, per-lab attempts incl. excluded ones |

## Delft (raw/delft, raw/delft2)
- `bell_open_data.txt`: 4746 rows = every attempt that had ANY two-photon signature at the middle station C in a
  wide window (5415-5665 ns / 5665-5915 ns). The paper's filters then keep 245 (run 2: 3918 rows -> 300).
  Each row carries BOTH random setting bits (A, B), the readout clicks, and the filter inputs
  (herald click times/channels, excitation clicks, invalid markers). Column spec: `bell_open_data_header.ods`.
- So the discarded candidate heralds come WITH their settings. What is NOT in it: the ~billions of attempts with
  no herald signature at all (no settings are logged for those).
- Readout no-click is an outcome (x = -1), not a discard. Replication: k/n = 196/245 (matches paper).

## NIST (raw/nist)
- `03_43.build.hdf5` (run "afterfixingModeLocking", one of the three runs in the paper's Table S-I):
  `alice|bob/settings` (uint8, 1 = setting 0, 2 = setting 1, 3 = both fired: 2 trials), `alice|bob/clicks`
  (uint16 bitmask of 16 laser-pulse slots in the Pockels-cell window; 0 = no click), one entry per trial,
  107,109,596 trials. So every no-click trial is present with both settings. Also per-click timing (`phase`,
  `laserPulseNumber`) to redefine windows, `config/*` (click window offset/radius), `badSyncInfo`.
- The CH/Eberhard analysis uses ALL trials (no post-selection), so the "holes" here are no-click trials, not discards.
- Other runs (1.0-2.6 GB each) and raw time tags (`rawdata_from_servers`, `compressed`: records of channel,
  78.125 ps timetag, buffer#; ch0 click, ch2 RNG0, ch4 RNG1, ch5 GPS PPS, ch6 sync) are listed in
  `raw/nist/s3_sizes.txt`; descriptions in `raw/nist/File_Folder_Descriptions*.pdf`. Per-run 16-outcome tables
  for the no-signaling checks are in `raw/nist/diag/*.xlsx`.

## Munich (raw/munich) -- 2016 runs, not 2015
- `*_lab_1/2.csv`: every attempt per lab with setting, result, "excluded from evaluation" + reason
  (e.g. Maintenance); `*_pairs.csv`: the kept pairs.

## First profile (scripts `profile_*.py`, outputs `profile_*.out`)

**Delft run 1, kept vs discarded by (a,b):** 53/1090, 79/1118, 62/1140, 51/1153 (discard rate 0.954, 0.934, 0.948, 0.958).
chi2 = 7.81, dof 3, p = 0.050 -> NOT setting-dependent at p<0.01. Per filter: herald window p = 0.42,
excitation click p = 0.50, invalid marker p = 0.17. Marginals: A p = 0.16, B p = 0.47.

**Delft run 2:** 69/971, 69/871, 78/887, 84/889. chi2 = 3.23, p = 0.36 -> NOT at p<0.01.

**NIST 03_43, no-click trials (all 16 slots; the 3-slot grouping gives the same pattern):**
- No-click rate vs own local setting: YES, huge (A 0.99931 vs 0.99785, chi2 ~40,000). This is by design (Eberhard
  angles give different single rates per setting); it is the physics being measured, not a filter.
- Coincidence / both-silent rates vs (a,b): YES (that's the Bell signal: (1,1) coincidences 265 vs ~12,600).
- No-click rate vs the REMOTE setting (no-signaling), 4 tests per window: A|a=0 p = 0.22, A|a=1 p = 0.41,
  B|b=0 p = 0.017, B|b=1 p = 0.77. 3-slot window: 0.74, 0.59, 0.0098, 0.20. One of 8 dips just under 0.01
  (B's silence vs Alice's setting when B chose 0); 8 tests, so not significant after correction. Same cell both windows.

**Munich:** lab-1 exclusions vs setting: 7 vs 10 (p = 0.62); 166 vs 166 (p = 0.86). Lab 2 has no exclusions.
