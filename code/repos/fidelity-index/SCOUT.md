VERDICT: YES, a desk, but narrow. Best comparison: NCHS state divorce count/rate (state of occurrence, 45 states + DC) against the ACS 1-year "divorced in the last year" estimate (B12503, with margin of error) for the same state-year, per 1,000 population. Marriages (NCHS state count vs ACS B12501) is a clean second pair. NCHS provisional-vs-final is NOT usable: NCHS publishes one provisional series and never labels a final one.

Scout run 11 Nov 2026. Raw files and helper scripts are in /Users/heuremen/bones-forge/fidelity_index/ (raw/ holds the downloads). Nothing outside this folder was touched.

## 1. CDC NCHS National Vital Statistics System

Landing page: https://www.cdc.gov/nchs/nvss/marriage-divorce.htm

Files, all provisional, all with PDF and XLSX versions:
- Marriage rates by State, 1990, 1995, 2000-2024: https://www.cdc.gov/nchs/data/dvs/marriage-divorce/state-marriage-rates-90-95-00-24.xlsx
- Divorce rates by State, 1990, 1995, 2000-2024: https://www.cdc.gov/nchs/data/dvs/marriage-divorce/state-divorce-rates-90-95-00-24.xlsx
- Provisional number of marriages and marriage rate: United States, 2000-2024, and Provisional number of divorces and annulments and rate: United States, 2000-2024 (same workbook): https://www.cdc.gov/nchs/data/dvs/marriage-divorce/national-marriage-divorce-rates-00-24.xlsx
- State counts, 2000-2023 (PDF only, no XLSX found): https://cdc.gov/nchs/data/health_policy/Marriage-numbers-by-state-2000-2023.pdf and https://cdc.gov/nchs/data/health_policy/Divorce-numbers-by-state-2000-2023.pdf
- The 2024 state counts file was not found. The 2024 state rates exist, so counts can be backed out only approximately from rate times population.

Basis, from the file header: "Rates are based on provisional counts of divorces by state of occurrence. Rates are per 1,000 total population." Divorce footnote: "Includes annulments. Includes divorce petitions filed or legal separations for some counties or States."

Non-reporting states for divorce, 2024 file: California (blank for every year 2000-2024, last value 1990), Hawaii (blank since 2004; 2000-2003 present), Indiana (blank every year), Minnesota (blank since 2005; last value 2004), New Mexico (blank 2016-2024). That is five states, matching the CDC statement that the national divorce count covers 45 states plus DC. Louisiana is patchy (blank 2004-2012 apart from 2002-2003, present 2013-2024). Georgia is blank 2005-2016, present 2017 on.

Provisional vs final: there is no final series. The page says current rates come from provisional counts, the monthly provisional reports ended with the 2009 data, and detailed collection was suspended in January 1996. Revision check I ran: the 2022 vintage workbook (state-*-rates-90-95-00-22.xlsx) against the 2024 vintage, for 2020, 2021 and 2022. Zero state rates differ at the printed 0.1 precision. The file notes list only three revisions: Maryland 2021 rate, Texas 2016 rate, Illinois 2016 national marriage figure. So the revision reading is real but almost empty at this precision. It is a footnote row, not a desk. Only one vintage pair was available to me, and older vintages may sit in web archives.

Download format: XLSX and PDF, no API, no CSV. Population denominator is Census estimates (April 1 census years, July 1 otherwise).

## 2. Census American Community Survey

Tables, confirmed in the Census API group list: B12501 "Marriages in the Last Year by Sex by Marital Status for the Population 15 Years and Over", B12503 "Divorces in the Last Year by Sex by Marital Status for the Population 15 Years and Over" (also B12502 widowhood, B12505 times married, B12504 marriage duration). Variables: B12503_005 male divorced last year, B12503_010 female divorced last year, B12501_005 male married last year, B12501_010 female married last year, each with an _M margin (90% confidence).

Years: 1-year estimates exist for states for every year pulled (2022, 2023, 2024 confirmed). 2020 had no standard 1-year release (not re-verified here). 5-year tables exist for the same group but are not needed at state level.

Pulled from the table-based summary files, no API key needed: https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/1YRData/acsdt1y2023-b12503.dat (same pattern for 2022, 2024 and for b12501, b01003). The keyed API at api.census.gov refuses unkeyed calls (redirect to missing_key). A free key would make it cleaner.

Two ACS numbers per state-year: female count and male count. They should be near equal if the survey were exact. They are not, which is itself a width reading (Florida 2023: 79,000 women vs 64,100 men).

## 3. State vital records offices

