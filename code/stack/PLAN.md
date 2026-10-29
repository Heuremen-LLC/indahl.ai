# STACK: every test result on this site in one table. Plan, written before the first table is built.

## What it does
Each live page keeps its own results under its own plan and its own rule. This page reads their public feeds and lines up the headline tests side by side: what was compared, how many failed, the share with its 95% interval, and the outcome the page's own rule gave. It adds no reading of its own, changes no rule, and recomputes nothing except where a feed gives a share without an outcome (TRIALS, see below).

## Rows (fixed now)
A headline test is a comparison with a stated claim, a count compared, a count failing and an outcome under a fixed rule. The list is: SUPPORT (silent supported cycles, and products with at least one), PKGLICENSE, HFLICENSE (models, datasets), HFSIZE, SECRECORDS (HSTS preload header, SPF lookup limit), PKGINSTALL, HPT (the three steps), TRIALS (stopped records with no reason given, withdrawn records that list participants enrolled, and results due against results posted). TRIALS results posted gives no outcome in its feed. For that row only the outcome is read from the TRIALS plan's rule, ABOVE if the lower end of the share with no results is above 0.25, CONSISTENT if the upper end is below 0.10, otherwise CANNOT_TELL.
A new test joins the table when its page ships. A test whose feed cannot be read is shown as NOTHING_RETURNED, never dropped.

## Order and tally
Rows are listed by outcome in this order: ABOVE, BELOW, CONSISTENT, CANNOT_TELL, NOTHING_RETURNED, and by lower end of the interval within each group. This is an ordering of the table and not a ranking of anyone: the rows are tests of claims, and a share is the share of items in that test.
Beside the table, the pages that report many separate items (TIME, COIN, UPTIME, FORECAST, CADENCE, CADA, LAUNCH, ARXIVDRIFT, LINKROT) are tallied by the outcome of each item.

## Not claimed
That two rows are comparable with each other. Each has its own claim, population and rule, and the rows are side by side only so they can be read together. That a share is a rate across the internet. That the order says which claim matters more.

## Addendum 1 (29 Oct, before the first table, on checking the feeds)
LINKROT's feed carries a share, an interval and an outcome for links gone, so LINKROT (links gone, of links read) joins the row list. Its outcome is the one LINKROT's own rule gave. The rows for TRIALS stopped records come from the TRIALS feed under its cancelled block. No other change.
