# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 09:35 FORECASTERS: stated shares for FEDSEP, REVISE and WATER entered as ledger rows, quoted from each desk's PLAN.md, for the one-axis page indahl.ai/forecasters
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is a statement that held exactly, drawn as the zero line. Every row is plotted against its own stated share, and nothing is pooled across desks or recounted
- II: n/a: no flips or repeats are read. The page shows each desk's own cells as the desk publishes them
- III: n/a: no sign or product is read across desks. Each row's sign is the desk's own share minus its own stated share, and the row says what the share counts
- V: holds: each desk keeps its own ruler and interval (bootstrap over years for FEDSEP, Wilson over months for REVISE, Wilson on water years for WATER, Wilson for NEO and FORECAST), named on the page
- VI: holds: the outcome shown is the desk's own label from its feed, one of ABOVE, BELOW, CONSISTENT, CANNOT_TELL, never relabelled
- R: holds: stated shares read from fedsep_index/PLAN.md line 13 (about 0.30 outside), revise_index/PLAN.md line 14 (about 0.10 exceedance), water_index/PLAN.md addendum 1 (approximately an 80% probability, Reclamation's own sentence). NEO's 0.9973 is in its feed and is our reading, said on the page
- P1: holds: each ledger row greps the plan's own words. Reclamation's sentence is quoted verbatim from the plan addendum
- P2: holds: every printed number is a reference into a feed snapshot (forecasters/feeds/<desk>.json, fetched from indahl.ai/<desk>/live.json at build) or a live ledger row, re-rendered by forecasters.py --gate
- P3: holds: item labels are the desk's own cell names (pooled names, count names, cell names, bin and lead) read from the feed
- P4: holds: no cause is named. The page says the members measure unlike things and is no ranking
- P5: holds: the page names each desk's interval in a note under the table
- P6: holds: the page prints only the desk's own numbers and labels. The difference from the stated share is drawn, not printed
- P7: holds: ledger rows first, page through ledger/ship.sh, verified live
- P8: holds: rendered page read after the build, chart checked at phone width and in dark mode
- P9: holds: plain sentences, no semicolons, no counts in headings, Heuremen LLC, no AI statement
- P10: holds: NEO's 99.73 percent is labelled our reading on every row. The FEDSEP, REVISE and WATER shares are the plans' committed figures
