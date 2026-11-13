# SOCIAL ship plan (prepared 10 Nov 2026, NOT APPLIED)

Staging only. Nothing below has been run or edited outside `social_index/`. No deploy, no `ledger/ship.sh`, no edit to
`indahl-ai/build_site.py`, the worker, the ledger or `copies.json`. Modelled on the WIKI ship of 10 Nov 2026 (indahl-ai e059c6b7,
`wiki_index/CHECKS.md` entries "WIKI ship" and "WIKI live check").

Long unchanged stretches inside a diff line are cut with `…`. Apply each change by hand at the place shown, with a backup
`<file>.bak-<date>-socialship` first, as the WIKI ship did.

## What is staged

| File | What it is |
|---|---|
| `social_index/build_social.py` | Assembler. Places `dsa/`, `adspend/` and `tiktok/` section files byte for byte, adds the lead, the outcomes table, the Bluesky slot and the headline. Opens `bluesky/` only with `--bluesky-cleared`. |
| `social_index/social.html` | The staged page (full page with the site chrome copied from `indahl-ai/launch.html`, as `wiki.html` is). |
| `social_index/summary_social.json` | Headline, headline rule, per-section outcomes, section and summary hashes, and the summary path of every number the assembler printed. |
| `social_index/check_social.py` | Every number on the page against the section summaries and data files, headline rule, Bluesky slot, copy rules, site gate pre-flight. Read only. |

State on 10 Nov 2026: `check_social.py` PASS on the numbers (steps A to G). Step H, the site gate pre-flight, finds one ship blocker (open item 1).

## Open items to settle before the ship

1. **Site gate blocker: "trusted flagger".** `heuremen-specbook/tone_scan.py` ARGUE has `\btrust(?:ed|worthy)?\b`. The DSA section says
   "trusted flagger" 53 times. It is the DSA's own term (Article 22) and the name of a report field, so it cannot be reworded. `site_gate.py`
   would refuse the ship with 53 breaches of 0b.8. Proposed change, same kind as the WIKI quote exemption (backup
   `tone_scan.py.bak-<date>-socialship`):
   ```diff
   --- heuremen-specbook/tone_scan.py
   -         r"\btrust(?:ed|worthy)?\b", r"\bensur(?:e|es|ing)\b", …
   +         r"\btrust(?:ed|worthy)?\b(?! flaggers?\b)", r"\bensur(?:e|es|ing)\b", …   # SOCIAL ship: "trusted flagger" is the DSA's term (Article 22) and a report field name
   ```
   With that one change the pre-flight reads 0 hits (checked by counting: all 53 hits are followed by "flagger").
2. **Headline.** The staged headline is `31 of 6,160`, from the political ad spend section: rows that read above, below or consistent and do
   not turn on the timing band, the itemization rule set after the data, a name match or a note
   (`summary_adspend.json` `outcomes.decided_cycle_rows.robust_id_no_flags`). It is the only count in the three summaries that is both
   decided and free of rules set after the data. DSA has 162 decided rows as printed (39 above, 82 below, 41 consistent), but
   `summary_dsa.json` does not say which of them use no rule set after the data, so DSA gives no headline. A count from the row flags in
   `dsa/public/dsa.json` (`rules_after_data`, `defined_after_data` both empty) gives 23 above, 36 below, 19 consistent on main rows. It is
   not used: one notice row is unflagged although the section says the notice rules were set after the data, so the flags are not complete.
   If a DSA headline is wanted, the DSA tick should write that count into `summary_dsa.json` and a reader goes into `HEADLINE_READERS`.
   TikTok has no decided row under its committed rules. Its one Above is a reading defined after the data and is kept out.
3. **Title.** Staged: `SOCIAL | Platform Reports Against the Filings | Heuremen LLC`, hero `SOCIAL · Platform Reports Against the Filings`,
   division line `Platform reports against the filings`. One constant each in `build_social.py` (`TITLE`, `HERO`, `DESC`).
4. **Respond units.** Section links as written: DSA `/respond?u=social-dsa`, ad spend `/respond?u=adspend-all`, TikTok none. The page adds
   `/respond?u=social-all` and a replies block with prefix `social`. The worker and `respondreq.js` accept neither `social` nor `adspend`
   today, so both links answer as refused until the regex change below. A reply filed under `adspend-all` would not show in the page's
   replies block (prefix `social`). Cleaner: the ad spend tick writes `social-adspend` and the TikTok tick adds a `social-tiktok` line. That
   is the section owners' edit, not made here. The diff below accepts both prefixes so nothing breaks either way.
