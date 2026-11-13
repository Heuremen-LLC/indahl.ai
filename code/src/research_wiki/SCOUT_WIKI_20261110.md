# Wikipedia and Wikimedia open data scout

Read on 9 November 2026 (HST), 10 November UTC. Asked: Wikipedia's data is open, is there anything we could use? Scope: open, keyless Wikimedia data a Heuremen LLC desk could reuse, especially where a party states a number or a rule and public data shows what was delivered. No sign-ups, no accounts, no keys were used. Every request carried the User-Agent `HeuremenLLC-research/1.0 (https://indahl.ai)`. Wikimedia's policy accepts a website as the contact, so no email was sent. Samples are in `~/bones-forge/research_wiki/samples/`.

## The short answer

Yes. Almost everything Wikimedia publishes is open with no key. Page views, unique devices, edits and editors come from one API under CC0. The live edit stream, the full history dumps and Wikidata with its public query service are also keyless, and Wikidata is CC0 too. A script that names itself in its User-Agent may make 200 requests a minute.

Tonight's proof runs gave three readings.

1. Wikidata copies official numbers and names the source. 8,155 population values for 169 countries cite World Bank Open Data. Only 1,102 of them (13.5%) match the World Bank's figure today. But 99.8% match some World Bank release exactly. The copies were faithful when made, and the source has revised since. For 27 countries the default population that Wikidata returns is a 2017 World Bank figure last carried by the World Bank's April 2019 release, among the releases we read.
2. The Wikimedia Foundation states its reach on its homepage and publishes the data to check it. "Nearly 15 billion views each month" sits between human traffic to Wikipedia (12.5 billion a month on average over the last 12 months) and all traffic including automated (20.9 billion). "324 new edits" a minute sits between edits without bots (224.5) and with bots (348.7). "Over 67 million articles" holds (68,737,539).
3. Wikipedia is a Very Large Online Platform under the EU's Digital Services Act. Its own harmonised DSA report for January to June 2026 states one moderation measure taken by the Foundation. The DSA Transparency Database lists "Wikimedia" as a platform with zero statements of reasons. The Foundation's stated DMCA counts and the notices it posts agree within one notice per half-year.

## Ranked desk ideas

Ranked by (a) a clear stated side, (b) a keyless delivered side, (c) repeatable or live, (d) not duplicating our desks.

### 1. Copies against the source (Wikidata figures against the source they cite)

The stated number: a Wikidata statement gives a value, a point in time and a reference that names its source ("stated in" World Bank Open Data, a statistics office, a census). Many Wikipedia infoboxes draw on Wikidata, and search engines and language models read it. Every statement is CC0.

The delivered data: the cited source, read now, and the source's own archive of past releases. For the World Bank this is the World Development Indicators API and the WDI Database Archives (source 57). The archive keeps 142 releases, from April 1989 to July 2026. Both are keyless and CC BY 4.0.

The comparison: for each statement, does the value match the source's current figure for the same country and year? If not, does it match an older release exactly? Each statement falls in one bin: matches the current release, matches an older release, within 0.1% of a release, matches no release read, or cannot tell (the source has no value). The desk prints the share in each bin with a Wilson interval, and one of the four outcomes against a threshold fixed in the plan. A stale copy is not an error. The source revises its own history every year, and the page would say so.

Proof run tonight. Population (P1082) of sovereign states (class Q3624078), statements whose reference is "stated in" World Bank Open Data (Q21540096), against 29 World Bank releases read tonight (the current one plus about two a year from April 2012 to July 2026):

| Reading | Statements | Share (Wilson 95%) |
|---|---|---|
| Matches the World Bank's current figure exactly | 1,102 | 13.5% (12.8% to 14.3%) |
| Matches an older World Bank release exactly | 7,034 | 86.3% (85.5% to 87.0%) |
| Within 0.1% of a release read | 10 | 0.1% (0.07% to 0.23%) |
| Matches no release read | 9 | 0.1% (0.06% to 0.21%) |
| Total | 8,155 | 169 countries, years 1960 to 2024 |

Against the current figure alone, 5,458 values (66.9%, 65.9% to 67.9%) differ by 1% or more. The median gap for the stale values is 2.8%. 8,002 of the 8,155 carry no "retrieved" date, so the release can only be found by matching, as we did. 142 of the 169 countries have no World Bank-cited value that matches the current release. For 106 countries the newest World Bank-cited year in Wikidata is 8 years behind the World Bank's newest year, 2025.

