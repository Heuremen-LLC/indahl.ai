#!/bin/bash
# 10 Nov: a ship always runs under the kernel site lock (ledger/site_lock.py); a ship started outside it waits in line
if [ -z "$SITE_LOCK_HELD" ]; then exec python3 "$(cd "$(dirname "$0")" && pwd)/site_lock.py" run --label "ship.sh: $1" -- bash "$0" "$@"; fi
# ship.sh "what changed" -- ONE command from source to live (23 Oct 2026; his "a system like the big companies, so we stop updating by hand").
# The big-company pattern on one Mac: single source of truth -> build -> gates -> deploy -> verify live. Any gate failing stops everything.
#   1 BUILD   re-render every canonical whose source changed (the paper via tectonic, Faults/Guards via ligera/render.sh, the bill via render_bill.py)
#   2 COPY    copies.py publish: every canonical over all its copies (copies.json)
#   3 GATES   check_ledger.py (every public number has its row) + copies.py check (every copy identical) + site_gate.py (the specbook)
#   4 COMMIT  heuremen.org and indahl-ai, if changed (new files cited by a live ledger row are added) (their pre-commit hooks run the same gates again)
#   5 DEPLOY  push heuremen.org; npx wrangler deploy for indahl.ai if the worker's files changed
#   6 VERIFY  copies.py live: every public URL byte-identical to its canonical (retries while caches refresh)
#   (11 Nov) downloads.py refresh runs first in step 1 and downloads.py gate in step 3: every public download equals its source or ship refuses
#   (11 Nov) sweep_backups.py in step 1 and the backups gate in step 3 keep backup files out of the served folder and the public mirror; 7d archive push, 7e zenodo_sync.py --publish after a verified deploy
#   7 STAMPS  stamps.py release: OpenTimestamps on the release record + Internet Archive captures of what changed (logs, never fails a release)
set -euo pipefail
MSG="${1:?usage: ship.sh \"what changed\"}"
B="$HOME/bones-forge"; L="$B/ledger"; W="$B/cloudflare-workers/heuremen-door"
exec > >(tee "$L/.last_ship_gates.txt") 2>&1   # 10 Nov: the ship output is kept, so /build.json can carry the gate lines (indahl-ai/accountability.py buildinfo)
AUTHOR=(-c user.name=Wayfinder -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
newer() { [ "$1" -nt "$2" ]; }
echo "== 1 BUILD"
for k in FAULTS:faults GUARDS:guards; do src="$B/ligera/${k%%:*}.html"; out="$B/heuremen.org/${k##*:}.pdf"
  if newer "$src" "$out"; then "$B/ligera/render.sh" "$src" "$out"; else echo "  ${k##*:}: up to date"; fi; done
if newer "$B/arxiv_one_readout/main.tex" "$B/heuremen.org/a-readout-is-not-an-idle.pdf"; then
  T=$(mktemp -d); cp -p "$B/arxiv_one_readout/main.tex" "$B/arxiv_one_readout/refs.bib" "$T/"; cp -Rp "$B/arxiv_one_readout/figures" "$T/"
  (cd "$T" && tectonic main.tex >/dev/null 2>&1) || { echo "SHIP REFUSED: the paper does not compile"; exit 1; }
  cp "$T/main.pdf" "$B/heuremen.org/a-readout-is-not-an-idle.pdf"; cp "$T/main.pdf" "$B/arxiv_one_readout/main.pdf"; rm -rf "$T"; echo "  paper: rebuilt"
else echo "  paper: up to date"; fi
# 30 Oct: the public repo builds the paper from its own copy of the source and checks it against the live PDF (paper workflow); keep that
# copy equal to ours on every ship, so the public build never runs on stale source.
PP="$B/public_mirror/heuremen.org/paper"; if [ -d "$PP" ]; then cp "$B/arxiv_one_readout/main.tex" "$B/arxiv_one_readout/refs.bib" "$PP/"
  for f in "$B"/arxiv_one_readout/figures/*.py "$B/arxiv_one_readout/figures/README.md"; do [ -f "$f" ] && cp "$f" "$PP/figures/"; done; echo "  paper source: synced to the public repo"; fi
if newer "$B/indahl-ai/qia_template/QIA-2026-001.json" "$B/indahl-ai/qia_template/QIA-2026-001.pdf"; then
  (cd "$B/indahl-ai/qia_template" && python3 render_bill.py QIA-2026-001.json); else echo "  bill: up to date"; fi
python3 "$L/sweep_backups.py"   # 11 Nov: backup-named files and folders are MOVED to archive_private/public_backups before anything is built or gated
python3 "$B/census_index/refresh_page.py"   # 11 Nov: CENSUS page tables and census.* ledger rows follow the latest desk run (ledger before surface)
python3 "$B/neo_index/refresh_page.py"   # 11 Nov: NEO page tables and neo.* ledger rows follow the latest desk run (ledger before surface)
python3 "$B/quake_index/refresh_page.py"   # 11 Nov: QUAKE page tables and quake.* ledger rows follow the latest desk run (ledger before surface)
python3 "$B/ledger/roadmap_sync.py"   # 11 Nov: /changes follows the record (every live desk listed, open items recomputed), no hand edits
python3 "$B/qia_leads/matrix_page/render_list.py"   # 11 Nov: the /qia/list table is rendered from list.json (one source for the page and the download)
python3 "$L/downloads.py" refresh   # 11 Nov: every download is re-made from its source (copies.py publish), the List packs and the QIA Research Package are rebuilt when a file inside differs from its source, pack sizes re-read, all before build_site.py reads them
{ python3 "$B/indahl-ai/reproduce_kits.py" refresh | tail -30; } || true   # 10 Nov: remake the desk reproduce kits the ledger or a live feed has moved past (never fails here, the gate in step 3 decides)
(cd "$B/indahl-ai" && python3 build_site.py)
python3 "$L/downloads.py" refresh --post || { [ $? -eq 10 ] && { (cd "$B/indahl-ai" && python3 build_site.py) && python3 "$L/downloads.py" refresh --post; }; }   # 11 Nov: packs made from built pages (OY) are rebuilt after the pages; exit 10 = one changed, so the site is built once more with its new size and ledger row, and the pack's input record is re-read against those pages (contents unchanged, so no second pack)
python3 "$L/receipts.py" build   # 10 Nov: one receipt page per ledger row at indahl.ai/r/<row> (build_site.py has already put the receipt links on the pages)
echo "== 2 COPY";  python3 "$L/copies.py" publish | tail -1
echo "== 3 GATES"; python3 "$L/check_ledger.py" | tail -1; python3 "$L/copies.py" check | tail -1
DG=$(python3 "$L/downloads.py" gate 2>&1) || true; if ! echo "$DG" | grep -q "stale: 0" && ! echo "$DG" | grep "STALE" | grep -vq "its feed moved past the pack"; then echo "downloads: a live feed moved mid-ship, packs rebuilt once and re-checked"; python3 "$L/downloads.py" refresh >/dev/null 2>&1; DG=$(python3 "$L/downloads.py" gate 2>&1) || true; fi; echo "$DG" | tail -1; echo "$DG" | grep -q "stale: 0" || { echo "$DG" | head -20; echo "SHIP REFUSED: a download is stale"; exit 1; }   # 11 Nov: downloads gate, a stale download or pack stops the ship (runs once)
BG=$(python3 "$L/backup_patterns.py" 2>&1) || true; echo "$BG" | tail -1; echo "$BG" | grep -q "backups gate: 0 in public" || { echo "$BG" | head -20; echo "SHIP REFUSED: a backup file is in the served folder or the public mirror"; exit 1; }   # 11 Nov: no backup-named file or folder is served or mirrored
python3 "$B/heuremen-specbook/site_gate.py" | tail -1   # restored 11 Nov: it had been commented out by the downloads edit
bash "$L/runcheck_gate.sh" || { echo "SHIP REFUSED: the Check a Run page and the qia-check package disagree"; exit 1; }   # 13 Nov: page/package parity, runs only when either changed
python3 "$B/qia_leads/matrix_page/source_gate.py" | tail -1
python3 "$B/qia_leads/matrix_page/render_list.py" --check   # 11 Nov: refuse if the /qia/list page and list.json disagree
python3 "$L/receipts.py" check | tail -1   # 10 Nov: every ledger row has its receipt page and every receipt link on a served page resolves   # 30 Oct: every QIA calibrated row cites a kept file holding its number, or no ship
python3 "$B/indahl-ai/findable.py" --gate | tail -1   # 10 Nov: every served page's JSON-LD parses and each Dataset has the fields Google requires
python3 "$B/indahl-ai/corrections.py" --gate | tail -1   # 10 Nov: every corrections row links to a real file or commit, and its copy keeps the public-copy rules
python3 "$B/indahl-ai/brands.py" --gate | tail -1   # 10 Nov: every brand-page number traces to a desk row or a ledger row
python3 "$B/indahl-ai/entities.py" --gate | tail -1   # 10 Nov evening: every entity page traces its rows to a served page or a brand-page row; with the Follow links, each page is unchanged without them
python3 "$B/indahl-ai/forecasters.py" --gate | tail -1   # 10 Nov: every /forecasters number traces to a desk feed or a ledger row, labels sit where the drawn intervals sit
python3 "$B/indahl-ai/email_gate.py" | tail -1   # 10 Nov: no email address in any built site file (newsletter subscribers live only in the private KV)
"$B/notify_state/venv/bin/python" "$B/indahl-ai/notify.py" --gate | tail -1   # 10 Nov: every feed, calendar and OPML file parses (feedparser, icalendar), every calendar event cites its source schedule   # 10 Nov: no email address in any built site file (newsletter subscribers live only in the private KV)
python3 "$B/indahl-ai/accountability.py" gate | tail -1   # 10 Nov: the accountability pages exist, keep the public-copy rules, /security/self matches its check file
python3 "$B/indahl-ai/alert_receipts.py" gate | tail -1   # 10 Nov: the alert receipt chain links, and no receipt holds subscriber data
python3 "$B/indahl-ai/reproduce_kits.py" gate | tail -25   # 10 Nov: every desk reproduce kit, rerun in a clean folder from its own contents, prints the headline the ledger covers and the live feed serves
echo "== 4 COMMIT"
# every file a live ledger row cites on the site is added even when new (23 Oct: shot_grid.text was cited, never committed, and the
# Zenodo build caught it); a cited file that does not exist refuses the ship.
python3 - "$B" <<'PY' || { echo "SHIP REFUSED: a ledger row cites a site file that does not exist"; exit 1; }
import json, os, subprocess, sys
B = sys.argv[1]; need = set()
for l in open(B + '/ledger/ledger.jsonl'):
    r = json.loads(l); f = r.get('source', {}).get('file', '')
    if r.get('status') == 'live' and f.startswith('heuremen.org/'): need.add(f[len('heuremen.org/'):])
gone = sorted(f for f in need if not os.path.exists(B + '/heuremen.org/' + f))
if gone: print('  missing:', gone); sys.exit(1)
subprocess.run(['git', '-C', B + '/heuremen.org', 'add', '--'] + sorted(need), check=True)
PY
for r in heuremen.org indahl-ai; do cd "$B/$r"; git add -u; git add -A -- '*.pdf' 2>/dev/null || true; [ "$r" = indahl-ai ] && git add -A -- oy 2>/dev/null || true
  if git diff --cached --quiet; then echo "  $r: nothing to commit"; else git "${AUTHOR[@]}" commit -q -m "$MSG" && echo "  $r: $(git log --oneline -1)"; fi; done
echo "== 5 DEPLOY"
cd "$B/heuremen.org"; WTOKEN=$(gh auth token -u claude-wayfinder 2>/dev/null); PR=0; PO=$(WTOKEN="$WTOKEN" git -c credential.helper= -c 'credential.helper=!f() { echo username=claude-wayfinder; echo "password=$WTOKEN"; }; f' push -q 2>&1) || PR=$?; echo "$PO" | sed -E 's#https://[^@]*@#https://#' | tail -2; if [ $PR -eq 0 ]; then echo "  heuremen.org pushed"; else echo "  heuremen.org PUSH FAILED (the Pages source repo refused it; live heuremen.org is NOT updated)"; fi
cd "$B/indahl-ai"; git push -q 2>&1 | sed -E 's#https://[^@]*@#https://#' | tail -2 || true
STAMP="$W/.last_deploy.sha"; NOW=$("$L/deploy_hash.sh")   # 10 Nov: one hash for ship.sh and push_public.sh (deploy_hash.sh), so the two lists never drift
if [ "$(cat "$STAMP" 2>/dev/null)" != "$NOW" ]; then (cd "$W" && npx wrangler deploy 2>&1 | grep -i -E "deployed|uploaded|error" | grep -v -i token | tail -3) && echo "$NOW" > "$STAMP" && { python3 "$L/stamps.py" manifest || true; }; else echo "  indahl.ai worker: unchanged"; fi   # 10 Nov: the manifest of what this deploy sent (stamps.py)
echo "== 5b PUBLIC REPOS"
# 31 Oct: the result is recorded for the watch (it was swallowed by "|| true" and a refusal went unseen for hours); a refusal is printed loud
set +e; PUBOUT=$(SHIP_DEPLOYED=1 "$L/push_public.sh" "$MSG" 2>&1); PUBRC=$?; set -e; echo "$PUBOUT"   # 10 Nov: SHIP_DEPLOYED=1 makes a skipped page mirror a hard failure (exit 3)
python3 - "$PUBRC" "$PUBOUT" > "$L/public_push_status.json" <<'PY'
import json, sys, time; rc = int(sys.argv[1]); out = sys.argv[2]; bad = rc != 0 or 'REFUSED' in out
print(json.dumps({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': not bad, 'site_pages': rc != 3 and 'site pages mirrored' in out, 'rc': rc, 'last': (out.strip().splitlines() or [''])[-1]}))
PY
python3 "$B/indahl-ai/accountability.py" buildinfo 2>&1 | tail -1 || true   # 10 Nov: the release record at /build.json (commits, deploy fingerprint, gate lines, pages hash), KV build_json
if [ $PUBRC -eq 3 ]; then echo "!! 5b FAIL: the site deployed but its pages were NOT mirrored to the public indahl.ai repo (code only). Alert written for Bones."; fi
set +e; python3 "$L/served_public_gate.py"; SPG=$?; set -e; if [ $SPG -ne 0 ]; then echo "!! 5b FAIL: files the site serves are missing from the public indahl.ai repo"; printf -- '- [public:served] since %s: served files missing from the public indahl.ai repo (ledger/served_public_gate.py)\n' "$(date '+%Y-%m-%d %H:%M')" >> "$B/alerts/ALERTS_OPEN.txt"; fi   # 14 Nov (Wayfinder caught it): everything the site serves is in the public repo, checked every release
if [ $PUBRC -ne 0 ] || echo "$PUBOUT" | grep -q REFUSED; then echo "!! PUBLIC REPOS REFUSED: the site shipped, the public code copies did not (see above; the watch shows this BAD until fixed)"; fi
echo "== 5c INDEXNOW"; python3 "$B/tools/indexnow.py" 2>&1 | tail -1 || true
# 7 STAMPS (10 Nov): outside timestamps after a verified release. release_<commit>.json (commit, ledger hash, manifest of every deployed file)
# stamped with OpenTimestamps, changed public URLs sent to the Internet Archive in the background, paced. Never fails a release.
stamps() { echo "== 7 STAMPS"; set +e; python3 "$L/stamps.py" release 2>&1 | tail -4; echo "== 7b WEBSUB"; python3 "$B/indahl-ai/websub_ping.py" ship 2>&1 | tail -1; echo "== 7c LEDGER BACKUP"; git -C "$L" push -q backup HEAD:main 2>&1 | tail -1 && { rm -f "$L/ledger_backup_status.json"; echo "  ledger pushed to the private backup"; } || { echo "  ledger backup push FAILED"; echo "{\"at\": \"$(date -u +%FT%TZ)\", \"ok\": false}" > "$L/ledger_backup_status.json"; }; echo "== 7d ARCHIVE BACKUP"; bash "$L/archive_push.sh" 2>&1 | tail -2; echo "== 7e ZENODO"; python3 "$L/zenodo_sync.py" --publish 2>&1 | tail -20 || echo "  zenodo sync crashed (status file written)"; [ -f "$L/zenodo_status.json" ] || true; set -e; return 0; }   # 11 Nov: 7d pushes archive_private to the private repo, 7e makes a new Zenodo version of each record whose site files changed (24 h guard per record), both after the deploy verified and every gate was 0, neither fails a ship; a failure writes archive_backup_status.json / zenodo_status.json for alerts_check.py   # 10 Nov: 7b tells the WebSub hub which feeds changed (never fails a release, failures alert Bones)
echo "== 6 VERIFY"
for i in 1 2 3 4 5 6; do python3 "$L/copies.py" live > /tmp/ship_live.txt 2>&1 && { tail -1 /tmp/ship_live.txt; stamps; exit 0; }; sleep 20; done
cat /tmp/ship_live.txt; echo "SHIP: live does not match yet -- read the LIVE OFF lines"; exit 1
