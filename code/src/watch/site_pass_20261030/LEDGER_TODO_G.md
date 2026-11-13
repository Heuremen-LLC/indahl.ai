# Ledger commands for lane G (/oy main page), 30 Oct 2026. Written by the lane G fix agent. Nothing here has been run.
# Run them from any directory, in this order, BEFORE the next ship. oy_matrix = indahl-ai/oy.html, which is built from oy_index/matrix_page/oy_body.html.
# oy_body.html already carries the new text. Until these run, check_ledger.py reports MISSING for the 12 rows swapped below.
# No value, lo, hi or outcome changes, so no --checks block is needed. The set commands change claim text only.
# After the commands: python3 ~/bones-forge/ledger/check_ledger.py shows drift 0 once the page is rebuilt by ship.sh.

## G-1 and G-2: 148 rows with one of them ours, the date, the method and the selection rule are printed above the counts
# The method paragraph prints "The list has 148 rows, one of them ours. The counts below are out of 148 rows and include our own." oy.rows_148 already carries 148 including row 0.
python3 ~/bones-forge/ledger/ledger.py on oy.rows_148 oy_matrix "The list has 148 rows, one of them ours. The counts below are out of 148 rows and include our own."
# The zero for a learning outcome now says none found in any row and in six searches, as of 25 Oct 2026. The row oy.learning_outcome_zero already says counterexample search 6 ways, 25 Oct.
python3 ~/bones-forge/ledger/ledger.py on oy.learning_outcome_zero oy_matrix "None found in any row, and none in six searches for it. As of 25 October 2026."

## G-16 Kestin: the interval is named (95% percentile bootstrap over students, 5,000 resamples, post-test points). Recounted today with oy_index/harvard_kestin/recount.py on the GitHub .dta: [0.40, 0.91], indices 124 and 4874 of 5000.
python3 ~/bones-forge/ledger/ledger.py on oy.kestin oy_matrix "The interval is a 95% percentile bootstrap over students, 5,000 resamples, in points on the post-test score"

## G-17 UMD: paper 0.37 (0.27 to 0.37), our division of Table 3 gives -0.32 and -0.37, 41 and 3,387 come from the OSF pre-registration
python3 ~/bones-forge/ledger/ledger.py off oy.umd oy_matrix --why "text now separates the paper figure (0.37; 0.27 to 0.37) from our division of Table 3 (-3.55/11.09 = -0.32, -4.12/11.09 = -0.37) and names the OSF pre-registration as the source of 41 and 3,387 (site pass G-17)"
python3 ~/bones-forge/ledger/ledger.py on oy.umd oy_matrix "The paper reports final grades lower by 0.37 SD in the exact-match sample and by 0.27 to 0.37 SD across samples. Our division of its Table 3 by the control SD gives -0.32 without controls and -0.37 with controls in the exact-match sample. The OSF pre-registration lists 41 instructors and 3,387 consenting students. The paper analyses 30 and 2,379"

## G-18 UMN: learning processes, not statements. 42 of 65 is the report; 0 of 65 is our count from its 65 per-process tables (max 32% rating evidence 3 or 4, rule is 75%)
python3 ~/bones-forge/ledger/ledger.py off oy.umn oy_matrix --why "report unit is learning processes; the 0 of 65 is our count from the per-process tables, not a figure the report prints (site pass G-18)"
python3 ~/bones-forge/ledger/ledger.py on oy.umn oy_matrix "Of the 65 learning processes, 42 reached consensus on enhancement, vulnerability or both, as the report states. Applying the report’s own evidence rule to its 65 per-process tables, 0 of 65 reach consensus on evidence. That total is our count from the tables"
python3 ~/bones-forge/ledger/ledger.py set oy.umn --field claim --to "UMN/UNC/UCI consensus: 42/65 learning processes effect consensus (report), 0/65 evidence consensus (our count from its per-process tables)" --why "claim text says whose count each figure is" --evidence oy_index/matrix_page/findings.py