The sharpest rows are the defaults. 38 countries have a World Bank-cited population as their preferred value, which is the value a plain query returns. 37 of the 38 carry an older release's figure. 30 of them are 2017 values, and 27 of those were last carried by the April 2019 release among the releases we read. A few, Wikidata's default against the World Bank's current figure for the same year:

| Country | Year | Wikidata default | World Bank now | Gap | Newest release read that carried it |
|---|---|---|---|---|---|
| South Sudan | 2017 | 12,575,714 | 10,259,154 | +22.6% | April 2019 |
| Palau | 2017 | 21,729 | 17,812 | +22.0% | April 2019 |
| Yemen | 2017 | 28,250,420 | 33,090,921 | -14.6% | April 2019 |
| Marshall Islands | 2017 | 53,127 | 46,529 | +14.2% | April 2019 |
| Turkmenistan | 2021 | 6,117,933 | 7,092,043 | -13.7% | July 2022 |

A direct query confirmed the default value for six of these countries. The World Bank's newest figure for Yemen (2025) is 41,773,878.

Caveats that keep this a reading: we read 29 of the 142 archived releases, so the 9 "no release" values may match a release we did not read. This is one property and one source. The match rule is exact to the person, and an importer's rounding would land in "within 0.1%". Wikidata is written by volunteers, not by one party, so the desk names the property and the source, never an editor. Which release the import used is inferred by matching, not stated.

Coverage: the same method works wherever Wikidata cites a source that keeps an API and its own history. World Bank GDP and other WDI series, Eurostat (its JSON API answered keyless tonight), IMF and UN population figures, and company figures that cite SEC filings. The SEC company facts API answered tonight without an email in the User-Agent, but SEC's policy asks for one. The US Census API now requires a key (a keyless call redirected to its "missing key" page).

Not duplicating: REVISE reads one agency's first estimate against its own later revisions. ARXIVDRIFT reads a paper against its later versions. This desk reads a third party's copy against the source. It pairs well with REVISE, because the same archive shows how far the World Bank moved each figure from release to release.

### 2. The Foundation's stated reach against its own data

The stated numbers: the Wikimedia Foundation homepage, "By the numbers", read tonight. "Wikipedia receives nearly 15 billion views each month." "The Wikimedia Foundation supports nearly 265,000 volunteers every month." "Every minute 324 new edits are made to Wikipedia." "With over 67 million articles, in 300+ languages". Lower on the same page and on "Who we are": "nearly 250,000 volunteers". The projects page: Commons has "114 million images, photographs, videos and music files and counting". Under the DSA the Foundation also states average monthly active recipients in the EU per half-year and per member state, built from unique devices and a stated "2.4" devices per person.

The delivered data: the Foundation's own Analytics API, CC0 and keyless. It gives page views per project, unique devices, edits, editors and page views by country. The live edit stream (EventStreams). Each wiki's own site statistics.

The comparison: each stated number against the delivered series for the same scope and period. The interval comes from the scope choices that the statement leaves open, such as human traffic or all traffic, bots in or out, one wiki or all. The plan has to fix a rule for "nearly" and "over" before the first reading.

Proof run tonight. Twelve months, November 2025 to October 2026, unless noted:

| Stated | Delivered | Reading |
|---|---|---|
| "nearly 15 billion views each month" | Wikipedia, all 348 open editions, human traffic: 12.48 billion a month on average, 11.35 (October 2026) to 13.98 (November 2025). All traffic including automated: 20.89 billion on average, 18.78 to 23.29. All projects, human traffic: 12.36 to 14.73 | The stated figure sits between the two scopes. Human-only traffic to Wikipedia is below 14 billion in every month. All-project human views were 15.54 billion in October 2024, 14.45 billion in October 2025 and 12.36 billion in October 2026 (down 14.4% in a year) |
| "324 new edits" every minute | All Wikipedias, every editor type including bots: 348.7 a minute on average, 300.2 to 393.2. Registered and anonymous editors without bots: 224.5, 213.8 to 234.5. Live stream, two minutes from 02:12 UTC on 10 November: 394 a minute with bots, 147.5 without bot-flagged edits | The stated figure sits between the scopes. It matches only if bot edits are counted |
| "nearly 265,000 volunteers every month" and "nearly 250,000 volunteers" | Registered editors with 1+ edits in a month, summed over all 842 open wikis: 329,245 on average (315,636 to 350,712). This counts a person once on every wiki they edit. With 5+ edits: 122,836 (117,580 to 130,181). Wikipedias only, 1+ edits: 251,741 | CANNOT_TELL. The API has no editor count deduplicated across wikis. 265,000 can only fit a 1+ edit definition, because even the double-counted 5+ edit sum is far below it. The two stated figures differ from each other by 15,000 |
| "over 67 million articles, in 300+ languages" | Sum of article counts over the 348 open Wikipedias: 68,737,539 | Holds |
| Commons, "114 million ... files and counting" | Commons file count tonight (site statistics): 150,432,126 | Holds as a floor. The count is 32% above the stated figure |

