#!/usr/bin/env python3
"""reproduce_kits.py (10 Nov 2026): one reproduce kit per desk headline, a ship gate that reruns every kit, and the per-desk table on /reproduce.

A kit is a folder that recomputes one desk's headline number and outcome label with the desk's own code, offline, from what the kit holds:
  inputs/         the exact files the desk's scoring read when the published number was computed (full kits), stored gzip-compressed.
                  A fetch-and-verify kit leaves them out, because the source's terms forbid passing its data on. Its MANIFEST.json lists
                  every input file with its sha256 and the source addresses and read times the desk recorded, so a reader can fetch and check.
  code/           the desk's own scoring code, copied byte for byte from the desk folder (the same files as code/<desk>/ in the public repo)
  kit.json        the steps (which scripts run, in which order), the output file, and the headline fields (ledger/live_headlines.py DESKS)
  run.py          one command: python3 run.py --check
  expected.json   the headline the kit must print, with expected.sha256 (sha256 of the exact bytes run.py prints)
  published.json  the headline as the live feed served it when the kit was made: feed address, read time, feed stamp, sha256 of the feed bytes
  MANIFEST.json, SHA256SUMS.txt, README.md

  python3 reproduce_kits.py build all|<desk> ...   make or remake kits (each kit must reproduce the live feed's headline, or the old kit stays)
  python3 reproduce_kits.py refresh                ship.sh step 1: remake only the kits the ledger or the live feed has moved past, then verify
  python3 reproduce_kits.py gate                   ship.sh step 3: every kit, run in a clean temp folder from kit contents alone, must print its
                                                   expected headline, which must equal the published headline it names and be covered by the
                                                   desk's current ledger value row (same label, number inside its interval), and must not be
                                                   a material change behind the live feed. Any mismatch refuses the ship.
  python3 reproduce_kits.py mirror DIR             push_public.sh: copy the kits to DIR/reproduce/ (private inputs never leave this machine)
  python3 reproduce_kits.py selftest               a corrupted input must make the gate refuse
Build hook (build_site.py, one line after accountability.apply): apply(PAGES) puts the per-desk table on /reproduce and a link on each desk page.
Python 3.9 compatible, standard library only."""
import copy, datetime as D, gzip, hashlib, html, inspect, io, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
ROOT = os.path.join(B, 'reproduce_kits'); KITS = os.path.join(ROOT, 'kits'); EXTRACTS = os.path.join(ROOT, 'extracts'); PRIV = os.path.join(ROOT, 'private'); INDEX = os.path.join(ROOT, 'index.json')
sys.path.insert(0, os.path.join(B, 'ledger'))
import live_headlines as LH   # noqa: E402  the headline fields, the reading and the material-change rule, one source for the ledger and the kits

E = lambda s: html.escape(str(s), quote=True)
UA = {'User-Agent': 'heuremen-reproduce/1.0 (+https://indahl.ai/reproduce)'}
REPO = 'https://github.com/Heuremen-LLC/indahl.ai'
DEAD = 'http://127.0.0.1:9'   # every kit runs with its proxies pointed here, so a step that reaches for the network fails instead of reading a newer source
RUN_TIMEOUT = 1800
MAX_FILE = 45 * 1048576   # a stored (compressed) input above this is not put in a public kit