5. **Data files the sections link.** `/social/dsa.json`, `/social/dsa_summary.json`, `/social/dsa_automation_monthly.json` (in
   `dsa/public/`), `/social/adspend.json` (`adspend/data/adspend_public.json`, 5.7 MB), and the page's `/social/summary.json`. None is
   served yet. The TikTok section says "The data file keeps the outcome under the first rule for every row" and links no data file. Either
   the TikTok tick adds a link to `/social/tiktok.json` (`tiktok/data/tiktok.json`, 1.1 MB, not yet read for what it exposes) or that
   sentence stays without a link.
6. **Code links.** The ad spend section links `code/adspend` in the public repo. DSA and TikTok link no code. `push_public.sh` copies only
   the top level of a desk folder, so each section needs its own entry and its folder made once in the mirror (diff below).
7. **Clearance on disk.** `adspend_referee/REFEREE.md` (9 Nov 22:15) and `tiktok_referee/REFEREE.md` (10 Nov 04:45) both end FIX THEN
   SHIP, and the section files are newer than both. The brief says ad spend is cleared and the TikTok fixes are applied. Read only reruns
   today: `adspend_referee/scripts/page_check.py` prints `PROBLEMS: none` on the current section. `tiktok_referee/code/r2_page_check.py`
   finds 404 numbers and outcomes, 0 number differences and 21 outcome differences, and all 21 are the referee's own B1 and B2 moves
   (18 proactive rows and 3 automated share readings to Cannot tell). Neither folder holds a written second-pass verdict.
8. **Small.** `class="mtx wide"` in the DSA section has no rule in `style.css` (harmless, the table still scrolls). The outcomes table
   prints the stamps as the summaries hold them, in UTC, as the TikTok section and WIKI do.

## What remains for Bluesky

1. Wait for the replay and the referee. Nothing in `bluesky/` or `bluesky_referee/` was read, listed or touched for this build.
2. The section needs `bluesky/section_bluesky.html` (one `<section id="…">` block, `<h2>` title, no page chrome, no script) and
   `bluesky/summary_bluesky.json`.
3. In `build_social.py`: add the Bluesky entry to `SECTIONS` with its summary paths (outcome tally, row count, stamp, gate) so it gets a
   row in the outcomes table, and a reader in `HEADLINE_READERS` only if its summary counts decided rows free of rules set after the data.
   Until then `--bluesky-cleared` places the section as it is with no table row.
4. In `check_social.py`: add Bluesky to `CFG` (same paths, plus its data files for step D) and, if needed, its formulas in `derived()`.
   Step D fails on any section number it cannot find, so this step is not optional.
5. `python3 -I build_social.py --bluesky-cleared && python3 -I check_social.py --gate`. The slot text "being read" must be gone
   (`build_site.py` asserts it, below). Add Bluesky to `DESC`, the feed line and the API text if it belongs there.
6. Then the ship steps below.

## Ship steps, in order (as WIKI)

1. Settle the open items. Rebuild and check: `python3 -I build_social.py [--bluesky-cleared] && python3 -I check_social.py --gate`.
2. Freeze the reading: copy `summary_social.json` and each `summary_<key>.json` to `social_index/shipped/shipped_<date>_…json` (the
   ledger rows grep the frozen copies, as `wiki_index/data/shipped_20261110_*` do).
