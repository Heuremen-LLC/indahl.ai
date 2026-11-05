# YO Read FRESH TEST, Addendum 8: the metadata same-work check (Sage, 5 Nov 2026), BEFORE any output is read

No eval_fresh file, out_ log or OUTPUTS_YO_FRESH content has been opened.
1. contam/yf_contam_meta.py (flag rule fixed and committed in 45de0bb before any score): authors and title of each fresh paper against the 540
   trained papers, read-only from Zenodo, arXiv and Crossref (contam/meta_cache.json). Flag: top match with (author overlap >= 0.5 and title
   Jaccard >= 0.3) or title Jaccard >= 0.6.
2. Known-good: 8 of 8 known same-work fresh papers with a trained twin have the twin as top match and are flagged (Sage's bar: 7 of 8),
   including the 2 the full-text check missed.
3. Floor: 6 of the 107 TEST papers with metadata are flagged (41 have none). They are papers in the training corpus matching same-author
   papers in training, so some may be real siblings; the rate is an upper bound on false hits.
4. Primary (88): 0 flagged, 0 without metadata. Sensitivity (84): 0 flagged. Full (288, secondary): 13 flagged, 9 of them known same-work
   papers already outside primary; the other 4 are named in contam/yf_contam_meta.out.
5. So Addendum 7 item 4's third sensitivity (primary minus metadata flags) is primary itself. No further analysis is added.

Files (sha256):
   e8bd4cb9dde7be07961022e6ec926de82489bd8524293d272589398e0b1dc4f1  contam/yf_contam_meta.py
   7128cbcb431830a93b4170060de11741bb73118ed4dbdc62d9ee8be9df8d4535  contam/yf_contam_meta.out
   e7f97e25cb963c1767852a36a0ee2e6a3ed4ebf26ab5b9f21df8b8217738a3a7  contam/yf_meta_fetch.py
   35367c3c6282078c14ea49167490a9df5c9615041a0fde14030b1523d2d1c977  contam/meta_cache.json
