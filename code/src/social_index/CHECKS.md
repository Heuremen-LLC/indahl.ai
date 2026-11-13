# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 07:45 SOCIAL ship: ledger rows for the ad spend headline (31 of 6,160) and the section outcome tallies (DSA, ad spend, TikTok, Bluesky), page at /social under HERMES, data files /social/*.json
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: no new reading. Each section is its referee-cleared reading (DSA, ad spend, TikTok with its fixes, Bluesky after the completed replay). The Bluesky section was re-rendered from the stored replay with --no-fetch: rows and series in bsky.json equal the referee build exactly, only copy changed. Each summary is frozen as shipped/shipped_20261110_summary_<key>.json
- II: holds: every ledger row is one count from an outcome tally as the section summary holds it. Nothing is netted, above, below, consistent, cannot tell and nothing returned stay apart
- III: holds: the ledger rows carry no signed gap. Gaps stay on the section rows as the referees left them
- V: holds: the ledger rows are counts, not shares or intervals. Bluesky ranges say they are the spread of the counting rules, not a sampling interval, as cleared
- VI: holds: all five outcomes kept apart in the outcomes table and in the ledger rows. No outcome was changed at ship. The TikTok reading defined after the data is its own row, labelled, and not in the headline
- R: holds: every ledger value is read from a frozen summary by an exact grep string. check_social.py --gate: every page number found in its summary or data files, 0 unexplained, site gate pre-flight 0 hits
- P1: holds: section quotes are the referee-cleared text, placed byte for byte (check_social step A, four sections)
- P2: holds: every section links its data file at /social/<file>.json, each published through a copies.json entry (DSA rows, DSA summary, DSA automation, ad spend rows, Bluesky rows, page summary). TikTok links no data file
- P3: holds: labels and measure names are as each section's referee pass left them. "trusted flagger" is the DSA Article 22 term, kept verbatim, with a narrow exact-phrase exemption in tone_scan.py
- P4: holds: no cause is named on the page or in any ledger claim. The Bluesky "since" clauses describe the counting rule and the stream mechanism, as the referee read them
- P5: holds: every interval on the page says what it is (Bluesky range across counting rules, ad spend timing bands) as cleared
- P6: holds: the headline 31 of 6,160 is built with the page from the frozen ad spend summary (decided rows that rest on no rule set after the data), so it cannot run ahead of the body
- P7: cannot tell: ledger rows go in before the page carries the numbers and the release goes only through ledger/ship.sh. The live check is the next entry
- P8: holds: indahl-ai/build_site.py takes the headline block and body of social.html and wraps them with page() (nav, division line, footer, reference code). Menu entry SOCIAL under HERMES after WIKI. The rendered live page is checked in the next entry
- P9: holds: plain sentences, no semicolons in visible text, no counts of our own things in titles, headings or lead, no AI statements, we pronouns, Heuremen LLC (check_social step G)
- P10: holds: every reading defined after the data keeps its label from its referee pass (ad spend itemization rule, TikTok column, DSA rows)
- O1: cannot tell: no tick bus rider is set up at ship. Rider lines for the four section ticks are proposed to Bones, not applied
- O2: holds: each tick prints a failed gate as FAILED and turns outcomes to cannot tell (Bluesky planted world, DSA and TikTok gates), as the referees checked
- O3: n/a: no GPU used, the desk is HTTP reads, a websocket replay and Python scoring on the CPU
- O4: holds: each summary stamp is YYYY-MM-DD HH:MM UTC, the time the reading was scored, and the outcomes table prints it
- O5: holds: build and check run as python3 -I from absolute paths, copies.json paths are relative to ~/bones-forge as copies.py expects
- O6: n/a: no GPU job, CPU and network only

