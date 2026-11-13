# ADSPEND referee report

Read-only refuting pass on the ADSPEND section of the SOCIAL desk: Google's stated US election-ad spend per advertiser set against matched FEC committees' reported payments to Google, cycles 2020 to 2026. Written 10 November 2026 UTC. Nothing in `social_index/adspend/` was edited.

Inputs read: `PLAN.md` (plan and five addenda, commits efd6696 to 9242f45), `adspend_tick.py` (07940ee), `data/raw/` as listed in `manifest.json` (Google bundle Last-Modified 9 Nov 2026 23:45:03 GMT, report data updated 2026-11-09 14:04:54 PT, FEC oppexp, cm, webk, weball and independent expenditure files for 2020 to 2026), `data/adspend.json`, `summary_adspend.json`, `section_adspend.html`.

Method: our own loader and recount engine, written from the plan text and run on the raw files only (`scripts/`). No code is shared with `adspend_tick.py`. The payee and purpose patterns were copied from PLAN.md, not from the tick. The cm treasurer field was never read. No individual contributor file was opened. Payee names were kept only for rows a broad Google-ish net caught, and a row coded to an individual keeps its name only when the name is a Google entity typed into a name field.

## Verdict: FIX THEN SHIP

The arithmetic holds. Our independent recount reproduces all 6,397 cycle rows: the same rows, the same outcome on the primary ruler, the second ruler and the unseen-in-full variant, the same windows, committee IDs and party fields, and every number to the cent except two rows whose differences move nothing. Every number on the page matches `summary_adspend.json` and `data/adspend.json`.

The page as built must not go out. Two of the six featured Below rows compare a federal committee with a Google advertiser that is another entity or another account. The Nothing returned column counts mostly rows that the plan's own definition excludes. Both are fixable without changing the design. Apply the fixes below, rerun the tick, then rerun `scripts/page_check.py` and `scripts/cmp_all.py` against the new outputs.

## What reproduces

Every cycle row: 6,397 of 6,397 rows match on outcome (primary, second ruler, unseen in full), window, committee ID and party field. Numbers match to two cents except:
- BOWMAN & BOWMAN 2024 (C00883157): D_lo 1,265 in the tick, 1,000 under the plan's payee words (the tick's extra word `\bADDS\b`, see the plan and code section). Outcome Cannot tell either way.
- AMERICA LEADS ACTION 2024 (C00864926): pool 9,993,533.27 in the tick, 9,992,010.77 ours. One superseded row survives because the tick applies the amendment rule after filtering. Outcome Cannot tell either way.

Featured rows and a seeded draw of six decided rows (seed 20261110, drawn from the 108 decided rows not featured), each rebuilt from the raw rows:

