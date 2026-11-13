# Referee B: Long Bets and Manifold resolved set (10 November 2026)

Verdict: FIX THEN SHIP. Nothing blocks ship. Fix-before-ship items listed below.

## Part 1. Long Bets (56 items checked, 8 dropped keys skipped)
- Quote verbatim in the raw page: 56 of 56 (whitespace and entities normalised). Script: referee/code/lb_check.py.
- Predictor name and badge side: all 19 concluded badges checked against the page layout (badge sits in the predictor or challenger block); every "who" is the predictor and every lb_result side matches. Script: referee/code/lb_struct.py.
- Deadline follows from the page Duration years (or the dated words for 395 and 712): 56 of 56.
- fixes_B.json: 24 ok, 32 fix.

Fix before ship
1. 26 prediction entries (10, 43, 317, 351, 426, 622, 638, 710, 795, 796, 832, 836, 838, 839, 842, 859, 873, 877, 931, 934, 951, 961, 973, 977, 886, 893): "challenger" holds page text ("Unchallenged ... Argument ..."). Set to null.
2. Bet 601: reading WRONG holds, but the evidence is a URL check on 10 Nov 2026, not the deadline. Use the Internet Archive post of 22 Feb 2022: "As of this writing, the URL absolutely has survived." (https://blog.archive.org/2022/02/22/a-long-bet-pays-off/).
3. Bet 367: reading WRONG holds, but the reason text "team member leaves the test open" is false. The page terms say "a member of the regular season roster of players". Rewrite criterion and reason.
4. Bet 712: reading WRONG holds; replace the Wikipedia Zoox evidence with TechCrunch 10 Sep 2025 ("For now, the Zoox robotaxi service currently offer rides for free.").
5. Bet 3: RIGHT rests on the badge. Netflix FY2010 10-K gives 20,010 thousand subscribers and profit, but no 10,000-title count was found. Add the count or read CANNOT_TELL.
6. Bet 763: no published VR viewer count exists; WRONG rests on the badge. CANNOT_TELL fits the plan rule.
7. Bet 765: RIGHT rests on the badge; no record of the share on throttled packages found. Add a dated record or CANNOT_TELL.

Notes (ok, label them)
- Bet 2 is contested (Long Now ruled for Winer; Cadenhead's tally of the same AP list was 3-2 for Winer; Long Now staff called the wording vague).
- Bet 5, 120 are absence readings. 120 has a positive record (Wikipedia: "Expert consensus is that allegations of the existence of Bigfoot are not credible.").
- Bet 9: badge is on the challenger (Pinker). The May 2022 terms give a Metaculus test on lab origin. CANNOT_TELL holds, reason text should say this. The six-month window can run past the 2020-12-31 start.
- Bet 12 (Nobel 2020 to Penrose, Genzel, Ghez), 117 (EIA 7.42 cents in 2003, 2005 higher), 197 (FHWA 3,009,218 vs 2,985,095 million VMT, the bet names BTS), 362 (S&P index fund beat all five funds-of-funds), 363, 382, 395: readings hold. Several lack a live-read quote: nobelprize.org returned 403, the Berkshire PDF is not machine-readable for me, the EIA archive page came back empty. Re-read them by hand before ship.
- Bet 687 verified live at BLS: 4.1 percent and 62.3 percent.
- Bet 750: Long Bets prints "Christof - Koch".
- 20 and 9 stay CANNOT_TELL, which is right.

## Part 2. Manifold resolved set
Own script: referee/code/recount_manifold.py (reads raw search files and bets files only).
- 5,657 unique resolved markets in raw. Rule applied: not binary 0, under 50 bettors 4,568, outside window 551, resolved CANCEL 16 and MKT 9, created under 30 days before reference 70, no bet before 2, read 441. Same counts as the researcher.
- Same 441 market ids, same resolutions, probabilities equal to 5e-7 (researcher rounds to 6 places). MATCH.
- Bins n = [180,70,30,35,17,17,15,17,23,37] and happened = [3,9,2,12,9,12,8,14,21,34]. Match. Brier 0.0935, base-rate Brier 0.2021 (base rate 0.2812), skill 0.5374. Match.
- Bin outcomes from my Wilson 95 percent: 0-0.1 BELOW (mean 0.048, share 0.017, interval 0.006-0.048), 0.1 CONSISTENT, 0.2 BELOW (n=30; mean 0.243, interval 0.019-0.213), 0.3 CONSISTENT, 0.4 to 0.8 CANNOT_TELL (n under 30), 0.9 CONSISTENT. Note the 0.2 bin sits at n=30 exactly, the first bin allowed to read, and its interval top (0.2132) is only just below the mean 0.2433.
- Live spot check of 5 markets (lp17jc8bxl, qZRLLPOhnl, vcGSnNu2644XxhBgSzM6, NypJd6LMEHq3ZqBNil9T, 9uzPCdRlAU) against the API: resolution and probAfter of the pre-moment bet identical to the file.

Things in the rule that could mislead (notes)
- uniqueBettorCount is today's count, not the count at the stated moment (the 50-bettor filter looks forward).
- The probability is the last bet's probAfter, which can be old: median 7 days before the moment, 84 of 441 more than 30 days old, max 290. 42 selected bets are limit-order records, 18 redemptions and 6 amount-0 bets (probAfter equals the market price, so harmless but not a trade).
- Manifold sets closeTime to the resolution time when resolved early (0 markets show resolution before close), so the earlier-of rule behaves as intended.
- 441 markets are not independent: top creators hold 22 (_deleted_), 20, 17, 16, 14 rows. Bin 0 (n=180, 3 happened) is dominated by long-shot "will X happen" markets. Median market life is 425 days, and the 30-day-before probability is often far from the creation price.
- Boundary values (0.2, 0.3, 0.5, 0.6 x3, 0.7 exactly) go up as the plan says; bin counts agree with and without float care.
