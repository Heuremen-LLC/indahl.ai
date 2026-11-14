# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 14:10 Desk data packs on every desk page, the Data pack link at the top right of every page with data, and grab-and-go pack lists with zip sizes on the division pages
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every pack was built from the live feed it describes and checked against a second read of that feed, so the none is the feed itself and a pack that drifts from it is refused
- II: n/a: no comparison between two runs, the packs carry the desks' own results and the sizes are file sizes
- III: n/a: no signed difference is reported, sizes and row counts are levels of one file
- V: holds: two counts side by side for every CSV, the row count read back with csv.DictReader and the count in the live feed, with outcome, n, lo and hi compared row by row
- VI: n/a: no interval outcome is claimed by the pack itself, it carries the desks' outcomes as printed
- R: holds: zip sizes read from the files in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 10 Nov 2026, and the pages print that file
- P1: n/a: no quoted text is added to any page, the list lines reuse the desk lines already in the menu
- P2: holds: every size names its zip, which is linked beside it, and each pack names its feed and as-of time in its README
- P3: holds: pack and desk names as built, file names as served
- P4: holds: no cause named, sizes and links only
- P5: n/a: no intervals on these lines
- P6: holds: each line says what the zip holds and that results-only packs carry no source data, nothing stronger
- P7: holds: ledger rows pack.size.* added before the release, the zips in ledger/copies.json, release through ledger/ship.sh, live fetch and sha256 after
- P8: holds: rendered pages read after build, site gate breaches 0, check_ledger drift 0
- P9: holds: plain sentences, no semicolons, no counts of our things in headings, no AI statements, Heuremen LLC
- P10: n/a: no rule was set after the data, the licence handling per desk was set from the licence notes before the packs were built

## 2026-11-10 14:20 Desk packs of SOCIAL, HERMES and IRIS rebuilt with a Cite section and a doi field in CITATION.cff, for their Zenodo records
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each pack was rebuilt from the live feed it describes and checked against a second read of that feed by tools/desk_pack.py, every check held on all 22 packs
- II: n/a: no comparison between two runs, the packs carry the desks' own results and the sizes are file sizes
- III: n/a: no signed difference is reported, sizes are levels of one file
- V: holds: the row counts of every CSV were read back and compared with the live feed by the same build, and the zip sizes were read from the files in public/ into tools/desk_packs/pack_sizes.json
- VI: n/a: no interval outcome is claimed by the pack itself, it carries the desks' outcomes as printed
- R: holds: zip sizes read from the files in public/ by tools/desk_pack.py sizes on 10 Nov 2026, five sizes moved by 1 KB with the newer feed reads and the added Cite text
- P1: n/a: no quoted text is added to any page
- P2: holds: every size names its zip, and each pack names its feed, its as-of time and now its Zenodo DOI in its README
- P3: holds: pack and record names as built, file names as served
- P4: holds: no cause named, sizes, links and DOIs only
- P5: n/a: no intervals on these lines
- P6: holds: the Cite section says only where the pack is deposited and that the DOI points to the newest version
- P7: holds: ledger rows pack.size.* set before the release, release through ledger/ship.sh, live sha256 compared before the Zenodo upload
- P8: holds: check_ledger drift read after the rebuild and fixed row by row before the ship
- P9: holds: plain sentences, no semicolons, no counts of our things in headings, no AI statements, Heuremen LLC
- P10: n/a: no rule was set after the data

