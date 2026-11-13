
## 2026-11-12 10:26 SUPPORT moved onto Faults and Guards 2.0 (plan addendum of 12 Nov 2026): band [0,0.05), size 0.10, reasons and REQ-13, product-level row every tested cycle unreleased CANNOT_TELL to ABOVE
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is zero unreleased cycles, the claim of PLAN.md. The gate (python 3.8 and 3.15) still runs before every pass and the 12 Nov rebuild read the stored cycles file, so no cycle was dropped or added by the outcome change
- II: n/a: no repeated item, one read of each cycle and the rebuild used the same stored rows (430 tested, 104 unreleased) as the 10 Nov to 12 Nov feed
- III: holds: only ABOVE can occur against a band that starts at zero, the cells are all in the same direction, no sum or product of cells is formed
- V: holds: the ruler is PLAN_ADDENDUM_std2.md written and committed (3caec07) before the rebuild, size 0.10, band [0,0.05) open at the top, product bootstrap 4000 draws seed 7 for the headline, Wilson for the other cells, both named
- VI: holds: four outcomes kept and K.read applied in section 6.4 order, both alternatives tested (zero and 0.10 in one interval gives TOO_WIDE_TO_RESOLVE), the rebuild gives all cycles ABOVE unchanged, at least one product ABOVE unchanged, every tested cycle unreleased CANNOT_TELL to ABOVE
- R: holds: 430, 104, 228, 41 and 20 are read from summary_support.json rebuilt from data/cycles.json, intervals [0.154,0.3375] for the headline and [0.0575,0.1316] for the flipped row did not move, the flip is labelled as caused by the closed dead zone
- P1: n/a: the page quotes no third-party text in the changed paragraph, only our own rule
- P2: holds: the rule paragraph names the addendum and its date, 12 Nov 2026, and the figures sit in the live feed rows beside it
- P3: holds: the setting labels on the page (95 percent interval, 5 percent edge, 10 percent size) match PLAN_ADDENDUM_std2.md items 1 to 3
- P4: n/a: no cause is named in the changed text, only the outcome rule and its reasons
- P5: holds: the rule paragraph says the headline interval is the bootstrap over products and the Wilson columns are shown beside it, and the new text adds the reason and REQ-13 line
- P6: holds: the new text says what the rule is and that earlier readings stand under the rule they named, nothing about abandonment
- P7: cannot tell: build_site.py edited, the owner ships later through ship.sh so the live page is not checked yet and no ledger row changes (the headline row is unchanged and the flipped product-level cell has no ledger row)
- P8: cannot tell: the page is not built or rendered in this pass, live.js passed node --check and shows the reason and REQ-13 column in two tables, rendering is checked at ship
- P9: holds: the new public sentences contain no semicolon and no count of our own things in a heading, the plain wording was read once more after the edit
- P10: holds: the product-level shares stay labelled as defined after the first read, and the new dead-zone closure is stated in the addendum with its date, 12 Nov 2026, after the data
- O1: n/a: no new job, the rider is the existing support_tick.py on the tick bus
- O2: holds: a gate failure now prints CANNOT_TELL with NO_INTERVAL_FORMABLE and the page shows the failed gate, no failure is called a pass
- O3: n/a: no GPU work in this change
- O4: holds: liveness is the completed run of support_tick.py, the offline rebuild wrote summary_support.json from data/cycles.json and the code exits through the same summary path
- O5: n/a: the rebuild used absolute paths through the script directory and set no PATH change
- O6: n/a: no GPU job of any kind was started by this change
