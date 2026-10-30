# Selvam and Ghosh, arXiv 2607.10626: a recount and readings

Our recount of "Eval-Pair Matrix: Answer-Paired Meta-Evaluation of LLM Judges for Grounded RAG" by Sriram Selvam and Anneswa Ghosh
(arXiv 2607.10626), from their public repository selvamsriram/eval-pair-matrix at daefdef (byte-identical to the anonymous mirror the paper
prints). The plan was committed before each reading was computed. GIT_LOG.txt lists the commits with their times. The data holds GaRAGe
passages and carries no license, so this folder holds no passage, question or answer text, only ids, flags and counts.

## What rebuilds

From the nine judge files, with our own code, the paired same-model contrast on the 275 validated records rebuilds with its intervals:
-0.5 pp [-2.7, +1.7] on the 456 answers that adopted the induced claim and -4.3 pp [-6.6, -2.0] on the 363 that avoided it (819 answers have
the matching judge and at least one other). Our intervals are a record-clustered bootstrap, 10,000 resamples.

## Readings

Every reading below was defined after reading the paper, and the later ones after the first results, as PLAN.md.text records.

- A third role. Each contradiction was written by one of the three models, so each answer also has a perturber. With the perturber's judge
  in place of the generator's, the contrast is -0.9 pp [-3.8, +2.0] on adopted answers and +2.3 pp [-0.4, +5.1] on avoided ones. On answers
  the perturber did not generate, that contrast against the mean of the other two judges is +4.5 pp [+0.8, +8.3] on avoided answers, but it
  moves with the generator's own judge, which flags less there (-5.3 pp [-8.4, -2.2]). Comparing the two judges that are not the generator's,
  the judge from the model that wrote the contradiction and the third judge do not differ detectably: 0.0 pp [-3.9, +3.9] on adopted answers
  (17 against 17 discordant) and +2.4 pp [-2.0, +6.9] on avoided ones (18 against 12). On adopted answers that excludes a difference larger
  than about 4 pp.
- The generator as perturber. Where the generator also wrote the contradiction, the matching-judge contrast is -2.2 pp [-6.4, +1.6] on
  adopted answers and -2.1 pp [-5.6, +0.9] on avoided ones, against +0.3 and -5.3 pp on the other answers. Neither difference resolves.
- Validation. On all 300 records the validating model is the perturbing model, and all 25 records that fail a gate were perturbed by Gemini
  (of its 125).
- The adopted and avoided strata come from a GPT-5.4 labeller, so the GPT judge shares a family with the stratum variable.

## Run it

src/fetch_theirs.py downloads the nine judge files from their repository at a pinned commit (FILES.tsv) and checks their hashes. Then run
src/readings.py with python3 from this folder (standard library). Nothing of theirs is run. CHECKS.md.text holds our checks.

Heuremen LLC