# --------------------------------------------------------------------------------------------------------------------------- desk specs
# folder: the desk folder under ~/bones-forge. mode: 'inputs' (inputs in the kit) or 'fetch' (inputs kept here, listed with sha256 and sources).
# inputs: files the scoring reads, relative to the desk folder. code: the desk's scripts copied unmodified. steps: scripts run in order (python3 -I).
# output: the file whose fields the headline is read from. why: for fetch kits, the licence reason (as tools/desk_pack.py states it).
# sources: for fetch kits, how a reader gets the inputs again. Desks with no kit are in NOKIT with the reason and what is checkable.
SPECS = {
 'seasonal': dict(folder='seasonal_index', mode='inputs', inputs=['data/seasonal_live.json', 'data/raw/cpc_verif_grid/*', 'PLAN.md', 'data/plan_seal.json'], code=['seasonal_tick.py', 'heuremen_kit.py'],
     extract='clock_run.py', extract_of='the clock only. It runs seasonal_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/seasonal_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'seasonal_tick.py', 'data/seasonal_live.json', '--offline']], output='data/seasonal_live.json', deps='numpy'),
 'solar': dict(folder='solar_index', mode='fetch', why='the GFZ file the desk reads for Kp also carries sunspot numbers under CC BY-NC 4.0 and F10.7 from DRAO and NRCan, which the data pack leaves out',
     sources=['NOAA SWPC Report and Forecast of Solar and Geophysical Activity as first published, ftp://ftp.swpc.noaa.gov/pub/warehouse/ (data/raw/warehouse), with our own dated copies in data/snapshots.', 'NOAA SWPC Edited Solar Events and daily indices, ftp://ftp.swpc.noaa.gov/pub/indices/ (data/raw/indices and the event lists).', 'GFZ Potsdam Kp, https://kp.gfz.de/ (data/raw/gfz, the file Kp_ap_Ap_SN_F107_since_1932.txt).'], inputs=['data/solar_live.json', 'data/raw/*', 'data/raw/*/*', 'data/raw/*/*/*', 'data/snapshots/*_sgarf.txt.gz', 'data/known_good_rows.json', 'PLAN.md', 'data/plan_seal.json'],
     code=['solar_tick.py', 'heuremen_kit.py'], extract='clock_run.py', extract_of='the clock only. It runs solar_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/solar_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'solar_tick.py', 'data/solar_live.json', '--offline']], output='data/solar_live.json'),
 'flu': dict(folder='flu_index', mode='inputs', inputs=['data/flu_live.json', 'data/raw/hub/model-output/FluSight-ensemble/*-FluSight-ensemble.csv', 'data/raw/hub/target-data/time-series.csv',
     'data/raw/hub/target-data/target-hospital-admissions.csv', 'data/raw/hub/auxiliary-data/locations.csv', 'data/known_good_rows.json', 'PLAN.md', 'data/plan_seal.json'],
     code=['flu_tick.py', 'heuremen_kit.py'], extract='clock_run.py', extract_of='the clock only. It runs flu_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/flu_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'flu_tick.py', 'data/flu_live.json', '--offline']], output='data/flu_live.json', deps='numpy',
     note='locations.csv comes from the FluSight Forecast Hub repository, under its MIT licence (https://github.com/cdcepi/FluSight-forecast-hub/blob/main/LICENSE). The hub baseline model files are left out. They feed only the interval score beside the headline, so a full run of this kit prints those cells empty while the headline cell is unchanged.'),
 'steo': dict(folder='steo_index', mode='inputs', inputs=['data/steo_live.json', 'data/raw/wayback/cg_*.xls*', 'data/raw/wayback/cdx_chart_gallery.json', 'data/releases.json', 'data/raw/spot/RWTCm.xls', 'data/raw/spot/RNGWHHDm.xls',
     'data/pdf_levels.json', 'data/known_good_rows.json', 'PLAN.md', 'data/plan_seal.json'], code=['steo_tick.py', 'heuremen_kit.py'], extract='clock_run.py', extract_of='the clock only. It runs steo_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/steo_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'steo_tick.py', 'data/steo_live.json', '--offline']], output='data/steo_live.json',
     deps='numpy and xlrd', python=os.path.join(B, 'steo_index', 'venv', 'bin', 'python')),
 'linkrot': dict(folder='linkrot_index', mode='inputs', inputs=['data/links.json', 'summary_linkrot.json'], code=['heuremen_kit.py'], extract='linkrot_score.py',
     extract_of='linkrot_tick.py lines 84 to 92 and 101, the cell and combined functions and the all cell', ref=['linkrot_tick.py'], steps=[['linkrot_score.py']], output='out.json',
     note='The outcome needs the desk\'s own live gate to have passed on the run (a planted live link and a planted dead link read as expected). That gate cannot be replayed, so the kit reads its result from summary_linkrot.json, the summary that run wrote.'),
 'hpt': dict(folder='hpt_index', mode='inputs', inputs=['data/domains.json', 'summary_hpt.json'], code=['heuremen_kit.py'], extract='hpt_score.py',
     extract_of='hpt_tick.py lines 121 to 124 and 128, the grp function and the comparison block', ref=['hpt_tick.py'], steps=[['hpt_score.py']], output='out.json',
     note='The outcome needs the desk\'s own live gate to have passed on the run. That gate cannot be replayed, so the kit reads its result from summary_hpt.json, the summary that run wrote.'),
 'campus': dict(folder='campus_index', mode='fetch', why='each school keeps its rights to its pages, and the data pack holds only our status counts',
     sources=['Every external source cited on https://indahl.ai/oy, read pass after pass. The newest line of data/reads.jsonl holds the status of each address on the newest pass, with the pass time.'], inputs=['data/reads.jsonl'], code=[], extract='campus_score.py',
     extract_of='campus_tick.py lines 126 to 138, the stnow function and the state_now block', ref=['campus_tick.py'], steps=[['campus_score.py']], output='out.json'),
 'secrecords': dict(folder='secrecords_index', mode='fetch', inputs=['data/domains.json', 'summary_secrecords.json'], code=['heuremen_kit.py'], extract='secrecords_score.py',
     extract_of='secrecords_tick.py lines 150 to 162, read_share, the grp function and the comparison block', ref=['secrecords_tick.py'], steps=[['secrecords_score.py']], output='out.json',
     sources=['The domain list: the top 1,000 rows of the Tranco list of the date in data/listdate.txt of the desk, https://tranco-list.eu/', 'For each domain, the first HTTPS response of https://DOMAIN/ (no redirect followed) and its SPF record read through DNS over HTTPS, as secrecords_tick.py does. Each row of data/domains.json carries the time it was read in its read field.']),
 'hfsize': dict(folder='hfsize_index', mode='fetch', inputs=['data/repos.json', 'summary_hfsize.json'], code=['heuremen_kit.py'], extract='hfsize_score.py',
     extract_of='hfsize_tick.py lines 56 to 57 and 63, the counts, the interval and the comparison block', ref=['hfsize_tick.py'], steps=[['hfsize_score.py']], output='out.json',
     sources=['The 1,000 most downloaded models, https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1000', 'For each model, https://huggingface.co/api/models/MODEL (safetensors totals), as hfsize_tick.py reads them. Each row of data/repos.json carries its read time.']),
 'support': dict(folder='support_index', mode='fetch', inputs=['data/cycles.json', 'summary_support.json'], code=['heuremen_kit.py'], extract='support_score.py',
     extract_of='support_tick.py lines 66 to 87, the counts, the product bootstrap and the all cell', ref=['support_tick.py'], steps=[['support_score.py']], output='out.json',
     sources=['For each product, https://endoflife.date/api/PRODUCT.json, read on the date of the updated field of the feed. The class of each cycle (supported, and no release in more than a year) was set on that date and is stored in each row.']),
 'weights': dict(folder='weights_index', mode='fetch', inputs=['data/repos.json'], code=['heuremen_kit.py'], extract='weights_score.py',
     extract_of='weights_tick.py lines 70 to 76 and 84 to 86, the latest pair, the any-pass count and their intervals', ref=['weights_tick.py'], steps=[['weights_score.py']], output='out.json',
     sources=['For each model, https://huggingface.co/api/models/MODEL/tree/main on each pass. data/repos.json holds the sha256 of every weight file Hugging Face reported on each pass, with the pass times, so a reader can compare them with the files as served now.']),
 'change': dict(folder='change_index', mode='fetch', inputs=['data/rows.json'], code=[], extract='change_score.py',
     extract_of='change_tick.py lines 128 to 143, the days and life_of functions and the lifespan block', ref=['change_tick.py'], steps=[['change_score.py']], output='out.json',
     sources=['The Google model deprecation page and the other vendor pages listed in the sources block of https://indahl.ai/change/live.json. data/rows.json holds each dated row as read, with the first and last time it was seen.']),
 'launch': dict(folder='launch_index', mode='fetch', inputs=['data/snapshots.jsonl'], code=['heuremen_kit.py'], extract='launch_score.py',
     extract_of='launch_tick.py lines 28 to 58, flown_watched and the cells, without the count still waiting', ref=['launch_tick.py'], steps=[['launch_score.py']], output='out.json',
     sources=['Launch Library 2, https://ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=100&mode=normal and .../previous/?limit=100&mode=normal, read every 6 ticks. Each row of data/snapshots.jsonl is one launch as read, with the read time in its read field.']),
 'pkginstall': dict(folder='pkginstall_index', mode='fetch', inputs=['data/projects.json', 'data/listdate.txt', 'summary_pkginstall.json'], code=['heuremen_kit.py'], extract='pkginstall_score.py',
     extract_of='pkginstall_tick.py lines 112 to 116, the counts, the interval and the comparison block', ref=['pkginstall_tick.py'], steps=[['pkginstall_score.py']], output='out.json',
     sources=['The top PyPI projects list of the date in data/listdate.txt, https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json', 'For each project, https://pypi.org/pypi/PROJECT/json, and pip install --dry-run of the command its description gives. Each row carries its read time.'],
     note='This kit recounts the class pip gave each command when the desk read it. pip resolves against the live PyPI index, which cannot be replayed, so those classes are inputs here.'),
 'pkglicense': dict(folder='pkglicense_index', mode='fetch', inputs=['data/projects.json', 'summary_pkglicense.json', '@pkginstall/data/projects.json=pkginstall_index/data/projects.json', '@pkginstall/data/listdate.txt=pkginstall_index/data/listdate.txt'],
     code=['heuremen_kit.py'], extract='pkglicense_score.py', extract_of='pkglicense_tick.py lines 97 to 102, the rows of the listed names, the counts and the disagree block', ref=['pkglicense_tick.py'], steps=[['pkglicense_score.py']], output='out.json',
     sources=['The top PyPI projects list of the list date in summary_pkglicense.json, https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json', 'For each project, https://pypi.org/pypi/PROJECT/json and the licenseInfo of its GitHub repository from the GitHub GraphQL API. Each row carries its read time.'],
     note='Until 10 Nov 2026 the desk did not keep the list of names it scored. From its next full read it keeps them in data/names.json. This kit reads the same list of the same date from the PKGINSTALL desk, which keeps each rank, and stops if the two list dates differ.'),
 'airline': dict(folder='bts_index', mode='inputs', inputs=['data/results.json'], code=['heuremen_kit.py'], extract='airline_score.py',
     extract_of='airline_summary.py lines 12 to 25, the table of 2026 against 2025 and the headline block', ref=['airline_summary.py', 'airline_tick.py'], steps=[['airline_score.py']], output='out.json',
     note='data/results.json holds the per-airline comparisons airline_tick.py made from the BTS month files (route medians and their bootstrap intervals). This kit starts from that file. The month files are the BTS Reporting Carrier On-Time Performance downloads, about 37 MB, read by airline_tick.py.'),
 'fedsep': dict(folder='fedsep_index', mode='inputs', inputs=['data/projections.json', 'data/outcomes_day.json'], code=['heuremen_kit.py'], extract='fedsep_score.py',
     extract_of='fedsep_tick.py lines 24 and 49 to 69, the inside test, the triples and the pooled bootstrap', ref=['fedsep_tick.py'], steps=[['fedsep_score.py']], output='out.json'),
 'cadence': dict(folder='cadence_index', mode='inputs', inputs=['data/portal_*.json'], code=[], extract='cadence_score.py',
     extract_of='cadence_tick.py lines 8 to 32 and 70 to 95, the interval and date readers and the series and overdue loop', ref=['cadence_tick.py'], steps=[['cadence_score.py']], output='out.json'),
 'water': dict(folder='water_index', mode='inputs', inputs=['data/water.json', 'summary_water.json'], code=['heuremen_kit.py'], extract='water_score.py',
     extract_of='water_tick.py lines 34, 180 to 186, 213 to 220 and 464, the verdict and the six-month band cells', ref=['water_tick.py'], steps=[['water_score.py']], output='out.json',
     note='data/water.json holds every scored row the run made from the Reclamation 24-Month Study reports and the measured levels. The reports themselves are about 1.6 GB of PDFs, listed with their addresses in the RISE catalog. The run\'s gate reads two of those reports, so the kit takes its result from summary_water.json.'),
 'cone': dict(folder='cone_index', mode='inputs', inputs=['data/cone.json'], code=['heuremen_kit.py'], extract='cone_score.py',
     extract_of='cone_tick.py lines 18 to 25, 200 to 222 and 398 to 401, the storm-level bootstrap and the whole-path cells', ref=['cone_tick.py'], steps=[['cone_score.py']], output='out.json',
     note='data/cone.json holds every forecast path the run scored, inside or outside the cone, from the NHC a-decks and HURDAT2 (about 300 MB of NHC files). This kit starts from those scored paths.'),
 'credit': dict(folder='credit_index', mode='inputs', inputs=['data/cache/agg_*.json'], code=['heuremen_kit.py'], extract='credit_score.py',
     extract_of='credit_tick.py lines 23, 39, 128 to 150 and 195 to 200, the printed band, the company-month block bootstrap and ruler one for 2025', ref=['credit_tick.py'], steps=[['credit_score.py']], output='out.json', deps='numpy',
     note='The aggregate file holds company, month, product family, complaints and complaints not answered in time, counted by credit_tick.py from the CFPB complaint database download (about 365 MB, no complaint text kept). Its name carries the first 16 characters of the sha256 of the download it was counted from.'),
 'census': dict(folder='census_index', mode='inputs', inputs=['data/census.json', 'summary_census.json'], code=['heuremen_kit.py'], extract='census_score.py',
     extract_of='census_tick.py cells() and the outcome rule against 90 percent, for the national total cells', ref=['census_tick.py'], steps=[['census_score.py']], output='out.json',
     note='data/census.json holds every row the run scored, first print, later value and stated width, from the ALFRED vintages and our dated Census API copies. The gate result comes from summary_census.json, the summary of the same run.'),
 'quake': dict(folder='quake_index', mode='inputs', inputs=['data/quake_rows.json.gz', 'summary_quake.json'], code=['heuremen_kit.py'], extract='quake_score.py',
     extract_of='quake_tick.py lines 17 to 18, 60 to 65, 328 to 348 and 360, the sequence-block bootstrap and the headline cell', ref=['quake_tick.py'], steps=[['quake_score.py']], output='out.json',
     note='data/quake_rows.json.gz holds every forecast window the run scored against the USGS catalog (the forecast files and catalog reads are about 460 MB). The block list and the gate result come from summary_quake.json, the summary of the same run.'),
 'neo': dict(folder='neo_index', mode='fetch', inputs=['data/raw/wayback/*', 'data/snapshots/cad_*.json.gz', 'data/raw/cad_current.json', 'data/cache/des_*.json', 'data/known_good_rows.json', 'data/plan_seal.json', 'PLAN.md', 'data/neo_live.json'],
     code=['neo_tick.py', 'heuremen_kit.py'], extract='clock_run.py', extract_of='the clock only. It runs neo_tick.py with --offline --no-sbdb and the clock pinned to the time the published run read (the generated field of data/neo_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'neo_tick.py', 'data/neo_live.json', '--offline', '--no-sbdb']], output='data/neo_live.json',
     sources=['The current JPL record, https://ssd-api.jpl.nasa.gov/cad.api with the query neo_tick.py builds (data/raw/cad_current.json, written at each run).', 'Internet Archive copies of earlier Close-Approach answers: the capture list at https://web.archive.org/cdx/search/cdx?url=ssd-api.jpl.nasa.gov/cad.api*&from=2024 (stored as data/raw/wayback/cdx_cad_api.json), each capture fetched from web.archive.org by its timestamp and address.', 'Our own dated copies of the JPL record (data/snapshots/cad_*.json.gz), each with its address and read time inside.', 'The Close-Approach answers for renamed or numbered objects the desk keeps in data/cache/des_*.json, https://ssd-api.jpl.nasa.gov/cad.api?des=OBJECT with the date window neo_tick.py builds (line 175).'],
     note='data/neo_live.json is read only for the time the published run read, which pins the clock. The run writes a fresh data/neo_live.json and the headline is read from that.'),
 'tornado': dict(folder='tornado_index', mode='fetch', inputs=['data/tornado_live.json', 'data/raw/*/*', 'data/raw/*/*/*', 'data/cache/pointcheck.json', 'PLAN.md', 'data/plan_seal.json'],
     code=['tornado_tick.py', 'heuremen_kit.py', 'shpread.py'], extract='clock_run.py', extract_of='the clock only. It runs tornado_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/tornado_live.json), which the desk uses to tell a settled or passed row from an open one', ref=[], steps=[['clock_run.py', 'tornado_tick.py', 'data/tornado_live.json', '--offline']], output='data/tornado_live.json', deps='numpy and matplotlib',
     why='its inputs are about 550 MB of SPC outlook archives, storm reports, warnings and boundary files, more than a public kit carries. Every source is public domain and listed below, and each file is named with its sha256',
     sources=['SPC Day 1 Convective Outlooks, one zip per year, from the Iowa Environmental Mesonet archive, https://mesonet.agron.iastate.edu/request/gis/outlooks.phtml (data/raw/outlooks/day1_YYYY.zip).', 'The SPC tornado database 1950 to 2025, https://www.spc.noaa.gov/wcm/ (data/raw/db), and SPC preliminary storm reports (data/raw/prelim).', 'NWS storm-based tornado warnings from the Iowa Environmental Mesonet archive, https://mesonet.agron.iastate.edu/vtec/ (data/raw/warnings).', 'US Census cartographic state boundaries, cb_2024_us_state_20m.zip, https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html (data/raw/boundaries).']),
 'ailuminate': dict(folder='ailuminate_index', mode='fetch', inputs=['newest:data/raw/*', 'data/reads.jsonl'], code=['heuremen_kit.py'], extract='ailuminate_score.py',
     extract_of='ailuminate_tick.py, CATS, ordinal, ord_str, parse_page, parse_pdf and pdf_text as written, and the rows, cmp, oc and A lines on the newest read', ref=['ailuminate_tick.py'],
     steps=[['ailuminate_score.py']], output='out.json', deps='pypdf 6.21.4', note='pypdf 6.21.4 is the version the desk runs, and the text it extracts from each PDF is what the parser reads.', python=os.path.join(B, 'revise_index', 'venv', 'bin', 'python'),
     sources=['The MLCommons AILuminate Safety results page, https://mlcommons.org/ailuminate/safety/results/ (page.html of the newest read).', 'The Detailed Results PDF of each system from the MLCommons Google Drive folder the page links, https://drive.google.com/embeddedfolderview?id=1hRjh2gALmmlpNMIDuoASBKMHUO7V0T95. The read log data/reads.jsonl records the sha256 of the page and of every PDF on every read.']),
 'airq': dict(folder='airq_index', mode='fetch', inputs=['data/w2026/aqs_*.json', 'data/w2026/pa_*.json'], code=['heuremen_kit.py'], extract='airq_score.py',
     extract_of='airq_tick.py run with AIRQ_WINDOW=2026: the constants and metrics, meets, corrected, ab_ok, haversine and outcome as written, stage A over the kept AQS files and stage E as written. airq_promote.py and airq_tie.py, which run after it, leave these fields as they are',
     ref=['airq_tick.py', 'airq_promote.py', 'airq_tie.py'], steps=[['airq_score.py']], output='out.json',
     sources=['EPA Air Quality System hourly PM2.5 (parameter 88101), https://aqs.epa.gov/data/api/sampleData/byState for each state, 1 March to 30 June 2026, read month by month. data/w2026/aqs_NN.json keeps the daily means the read built from those rows.', 'PurpleAir outdoor sensors within 200 metres of each monitor, https://api.purpleair.com/v1/sensors (data/w2026/pa_near.json), and each sensor\'s daily history, https://api.purpleair.com/v1/sensors/ID/history with average=1440 (data/w2026/pa_ID.json, the answer as served, with its time_stamp). A PurpleAir read needs a PurpleAir key.']),
 'trials': dict(folder='trials_index', mode='inputs', inputs=['data/records.jsonl', 'data/read_at.txt'], code=['trials_summary.py', 'heuremen_kit.py'],
     steps=[['trials_summary.py']], output='data/summary.json'),
}
NOKIT = {
 'hosts': dict(name='HOSTS', why='The headline is the count at the newest poll of OpenRouter, a live service whose answers cannot be replayed, and its flag test reads the 24 hours before the poll by the clock. We keep each poll as parsed rows, not as the service\'s answers.',
     check='Each published copy of the feed has its sha256 on the <a href="/tape">TAPE</a> chain, so a copy you kept can be checked against what we published. The data pack holds the counts and outcomes.'),
 'tape': dict(name='TAPE', why='The headline is a clock, the time since the newest entry was chained.',
     check='The chain itself can be checked offline. <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/tape">code/tape</a> holds tape.jsonl, every leaves file and tape_verify.py, which recomputes every hash and beacon with no network.'),
 'revise': dict(name='REVISE', why='The headline compares the first BLS estimate with the most recent value, read from the BLS flat file on each run. The BLS table of first, second and third estimates is kept with its sha256. Until 10 Nov 2026 the flat file was not kept, so the published values cannot be replayed. From the next read on, each version of the flat file is kept by its sha256, and the start of its sha256 is in the feed.',
     check='The feed names the sha256 of the BLS table it read, and the <a href="/tape">TAPE</a> chain holds the sha256 of each published feed.'),
 'uptime': dict(name='UPTIME', why='The desk probes vendor services and their status pages live from two networks. A probe answer cannot be replayed.',
     check='Each published copy of the feed has its sha256 on the <a href="/tape">TAPE</a> chain, and the data pack holds the counts and outcomes.'),
 'time': dict(name='TIME', why='The desk measures public time servers live against a GPS-disciplined clock. A time reading cannot be replayed.',
     check='Each published copy of the feed has its sha256 on the <a href="/tape">TAPE</a> chain, and the data pack holds the readings and outcomes.'),
 'cada': dict(name='CADA', why='The desk asks public DNS resolvers live whether they block fresh abuse listings. A resolver answer cannot be replayed.',
     check='Each published copy of the feed has its sha256 on the <a href="/tape">TAPE</a> chain, and the data pack holds the counts and outcomes.'),
}

# the licence handling of each desk, from tools/desk_pack.py (the data packs): a 'results' pack holds no source data, so its kit cannot either
try:
    sys.path.insert(0, os.path.join(B, 'tools')); import desk_pack as _DP; PACK = _DP.DESKS
except Exception: PACK = {}
for _k, _v in SPECS.items():
    _p = PACK.get(_k) or {}
    if _p.get('lic') == 'results' and _v['mode'] != 'fetch': raise SystemExit('reproduce_kits: %s is results-only in desk_pack.py, so its kit must be fetch-and-verify' % _k)
    if _v['mode'] == 'fetch': _v['why'] = _v.get('why') or _p.get('why') or 'the source terms do not allow passing its data on'

# ------------------------------------------------------------------------------------------------------------------------------- helpers
def sha(b): return hashlib.sha256(b).hexdigest()
def fsha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()
def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n'
def utc(t=None): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))
def load_index():
    try: return json.load(open(INDEX))
    except Exception: return {}