The volunteers figure may become checkable. Wikitech's page on the MediaWiki history data says that from the 2025-11 snapshot "user_central_id was added as a stable identifier to uniquely a user account globally across all wikis". If the public TSV dumps carry that field (not checked tonight), the desk can count each person once across all wikis, month by month.

The stated block changes over time, so the desk keeps every version. The Wayback Machine capture of 1 November 2025 reads "more than 15 billion views each month", "nearly 260,000 volunteers", "342 new edits" and "over 64 million articles". The capture of 1 December 2025 reads "nearly 15 billion", "nearly 265,000", "324" and "over 65 million". The captures of January 2026 and tonight's page match December, except that the article count is now "over 67 million". The views, volunteers and edits figures have read the same since at least 1 December 2025. Captures are in `samples/wayback/`.

DSA readings on the same desk:

- The harmonised report's EU total for January to June 2026 (157,313,000) equals the sum of its 27 member-state rows. The same holds for July to December 2025 (155,663,000).
- Finland is stated at 2,960,000 in three half-years in a row. Every other member state's figure changes each period, except Latvia, which repeats once. The public unique-device series for Finnish Wikipedia averaged 9,151,622 a month in January to June 2025, 9,189,700 in July to December 2025 and 7,369,475 in January to June 2026. That is a fall of 19.8% in the last half-year. Finnish Wikipedia is not the same scope as readers in Finland, so this is a question for the plan, not a finding.
- Stated EU devices (157,313,000 times 2.4) are 21.0% of global Wikipedia unique devices for the same half-year. EU countries account for 25.8% of all-project human page views in the same months. A higher rate of views per device in the EU would explain that gap. Per-country unique devices are not published, so the stated number cannot be rebuilt from public data. The outcome would be CONSISTENT inside a wide band, or CANNOT_TELL.
- From August 2025 to January 2026 against February to July 2026, the stated EU figures for the smaller projects rose by 1.6 to 4.9 times (Wikivoyage 690,000 to 2,108,000, Wikidata 1,337,000 to 3,513,000). Global unique devices for the same projects rose too, by 1.2 to 2.8 times (Wikidata 2.8 times). The page itself attributes earlier jumps of this kind to automated traffic that passed the bot filter, in July to September 2024 and April to July 2025.
- The page's EU table runs on windows one month later than the report (February to July against January to June). The two Wikipedia totals agree within 11,000 for 2026 and differ by 2.4% and 3.6% for the two previous pairs.
- The harmonised file codes Spain as "SP". The ISO code is ES. A parser keyed on ISO codes would drop Spain. This matters for the SOCIAL desk parser.

Not duplicating: SOCIAL's fifth idea ("Stated users") found no platform that publishes delivered usage. Wikipedia is the one very large platform that does. CADENCE and UPTIME read other parties.

### 3. Wikipedia's DSA filings against the DSA database (a row for SOCIAL)

The stated numbers: the Foundation's harmonised DSA transparency reports for Wikipedia (XLS files in the Commission template, on the Foundation's governance wiki) and its half-yearly transparency report (DMCA notices, takedown requests, user data requests).

The delivered data: the EU DSA Transparency Database (CC BY 4.0, keyless, already pulled for SOCIAL). The DMCA notices the Foundation posts on its governance wiki, by year category, with page creation dates read from the API.

Proof run tonight:

| | Stated | Delivered |
|---|---|---|
| Wikipedia, January to June 2026, measures taken by the provider | 1, not automated, language code FR, taken on a notice. 121 notices received, 5 from trusted flaggers. 2 orders to act from member states | Platform "Wikimedia" (database id 253): 0 statements in the January to June 2026 aggregates (233 platforms, 3,353,954,239 statements). 0 in October 2026. The database search shows "Statements of reasons: 0" for the six months it covers |
| Wikipedia, July to December 2025 | 1 measure. 100 notices. 1 order to act | Not pulled tonight |
| DMCA notices granted, January to June 2025 | 6 of 13 | 7 notice pages posted |
| DMCA, July to December 2025 | 1 of 11 | 1 |
| DMCA, January to June 2026 | 3 of 14 | 4 |