## 2026-11-10 07:55 SOCIAL live check after the release (ship.sh, live drift 0, public indahl.ai a8f445048, site content in indahl-ai 44cb703e)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: https://indahl.ai/social equals the built indahl-ai/social.html byte for byte, and every /social/*.json equals its canonical (copies.py live drift 0)
- II: holds: the outcomes table on the live page prints all five outcomes per section apart, as the ledger rows hold them
- III: holds: no signed gap is in a ledger row. Section gaps are as built from the cleared sections
- V: holds: the live page is the built page, so every range keeps its stated meaning
- VI: holds: live outcomes match the ledger rows (DSA 39/82/41/330/27, ad spend 28/26/26/6,056/24, TikTok 0/0/0/330/498, Bluesky 0/1/0/25/0)
- R: holds: check_ledger drift 0, copies drift 0, site gate 0 breaches, source gate 0 fail at release
- P1: holds: section quotes are the built text placed byte for byte
- P2: holds: all six /social/*.json links answer 200 through an exact-name worker route (added at release, SHIP_PLAN had said none was needed) and the public repo serves code/social, code/adspend, code/social-dsa, code/social-tiktok and code/social-bluesky
- P3: holds: menu entry SOCIAL under HERMES after WIKI, HERMES list line "Platform reports against the filings"
- P4: holds: no cause named on the live page
- P5: holds: interval wording as built
- P6: holds: the live headline is 31 of 6,160, built with the page
- P7: holds: ledger rows went in before the page carried the numbers and the release went through ledger/ship.sh with every gate at 0
- P8: holds: /api/v1 lists social and /api/v1/social returns the page summary. /respond?u=social-all and adspend-all are accepted, a unit outside the list is not
- P9: holds: house style checked by check_social step G and the site gate
- P10: holds: post hoc labels as built
- O1: cannot tell: tick bus rider lines for the four section ticks are proposed to Bones, not applied
- O2: holds: a failed gate in each tick turns outcomes to cannot tell, as cleared
- O3: n/a: no GPU used
- O4: holds: stamps YYYY-MM-DD HH:MM UTC
- O5: holds: absolute paths in the worker route and copies entries
- O6: n/a: no GPU job, CPU and network only

## 2026-11-12 10:58 Faults and Guards 2.0 migration of the SOCIAL assembler, adspend, DSA, TikTok and Bluesky sections (PLAN_ADDENDUM_std2.md in each section folder)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, every section plan and its seal are untouched, the section addenda are new files committed in the adspend, DSA, TikTok and Bluesky repositories before the re-runs
- II: n/a: no repeated item and no gap is netted, every section was rebuilt from the files on disk with the same data and every ABOVE, BELOW and CONSISTENT count equals the 10 Nov reading
- III: holds: above and below stay separate in every section, and every number other than the CANNOT_TELL and former NOTHING_RETURNED counts, the new reason fields, the plan commit that git reports now and the run time equals the 10 Nov summaries, with the reading stamps kept by the std2 rewrite flags
- V: holds: the rules are named in each section addendum before the re-runs, DSA ratio and share rows and Bluesky stated figures are read with K.read and closed edges, adspend and TikTok keep their own size rules, no interval method with a level is involved and no draw or seed applies
- VI: holds: four outcomes kept in every section, NOTHING_RETURNED is no longer an outcome anywhere, the rows that read it are CANNOT_TELL with NO_INTERVAL_FORMABLE, the adspend headline reads 31 of 6,160 as before
- R: holds: counts are read from the rebuilt summaries, adspend 28 above 26 below 26 consistent 6,080 cannot tell, DSA 39 82 41 357, TikTok 0 0 0 828, Bluesky 0 1 0 25, REQ-13 reads 0 NOTHING_RETURNED beside each
- P1: n/a: no quotation of any source is added or changed by this migration
- P2: n/a: no new figure is added, every number keeps its section and row label
- P3: n/a: no setting label of any source is touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a cannot tell carries and what NOTHING_RETURNED means
- P5: holds: the sections still state that their ranges are rule spreads and not sampling intervals
- P6: holds: the headline sentence keeps its numbers and adds the REQ-13 line, no stronger than the reading
- P7: holds: 14 social rows are updated and 3 nothing rows are withdrawn in locked passes through ledger.py with the new frozen summaries in social_index/shipped, check_social.py reads PASS, nothing is deployed from here
- P8: cannot tell: the section pages and social.html were rebuilt and check_social.py passes its checks, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences, no semicolons in the added text, check_social.py G reads no semicolon in the visible text
- P10: holds: the addenda are dated 12 Nov 2026 and committed before the re-runs, and no decided outcome changed
social-record social.adspend.above: Political ad spend A matched committee, or group of committees, and an election cycle 28 26 26 6,080
social-record social.adspend.below: Political ad spend A matched committee, or group of committees, and an election cycle 28 26 26 6,080
social-record social.adspend.cannot_tell: Political ad spend A matched committee, or group of committees, and an election cycle 28 26 26 6,080
social-record social.adspend.consistent: Political ad spend A matched committee, or group of committees, and an election cycle 28 26 26 6,080
social-record social.adspend.decided: In all 80 read above, below or consistent and 6,080 read cannot tell.
social-record social.adspend.decided.robust: 31 of 6,160
social-record social.bluesky.below: Bluesky A figure in Bluesky's transparency report and a year 0 1 0 25
social-record social.bluesky.cannot_tell: Bluesky A figure in Bluesky's transparency report and a year 0 1 0 25
social-record social.dsa.above: EU moderation reports A platform, a half-year and a measure 39 82 41 357
social-record social.dsa.below: EU moderation reports A platform, a half-year and a measure 39 82 41 357
social-record social.dsa.cannot_tell: EU moderation reports A platform, a half-year and a measure 39 82 41 357
social-record social.dsa.consistent: EU moderation reports A platform, a half-year and a measure 39 82 41 357
social-record social.tiktok.after_data.above: Jan to Mar 2026 25 18,545,004 20,361,489 32,956,870 +4.8% to +66.5% Cannot tell (NO_INTERVAL_FORMABLE) Above
social-record social.tiktok.cannot_tell: TikTok quarterly report A quarter and a measure, for the EU total or for one market 0 0 0 828
