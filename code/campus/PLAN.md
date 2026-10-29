# CAMPUS: the documents behind the OY Matrix, kept over time. Plan, committed before the first read.

## The question
The OY page (indahl.ai/oy) lists what colleges and universities have published about their own AI policies and measurement, with a source link for every row. Those sources are web pages and PDFs that their owners can move, rewrite or remove. We read every external source on the page, store what it said, and read it again on later passes, so that a change shows and so that the Matrix can be kept right. This is a record. It has no ABOVE or BELOW outcome, no STACK row, and it never ranks or judges a school.

## Population (fixed now)
Every external link (an address that does not belong to indahl.ai or heuremen.org) in the HTML of indahl.ai/oy on the day of the read. The institution is the first cell of the table row the link sits in, when the link is inside a table row, otherwise the nearest heading. Links are de-duplicated by address, and an address keeps every institution it is cited for.

## Read (fixed now)
For each address, one GET with a pause of 0.5 seconds between requests to the same host and 1 second overall, the user agent heuremen-campus/0.1 (+https://indahl.ai/campus), 30 second timeout, redirects followed, at most 3 tries on a connection error or HTTP 429 or 5xx, and no disguise. Stored per address and read: HTTP status, final address, content type, size, whether it is an HTML page, a PDF or something else, and the visible text (HTML: tags, scripts and styles removed; PDF: text of every page with pypdf) reduced to its words in lower case. The words are kept as a file named by the SHA-256 of the address. A page that returns fewer than 30 words has class NO_TEXT and is compared by size.

## Pair classes, comparing a read with the previous read of the same address (fixed now)
- SAME: both reads returned text and the overlap of their 3-word shingles (Jaccard) is at least 0.90.
- CHANGED: both reads returned text and the overlap is below 0.90.
- MOVED: the final address differs from the previous read's final address and the page resolves. A MOVED page is also compared for text and carries SAME or CHANGED.
- GONE: the previous read resolved (HTTP 200) and this read returns 404 or 410, or the host no longer answers on 2 reads separated by one pass.
- BLOCKED: HTTP 401, 403 or 429 on this read. Neither SAME nor GONE. Counted apart.
- ERROR: any other status or a connection failure on one read. Retried at the next pass and never called GONE on one failure.
The first read has no previous read and returns NOTHING_RETURNED for the pair classes. Each pass also prints the state now: counts of 200, redirect, BLOCKED, ERROR, GONE.

## Known-good, run before every pass
The shingle overlap must give 1.0 for identical text, below 0.05 for unrelated text, and between 0.90 and 1.0 for a text with one word in 40 changed (so the SAME bound is live). A planted fixture page (served by the code itself on a local port) must read 200 then, after its text is changed, CHANGED, then after a 404 read GONE once the two-read rule is met. The link extractor must find the planted external links in a planted OY-like page and none of the internal ones.

## Hand check
After the second pass: every GONE and every CHANGED page whose overlap is below 0.50 is opened by hand. What was found goes in data/hand_checked.json. A row of the Matrix whose source is GONE or rewritten is rechecked by hand against its row before the page says anything about it.

## Schedule
Every 720 ticks of the tick bus (about 2.5 days).

## Not claimed
That a changed page was changed to hide anything: pages change for many ordinary reasons, and dates, menus and counters can move a score. That a missing page means a policy was withdrawn. Anything about why. That the links on the OY page are every document a school has published.

## Addendum 1 (29 Oct, before any real page was read)
The first run of the known-good failed on two points of its own test data. (1) The planted text with one word in 40 changed has an overlap of 0.84, not between 0.90 and 1.0, because each changed word removes three 3-word shingles. The SAME bound of 0.90 is unchanged. The planted check now changes one word in 80, which must give an overlap from 0.90 up to but not including 1.0. (2) The link extractor listed the nearest heading as well as the table cell for a link inside a table row. It now gives the heading only for links outside a table row, as the plan says.