Other stated counts in the January to June 2026 reports: 953 content alteration and takedown requests (2 granted), 40 user data requests (4 granted), 17 internal moderators, 5 internal complaints.

Caveats: on Wikipedia most moderation is done by volunteer communities, and the Foundation reports only its own actions. A statement of reasons is required only in some cases (for example the DSA ties it to known contact details of the affected user). So "1 stated, 0 filed" needs the legal scope rule in the plan before any outcome is printed. With counts this small the interval is about definitions, not sampling: request received against notice posted, and counter-notices (one 2026 notice has one). This ranks third because it is a row for SOCIAL's first idea, not a desk of its own.

### 4. Stated live against live (Wikipedia citations, extending LINKROT)

The stated side: Wikipedia citation templates carry `url-status=live` or `dead` and an `access-date`, and editors tag dead links with {{dead link}}. English Wikipedia counts 363,697 articles with a dead-link tag and 203,001 with a link marked permanently dead (no archive found).

The delivered side: the link, requested now from two networks under LINKROT's rules (a block is not rot, controls run before each pass).

The comparison: the share of links stated live that are gone, and the share of links stated dead that answer. The external links dump (5,036,480,852 bytes, 7 November 2026) and the API give the population. No proof run tonight. It reuses LINKROT's code and rules, so it is cheap to build.

### 5. Stated update dates on Wikipedia pages (CADENCE's shape)

The stated side: editors mark statements with "as of" dates and {{Update after}} dates. English Wikipedia holds 87,741 articles with potentially dated statements and 45,978 tagged as needing an update.

The delivered side: the page history, from the API or the dumps. Did the text change after the stated date?

This is CADENCE's method on a new population. It ranks fifth because the stated party is a maintenance tag, not an institution.

Others considered:

- Page protection logs. Every protection states an expiry, but MediaWiki lifts it automatically, so stated and delivered agree by construction. The protection policy is written in words, not numbers. Dropped.
- Page views as a control series. Daily views per article, CC0 and keyless, from 2015 in the API and 2011 in the dumps. Use them as the control the SOCIAL scout named, never as a measure of use.
- EventStreams as a live witness. Used above for edits a minute. It also streams page deletions and creations, so it could time-stamp provider actions as they happen.
- Wikidata official websites (P856) against live. Overlaps LINKROT and UPTIME.
- Wikimedia Enterprise free tier. Needs an account and a click-through agreement. No desk above needs it.

## Rules that apply to every Wikimedia request

- User-Agent policy: "Scripts should use an informative User-Agent string with contact information, or they may be blocked without notice." "The contact information should be given as an email address, a website, or a wiki user". Our User-Agent gives the website. Source: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
- API rate limits: the table row "User-Agent only", described as "Unauthenticated bot requests with a compliant User-Agent header", allows 200 requests a minute. The row "Unidentified" allows 10. Clients should "limit the number of concurrent requests to 3 or fewer" and "respect the Retry-After header provided with a 429 Too Many Requests status code". "The rate limits described on this page are new in 2026 and are subject to experimentation and change." Also: "If you require high-volume, commercial access: Wikimedia Enterprise APIs are available with free access for all users up to certain speed and volume limits." A desk at our scale stays well under 200 a minute. Source: https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits
- Robot policy: for the REST API, "If unauthenticated, keep the concurrency of your requests to 3 at a time, and below 5 requests per second overall." For the Action API, "keep the concurrency of your requests to 1 at a time, and below 5 requests per second overall." In general, "the maximum concurrent number of requests is fewer than 10 overall, and keep the average requests per second below 20." Source: https://wikitech.wikimedia.org/wiki/Robot_policy
- Terms of Use, prohibited: "Engaging in automated uses of the Project Websites that are abusive or disruptive of the services, violate acceptable usage policies where available, or have not been approved by the Wikimedia community" and "Disrupting the services by placing an undue burden on an API". Tonight's reads ran one request at a time, inside the published API limits. Source: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use
- Licences: "all information on Wikimedia projects may be freely shared, copied, remixed, and used for any purpose (including commercial purposes!) in perpetuity." Text is "licensed under the GNU Free Documentation License (GFDL) and the Creative Commons Attribution-Share-Alike 4.0 License". Wikidata: "Copyrights of structured data in the main, Property, Lexeme, and EntitySchema namespaces are waived using the Creative Commons Zero (CC0) public domain dedication". "All Analytics datasets are available under the Creative Commons Zero (CC0) public domain dedication, unless otherwise specified." Source: https://dumps.wikimedia.org/legal.html