- Pennsylvania: publishes. Marriage and Divorce Statistics PDFs, 2022 and 2023: https://health.pa.gov/topics/HealthStatistics/VitalStatistics/MarriageDivorce/Documents/Marriage_Divorce_2023.pdf and .../Marriage_Divorce_2022.pdf. Search summary of the state report: 2022 marriages 72,031 and divorces/annulments 29,101; 2023 marriages 69,288 and divorces/annulments 28,009, with Philadelphia County divorces missing in the 2023 report per that summary. Match to NCHS: divorces identical both years (29,101; 28,009). Marriages differ slightly (NCHS 72,091 vs state 72,031 for 2022; NCHS 69,242 vs state 69,288 for 2023). I did not open the PDFs myself, so verify the Philadelphia note before use. If Philadelphia is really missing from 2023, then NCHS 28,009 would carry the same hole.
- New York: publishes. Vital Statistics of New York State, Table 48 "Dissolutions of Marriage by County of Decree and Type of Decree", Table 51 "Divorces by County of Decree and Duration of Marriage", Table 47a marriages by county (excludes NYC): https://healthweb-back.health.ny.gov/statistics/vital_statistics/2022/table48.htm. 2022 state total dissolutions 44,313, divorces 44,222 (NYC 16,532). NCHS 2022: 44,420. Close, not identical. Marriage Table 47a is ex-NYC only so a state total needs NYC's own report. 2023 tables exist but the cache looked incomplete.
- Florida: publishes through FLHealthCHARTS query tools (MarriageQ, DissolutionQ), counts by county, daily provisional updates, "once a year is finalized, the term provisional is removed and that data will not change": https://www.flhealthcharts.gov/FLQUERY_New/Marriage/Count . Dissolution county is the county issuing the decree. This is the only place I found an explicit provisional/final flag. I could not pull 2022/2023 totals (interactive query). Needs a browser pull.
- Texas: DSHS posts marriage license and divorce decree indexes by year (https://www.dshs.texas.gov/vs/marr-div/indexes.aspx), described as not comprehensive, and does not publish annual state totals. I found only a 2014 annual figure (177,230 marriages). No usable match to NCHS.
- California: no divorce counts reach NCHS and I found no CDPH statewide divorce series. A BGSU monthly data project credits California 2017-2022 to personal communication with state staff. California marriages are in the NCHS table (2022: 223,006; 2023: 215,199).

## 4. Other official sources

- Bowling Green NCFMR Family Profiles (rebuild rates from ACS): Refined Marriage Rate FP-24-25 (2023), Refined Divorce Rate FP-24-26 (2023), Marriage-Divorce Ratio FP-24-27 (2023) and FP-25-32 (2024). https://www.bgsu.edu/ncfmr/resources/data/family-profiles/FP-24-26.html . 2023 national refined divorce rate 14.4 per 1,000 married women, Alaska highest 24.3, Vermont about 8; 2023 refined marriage rate 31.5 per 1,000 unmarried women. A university center, not an agency, but it is the same ACS source as section 2 with a different denominator (married women, not total population). It is a third reading of the same events, useful as a check on my ACS arithmetic. Its monthly 2017-2022 state marriage/divorce compilation cites state agencies by personal communication.
- NCHS National Survey of Family Growth (NSFG) and CPS marital history: not pulled. Both are national or regional survey samples with no state-level divorce counts, so they do not fit a state-year side-by-side. Not scouted further.

## 5. Side-by-side numbers (no labels)

Left: NCHS state-reported, by state of occurrence, from the 2000-2023 state count PDFs. Right: ACS 1-year, by residence of respondent, female and male persons, with 90% margin. Rates are per 1,000 total population (Census B01003 for ACS rows; NCHS rate is the printed state rate table, count check in brackets).

DIVORCE (NCHS includes annulments)

| State, year | NCHS count | NCHS rate | ACS women divorced last year | ACS rate (women count / population) | ACS men divorced last year |
|---|---|---|---|---|---|
| Texas 2022 | 56,269 | 1.9 | 89,194 +/- 6,115 | 2.97 +/- 0.20 | 84,520 +/- 6,154 |
| Texas 2023 | 62,796 | 2.1 | 94,986 +/- 6,586 | 3.11 +/- 0.22 | 82,108 +/- 6,507 |
| Florida 2022 | 69,683 | 3.1 | 69,400 +/- 5,484 | 3.12 +/- 0.25 | 63,454 +/- 4,657 |
| Florida 2023 | 66,958 | 3.0 | 79,000 +/- 5,982 | 3.49 +/- 0.26 | 64,100 +/- 5,501 |
| New York 2022 | 44,420 | 2.3 | 48,203 +/- 3,771 | 2.45 +/- 0.19 | 43,326 +/- 3,884 |
| New York 2023 | 47,585 | 2.4 | 52,164 +/- 4,225 | 2.67 +/- 0.22 | 43,623 +/- 3,837 |
| Pennsylvania 2022 | 29,101 | 2.2 | 32,766 +/- 3,436 | 2.53 +/- 0.26 | 30,779 +/- 3,377 |
| Pennsylvania 2023 | 28,009 | 2.2 | 32,320 +/- 3,490 | 2.49 +/- 0.27 | 30,209 +/- 2,961 |

ACS 2024 divorced last year, women: Texas 98,353 +/- 7,165; Florida 73,783 +/- 5,738; New York 47,357 +/- 4,012; Pennsylvania 34,844 +/- 3,360. NCHS 2024 printed rates: Texas 1.9, Florida 2.8, New York 2.3, Pennsylvania 2.1.

California divorce: NCHS has none. ACS women divorced last year 2022 94,652 +/- 5,566; 2023 104,529 +/- 5,534. This is a case where only one number exists, so no pair.

MARRIAGE

| State, year | NCHS count | NCHS rate (printed) | ACS women married last year | ACS men married last year | State office |
|---|---|---|---|---|---|
| Texas 2022 | 174,424 | | 229,790 +/- 10,804 | 240,585 +/- 11,716 | none |
| Texas 2023 | 178,055 | 5.8 | 233,654 +/- 8,435 | 240,102 +/- 10,417 | none |
| Florida 2022 | 158,978 | | 150,076 +/- 7,476 | 159,935 +/- 6,681 | not pulled |
| Florida 2023 | 158,790 | | 164,445 +/- 7,975 | 178,784 +/- 8,655 | not pulled |
| New York 2022 | 123,526 | | 123,941 +/- 5,834 | 138,265 +/- 6,659 | not pulled |
| New York 2023 | 126,938 | | 126,577 +/- 6,870 | 139,436 +/- 8,042 | not pulled |
| Pennsylvania 2022 | 72,091 | | 85,590 +/- 5,895 | 92,437 +/- 6,620 | 72,031 |
| Pennsylvania 2023 | 69,242 | | 85,201 +/- 5,871 | 90,534 +/- 5,784 | 69,288 |

(Only the 2023 Texas printed marriage rate was verified in the search result, 5.8; other printed rates are in the XLSX.) National NCHS: marriages 2,065,905 (2022), 2,041,926 (2023), 2,128,446 (2024); divorces and annulments 673,989 (2022), 672,502 (2023), 662,950 (2024).

The ACS figures are my own arithmetic from the published estimates: rate = women-divorced estimate divided by B01003 total population, margin = published margin divided by population, ignoring the population margin (small). Rates, counts and ACS values were checked once against the raw downloads in raw/ but not independently re-run. The NCHS count parse was checked against the printed rates (Texas 2022 56,269 for rate 1.9, 2023 62,796 for rate 2.1).

## 6. Terms of use and like-for-like problems

Terms: NCHS and Census output are US federal work and, as I understand, public domain with a request to cite. I did not find or quote a license page. NCHS asks users not to identify individuals (not an issue for aggregates). NCFMR pages are a university copyright, so quote numbers with credit and link, do not mirror. State sites: standard government sites. Florida's FLHealthCHARTS needs a data use agreement for anything beyond the public query tool. All state-level terms were not checked line by line and need a read before any republishing.

Why the pair is not like-for-like:
1. Place of occurrence vs place of residence. NCHS counts events where they were granted or licensed. ACS counts people who live in the state now. Nevada-style destination states and states with residency rules inflate NCHS. Pennsylvania's own page says counts are by occurrence.
2. Event vs person. A divorce is one event and two people. ACS women count and men count both estimate the same events and differ by 5 to 20 percent in these pulls. The pairing I used (women count) is a choice and the men count gives a different reading in several rows.
3. Reference period. ACS asks about "the last 12 months" before interview, so each annual estimate is a rolling window, not a calendar year. NCHS is calendar-year filings.
4. Annulments and petitions. NCHS divorce includes annulments, and for some states includes petitions filed or legal separations. ACS asks about divorce only.
5. Universe. ACS covers age 15 and over, ever married. NCHS rate denominator is total population. The like-for-like rate for ACS would be per 1,000 total population (what I used) or per 1,000 married people, not the NCHS rate.
6. Same-sex marriages. NCHS counts what the state reports with no uniform breakout. ACS includes them by respondent report.
7. Survey error. ACS is a 1-year sample with a 90% margin of roughly 6 to 8 percent on state divorce counts. Reading a gap of 1,000 events here means nothing. A fair reading needs the margin, and ACS margins are 90% not 95%.
8. Missing data. Five states report no divorces to NCHS. Pennsylvania 2023 reportedly lacks Philadelphia. Georgia, Louisiana, and others have blank runs. The national divorce count is 45 states plus DC, so it is not a national number.
9. Provisional status. NCHS never publishes a final count for these years. Florida says final data "will not change" once finalized, which would make a Florida provisional-vs-final reading possible only if the provisional snapshots had been saved. They are not saved by the state. A desk would need to start snapshotting now.
10. Population denominators differ by vintage (NCHS uses Census estimates, ACS uses its controlled population totals).

Open items before any build: confirm the PA 2023 Philadelphia gap from the PDF itself; pull Florida and New York 2022 and 2023 state totals from FLHealthCHARTS and the NY tables; get a free Census API key; decide whether to start snapshotting the NCHS XLSX on a schedule so a provisional-vs-revised reading exists in the future.
