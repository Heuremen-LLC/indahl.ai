# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-11 pre-seal log: what was looked at before PLAN.md was committed (commit b11e6aa)
- Scout (census_scout/SCOUT.md item 5) printed California, Texas, Arkansas values across V2019, V2020, V2022 to V2025 and the census count. Disclosed in PLAN.md.
- Copied from census_scout/raw into data/raw: nst-est2019-alldata.csv, nst-est2020.csv, NST-EST2022 to 2025-ALLDATA.csv, census2020_pl_state.json. Column headers of V2019, V2020, V2022 and V2025 printed.
- Pulled with census_scout/cget.sh (key read at call time, never printed or stored): api 2021/pep/population (get NAME,POP_2020,POP_2021, 52 rows, saved data/raw/api2021.json) and api 2019/pep/population (get NAME,POP,DATE_CODE, 625 rows, saved data/raw/api2019.json). First 8 lines of each were printed (Oklahoma, Nebraska, Hawaii, South Dakota, Tennessee, Nevada, New Mexico in 2021, Alabama date codes 1 to 8 in 2019). Date codes found: 1 to 12.
- Two guessed URLs for a V2021 flat file (www2.census.gov .../datasets/2020-2021/state/totals/NST-EST2021-ALLDATA.csv and the lower case name) returned 404, so V2021 comes from the API only.
- Census count: Alabama 5,024,279 printed, 52 rows in the file.
- Not looked at: any later minus earlier difference, any outcome, any count, the PES values for this desk.

## 2026-11-11 CENSUS VINTAGES desk first read (draft page, not shipped, no ledger rows)
- I: holds: plan commit b11e6aa 13:22:43 -05:00, sha256 c99073f1, data/plan_seal.json, first run after the seal. 2,550 rows, frame 51 areas. Class A 2,040 rows CANNOT_TELL no width by rule, B 255 rows (41 ABOVE, 5 BELOW, 209 CONSISTENT), C 51 rows (9, 1, 41), D 204 rows all CONSISTENT.
- Gates all passed: format and frame, API 2019 equals the flat file for 510 values, census total 331,449,281, 24 hand-read scout values equal, PES SE equal to API for 51 areas, rule synthetic rows, kit self-test.
- Not done: V2021 has no flat-file cross-check and no estimates base (API only). Not rendered in a browser. lint_copy.py gives 0 hits. Code committed after the first reading.

## 2026-11-11 post-referee fixes (outside referee recount: every count right, none changed). Copy and display only, the sealed rule and every sealed outcome are unchanged. summary_vintages.json counts are the same.
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: sealed counts rerun and identical (ABOVE 50, BELOW 6, CONSISTENT 454, CANNOT_TELL 2040). Plan commit b11e6aa and sha256 unchanged
- II: n/a: no repeated item
- III: holds: ABOVE and BELOW still printed apart, CANNOT_TELL its own column
- V: holds: the sealed ruler is untouched. Added a second ruler centered on each state published net coverage error (outside 1.645 times the standard error), labelled as added after the referee. April estimate against the count reads 11 ABOVE and 5 BELOW (16 states) against the sealed 9 ABOVE and 1 BELOW (10 states). July 2020 Vintage 2020 against Vintage 2025 reads 11 ABOVE and 6 BELOW against the sealed 8 and 1. Both counts and both state lists are printed side by side on the page. The sealed rule stays the lead
- VI: holds: four outcomes kept
- R: fixed: MUST 1 the lead is now the finding sentence with a label slot (8 states above, 1 below, 42 inside, none CANNOT_TELL). MUST 2 the width section says the yardstick is centered on zero, ignores each published net coverage error, is the survey sampling error for household population, and that V2020 to V2021-2025 is the same gap as the April comparison with later components. MUST 3 page says no headline was named in the plan, the latest Vintage was chosen after the run, and V2021 reads 9 ABOVE, 1 BELOW, 41 CONSISTENT. MUST 4 class D reads inside by construction, widest gap and smallest yardstick computed from the summary, the expected-to-sit line dropped. SHOULD 5 signed medians and down and up counts beside the magnitude medians, labelled. SHOULD 6 class A yardstick-unit column and the value-under-one sentence removed. SHOULD 7 softer wording, stated and delivered no longer used for the readings. SHOULD 8 gate for the V2021 sums (331,501,080 and 331,893,745) added to the join gate, passed, and a page line says V2021 has no flat-file check beyond it. SHOULD 9 class A note that each cell pools the years the pair shares. Nits: tiny changes print as under 0.01 percent in size, data/raw/t.csv (a saved 404 page) deleted, the sensitivity column names CONSISTENT. lint_copy.py 0 hits. Render in a browser: see the ship record.

