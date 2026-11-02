# Example: one entry

This is a fictional entry, written to show the format. The reading is invented. Every line is answered, and each answer says what was checked.

## 2026-11-01 10:00 Fictional reading: accuracy of two small models on a 400-question benchmark, before and after fine-tuning
packs: L
- I: holds: the comparison was written down before any run, with the same questions, prompt, decoding settings and answer extraction for both models, and the count of questions each arm lost to an unreadable reply is listed below.
- II: holds: every comparison lists questions that went right to wrong and wrong to right before any net, and each is set beside the flips between two runs of the same model.
- III: holds: both subject groups were compared with their signs shown, and the two groups move in opposite directions, so no single verdict is printed for the pair.
- V: holds: each accuracy is printed with its 95% interval, the paired difference has an exact test on the discordant questions, and the repeat floor sits beside it.
- VI: holds: each comparison ends in ABOVE, BELOW, CONSISTENT or CANNOT_TELL, and CONSISTENT is printed with the margin it was tested against.
- R: holds: counts come from the saved output files and their hashes, versions and dates come from the run logs, and nothing was typed from memory.
- L1: holds: the replies were read in full, 10 per subject group for each model, before any rate was printed, and no group had more than 1 of 10 mis-parsed.
- L2: holds: only progress lines were looked at until the reading of replies was finished.
- L3: holds: harness, prompt format, chat template, extraction rule, number of examples and token limit are named for both models and are the same.
- L4: holds: the repeat floor was measured by running the same model twice on one machine, with the server version and flags recorded.
- L5: n/a: no published output files were recounted in this reading, only the runs made for it.
- L6: holds: unread and truncated replies are counted by reason for each model, 4 and 6 of 400, and are listed in the output folder.
- L7: n/a: no judge model or labelled gold set was used, the answers are exact-match.
- L8: holds: the comparison is paired on question ids, the three seeds are shown as a spread, and no point win is reported.
- L9: holds: the prompts were searched for the answer strings and none contain them.
- L10: holds: model names are pinned by file hash, and the server, device and host are listed as carriers.
- L11: holds: the benchmark file was the same file for every run, with its row count checked at 400 before the first run.
- L12: n/a: no referee or labeller model took part in this reading.