## 2026-11-10 15:10 Zenodo DOIs on the pages: concept DOI on every pack page, a Zenodo line on each desk page whose pack is deposited, and on the HERMES, IRIS and SOCIAL pack boxes
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each DOI was read back from the Zenodo API after publishing and the md5 Zenodo stores for every file equals the local file, whose sha256 equals the live zip
- II: n/a: no comparison between two runs
- III: n/a: no signed difference is reported
- V: holds: two records side by side for each DOI, zenodo_packs/dois.json written from the publish response and ledger/zenodo_dois.json, and they agree
- VI: n/a: no interval on these lines
- R: holds: DOIs read from the Zenodo publish response on 10 Nov 2026
- P1: n/a: no quoted text
- P2: holds: every DOI is a link to doi.org and names the record it resolves to
- P3: holds: record names as published on Zenodo
- P4: holds: no cause named, links only
- P5: n/a: no intervals
- P6: holds: the lines say only where the pack is deposited
- P7: holds: ledger rows zenodo.* added before the release, release through ledger/ship.sh
- P8: holds: rendered pages read after build, the DOI lines found on the pages listed in the ledger rows
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-10 20:40 Zenodo second pass: ATLAS 2026-11-10 version published, HERMES Desk Packs 2026-11-10.2 with SEASONAL, STEO, FLU, TORNADO and CREDIT, new records ATLAS Desk Packs (NEO, SOLAR, QUAKE, CONE) and OY Desk Packs (CAMPUS, RANK), DOIs on the pages
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each DOI was read back from the Zenodo publish response and the API after publishing, the md5 Zenodo stores for every file equals the local file (52 files, all match), and every zip sha256 equals the live .sha256 before upload
- II: n/a: no comparison between two runs
- III: n/a: no signed difference is reported
- V: holds: two records side by side for each DOI, zenodo_packs/dois.json written from the publish response and ledger/zenodo_dois.json, and they agree, and doi.org/10.5281/zenodo.23874305 resolves to record 24110654
- VI: n/a: no interval on these lines
- R: holds: DOIs read from the Zenodo publish response on 10 Nov 2026 evening, ATLAS md5 995351372741192a8a4d04fb224993c5 equals the live zip
- P1: n/a: no quoted text
- P2: holds: every DOI is a link to doi.org and names the record it resolves to, each source licence was read from tools/desk_pack.py DESKS and the packs' own LICENSE files (RANK and NEO results only, SOLAR GFZ Kp CC BY 4.0 credited, FLU FluSight CC BY 4.0 credited, the rest US government work)
- P3: holds: record names as published on Zenodo
- P4: holds: no cause named, links only
- P5: n/a: no intervals
- P6: holds: the lines say only where the pack is deposited, the ATLAS desk lines say the data is inside the ATLAS Data Pack
- P7: holds: ledger rows zenodo.atlas.version, zenodo.atlas_desks.concept and zenodo.oy_desks.concept added before the release, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages read after build, the DOI lines found on the pages listed in the ledger rows
- P9: holds: plain sentences, no semicolons, no AI statements, no counts of our things in titles, creators as in the existing records
- P10: n/a: no rule set after the data

