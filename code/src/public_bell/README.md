# public_bell: raw data from landmark Bell tests (downloaded 2026-09-29)

Byline: Wayfinder & Bones. The report is `LATER_SORTS_PUBLIC.md`. Code is in `code/`, and numeric results are in `results/`.

## What is here

| folder | experiment | source | license / terms | size on disk |
|---|---|---|---|---|
| `weihs1998/` | Weihs et al., PRL 81, 5039 (1998), Innsbruck, 400 m, fast random switching | Zenodo, doi:10.5281/zenodo.7185335: `Alice.zip` (597,516,085 B, md5 1326b368d1ce9349f9e9c2a46f4e305d) and `Bob.zip` (483,185,117 B, md5 978a155e608aa3ed8885b9abf236c1ad), both md5-verified against Zenodo | CC-BY-4.0. The data page asks reusers to cite Weihs et al. 1998 and, if possible, to tell the lead author | 1.04 GB zipped + 1.45 GB unzipped |
| `nist2015/` | Shalm et al., PRL 115, 250402 (2015), NIST Boulder, loophole-free | NIST "Bell Test Research Software and Data" page (nist.gov/pml/applied-physics-division/bell-test-research-software-and-data). S3 bucket `nist-belltestdata/belldata/processed_compressed/hdf5/`. The format description is `file_folder_descriptions.pdf` | US-government work, not subject to US copyright, provided "as is". The NIST page asks for attribution | 8 HDF5 files, 10.5 GB |
| `delft2015/` | Hensen et al., Nature 526, 682 (2015), Delft, electron spins 1.3 km apart | 4TU.ResearchData, doi:10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31, `data.zip` (152,913 B, md5 342f29f8...) | 4TU General Terms of Use | 0.6 MB |
| `delft2016/` | Hensen et al., Sci. Rep. 6, 30289 (2016), second Delft run | 4TU, doi:10.4121/uuid:53644d31-d862-4f9f-9ad2-0b571874b829, `data.zip` (131,394 B, md5 de565fc8...) | 4TU General Terms of Use | 0.6 MB |
| `munich2017/` | Rosenfeld et al., PRL 119, 010402 (2017), Munich, atoms 398 m apart | Zenodo, doi:10.5281/zenodo.22936124. This deposit (Sept 2026) recovers the old bellexp.quantum.physik.uni-muenchen.de downloads. It holds two public runs, April 2016 and June 2016, 10,201 + 10,202 events | CC-BY-4.0 | 4 MB |
| `illinois2013/` | Christensen et al., PRL 111, 130406 (2013), Illinois, detection-loophole-free CH test | research.physics.illinois.edu/QI/BellTest/: `CH_Bell_Data.zip` (288,658,701 B) plus `data_organization.txt` | Public download, no license stated. The page asks for questions to go to B. Christensen | 0.58 GB |
| `papers/` | PDFs and extracted text of the published reanalyses read for the report | arXiv | Copyright of the authors, kept here only as reading copies | 33 MB |

## Format notes (the ones that bit)

- **Weihs `*_C.dat` bit order is the reverse of the Zenodo text.** The lowest bit is the switch (setting) and the next bit is the detector (outcome). With the bits read that way, the E(a,b) values match the group's own evaluation files `*_R.dat` to about 0.005 (for example longdist1: E00 = -0.788 vs -0.789). The Zenodo page itself says: "Somebody said that the bits must be reversed." They were right.
- Weihs `*_R.dat` "Window" is a half-width. Using ±3 ns gives 17,606 coincidences in longdist1 against their 17,639.
- Four Weihs files are unusable: longdist6, 7, 8 and 21. They have no coincidence peak within ±20 µs, no `_R.dat` evaluation, and longdist21's header says "Wrap Error". newlongtime0 is unusable for the same reason.
- Bob's longtime1 has 765 corrupt time tags (values around 1e79, or sign-flipped) near t = 256 s. They were dropped.
- Weihs time tags are not perfectly sorted (small negative steps of up to about 16 ns), so each file was re-sorted.
- NIST HDF5 files: `alice/settings` and `bob/settings` hold one value per 100 kHz trial (1 = setting 0, 2 = setting 1, rare 0 or 3 = invalid). `clicks` is a uint16 bitmask over the 16 laser pulses in the Pockels-cell window. `laserPulseNumber` and `phase` exist only in some files, have no trial index, and were not used. `badSyncInfo` is missing from some files.
- Illinois: each `.mat` file is 1 s with one fixed setting pair. The settings come from `randomdata`, a 65,536-bit list that is identical in every file: Alice = random(i), Bob = random(i+1). This was checked to match `asetting`/`bsetting` in all 4,450 files. The time bin is 156.25 ps. Trial = the ch15 trigger plus the hidden trigger halfway between. A click is a detection 8,000 to 26,000 bins after the trial starts.

## Checked and skipped

- **NIST raw time tags** (`rawdata_from_servers`, about 48 to 50 GB) and the `compressed` per-side time-tag zips (about 35 GB): skipped because they are over the ~20 GB limit. The processed HDF5 files already carry per-trial settings and per-pulse clicks.
- **NIST early runs** 00_44, 01_11, 02_54, 03_31 and 03_43 (the NIST notes describe them as having the wrong timing, RNG bias, or a laser that was not mode-locked): not downloaded. The eight runs used are the six runs from the paper plus the two "blind" runs (17_04 and 03_12).
- **Vienna 2015** (Giustina et al., PRL 115, 250401): no public raw data found, and the paper has no data statement. **Vienna 2013**: shared only with collaborators.
- **BIG Bell Test 2018** (Nature 557, 212): not public. Section IX of the paper says: "Experimental data are available upon reasonable request from the contact author of each experiment."
- **Cosmic Bell tests** (Handsteiner 2017, Rauch 2018): no public data found.
- **ETH 2023 superconducting test** (Storz et al., Nature 617, 265): "available from the corresponding authors upon reasonable request."
- **Larsson's `belltiming.tar.gz`** (10 s of Weihs data): host unreachable (DNS failure). The full Zenodo set replaces it.
- **CURBy / NIST randomness beacon**: not examined. It is a randomness service, not a landmark test.

## Code (`code/`)

- `bellsort.py`: stratified likelihood-ratio (G) test, plus an exact trial-shuffle null (hypergeometric draws that match the margins).
- `nist_tables.py`, `weihs_tables.py`, `delft_munich_tables.py`, `illinois.py`: per-dataset builders for the sort tables. All use a single process and stream NIST in 5 M-trial chunks. Peak memory is at most about 1.9 GB.
- `analyze_tables.py`: tests every table and pools across runs. `compile_family.py`: one p per sort, plus Bonferroni and Benjamini-Hochberg over all 448.
- `weihs_diag.py`, `weihs_diag2.py`: diagnostics (effect vs gap, and partner removal). `nist_lagprofile.py`: post-hoc lag scan for NIST.

Environment: `~/bones-forge/qvenv/bin/python`. `h5py` and `pypdf` were installed into it for this work.
