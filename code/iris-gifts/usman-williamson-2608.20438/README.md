# Usman and Williamson, arXiv 2608.20438: a reading

A reading of the released runs behind "Peer-Voted LLM-Agent Stress Tests Find Feed-Induced Lexical Convergence but No Reliable
Matched-Exposure Advantage for Distributed Sources" by Rana Muhammad Usman and Dominic Williamson (arXiv 2608.20438), from their Hugging
Face release at revision 64d770e. The plan was committed before the reading was computed. GIT_LOG.txt lists the commits with their times.

## Reading

Defined after reading the paper and code. In each block, every honest agent's round-0 request is the same prompt and the same seed in all
four conditions (control, likes, single source, distributed sources). Round 0 shows no feed, honest agents come first in every
condition, and the request seed is a function of trial seed, round, phase and ordinal. Both Qwen models returned identical text in all
four conditions for 192 of 192 agents. For the other five models, the text differed in at least one condition for gemma4 e4b 190,
granite4 3b 189, ministral-3 8b 189, gemma4 12b 153 and ministral-3 14b 192 of 192 agents (u1.text). Posts are stored cut at 180
characters, so these counts are bounds. The request is identical, while server state and the mix of concurrent requests are not, so this
is a repeat floor for the whole serving setup as it ran. No cause is named.

## Run it

src/fetch_theirs.py downloads the posts and configs read here from the authors' dataset at a pinned revision (FILES.tsv) and checks every
hash. Then run src/u1.py with python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