def save_index(ix):
    os.makedirs(ROOT, exist_ok=True); tmp = INDEX + '.tmp'; json.dump(ix, open(tmp, 'w'), indent=1, sort_keys=True); os.replace(tmp, INDEX)
def get_feed(slug):
    u = '%s/%s/live.json?x=%d' % (LH.SITE, slug, time.time())
    b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
    return b, json.loads(b)
def gz(src, dst):
    """deterministic gzip (no name, mtime 0), so the same input always gives the same stored bytes"""
    with open(src, 'rb') as f, open(dst, 'wb') as o:
        with gzip.GzipFile(filename='', mode='wb', fileobj=o, mtime=0, compresslevel=9) as z: shutil.copyfileobj(f, z)

COMPARE = ('value', 'display', 'outcome', 'lo', 'hi', 'keys', 'n', 'of')
def headline_of(slug, out):
    """the headline fields of one desk read from a summary or feed object, as live_headlines.reading reads them (stamp left out: a kit
    recomputes the number, not the time the rider published it)"""
    spec = LH.DESKS[slug]; r = LH.reading(spec, out)
    for k in ('n', 'of'): r[k] = None if not spec.get(k) or LH.dig(out, spec[k]) is LH._MISS else LH.dig(out, spec[k])
    return {'desk': spec['name'], **{k: r.get(k) for k in COMPARE}}


