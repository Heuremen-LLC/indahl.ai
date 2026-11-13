# Thunderdome: the two models that fault least meet head to head (27 Oct 2026, his idea)
Written and committed before any round 1 to 11 rate has been read. The finalists are chosen by this rule and nothing else.

## Who enters (select_finalists.py)
Over rounds 1 to 11 (round 1 is faultsbench2), per model and per round, the known-good gate must pass (repeat agreement 95% on the scored class, family controls right on 80%).
A model enters the pool if its gate passed in at least 9 of the 11 rounds. In each round it gets one number: the mean over P1 to P4 of its fault rate with the Guard wording in the prompt (guard arm, readable replies only, families whose gate failed excluded).
Its score is the mean of those round numbers. The two lowest scores are the finalists. A tie within 0.005 goes to the model with more gate passes, then to the lower bare-arm fault rate.
If fewer than two models qualify, there is no Thunderdome and the page says so. Nothing is ranked on a page below the top two.

## The arena
Two fresh question sets, rounds 12 and 13 (faultsbench_r12, faultsbench_r13: new stories, new seeds, built and committed now). Both finalists answer exactly the same items in the same arms, temperature 0.
Reading: for each family, paired fault difference (finalist 1 minus finalist 2) on the guard arm and on the bare arm, bootstrap 2,000, outcomes AHEAD / BEHIND / CONSISTENT / CANNOT_TELL, never a forced winner.
If the two sets give opposite signs for a family, that family is CONSISTENT and both sets are shown. The page says which model faulted less only where the interval excludes zero in both sets.
Gate, parser hand-check and referee passes apply as in every round. No model is named a best model.

## ADDENDUM 1 (28 Oct, after rounds 12 and 13 were scored, before anything was published)
1. Parser hand-check on both finalists, both rounds, per the standing rule. No scorer change and no repair. Findings: qwen3:4b writes a long chain of reasoning and runs past the 1,500 token reply budget (done_reason length) on 28 of 30 P2 items and 29 of 30 P4 items in the rounds read, so those replies are UNREAD by rule. smollm2:1.7b answers every undecidable P1 item with the single sentence "No, A is not better than B" and gives P2 accuracies that do not match the counts it was given, so those are UNREAD by rule.
2. Under the plan's reading rule, a family gate that fails makes that family CANNOT_TELL for that model. A paired reading needs both finalists' gates to pass in the same round, so most families have no paired reading. The page shows each model's rate where its gate passed, the count of unread replies everywhere, and says cannot tell where the rule requires it. No winner is named.
3. A larger reply budget for qwen3:4b would be a plan change. It would be a separate declared arm in a later round, never a rescoring of these.

## ADDENDUM 2 (28 Oct, same day, correction)
Addendum 1 point 1 said smollm2:1.7b answers every undecidable P1 item with the single sentence "No, A is not better than B". That holds for round 12 (30 of 30 unread). In round 13 the same model's P1 replies were mostly readable (5 of 30 unread). The sentence on the page that repeated the claim has been removed, and the page now gives counts only. Scores and rules are unchanged.

## ADDENDUM 3 (30 Oct 2026, site pass, correction)
1. The selection rule as run did not match its text. The plan says "families whose gate failed excluded". select_finalists.py skipped only outcomes starting "CANNOT_TELL (family" and "CANNOT_TELL (repeat". A family whose outcome was "CANNOT_TELL (too few read)" (under 10 readable pairs, score.py) stayed in. As run on 27 Oct the guard-arm means were smollm2:1.7b 0.058, qwen3:4b 0.167 and olmo2:7b 0.210. The qwen3:4b figure came from 21 family-rounds that read "too few read". Across its 44 family-rounds qwen3:4b has no readable one (23 "family control failed", 21 "too few read", feed /iris/bench-results.json).
   With every CANNOT_TELL excluded, as the text says, the means are smollm2:1.7b 0.058 and olmo2:7b 0.224, and qwen3:4b has no score. Under the written rule the finalists would have been smollm2:1.7b and olmo2:7b.
   Rounds 12 and 13 were run with smollm2:1.7b and qwen3:4b and are not re-run. select_finalists.py now excludes every CANNOT_TELL outcome, for any future selection. The lab page says what was computed.
2. The scorer behind the round rates was amended 11 times (faultsbench2/PLAN_v2.md, addenda 1 to 11, each dated). Addenda 1 and 2 were written before any rate was read. Addenda 3 to 11 were written after round 1 rates had been computed or while reading later rounds, and select_finalists.py ran on the rescored rounds. The sentence at the top of this plan, "Written and committed before any round 1 to 11 rate has been read", holds for this plan (commit ac4fd66, 27 Oct 09:33) and does not cover the scorer.
3. Addendum 1, point 1, gave "28 of 30 P2 items and 29 of 30 P4 items" as if they were one set. From the reply files, qwen3:4b bare arm: P2 was cut off at the reply budget on 28 of 30 items in round 12 and on 0 of 30 in round 13, and P4 on 30 of 30 in round 12 and 29 of 30 in round 13. We have not found why P2 differs between the two rounds. The rounds used different stories and seeds. Nothing was rescored.