| Row | Google stated (band) | FEC Google rows | D_lo / D_hi | Unseen counted (in full) | Outcome (2nd ruler / unseen in full) |
|---|---|---|---|---|---|
| HARRIS VICTORY FUND 2024, C00744946 | 82,116,000 (71,653,300 to 82,124,200) | 20 rows "ONLINE FUNDRAISING", AD | 82,202,290.88 / same | 400 (365,504.92) | Cannot tell, near (same / same). Ad payments sit 78,091 over the band's top against a size of 8,212,420 |
| BIDEN VICTORY FUND 2020, C00744946 | 15,932,100 (13,363,300 to 15,934,200) | 6 rows "DIGITAL ADVERTISING", AD | 14,530,082.57 / same | 400 (28,095.83) | Consistent (Cannot tell / Consistent) |
| TRUMP SAVE AMERICA JFC 2022, C00770941 | 7,590,600 (5,913,600 to 7,603,700) | 19 rows "ONLINE ADVERTISING", AD | 10,405,151.72 / same | 400 (1,610.39) | Above (Above / Above), margin 2,801,452 against 760,370 |
| WARREN FOR PRESIDENT 2020, C00693234 | 3,050,100 (3,045,800 to 3,054,700) | 22 AD rows "DIGITAL MEDIA SERVICES" 4,845,804.07, 26 memo NONAD "SUBSCRIPTION" 50,460.30 | 4,845,804.07 / 4,896,264.37 | 400 (379,581.92) | Above (Above / Above) |
| CCAGW PAC 2024, C00391490 | 133,600 (133,200 to 134,000) | none. Summary: 640 disbursed, all contributions | 0 / 0, pool 0 | 0 | Below (Below / Below) |
| CARL DEMAIO FOR CONGRESS 2020, C00715029 (in the plan's record, not on the page) | 54,000 (53,400 to 54,700), window to 7 Dec 2020 | 49 memo rows "ONLINE ADS", AD | 54,000.00 / same | 400 (1,419.07) | Consistent (Consistent / Cannot tell) |
| ALEXANDRIA OCASIO-CORTEZ FOR CONGRESS 2020, C00639591 | 456,700 (393,400 to 466,000) | 425 rows (396 memo), AD 513,478.32 | 513,478.32 / 528,822.76 | 400 (55,350.55) | Above (Cannot tell / Above). Margin 47,478 against a size of 46,600 |
| DAVID OCAMPO GRAJALES FOR CONGRESS 2022, C00799858 | 2,300 (1,600 to 3,200) | 5 AD 1,970.57, 4 NONAD 193.34 | 1,970.57 / 2,163.91 | 400 (2,203.30) | Consistent (Cannot tell / Cannot tell) |
| BLACK MEN VOTE PAC 2024, C00528950 | 4,700 (400 to 5,200) | 2 AD rows "ADS - NOT CANDIDATE SPECIFIC" 60,120.76, 23 UNCLEAR 7,900.02 | 60,120.76 / 68,020.78 | 400 (2,346.46) | Above (Above / Above) |
| TROY CARTER FOR CONGRESS 2026, C00763649 | 0 (0 to 1,700) | 16 AD memo rows 43,767.49, 50 NONAD 5,639.28 | 43,767.49 / 49,406.77 | 418,731.80 (same) | Above (Above / Above) |
| MIDDLE GROUND 2026, C00952028, name match | 94,600 (94,100 to 95,100) | none, pool 53,724.80 | 0 / 0 | 124.95 | Below (Below / Below) |
| TRENT STAGGS FOR UTAH 2024, C00840934, name match | 10,000 (8,100 to 11,900) | 25 AD 9,540.78, 6 NONAD 834.96 | 9,540.78 / 10,375.74 | 400 (13,248.77) | Consistent (Cannot tell / Cannot tell) |

The plan's recount record (row counts, purposes and sums for the six named rows) is correct to the cent. Three rows in the draw carry problems taken up below: Black Men Vote PAC's Above rests on rows the committee labels not candidate-specific, Troy Carter 2026's Above has no Google spend in the window, and Middle Ground 2026's Below matches another account.

The page: every number checked against the summary and the data. Match paragraph (18,039, 4,361, 3,351, 1,010, 13,678, $1,330,810,600, 12,408, 1,249), the cycle table, the 2026 cut, the reasons line (2,387 and 2,281), all 38 committee rows cell by cell (name, ID, cycle, Google stated, band, ad rows to all rows, pool, outcome, reason, flags, name-match and related-committee labels), the selection of both tables, and both rulers. No mismatch. No semicolon in the rendered text.

## Issues

### Wrong-entity and wrong-account matches decide Below rows, two of them featured
Severity: blocks ship.

Evidence, row by row:
- HOUSE REPUBLICAN CAMPAIGN COMMITTEE, C00487678, Below in 2020, 2022 (featured) and 2024, name match. The Google advertiser (EIN 23-7290361, $630,500 from 2020 to 2026) served 99% of its spend in Michigan. The federal committee's filed address is Minnesota, it reports no Google row, and its 2020 receipts all came from other political committees ($87,000). Google lists the same exact name for three more advertisers, one registered in Michigan (US-MI 000436) and two in Pennsylvania. Addendum 2 dropped those three, and the EIN-listed one slipped through to the Minnesota committee.
- GREG FOR MONTANA, C00631945, Below 2020, ID plus name. All of the 2020 spend sits on an EIN-listed advertiser of that name ($56,300, 98% Montana, $31,800 of it in October 2020). The advertiser that listed the FEC ID states $2,900 in all, spent from June 2019 to January 2020. The committee's candidate ID H8MT01182 is a 2018 House candidacy and it reports $780 of Google rows in the window. The name match joined a different account to the federal committee.
- UNITING MISSOURI PAC, C00753392, Below 2020 (featured), name match. Google spend is 91% Missouri: $4,900 in March and April 2020, then $234,300 from August to November. The federal PAC's first itemized expenditure is 21 August 2020. Its rows are campaign workers, rent, payroll taxes and compliance, with no ad payment, and its total disbursements are $87,227. Google's figure starts five months before the federal PAC's first expenditure and is 2.7 times its total spending. The match is unconfirmed and the evidence points to another account.
- MIDDLE GROUND, C00952028, Below 2026, name match. Google spend is $94,600, 98% New Jersey, October and November 2025. The federal PAC first acts on 28 May 2026 (independent expenditures paid to a non-Google payee) and its first itemized row is 30 June 2026. Google also lists the name under a New Jersey state registration.
- JUSTICE 2020, C00715938, Below 2020, name match. Google spend is $1,900, 75% West Virginia, July to September 2020. The federal committee is a joint fundraising committee with a Washington DC address whose itemized rows are merchant fees, catering and compliance, and $1.17M of its $1.27M disbursed went to affiliates.
- MCKAYLA WILKES FOR CONGRESS, C00765412, Below 2020, ID match. The advertiser lists C00765412, whose candidate ID H2MD05536 is a 2022 candidacy, and whose 2020 candidate summary is all zero. Committee C00698563, of the same name, paid Google $53,876 in 116 rows in the 2020 window, against Google's $53,500 for the advertiser.
- KEEP AMERICA GREAT COMMITTEE (C00733519, 2020), ELECT LIBERTY (C00828665, 2024), NEW YORKERS FOR COMMON SENSE (C00890061, 2026), Below, all name matches. Each webk record has no coverage date and every total at zero, and each committee has no oppexp or independent expenditure row. The FEC holds no processed report for them, which is Nothing returned in substance, and the entity is unconfirmed (Elect Liberty: ads 95% New Hampshire against a Utah-addressed committee. New Yorkers for Common Sense: New York ads in June 2025 against a terminated Virginia-addressed joint fundraising committee. Keep America Great: the advertiser lists no ID).
- PRESERVE PROTECT AND DEFEND PAC, C00676213, Below 2020, ID plus name. All 2020 spend ($17,000, 79% Kentucky, May 2020) sits on the EIN-listed advertiser that matched by name. The advertiser that listed the FEC ID spent only in August 2025. The 2026 row rests on that ID-listed advertiser and stands.

The seeded draw of name matches agrees: of 10 random name matches, 7 are the same entity, 2 attach another committee (BAUGH FOR CONGRESS: 2024 ads matched to C00607432, a 2016 committee whose cm records end in 2020. SENATE MAJORITY FUND: Colorado ads from August to November 2020 matched to C00810762, which first appears in the 2022 committee file), and 1 is unresolved (NO KINGS PAC: ads 94% New Hampshire in August 2026, federal PAC addressed in Texas). ID and candidate-ID matches drew 10 of 10 same entity each.

Fix:
1. Google-side collision guard: an advertiser whose normalized name equals that of another Google advertiser carrying a state registration is unmatched. This catches 29 of the 1,010 name matches, including House Republican Campaign Committee and Middle Ground, and 10 Nothing returned rows (statewide campaign committees named like a federal committee of the same person, such as COOPER FOR NORTH CAROLINA, MILLS FOR MAINE and BETO FOR TEXAS).
2. A name match cannot decide Below on its own: if G_lo without the name-matched advertisers does not reach Below, the row reads Cannot tell. This catches the rest of the name-tier Below rows above. Name matches keep deciding Above and Consistent, where the committee's own Google rows link the two sides.
3. Cycle guard: a row whose matched committee is not in that cycle's cm file, or whose candidate ID is for a later election than the row's cycle, makes no row or reads Cannot tell. This catches McKayla Wilkes 2020.
4. An empty summary record (no coverage date, every total zero) counts as no summary.

### Nothing returned counts mostly rows the plan's definition excludes
Severity: blocks ship.

Evidence: PLAN.md defines Nothing returned as "Google states spend in the window and the FEC files hold no Schedule B row, no Schedule E row and no summary record". The tick tests `g1['hi'] > 0`, which counts weeks starting up to 98 days before the window opens and 31 days after it closes. Of the 170 Nothing returned rows, 93 have zero Google spend stated inside the window, 109 belong to committees absent from that cycle's cm file, 147 are one or the other, and 23 meet the definition in substance. By cycle the column reads 14, 51, 55 and 50, and the rows that are neither number 5, 9, 6 and 3. The page never defines Nothing returned.

Fix: test Google spend stated inside the window, as the plan says. Treat committees not registered in the cycle per the cycle guard above. Define Nothing returned on the page.

### Above where Google states nothing in the window
Severity: fix before ship.

Evidence: 19 of the 49 Above rows have Google stated spend 0 in the window, so the outcome follows from the $1,000 floor alone. All seven 2026 Above rows are of this kind. Google's weekly file has no gap in 2025 and 2026 (monthly totals run above the same months of 2021 and 2022), so these are not a data gap. Rows: CALIFORNIA REPUBLICAN PARTY FEDERAL ACCT. 2020, CASA IN ACTION PAC 2020, EMMER FOR CONGRESS 2020, GUN RIGHTS AMERICA 2020 and 2022, LISA BLUNT ROCHESTER FOR CONGRESS 2020, TEA PARTY PATRIOTS CITIZENS FUND 2020, DEMOCRATIC PARTY COMMITTEE ABROAD 2022, 2024 and 2026, NATIONAL FEDERATION OF INDEPENDENT BUSINESS FEDERAL PAC 2022, MASSACHUSETTS REPUBLICAN PARTY 2024, VERN BUCHANAN FOR CONGRESS 2024 and 2026, NEBRASKA REPUBLICAN PARTY 2026, OJEDA FOR NC 2026, TROY CARTER FOR CONGRESS 2026, WAGING PEACE 2026 (advertiser MIKE GALLAGHER FOR WISCONSIN, the same committee renamed), WORKERS VOTE 2026. The summary already counts them (`above_with_google_zero_in_window: 19`) but the page does not.

Fix: read these Cannot tell with the reason "Google lists no election ads for this advertiser in the window", or keep Above with that flag printed on the row and the count in the copy.

### Above on purchases outside the advertiser's election-ad record
Severity: fix before ship.

Evidence: the Above test has no counterpart to the pool and unseen terms that protect Below. Several Above rows show, in the committee's own purpose text, ads that may sit outside this advertiser's election-ad record. BLACK MEN VOTE PAC 2024: the whole D_lo is "ADS - NOT CANDIDATE SPECIFIC". NEW HAMPSHIRE DEMOCRATIC PARTY 2020: the whole D_lo is "DIGITAL ADVERTISING - NOT CANDIDATE SP[ECIFIC]". FOR OUR FUTURE 2020: the whole D_lo is "DIGITAL ADVERTISING - NO EXPRESS ADVOC[ACY]". WAY TO LEAD PAC 2020: "AD BUY (NON IE)". CASA IN ACTION PAC 2022 (featured): "NONFEDERAL DIGITAL ADVERTISING" and Pennsylvania electioneering ads. CASA IN ACTION PAC has a related advertiser, "CASA IN ACTION, INC." (EIN listed, name-matched into group C90015215, which reads scope). That advertiser states $124,500 in the 2020 possible window and $36,100 in 2022's. The PAC's 2020 D_lo is $99,615 of independent expenditures paid to Google plus $363 of Schedule B. Its 2022 Above clears the size by $5,844 (margin 21,234 against a size of 15,390), less than the related advertiser's $36,100. Refunds a committee receives from Google are Schedule A receipts, which no file read here holds, so D_lo is gross.

Fix: relabel CASA IN ACTION PAC 2020 (it is also in the zero-spend list). Flag CASA IN ACTION PAC 2022 with "a related advertiser states spend in the window" or take it off the featured table. Flag Above rows whose own purpose text says the ads were not candidate-specific or not express advocacy. State the Above-side limits in the copy (see the copy section).

### Above resting on filer estimates in 24- and 48-hour reports
Severity: fix before ship.

Evidence: the independent expenditure file holds 24- and 48-hour reports, and their amounts are often marked as estimates. Four Above rows fail Above once Schedule E rows whose purpose says estimate leave D_lo: GUN RIGHTS AMERICA 2020 (6,000 of 6,100 estimated) and 2022 (7,000 of 7,000), AMERICAN VALUES 2024 (D_lo falls from 8,950 to 1,500 against G_hi 6,600), FOR OUR FUTURE 2024 (three rows of "Digital Advertising (Estimate)", 30,000 of 30,000). The CASA IN ACTION PAC 2020 D_lo is $95,500 estimates out of $99,615.

Fix: Schedule E rows marked as estimates count in D_hi and not in D_lo, or the rows carry a flag. Either way the column header should not call estimates payments.

### Below and the pool of payments to others
Severity: fix before ship.

Evidence: the plan fixed the pool before the data as Schedule B rows whose purpose names ads, digital or media, plus Schedule E and party coordinated totals. Payments to card companies, reimbursements and consulting fees are outside it by design. In 9 of the 38 Below rows, card payments and reimbursements in the window alone are larger than the gap less the size: DEMOCRATIC STRATEGY INSTITUTE 2020 (cards $289,299 against a gap of $22,989) and 2022 ($265,289 against $119,200), GREG FOR MONTANA 2020, IHSSANE FOR CONGRESS 2020, MCMORRIS RODGERS WIN THE FUTURE FUND 2022 (cards $78,553 against $1,500, and the candidate's own committee C00390476 paid Google $4,878 in the window), NATIONAL DEMOCRATIC TRAINING COMMITTEE PAC 2022 (featured, cards $2,699,777 against $138,233), NOEM VICTORY FUND 2022, COMMITTEE TO ELECT JOE REAGAN 2024, FRIENDS OF SCHUMER 2024 (cards $401,802 against $7,835). In 7 more, consulting or fundraising payments are larger than the gap less the size. Committees must memo-itemize card vendors over $200, so these rows stay a measured difference. The copy, though, says payments to others could close the gap, which reads wider than the pool.

Fix: the copy sentence below, and a flag on the 9 card and reimbursement rows ("card payments or reimbursements could close the gap").

### Copy
Severity: fix before ship for items 1 to 6, note for items 7 to 11.

1. "Federal political committees report each payment they make to Google to the FEC." The page later relies on the rule that payments under $200 a year to a payee are not itemized. Replacement: "Federal political committees report their payments to the FEC, itemized by payee once a payee's total passes 200 dollars in a year, or in an election cycle for a candidate's committee."
2. "Those rows read Cannot tell unless even the payments to others cannot close the gap." Replacement: "Those rows read Cannot tell unless the committee's payments to others for ads, digital or media cannot close the gap either. Card payments, reimbursements and consulting fees are not counted in that pool."
3. The Above side is unexplained while the Below side is. Add: "Ads that Google does not class as election ads, ads that run under another advertiser's account and refunds a committee receives from Google appear only on the FEC side, so a committee's payments can exceed Google's figure."
4. Nothing returned is not defined. Add: "Nothing returned: Google states spend in the window and the FEC files hold no row and no summary for the committee in that cycle."
5. The intro says per quarter, but quarter rows appear nowhere on the page and `data/adspend.json` is not published (it is in `.gitignore`). The figures should say where they live. Link the data file the page reads from, or drop "and per quarter".
6. "Otherwise it counts up to 400 dollars, the most that the FEC's itemization rule leaves unitemized for one payee in a cycle." For a candidate's committee the rule's period is the election cycle. Replacement: "Otherwise it counts up to 400 dollars, the most the itemization rule can leave unitemized for one payee over two years (200 dollars a calendar year, or 200 dollars an election cycle for a candidate's committee)."
7. Consistent omits that ad payments must reach the bottom of the band. Replacement: "Consistent: ad payments to Google reach the bottom of the band, every payment to Google plus that unseen money stays under its top, and the band spans no more than a factor of two."
8. "Largest matched committees" and "The largest rows" carry an adjective and hide the sort key. Replacement headings: "Matched committees with the most Google stated spend, 2024 and 2026" and "Rows that read Consistent, Above or Below, with the most Google stated spend or ad payments, across all cycles".
9. "Committee names are as the FEC's committee file holds them today." Names come from each cycle's committee file (cm20 dated December 2024, cm22 to cm26 November 2026). Replacement: "as each cycle's committee file holds them on the day we read it".
10. "The plan, its sizes and its bands were committed before we compared any committee." The commits are local (no remote), the plan's first commit is stamped exactly 21:00:00, and the tick was first committed after run 5. A reader cannot check the sequence. Link the plan with its dated addenda, or say "written before" and link it.
11. "and 35 related committees named with it in Google's file". In the NRCC group, 4 of 35 members join only through other advertisers. "joined with it through Google's file" is exact. No decided row is in a multi-committee group.

Checks passed: no semicolon, no adjective about any committee, no cause named, the band is called a bound and not a confidence interval, party appears only in the closing sentence, and committee names are as filed.

### Plan and code disagree in places that move nothing
Severity: fix before ship (record it). No outcome moves.

- AD payee words: the tick adds `\*ADS|GOOGLEADS|ADS\d|ADWRDS|\bADDS\b` and `YOU TUBE` to the plan's AD payee pattern, and treats a payee that is both an AD and a NONAD product as neutral, under a comment that says "PLAN.md, verbatim patterns". Effect: one D_lo value (BOWMAN & BOWMAN 2024), no outcome.
- Schedule E mixed payees: the plan says a payee that also names another company never counts as an ad row. The tick puts every Schedule E Google row in D_lo. No outcome.
- The amendment rule runs after the Google and pool filter, so a superseded row survives when its amendment changed the purpose (AMERICA LEADS ACTION 2024, $1,522.50, "WEB SERVICES" amended to "BANK FEES"). One row in all matched committees, no outcome.
- The itemized total behind unseen is summed before the amendment rule. No outcome.
- The Schedule E deduplication ignores transaction IDs. WAY TO LEAD PAC 2020 counts an amended 24-hour entry twice ($1,000 original and $500 amendment of transaction VVAZQAQ6VM5). No outcome.
- The tick was first committed after run 5, so the code behind runs 1 to 4 is not recorded.

Fix: a dated addendum that records the payee words and the Schedule E reading, or revert them to the plan. Run the amendment rule before filtering. Commit the tick with each addendum.

### Addenda 4 and 5
Severity: note.

- The regulation is read correctly. 11 CFR 104.3(b)(3)(i), committees other than authorized committees: "Each person to whom an expenditure in an aggregate amount or value in excess of $200 within the calendar year is made by the reporting committee to meet the committee's operating expenses". 104.3(b)(4)(i), authorized committees: "in excess of $200 within the election cycle". Over a two-year window that bounds unitemized money to one payee at $400 (two calendar years, or at most two election cycles), as long as the committee itemized as required and Google is one legal payee. For a candidate's committee in the 18-month 2026 window the bound is $200, so $400 is loose in the safe direction.
- Threshold: 0.9 is ours and was defined after the data. Decided rows at other thresholds: 80% loses none and adds 2 (FRIENDS OF SCHUMER 2020 to Below, ALEXANDRIA OCASIO-CORTEZ FOR CONGRESS 2026 to Consistent). 85% adds 1. 95% loses 3 (FRIENDS OF SCHUMER 2024 Below, NATIONAL DEMOCRATIC TRAINING COMMITTEE PAC 2022 Below, DAVID OCAMPO GRAJALES FOR CONGRESS 2022 Consistent), all three already marked "depends on the itemization rule". 99% loses 16 and 100% loses 22 (Addendum 4). For a single-committee row the threshold only switches the cap on or off, which is what the flag compares, so the threshold can move only rows the flag already marks. No decided row is a multi-committee group.
- Cap: $200 adds 4 Consistent (DOUG WHITE FOR CONGRESS 2022, BIRD FOR CONGRESS 2024, ROYCE WHITE FOR CONGRESS 2022, CARL4CONGRESS, LLC 2020). $600 moves none. $800 loses 3 (CARL DEMAIO 2020, DICKINSON 2020, FRIENDS OF JASON WALTON 2024). $1,200 loses 6.
- Missing reports: none of the 55 decided rows where the cap applied has a quarter inside its active span with no itemized row and Google spend.
- The addendum's reason, that the remainder is mostly unitemized spending, fails for large remainders: NATIONAL DEMOCRATIC TRAINING COMMITTEE PAC 2022 $1,089,908, ALEXANDRIA OCASIO-CORTEZ FOR CONGRESS 2024 $578,485, DEVIN NUNES CAMPAIGN COMMITTEE 2020 $553,160, WARREN FOR PRESIDENT 2020 $379,582, FRIENDS OF SCHUMER 2024 $291,147. Sums that size would need thousands of payees under $200. They more likely sit on lines the operating-expenditure file leaves out (Form 3 line 21, Form 3X line 29). The bound still holds because ad buys belong on the operating lines, which must be itemized above $200. The committee-to-committee files (itpas2, itoth) are committee data, not contributor files, and could account for those lines and replace the threshold with a measured term.

### Timing band and the Cannot tell reasons
Severity: note.

- 36 decided rows depend on timing and say so. Above and Below can only get harder as the band widens, and a row that is Consistent under both rulers stays Consistent under any ruler between them. So no unflagged decided row changes for a ruler between 31/92 and 92/183 days. Narrower rulers were not tried and could only add decided rows.
- The Cannot tell reasons follow the stored numbers. Agency rows are wide by design (any committee buying through others). Harris Victory Fund 2024 reads near correctly.
- Rows forced into a decided outcome are the ones listed above: Above with no Google spend in the window, Above on estimates, Above on a related advertiser's account, Below on another entity or account, Below on an empty summary.
- Thin margins: ALEXANDRIA OCASIO-CORTEZ FOR CONGRESS 2020 (featured) clears the Above size by $878 (1.02 times) and carries "depends on timing". ANITA FOR ARIZONA 2020, EMMER FOR CONGRESS 2022, CATHOLICS FOR THE FUTURE 2024 and DEMOCRATIC PARTY COMMITTEE ABROAD 2026 clear it by 1.11 times or less.

### Payee rule
Severity: note.

- Across all committees, 84,351 oppexp rows carry a Google-ish payee (204 strings). The plan's rule catches 84,093 rows ($277,648,381, 169 strings).
- Google entities missed: "ALPHABET, INC." (the comma defeats `ALPHABET INC`, 17 rows $7,715), "ALPHABET" (2 rows $1,326), "GOODLE ADS" (6 rows $1,144), "GOGGLE WORKSPACE" (3 rows $540), "GMAIL" (1 row $313), "GOODLE DOMAINS" and "GOODLE LLC" ($18). About $11,056 in 32 rows. Adding them to the rule moves no outcome.
- Non-Google entities caught: nothing of weight. No agency with Google in its name appears among payees. "TOP OF GOOGLE-YAHOO-BING" is excluded as planned. Google Fiber is an Alphabet company and classes NONAD. "GOOGLE NET PAC" ($66, Google's own PAC) and "GOOGLE *PAY" card pass-through purchases ($1,600) are caught as NONAD Google rows, both trivial. "BOOMERANG FOR GMAIL" (a third-party add-on) is rightly not caught.

### Neutrality
Severity: fix before ship through the wrong-entity rows and the Above copy line, otherwise note.

- The method never reads the party field. It is stored and not used.
- Decided cycle rows by filed party: DEM 33 (Above 18, Below 5, Consistent 10), REP 33 (Above 11, Below 9, Consistent 13), blank 46 (20, 23, 3), IND 1 (Below). Decided share: DEM 1.4% of 2,301 rows, REP 1.7% of 1,958.
- Four of the nine REP Below rows are wrong-entity matches (House Republican Campaign Committee three times, Greg for Montana). One DEM Below (McKayla Wilkes) is the cycle mismatch. After those drops, Below reads DEM 4, REP 5. The name tier's failures fell on one side here because state caucus and statewide campaign committees share names with federal committees.
- Below has two shields (pool and unseen) and Above has none. Direct payments to Google are concentrated on DEM-filed committees in this data: $133.7M against $17.6M of Schedule B Google dollars in matched rows, and 68% of DEM rows against 42% of REP rows report any Google payment. So Above lands more on DEM-filed committees (18 against 11) and agency Cannot tell more on REP-filed ones (45% of their Cannot tell rows against 38%). Under the rules below, Above reads DEM 12, REP 4, blank 12. That is data composition passed through an asymmetric test. Copy item 3 keeps a reader from taking Above as a mark.
- Purpose classes: REP Google dollars are 84.4% AD and 13.6% NONAD, DEM 93.1% AD and 6.3% NONAD. This touches only D_lo (Above and Consistent), in the safe direction.

## The six checks, answered

1. Recount: the six named rows and six drawn rows (seed 20261110) reproduce exactly from raw, and so do all 6,397 cycle rows. Harris Victory Fund 2024 reads Cannot tell (near), not a decided row. Carl DeMaio 2020 is in the plan's record but not on the page.
2. Matching: ID 10 of 10 and candidate ID 10 of 10 are the same entity. Name: 7 of 10 the same, 2 wrong committee, 1 unresolved. Among decided rows, the name tier produced the wrong-entity Below rows listed above. The payee rule is sound: it misses about $11,056 of Google rows and catches nothing material that is not Google.
3. Addenda 4 and 5: the regulation is read correctly. The 0.9 threshold is arbitrary but moves only rows already flagged: at 80% none lost and 2 gained, at 95% 3 lost.
4. Timing and agency: the Cannot tell rows are honest and the timing flags cover every ruler between the two. Forced decided rows: Above with no Google spend in the window (19), Above on estimates (4, two of them also in the 19), Above on a related advertiser (CASA in Action PAC), and Below on wrong entities, wrong accounts, a cycle mismatch or empty summaries.
5. Neutrality: counts above. Party plays no part in the method. The side effects come through the name tier and the unshielded Above test.
6. The page: every number matches the summary and the data.

## Rows to drop or relabel

Drop (another entity, another account or another cycle's committee):
- HOUSE REPUBLICAN CAMPAIGN COMMITTEE, C00487678: 2020, 2022 (featured), 2024, Below
- GREG FOR MONTANA, C00631945: 2020, Below (remove the EIN-listed advertiser from the group and recompute)
- MIDDLE GROUND, C00952028: 2026, Below
- JUSTICE 2020, C00715938: 2020, Below
- MCKAYLA WILKES FOR CONGRESS, C00765412: 2020, Below

Relabel out of a decided outcome:
- UNITING MISSOURI PAC, C00753392: 2020, Below (featured), to Cannot tell, name match unconfirmed
- KEEP AMERICA GREAT COMMITTEE, C00733519 (2020), ELECT LIBERTY, C00828665 (2024), NEW YORKERS FOR COMMON SENSE, C00890061 (2026): Below, empty summary and unconfirmed name match
- PRESERVE PROTECT AND DEFEND PAC, C00676213: 2020 Below, to Cannot tell (all 2020 spend on a name-matched advertiser). The 2026 row stands.
- CASA IN ACTION PAC, C00685693: 2020 Above, to Cannot tell
- The 19 Above rows with no Google spend stated in the window, listed above, to Cannot tell with that reason (or a printed flag)
- AMERICAN VALUES 2024, C00821439 and FOR OUR FUTURE 2024, C00620971: Above on estimates, to Cannot tell (Gun Rights America 2020 and 2022 are in the 19)
- Nothing returned: the 147 rows with no Google spend in the window or no registration in the cycle

Flag on the page (outcome kept):
- CASA IN ACTION PAC 2022, Above (featured): a related advertiser states spend in the window
- Below with card payments or reimbursements larger than the gap: DEMOCRATIC STRATEGY INSTITUTE 2020 and 2022, IHSSANE FOR CONGRESS 2020, MCMORRIS RODGERS WIN THE FUTURE FUND 2022, NATIONAL DEMOCRATIC TRAINING COMMITTEE PAC 2022 (featured), NOEM VICTORY FUND 2022, COMMITTEE TO ELECT JOE REAGAN 2024, FRIENDS OF SCHUMER 2024
- Above whose own purpose text says not candidate-specific or not express advocacy: BLACK MEN VOTE PAC 2024, NEW HAMPSHIRE DEMOCRATIC PARTY 2020, FOR OUR FUTURE 2020, WAY TO LEAD PAC 2020

## What these rules would produce

Our rules for the rerun are: the name-match guards, the cycle guard, empty summary counted as no summary, Nothing returned as the plan defines it, Above only with Google spend in the window, and estimates out of D_lo. They are ours and were defined after the data, and each one can only move a row out of a decided outcome. Outcomes Above, Below, Consistent, Cannot tell, Nothing returned:

| Cycle | Now | With these rules |
|---|---|---|
| 2020 | 18, 10, 11, 1,111, 14 | 12, 3, 11, 1,133, 5 |
| 2022 | 11, 9, 7, 1,651, 51 | 8, 8, 7, 1,697, 9 |
| 2024 | 13, 12, 8, 1,631, 55 | 8, 10, 8, 1,687, 6 |
| 2026 | 7, 7, 0, 1,721, 50 | 0, 5, 0, 1,777, 3 |
| All | 49, 38, 26, 6,114, 170 | 28, 26, 26, 6,294, 23 |

The featured Below six would become NATIONAL DEMOCRATIC TRAINING COMMITTEE PAC 2022, PLANNED PARENTHOOD ACTION FUND INC PAC 2022, DEMOCRATIC STRATEGY INSTITUTE 2022, CCAGW PAC 2024, DEMOCRATIC STRATEGY INSTITUTE 2020 and IOWA VALUES 2020. The featured Above and Consistent rows stay as they are, apart from the CASA in Action PAC 2022 flag.

## Reproduce

From `~/bones-forge/social_index/adspend_referee/scripts/`, run each script with `python3 -I`:
- `load_raw.py`: about 30 seconds, writes `raw_cache.pkl` (about 860 MB) in this folder, regenerable, delete after use
- `cmp_all.py`: full recount and diff against `data/adspend.json`
- `recount_rows.py`: named rows and the seeded draw
- `variants.py`: payee words, Schedule E mixed payees, amendment total, threshold and cap sweeps
- `match_audit.py`: seeded match draws and every decided row with a name match (writes `geo.pkl`)
- `below_detail.py`: unseen inputs for Below and Consistent rows
- `audits.py`: payee rule, Nothing returned, party counts, payments outside the pool behind each Below row
- `proposed.py`: what the rules above produce
- `page_check.py [adspend folder]`: every page number against the summary and the data (rerun after each tick)

Seed 20261110 drives both draws.
