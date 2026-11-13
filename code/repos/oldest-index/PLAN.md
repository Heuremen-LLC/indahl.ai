# OLDEST: the oldest domains that still serve a page, and whether the page is still the page. Plan, committed before any domain is read.

## The question
Which of the most visited domains on the web are the oldest, which of them still answer today, and for those that do, does the home page still look like the first one the Internet Archive saved? This is a record, not a test of a claim, so it has no ABOVE or BELOW outcome and no row on STACK.

## Three ages, never folded together
1. Registration age: the registration date in the registry's own RDAP record. Hard evidence for the domain and nothing about the page.
2. First capture: the earliest capture in the Internet Archive's CDX index for the home page address. A lower bound on the age of the page. The index starts in 1996, and it can gain earlier captures later.
3. Continuity: whether the home page today still resembles that first capture.

## Population (fixed now)
The first 30,000 domains of Tranco list Y83YG (the list of 1 October 2026, 1,000,000 domains, a published research list with a fixed identifier). Only domains whose top level has an RDAP service in the IANA bootstrap file (data.iana.org/rdap/dns.json) are looked up. Domains under other top levels are counted as NOT_COMPARABLE with that reason. Later extension of the list is a plan addendum.

## Read (fixed now)
1. RDAP: for each domain one request to its registry's RDAP base, with a pause of 0.3 seconds, the user agent heuremen-oldest/0.1 (+https://indahl.ai/oldest). The registration date is the event with action registration. No registration event, or no answer after three tries, is NOTHING_RETURNED and is counted.
2. For domains registered before 1 January 2000 only (the old set): the home page today (GET of https://domain/ then http://domain/, following redirects, 30 second timeout, no disguise). Classes: LIVE_SAME_HOST when the final host is the domain or its www form and the status is 200; LIVE_ELSEWHERE when the final host belongs to a different registered domain; ERROR when the site answers with an error status; UNREACHABLE when no connection can be made.
3. For the old set: the first capture and the number of distinct years with a capture, from the CDX index (fields timestamp and statuscode, status 200 only, collapse on timestamp year, oldest first). The first capture's text is fetched from the Wayback raw form (web.archive.org/web/TIMESTAMPid_/URL).
4. Continuity, for LIVE_SAME_HOST domains with a first capture: the Jaccard overlap of the sets of 3-word shingles of the visible text of the first capture and of today's page (tags, scripts and styles removed, lower case). Fixed bins: MATCHES at 0.30 or more, CHANGED below 0.30, NO_TEXT when either side has fewer than 30 words. A parked or for-sale page is a separate bin, PARKED, when today's visible text contains one of the phrases: this domain is for sale, domain for sale, buy this domain, parked free, domain parking. A page too short or too long to compare is NO_TEXT, never MATCHES.
5. Reported: the 100 oldest by registration date with every class and date, counts by registration decade, and for the old set the counts of each class, with Wilson 95 percent intervals for the share MATCHES among compared.

## Known-good, run before the real read
- RDAP: symbolics.com must return a registration date of 1985-03-15.
- CDX: info.cern.ch must return a first capture no later than 1998-01-01 with status 200.
- Planted text through the overlap code: identical text must give 1.0, two unrelated paragraphs under 0.05, the same text with 10 percent of words changed between 0.40 and 0.90.
- A parked page fixture must read PARKED and a short page NO_TEXT.
- If the Internet Archive answers with its offline page or an error, the domain is NOTHING_RETURNED for the capture step, never a missing capture.

## Hand check
The ten oldest domains with class MATCHES and ten chosen by seed 7 from CHANGED are opened: both texts are read side by side, and the first capture is opened in the Wayback viewer.

## Not claimed
That a domain was in continuous use since its registration date; domains lapse and are re-registered, and the RDAP date is the date of the current registration. That an earlier capture means an earlier page. Anything about domains outside the first 30,000 of the list. That MATCHES means the same author or the same files: it means the visible text overlaps.
