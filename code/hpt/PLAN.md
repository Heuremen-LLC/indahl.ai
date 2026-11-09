# HPT: hospital price-transparency files, stated against found. Plan, written before any hospital website is read.

## Claim read
The federal hospital price transparency rule (45 CFR 180) asks each hospital to publish its standard charges in a machine-readable file. CMS's published FAQ for the TXT file says: the file must be named cms-hpt.txt and must be located at the root of the domain of the public website that hosts the machine-readable file, and a hospital whose file is hosted on a health system's website must have the system place the TXT file at the root of the system's domain. The TXT file gives the location name, the page that hosts the file and a direct link to the file (lines location-name, source-page-url, mrf-url). A URL redirect to the file is accepted. The machine-readable file's template starts with hospital_name, last_updated_on and version.
Stated: a hospital website has a cms-hpt.txt at its root that links to a standard-charges file. Found: what is at that address today.

## Population
United States hospitals in Wikidata (instance of hospital or a subclass, country United States, with an official website, and no dissolved or end date), read by SPARQL on the day of the read (the date is stored). Unit: the website's domain, one row per distinct host with its leading "www." removed. A website whose address has a path beyond the root (a page on a shared site such as a city or state government site) is NOT_COMPARABLE.

## Read (fixed now)
Three steps for each domain, each with one request at a time and a pause of 0.4 seconds, a user agent naming this site and a 30 second timeout. No browser disguise is used: a site that refuses our user agent is NOT_COMPARABLE and counted apart.
1. TXT file: GET https://DOMAIN/cms-hpt.txt following redirects. If the connection fails, www. is tried. AGREE when the response is 200 and the body has a line starting mrf-url: . DISAGREE when the response is 404 or 410, or 200 with no mrf-url line. NOT_COMPARABLE when the site cannot be reached or answers 403, 429 or a server error.
2. Link resolves: for domains that AGREE in step 1, GET the first mrf-url with a Range header for the first 4,096 bytes. AGREE when 200 or 206 and the path ends .csv, .json, .zip or the content type is csv, json, zip or a binary stream. DISAGREE when 404 or 410, or a web page (text/html) comes back instead of a data file. NOT_COMPARABLE when 403, 429, a server error, or no connection.
3. Template header: for step 2 AGREE rows that are not zip, the first 4,096 bytes must contain hospital_name, last_updated_on and version (any case). AGREE when all three appear, DISAGREE otherwise. Zip files are NOT_COMPARABLE.
Reported per step: counts by class, the share DISAGREE among AGREE plus DISAGREE with a Wilson 95% interval, and every DISAGREE row. Outcome per step against the claim (zero disagreement): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 comparable domains: CANNOT_TELL.
Re-read every 30 days.

## Hand check (fixed now)
Ten DISAGREE rows from step 1, chosen by a fixed seed of 7, are opened by hand: the home page is fetched and searched for a link about price transparency, to see where the hospital says its file is. Every DISAGREE row of steps 2 and 3 is opened by hand. A reading error is corrected by a dated addendum and the whole read is run again.