3. `social_index/CHECKS.md`: a ship entry with packs P and O, complete, since `ledger.py add` needs `--checks` (WIKI: "2026-11-10 04:50
   WIKI ship").
4. Ledger first (rows below), then `copies.json`, then the surface edits (build_site.py, worker, respondreq, api, push_public).
5. `ledger/ship.sh "SOCIAL desk at /social under HERMES: …"`. Then the live check entry in `CHECKS.md`.

### 1. `indahl-ai/build_site.py` (backup `build_site.py.bak-<date>-socialship`)

```diff
@@ line 10, HOME
-        '/trials': '/hermes', … '/water': '/atlas', '/wiki': '/hermes'}
+        '/trials': '/hermes', … '/water': '/atlas', '/wiki': '/hermes', '/social': '/hermes'}
@@ line 79, _hlslot
     if path == '/wiki' and globals().get('_WIKISLOT'): return _WIKISLOT   # 10 Nov 2026: WIKI ships one reading, …
+    if path == '/social' and globals().get('_SOCIALSLOT'): return _SOCIALSLOT   # SOCIAL ships one reading per section, so its headline is the one built with the page (social_index/build_social.py)
@@ after line 1386, the WIKI block
 _FEED.append(('/wiki', 'WIKI: Figures Against Their Source', …))
+# SOCIAL, under HERMES. One page, one section per pair of records. social_index/build_social.py places each cleared section file
+# (section_<key>.html, written by that section's own tick) byte for byte and reads every number outside the sections from
+# summary_<key>.json. Body and headline are taken from social.html here, so nav, division line, footer and reference code come from page().
+_so = open(os.path.join(HERE, '..', 'social_index', 'social.html'), encoding='utf-8').read()
+_so_main = _so[_so.index('<main class="wrap">') + len('<main class="wrap">'):_so.index('</main>')]
+_SOCIALSLOT = _so_main[:_so_main.index('</section>') + len('</section>')] if _so_main.startswith('<section id="hl-slot"') else ''
+_SOCIALBODY = _so_main[len(_SOCIALSLOT):]
+assert 'section is being read' not in _SOCIALBODY, 'SOCIAL: the Bluesky slot is still in the page (build_social.py --bluesky-cleared)'
+assert '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>' in _SOCIALBODY, 'SOCIAL: the division line is not where build_social.py puts it'
+_SOCIALBODY = _SOCIALBODY.replace('<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>', '', 1).lstrip('\n')
+PAGES['/social'] = page('/social', 'SOCIAL | Platform Reports Against the Filings | Heuremen LLC', 'SOCIAL: what large platforms state about their own conduct, read against public filings that cover the same activity. EU moderation reports against the DSA Transparency Database, Google\'s political ad library against FEC filings, and TikTok\'s quarterly report against its EU filings.', _SOCIALBODY, hero_slim('SOCIAL &middot; Platform Reports Against the Filings'))
+_FEED.append(('/social', 'SOCIAL: Platform Reports Against the Filings', 'EU moderation reports against the DSA Transparency Database, Google\'s political ad library against FEC filings, and TikTok\'s quarterly report against its EU filings.'))
@@ line 1923, DESKS['/hermes']
-                  … ('/linkrot', 'LINKROT', 'Stated code links against live'), ('/wiki', 'WIKI', 'Cited figures against their source')]}
+                  … ('/linkrot', 'LINKROT', 'Stated code links against live'), ('/wiki', 'WIKI', 'Cited figures against their source'), ('/social', 'SOCIAL', 'Platform reports against the filings')]}
```

Notes.
- The title and description strings must equal `TITLE` and `DESC` in `build_social.py`.
- `_live` (line 47) is left alone. SOCIAL has no live feed, so it gets no Dataset block with a `live.json` distribution. WIKI went in
  because `/wiki/live.json` is read again weekly.
- The first assert stops a ship with the Bluesky slot in the page. If the call is to ship the three sections with the slot showing, drop
  that one assert and nothing else.
- If no section qualifies for a headline, `build_social.py` writes no headline block, `_SOCIALSLOT` is empty and `_hlslot` falls through
  to its normal path (no `social` key in `watch/headlines.json`, so no block).
- The dropdown under HERMES and the HERMES division list come from `DESKS`, as for WIKI. `pages.js` and every page's nav are rebuilt by
  `build_site.py` in `ship.sh` step 1 (WIKI touched 619 files that way).

### 2. Worker: `cloudflare-workers/heuremen-door/worker.js` (backup `worker.js.bak-<date>-socialship`)

```diff
@@ line 308, the respond unit test
-  const ok = /^(model|oy|…|tape|water|wiki)-[a-z0-9._-]{1,70}$/.test(uq);
+  const ok = /^(model|oy|…|tape|water|wiki|social|adspend)-[a-z0-9._-]{1,70}$/.test(uq);
```
`indahl-ai/respondreq.js` (backup the same way):
```diff
@@ line 5
-const UNIT = /^(model|oy|…|tape|water|wiki)-[a-z0-9._-]{1,70}$/;
+const UNIT = /^(model|oy|…|tape|water|wiki|social|adspend)-[a-z0-9._-]{1,70}$/;
```
Drop `|adspend` from both if the ad spend section's link is changed to `social-adspend` (open item 4).

No route is needed for the data files. They are static files under `public/social/` (next section), served by the assets binding like
`public/water/live.js`. WIKI needed a route only because `/wiki/live.json` is read from KV.

`indahl-ai/api.js` (backup the same way), one entry in each list, after the `wiki` entries (lines 42 and 89):
```diff
+  { id: 'social', url: 'https://indahl.ai/social', what: "What large platforms state about their own conduct against public filings that cover the same activity: EU moderation reports against the DSA Transparency Database, Google's political ad library against FEC filings, TikTok's quarterly report against its EU filings." },
…
+  { name: 'social', description: "SOCIAL: the outcome counts and headline of each section (EU moderation reports against the DSA Transparency Database, Google's political ad library against FEC filings, TikTok's quarterly report against its EU filings), with the links to each section's rows.", params: {}, run: async (env, a, req) => wrap('https://indahl.ai/social', await (await env.ASSETS.fetch(new Request(new URL('/social/summary.json', req.url)))).json()) },
```
The `ASSETS.fetch` form is the one `api.js` line 8 already uses for `/<division>/list.json`. Check the `run` signature against `callTool`
(`t.run(env, args, req)`) when applying.

### 3. `ledger/copies.json` (backup `copies.json.bak-<date>-socialship`)

Canonical is the file the section's tick writes. `copies.py publish` puts it in the worker's `public/social/`, and `copies.py live`
checks the URL after the ship. Same shape as `water-live-js`, with the direction turned (there the worker copy is the one edited).

```diff
+ "social-summary": {"canonical": "social_index/summary_social.json", "copies": ["cloudflare-workers/heuremen-door/public/social/summary.json"], "live": ["https://indahl.ai/social/summary.json"], "_note": "SOCIAL: written by social_index/build_social.py. Never edit the copy."},
+ "social-dsa-rows": {"canonical": "social_index/dsa/public/dsa.json", "copies": ["cloudflare-workers/heuremen-door/public/social/dsa.json"], "live": ["https://indahl.ai/social/dsa.json"], "_note": "SOCIAL, DSA section: written by the DSA tick."},
+ "social-dsa-summary": {"canonical": "social_index/dsa/public/dsa_summary.json", "copies": ["cloudflare-workers/heuremen-door/public/social/dsa_summary.json"], "live": ["https://indahl.ai/social/dsa_summary.json"], "_note": "SOCIAL, DSA section."},
+ "social-dsa-automation": {"canonical": "social_index/dsa/public/dsa_automation_monthly.json", "copies": ["cloudflare-workers/heuremen-door/public/social/dsa_automation_monthly.json"], "live": ["https://indahl.ai/social/dsa_automation_monthly.json"], "_note": "SOCIAL, DSA section."},
+ "social-adspend-rows": {"canonical": "social_index/adspend/data/adspend_public.json", "copies": ["cloudflare-workers/heuremen-door/public/social/adspend.json"], "live": ["https://indahl.ai/social/adspend.json"], "_note": "SOCIAL, ad spend section: the public rows file (5.7 MB)."}
```
Before applying: make `public/social/`, confirm `copies.py publish` creates a copy that does not exist yet (WATER's copy existed), and
confirm `dsa/public/dsa_summary.json` (542 bytes) is the file meant for the public and not `dsa/summary_dsa.json` (they differ). Add a
`social-tiktok-rows` entry only if open item 5 goes that way.

### 4. `ledger/ledger.py` and the ledger rows (backups `ledger.py.bak-…`, `ledger.jsonl.bak-…`)

```diff
@@ SURFACES, after 'wiki'
     'wiki': 'indahl-ai/wiki.html',   # 10 Nov: the WIKI desk (HERMES); …
+    'social': 'indahl-ai/social.html',   # the SOCIAL desk (HERMES); built by social_index/build_social.py from the section files, headline built with it
```

Rows go in before the page carries the numbers (WIKI P7), each with `--checks social_index/CHECKS.md`, source a frozen summary and an exact
grep string. Snippets are the built page's own text, so take them from `indahl-ai/social.html` after `build_site.py` runs and put them
on with `ledger.py on`. Values today:

| id | claim | value | unit | outcome | source file (frozen copy) | grep |
|---|---|---|---|---|---|---|
| `social.adspend.decided.robust` | Matched committees and cycles that read above, below or consistent with an outcome that does not turn on timing, the itemization rule, a name match or a note | 31 | of 6160 | COUNT | `summary_adspend.json` | `"robust_id_no_flags": 31` |
| `social.adspend.decided` | Matched committees and cycles that read above, below or consistent | 80 | of 6160 | COUNT | `summary_adspend.json` | `"n": 80` |
| `social.adspend.above` / `.below` / `.consistent` / `.cannot_tell` / `.nothing` | Ad spend rows by outcome, all cycles | 28 / 26 / 26 / 6056 / 24 | of 6160 | COUNT | `summary_adspend.json` | the `"all": {…}` tally |
| `social.dsa.above` / `.below` / `.consistent` / `.cannot_tell` / `.nothing` | DSA comparison rows by outcome, as printed | 39 / 82 / 41 / 330 / 27 | of 519 | COUNT | `summary_dsa.json` | the `"outcomes": {…}` tally |
| `social.tiktok.cannot_tell` / `.nothing` | TikTok rows by outcome under the committed rules | 330 / 498 | of 828 | COUNT | `summary_tiktok.json` | `"CANNOT_TELL": 330` and `"NOTHING_RETURNED": 498` |
| `social.tiktok.after_data.above` | TikTok EU rows that read above in the reading defined after the data (videos removed, Jan to Mar 2026, limits stated). Not in the headline | 1 | of 60 | COUNT | `summary_tiktok.json` | `"ABOVE": 1` |

Command shape (one per row):
```
python3 ledger/ledger.py add social.adspend.decided.robust --claim "…" --value 31 --unit "of 6160" --outcome COUNT \
  --source social_index/shipped/shipped_<date>_summary_adspend.json --grep '"robust_id_no_flags": 31' --checks social_index/CHECKS.md
python3 ledger/ledger.py on social.adspend.decided.robust social "31 of 6,160"
```
The rows are counts, as the WIKI population and GDP rows are. No section's own featured rows are added here. If Bones wants them in the
ledger they come from the section summaries the same way. Bluesky rows follow once its summary is read.

### 5. `ledger/push_public.sh` (backup `push_public.sh.bak-<date>-socialship`)

```diff
@@ line 48, DESKS
-         … 'water': ('water_index', A), 'wiki': ('wiki_index', A), 't1t2-check': ('t1t2_check', A), …
+         … 'water': ('water_index', A), 'wiki': ('wiki_index', A), 'social': ('social_index', A), 'adspend': ('social_index/adspend', A), 'social-dsa': ('social_index/dsa', A), 'social-tiktok': ('social_index/tiktok', A), 't1t2-check': ('t1t2_check', A), …
```
The copy runs only for folders that already exist in the mirror, so make `public_mirror/indahl.ai/code/social`, `code/adspend`,
`code/social-dsa` and `code/social-tiktok` once, each with a short README as WIKI got. Only `PLAN*.md`, `*.py` and `spec.json` at a
folder's top level are copied, so `SHIP_PLAN.md`, the data folders and the referee folders stay private. `code/adspend` is the path the
ad spend section already links. Read every `*.py` in the three section folders for paths and tokens before the first push, as the guards
in `push_public.sh` will.

### 6. After the ship, as WIKI did

- `nodes_repo/drift/targets.json`: add page `social`. No feed entry unless a rider is set up.
- `stack_index/stack_tick.py`: a SOCIAL row only if the headline stays a single count (WIKI has one at line 83).
- No tick bus rider. Each section is one reading. A rider is a later call, section by section.
- Live check entry in `social_index/CHECKS.md`: live page equals the built `indahl-ai/social.html`, `/social/*.json` equal their
  canonicals (`copies.py live`), `/respond?u=social-all` answers 200, `/api/v1/social` returns the summary, menu entry SOCIAL under
  HERMES after WIKI.

## Reproduce the staging check

```
cd ~/bones-forge/social_index
python3 -I build_social.py
python3 -I check_social.py            # numbers, headline rule, slot, copy. Add --gate to fail on site gate hits, --list for full lists
```
