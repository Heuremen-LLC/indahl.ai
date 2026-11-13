# How deep the well goes (12 Nov 2026)

Source: arXiv yearly statistics pages (arxiv.org/year/<cat>/<year>), primary articles, not counting cross-lists. Raw: scratchpad
arxiv_year_counts.txt, copied below. OpenAlex was rate-limited (429) all afternoon, so its field counts are not used.

| Year | astro-ph | gr-qc (gravity, incl. GW) |
|---|---|---|
| 2015 (whole year) | 12,900 | 2,776 |
| 2016 | 13,214 | 2,599 |
| 2017 | 13,262 | 2,659 |
| 2018 | 14,079 | 2,857 |
| 2019 | 14,421 | 3,046 |
| 2020 | 14,835 | 3,359 |
| 2021 | 14,463 | 3,522 |
| 2022 | 14,496 | 3,496 |
| 2023 | 15,274 | 3,859 |
| 2024 | 16,333 | 4,026 |
| 2025 | 18,660 | 4,471 |
| 2026 (to 12 Nov) | 18,203 | 4,581 |

2016 to 12 Nov 2026: astro-ph 167,240, gr-qc 38,475. September to December 2015 adds about a third of 2015's total, which is an
estimate (monthly counts are on the same pages if needed).

So the window from September 2015 holds about 170,000 astro-ph papers and about 39,000 gr-qc papers on arXiv alone, before journals
that skip arXiv. That is far beyond a hand index. The desk picks slices: papers that ship public data (GWOSC strain, Gaia, TESS,
JWST/MAST, Planck) and headline numbers we can recompute from it. The gravitational-wave catalog papers and the work that reuses
GWOSC data are the first slice. That slice is countable in the hundreds to low thousands. Counting it needs an API that is not
rate-limited: NASA ADS with a token, or OpenAlex after its daily reset.
