# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 16:40 FOLLOW CHANNELS (indahl.ai/follow): calendar of source release dates, per-organisation feeds, WebSub, newsletter feed, JSON Feed, webhooks, device notifications, OPML, changelog
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no new reading. The channels carry the change rows live_headlines.py already writes, the same rows as the desk change feeds and the outcome alerts
- II: n/a: no flip is counted. A change row is sent as it stands in the ledger
- III: n/a: no sign or product is read
- V: n/a: no ruler. The calendar prints dates, not readings
- VI: holds: the outcome words in webhooks, notifications and organisation feeds are the four the desk feeds print (changes_feed.WORD), taken from the same function
- R: holds: release dates read on 10 Nov 2026 from the sources' own schedule pages and copied into indahl-ai/notify_schedules.json with the page URL and read date: EIA STEO release schedule (eia.gov/outlooks/steo/release_schedule.php, Dec 2026 to Dec 2027), NOAA CPC long-lead schedule for 2026 (cpc.ncep.noaa.gov/products/predictions/schedule.php, 19 Nov and 17 Dec 2026, CPC says its 2027 list comes on or about 2 Dec 2026), NHC season dates (nhc.noaa.gov/climo/, Atlantic 1 June to 30 November, eastern Pacific 15 May to 30 November), FOMC calendar meetings marked with a Summary of Economic Projections (federalreserve.gov/monetarypolicy/fomccalendars.htm, tentative until confirmed, as the Fed says). REVISE left out: bls.gov refuses automated reads of the Employment Situation schedule. FLU left out: no stated release schedule found in the FluSight hub
- P1: holds: each event description quotes the source's own statement of time and status (EIA noon to 12:15 ET, CPC about 8:30 ET, Fed tentative dates)
- P2: holds: every event carries the schedule page as URL and in its description, the gate (notify.py --gate) refuses an event without an https URL
- P3: holds: page headings are names (Follow, Webhooks, Changelog), no counts
- P4: n/a: no cause named
- P5: n/a: no interval printed
- P6: holds: no date is projected past what the source lists (the NHC season dates for 2027 follow from NHC's own fixed season statement)
- P7: holds: no public number of ours changes, so no ledger row. The schedules file is the record of what was read, with its URLs. Released through ledger/ship.sh under site_lock
- P8: cannot tell before the ship: the live .ics and feeds are parsed after the ship with icalendar and feedparser
- P9: holds: plain sentences, no semicolons, no AI statements (site gate 0 on the test build, notify gate 0)
- P10: holds: the changelog prints release commit messages as written, from 10 Nov 2026, leaving out any message with a house word or the words the filter in notify.py commits() lists
- O1: holds: two new tick-bus riders, webhooks_send.py and push_send.py, every tick, each with its own run lock and first-run seen marking (nothing historical sent). WebSub pings ride ship.sh step 7b and ledger/changes_feed.py push
- O2: holds: senders tested in scratch against a local listener: signed POST verified with the page's own snippet, Slack shape, retry at +300 s, turned off at 10 in a row with the KV record and manage page reading it, push encrypted with pywebpush and decrypted with http_ece, VAPID JWT verified, 410 deletes
- O3: n/a: no GPU
- O4: holds: failures write notify_state/<name>_status.json and watch/alerts_check.py 2d opens an alert for Bones
- O5: holds: webhooks_send.py and websub_ping.py run on the bus's /usr/bin/python3 3.9, push_send.py on notify_state/venv (pywebpush 2.5.0). Absolute paths
- O6: n/a: no GPU job

## 2026-11-10 12:20 LIVE HEADLINES: one live_headline ledger row per live desk headline (cold read row 12), check_ledger reads each against its feed, value rows on a material change only
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is a headline whose number moved inside its previous interval, planted in live_headlines.py selftest, and it writes no row. A move outside, an outcome flip and a change in a field the plan's rule reads each write one
- II: holds: no rate is read here. The rows record where a number comes from and when it moves enough to keep. The live value is never compared by the gate, by design, since it moves on every read
- III: n/a: no sign or product is read. The change rule is a test on one reading against the previous value row
- V: holds: two rulers side by side where a desk prints both, the flip of the four outcomes and the move outside the previous interval. A desk without a width uses its plan's own stated rule, and a desk with neither says so in its row
- VI: holds: the outcome flip is read only between the four labels ABOVE, BELOW, CONSISTENT and CANNOT_TELL. A desk with no outcome (TAPE) writes no value rows and its row says so
- R: holds: feed fields read from the live feeds at 12:05 UTC on 10 Nov, every field present on all 21 feeds. Rider periods read from watch/tick_bus.py and their wall times measured from watch/ticks.log since 3 Nov (median tick 5.5 min). Plan cadence and rule lines read from each PLAN.md
- P1: holds: rule text in each row quotes the plan's line numbers, and Wayfinder's word on WATER is quoted as given
- P2: holds: each row names its feed URL, the JSON path of the headline number, the stamp it is read by, and the producer function in watch/headlines.py
- P3: holds: the surface snippet of each row is the desk page's own question heading, read from the built page
- P4: holds: no cause is named. A stale feed is reported as stale, with the stamp and the limit
- P5: holds: each value row prints the interval the desk prints, and says which one (Wilson on the unit the plan names, or bootstrap where the plan names it)
- P6: holds: a value row records the published headline line beside the reading, no stronger
- P7: holds: rows enter the ledger before any surface change, through one release path, ledger/ship.sh
- P8: holds: the check reads the live feeds the pages read, with a cache-busting query
- P9: holds: no public copy is added by this entry. The row text is internal ledger text
- P10: holds: the cadence choices are labelled as read from the rider and the plan, and rounding up to the quarter or half hour is said in each row
- O1: holds: the writer is ledger/live_headlines.py run. The tick-bus line is proposed, not added, since tick_bus.py is not ours to edit in this pass
- O2: caught: at 12:05 UTC SECRECORDS read 10.2 h old against its 9 h limit and SUPPORT 8.9 h against 6.75 h. Both riders missed one fire, at tick 26970 and 26976, caught-up cycles the bus logs as none and runs no rider on. SUPPORT's next fire ran at tick 27024. The missed SECRECORDS pass was run by hand with the rider's own command
- O3: n/a: no GPU used, network reads only
- O4: holds: liveness is the feed's own stamp, the time of the read that wrote the number, never a running process
- O5: holds: absolute paths, Python 3.9 compatible (selftest run under the bus's /usr/bin/python3 3.9.6 and homebrew python)
- O6: n/a: no GPU job, network reads only

## 2026-11-10 10:30 NEWSLETTER AUDIT FIXES, HERMES and ATLAS: plan-rule readings for SUPPORT, TRIALS, AIRQ and CADENCE, both intervals on REVISE and WIKI, NEO dependence clause, CHANGE outcome dropped, Lenovo one rank rule, ATLAS beside figure, missing rows
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: fixed: each changed reading keeps the old one beside it, like for like on the same read. SUPPORT old rule 127 of 512 against the plan's 103 of 428 on the 14:43 UTC pull, TRIALS 5,019 of 22,580 against 4,775 of 22,185 on the 11:53 read, CADENCE 633 of 1,219 against 633 of 1,229 on the same stored files, AIRQ lower tie against upper tie on the same pairs, Lenovo all-edge rank against same-accelerator rank on the same file
- II: holds: no flip is netted. Every outcome that moves is named: Lenovo LN1, LN4 and LN9 BELOW to CONSISTENT, the tally 5 BELOW to 2 BELOW. No desk headline outcome moved: SUPPORT ABOVE, TRIALS CANNOT_TELL, AIRQ ABOVE and CANNOT_TELL under both ties
- III: n/a: no sign or product is read. Shares and counts only
- V: fixed: two rulers side by side where they disagree. REVISE months ABOVE beside calendar years CANNOT_TELL [0.10, 0.33], the plan names months. TRIALS Wilson beside the sponsor-clustered interval. WIKI Wilson beside countries, the countries interval quoted. NEO Wilson BELOW beside the reading without the 9 Feb 2024 copy, CONSISTENT
- VI: holds: four outcomes kept, each against the plan's thresholds. CHANGE lifespan carries none, as the plan's Addendum 1 says, and its value row now records COUNT
- R: holds: counts read from the desks' own files by the desks' own code after the fix. trials_index/data/records.jsonl read 11:53 UTC, endoflife.date pulled 14:43 UTC, airq_index/data/w2026/pairs.json, cadence_index/data portal files of 10 Nov, mlperf_index/raw/inf_5.1.json, atlas/raw/epoch with EIA-861 2024 prices. Frozen copies in research/nl_audit_fix_20261110/feeds. Post hoc: every rule written today is labelled with its date on the page and in a plan addendum
- P1: holds: no vendor or agency quote is changed. Lenovo's own words stay as quoted in claims_lenovo_v51.json
- P2: holds: every figure names its file. Desk feeds and frozen copies for live numbers, scale_rows_text.txt for ATLAS, shipped_20261110_wiki_live.json for WIKI, sad_claims.json for MODEL
- P3: fixed: the registry class OTHER_GOV is named state, local and non-US public bodies, as the registry defines it, never government sponsors in general
- P4: holds: no cause is named for any count. The Lenovo correction says which rule changed and that it favours the vendor
- P5: holds: each interval says what it is: Wilson on records, sponsor-clustered on lead sponsors, bootstrap over products, bootstrap over calendar years, countries resampled
- P6: fixed: no headline is stronger than its plan. NEO says the below reading rests on one copy. AIRQ leads with both readings, the plan names neither. CADENCE prints nearly 16 years, not 16
- P7: holds: ledger rows first, then pages, through ledger/ship.sh only
- P8: cannot tell: the rendered pages are checked after the ship by the copies.py live step and a fetch of each feed. Not before
- P9: holds: public copy in plain sentences, no semicolons, no AI statements
- P10: holds: post hoc rules are labelled defined or stated on 10 Nov 2026, after the data, on the page and in each plan addendum (TRIALS 5, SUPPORT 3, AIRQ 5, CADENCE 2)
- O1: holds: no new rider. The desks' existing tick-bus riders run the changed code on their next fire
- O2: caught: the SUPPORT code tested cycles whose support end had passed, the TRIALS code scored the lag zone, the CADENCE code read R/P3.5D as unreadable and let file order pick a cadence. Each is called a departure from the plan in its addendum
- O3: n/a: no GPU used, network and file reads only
- O4: holds: liveness is each feed's own stamp
- O5: holds: absolute paths in every command, the desks run under the tick bus's python as before
- O6: n/a: no GPU job, network and file reads only

## 2026-11-10 15:45 NEWSLETTER ISSUE 0 on the web (indahl.ai/newsletter/0): one ledger row per number in the issue, each read against its desk's live row and the live page at publish time
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no new reading. Every number in the issue is a number a live desk row already carries, quoted from that row's own source line
- II: n/a: no flips are counted in the issue. The issue quotes desk headlines and counts as they stand on the live pages
- III: n/a: no sign or product is read. Counts and shares only
- V: holds: where the desk prints two rules the issue prints both. OY prints the rule written before the read (10 of 148) beside the rule set after the first 41 schools (3 to 4 of 148)
- VI: holds: no outcome is restated beyond its desk. WATER below, NEO below with the copy named, QIA above, as on the live pages read 15:17 UTC
- R: holds: counts read at 15:17 UTC 10 Nov from the live pages /oy /qia /water /cadence /neo and from the rows oy.s0_*, water.band6.*, neo.cell.all, neo.dep.copy20240209, live.cadence.v20261110T120408Z, media.gate_*. The OY second rule is labelled as set after the first 41 schools
- P1: n/a: no quote of a third party in the issue
- P2: holds: every number names its desk page by address in the same paragraph (indahl.ai/oy, /qia#gates, /water, /cadence, /neo)
- P3: holds: the OY unreached wording follows the live page (refused our reader or need a login), fixed from blocked our reader alone
- P4: holds: no cause is named for any gap. The issue says we name no cause
- P5: n/a: the issue prints no interval. The intervals stay on the desk pages it links
- P6: fixed: the QIA line carries no run count, since the live /qia table still lists the earlier runs and the fix that adds the two missing runs has not shipped. Every run listed on the live page reads above for both gates
- P7: holds: rows written held before the page, flipped to live in the ship step under ledger/.site_edit.lock, released through ledger/ship.sh only
- P8: cannot tell: the rendered page is checked after the ship by a fetch of indahl.ai/newsletter/0. Not before
- P9: holds: plain sentences, no semicolons, no AI statements, no counts of our own things in any heading
- P10: holds: the OY rule set after the data is labelled as such in the issue, in the words the OY page uses

## 10 Nov 2026: status "staged" (Bones)
A new desk's ledger rows are written as status "staged" until the desk's first ship. check_ledger skips staged rows both ways (neither MISSING nor ZOMBIE), and receipts.py builds no public receipt for them. In the ship step, under ledger/site_lock.py, the desk flips its rows staged -> live and then runs ship.sh. "held" keeps its old meaning: a shipped number taken out for a re-read, which must not be printed. 71 rows (flu, steo, seasonal, quake, tornado, cone, now, rank) were moved held -> staged today.

## 2026-11-10 17:10 ACCOUNTABILITY (indahl.ai/security/self, /verify, /transparency, /r/alert/, /reproduce, /security/policy, /security/thanks, /mydata): SECRECORDS on our own domains, signing key, alert receipts, transparency counts, canary
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none on /security/self is NOT_COMPARABLE, the desk's own label for a header that states no preload or a domain with no SPF record, printed as the desk prints it. On /transparency a count of nothing is a cell under 5 and reads fewer than 5, never zero
- II: n/a: no flip is counted. Counts on /transparency are tallies of sender log lines, receipt lines and KV keys gone since the last pass
- III: n/a: no sign or product is read
- V: holds: the SECRECORDS rulers are the desk's own functions (hsts_class, spf_class, doh), read from secrecords_tick.py as written, not copied. The header table beside it is labelled as not a desk claim
- VI: holds: AGREE, DISAGREE and NOT_COMPARABLE only, the desk's labels, with the desk's own reason text
- R: holds: read 10 Nov 2026 about 22:00 UTC from the Mac through ?door=1 (the outside view), saved as indahl-ai/security_self_before.json and security_self.json. heuremen.com answers with a Cloudflare 301 to indahl.ai before the worker runs, so its first-response HSTS is not ours to set in code. heuremen.org is GitHub Pages
- P1: holds: every label on /security/self is the desk's word for the reading in security_self.json, the gate (accountability.py gate) refuses a page whose labels differ from the file
- P2: holds: DMARC reporting addresses are masked as (a reporting address) on the page, the record is otherwise printed as read
- P3: holds: headings are names (Verify, Reproduce, Transparency, Our Own Records, Reporting Policy, Thanks, Your Data), no counts (site gate 0)
- P4: n/a: no cause named
- P5: n/a: no interval printed. Alert receipts print the ledger row's interval as it stands
- P6: holds: nothing projected. Transparency counts the last 30 UTC days and says so
- P7: holds: ledger rows security.self.* (six labels) and security.signing_key.kid, staged, flipped to live inside the ship command. Transparency counts are a live feed (KV transparency), not ledger rows, as the live desk feeds are
- P8: cannot tell: before the ship, signatures are checked live after the ship in Python and Node against the published key, the CSP is read in a browser on each page type
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC (site gate 0, accountability gate 0 on the test build)
- P10: holds: alert receipts carry only desk, before, now, interval, ledger row id and hash, times and channel kinds. alert_receipts.check_public refuses an address, a URL off indahl.ai, an endpoint or a token, and the transparency writer refuses any integer under 5
- O1: holds: three new riders, alert_receipts.py (every tick), canary.py (every 3), transparency.py (every 12), each with its own lock or idempotent writes. KV writes only on change for receipts
- O2: holds: tests in scratch: signature round trip Python and Node, guard refuses a staged row, canary dry run catches a missing delivery, suppression selftest
- O3: n/a: no GPU is used here
- O4: holds: a refused alert, a canary problem or a failed count write sets notify_state/<name>_status.json ok false and watch/alerts_check.py 2d opens a Bones alert
- O5: holds: bus python 3.9 standard library, signing through node when the cryptography package is absent (sign.py)
- O6: n/a: no GPU job is started

## 2026-11-10 18:30 REPRODUCE KITS (indahl.ai/reproduce, reproduce/<desk>/ in the public repository): one kit per desk headline that recomputes the number and its label offline, and a ship gate that reruns every kit
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is a corrupted input. reproduce_kits.py selftest flips one byte of one input of a kit and the kit's own run refuses it by name (input differs from the one the desk read), and the untouched kit passes
- II: n/a: no flip is counted. A kit reprints a headline the desk already published, field for field
- III: n/a: no sign or product is read. The kits rerun each desk's own counts, intervals and outcome rules
- V: holds: the ruler of each kit is the desk's own, run unmodified (trials_summary.py, seasonal_tick.py, solar_tick.py, flu_tick.py, steo_tick.py, neo_tick.py with the clock pinned) or copied line for line into an extract that names the lines it follows. The gate holds each kit against three records side by side: its own expected output, the headline the live feed served when the kit was made, and the desk's current ledger value row under live_headlines.py's own material-change rule
- VI: holds: the labels a kit prints are the desk's four (ABOVE, BELOW, CONSISTENT, CANNOT_TELL), and a kit whose label differs from the ledger row refuses the ship
- R: holds: every kit was made on 10 Nov 2026 between 18:00 and 18:30 local time from the files on disk and checked against a fresh read of https://indahl.ai/<desk>/live.json, every field of the headline equal (value, display, n, of, lo, hi, outcome, key fields). Feed stamps, read times and feed sha256 are in each kit's published.json. 24 kits, 9 desks listed without a kit with the reason
- P1: n/a: no quote of a third party is added. Source names and terms in each kit README are copied from tools/desk_pack.py
- P2: holds: each kit names its inputs with path, size and sha256, its code with sha256 and the public copy, the feed address and stamp it reproduces, and the expected output sha256. /reproduce prints the expected output sha256 and the time each kit was last verified
- P3: holds: headings are names (Reproduce a desk headline, Desks whose headline cannot be rerun), no counts (site gate 0 on the test build)
- P4: n/a: no cause named
- P5: holds: no interval is printed on /reproduce. Each kit prints the interval the desk prints, under the field name the ledger reads
- P6: holds: /reproduce says what a kit reproduces (the headline at a feed stamp) and that the live page can move inside the interval between releases, the ledger's own rule. Where a kit starts from a stored intermediate (scored rows, an aggregate) its README says so and names what built it
- P7: holds: ledger row reproduce.kits written staged before the page change and flipped to live inside the ship command. Released through ledger/ship.sh under site_lock only. No public number of ours changes
- P8: cannot tell: before the ship, the /reproduce table and the desk links are read in a browser at phone width after the ship, and the kits are rerun from a clean clone of the public repository
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC (site gate 0, accountability gate 0 on the test build)
- P10: holds: licences follow tools/desk_pack.py exactly. A desk whose pack is results-only gets a fetch-and-verify kit with no source data in it, and reproduce_kits.py refuses to load a spec that breaks this. Inputs of those kits stay in ~/bones-forge/reproduce_kits/private and are never mirrored
- O1: holds: no new rider. ship.sh step 1 runs reproduce_kits.py refresh (remakes a kit only when the ledger row or the live feed has moved past it, or the desk code changed) and step 3 runs reproduce_kits.py gate. push_public.sh copies the kits to reproduce/ in the public repository
- O2: caught: running a desk's tick in a kit could push to live KV (most ticks end in wrangler kv put with no guard), so no tick runs in a kit except the forecaster ticks with --offline and no --publish, and every kit step runs with its proxies pointed at a closed port. Caught while building: NEO's scoring also reads its SBDB and designation caches with --no-sbdb, and PKGLICENSE does not store the list of names it scored (its summary-only mode reads the wrong list, 699 against 704)
- O3: n/a: no GPU is used
- O4: holds: a kit counts as verified only when its run in an empty folder prints its expected bytes, and the gate writes the verified time per kit
- O5: holds: absolute paths, standard library in the engine and runner, Python 3.9 compatible. STEO's kit runs under the desk's own venv (xlrd), named in its README
- O6: n/a: no GPU job is started

## 2026-11-10 23:40 FOLLOW ANY COMPANY OR NAMED THING (indahl.ai/alerts, /brand/<slug>, /e/<kind>/<slug>, Follow beside names): entity index, en follows, brand pages by division, bell pass
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no new reading. Entity pages copy rows the desks and pages already publish
- II: n/a: no flip is counted. A row about a followed thing is sent when its stated figure or outcome moves, a row is added or no longer listed, or a section whose heading names it changes
- III: n/a: no sign or product is read
- V: n/a: no ruler
- VI: holds: outcome words are the desks' own, copied cell for cell (brands.py cells, page rows as the page shows them)
- R: holds: rows read from the build's own pages and the desks' feed snapshots at build, and by the sender from the public mirror and brands.py feed snapshots
- P1: holds: entities gate refuses an entity page whose copied cells are not on the source page as built, and a brand-page row cell not traced to its rows
- P2: holds: names matched exact case and whole word, with a stoplist of names that are also common words or surnames, a name that is the tail of a longer proper name skipped
- P3: holds: headings are names (Rows about X on other pages, Named on these pages, Sections about it), no counts (site gate 0)
- P4: n/a: no cause named
- P5: n/a: no new interval
- P6: n/a: nothing projected
- P7: n/a: no public number added. Cadence label (about every 30 minutes) is the sender's own read interval
- P8: holds: tests in scratch: worker harness 44/44, sender scenario (Falcon section change reaches the Falcon follower only, IBM QIA row reaches the IBM follower, cosmetic rebuild with bells sends nothing, no resend, daily digest once), hooks unit test (guarded rows left unseen and retried, email_sent gets outcome changes)
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC, privacy 2026-11-10g
- P10: holds: the record gains en (entity ids) only. Entity events are not put on the public alert receipts
- O1: holds: the sender reads the desks' feeds for named things at most every 30 minutes and the mirror only when a release changes it, state in outcome_alerts/entities_state.json, first pass seeds and sends nothing
- O2: holds: bell gate: each served page byte for byte the built page without its Follow links, none outside main or in a masked region, nested masked blocks refused
- O3: n/a: no GPU
- O4: holds: a gate failure stops the ship, a guard refusal opens the Bones alert through alert_receipts
- O5: holds: standard library only
- O6: n/a: no GPU job

## 2026-11-10 19:40 REPRODUCE FOLLOW-UP: kits for AIRQ, AILUMINATE and TORNADO, the clock pinned in every kit that runs a desk tick, a publish guard on every desk tick's KV put, PKGLICENSE summary-only name list, NEO --no-sbdb, REVISE keeps the BLS flat file
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none of the publish guard is a tick run with no flag and no scheduler, tested on the guard text in three modes (no flag: not put, --publish: put, HEUREMEN_PUBLISH=1: put and passed on), and a copy of the PKGLICENSE tick run in a temp folder printed the guard line and published nothing
- II: n/a: no flip is counted. Each new kit reprints a headline the desk already published, field for field
- III: n/a: no sign or product is read
- V: holds: each new kit runs the desk's own code or copies its scoring lines as written (AIRQ stage A and E, AILUMINATE parse functions and test A, TORNADO the tick itself), held against the live feed, the ledger value row and the live feed again at the gate
- VI: holds: the labels are the desk's own, AIRQ ABOVE, AILUMINATE CONSISTENT, TORNADO ABOVE, equal to the ledger rows live.airq, live.ailuminate and live.tornado
- R: holds: kits made 10 Nov 2026 about 19:10 to 19:40 local time against fresh reads of each live feed. PKGLICENSE: the live page and the rider's full run read 7 of 704. Only the summary-only path, which no rider runs, read 699, so no published number was wrong and no correction is due. Caught after midnight UTC: the SOLAR kit printed another headline once the date changed, since the tick reads the clock for settled days. Every kit that runs a desk tick now pins the clock to the run's own generated time (clock_run.py) and SOLAR reproduces its first hash again
- P1: n/a: no third-party quote is added
- P2: holds: each new kit lists its inputs with sha256 and sources (AILUMINATE also the sha256 its read log records for the page and every PDF)
- P3: holds: no new headings with counts, site gate 0 on the test build
- P4: n/a: no cause named
- P5: n/a: no interval is printed on the page
- P6: holds: the no-kit entry for REVISE says the flat file is kept from the next read on, nothing stronger
- P7: holds: no public number changes, so no new ledger row. reproduce.kits (live) covers the new kits. Released through ledger/ship.sh under site_lock
- P8: cannot tell: before the ship. After it, every live feed is read again for a fresh stamp and the kits are rerun from a clean clone of the public repository
- P9: holds: plain sentences, no semicolons, no AI statements in the new copy
- P10: holds: AIRQ, AILUMINATE and TORNADO are fetch-and-verify kits. AIRQ and AILUMINATE are results-only packs (PurpleAir and MLCommons terms), TORNADO's inputs are about 550 MB of public domain files, more than a public kit carries
- O1: holds: no new rider. watch/tick_bus.py, watch/house_clock.py and qia_mirror/audit_cycle.sh (the six-hourly launchd job) each export HEUREMEN_PUBLISH=1 to what they start (one line each). The guard also covers watch/headlines.py, watch/activity_check.py and watch/desk_progress.py, the HOSTS and QIA queue ticks start headlines.py only when publishing, NAS and the watch writers record a put only when it happened, and TAPE copies to the public mirror and pushes only when publishing. The bus restarts itself on the edit (launchd KeepAlive) and came back at 19:01 local time
- O2: caught: the read-only referee found audit_cycle.sh would have stopped putting three QIA feeds, an unguarded headlines.py started by two ticks, and a NAS state file written on a put that did not happen. All fixed before the ship. Operational tools that are not ticks (indahl-ai/inquiries.py, replies/reply_review.py, darkwave_daily/push_tables.py, qia_runcheck/push_index.py) are left as they are and named here. The gate refused two kits during this work, as it should. SECRECORDS: a pass was rewriting its data mid-run, so the kit could not be remade against the live feed. The gate now refuses only drift in code a kit runs, and notes drift in the desk files an extract follows. SOLAR: the date change above
- O3: n/a: no GPU is used
- O4: holds: liveness after the guard is read from each feed's own stamp. UPTIME, TIME, CADA and FORECAST were put to KV at 00:06 UTC by guarded ticks after the bus restart, and the jobs log shows no guard refusal
- O5: holds: absolute paths, Python 3.9 compatible guard text, the AILUMINATE kit runs under the desk's revise venv (pypdf 6.21.4)
- O6: n/a: no GPU job is started