# ------------------------------------------------------------------------------------------------------------------------------- runner
# run.py is generated from this text plus the two functions of ledger/live_headlines.py that read a headline (dig and display), copied as
# written, so the kit reads its output exactly as the ledger reads the live feed.
RUNNER = r'''#!/usr/bin/env python3
"""run.py: recompute the @@NAME@@ headline from this kit, offline. Heuremen LLC, https://indahl.ai/reproduce

  python3 run.py                  recompute and print the headline as one line of JSON
  python3 run.py --check          also compare with expected.json and exit 1 on any difference
  python3 run.py --inputs DIR     read the input files from DIR instead of ./inputs (fetch-and-verify kits: the files you fetched)

The desk's own scripts in code/ run in a fresh temporary folder laid out like the desk folder, with the inputs beside them, with no network
(the proxy settings point at a closed local port). The headline is read from the output with the same field paths the ledger uses.
Standard library only, Python 3.9 or later."""
import gzip, hashlib, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
K = json.load(open(os.path.join(HERE, 'kit.json')))
_MISS = object()
@@DIG@@
@@F@@
@@DISPLAY@@

def reading(spec, d):
    g = lambda k: (None if not spec.get(k) else (lambda x: None if x is _MISS else x)(dig(d, spec[k])))
    v = dig(d, spec['field'])
    return dict(value=None if v is _MISS else v, display=display(spec, d), outcome=g('outcome'), lo=g('lo'), hi=g('hi'), n=g('n'), of=g('of'),
                keys=[(lambda x: None if x is _MISS else x)(dig(d, k)) for k in (spec.get('keys') or [])])

def main(a):
    src = a[a.index('--inputs') + 1] if '--inputs' in a else os.path.join(HERE, 'inputs')
    man = json.load(open(os.path.join(HERE, 'MANIFEST.json')))
    tmp = tempfile.mkdtemp(prefix='kit-'); work = os.path.join(tmp, 'work')
    try:
        os.makedirs(work)
        for f in man['inputs']:   # every input is checked against the sha256 the desk's scoring read, before anything runs
            p = os.path.join(src, f['stored'])
            if not os.path.exists(p): p = os.path.join(src, f['path'])
            if not os.path.exists(p): sys.exit('missing input: ' + f['path'])
            b = open(p, 'rb').read()
            if f.get('gzip_added') and p.endswith('.gz'): b = gzip.decompress(b)
            if hashlib.sha256(b).hexdigest() != f['sha256']: sys.exit('input differs from the one the desk read: %s (sha256 %s, expected %s)' % (f['path'], hashlib.sha256(b).hexdigest(), f['sha256']))
            d = os.path.join(work, f['path']); os.makedirs(os.path.dirname(d), exist_ok=True); open(d, 'wb').write(b)
        for f in man['code']:
            d = os.path.join(work, f['path']); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(os.path.join(HERE, 'code', f['path']), d)
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': tmp, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'PYTHONHASHSEED': '0',
               'http_proxy': '@@DEAD@@', 'https_proxy': '@@DEAD@@', 'HTTP_PROXY': '@@DEAD@@', 'HTTPS_PROXY': '@@DEAD@@', 'no_proxy': '', 'NO_PROXY': ''}
        for st in K['steps']:
            r = subprocess.run([sys.executable, '-I'] + st, cwd=os.path.join(work, K.get('cwd', '')), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=@@TIMEOUT@@)
            if r.returncode: sys.exit('step %s failed (exit %d): %s' % (' '.join(st), r.returncode, r.stderr.decode('utf-8', 'replace')[-600:]))
        out = json.load(open(os.path.join(work, K['output']), encoding='utf-8'))
        h = dict(desk=K['name'], **reading(K['headline'], out))
        line = json.dumps(h, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.stdout.write(line)
    if '--check' in a:
        exp = open(os.path.join(HERE, 'expected.json'), encoding='utf-8').read()
        got = hashlib.sha256(line.encode('utf-8')).hexdigest(); want = open(os.path.join(HERE, 'expected.sha256')).read().split()[0]
        if line != exp or got != want: sys.stderr.write('DIFFERS from expected.json (sha256 %s, expected %s)\n' % (got, want)); return 1
        sys.stderr.write('matches expected.json, sha256 %s\n' % got)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
'''