## Known-good
Before each read: the parser reads a planted TXT body with an mrf-url line as AGREE and one without as DISAGREE, a planted CSV header with the three names as AGREE and without as DISAGREE. Live: a URL known to return 404 on a reachable site (https://indahl.ai/cms-hpt.txt) must read DISAGREE, and a planted address with a path must read NOT_COMPARABLE.

## Not claimed
That a hospital is or is not compliant. A hospital can host its file on a health system's domain, and the rule then places the TXT file at the system's domain, so a missing file at the hospital's own domain can be correct. The file's charges, their accuracy or completeness. Anything about the hospital's care.

## Addendum 1 (29 Oct, after the first read and the hand check, before anything was shown)
The first read returned step 1: 511 AGREE, 517 DISAGREE, 893 NOT_COMPARABLE. Step 2: 487 AGREE, 14 DISAGREE. Step 3: 417 AGREE, 13 DISAGREE, 57 NOT_COMPARABLE. The hand check was done as planned.
1. Step 1, ten DISAGREE rows chosen by seed 7. Two are hospitals that state price information on a page of their own site and keep the file at a health system domain or another host (khrancho.com, virginiamason.org). One serves a web page for every address, so the file is absent (bamc.org, einstein.edu). One could not be opened for the page check (lmhospital.org, HTTP 403 on the home page). Five are not hospital websites in the sense of the rule or are part of a system whose root file sits on another domain (rockymountainmsclinic.com, cliffordbeers.org, recoveryunplugged.com, nrlc-group.net, dukecancerinstitute.org). The Wikidata population includes clinics and parts of systems. The step 1 share is therefore not a compliance rate, as the plan already said, and its outcome is now fixed as CANNOT_TELL with this reason. The counts stay on the page. A tighter population would be a new plan.
2. Step 2, 14 DISAGREE rows. Ten are files that return 404 now. Two serve a web page (mvhealth.org, onslow.org). Two are reading errors: choa.org returns a gzip-compressed data file labelled text/html, and valleychildrens.org returns a CSV labelled application/force-download. The reader trusted the content type. It now decodes a gzip prefix, calls it a web page only when the content itself starts as HTML, and otherwise calls it data.
3. Step 3, 13 DISAGREE rows. Eleven are reading errors. Six are JSON files whose key names can sit after the data, so a header test on the first 4,096 bytes cannot say; five are zip files served without a .zip name. Two are true (childrens.com and claxtonhepburn.org serve a CSV without the template header names). Step 3 now returns NOT_COMPARABLE for JSON and for anything starting with the zip signature.
4. Because the reader changed, steps 2 and 3 are read again for every domain whose step 1 was AGREE. Step 1 was not changed and its results are kept. Every DISAGREE row of the new steps 2 and 3 is opened by hand before it is listed.

Addendum 2 (29 Oct, after the second read of steps 2 and 3 and a hand check of every DISAGREE row). Step 2: 487 AGREE, 13 DISAGREE, 11 NOT_COMPARABLE. Step 3: 327 AGREE, 2 DISAGREE, 158 NOT_COMPARABLE (JSON and zip files). Correction to addendum 1: choa.org was not a reading error. Its address returns a gzip-compressed web page, decoded by hand, so DISAGREE stands. The gzip decoding stays because it is the correct way to look at such a response. All 13 step 2 and both step 3 DISAGREE rows were opened by hand and are listed with the reason found.


## Addendum on cadence (29 Oct)
The re-read every 30 days in the plan is replaced by every 1,740 ticks of the tick bus, about 7 days, so that a change at a hospital shows within days. Nothing else changes.
# Correction (30 Oct 2026, site pass H-8, H-19). Ready to append to PLAN.md and commit in one step. Not appended because the rider refuses to run while PLAN.md differs from its commit.

1. The value of mrf-url is the rest of the line, with spaces percent-encoded as a browser sends them. The reader took the text up to the first space. Alice Peck Day Memorial Hospital and Cheshire Medical Center publish addresses with spaces in the file name, were read as 404, and both open as data once read in full. All 511 domains whose cms-hpt.txt had been read were read again on 30 Oct. Five addresses differed: the two above, ufhealthjax.org (its file now lists another location first), woodcountyhospital.org (its file doubles the key, mrf-url: mrf-url: https://..., read as that whole value, not comparable as before) and och.scvh.org (answered a server error on the re-read and was left as stored). Step 2 is now 11 of 500, where it read 13 of 500.
2. The read-in-full rows for the two domains are removed because they no longer fail step 2. The notes that remain were all made on the addresses the files give.
3. The read-in-full table links each website to the cms-hpt.txt that answered and each row to the linked file.

## Addendum 3 (9 Nov 2026, from the site pass, before the reread)
The Python that runs the reader (3.9) does not follow an HTTP 308 redirect, so step 1 filed 18 domains that answer with a 308 as "blocked or server error (HTTP 308)" and never read the address the redirect gives. A 308 is a redirect, not a block. The reader now opens every address through the kit's opener, which follows 308 the way it follows 307 (same method, as RFC 9110 says), and a redirect that still cannot be followed is filed as "redirect not followed (HTTP 3xx)". The kit's self-test gains a planted check: a local server answers with a 308, and the opener must land on the page it points to.
Every domain filed under a 3xx status is read again through steps 1 to 3 with the new opener (HPT_REREAD308). Every other row is kept as read. New DISAGREE rows of steps 2 and 3 are read in full before they are listed, as before. LINKROT and CAMPUS share the old opener. Neither held a 308 on 9 Nov, so neither changes now.
