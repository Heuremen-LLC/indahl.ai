# Saqlain, arXiv 2610.29812: readings

Readings of the released runs behind "Real PMIDs, Wrong Papers: Harness Design for Biomedical Claim-Verification Agents" by Mohammed
Saqlain (arXiv 2610.29812), from the author's repository at commit 6a6acdb7cedd. The plan was committed before each reading was computed.
GIT_LOG.txt lists the commits with their times.

## What rebuilds

Accuracy for every harness and backbone from the per-claim results files equals summary.json (readings.text).

## Readings

Every reading below was defined after reading the paper.

- The same PubMed search, twice. The two backbone runs each cached the searches they sent, so 166 queries appear twice in the released
  cache. For 156 PubMed returned the same list both times, for 9 a different set of papers, and for 1 the same papers in a different order.
  Where the list can be traced, the first cached copy is the one the Gemini 3.1 run recorded and the second the Gemini 3.5 run. The cache
  loader keeps the last line for a key, so a rerun from the released cache hands Gemini 3.1 the Gemini 3.5 list for those queries. The
  reported tables come from the results files and are not affected.
- "Without sacrificing SUPPORT/CONTRADICT accuracy" (F4), on the 64 claims whose gold is SUPPORT or CONTRADICT. Against single-shot
  retrieval it holds for both backbones (+0.484 and +0.438). Against closed-book and the agent harness it holds for Gemini 3.1 flash-lite
  (+0.078 [-0.016, +0.172] and +0.125 [+0.016, +0.234]). For Gemini 3.5 flash-lite the oracle minus closed-book is -0.078 [-0.203, +0.031]
  and minus the agent +0.016 [-0.109, +0.141], so the data cannot tell between no loss and a loss of about twenty points. The Gemini 3.5
  oracle predicts NEI on 45 claims against 36 gold NEI (precision 0.69), the Gemini 3.1 oracle on 31 (precision 0.90). Intervals are 95%
  paired bootstrap over claims.

## Run it

src/fetch_theirs.py downloads the ten files read here at the pinned commit (FILES.tsv) and checks every hash. Then run src/readings.py
with python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
