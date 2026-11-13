
## 2026-10-30 10:43 Site pass H-22: EIA Adjustment line dropped from the utility table, next utility enters (Interstate Power and Light)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the table is the forty largest utilities by sales from the same EIA-861 file, the Adjustment line is EIA's balancing entry and not a utility
- II: n/a: no difference is netted, rows are listed as EIA prints them
- III: n/a: sales figures without a sign or a direction
- V: holds: the ruler is EIA's own sales figure, unchanged
- VI: n/a: a list of official figures, no outcome word on these rows
- R: holds: the new row's figures read from atlas/electricity/rows_text.txt as the build writes them from EIA-861
- P1: n/a: the rows carry no quotes
- P2: holds: the page names EIA-861 and the year
- P3: holds: the providers note already says the Adjustment entry is not a provider, the table now agrees
- P4: n/a: no cause is named for any figure
- P5: n/a: the table carries no intervals
- P6: holds: no summary sentence changed
- P7: holds: ledger row withdrawn and the new row added before the build
- P8: cannot tell: the rendered page is checked after the release build
- P9: holds: plain table cells
- P10: n/a: nothing here was defined after the data

## 2026-10-30 11:41 ATLAS one switchable map and the cost-to-scale arithmetic (Epoch AI stated power x 8,760 h x EIA-861 2024 state industrial price), plus the Google Papillion placement corrected at the source (Kansas 237 to 0 MW, Nebraska 458 to 695 MW)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no none or comparison arm; the figure is a product of published figures, stated as arithmetic on the page
- II: n/a: no gap is netted; each site's cost is printed on its own row with the total beside it
- III: n/a: no sign or direction words; costs are positive products
- V: holds: two rulers side by side, the EIA-861 2024 state industrial price for the headline and the commercial price beside it (7,419.0 and 10,807.1 million dollars)
- VI: n/a: no outcome words; sites with no stated power or no state are listed apart, not dropped (3 with power, 449 MW, and 8 unplaced)
- R: holds: Bones recomputed the 57-site total from scale.json with exact fractions (7,419.00 and 10,807.08 million dollars, 11,560.32971 MW); the 25 state prices equal the published electricity.json prices on 25 of 25; the agent recomputed 8 sites from the raw Epoch CSV and Sales_Ult_Cust_2024.xlsx
- P1: n/a: nobody is quoted on the new text
- P2: holds: EIA-861 2024 and the Epoch pull date of 28 Oct 2026 are named on the figures; /atlas/scale.json carries every row
- P3: holds: industrial and commercial are EIA's sector columns, stated power is Epoch's current power column, and the page says it is IT power
- P4: n/a: no cause or mechanism is named
- P5: n/a: no interval; the rounding gap between printed rows and the total (7,419.1 vs 7,419.0) is stated
- P6: holds: the lead says full stated power for a full year at the state average, arithmetic, not a forecast and not any site's bill
- P7: holds: rows added through ledger.py add with this entry, Papillion rows withdrawn with evidence and added again
- P8: cannot tell: the release build is read live after ship.sh, not before this entry
- P9: holds: the agent ran tone_scan and count_scan clean; no semicolons in the new prose
- P10: holds: the Papillion correction and the Madison address-text placement are both stated on the page