def runner_text(name):
    src = lambda f: inspect.getsource(f)
    t = RUNNER.replace('@@NAME@@', name).replace('@@DEAD@@', DEAD).replace('@@TIMEOUT@@', str(RUN_TIMEOUT))
    disp = src(LH.display).replace(", now=None", "").replace("(now or time.time())", "0")   # 'age' (a clock) is never a kit headline
    return t.replace('@@DIG@@', src(LH.dig)).replace('@@F@@', src(LH._f)).replace('@@DISPLAY@@', disp)


# ------------------------------------------------------------------------------------------------------------------------------- build
def kit_json(slug):
    s = SPECS[slug]; h = LH.DESKS[slug]
    return {'desk': slug, 'name': h['name'], 'steps': s['steps'], 'cwd': s.get('cwd', ''), 'output': s['output'],
            'headline': {k: h[k] for k in ('field', 'n', 'of', 'lo', 'hi', 'outcome', 'keys', 'show') if h.get(k) is not None}}


def assemble(slug, dest, feed_bytes, feed):
    """write the kit for slug into dest (empty). Inputs of a fetch kit go to dest/../private-inputs. Returns the manifest."""
    s = SPECS[slug]; src = os.path.join(B, s['folder']); full = s['mode'] == 'inputs'
    os.makedirs(os.path.join(dest, 'code'))
    pin = os.path.join(dest, 'inputs') if full else os.path.join(dest + '.private', 'inputs'); os.makedirs(pin)
    man = {'desk': slug, 'name': LH.DESKS[slug]['name'], 'mode': s['mode'], 'made': utc(), 'inputs': [], 'code': []}
    import glob as _g
    rels = []
    for pat in s['inputs']:   # a pattern with * takes every file it matches, sorted
        if pat.startswith('newest:'):   # 'newest:<folder pattern>': every file of the newest folder it matches (by name), the read a headline comes from
            ds = sorted(x for x in _g.glob(os.path.join(src, pat[7:])) if os.path.isdir(x))
            if not ds: raise RuntimeError('no folder matches ' + pat)
            rels += sorted(os.path.relpath(os.path.join(ds[-1], f), src) for f in os.listdir(ds[-1]) if os.path.isfile(os.path.join(ds[-1], f))); continue
        rels += sorted(os.path.relpath(x, src) for x in _g.glob(os.path.join(src, pat)) if os.path.isfile(x)) if '*' in pat and not pat.startswith('@') else [pat]
    for rel in rels:
        p = os.path.join(src, rel)
        if rel.startswith('@'):   # '@<kit path>=<path under ~/bones-forge>': an input another desk keeps
            rel, other = rel[1:].split('=', 1); p = os.path.join(B, other)
        if not os.path.exists(p): raise RuntimeError('input missing: ' + rel)
        zipped = not rel.lower().endswith(('.gz', '.zip', '.xlsx', '.pdf', '.png', '.jpg'))   # files that are compressed already are stored as they are
        st = rel + '.gz' if zipped else rel; d = os.path.join(pin, st); os.makedirs(os.path.dirname(d), exist_ok=True)
        gz(p, d) if zipped else shutil.copyfile(p, d)
        row = {'path': rel, 'sha256': fsha(p), 'bytes': os.path.getsize(p), 'stored': st, 'gzip_added': zipped, 'stored_sha256': fsha(d), 'modified': utc(os.path.getmtime(p))}
        if full and os.path.getsize(d) > MAX_FILE: raise RuntimeError('input too large for a public kit: %s (%d bytes stored)' % (rel, os.path.getsize(d)))
        man['inputs'].append(row)
    for rel in s['code']:   # the desk's own files that run, byte for byte
        d = os.path.join(dest, 'code', rel); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(os.path.join(src, rel), d)
        man['code'].append({'path': rel, 'sha256': fsha(d), 'public_copy': '%s/blob/main/code/%s/%s' % (REPO, s.get('code_dir', slug), rel)})
    if s.get('extract'):   # the minimal extract, or clock_run.py, which runs the desk tick itself with the clock pinned and never with --publish of the desk's scoring (the tick scripts also fetch and publish, so they never run in a kit)
        rel = s['extract']; d = os.path.join(dest, 'code', rel); shutil.copyfile(os.path.join(EXTRACTS, rel), d)
        man['code'].append({'path': rel, 'sha256': fsha(d), 'extract_of': s.get('extract_of', '')})
    man['reference'] = []
    for rel in s.get('ref', []):   # the desk scripts the extract follows, byte for byte, for reading beside it (not run)
        d = os.path.join(dest, 'desk', rel); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(os.path.join(src, rel), d)
        man['reference'].append({'path': 'desk/' + rel, 'sha256': fsha(d)})
    if not full: man['sources'] = s.get('sources', []); man['why_not_included'] = s['why']
    json.dump(kit_json(slug), open(os.path.join(dest, 'kit.json'), 'w'), indent=1, sort_keys=True)
    json.dump(man, open(os.path.join(dest, 'MANIFEST.json'), 'w'), indent=1, sort_keys=True)
    open(os.path.join(dest, 'run.py'), 'w').write(runner_text(LH.DESKS[slug]['name']))
    return man


