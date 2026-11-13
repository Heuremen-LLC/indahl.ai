# MLPerf stated vs delivered (working name, 28 Oct 2026). Local only. Nothing on a site, nothing shipped.

## What it is
Per-accelerator throughput from the MLCommons summary files (Apache-2.0), plus every quantitative claim a vendor makes about those results, held against the same file.
Public-company rule applies: quotes only, both documents, no adjectives, no ticker talk.

## Sources (hashes in perchip_rows.json and claims_nvidia_v51.json)
- github.com/mlcommons/inference_results_v5.0, v5.1, v6.0 summary_results.json (closed, datacenter, throughput units). 1,727 rows, 569 model/scenario/accelerator groups.
- NVIDIA developer blog on v5.1 (saved raw/nv_blog_v51.html, text raw/nv_blog_v51.txt, fetched 28 Oct 2026).

## Schema notes (read before counting)
- ID is a system entry, not a row. One ID carries many model/scenario rows.
- a# is accelerators per node. Total = Nodes x a#. v6.0 adds Total Accelerators and it agrees with Nodes x a# on every row where both exist (0 mismatches in all three files).
- a# is an empty string on CPU-only systems. Closed datacenter rows left out for that reason: v5.0 49, v5.1 61, v6.0 24. They are counted here, not dropped silently.
- Per-GPU is not an MLPerf primary metric. It is result divided by accelerator count, the same way NVIDIA computes it.

## Method for a claim
1. Quote the sentence and the entry IDs it cites. 2. Recompute from the file with check_claims.py. 3. One of four outcomes: ABOVE / BELOW / CONSISTENT / CANNOT_TELL. 4. IBM-style rebuttal test before anything is called BELOW: different division, precision, scale, software, availability.

## Result so far: NVIDIA v5.1 blog, all nine checks listed (claims_nvidia_v51.json)
- C1, C2, C3, C6, C7 (three cells): CONSISTENT.
- C4 (about 5x vs Hopper): CANNOT_TELL. NVIDIA states its Hopper cells are not verified by MLCommons and the file has no closed H200 DeepSeek-R1 row. Its own cells give 4.66x offline and 5.23x server. The one published H200 row (HPE, open) gives 5.25x.
- C5 (nearly 1.5x disaggregated vs aggregated): ratio 1.467x holds. CANNOT_TELL on the attribution. The two entries differ in system size (72 vs 8 GPUs), and on the same two systems Server is 1.040x and Offline 1.011x. The summary file and the entry README do not say whether entry 5.1-0071 used disaggregated serving.
- No claim in this post came out BELOW. That goes on the table as it is.

## Next
1. Other vendor claims, each read by hand from the vendor's own page: AMD v5.1 technical blog (rocm.blogs.amd.com), NVIDIA v5.0 and v6.0 posts. Same check_claims pattern, one file per source.
2. Hand-count 10 rows per claim file against the repo entry before reading results (parser hand-check, his standing rule).
3. Ledger rows for every number that goes on a page. Then site build, gates, ship via ship.sh. Staged only until his word.
4. Open question for the page design: per-accelerator table by model and scenario with min / median / max across submitters (17 groups with 5+ submissions spread more than 15 percent, for example v6.0 DeepSeek-R1 Server on B300 from 4,430 to 7,552 tokens/s/GPU).

## Result 2: AMD v5.1 technical blog, twelve checks (claims_amd_v51.json, saved raw/amd_v51.html)
- CONSISTENT: A1 2.7x (2.695x), A3 3.4x (3.400x), A4 +2% / +4% (+1.7% / +4.2%), A5 94% (94.6%, range 93.7 to 96.8), A7 1942 and 2019 tokens/s, A10 +8% (+8.7%), A11 Mixtral Offline ahead of the H200 mean (1.109x, only 2 H200 submissions).
- A3 label mismatch: the blog calls entry 5.0-0054 a 4-node MI325X submission. The file lists it as 32 x MI300X, and no multi-node MI325X entry exists in v5.0. The ratio holds. Shown as a note on the row.
- CANNOT_TELL: A2 (3.9x and 7.9x multinode against an internal baseline; the published single-node row gives 3.77x and 6.97x), A6 (partners "nearly identical", no figure; spread 94.7 to 101.1 percent of AMD's row), A8 and A9 (baseline rows not in the file), A12 (figure bars are images).
- No claim came out BELOW.
