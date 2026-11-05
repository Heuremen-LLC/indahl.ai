# YO Read FRESH TEST, Addendum 7: sensitivity analyses (Sage, 5 Nov 2026), written after the run and BEFORE any output is read

The run finished at 2026-11-05T01:54:16Z (RUN_STARTED.log). No eval_fresh file, out_ log or OUTPUTS_YO_FRESH content has been opened.
This addendum must have its own Bitcoin block before the outputs are read. The output stamp's block must also land first.

1. PRIMARY stays the headline. The analyses below are reported whatever they show, beside primary, with the same scorer.
2. Sensitivity "pktron": primary minus doi:10.2139/ssrn.7358502 (87 papers). It shares its author's code-availability text with a
   trained paper on another topic (rs-10838198, train.jsonl row 1071). Read as a sibling, not the same work (contam/yf_contam.out).
3. Sensitivity "text90": primary minus every primary paper whose full-text 8-word-shingle share with one trained paper exceeds the
   floor's 90th percentile (0.121; floor = 148 TEST papers of the 688 vs the 540 trained papers; contam/yf_contam_text.out).
   That is one paper: doi:10.5281/zenodo.18209070 (0.133 with zenodo.18164730). Read by hand: not the same work (contam/HAND_READ.text).
   It is dropped anyway, because the rule is the threshold.
4. A third sensitivity, primary minus papers a metadata check (authors and title against the trained papers) flags, goes in a
   further stamped addendum if that check runs; it too must have its block before the read.
5. Method: yf_minus.py TAG. It filters data/test_items_primary.jsonl and runs yf_score.py unchanged (it refuses unless the scorer's
   sha256 equals the Addendum 3 hash 26194d1a...), writing results_fresh_primary_minus_TAG.*. Planted test: yf_minus_tests.out.
6. Disclosed limits added here (no change to what the run measured):
   - The run start is self-clocked (our manifest clock, 01:35:35Z). The plan blocks prove the plan came first. Nothing outside proves
     the run did not start earlier. The gate block hash seeds nothing (decoding is greedy; training seeds are fixed in the yamls).
   - The ots client version is not recorded. The driver loads the base model by name with no revision=; the pin rests on refs/main
     70d244cc plus HF_HUB_OFFLINE=1 (manifest), with all 10 snapshot files hashed in Addendum 4.
   - The 688-paper exclusion list's hash (eb26c018, list.json.pre-removal-20261102) is in no stamped file; our own git holds it (cd409a2).
   - Contamination: no fresh prompt contains a training sentence beyond site chrome (contam/yf_contam.out). Every training sentence is
     fixed by block 974519 (contam/CUSTODY.text). Full text: no primary or sensitivity paper exceeds the floor's 99th percentile
     (0.319); the floor comes from the training corpus and period, so it is a looser bar for fresh papers than it looks. A same-work
     version that shares little text is not ruled out (the full-text check found 6 of 8 known trained twins, 3 above the floor).
   - The ADAPTERS_*.sha256 lists hash only adapters.safetensors; Addendum 4 stamps the weights and configs.

Files (sha256):
   0fd28201b491a3c46acd4f97508ff38dd2951b4313006beb7999061c7ac4fd4d  yf_minus.py
   3f6bf6d229220df35abb48d9f120b5babf33532eff367afcef06d5a5799b66db  yf_minus_tests.out
   f1343a09456481144f6d7b3bd25a84ece99ebdcc532025ac19b3aab357344342  contam/yf_contam.py
   925b9b74f72b867aa6446a101e2b4e725d9f2bcb8fd238494e71c7eb8d591d99  contam/yf_contam.out
   7922f7de6d2254da7752d8fd3d4f6d86ffe6694a6257807c10f1e691c4eaabc1  contam/yf_contam_known.py
   0e91b7d68c9eb61fddba4bbe9fd08d27326e0d5bd20d5edd556c03579b51cb95  contam/yf_contam_known.out
   ebb4a1d4e32bf4ff020f53ed0f2be61c76caaf115cf2cfb2c6c08256c13720a5  contam/yf_contam_text.py
   81f6f7d0e60d502c3acaeafe96f08c5e7f994f2797122b23f399cc8e76864f8c  contam/yf_contam_text.out
   7dd9ca1365a2aa33f2e7f050a9cc4582c174a229376a351a958b465ad552246f  contam/HAND_READ.text
   9cc066e838ac17d5b8bd91360589b13c206bb75d50f764665ece47a7b34f229c  contam/CUSTODY.text