def run_kit(kdir, inputs=None, py=None):
    """run a kit's own command in a clean temp copy. Returns (exit code, stdout, stderr)."""
    tmp = tempfile.mkdtemp(prefix='kitgate-')
    try:
        k = os.path.join(tmp, 'kit'); shutil.copytree(kdir, k)
        if inputs: shutil.copytree(inputs, os.path.join(k, 'inputs'))
        a = [py or sys.executable, '-I', 'run.py', '--check']
        r = subprocess.run(a, cwd=k, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=RUN_TIMEOUT + 60,
                           env={'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': tmp, 'TZ': 'UTC', 'http_proxy': DEAD, 'https_proxy': DEAD})
        return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def write_readme(slug, dest, man, exp_line, exp_sha, pub):
    s = SPECS[slug]; h = LH.DESKS[slug]; name = h['name']; full = s['mode'] == 'inputs'
    hd = json.loads(exp_line)
    steps = ' then '.join('code/' + ' '.join(st) for st in s['steps'])
    L = ['# %s reproduce kit' % name, '', 'Heuremen LLC · https://indahl.ai/%s · https://indahl.ai/reproduce' % slug, '',
         'This kit recomputes the %s headline number and its outcome label with the desk\'s own code%s, from what the kit holds, with its network proxies pointed at a closed port.' % (name, ' (its scoring lines, copied as written)' if s.get('extract') and s.get('ref') else ''), '',
         '## The command', '', '```', 'python3 run.py --check', '```', '',
         ('Needs Python 3.9 or later with %s (PyPI). ' % s['deps'] if s.get('deps') else 'Needs Python 3.9 or later and nothing else. ') + 'It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `%s`.' % exp_sha, '',
         '## What it reproduces', '',
         'The headline as the live feed %s served it at the feed stamp %s, read by us at %s. The feed bytes had sha256 `%s`.' % (pub['feed'], pub['stamp'], pub['read_at'], pub['feed_sha256']), '',
         '- number: %s' % hd['display'], '- value: %s' % json.dumps(hd['value'])] + \
        (['- interval: %s to %s' % (hd['lo'], hd['hi'])] if hd.get('lo') is not None else []) + \
        (['- outcome: %s' % hd['outcome']] if hd.get('outcome') else ['- outcome: none, this headline carries no outcome label']) + ['',
         'The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, '
         'and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).', '',
         '## Inputs', '']
    if full:
        L += ['The exact files the desk\'s scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.', '']
    else:
        L += ['Not included. %s, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk\'s scoring read, with its size, '
              'its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.' % (s['why'][0].upper() + s['why'][1:]), '',
              'The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. '
              'With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.', '']
        L += ['- %s' % x for x in s.get('sources', [])] + ['']
    pk = PACK.get(slug) or {}
    if pk.get('src'):
        L += ['## Sources and their terms', '', 'As the %s data pack lists them. Credit each source when you use its values.' % name, ''] + ['- %s, %s. %s.' % (n, u, l[:1].upper() + l[1:]) for n, u, l in pk['src']] + ['']
    L += ['## Input files', '', '| File | Bytes | sha256 |', '|---|---|---|'] + ['| %s | %s | `%s` |' % (f['path'], '{:,}'.format(f['bytes']), f['sha256']) for f in man['inputs']] + ['',
          '## Code', ''] + ((['The desk\'s own scripts, byte for byte, under code/. They run in this order: %s. The same files are in the public repository under code/%s/.' % (steps, s.get('code_dir', slug)), '']) if not s.get('extract') else
          (['code/%s runs the desk\'s own scripts in code/, byte for byte, and changes %s. The same files are in the public repository under code/%s/. Scripts that run: %s.' % (s['extract'], s['extract_of'], s.get('code_dir', slug), steps), ''] if not s.get('ref') else
           ['The desk\'s tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/%s is the scoring step of that script and nothing else: %s. '
            'The desk files it follows are under desk/, byte for byte, to read beside it. %s that run: %s. Before every release the gate checks that this extract prints the number the desk published.'
            % (s['extract'], s['extract_of'], 'The scripts', steps), ''])) + [
          '## Files', '', '- kit.json: the steps, the output file and the headline fields.', '- run.py: the command.', '- expected.json and expected.sha256: the line run.py must print.',
          '- published.json: the headline as the live feed served it when this kit was made.', '- MANIFEST.json: every input and code file with its sha256.', '- desk/: the desk scripts the extract follows, where the kit runs an extract.', '- SHA256SUMS.txt: the sha256 of every file in this folder.', '']
    if s.get('note'): L += ['## Note', '', s['note'], '']
    open(os.path.join(dest, 'README.md'), 'w').write('\n'.join(L))


def build(slug, quiet=False):
    """make the kit for slug. It replaces the old kit only when the kit's own command, run in a clean folder, prints exactly the headline the
    live feed serves now. Returns (ok, message)."""
    if slug not in SPECS: return False, 'no kit spec'
    os.makedirs(KITS, exist_ok=True); os.makedirs(PRIV, exist_ok=True)
    stage = tempfile.mkdtemp(prefix='kitbuild-', dir=ROOT); dest = os.path.join(stage, slug)
    try:
        fb, feed = get_feed(slug); read_at = utc()
        live_h = headline_of(slug, feed)
        man = assemble(slug, dest, fb, feed)
        open(os.path.join(dest, 'expected.json'), 'w').write('{}\n'); open(os.path.join(dest, 'expected.sha256'), 'w').write('0\n')
        open(os.path.join(dest, 'SHA256SUMS.txt'), 'w').write('')
        pin = None if SPECS[slug]['mode'] == 'inputs' else dest + '.private/inputs'
        py = SPECS[slug].get('python')
        rc, out, err = run_kit(dest, pin, py)
        line = out if out.endswith('\n') else out + '\n'
        try: got = json.loads(line)
        except Exception: return False, 'the kit printed no headline: ' + (err.strip().splitlines() or ['?'])[-1][:300]
        if got != live_h:
            diff = {k: (got.get(k), live_h.get(k)) for k in live_h if got.get(k) != live_h.get(k)}
            return False, 'the kit does not reproduce the live feed now (kit, live): %s' % json.dumps(diff)[:400]
        fb2, feed2 = get_feed(slug)
        if headline_of(slug, feed2) != live_h: return False, 'the live feed moved during the build'
        es = sha(line.encode('utf-8'))
        open(os.path.join(dest, 'expected.json'), 'w').write(line); open(os.path.join(dest, 'expected.sha256'), 'w').write('%s  expected.json\n' % es)
        pub = {'feed': LH.feed_url(slug), 'read_at': read_at, 'stamp': LH.dig(feed, LH.DESKS[slug]['stamp']), 'feed_sha256': sha(fb), 'headline': live_h}
        json.dump(pub, open(os.path.join(dest, 'published.json'), 'w'), indent=1, sort_keys=True)
        write_readme(slug, dest, man, line, es, pub)
        names = sorted(os.path.relpath(os.path.join(r, f), dest) for r, _, fs in os.walk(dest) for f in fs if f != 'SHA256SUMS.txt')
        open(os.path.join(dest, 'SHA256SUMS.txt'), 'w').write(''.join('%s  %s\n' % (fsha(os.path.join(dest, n)), n) for n in names))
        rc, out2, err2 = run_kit(dest, pin, py)   # the finished kit, once more, with its real expected.json
        if rc or out2 != line: return False, 'the finished kit did not pass its own check: ' + err2.strip()[-300:]
        bad = guard_text(dest)
        if bad: return False, 'a kit file would be refused by the public repository guard: %s' % bad
        # place: kit folder (published) and private inputs (never published)
        old = os.path.join(KITS, slug); shutil.rmtree(old + '.old', ignore_errors=True)
        if os.path.exists(old): os.rename(old, old + '.old')
        os.rename(dest, old); shutil.rmtree(old + '.old', ignore_errors=True)
        if pin:
            pd = os.path.join(PRIV, slug); shutil.rmtree(pd, ignore_errors=True); os.makedirs(pd); os.rename(pin, os.path.join(pd, 'inputs'))
        ix = load_index(); ix[slug] = {'mode': SPECS[slug]['mode'], 'made': man['made'], 'expected_sha256': es, 'stamp': pub['stamp'], 'verified': utc(),
                                       'headline': live_h, 'inputs_bytes': sum(f['bytes'] for f in man['inputs']), 'code_sha': code_shas(slug)}
        save_index(ix)
        return True, 'kit made, %s, expected sha256 %s' % (live_h['display'], es[:16])
    except Exception as e:
        return False, '%s: %s' % (type(e).__name__, str(e)[:300])
    finally:
        shutil.rmtree(stage, ignore_errors=True)


# ------------------------------------------------------------------------------------------------------------------------------- guard
# the public repository refuses a push whose files carry a house name or say an AI wrote them (ledger/push_public.sh). A kit must never trip it.
_LEAK = re.compile(r"\bN[o]va's\b|\bN[o]va\s+(tick|ticks|clock|bus|time)\b|\b(ticks?|clock)\s+of\s+N[o]va\b")
_NOVA = re.compile(r"\bN[o]va\b")
_ALLOW = re.compile(r"Texas Solar N[o]va|Petra N[o]va|N[o]va Power|N[o]va Place|Amazon N[o]va|N[o]va\s+(?:2\s+)?(?:Micro|Lite|Pro|Premier|Sonic|Canvas|Reel|Act|Omni)\b"
                    r"|Bones (?:&middot;|·) Wayfinder (?:&middot;|·) Sage (?:&middot;|·) Shuttle (?:&middot;|·) N[o]va")