## G-19 WSU: the bin is renamed Outcome reported without counts (the quote prints 33%). The quote itself is not tracked by a ledger row.
python3 ~/bones-forge/ledger/ledger.py off oy.trial_wo_numbers oy_matrix --why "bin label renamed from without numbers to without counts: the WSU quote prints 33% and no case count (site pass G-19)"
python3 ~/bones-forge/ledger/ledger.py on oy.trial_wo_numbers oy_matrix "Outcome reported without counts 3"
python3 ~/bones-forge/ledger/ledger.py set oy.trial_wo_numbers --field claim --to "Wall S0: outcome reported without counts (columbia, gsu, wsu)" --why "bin label renamed on the page" --evidence oy_index/matrix_page/build_matrix_page.py

## G-20 Jabarian and Imas, MIT, Lin: detector, ruler and grader are named
python3 ~/bones-forge/ledger/ledger.py on oy.jabarian oy_matrix "by our count, 1 of 1,992 at the vendor’s “Possibly AI” label"
python3 ~/bones-forge/ledger/ledger.py on oy.mit oy_matrix "counting an evidence item as named when the report cites it in the same subsection"
python3 ~/bones-forge/ledger/ledger.py off oy.mj4bu oy_matrix --why "text now names the grader and setup and says passing answers (site pass G-20)"
python3 ~/bones-forge/ledger/ledger.py on oy.mj4bu oy_matrix "GPT-4o re-grader (gpt-4o-2024-08-06, temperature 0, three calls per answer, majority label) on Python function designs: after a synonym swap, 47 of 100 passing answers fail, against 7% for unchanged copies"

## G-21 semicolons out of /oy cells (plain sentences). Same numbers, same words, a period where the semicolon was.
python3 ~/bones-forge/ledger/ledger.py off oy.bastani oy_matrix --why "semicolon replaced by a comma (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.bastani oy_matrix "The exam effect, -0.054 (-17%), is significant under clustered standard errors (p ≈ 0.02) and not under a wild cluster bootstrap (p ≈ 0.11, 13 GPT-Base classrooms)"
python3 ~/bones-forge/ledger/ledger.py off oy.cornell oy_matrix --why "semicolon replaced by a period (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.cornell oy_matrix "An item count of 2,029 against 1,988 respondents. Group labels total 2,539"
python3 ~/bones-forge/ledger/ledger.py off oy.denison oy_matrix --why "semicolon replaced by a period (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.denison oy_matrix "53% used AI for coursework in fall 2024, 78% in spring 2025, nearly 80% in October 2025. 55% agree"
python3 ~/bones-forge/ledger/ledger.py off oy.fisher_abstract oy_matrix --why "semicolon replaced by a period (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.fisher_abstract oy_matrix "Its tables: any prohibition 57% to 59%. 25 of the 34 points fall at a change from one-choice to multi-choice forms"
python3 ~/bones-forge/ledger/ledger.py off oy.gwu oy_matrix --why "two semicolons replaced (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.gwu oy_matrix "The text prints “a 476.2% increase in the ‘cheating’ category” and its own table prints 472.6%. The table prints 84.64% of reports as cheating, and 209 of 256 is 81.64%"
python3 ~/bones-forge/ledger/ledger.py off oy.oppenheimer oy_matrix --why "semicolons replaced by periods (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.oppenheimer oy_matrix "89% at the scale ceiling. The printed t(177) = 4.25 carries the p of a paired test, t(26) = 2.97, p = .006"
python3 ~/bones-forge/ledger/ledger.py off oy.pardos oy_matrix --why "semicolon replaced by a period (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.pardos oy_matrix "margins of about 13.4 points or wider. The ChatGPT group starts 10-12 points lower"
python3 ~/bones-forge/ledger/ledger.py off oy.pilot_rochester oy_matrix --why "semicolon and the internal phrase course count not read replaced by a plain sentence (site pass G-21)"
python3 ~/bones-forge/ledger/ledger.py on oy.pilot_rochester oy_matrix "GoodNurse course. Users 95.1% vs non-users 88.8%. The paper is behind a paywall and we have not read the number of students."
