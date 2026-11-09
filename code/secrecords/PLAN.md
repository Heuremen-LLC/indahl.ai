# SECRECORDS: what a domain's published security records state against what those records can do. Plan, written before any domain is read.

## Claims read
1. HSTS preload. A site that sends Strict-Transport-Security with the preload directive states that it asks to be on browsers' HSTS preload lists. The published requirements for that list are a max-age of at least 31,536,000 seconds and the includeSubDomains directive. Stated: the header asks for preloading. Record: the same header.
2. SPF. A domain that publishes an SPF record states which servers may send its mail. RFC 7208 section 4.6.4 limits an evaluation to 10 DNS lookups (each include, a, mx, ptr, exists and redirect counts, and the lookups of included records count too). A record that needs more than 10 returns a permanent error, so it states a policy that receivers cannot apply. Stated: the SPF record. Record: the count of lookups its evaluation needs.

## Population
The 1,000 highest ranked domains in the Tranco list on the day of the read (the list id is stored). Unit: one domain. For claim 1, domains whose HTTPS response states preload. For claim 2, domains that publish an SPF record.

## Read (fixed now)
HSTS: one HTTPS GET of https://DOMAIN/ following redirects, timeout 15 seconds, user agent naming this site. The header of the final response is read. If the request fails, the domain is NOT_COMPARABLE for claim 1.
SPF: the TXT records of the domain through Cloudflare's DNS over HTTPS service. The record starting v=spf1 is read. Lookups are counted by following include and redirect recursively to a depth of 10, with each mechanism of the kinds above counted once where it occurs. ip4, ip6, all and exp are not counted. A record that cannot be fetched during the count is counted as the lookup it cost and the domain is NOT_COMPARABLE if the count was cut short.
Classes for each claim: AGREE (claim 1: max-age at least 31,536,000 and includeSubDomains present. Claim 2: count of 10 or fewer), DISAGREE (the opposite), NOT_COMPARABLE (no statement to read or a read that failed).
Reported per claim: counts by class, the share DISAGREE among AGREE plus DISAGREE with a Wilson 95% interval, and every DISAGREE row with the header or the record.
Outcome against the claim that the published record can do what it states (zero disagreement): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 comparable domains: CANNOT_TELL.
Descriptive, no outcome and no claim: the share of the domains whose HTTPS response carries an HSTS header at all, the share that publish an SPF record, and the DMARC policy (none, quarantine, reject, or no record) read from _dmarc.DOMAIN.
Re-read every 30 days.

## Hand check (fixed now)
Every DISAGREE row is opened by hand, the header or the record and the count, before it is shown, and the reason written beside it. A row where the reading was wrong is corrected by a dated addendum and the whole read is run again.

## Known-good
Header tests: "max-age=31536000; includeSubDomains; preload" AGREE, "max-age=300; preload" DISAGREE, "max-age=63072000; preload" DISAGREE, "max-age=31536000; includeSubDomains" NOT_COMPARABLE, "max-age=31536000; includeSubDomains; preload" in mixed case AGREE. SPF tests on planted record sets: a record with 3 includes of ip-only records counts 3, a chain of 11 counts 11 and reads DISAGREE, a redirect counts 1 plus the target, a record with only ip4 counts 0. Live: github.com sends the header with preload and reads AGREE; google.com publishes an SPF record and reads a count of 10 or fewer. Any wrong answer stops the pass.

## Not claimed
That a domain is or is not safe. That mail is or is not delivered. Whether a browser's preload list contains the domain. Anything about subdomains.

## Note 1 (29 Oct, hand check of the first read, before anything was shown)
Both tests read ABOVE under the fixed rule. All 36 HSTS rows and all 21 SPF rows were opened by hand. For HSTS the header as sent was read for each row and seven were fetched again live and matched what was stored. The reasons found: 18 send preload without includeSubDomains, 9 send a max-age under 31,536,000, 8 do both, and 1 (ntp.org) writes max-age with a hyphen instead of an equals sign. For SPF all 21 records were counted again with dig and a second script that follows the same counting rules but shares no code with the reader, and all 21 counts matched. No row was a reading error. The reading did not change and no rule changed.
This is a statement about headers and records, not about whether those domains are on any preload list or whether their mail is delivered.