_AIAUTH = re.compile(r"(?<![|\w])(?:AI\s+named|an\s+AI\s+called|(?:told|written|narrated|drawn|authored)\s+(?:for\s+kids\s+)?by\s+an?\s+AI\b)", re.I)
_EXT = ('.html', '.js', '.json', '.md', '.py', '.txt', '.text', '.yml', '.sh', '.xml', '.csv', '.tsv', '.tex', '.bib', '.cff', '.jsonl')
def guard_text(d):
    for r, _, fs in os.walk(d):
        for f in fs:
            if not f.endswith(_EXT): continue   # the same file kinds push_public.sh reads (source data names such as a trial sponsor live in .gz inputs)
            p = os.path.join(r, f)
            t = open(p, 'rb').read().decode('utf-8', 'ignore')
            m = _LEAK.search(t) or (_NOVA.search(t) and _NOVA.search(_ALLOW.sub(' ', t))) or _AIAUTH.search(t)
            if m: return '%s (%s)' % (os.path.relpath(p, d), m.group(0))
    return None


# ------------------------------------------------------------------------------------------------------------------------------- ledger cover
def ledger_row(slug, rows=None):
    import ledger as L
    rows = rows or L.load()
    vs = [r for r in rows.values() if r.get('kind') == 'live_value' and r.get('live_of') == 'live.%s.headline' % slug and r.get('status') == 'live']
    return max(vs, key=lambda r: r['history'][0]['at']) if vs else None


def covered(slug, row, h):
    """None when the ledger value row covers the kit's headline (same label, not a material change under the desk's own rule), else why not"""
    if row is None: return 'no live ledger value row for this desk'
    spec = LH.DESKS[slug]; prev = row.get('reading') or {}
    if spec.get('outcome') and prev.get('outcome') != h.get('outcome'): return 'label %s, the ledger row %s says %s' % (h.get('outcome'), row['id'], prev.get('outcome'))
    why = LH.material(spec, prev, h)
    return None if why is None else 'against the ledger row %s: %s' % (row['id'], why)


def code_shas(slug):
    s = SPECS[slug]; f = lambda p: fsha(p) if os.path.exists(p) else None
    out = {rel: f(os.path.join(B, s['folder'], rel)) for rel in s['code'] + s.get('ref', [])}
    if s.get('extract'): out['extract:' + s['extract']] = f(os.path.join(EXTRACTS, s['extract']))
    out['spec'] = sha(json.dumps(s, sort_keys=True).encode()); out['runner'] = sha(RUNNER.encode()); out['readme'] = sha(inspect.getsource(write_readme).encode())
    return out


# ------------------------------------------------------------------------------------------------------------------------------- refresh / gate
def stale(slug, ix, rows, feed=None):
    """why the kit of slug needs remaking, or None"""
    k = ix.get(slug); kd = os.path.join(KITS, slug)
    if not k or not os.path.isdir(kd): return 'no kit yet'
    s = SPECS[slug]
    if k.get('code_sha') != code_shas(slug): return 'the desk code, the extract or the kit spec changed'
    c = covered(slug, ledger_row(slug, rows), k['headline'])
    if c and 'no live ledger' not in c: return c
    if feed is not None:
        live = headline_of(slug, feed); why = LH.material(LH.DESKS[slug], k['headline'], live)
        if why: return 'the live feed has moved past the kit: ' + why
    return None


def refresh():
    import ledger as L
    ix = load_index(); rows = L.load(); out = []
    for slug in SPECS:
        try: _, feed = get_feed(slug)
        except Exception as e: feed = None; out.append('%s: live feed not read (%s)' % (slug, type(e).__name__))
        why = stale(slug, ix, rows, feed)
        if not why: continue
        ok, msg = build(slug)
        out.append('%s: %s -> %s' % (slug, why, msg if ok else 'NOT REMADE: ' + msg)); ix = load_index()
    print('reproduce refresh: %d kits, %d remade or tried' % (len([s for s in SPECS if s in ix]), len([o for o in out if '->' in o])))
    for o in out: print('  ' + o)
    return 0


def gate(only=None):
    import ledger as L
    ix = load_index(); rows = L.load(); bad = []; notes = []; okn = 0; t0 = time.time()
    if not only:
        for d in LH.DESKS:
            if d not in SPECS and d not in NOKIT: bad.append('%s: a desk with a ledger headline has neither a kit nor a no-kit entry' % d)
    for slug in (only or SPECS):
        kd = os.path.join(KITS, slug)
        if slug not in ix or not os.path.isdir(kd): bad.append('%s: no kit (every desk in SPECS must have one)' % slug); continue
        pin = None
        if SPECS[slug]['mode'] == 'fetch':
            pin = os.path.join(PRIV, slug, 'inputs')
            if not os.path.isdir(pin): bad.append('%s: the stored inputs of this fetch kit are missing' % slug); continue
        _run = lambda d: {k: v for k, v in (d or {}).items() if k not in SPECS[slug].get('ref', [])}   # the desk files under desk/ are for reading beside an extract and never run
        if _run(ix[slug].get('code_sha')) != _run(code_shas(slug)): bad.append('%s: the code a kit runs, its extract or its spec changed since the kit was made, and refresh did not remake it' % slug); continue
        if ix[slug].get('code_sha') != code_shas(slug): notes.append('%s: a desk file the extract follows changed since the kit was made (the kit is remade on the next refresh that can reproduce the live feed)' % slug)
        rc, out, err = run_kit(kd, pin, SPECS[slug].get('python'))
        exp = open(os.path.join(kd, 'expected.json'), encoding='utf-8').read()
        if rc or out != exp: bad.append('%s: the kit does not reproduce its expected headline (%s)' % (slug, (err.strip().splitlines() or ['exit %d' % rc])[-1][:300])); continue
        if sha(out.encode('utf-8')) != ix[slug].get('expected_sha256'): bad.append('%s: the expected sha256 on /reproduce is not the kit\'s' % slug); continue
        h = json.loads(out); pub = json.load(open(os.path.join(kd, 'published.json')))
        if h != pub['headline']: bad.append('%s: the kit headline differs from the published headline it names' % slug); continue
        c = covered(slug, ledger_row(slug, rows), h)
        if c: bad.append('%s: %s' % (slug, c)); continue
        try:
            _, feed = get_feed(slug); why = LH.material(LH.DESKS[slug], h, headline_of(slug, feed))
            if why: bad.append('%s: the live feed has moved past the kit: %s' % (slug, why)); continue
        except Exception as e: bad.append('%s: live feed not read (%s)' % (slug, type(e).__name__)); continue
        ix[slug]['verified'] = utc(); okn += 1
    save_index(ix)
    print('reproduce gate: %d kits rerun from their own contents in %.0f s; breaches: %d' % (okn + len(bad), time.time() - t0, len(bad)))
    for b in bad: print('  ' + b)
    for n in notes: print('  note: ' + n)
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------------------------------------- mirror
def mirror(dest_repo):
    d = os.path.join(dest_repo, 'reproduce'); os.makedirs(d, exist_ok=True); ix = load_index(); n = 0
    keep = {s for s in SPECS if s in ix and os.path.isdir(os.path.join(KITS, s))}
    for x in os.listdir(d):
        if os.path.isdir(os.path.join(d, x)) and x not in keep: shutil.rmtree(os.path.join(d, x))
    for s in sorted(keep):
        t = os.path.join(d, s); shutil.rmtree(t, ignore_errors=True); shutil.copytree(os.path.join(KITS, s), t); n += 1
    open(os.path.join(d, 'README.md'), 'w').write(readme_index(ix))
    shutil.copyfile(os.path.abspath(__file__), os.path.join(d, 'reproduce_kits.py'))
    print('  public reproduce kits: %d copied' % n)
    return 0


