# Referee A: onrecord, ai, fortune (10 Nov 2026)

Verdict: FIX THEN SHIP (two rows block until dropped or split).

Method: every quote and every evidence quote checked against the saved raw copies (whitespace, quote marks, entities normalized, PDFs text-extracted). Live re-fetch of NASA Artemis, ESA Plato, ESA Juice, NASA Dragonfly, Altman (two posts), LessWrong (Legg, Christiano). Numbers re-added (Tesla, EIA). Machine list: fixes_A.json.

Counts: onrecord 25 ok / 10 fix / 0 drop. ai 13 ok / 7 fix (8 rows) / 2 drop. fortune 19 ok / 3 fix / 0 drop.

All saved quotes are verbatim in their raw copies except where listed below. No quote is an outlet paraphrase (the two outlet quotes, Fox/Ghosn and Register/Gates, are direct quotations the outlet attributes).

## Blocks ship
- ai amodei_mlg_2026: "could come as early as 2026, though ... much longer" is an earliest date, not a deadline. Drop (or log with a CANNOT_TELL-by-design reason, not a 31 Dec 2026 reading).
- ai aiimpacts23_milestones_2028: three milestones in one row, "at least 50%" stored as 0.5, conjunction criterion. Split into three rows with range 0.5 to 1, or drop.

## Fix before ship
- onrecord zimmer2016_5yr, bmw_2021: reason text contains "Doubt flagged ... a referee should confirm". Remove. Both readings (WRONG) hold.
- onrecord apple_neutral_2030: criterion does not match the quote (every device sold, net zero). Reworded.
- onrecord ibm_kookaburra_2026, ibm_cockatoo_2027: quote omits the product name. Prefix added (verbatim on the page).
- onrecord nasa_moon_landing_2028, nasa_artemis3_2027, nasa_dragonfly_2034, esa_plato_2027, esa_juice_2031: semicolon in deadline_rule.
- ai christiano_takeover: quote taken from the "(see above)" repeat. Use "Probability of an AI takeover: 22%". Also a semicolon in deadline_rule.
- ai altman_refl_agents: said 2025-01-06 not shown on page. Post is reported as 5 January 2025.
- ai musk_2026, aiimpacts23_all_tasks_2027, legg_q1_2018/2028/2050: semicolons in deadline_rule. aiimpacts23: saved abstract is v3, confirm sentence is in v1.
- fortune hubbert_1956_peak: quote says about 1965, deadline and RIGHT use 1970. Quote both cases (1965 at 150 billion barrels, 1970 at 200 billion), then RIGHT holds. Landed record calls 1971 (9,463) the 1970s high, it is 1970 (9,637).
- fortune asimov_2014: the quoted robot line cannot be tested, so the entry reading is CANNOT_TELL. The WRONG rests on two other items read via secondary pages. NYT text was not read.
- fortune ladies_home_journal_1900: popular line is C, X, Q, saved quote and reading are the population line. Align them.

## Notes
- Archive: 23 onrecord entries have no archive_url (nissan2013, nasa_jwst_2021, six Tesla, gates_spam_2004, msft, apple, google, airbus, five IBM, five NASA/ESA). Capture them or state none was made.
- NASA/ESA pages are undated, date said = date read, disclosed in the rule.
- Esa Plato: ESA news item (23 Apr 2026) says early 2027, page says April 2027.
- zimmer2016_2025 and gates_spam_2004: CANNOT_TELL is allowed by the plan. A plain reading would give WRONG for both (most households in large cities have a vehicle, spam stayed the majority of email in 2006). Caller's call, needs a cited record.
- legg_q1_2018: DID_NOT_HAPPEN also supportable.
- tesla_10kweek_2019: evidence quote is the S/X row, use the Total production row.
- moore_1965_cramming: CANNOT_TELL is conservative, Figure 1 of the 1975 paper (saved PDF) could decide it.
- Fortune verdicts for duell, olsen, gates_640k, decca, zanuck, simon_machines, watson, fisher, asimov rest on a named secondary that quotes the primary. The entries say so. Show "primary read by us: no" on the page.
- Copy scan (semicolons, judgement and cause words) of criterion, event, reason, summary, record, rule: only the items above. No mockery, politics or religion found.
- Independent checks that agree: Tesla quarterly sums (385,990 production, 367,656 deliveries), EIA crude series, 2000 census 281,421,906, Artemis I launch 16 Nov 2022, Artemis II April 2026, Webb launch 25 Dec 2021, IBM Eagle/Osprey/Condor dates, Minsky quote in Life PDF, Gates 1989 "about only 6 years", Metcalfe column and 1997 retraction as reported.
