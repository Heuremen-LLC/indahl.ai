# Deviations from PLAN_A_CEILING.md (declared 12 Nov 2026 after Sage's read)

1. Matching rule. The file says a pair is IN when the retrieved chunks contain "the specific figure, table, caption, run date or
sentence the note names". The run required EVERY key string chosen for the pair to be in the top 6. This was set by the judging
agent while writing scripts/ft_judge.py, not by the plan, and the pooled verdict depends on it:
   all keys (as run):  pooled 52/91 = 0.571 [0.469, 0.668], below 0.60
   any one key:        pooled 0.659 [0.557, 0.748], above 0.60
Both are reported. The file named per-code pass lines and did not name a pooled gate; the pooled number is descriptive under either rule.

2. Order of key choice. File times: retrieval.json written 13:46:09, judge_prompt.txt 13:46:55, ft_keys.py 13:50:46,
judgments.jsonl 13:51:06. The key strings were written after the retrieval output existed, by an agent that could read it and
the notes together. Whether keys were fitted to hits: CANNOT_TELL from the logs. Treat the per-code shares as possibly favourable.

3. Denominator. IN/(IN+OUT) uses 91 of 196 flagged pairs. Over all flagged pairs, IN is 52/196 = 26.5%. The abstract ceiling
was 9/191 = 4.7% [2.5, 8.7]. NOT_IN_TEXT is 45 of 196 (23%): evidence a recount cites that lives outside the paper's text
(released files, figures, the recount's own runs). That is a finding for the standard.

4. F6 sits at 9/15 = 0.600 and the one disagreement in the second read (9353f71dcb70 F6) is on that code. If it flips, F6 is 8/15
and fails. F6 is exploratory, outside any keep rule.

5. pypdf: extraction ran on 6.21.1 (system python) as frozen; chunking and BM25 ran in the venv (pypdf 6.19.0 present, unused).