def readme_index(ix):
    L = ['# Reproduce a desk headline', '', 'Heuremen LLC · https://indahl.ai/reproduce', '',
         'Each folder recomputes one desk\'s headline number and outcome label with the desk\'s own code, offline. In each folder run `python3 run.py --check`.', '',
         'reproduce_kits.py is the code that makes the kits and the release gate that reruns every kit before each release.', '',
         '| Desk | Inputs | Expected output sha256 |', '|---|---|---|']
    for s in sorted(k for k in SPECS if k in ix):
        L.append('| [%s](%s/) | %s | `%s` |' % (LH.DESKS[s]['name'], s, 'included' if SPECS[s]['mode'] == 'inputs' else 'fetch and verify', ix[s]['expected_sha256']))
    if NOKIT:
        L += ['', '## Desks without a kit', ''] + ['- %s: %s' % (v['name'], v['why']) for k, v in sorted(NOKIT.items())]
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------------------------------------------------------------------- pages
def _when(t):
    try: return D.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').strftime('%d %b %Y %H:%M UTC').lstrip('0')
    except Exception: return t or ''


def table_html():
    ix = load_index()
    o = ['<h2 id="desks">Reproduce a desk headline</h2>',
         '<p>For each desk below, a kit holds the desk\'s own scoring code, the inputs it read or the list of them with their sha256, and one command that recomputes the headline number and its outcome label offline. '
         'Before every release we run every kit in an empty folder from its own contents. The release is refused if a kit does not print the headline it names, '
         'if the row our ledger keeps for the desk does not cover that headline (the same label and the number inside the row\'s interval, or for a desk with no interval the same key fields), or if the live page has moved past it.</p>',
         '<p>Where a source\'s terms allow it, the kit includes the inputs. Where they do not, the kit lists each input file with its sha256 and the sources to fetch it from, and we rerun the kit on the copies we keep. '
         'The live page can move inside the interval between releases. A move outside it or a change of label needs a new ledger row and a new kit.</p>',
         '<div class="tablewrap"><table class="rp-t rk-t"><thead><tr><th scope="col">Desk</th><th scope="col">Inputs</th><th scope="col">Command</th><th scope="col">Expected output sha256</th><th scope="col">Last verified</th></tr></thead><tbody>']
    for s in sorted((k for k in SPECS if k in ix), key=lambda k: LH.DESKS[k]['name']):
        k = ix[s]; nm = LH.DESKS[s]['name']
        inc = 'Included' if SPECS[s]['mode'] == 'inputs' else 'Fetch and verify'
        o.append('<tr id="kit-%s"><th scope="row"><a href="/%s">%s</a></th><td>%s</td><td><a href="%s/tree/main/reproduce/%s">reproduce/%s</a><br><code>python3 run.py --check%s</code></td><td><code class="rk-h">%s</code></td><td>%s</td></tr>'
                 % (s, s, E(nm), inc, REPO, s, s, '' if SPECS[s]['mode'] == 'inputs' else ' --inputs DIR', E(k['expected_sha256']), E(_when(k.get('verified')))))
    o.append('</tbody></table></div>')
    if NOKIT:
        o.append('<h2 id="no-kit">Desks without a kit</h2><p>These desks have no kit. The reason and what can be checked are listed for each.</p><ul class="ticks">')
        for s, v in sorted(NOKIT.items(), key=lambda kv: kv[1]['name']):
            o.append('<li id="kit-%s"><a href="/%s">%s</a>: %s %s</li>' % (s, s, E(v['name']), E(v['why']), v['check']))
        o.append('</ul>')
    o.append('<p>To run a kit, clone the repository and run the command in the desk\'s folder. The code that makes the kits and the release gate is <a href="%s/blob/main/reproduce/reproduce_kits.py">reproduce/reproduce_kits.py</a>.</p>' % REPO)
    return ''.join(o)


CSS = '<style>.rk-t td{vertical-align:top}.rk-h{word-break:break-all;font-size:12px}.rpk{margin:0 0 12px}</style>'


def apply(PAGES):
    """the per-desk table on /reproduce, and a Reproduce this number link on each desk page with a kit or a no-kit note"""
    ix = load_index(); n = 0
    if '/reproduce' in PAGES:
        d = PAGES['/reproduce']; i = d.find('<h2>What cannot be rebuilt from the repository alone</h2>')
        if i > 0:
            d = d.replace('<h2>What cannot be rebuilt from the repository alone</h2>', '<h2>What the release check does not cover</h2>', 1)
            d = d.replace('The comparison above needs no rerun.</p>', 'The comparison above needs no rerun. The desk headlines are covered by the kits below.</p>', 1)
        j = d.rfind('</section>')
        if j > 0: d = d[:j] + table_html() + d[j:]
        PAGES['/reproduce'] = d.replace('</head>', CSS + '</head>', 1)
    for s in list(SPECS) + list(NOKIT):
        p = '/' + s
        if p not in PAGES or '<main class="wrap">' not in PAGES[p]: continue
        if s in SPECS and s not in ix: continue
        line = ('<p class="meta rpk"><a href="/reproduce#kit-%s">Reproduce this number</a>: the desk\'s own scoring code, %s and one command that recomputes the headline offline.</p>'
                % (s, 'the inputs it read' if SPECS.get(s, {}).get('mode') == 'inputs' else 'the sha256 of every input it read')) if s in SPECS else \
               '<p class="meta rpk"><a href="/reproduce#kit-%s">Why this number has no kit</a>, and what can be checked.</p>' % s
        PAGES[p] = PAGES[p].replace('<main class="wrap">', '<main class="wrap">' + line, 1); n += 1
    return n


# ------------------------------------------------------------------------------------------------------------------------------- selftest
def selftest():
    """copy one included-input kit, corrupt one input byte, and require the gate's run to refuse it"""
    ix = load_index(); s = next((k for k in SPECS if k in ix and SPECS[k]['mode'] == 'inputs'), None)
    if not s: print('selftest: no included-input kit to test'); return 1
    tmp = tempfile.mkdtemp(prefix='kitself-')
    try:
        k = os.path.join(tmp, s); shutil.copytree(os.path.join(KITS, s), k)
        rc, out, err = run_kit(k); assert rc == 0, 'the untouched kit should pass: ' + err
        man = json.load(open(os.path.join(k, 'MANIFEST.json'))); f = os.path.join(k, 'inputs', next(x for x in man['inputs'] if x.get('gzip_added'))['stored'])
        b = bytearray(gzip.decompress(open(f, 'rb').read())); b[len(b) // 2] ^= 1
        with open(f, 'wb') as o:
            with gzip.GzipFile(filename='', mode='wb', fileobj=o, mtime=0) as z: z.write(bytes(b))
        rc, out, err = run_kit(k); assert rc != 0 and 'differs' in err, 'a corrupted input must refuse: %s %s' % (rc, err)
        open(os.path.join(k, 'expected.json'), 'a').write(' ')
        print('selftest: %s kit passes untouched, refuses a corrupted input (%s)' % (s, err.strip().splitlines()[-1][:120]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['build']:
        want = list(SPECS) if a[1:] == ['all'] else a[1:]; rc = 0
        for s in want:
            ok, msg = build(s); print('%-11s %s %s' % (s, 'ok  ' if ok else 'FAIL', msg)); rc |= 0 if ok else 1
        sys.exit(rc)
    elif a[:1] == ['refresh']:
        try: refresh()
        except Exception as e: print('reproduce refresh: stopped (%s: %s), the gate decides' % (type(e).__name__, str(e)[:200]))
        sys.exit(0)
    elif a[:1] == ['gate']: sys.exit(gate(a[1:] or None))
    elif a[:1] == ['mirror']: sys.exit(mirror(a[1]))
    elif a[:1] == ['selftest']: sys.exit(selftest())
    else: print(__doc__)
