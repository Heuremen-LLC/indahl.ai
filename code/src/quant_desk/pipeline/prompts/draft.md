First-pass desk audit for the quant desk (errata index of empirical quantitative-finance papers). Your output is a DRAFT. A blind second reader re-checks every PRESENT. Be conservative: PRESENT only when the paper itself shows it beyond doubt, CANNOT_TELL otherwise.

Inputs:
- /Users/heuremen/bones-forge/quant_desk/index/{BATCH}.json: 12 papers, newest first.
- /Users/heuremen/bones-forge/quant_desk/RULES.md: frozen rules and all the notes at the bottom, including the severity tiers. Read them fully.
- Code text: `cd /Users/heuremen/bones-forge/stan && python3 -c "import sys;sys.path.insert(0,'scripts');from common import code_block;[print(code_block(c)+'\n') for c in ['F1','F2','F3','F4','F5','F6','F7']]"`
- Format: match the keys of /Users/heuremen/bones-forge/quant_desk/index/../../sagar/index/batch_10_draft.jsonl rows exactly. Add "severity" (T1, T2 or T3) on every PRESENT, per RULES.md.

Keep scratch scripts in /private/tmp/quant_pipe/{BATCH}/ (create it).

For each paper: fetch https://arxiv.org/pdf/<id> (User-Agent "research-client", 3 seconds apart), extract with pypdf to /Users/heuremen/bones-forge/quant_desk/index/text/<id>.txt (skip if it exists), assign type E, M or T (see RULES.md), and mark F1 to F7.
- PRESENT and ABSENT need a verbatim quote of at most 250 characters, machine-checked as a whitespace-normalised substring, plus the page. Every cell needs "scope".
- F2: PRESENT only for a single best value headlined in the abstract or title with the spread not beside it. Recompute annualised returns, Sharpe ratios (mean over volatility, annualisation factor stated) and cumulative returns from printed inputs where possible.
- F3: PRESENT only for a claim with no significance, interval or null behind it.
- F6: PRESENT only for text against the paper's own table, caption, appendix or file, both quoted (quote_b in a note). Prose against prose is CANNOT_TELL, reason SCOPE, with "prose_vs_prose": true. An unreadable table is CANNOT_TELL, reason UNREADABLE.
- F5: recompute printed arithmetic (sums, percentages, 1-exp(-T*FAR), ratios of printed values), with the arithmetic and the input-rounding range. Never compare a median of ratios with a ratio of medians.
- F1: add "standard_practice": true where it applies.
- F4: "on request" is not released.

Write /Users/heuremen/bones-forge/quant_desk/index/{BATCH}_draft.jsonl, one row per paper. No author names or emails (mask GitHub handles as <author>). Contact no one. Edit nothing else.
