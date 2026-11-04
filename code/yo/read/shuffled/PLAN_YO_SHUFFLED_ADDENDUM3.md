# Addendum 3 to PLAN_YO_SHUFFLED.md (4 Nov 2026, Sage's two holes in the SELF-LABEL arm). Stamped before any self-label is generated.
1. Thinking mode. The prompt template is yo2_data.render (yo/yo2_data.py line 21-22), which calls apply_chat_template(..., add_generation_prompt=True,
   enable_thinking=False): Qwen3 thinking is OFF, pinned here. Dry check on 20 made-up prompts in the same format (none from the plan's items;
   DRYCHECK_20.py beside this file), 4 Nov ~10:12Z: 20 of 20 replies were a bare YES or NO within 8 tokens, 0 off-format.
   Parse: kept EXACTLY as yr_eval.py line 12, regex \b(YES|NO)\b, case-sensitive upper-case, whole word ("Nothing" is not read as NO; a lower-case
   "no" is not read either). Not made case-insensitive, because the frozen YO Read scoring uses this exact parse and every arm must use the same one.
2. Size confound. Off-format items are left out of SELF-LABEL training (Addendum 2), never filled with real labels and never defaulted to NO.
   Drop counts (overall and per question, train and valid) are written into selflabel/BASE_RATES.text beside the base rates, BEFORE any adapter trains.
   If more than 5 % of items drop overall, or more than 10 % for any one question, the page names training-set size as a live alternative
   explanation for that question's SELF-LABEL comparison.
