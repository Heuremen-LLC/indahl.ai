# CACA: Claimed And Checked Assurance, live DNS filter comparison (28 Oct 2026, his word)
Written and committed before any resolver is asked about any listed domain.

## What is measured
Public DNS resolvers that advertise blocking of malware and phishing domains. For each, the share of freshly listed bad domains it refuses, and how long after listing it starts to refuse them. DNS queries only. We never connect to a listed host, download a sample or open a page.

## Feeds (fresh listings)
Two public lists whose licenses allow this use: the Phishing.Database active domain list (MIT) and the CERT Polska domain list for blocking. A domain is fresh if it is in a feed now and was not in that feed at our previous read. First seen is our own read time, so the true listing time is earlier by at most one read interval, and that bound is published. Feeds with terms that bar commercial use are not used. If a feed's terms change or it goes away, its rows stop and the stop is stated.

## Sampling
Up to 40 fresh domains per feed read, chosen by a fixed-seed shuffle of the new names. Names that are IP addresses are skipped. All sampled names are kept, never dropped after a result.

## Resolvers
Controls, which state no filtering: Cloudflare 1.1.1.1, Quad9 unfiltered 9.9.9.10, Google 8.8.8.8. Filtered, each advertising malware or phishing blocking: Cloudflare 1.1.1.2, Quad9 9.9.9.9, OpenDNS 208.67.222.222, AdGuard 94.140.14.14, CleanBrowsing 185.228.168.9, DNS0.eu 193.110.81.0, Control D 76.76.2.1. A resolver that does not answer is NOTHING_RETURNED and is counted.

## Per query
A record, UDP, 3 s timeout, one try. Classes: ANSWERED (a public address), NXDOMAIN, REFUSED, SINK (0.0.0.0, 127.0.0.0/8, ::, or an address the provider documents for its block page), SERVFAIL, TIMEOUT.

## Checkpoints
Each sampled domain is asked at first sight, then 1 hour, 6 hours and 24 hours later, on an HST tick, never on a timer.

## Alive and blocked
A domain is alive at a checkpoint if at least two of the three controls answer with the same public address set. A filtered resolver blocks it at that checkpoint if it returns NXDOMAIN, REFUSED or SINK while the controls answer. SERVFAIL and TIMEOUT are not blocks and are counted on their own. A domain the controls cannot resolve is not alive and is left out of that checkpoint's rate and counted.

## Outcomes
Per resolver and checkpoint: share blocked of alive domains with a Wilson 95% interval. Time to block: for domains blocked at any checkpoint, the first checkpoint at which the resolver blocked, with the censoring stated. Provider statements are quoted verbatim with the page and date. Where a provider states a number the outcome is ABOVE, BELOW or CONSISTENT against the Wilson interval. Where it states no number the outcome is CANNOT_TELL and the delivered rate is published as measured. No ranking.

## Fairness
Each provider gets a vendor-response path on the page. Misses are reported as misses of this list on these dates, never as a statement about a provider's whole product.

## Addendum 1 (28 Oct, no query changed)
The division is named CADA, Claimed And Delivered Assurance. Page path /cada. Rules, feeds, resolvers and outcomes above are unchanged.

## Addendum 2 (28 Oct, no query changed)
The expansion is Checked Against Domain Abuse, so the name does not echo Stated Against Delivered. Rules, feeds, resolvers and outcomes are unchanged.

## Addendum 3 (28 Oct, no query changed)
The expansion is Checked Against Domain Alerts. Rules, feeds, resolvers and outcomes are unchanged.


## Note (29 Oct, from the internal audit)
This plan did not state its unit and what it does not claim in one place. Stated now, with no change to any rule, read or outcome. Unit: a listed fresh abusive domain at one checkpoint, for one filter. Not claimed: that any filter product is effective or ineffective, anything about domains outside the two lists, or that the lists are complete or correct.

## Note 2 (29 Oct, from the internal audit)
A resolver that answered none of its queries (dns0_eu, 1,075 timeouts) was scored as blocking 0 of 486 domains, 0 to 1 percent, which reads as a filter that blocks nothing. A timeout is a fact about our path or the resolver's availability, not about its filtering, and was sitting in the denominator as not blocked. From 29 Oct a query that returns no answer is counted apart as a timeout, is not in the denominator, and a resolver with no answered query at a checkpoint is shown as nothing returned with its timeout count. The six timeouts of ControlD and one of Quad9 are removed from their denominators the same way. No other rule changed.
The audit also notes two limits that are not fixed here and are stated: the Wilson intervals treat each sampled name as independent although names from one campaign cluster, and the cell at each checkpoint is read on the domains still alive then, so the 1 hour and 6 hour cells are not one cohort followed in time.
