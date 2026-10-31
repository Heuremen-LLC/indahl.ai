# Build report: our parser, tool environment and oracle for arXiv 2609.32042

## What was built
Standard library only (python3 -I). protocol.py parses replies and repairs, weather.py is the five tools, oracle.py gives pass or fail with tags, agent.py is the step loop, prompts.py renders the system prompt and the chatml and llama-3 text, miniyaml.py reads task files. replay.py and acceptance.py are the test; run_all.sh runs it with the other checks. His code was read as text and never run. The city table, neighbour graph, prompt strings and oracle patterns are transcribed constants, compared with his source through syntax trees (constants_check.py).

## Acceptance
We replayed all 73 released runs plus the 16 L0e and L0-control runs from his runs/ folder: 4,307 trajectories and 17,973 steps (release_data alone: 4,147 and 17,221). Tool-result mismatches: 0 of 10,606 steps that carry one. Verdict mismatches: 0. Also 0 differences in parsed action, parse error, state, repair, final state and step count. All 2,952 run.log lines match whole, including tags and argument values. All 4,307 matrix rows agree on pass and tag set. Run-level numbers match summary.json in all 89 runs and the run.log footers in all 68 that have one.

Trajectories / steps per suite, zero mismatches in every suite and model: main67 2,412 / 9,812 (three models, 804 each); ladder46 1,288 / 5,448; variance at T 0.7 402 / 1,845; subset15 45 / 116; L0e 80 / 398; L0-control 80 / 354. acceptance_report.txt has the table by model.

## Mismatches found on the way
The first pass had 58, all in parse-error message text, none in results or verdicts (first_pass_mismatches.tsv). Thirty-four were pydantic cutting long values by UTF-8 bytes, not characters. Twenty-four were Python: his logs came from 3.12, we run 3.14.7, which words a trailing-comma JSON error differently. Both are fixed; the final run has none.

## The 21 runs with no run.log
These are 12 June 11B runs, 8 June 7B runs and one 7B gate run. Their per-task verdicts are his replay, not a log. Ours equal that replay in 1,355 of 1,355 trajectories, tags included. We also held ours to the summary.json written at run time: pass count, success rate, repair count and the full tag histogram, equal in all 21. Task-level agreement is therefore with his replay only.

## Prompts
His logs hold no rendered prompt, so a byte comparison with logs is impossible. His runner hands messages to llama-cpp-python, which renders them. Our chatml and llama-3 text equals that library's formatter functions (v0.3.19, read as text) on all 17,973 real prompts and 100,000 random message lists. Our system prompts equal his templates and our message building matches his loop, both checked on syntax trees. rendered_step0.tsv pins step-0 prompt hashes for all 138 task files.

For the live run: his chat_format is explicit, so the GGUF's own template is never used. Send the raw text as a completion, stop at <|im_end|> or <|eot_id|>, and let the tokenizer add BOS.

## Not reproduced, not exercised
- Token-level prompt identity and latency need the GGUF tokenizers and a model; then tie out total_tokens with llama-tokenize.
- No record reaches these branches: forecast, severity, message and distance errors; fold-matched city names; the min_tool_calls and final_answer_no_temperature checks; malformed specs; two schema errors. Of 24 deliberate breaks (mutation_test.py), the acceptance test caught 14. The other ten sit in logic the records never exercise; selftest.py (152 hand-worked cases) or constants_check.py catches them, but those cases are our reading of his docs, not evidence.
- A list or dict for severity or a unit crashes his harness. Ours returns INVALID_ENUM.