## 2026-11-11 13:31 CENSUS VINTAGES desk ship record: every printed table row and number as shipped (durable source for the censusvin.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from census_vintages.html as built from summary_vintages.json of the run at 2026-11-11T18:30:56Z, and make_rows.py asserts the table rows against the cells and 51 states
- II: n/a: a table copied as shipped, no comparison between runs
- III: holds: ABOVE and BELOW are separate columns, CANNOT_TELL has its own column
- V: holds: sealed ruler 1.645 times the published survey standard error centered on zero, second ruler centered on the published net coverage error, both printed
- VI: holds: the four outcomes are on the page with the counts as the summary holds them
- R: holds: counts and values from the summary of 2026-11-11T18:30:56Z, no number typed by hand
- P1: n/a: no quoted text in this record
- P2: holds: each line carries the cell or state name and the columns the page prints
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: the interval is ours and the page says so
- P6: holds: the lines say what the table says and nothing stronger
- P7: holds: ledger rows added staged and flipped to live in the ship lock, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
vin-record censusvin.cell.a.v2019-to-v2020: V2019 to V2020 510 0 0 0 510 0.043 0.041 32 down, 478 up District of Columbia 2018, 0.37 percent
vin-record censusvin.cell.a.v2021-to-v2022: V2021 to V2022 102 0 0 0 102 0.077 0.061 21 down, 81 up District of Columbia 2020, -2.79 percent
vin-record censusvin.cell.a.v2021-to-v2023: V2021 to V2023 102 0 0 0 102 0.085 0.069 22 down, 80 up District of Columbia 2020, -2.79 percent
vin-record censusvin.cell.a.v2021-to-v2024: V2021 to V2024 102 0 0 0 102 0.094 0.076 18 down, 84 up District of Columbia 2020, -2.78 percent
vin-record censusvin.cell.a.v2021-to-v2025: V2021 to V2025 102 0 0 0 102 0.085 0.072 20 down, 82 up District of Columbia 2020, -2.77 percent
vin-record censusvin.cell.a.v2022-to-v2023: V2022 to V2023 153 0 0 0 153 0.010 0.007 42 down, 111 up Connecticut 2020, -0.55 percent
vin-record censusvin.cell.a.v2022-to-v2024: V2022 to V2024 153 0 0 0 153 0.037 0.027 21 down, 132 up District of Columbia 2022, 0.73 percent
vin-record censusvin.cell.a.v2022-to-v2025: V2022 to V2025 153 0 0 0 153 0.038 0.031 24 down, 129 up Florida 2022, 0.76 percent
vin-record censusvin.cell.a.v2023-to-v2024: V2023 to V2024 204 0 0 0 204 0.051 0.035 19 down, 184 up Florida 2023, 1.30 percent
vin-record censusvin.cell.a.v2023-to-v2025: V2023 to V2025 204 0 0 0 204 0.047 0.036 37 down, 167 up Florida 2023, 1.41 percent
vin-record censusvin.cell.a.v2024-to-v2025: V2024 to V2025 255 0 0 0 255 0.031 -0.004 154 down, 101 up District of Columbia 2024, -1.56 percent
vin-record censusvin.cell.bc.v2020-to-v2021-july-1-2020: V2020 to V2021, July 1 2020 51 9 1 41 0 0.833 0.520 13 down, 38 up At one times the standard error, 13 ABOVE, 3 BELOW, 35 CONSISTENT. At two times, 4 ABOVE, 1 BELOW, 46 CONSISTENT. New Jersey 4.47 percent
vin-record censusvin.cell.bc.v2020-to-v2022-july-1-2020: V2020 to V2022, July 1 2020 51 8 1 42 0 0.854 0.573 13 down, 38 up At one times the standard error, 13 ABOVE, 4 BELOW, 34 CONSISTENT. At two times, 4 ABOVE, 1 BELOW, 46 CONSISTENT. District of Columbia -5.88 percent
vin-record censusvin.cell.bc.v2020-to-v2023-july-1-2020: V2020 to V2023, July 1 2020 51 8 1 42 0 0.835 0.578 13 down, 38 up At one times the standard error, 14 ABOVE, 4 BELOW, 33 CONSISTENT. At two times, 4 ABOVE, 0 BELOW, 47 CONSISTENT. District of Columbia -5.89 percent
vin-record censusvin.cell.bc.v2020-to-v2024-july-1-2020: V2020 to V2024, July 1 2020 51 8 1 42 0 0.836 0.596 13 down, 38 up At one times the standard error, 14 ABOVE, 4 BELOW, 33 CONSISTENT. At two times, 4 ABOVE, 0 BELOW, 47 CONSISTENT. District of Columbia -5.88 percent
vin-record censusvin.cell.bc.v2020-to-v2025-july-1-2020: V2020 to V2025, July 1 2020 51 8 1 42 0 0.840 0.594 13 down, 38 up At one times the standard error, 14 ABOVE, 4 BELOW, 33 CONSISTENT. At two times, 4 ABOVE, 0 BELOW, 47 CONSISTENT. District of Columbia -5.87 percent
vin-record censusvin.cell.bc.v2020-april-1-2020-to-the-census-count: V2020 April 1 2020 to the census count 51 9 1 41 0 0.851 0.540 14 down, 37 up At one times the standard error, 13 ABOVE, 3 BELOW, 35 CONSISTENT. At two times, 4 ABOVE, 1 BELOW, 46 CONSISTENT. New Jersey 4.48 percent
vin-record censusvin.cell.sr.v2020-april-1-2020-to-the-census-count: April 1 2020 estimate of Vintage 2020 against the count 9 ABOVE, 1 BELOW, 41 CONSISTENT Above: Alabama, Hawaii, Illinois, Massachusetts, New Jersey, New York, Pennsylvania, Rhode Island and Vermont. Below: Arizona. 11 ABOVE, 5 BELOW, 35 CONSISTENT Above: Alabama, Arkansas, Florida, Idaho, Illinois, Maryland, Mississippi, New Jersey, Pennsylvania, Tennessee and Texas. Below: Arizona, Colorado, Delaware, Hawaii and Minnesota.
vin-record censusvin.cell.sr.v2020-to-v2025-july-1-2020: July 1 2020, Vintage 2020 against Vintage 2025 8 ABOVE, 1 BELOW, 42 CONSISTENT Above: Alabama, Hawaii, Illinois, New Jersey, New York, Pennsylvania, Rhode Island and Vermont. Below: Arizona. 11 ABOVE, 6 BELOW, 34 CONSISTENT Above: Alabama, Arkansas, Florida, Idaho, Illinois, Maryland, Mississippi, New Jersey, Pennsylvania, Tennessee and Texas. Below: Arizona, Colorado, Delaware, District of Columbia, Hawaii and Minnesota.
vin-record censusvin.cell.d.census-count-to-v2022-estimates-base: census count to V2022 estimates base 51 0 0 51 0 0.000 0.000 23 down, 28 up At one times the standard error, 0 ABOVE, 0 BELOW, 51 CONSISTENT. At two times, 0 ABOVE, 0 BELOW, 51 CONSISTENT. Montana under 0.01 percent in size
vin-record censusvin.cell.d.census-count-to-v2023-estimates-base: census count to V2023 estimates base 51 0 0 51 0 0.001 0.000 22 down, 28 up At one times the standard error, 0 ABOVE, 0 BELOW, 51 CONSISTENT. At two times, 0 ABOVE, 0 BELOW, 51 CONSISTENT. Arizona 0.09 percent
vin-record censusvin.cell.d.census-count-to-v2024-estimates-base: census count to V2024 estimates base 51 0 0 51 0 0.003 0.002 12 down, 38 up At one times the standard error, 0 ABOVE, 0 BELOW, 51 CONSISTENT. At two times, 0 ABOVE, 0 BELOW, 51 CONSISTENT. Arizona 0.09 percent
vin-record censusvin.cell.d.census-count-to-v2025-estimates-base: census count to V2025 estimates base 51 0 0 51 0 0.004 0.004 11 down, 38 up At one times the standard error, 0 ABOVE, 0 BELOW, 51 CONSISTENT. At two times, 0 ABOVE, 0 BELOW, 51 CONSISTENT. Arizona 0.09 percent
vin-record censusvin.state.alabama: Alabama 4,920,706 5,024,279 1.22 2.10 ABOVE 4,921,532 5,032,962 ABOVE, 2.26 percent
vin-record censusvin.state.alaska: Alaska 732,074 733,391 2.45 0.18 CONSISTENT 731,158 732,906 CONSISTENT, 0.24 percent
vin-record censusvin.state.arizona: Arizona 7,393,900 7,151,502 1.59 -3.28 BELOW 7,421,401 7,186,647 BELOW, -3.16 percent
vin-record censusvin.state.arkansas: Arkansas 3,029,672 3,011,524 2.21 -0.60 CONSISTENT 3,030,522 3,014,399 CONSISTENT, -0.53 percent
vin-record censusvin.state.california: California 39,418,894 39,538,223 0.65 0.30 CONSISTENT 39,368,078 39,527,808 CONSISTENT, 0.41 percent
vin-record censusvin.state.colorado: Colorado 5,798,266 5,773,714 1.45 -0.42 CONSISTENT 5,807,719 5,786,873 CONSISTENT, -0.36 percent
vin-record censusvin.state.connecticut: Connecticut 3,561,494 3,605,944 1.71 1.25 CONSISTENT 3,557,006 3,579,643 CONSISTENT, 0.64 percent
vin-record censusvin.state.delaware: Delaware 984,899 989,948 2.82 0.51 CONSISTENT 986,809 991,890 CONSISTENT, 0.51 percent
vin-record censusvin.state.district-of-columbia: District of Columbia 712,185 689,545 4.93 -3.18 CONSISTENT 712,816 670,958 CONSISTENT, -5.87 percent
vin-record censusvin.state.florida: Florida 21,688,239 21,538,187 0.91 -0.69 CONSISTENT 21,733,312 21,591,325 CONSISTENT, -0.65 percent
vin-record censusvin.state.georgia: Georgia 10,695,662 10,711,908 1.11 0.15 CONSISTENT 10,710,017 10,732,595 CONSISTENT, 0.21 percent
vin-record censusvin.state.hawaii: Hawaii 1,410,587 1,455,271 1.68 3.17 ABOVE 1,407,006 1,451,130 ABOVE, 3.14 percent
vin-record censusvin.state.idaho: Idaho 1,818,238 1,839,106 1.62 1.15 CONSISTENT 1,826,913 1,849,328 CONSISTENT, 1.23 percent
vin-record censusvin.state.illinois: Illinois 12,615,162 12,812,508 0.89 1.56 ABOVE 12,587,530 12,795,348 ABOVE, 1.65 percent
vin-record censusvin.state.indiana: Indiana 6,752,183 6,785,528 0.94 0.49 CONSISTENT 6,754,953 6,790,290 CONSISTENT, 0.52 percent
vin-record censusvin.state.iowa: Iowa 3,164,115 3,190,369 3.25 0.83 CONSISTENT 3,163,561 3,191,081 CONSISTENT, 0.87 percent
vin-record censusvin.state.kansas: Kansas 2,915,024 2,937,880 1.42 0.78 CONSISTENT 2,913,805 2,938,274 CONSISTENT, 0.84 percent
vin-record censusvin.state.kentucky: Kentucky 4,477,899 4,505,836 1.50 0.62 CONSISTENT 4,477,251 4,508,271 CONSISTENT, 0.69 percent
vin-record censusvin.state.louisiana: Louisiana 4,650,984 4,657,757 2.36 0.15 CONSISTENT 4,645,318 4,652,145 CONSISTENT, 0.15 percent
vin-record censusvin.state.maine: Maine 1,349,647 1,362,359 1.90 0.94 CONSISTENT 1,350,141 1,364,546 CONSISTENT, 1.07 percent
vin-record censusvin.state.maryland: Maryland 6,059,529 6,177,224 1.41 1.94 CONSISTENT 6,055,802 6,178,387 CONSISTENT, 2.02 percent
vin-record censusvin.state.massachusetts: Massachusetts 6,898,116 7,029,917 1.06 1.91 ABOVE 6,893,574 6,985,320 CONSISTENT, 1.33 percent
vin-record censusvin.state.michigan: Michigan 9,976,330 10,077,331 0.68 1.01 CONSISTENT 9,966,555 10,072,294 CONSISTENT, 1.06 percent
vin-record censusvin.state.minnesota: Minnesota 5,655,855 5,706,494 0.97 0.90 CONSISTENT 5,657,342 5,710,562 CONSISTENT, 0.94 percent
vin-record censusvin.state.mississippi: Mississippi 2,971,253 2,961,279 1.63 -0.34 CONSISTENT 2,966,786 2,958,385 CONSISTENT, -0.28 percent
vin-record censusvin.state.missouri: Missouri 6,151,737 6,154,913 0.97 0.05 CONSISTENT 6,151,548 6,155,074 CONSISTENT, 0.06 percent
vin-record censusvin.state.montana: Montana 1,078,405 1,084,225 3.70 0.54 CONSISTENT 1,080,577 1,087,156 CONSISTENT, 0.61 percent
vin-record censusvin.state.nebraska: Nebraska 1,937,258 1,961,504 1.35 1.25 CONSISTENT 1,937,552 1,963,318 CONSISTENT, 1.33 percent
vin-record censusvin.state.nevada: Nevada 3,128,500 3,104,614 3.44 -0.76 CONSISTENT 3,138,259 3,116,851 CONSISTENT, -0.68 percent
vin-record censusvin.state.new-hampshire: New Hampshire 1,365,533 1,377,529 1.58 0.88 CONSISTENT 1,366,275 1,378,752 CONSISTENT, 0.91 percent
vin-record censusvin.state.new-jersey: New Jersey 8,890,883 9,288,994 0.93 4.48 ABOVE 8,882,371 9,270,476 ABOVE, 4.37 percent
vin-record censusvin.state.new-mexico: New Mexico 2,106,117 2,117,522 2.42 0.54 CONSISTENT 2,106,319 2,118,446 CONSISTENT, 0.58 percent
vin-record censusvin.state.new-york: New York 19,382,373 20,201,249 0.94 4.22 ABOVE 19,336,776 20,122,262 ABOVE, 4.06 percent
vin-record censusvin.state.north-carolina: North Carolina 10,581,885 10,439,388 1.09 -1.35 CONSISTENT 10,600,823 10,450,215 CONSISTENT, -1.42 percent
vin-record censusvin.state.north-dakota: North Dakota 765,224 779,094 1.86 1.81 CONSISTENT 765,309 779,612 CONSISTENT, 1.87 percent
vin-record censusvin.state.ohio: Ohio 11,699,855 11,799,448 0.67 0.85 CONSISTENT 11,693,217 11,798,534 CONSISTENT, 0.90 percent
vin-record censusvin.state.oklahoma: Oklahoma 3,977,682 3,959,353 1.89 -0.46 CONSISTENT 3,980,783 3,965,243 CONSISTENT, -0.39 percent
vin-record censusvin.state.oregon: Oregon 4,237,408 4,237,256 1.22 -0.00 CONSISTENT 4,241,507 4,243,544 CONSISTENT, 0.05 percent
vin-record censusvin.state.pennsylvania: Pennsylvania 12,794,404 13,002,700 0.67 1.63 ABOVE 12,783,254 12,995,576 ABOVE, 1.66 percent
vin-record censusvin.state.rhode-island: Rhode Island 1,058,004 1,097,379 1.43 3.72 ABOVE 1,057,125 1,096,487 ABOVE, 3.72 percent
vin-record censusvin.state.south-carolina: South Carolina 5,205,864 5,118,425 1.26 -1.68 CONSISTENT 5,218,040 5,131,992 CONSISTENT, -1.65 percent
vin-record censusvin.state.south-dakota: South Dakota 891,688 886,667 1.87 -0.56 CONSISTENT 892,717 887,808 CONSISTENT, -0.55 percent
vin-record censusvin.state.tennessee: Tennessee 6,875,939 6,910,840 1.51 0.51 CONSISTENT 6,886,834 6,927,736 CONSISTENT, 0.59 percent
vin-record censusvin.state.texas: Texas 29,286,467 29,145,505 0.82 -0.48 CONSISTENT 29,360,759 29,237,895 CONSISTENT, -0.42 percent
vin-record censusvin.state.utah: Utah 3,239,542 3,271,616 1.23 0.99 CONSISTENT 3,249,879 3,283,970 CONSISTENT, 1.05 percent
vin-record censusvin.state.vermont: Vermont 623,821 643,077 1.83 3.09 ABOVE 623,347 642,965 ABOVE, 3.15 percent
vin-record censusvin.state.virginia: Virginia 8,587,217 8,631,393 1.11 0.51 CONSISTENT 8,590,563 8,637,303 CONSISTENT, 0.54 percent
vin-record censusvin.state.washington: Washington 7,678,379 7,705,281 1.08 0.35 CONSISTENT 7,693,612 7,726,812 CONSISTENT, 0.43 percent
vin-record censusvin.state.west-virginia: West Virginia 1,788,150 1,793,716 4.40 0.31 CONSISTENT 1,784,787 1,791,670 CONSISTENT, 0.39 percent
vin-record censusvin.state.wisconsin: Wisconsin 5,833,464 5,893,718 0.86 1.03 CONSISTENT 5,832,655 5,897,371 CONSISTENT, 1.11 percent
vin-record censusvin.state.wyoming: Wyoming 582,030 576,851 2.01 -0.89 CONSISTENT 582,328 577,669 CONSISTENT, -0.80 percent
vin-record censusvin.headline: July 1 2020, Vintage 2025 against Vintage 2020: 8 ABOVE, 1 BELOW, 42 CONSISTENT, 0 CANNOT_TELL
vin-record censusvin.lead: For July 1 2020, the Vintage 2025 figure sits above the Vintage 2020 figure by more than the survey yardstick in 8 states, below it in 1 and inside it in 42
vin-record censusvin.v2021: Against Vintage 2021 the same July 1 2020 comparison reads 9 ABOVE, 1 BELOW and 41 CONSISTENT
vin-record censusvin.v2021sums: add to 331,501,080 and its 51 values for July 1 2021 add to 331,893,745
vin-record censusvin.d: The widest gap between the base and the count is 0.09 percent, against yardsticks of 1.1 percent and up
vin-record censusvin.nowidth: every comparison between two Vintages on the same base is read CANNOT_TELL with the reason no width
vin-record censusvin.frame: The frame is the 50 states and the District of Columbia
