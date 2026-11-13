# STAN v1 plan, addendum 1

Written 12 November 2026 after the stamped plan (PLAN.md, sha256 in PLAN.sha256) and while the first teacher, Llama, had started on the first slice. No teacher output has been read or scored. Everything below was fixed before any label was read. Nothing in it depends on a label.

## Order of the owner

Stamp and go. The plan was committed and its OpenTimestamps receipt submitted before the first teacher call. The code check (scripts/gate.py) is only that the plan is committed and the receipt exists. Confirmation of the Bitcoin block is upgraded later in the background and never blocks work. Sage reviews the plan before anything ships, not before the run.

## Contamination wall around gold

Every pool candidate (588 List studies with held text, not gold) is compared with every gold record by scripts/matcher.py. It flags a pair on any of: a shared DOI or arXiv id in the OpenAlex family, title similarity at least 0.80 (word or character trigram Jaccard), abstract TF-IDF cosine at least 0.50, author surname overlap at least 0.60 together with title similarity at least 0.45, or author overlap at least 0.60 together with abstract cosine at least 0.30. The thresholds are fixed here. The pool is the first 100 of the seeded order minus anything flagged. The matcher is scored on a positive control of real twins of gold items (the other DOIs in the OpenAlex family of a gold work, fetched as their own records from Crossref or DataCite, matched on content only with the DOI signal switched off), on a synthetic paraphrase control, and on gold against gold non-twin pairs for false flags. Results are in results/contamination_wall.json. Recall on translations is untested because no translated twins were found.

## Hand spot-check

40 three-way grounded PRESENT or ABSENT agreements, seed 4242, written to review_queue/spot_check_40.md with label, quote, definition and claim text for a person to read. The question is whether the quote supports the label, not only whether it exists.

## Split report on teacher agreement

Teachers run on gold dev only. STAN's agreement with gold on dev is reported separately for (item, code) pairs where all three teachers agree at round 1 and for pairs where they split. This is reporting only and never trains anything. The paired test against the base on gold test is the only keep decision. Teachers are not run on gold test, so the teacher baseline is on dev only.

## Correlated teachers

Llama, Mistral and Gemma are trained on overlapping web text and may share blind spots, so three-way agreement is not independent evidence. The gold recounts are the only independent check. Nothing is tuned toward gold test. No prompt is edited after seeing test scores. Gold dev is for development. Gold test is read once, by scripts/final.py, which refuses to run twice.

## No Sage memory in any prompt

Teacher, base and STAN prompts contain only the standard's definition text for each code and the title and abstract of the item. No Sage core memory, pins, set-down content or library memory is in any prompt. The seats are used as models.

## Keep rule, interval and band wording

Unchanged from PLAN.md. Interval method and level: Wilson 95 percent for rates, paired bootstrap with 2000 resamples over items, seed 7, 95 percent percentile interval for differences. Band rule: the bound is zero with margin zero. ABOVE (whole interval above zero) is kept. Whole interval below zero is reported as harmful. An interval that straddles zero is not kept and reads CANNOT_TELL with reason STRADDLES_EDGE.

## Amendment 4, 12 November 2026: pool slices from the whole List, per-slice crosstalk and silver, training threshold

Written before any teacher output was read or scored.

- The pool grows from the whole QIA List (all studies with an arXiv or DOI link, not gold, not removed, not in slice 1) plus the IRIS List studies, in a seeded shuffle (random.Random(20261112)). Abstracts come from OpenAlex then the arXiv API, cached, three workers with a quarter-second pause each. The contamination wall of this addendum runs on every candidate. Items flagged are written to results/slice_wall_flagged.jsonl and never labelled. Items already in an earlier slice by title are skipped. Slice k holds 100 kept items, written to data/slices/slice_kk.json. Slice 1 is the first 100 of data/pool.json. The log is results/slice_log.json.
- Each teacher runs slice 1 first (with gold dev for the teacher baseline), then slices 2, 3 and so on through scripts/chain.sh, one writer per teacher file, so no teacher idles.
- Crosstalk runs per teacher on every item that all three teachers have labelled and has not yet had its second round. Silver and the review queue are rebuilt from everything labelled by all three.
- Training threshold, fixed now: v1 trains once, when the silver training set after the class cap reaches 400 rows, or when the slice builder and the teachers have finished all slices, whichever comes first. Slices that finish later are not used by v1. Rows from slices labelled after training starts go in the data folder for a later version.
- Nothing about the metrics, the keep rule or the splits changes.

## Amendment 5, 12 November 2026: gemma back to Armature (host only)

The Mac Ollama served gemma at about one item a minute because the house training holds the Mac GPU, against about six seconds an item on Armature. Gemma now runs on Armature again, with llama and mistral, one model at a time through scripts/arm_chain.sh so the three never fight over the loaded-model slot. Labels already written by gemma on the Mac stay (same model tag, temperature 0). No model, prompt, split, metric or rule changes.

## Amendment 6, 12 November 2026: training threshold lowered to 250 rows

Slice 1 yielded about 90 silver training rows after the class cap, so 400 rows would take about five slices and several hours of Armature time. The threshold in Amendment 4 is lowered to 250 silver training rows after the cap, or the end of all slices, whichever comes first. Nothing else changes. No test score has been read.