## Addendum 1 (29 Oct, from the internal audit, after the first publication)
Two findings.
1. The SPF counter skipped an include it had already met, counting the term once and not counting the lookups inside it again. RFC 7208 counts every term each time it is evaluated, so a record that includes the same provider twice costs twice. The reader undercounted and the count was biased toward AGREE. The independent recount in Note 1 shared this error, since it followed the same counting rules. The counter now follows the standard: every evaluated include, a, mx, ptr, exists and redirect counts each time, and only a record that includes itself through its own chain is cut. The gate gains a planted record that includes the same provider twice and must count 14. Every stored SPF record is counted again with the new rule. The earlier counts are kept in data/domains_spf_before_recount.json.
2. Note 1 said both tests read ABOVE. That was wrong: the HSTS test read ABOVE and the SPF test read CONSISTENT, as the feed says. No rule or reading changed with this correction.

Note 2 (29 Oct, after the full reread with the corrected SPF counter). The read finished on the same 1,000 domains. HSTS: 37 DISAGREE of 187 compared (36 of 186 before; the new row is shop.app, opened by hand: max-age 15,552,000 seconds, under the 31,536,000 the list asks for). SPF: 21 DISAGREE of 757 compared, the same count as before. The corrected counter changed the class of two domains: vk.ru went from AGREE to NOT_COMPARABLE (no SPF record was returned this time) and disneyplus.com from NOT_COMPARABLE to AGREE. Neither outcome changed: HSTS ABOVE, SPF CONSISTENT. The counting error in the first count did not move any DISAGREE row.


## Addendum on cadence (29 Oct)
The repeat cadence is now every 62 ticks of the tick bus, about 6.0 hours, so that a change at the source shows within hours. The earlier cadence was a default chosen when the corner was built. Nothing else changes; each pass keeps the same read, the same politeness pauses and the same known-good checks.

## Note 3 (30 Oct 2026, from the site pass)
Two HSTS rows, epicgames.com and wp.com, were DISAGREE but had not been opened when the page was published, so the page listed 35 of the 37. Both were read again on 30 Oct with a second tool (curl, same user agent) and match what was stored. Both are now listed. The page shows the count of mismatches still waiting for this above its tables. No rule or reading changed.

## Addendum 2 (9 Nov 2026, from the site pass, before the reread)
The HSTS read followed redirects and read the header of the final response, often on another host (for fbcdn.net it stored the header of www.facebook.com). The preload list's rule is about the base domain's own response: "If you are serving an additional redirect from your HTTPS site, that redirect must still have the HSTS header (rather than the page it redirects to)." (hstspreload.org, read 9 Nov 2026). A 308 was never followed under the Python that runs the reader, so those rows already read the base domain, and one column held two rules. Of the 189 rows that sent a preload header in the 8 Nov read, 125 were read after a redirect.
The read is now: one HTTPS GET of https://DOMAIN/ that follows no redirect, timeout 15 seconds, the same user agent. The header of that first response is read, whatever its status, a redirect included. Its status and its redirect target are kept in their own fields. If the request fails, the domain is NOT_COMPARABLE for claim 1, as before.
Known-good gains a planted check: a local server answers with a 301 and with a 308 that each carry one header, and the page they point to carries another. The reader must return each redirect's own header, status and target. A reader that follows the redirect fails it and stops the pass. The live github.com check uses the same reader. Classes, the outcome rule and the hand check do not change.
The whole read is run again on the day's Tranco list, every DISAGREE row whose header changed is read in full again before it is shown, and the page names the change. The 8 Nov read is kept in data/domains_before_addendum2.json.

## Note 4 (9 Nov 2026, after the reread under Addendum 2)
The read ran on the Tranco list of 9 Nov with the new reader. HSTS: 20 DISAGREE of 144 compared, 13.9 percent, 95 percent interval 9.2 to 20.5, so the outcome reads CANNOT_TELL under the fixed rule (the 8 Nov read gave 38 of 189, 20.1 percent, 15.0 to 26.4, ABOVE). 326 of the 1,000 base responses carry an HSTS header at all (446 when redirects were followed). SPF did not change: 20 of 764, CONSISTENT.
Every HSTS DISAGREE row but one was read again with a second tool (curl, same user agent, no redirect followed), and each reason now names the base domain's own response, its status and its redirect. 18 matched what was stored. shop.app sent max-age=63072000 to the second read and to a later read by the reader itself, against max-age=15552000 in the pass, so its header differs from one read to the next, and its reason says so. One row, unchanged by this addendum, still waits for its read in full. The HSTS reasons written under the old rule are kept in data/hand_checked_before_addendum2.json and are no longer shown, so a domain that reads DISAGREE again later is read in full again first.
