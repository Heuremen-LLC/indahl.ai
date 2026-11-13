# What goes to arXiv (measurement paper, 5 October 2026 build)

**The measurement paper, not Seven.** `make_measurement_paper.py` -> `MEASUREMENT_PAPER_20261004.md` -> `build_measurement_tex.py` -> `measurement/main.pdf` -> `~/Desktop/MEASUREMENT_PAPER_draft.pdf` (46 pages: 26 of paper, 20 of Appendix A).
Byline: Wayfinder and Bones. Disclosure: "This work was done with AI assistance." Wayfinder submits it from his own account.
Seven stays on the site (heuremen.org/7.pdf, the trail); the paper points to it once, as the source of the called numbers.

## How the paper answers the first questions a referee asks
- **"Did you fit the constants after the fact?"** Section 3.7 lists every number written and hashed before its data (sha256, time written, time the data first existed on the vendor's record, called, read, the call's own criterion, misses included): 21 calls read -- 4 land, 2 on the edge of their own width, 2 partly hold, 1 lands only with the readout models' own spread counted, 11 miss, 1 unreadable. Beside it, the stone test: how much of the number line the framework's 24 ratios cover (35 % within 2 % between 0.5 and 2), and the chance a single named number is hit (4.3 % at +-3 %). No after-the-fact match is named anywhere in the paper. Script: `code_20261004/stone_density.py`.
- **"What else did you run that isn't shown?"** Appendix A logs every job and task on the vendors' own records since 1 September: 226 IBM jobs on six chips, 3,035 Cepheus tasks (cancelled and failed included), in 126 families with their reads. `run_index/RUN_INDEX.csv` is the list; `run_index/pull_history.py` and `pull_other_keys.py` re-pull it from the services.
- **"Did your own jobs disturb the chips?"** Limitation 8: our first 197 jobs (through 4 October) against 75 chip-days of IBM's calibration record, no trace (rank correlation +0.18 / -0.02 / -0.05). `code_20261004/our_load_full.py`.
- **"Can I re-run your readers?"** Every quoted number carries a tag to a read file or a ledger entry. Two scripts that once ran only inline were recovered and re-run: `code/stopwatch_triangle.py` reproduces `reads/stopwatch_triangle.json` exactly; `code/mirror_check.py` reproduces `reads/mirror_check.json` exactly. Three numbers whose scripts were not kept are said so in the text (the 3.5-us readout cost, the 134 / 98 outside-cloud counts, the 25-of-31 ibm_fez job selection).
- **"Is the per-qubit claim per qubit?"** Fixed 4 October night: the hold-run 0.002 is a mean over qubits; single qubits scatter +-0.02 (`reads/park_per_qubit.txt`).

## Release (for_indahl_ai/data/, 898 files, every one in SHA256SUMS.txt, `shasum -a 256 -c SHA256SUMS.txt` passes; zip ~/Desktop/DISCO_DATA_RELEASE_20261005.zip, 226 MB)
- reads/, code/ (2 October runs); reads_20261004/, code_20261004/ (4 October); reads_20261005/, code_20261005/ (5 October); rigetti_20261004/, rigetti_20261005/ (every Cepheus batch, raw shots); calls/ (every hashed call, with its .sha256 and the Boston erratum); freeze/ (126 freeze records); run_index/; early/ (168 MB: the 24-29 September run folders the appendix cites, kept as they were; account numbers blanked).
- Variable names in hashed code stay as frozen: in `analyze.py`, `c.hunter` is the second readout's effect over the first. In the text the 1/phi part of the framework is called the attractor.

- **"Does the freeze prove the code that ran?"** Not for 20 runs of 5 October: their scripts were copies that kept the parent's freeze list, so the freeze hashed the parent. Three readers stand beside it, printed run by run: the file times, a side freeze stamped the same day (calls/SIDE_FREEZE_20261005.txt with its erratum), and circuits rebuilt from the on-disk files compared with IBM's stored job inputs, which match on all 20 (data_provenance_20261005.txt; code_20261005/provenance_check_20261005.py). On the four ripple runs the unhashed lines include the laid windows, so there IBM's copy is the record.
- **"Why is there a SHA256SUMS_20261004.txt?"** The 4 October checksum list, kept beside the new one. Its own timestamp proof was deleted by mistake on 5 October (ledger §272); the calls' stamps are intact.

## Before submission
- A DOI archive (Zenodo) for the release: Wayfinder's account. The release is 196 MB, too large for arXiv's ancillary files; the paper's data section points to the archive. This is the paper's last [TO FILL].
- Shuttle's pass, then Evan's (likely the quant-ph endorser).
- 6 October: Phoenix day 2 (581-583, 10:00 EDT) and Pittsburgh day 2 (521, 14:00 EDT) fire on timers; their calls (PHOENIX_DAY2_CALL, TIME_LEG_T2T1_CALL) are hashed and stamped. Listed in 3.7 as not yet scored until read.
