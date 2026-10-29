# LINKROT: "code and data are available at" against whether the link works. Plan, written before any link is checked.

## Claim read
A paper states, in its abstract or arXiv comment, that its code or data can be found at a URL. Stated: the link leads there. Delivered: the link resolves now, and whether it still resolves a week later.

## Population (a census, no sampling)
arXiv API, public. Papers in cs.LG, cs.CL, cs.CV, quant-ph, stat.ML whose abstract matches one of the tokens github, gitlab, huggingface, zenodo, bitbucket (the search side), and from whose abstract plus arXiv comment text we extract URLs on those five hosts. Papers whose link is only in the full text or only in the comment and not in the abstract search are not reached. That is a stated limit. Cohort = year of first submission, 2018 to 2026 (2026 partial). A unit is one unique link per paper.
GitHub and GitLab links are cut to https://host/owner/repo (first two path parts). Trailing punctuation is stripped.

## Check (fixed now)
One request per link, HEAD then GET if HEAD is refused, follow redirects, 20 second timeout, user agent naming this site, one request per host at a time with a pause. Status:
LIVE: final status 2xx.  GONE: 404, 410 or 451.  DNS_FAIL: the host name does not resolve.  BLOCKED: 401, 403, 429, 5xx or a refused connection.  TIMEOUT.
BLOCKED and TIMEOUT are counted apart and are never rot. A redirect that ends on a different owner or repo name is LIVE and also counted as MOVED.
Rot share = (GONE + DNS_FAIL) / (LIVE + GONE + DNS_FAIL), per cohort and per host, Wilson 95% interval.
Outcome against the claim that the link leads there (zero rot): ABOVE if the lower end of the rot interval is above 0.10. CONSISTENT if the upper end is below 0.05. Otherwise CANNOT_TELL. A cohort with fewer than 30 readable links is CANNOT_TELL. Thresholds fixed here.
Re-check: every link is read again every 7 days, so each link has a history and the cohort shares have a time series. A link that was GONE and reads LIVE later is counted as returned.

## Known-good gate
Before each full pass, 5 links that must read LIVE (github.com/torvalds/linux, www.python.org, arxiv.org/abs/1706.03762, example.com, zenodo.org) and 5 that must read GONE or DNS_FAIL (github.com/this-owner-does-not-exist-7q2/none, example.com/no-such-page-7q2, a made-up .invalid host, zenodo.org/records/1 does not count, raw.githubusercontent.com/torvalds/linux/master/no-such-file-7q2). If any control reads wrong, the pass is CANNOT_TELL for every cohort and the page says the instrument failed its gate.

## Not claimed
Whether a live repository holds what the paper says. Whether a GONE link was removed by the author. Hosts that block us are not rot. Papers not in the five categories or without a link in the abstract are not part of the population.

## Seats
This plan covers one seat (this Mac). A second seat from the independent runner network is added by a dated addendum before it is used, and a disagreement between seats on a link reads BLOCKED.

## Addendum 1 (29 Oct, before any link was checked)
The known-good list above has a garbled fourth dead item. The exact controls are:
Must read LIVE: https://github.com/torvalds/linux, https://www.python.org, https://arxiv.org/abs/1706.03762, https://example.com, https://zenodo.org.
Must read GONE or DNS_FAIL: https://github.com/this-owner-does-not-exist-7q2/none, https://example.com/no-such-page-7q2, https://made-up-host-7q2.invalid, https://raw.githubusercontent.com/torvalds/linux/master/no-such-file-7q2, https://zenodo.org/records/99999999999.
Search tokens are matched on the arXiv side; the URL extraction is a pattern for the five hosts. Nothing else changed.

## Addendum 2 (29 Oct, before the second seat was used)
The second seat from the independent runner network is added, as the plan's Seats section allows. Every link in the list is also requested from the GitHub runner network (the nodes repository, workflow linkrot-probe, one pass every 7 days, results committed to data/linkrot/results.jsonl) with the same classification, the same controls and the same per-host pause as the first seat.
Combining the seats (fixed now): a link with a reading from both seats within 14 days of each other reads LIVE if both read LIVE, and GONE or DNS_FAIL if both read that. If one seat reads LIVE and the other reads GONE or DNS_FAIL, the link reads BLOCKED and is counted as a disagreement, never as rot. Any other combination of two readings (for example one seat BLOCKED or TIMEOUT) keeps the first seat's reading. A link with a reading from one seat only keeps that reading. The page shows the number of disagreements and the number of links read by both seats.
The runner's controls are the same ten links. If any control reads wrong in a runner pass, the whole pass is discarded and the links keep their first-seat readings.
No threshold, class or outcome rule changes.

## Note 3 (29 Oct, from the internal audit)
When the arXiv request for a year and search token returned nothing, the census marked that cell done and never tried it again, so the census could be silently incomplete while the page says it reads every paper in its categories. A cell whose fetch failed is now left not done and tried again on the next pass, and its failure is printed. Stated and not fixed: any URL on the five code hosts in an abstract or comment counts as the paper's own code claim, including a link to someone else's code, and two seats agree on 1,980 of 1,980 links and a disagreement would read BLOCKED with no third reading to settle which seat is wrong.