## Access table

"Live check" means fetched tonight from this seat without a key.

| Source | What is published | Format, cadence | Terms for reuse (quoted where found) | Key or account | Usable by an LLC | Live check |
|---|---|---|---|---|---|---|
| Analytics API, page views | Views per article, per project and for all projects, by access and agent, daily and monthly. Top articles. Views by country, rounded up and ranked | JSON, daily | "All Analytics datasets are available under the Creative Commons Zero (CC0) public domain dedication, unless otherwise specified." | None | Yes | Yes. All projects, human traffic, January 2026: 14,340,426,735 views. Top-by-country lists up to 213 countries a month |
| Analytics API, unique devices | Unique devices per wiki and per project family, daily and monthly | JSON | CC0, as above | None | Yes | Yes. All Wikipedias, January 2026: 1,687,332,274. `all-wikidata-projects` returned 404, `www.wikidata.org` works |
| Analytics API, edits and editors | Edits per wiki or project family. Editors per wiki by activity level | JSON, monthly | CC0 | None | Yes | Yes. Editors refuse project families: "all-... project values are not accepted for this metric" |
| Page view dumps (pageview_complete) | Daily views per article since 2011 | bz2 files, daily | CC0 | None | Yes | Listing read |
| EventStreams | Every edit, page creation, deletion and log entry on every wiki, live, with replay from a timestamp | Server-sent events | "WMF's HTTP connection termination layer enforces a connection timeout of 15 minutes." No separate licence on the service page | None | Yes | Yes. 3,518 events in 120 s |
| XML and SQL dumps | Full text and history of every wiki, link tables, logs | XML and SQL, twice a month | Text under "GFDL" and "Creative Commons Attribution-Share-Alike 4.0" | None | Yes, with attribution and share-alike for text | Listing read. English Wikipedia external links dump 7 Nov 2026 |
| MediaWiki history dumps | Every revision, user and page event, one snapshot a month | TSV.bz2 | "All Analytics datasets are available under the Creative Commons CC0 dedication." | None | Yes | Listing read. Latest snapshot 2026-10 |
| Geoeditors | Editors per country per wiki, bucketed | TSV, monthly | CC0 (Analytics dataset) | None | Yes | Listing read. Latest October 2026 |
| Wikidata Query Service | SPARQL over all of Wikidata | JSON, live | Data CC0. Limits: "One client (user agent + IP) is allowed 60 seconds of processing time each 60 seconds", "30 error queries per minute", "access to the service is limited to 5 parallel queries per IP", and a 60 second deadline | None | Yes | Yes. 8,155 rows in 1.8 s |
| Wikidata entity JSON | One item with all statements and references | JSON | CC0 | None | Yes | Yes. Q30, 1.8 MB |
| Wikidata dumps | All entities | JSON and RDF, twice a week | CC0 | None | Yes | Listing read. latest-all.json.gz dated 6 Nov 2026 |
| Action API on each wiki | Logs (protection, deletion, blocks), categories, site statistics, revisions | JSON | Robot policy, quoted above | None | Yes | Yes |
| Wikimedia Enterprise | Current rendered HTML and structured content, snapshots and on-demand | API | Free account, Snapshot API: updates "Monthly", requests "up to 30/mo", snapshot chunks "up to 1,500/mo". On-demand API: requests "up to 50,000/mo". Agreement: "limited and revocable license to use and access the Enterprise APIs on a trial basis". Wikimedia keeps "the exclusive right to use such Aggregate Data and Analyses for any purpose" | Account and click-through agreement | Yes, after sign-up | Pricing and terms read. Not used |
| Enterprise HTML mirrors on the dumps site | Rendered HTML, archive only | tar.gz | "as of 24 March 2025, are no longer replicated on this site" | None | Archive only | Listing read. Last run 20 March 2025 |
| Foundation transparency report | User data requests, takedown requests, DMCA notices, by country and project | Web pages, half-yearly | "Except where otherwise noted, the content of this site is licensed under a Creative Commons Attribution-ShareAlike 4.0 International license." | None | Yes | Yes. January to June 2026 |
| Foundation harmonised DSA reports | Notices, orders, measures, moderators, complaints, EU recipients, per project | XLS in the Commission template, half-yearly | Statutory. We quote the number and link it | None | Yes | Yes. Wikipedia, July to December 2025 and January to June 2026 |
| DSA userbase statistics page | EU monthly active recipients per project family and per member state | Wiki page, half-yearly | CC BY-SA (wiki text) | None | Yes | Yes |
| Posted DMCA notices | Each granted notice, in year categories | Wiki pages and PDFs | CC BY-SA (wiki text) | None | Yes | Yes. 13 notice pages for 2025 and 2026 |
| EU DSA Transparency Database | Statements of reasons from every platform | See the social scout | CC BY 4.0 | None | Yes | Platform list read. "Wikimedia" is id 253, 0 statements |
| World Bank WDI API and WDI Database Archives | Indicators by country and year, 142 archived releases | JSON | "licenses datasets under the Creative Commons Attribution 4.0 International license (CC-BY 4.0)", which "allows users to copy, modify and distribute data in any format for any purpose, including commercial use" | None | Yes | Yes. WDI last updated 8 Oct 2026. 29 archive releases pulled |
| US Census API | Census and survey tables | JSON | Public domain | A key is now required | Yes, with a free key | Keyless call redirected to "missing_key.html" |
| SEC company facts | XBRL facts per company | JSON | SEC asks bots to declare "User-Agent: Sample Company Name AdminContact@<sample company domain>.com" | None, but a contact email is requested | Yes | Answered HTTP 200 without an email |
| Eurostat API | European statistics | JSON | Not read tonight | None | Yes | Yes. tps00001 |
| Wayback Machine capture index | Past versions of a page (used here for the homepage's stated numbers) | JSON index and archived pages | Not read tonight | None | Yes, as a dated witness | Yes. 35 monthly captures listed, 2024 to 2026. Three captures could not be fetched (timeouts) |

## Keys and accounts Wayfinder would need

None for the top three desks. All of them run on keyless CC0 or CC BY 4.0 data.

Optional, in order of use:

1. A non-personal company address for the SEC User-Agent, only if desk 1 adds company figures. SEC answered without one tonight, but its policy asks for one.
2. US Census API key. Site: https://api.census.gov/data/key_signup.html. Free. Only needed to add US census figures to desk 1.
3. Wikimedia Enterprise free account. Not needed for any desk above. Current rendered HTML of every article now sits behind it, since the keyless mirrors stopped in March 2025. Read the agreement first, including its aggregate-data clause.

A Wikimedia login would not help. New accounts get the same 200 requests a minute, and only established editors get 2,000.

## What we did not do

We did not log in anywhere, accept any terms, or sign up for Wikimedia Enterprise. We did not edit any wiki, and we did not edit the site. We did not download the full history dumps or the full Wikidata dump, because the APIs answered every question tonight. All three proof runs are raw readings. Each needs a plan with its scope rules committed, and a referee pass, before any surface uses it.

## Files

- `samples/cited/wikidata_pop_worldbank.json`: the 8,155 Wikidata statements (SPARQL result)
- `samples/cited/worldbank_SP.POP.TOTL.json`: World Bank population, current release
- `samples/cited/wdi_archive/`: 29 archived World Bank releases (gzipped JSON)
- `samples/cited/cited_compare_rows.json`, `samples/cited/cited_vintage_rows.json`: per-statement outcomes
- `samples/reach/`: Analytics API pulls (wide series, per-Wikipedia views and article counts, per-wiki editors, Commons statistics, Finnish and Latvian Wikipedia unique devices)
- `samples/eventstreams/rc_120s.sse`: two minutes of the recent-change stream, with start and end times
- `samples/dsa_wmf/`: Wikipedia harmonised DSA reports, July to December 2025 and January to June 2026
- `samples/dmca/`: posted DMCA notice categories and page creation dates
- `samples/pages/`: terms, policies and report pages as fetched tonight (HTML and text)
- `samples/enwiki_*.json`: dead-link, dated-statement and protection-log samples
- `samples/wayback/`: capture index and archived copies of the Foundation homepage
- `tools/wgrab.py`: page fetch and quote helper
- `tools/reach_proof.py`, `tools/reach_score.py`: desk 2 pull and scoring
- `tools/cited_compare.py`, `tools/cited_vintage.py`: desk 1 comparison against the current and archived releases
