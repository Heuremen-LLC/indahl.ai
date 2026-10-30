# Seo, arXiv 2610.01243: a recount and a reading

Our recount of "When the Judge Acts: Auditing VLM-Guided Image Selection on Culturally Situated Prompts" by Huichan Seo (arXiv
2610.01243), from the author's released runs and ratings. The plan was committed before the reading was computed. GIT_LOG.txt lists the
commits with their times.

## What rebuilds

From his run files, with our own code: the Qwen3-VL-4B judge picks slot A on 439 of 900 calls (0.488) and changes its selection across
the three orders on 179 of 300 prompts (0.597). His 8-bit MLX run of the same judge returns the same image as the bf16 run on 854 of 900
calls (0.949). The unanimity gate keeps 121 prompts with a gain over random of 0.141 [0.110, 0.173]. All as printed (known_good.text,
s1.text).

## Reading

Defined after reading the paper. The paper already prints the gate under the 8-bit MLX run (Table 12). This reading adds the overlap
between the two gates. Of the 134 prompts either gate keeps, 115 are kept by both, with the same image on all of them. Six are kept only
under the bf16 run and 13 only under the 8-bit MLX run. In all, 43 of the 300 prompts have at least one call whose chosen image differs
between the two runs (46 calls), and 18 of the 19 prompts that change membership turn on a single call. The 8-bit MLX run changes
precision, runtime and checkpoint (a community conversion) together, so this reads one change of setup, not precision alone.

## Run it

src/fetch_theirs.py downloads the four files read here from the author's repository at a pinned commit (FILES.tsv) and checks their
hashes. Then run each script in src with python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
