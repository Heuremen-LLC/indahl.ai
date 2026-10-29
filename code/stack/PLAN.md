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

## Addendum 2 (29 Oct, same day, on being told the table did not hold every test)
The first table held only the tests that report a share with an outcome. Every other live page also measures something, and leaving them out hid them. Three additions, no change to any rule.
1. The row list gains FEDSEP (the pooled share outside the stated range, this year and next year) and keeps REVISE and HPT.
2. A second table, Running measurements, lists every other live page with what it measures, the reading as its own feed gives it, and its state: ARXIVDRIFT, CADENCE, CADA, FORECAST, LAUNCH, CHANGE, SEAT, and the four QIA feeds (audit, T1 and T2 runs, queue, stability). A reading is copied from the feed as text and no outcome is added to it. A page whose feed has no outcome rule yet is shown as running, with what it is waiting for.
3. The tally of pages that report many separate items gains CADENCE, whose feed gives a count of series consistent, below and cannot tell for each portal; the counts are summed.
IRIS, MODEL, ATLAS and OY are pages of static tables with no live feed, and they are linked under the tables. The table still lists a test only when its page ships.

## Addendum 3 (29 Oct, same day, on the owner's note that the page should summarise every division and stack across them)
The page becomes three layers, with no change to any rule or reading.
1. A summary of every division and every group of live pages: what it holds and one live reading from its own feed. The divisions are QIA, IRIS, OY, ATLAS and HERMES. The live pages are grouped by the question they ask: a stated number against its record (REVISE, FEDSEP, SECRECORDS, HFSIZE, PKGLICENSE, HFLICENSE, TRIALS), a promised file or link (LINKROT, PKGINSTALL, HPT, ARXIVDRIFT), a stated date or window (SUPPORT, CHANGE, CADENCE, LAUNCH, FORECAST), and the checks on ourselves and on time and uptime (SEAT, TIME, UPTIME, CADA, COIN). A page sits in one group, fixed here.
2. The headline tests plotted on one shared axis, share with its interval, coloured by outcome, so tests from different divisions can be read against each other. The axis is the share of items failing and the plot says that two tests are not measures of the same thing.
3. A button that stacks three tests at random on that axis, for anyone who wants to put unlike tests next to each other. It reads the same rows and draws them. It chooses nothing and ranks nothing.
The tables from addenda 1 and 2 stay.

## Addendum 4 (29 Oct, on the division rename)
The fifth division is HERMES (Held Every Record, Measured Every Statement). Every live page has one home division: IRIS holds HFSIZE, HFLICENSE, PKGLICENSE and PKGINSTALL; ATLAS holds UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT and CHANGE; HERMES holds TRIALS, HPT, REVISE, FEDSEP, CADENCE, FORECAST, LAUNCH, COIN, ARXIVDRIFT and LINKROT; QIA and OY hold their own pages. The groups by question in addendum 3 stay as the cross-cut. HERMES is the menu of every division and desk at /hermes, and its MODEL desk is at /hermes/model.

## Note on naming (29 Oct)
This plan was written when the fifth division carried an earlier name. On 29 Oct 2026 the name was removed from the public files. The wording above was changed to the current names and nothing else. The earlier text is kept in the archive tag pre-hermes-20261029 and in the hash chain.