## 2026-11-11 Downloads refreshed from their sources on every ship, QIA List Pack and QIA Research Package rebuilt, zip sizes re-read for the pack.size rows
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the QIA List Pack held two entries removed at an author's request and the QIA Research Package held an older faults.pdf and t1t2 PLAN.md than their sources, ledger/downloads.py gate caught both, so the none is the gate reading each zip against its source
- II: n/a: no comparison between two runs, each zip is read against its own source file
- III: n/a: no signed difference is reported, sizes are levels of one file
- V: holds: two reads side by side, the list.json inside the pack and the published qia/list.json, csv rows and bib entries against the studies count, and every file inside the research package against the file it was copied from
- VI: n/a: no interval on these lines
- R: holds: zip sizes read from the rebuilt files in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 11 Nov 2026, QIA List Pack 881 KB and QIA Research Package 676 KB
- P1: n/a: no quoted text added to any page
- P2: holds: each size names its zip, which is linked beside it
- P3: holds: pack names as built, file names as served
- P4: holds: no cause named, sizes and links only
- P5: n/a: no intervals on these lines
- P6: holds: each line says what the zip holds, nothing stronger
- P7: holds: ledger rows pack.size.* edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages read after build, check_ledger drift 0 required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 AIRQ Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (92788c21dcb75ae7), size 8127 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 10 KB -> 11 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6fdc19aae9f9e210), size 10882 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 CAMPUS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 11 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (544325bf52699a32), size 10954 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 CONE Data Pack rebuilt by ledger/downloads.py: zip size 52 KB -> 55 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (fe0f310c3d793c40), size 56802 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 10 KB -> 11 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (2a95ad1e26a4dec9), size 11135 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 IRIS Research Package rebuilt by ledger/downloads.py: zip size 440 KB -> 441 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (abafce8fce38c9bc), size 451607 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 LINKROT Data Pack rebuilt by ledger/downloads.py: zip size 83 KB -> 85 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d3df7c0b58a5d9aa), size 86944 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 QUAKE Data Pack rebuilt by ledger/downloads.py: zip size 51 KB -> 54 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (cea47d533176ace2), size 55062 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (a44b110f9a51f974), size 8725 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 SUPPORT Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 12 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (78ea588e75ebb566), size 12776 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:00 TORNADO Data Pack rebuilt by ledger/downloads.py: zip size 27 KB -> 28 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (661dfd433befcd69), size 29108 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:00, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:06 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e6dda0907e18151c), size 7562 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:06, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:11 OY Data Pack rebuilt by ledger/downloads.py: zip size 162 KB -> 182 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (cd110f18890137e7), size 186818 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:11, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:33 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (7882d8944dfeec2b), size 7819 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:33, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:53 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (584944b591f489b3), size 7577 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:53, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 09:53 QIA List Pack rebuilt by ledger/downloads.py: zip size 881 KB -> 882 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (b985099c6c28260f), size 902938 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 09:53, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 10:37 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e9f2add63882da7b), size 7926 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 10:37, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 13:38 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 9 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (37091b7b37f17fa6), size 8605 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 13:38, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 13:38 WATER Data Pack rebuilt by ledger/downloads.py: zip size 766 KB -> 767 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (afda6abf9217424d), size 784919 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 13:38, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 16:15 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (f9ae8fe25cbb01aa), size 7513 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 16:15, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 16:27 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d56e914a6684e5eb), size 8350 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 16:27, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 16:42 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (57e335da99b39149), size 8729 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 16:42, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 17:42 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d103a67953fc407d), size 7561 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 17:42, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 19:08 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (904d67006eb7a006), size 7881 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 19:08, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 19:08 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 9 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (b02250a250d4fdee), size 8605 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 19:08, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 20:35 WATER Data Pack rebuilt by ledger/downloads.py: zip size 767 KB -> 766 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (efe98910785a3405), size 784854 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 20:35, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 21:22 ARXIVDRIFT Data Pack rebuilt by ledger/downloads.py: zip size 126 KB -> 127 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (404121e5b4c859d9), size 130068 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 21:22, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 21:22 SEAT Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (1aad59e80b8bfaf7), size 7816 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 21:22, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-11 22:32 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (67ad372f36c4fb1b), size 7670 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-11 22:32, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 01:53 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (fd5de59856a4f07e), size 8709 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 01:53, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 05:20 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 9 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (f4894434b9ff1154), size 8598 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 05:20, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 05:36 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (ee36d59578d42e11), size 7926 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 05:36, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 06:30 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (19ab1d66c0d43643), size 7652 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 06:30, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 06:30 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (02296807474c1da7), size 8709 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 06:30, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 07:54 QIA List Pack rebuilt by ledger/downloads.py: zip size 882 KB -> 876 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (f11e27602f74cf4d), size 896665 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 07:54, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 07:54 SEAT Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d14e202d1a4968a8), size 7675 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 07:54, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 07:54 WEIGHTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (b6c72e1055b2d678), size 8738 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 07:54, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 08:44 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 9 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (382921699e1dc0a4), size 8599 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 08:44, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 08:58 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (588ce0c5d7c3a44d), size 7822 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 08:58, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 08:58 SEAT Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (61b5a05093b44c6e), size 7687 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 08:58, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:04 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 10 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (fe0ab66f3ec3ce56), size 13706 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:04, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:04 CADA Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (7a062655d250616c), size 7980 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:04, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 11 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (1fee03c10dbac853), size 13737 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 FEDSEP Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (ac5e6ec3ab13b359), size 13808 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 11 KB -> 12 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (3687cb9ed0e0d54c), size 12753 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 MODEL Data Pack rebuilt by ledger/downloads.py: zip size 267 KB -> 272 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4f4af44de6aa849b), size 278019 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (bbd26c153cf6b7e1), size 7621 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 LINKROT Data Pack rebuilt by ledger/downloads.py: zip size 85 KB -> 86 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (41c4433d99c9747c), size 88045 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 REVISE Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8f9f731b2ffd9f4f), size 8405 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 SECRECORDS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8a3e6474cf0e87be), size 8718 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 SOCIAL Data Pack rebuilt by ledger/downloads.py: zip size 126 KB -> 128 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (042e7e9833146795), size 131572 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 STACK Data Pack rebuilt by ledger/downloads.py: zip size 18 KB -> 19 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (a4a911ebead6d2f9), size 19914 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 SUPPORT Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (ce61530c18d9c88b), size 13253 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 TIME Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 16 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (510b9dff30ec95b4), size 16671 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 TRIALS Data Pack rebuilt by ledger/downloads.py: zip size 35 KB -> 37 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (ec715a934eb93697), size 37602 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 UPTIME Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (2abcc57e62eeda72), size 7682 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:05 WATER Data Pack rebuilt by ledger/downloads.py: zip size 766 KB -> 781 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (12b56bacc102b161), size 799437 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:05, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:08 OY Data Pack rebuilt by ledger/downloads.py: zip size 182 KB -> 183 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e6e1d6ef7ac49735), size 187235 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:08, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:12 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (3eda33350de0e517), size 7989 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:12, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:12 UPTIME Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (75c50aa8960ebfb2), size 7678 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:12, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:15 UPTIME Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (9ed736262fd86810), size 7681 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:15, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:38 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8cf498559aa5496b), size 12843 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:38, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:46 CONE Data Pack rebuilt by ledger/downloads.py: zip size 55 KB -> 59 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (37f05a8cfc3c7959), size 60370 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:46, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:46 FEDSEP Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (357a4984be8d9f1e), size 13930 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:46, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:46 NEO Data Pack rebuilt by ledger/downloads.py: zip size 10 KB -> 11 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (f4d46b79e08f6a77), size 11663 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:46, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 11:46 QUAKE Data Pack rebuilt by ledger/downloads.py: zip size 54 KB -> 57 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (0286947315dc8c0e), size 58141 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 11:46, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 12:03 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e07c800a3bdcdc42), size 13873 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 12:03, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 12:03 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 12 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (cdc31101be4adf66), size 12795 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 12:03, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 17:25 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6c3ee35e795ed940), size 7592 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 17:25, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 17:25 TORNADO Data Pack rebuilt by ledger/downloads.py: zip size 28 KB -> 31 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (f7babeda4ced0871), size 31334 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 17:25, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 21:20 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (0373a019a4606907), size 13826 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 21:20, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 21:20 CHANGE Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 9 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6fa038beda7fb055), size 9019 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 21:20, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-12 21:20 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (2324b3ceef0d3fab), size 12875 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-12 21:20, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 00:39 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (a9265ba841b0c58e), size 13432 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 00:39, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 00:39 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8881963eb23f736f), size 13813 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 00:39, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 00:39 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 12 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4db85a13fecacfdd), size 12778 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 00:39, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 03:53 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (1cff8d3358cc33ec), size 8059 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 03:53, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 08:12 CREDIT Data Pack rebuilt by ledger/downloads.py: zip size 55 KB -> 58 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (406cc95c65885d86), size 58975 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 08:12, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 08:12 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (0c0cfc3e00ce02ff), size 12976 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 08:12, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 10:37 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (b609631b0f11ae5d), size 13849 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 10:37, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 11:27 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (367537adb680774d), size 13801 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 11:27, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 12:17 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 12 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (a5aa784549a487fe), size 12761 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 12:17, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 12:17 QIA Research Package rebuilt by ledger/downloads.py: zip size 676 KB -> 677 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4dadd78631d0da99), size 692768 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 12:17, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 12:30 QIA Research Package rebuilt by ledger/downloads.py: zip size 677 KB -> 676 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (611d6bfddde80b7c), size 692281 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 12:30, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 14:08 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (ad9c434958c6874a), size 13879 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 14:08, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 14:44 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (3a18474d23802351), size 13815 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 14:44, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 14:44 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (55d6a4e755391bb3), size 7623 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 14:44, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 14:44 QIA Research Package rebuilt by ledger/downloads.py: zip size 676 KB -> 680 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (a9bc83c579d04f41), size 696695 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 14:44, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 14:58 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (b9f6cdff8cad86f8), size 7808 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 14:58, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 15:34 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (c32da6f1bba25828), size 7566 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 15:34, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 15:59 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (bfc307321a0ebe10), size 13980 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 15:59, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 16:09 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (1b5a66d4e78cbfe0), size 7742 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 16:09, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 16:28 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (c5ed3b54cb3d79e8), size 13824 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 16:28, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 16:28 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (830c0b2a55bcfe3e), size 7470 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 16:28, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 16:34 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e6d999393e27f5c5), size 13820 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 16:34, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:01 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (fdf54abf487baadd), size 13666 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:01, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:01 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (9b63ca7a106f8dd4), size 13826 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:01, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:01 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (e3fea98cd4f994c6), size 7735 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:01, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:14 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (512b404914521b9b), size 14046 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:14, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:14 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8eb26b4cfc5cfb16), size 13822 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:14, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 17:34 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (51fb83c6f7c21326), size 7524 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 17:34, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:13 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (79dd6c4f9b1f1816), size 13769 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:13, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:21 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (5c9ca7a5fa3c4958), size 13963 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:21, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:31 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (919bdae38fe12fdd), size 13811 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:31, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:31 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (5b0be48773c14094), size 7701 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:31, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:37 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (0cfa7c76272f3aaa), size 13976 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:37, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:43 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (28940e94ff45b537), size 13824 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:43, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 18:43 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4742aa8e199725d9), size 7591 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 18:43, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 19:04 FORECAST Data Pack rebuilt by ledger/downloads.py: zip size 12 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (cb94636fc5560328), size 12855 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 19:04, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 19:33 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6dcd8c9f5e1e5ba9), size 7746 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 19:33, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 19:48 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8c293983c0893e3b), size 7313 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 19:48, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 20:27 QIA Research Package rebuilt by ledger/downloads.py: zip size 680 KB -> 681 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (eefa6efda245e95a), size 697059 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 20:27, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:10 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d68063005c1260d5), size 7825 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:10, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:16 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (5146f9960e3af534), size 7647 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:16, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:28 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8ed2c7a10bf89f1d), size 13819 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:28, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:28 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 7 KB -> 8 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (23822779ad7ca73b), size 7806 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:28, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:37 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6203111df7987a8b), size 13827 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:37, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:43 HOSTS Data Pack rebuilt by ledger/downloads.py: zip size 8 KB -> 7 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (c07e4c8b0601a19b), size 7597 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:43, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 21:57 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (8514a2427c1f0814), size 13823 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 21:57, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 22:11 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d770173485e650ae), size 13827 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 22:11, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 22:44 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4c52f5d90e7fcbc4), size 13823 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 22:44, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 22:58 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (65e959ed9cd02859), size 13828 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 22:58, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-13 23:04 AIRLINE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (af9738b13d880831), size 13799 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-13 23:04, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 00:29 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (d422a2369b3fec2c), size 13823 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 00:29, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 00:29 SOCIAL Data Pack rebuilt by ledger/downloads.py: zip size 128 KB -> 129 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4db1d48e5d0216fa), size 131988 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 00:29, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 00:29 WIKI Data Pack rebuilt by ledger/downloads.py: zip size 150 KB -> 151 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (6ba1d77aad344340), size 154220 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 00:29, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 01:32 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 13 KB -> 14 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (bc339a250a358895), size 13825 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 01:32, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 04:03 CADENCE Data Pack rebuilt by ledger/downloads.py: zip size 14 KB -> 13 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (53e0ba6d2d1b53b1), size 13822 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 04:03, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 04:32 TAPE Data Pack rebuilt by ledger/downloads.py: zip size 42 KB -> 43 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (4ce23ad189900bcb), size 43567 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 04:32, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data

## 2026-11-14 04:48 TAPE Data Pack rebuilt by ledger/downloads.py: zip size 43 KB -> 44 KB
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs
- II: n/a: no comparison between two runs, one file size read before and after
- III: n/a: no signed difference is reported, a size is a level of one file
- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back (dd26e3c71fbdd0ef), size 45277 bytes
- VI: n/a: no interval outcome is claimed
- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on 2026-11-14 04:48, the page prints that file
- P1: n/a: no quoted text is added to any page
- P2: holds: the size names its zip, linked beside it
- P3: holds: pack name as built, file name as served
- P4: holds: no cause named, a size and a link only
- P5: n/a: no intervals on this line
- P6: holds: the line says what the zip holds, nothing stronger
- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock
- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes
- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC
- P10: n/a: no rule set after the data
