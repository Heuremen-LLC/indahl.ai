"""downloads.py inventory|refresh|gate -- every downloadable file on indahl.ai refreshes from its source on every ship, and a stale one stops the ship.
Heuremen LLC, 11 Nov 2026 (Wayfinder: the /qia/list.json download held two entries removed at an author's request, a hand copy last made 8 Nov).

  inventory  write ledger/DOWNLOADS.md: every downloadable file under the worker's public/ folder, its source, its producer, its date, in sync now
  refresh    run first in ship.sh (before build_site.py): (1) copies.py publish, so every plain copy is re-made from its source (copies.json),
             (2) rebuild the List packs when they differ from the published list.json, (3) rebuild the QIA Research Package when any
             file it was made from differs from that file now, (4) re-read the pack sizes the grab-and-go lists and the pack.size.* ledger rows cite
  gate       one line, "downloads gate: N files; stale: K". Exit 1 on any stale file. Checks:
             - every plain copy (a copies.json set whose copy sits in public/) equals its source
             - every zip opens and its .sha256 sidecar matches its bytes, a desk pack's results/<desk>_outcomes.csv equals the served <desk>_outcomes.csv
             - each List pack holds the published list.json, list.csv rows, references.bib entries
             - the QIA Research Package holds every file it was made from, as that file reads now
             - nothing listed in ledger/removed_at_request.json is in the served list.json files or the List packs
Desk packs and packages (11 Nov) have input maps and rebuild when an input changes. Held on purpose: run bundles under */runs/ and newsletter issues (frozen records)."""
import os, sys, re, json, glob, time, zipfile, hashlib, subprocess, csv, io, shutil, importlib.util

B = os.path.expanduser('~/bones-forge'); L = B + '/ledger'; PUB = B + '/cloudflare-workers/heuremen-door/public'
P = lambda p: p if p.startswith('/') else B + '/' + p
sha = lambda b: hashlib.sha256(b).hexdigest()
rd = lambda p: open(P(p), 'rb').read()
COPIES = json.load(open(L + '/copies.json'))

def copy_rows():
    """(public path, set name, source) for every copies.json set whose copy sits in the served folder and whose canonical sits outside it"""
    rows = []
    for k, v in COPIES.items():
        if k.startswith('_'): continue
        if os.path.normpath(P(v['canonical'])).startswith(PUB + '/'): continue   # canonical in public/ = a built pack, checked below
        for cp in v['copies']:
            q = os.path.normpath(P(cp))
            if q.startswith(PUB + '/'): rows.append((os.path.relpath(q, PUB), k, v['canonical']))
    return rows

REMOVED = json.load(open(L + '/removed_at_request.json')) if os.path.exists(L + '/removed_at_request.json') else {'ids': []}
LISTPACKS = {'qia': 'qia/list.json', 'iris': 'iris/list.json'}

def qia_pkg_map(zf):
    """inner path -> the file build_package.py copies it from (what it fetches from PyPI or writes itself is not listed)"""
    r = 'qia-research-package/'; M = {}
    for k in ('CITATION.cff', 'README.md', 'TESTED.md', 'qia_check.py'): M[k] = 'qia_package/src/' + k
    M.update({'LICENSE.txt': 'public_mirror/indahl.ai/LICENSE.txt', 'yo/yo_audit.py': 'yo/release/yo_audit.py',
              'papers/a-readout-is-not-an-idle.pdf': 'indahl-ai/quantum-idle-audit.pdf', 'faultsguards/faults.pdf': 'heuremen.org/faults.pdf',
              'faultsguards/guards.pdf': 'heuremen.org/guards.pdf'})
    for k in ('run_check.py', 'PLAN.md', 'README.md', 'requirements.txt'): M['t1t2-check/' + k] = 'public_mirror/indahl.ai/code/t1t2-check/' + k
    CB = 'iris_package/dist/iris-research-package/check-block/'
    for n in zf.namelist():
        if n.startswith(r + 'check-block/') and not n.endswith('/'): M[n[len(r):]] = CB + n[len(r + 'check-block/'):]
    return {r + k: v for k, v in M.items()}

def zips(): return sorted(glob.glob(PUB + '/*/*.zip') + glob.glob(PUB + '/*/*/*.zip'))

def check_pack_integrity(stale):
    n = 0
    for z in zips():
        rel = os.path.relpath(z, PUB); n += 1
        try: zf = zipfile.ZipFile(z); bad = zf.testzip()
        except Exception as e: stale.append(f'{rel}: not a zip ({e})'); continue
        if bad: stale.append(f'{rel}: corrupt member {bad}')
        sc = z + '.sha256'
        if os.path.exists(sc) and open(sc).read().split()[0] != sha(open(z, 'rb').read()): stale.append(f'{rel}: .sha256 sidecar does not match the zip')
        name = os.path.basename(z)
        if name.endswith('-data-pack.zip'):
            desk = name[:-len('-data-pack.zip')]; inner = [x for x in zf.namelist() if x.endswith(f'/{desk}_outcomes.csv')]; pc = f'{PUB}/{desk}/{desk}_outcomes.csv'
            if inner and os.path.exists(pc) and zf.read(inner[0]) != open(pc, 'rb').read(): stale.append(f'{rel}: results/{desk}_outcomes.csv differs from the served {desk}/{desk}_outcomes.csv')
    return n

def check_listpacks(stale):
    n = 0
    for div, lj in LISTPACKS.items():
        z = f'{PUB}/{div}/{div}-list-pack.zip'; slug = f'{div}-list-pack/'; zf = zipfile.ZipFile(z); n += 1
        cur = open(f'{PUB}/{lj}', 'rb').read(); studies = json.loads(cur)['studies']
        if zf.read(slug + 'list.json') != cur: stale.append(f'{div}/{div}-list-pack.zip: its list.json is not the published {lj}')
        rows = list(csv.DictReader(io.StringIO(zf.read(slug + 'list.csv').decode('utf-8'))))
        if len(rows) != len(studies): stale.append(f'{div}/{div}-list-pack.zip: list.csv has {len(rows)} rows, list.json has {len(studies)}')
        nb = len(re.findall(r'^@', zf.read(slug + 'references.bib').decode('utf-8'), re.M))
        if nb != len(studies): stale.append(f'{div}/{div}-list-pack.zip: references.bib has {nb} entries, list.json has {len(studies)}')
    return n

def check_qia_pkg(stale):
    zf = zipfile.ZipFile(f'{PUB}/qia/qia-research-package.zip'); M = qia_pkg_map(zf)
    for inner, src in sorted(M.items()):
        if not os.path.exists(P(src)): stale.append(f'qia/qia-research-package.zip: source {src} is missing'); continue
        if zf.read(inner) != rd(src): stale.append(f'qia/qia-research-package.zip: {inner[len("qia-research-package/"):]} differs from {src}')
    return 1

def check_removed(stale):
    ids = [i.lower() for i in REMOVED.get('ids', [])]; n = 0
    if not ids: return 0
    for d in ('qia', 'iris'):
        n += 1; t = open(f'{PUB}/{d}/list.json', encoding='utf-8').read().lower()
        for i in ids:
            if i in t or i.replace('arxiv-', '') in t: stale.append(f'{d}/list.json: holds removed-at-request {i}')
        zf = zipfile.ZipFile(f'{PUB}/{d}/{d}-list-pack.zip'); n += 1
        for m in zf.namelist():
            if m.endswith(('list.json', 'list.csv', 'references.bib', 'references.ris')):
                t = zf.read(m).decode('utf-8', 'replace').lower()
                for i in ids:
                    if i in t or i.replace('arxiv-', '') in t: stale.append(f'{d}/{d}-list-pack.zip:{m}: holds removed-at-request {i}')
    return n

# ---------------------------------------------------------------------------------------------------------------------------------------
# 11 Nov (Wayfinder: "can the data packs also get an autonomous update every time that desk or page is updated ... we're not a static site")
# Every desk pack and package has an INPUT MAP below. refresh compares a hash of the inputs with the hash recorded when the pack was last made
# (ledger/pack_inputs.json). When they differ the pack is rebuilt into a scratch folder and its contents are compared with the placed zip.
# Same contents: nothing is placed (an unchanged desk never makes a new pack). Different contents: the zip is placed, stamped with the build date
# (fixed entry dates, sorted entries, so the bytes depend on the contents and the date only), its sidecar rewritten, the size row in the ledger
# edited FIRST (ledger/ledger.py set, with a generated CHECKS entry), and only then does build_site.py read the sizes.
# The gate compares every pack with its inputs. Feeds that live in the site KV (no file in public/) are read from the live site once, in refresh,
# and the gate checks that reading, so a tick between refresh and gate never refuses a ship.
IN_STATE = L + '/pack_inputs.json'
VOLATILE = ('TESTED.md', 'SHA256SUMS.txt')   # carry the build time and the hashes of the other files
def _state(): return json.load(open(IN_STATE)) if os.path.exists(IN_STATE) else {}
def _walk(p):
    p = P(p)
    if os.path.isfile(p): return [p]
    out = []
    for r, ds, fs in os.walk(p):
        ds[:] = sorted(d for d in ds if d not in ('__pycache__', 'dist', '.git') and not re.search(r'[._]bak-|\.pre-', d))
        out += [os.path.join(r, f) for f in sorted(fs) if not re.search(r'\.(pyc|bak)|\.bak-|\.pre-|\.DS_Store', f)]
    return out
def digest(paths, extra=b''):
    h = hashlib.sha256(extra)
    for p in paths:
        for f in _walk(p):
            h.update(os.path.relpath(f, B).encode() + b'\0'); h.update(open(f, 'rb').read())
    return h.hexdigest()

def desk_mod():
    os.environ['DESK_PACK_LOCAL'] = '1'
    sp = importlib.util.spec_from_file_location('desk_pack', B + '/tools/desk_pack.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def desk_units(DP):
    """desk pack zip (relative to public/) -> (slug, input paths in the served folder or the working folders)"""
    u = {}
    for slug, C in DP.DESKS.items():
        ins = [P('tools/desk_pack.py')]
        if C.get('rows'): ins.append(P(C['rows']['file']))
        if C.get('special') == 'social': ins += sorted(glob.glob(B + '/social_index/*summary*.json'))
        u[f'{slug}/{slug}-data-pack.zip'] = (slug, ins)
    return u

def desk_feeds(DP, slug):
    """(bytes of every feed the pack is made from, is any of them read from the live site)"""
    urls = [f'{DP.SITE}/social/summary.json', f'{DP.SITE}/social/dsa.json'] if slug == 'social' else [f'{DP.SITE}/{slug}/live.json']
    out = b''; net = False
    for u in urls:
        lp = PUB + u[len(DP.SITE):]
        if os.path.isfile(lp): out += open(lp, 'rb').read()
        else: out += DP.get(u, raw=True); net = True
    return out, net

PACKAGES = {   # zip under public/ -> builder folder, name inside the zip, inputs (files or folders under ~/bones-forge, hashed by content), when it can be rebuilt
 'atlas/atlas-data-pack.zip': dict(dir='atlas_package', stem='atlas-data-pack', stage='pre',
     inputs=['atlas_package/build_package.py', 'atlas_package/src', 'atlas_package/tools', 'atlas_package/snap', 'tools/desk_pack.py'] + [f'cloudflare-workers/heuremen-door/public/atlas/{f}.json' for f in ('datacenters', 'electricity', 'utilities', 'plants', 'planned', 'carbon', 'scale')]),
 'oy/oy-data-pack.zip': dict(dir='oy_package', stem='oy-data-pack', stage='post',   # reads the built OY pages, so it runs after build_site.py
     inputs=['oy_package/build_package.py', 'oy_package/src', 'oy_package/tools', 'indahl-ai/oy.html', 'indahl-ai/oy/school', 'oy_index/schools.json']),
 'hermes/model-data-pack.zip': dict(dir='model_package', stem='model-data-pack', stage='pre',
     inputs=['model_package/build_package.py', 'model_package/src'] + [f'cloudflare-workers/heuremen-door/public/hermes/model/{f}' for f in ('claims.json', 'accelerators_summary.json', 'storage_v30_results.json', 'mac_run.jsonl', 'accelerators.csv')]),
 'darkwave/darkwave-correction-kit.zip': dict(dir='darkwave_kit', stem='darkwave-correction-kit', stage='pre',
     inputs=['darkwave_kit/build_package.py', 'darkwave_kit/src', 'public_mirror/indahl.ai/LICENSE.txt', 'public_mirror/indahl.ai/code/readout-correction/run/data/fresh_kicks_ibm_kingston.json',
             'public_mirror/indahl.ai/code/readout-correction/run/data/fresh_kicks_ibm_marrakesh.json', 'heuremen.org/experiments/2026-11-02-darkwave-kit-check', 'heuremen.org/experiments/2026-11-02-darkwave-kit-check-2', 'qia_package/src/qia_check.py']),
 'iris/iris-research-package.zip': dict(dir='iris_package', stem='iris-research-package', stage='pre',   # also reads the newest faultsguards release from PyPI, which is not an input we can hash
     inputs=['iris_package/build_package.py', 'iris_package/src', 'public_mirror/indahl.ai/code/checks', 'public_mirror/indahl.ai/code/iris/faultsbench', 'heuremen.org/faults.pdf', 'heuremen.org/guards.pdf']),
}
# held as they are, on purpose (listed in DOWNLOADS.md and the report): run bundles (zips under */runs/, a finished run is a fixed record), newsletter issues (a sent issue is dated)
FROZEN = [('*/runs/*.zip', 'frozen record of a finished run, integrity-checked'), ('newsletter/*', 'a sent issue is dated and stays as sent')]

def zip_inner(path):
    zf = zipfile.ZipFile(path); return {n.split('/', 1)[1]: zf.read(n) for n in zf.namelist() if '/' in n and not n.endswith('/')}

def repack(src_zip, dst):
    """same files, sorted, entry dates = today, so the bytes depend on the contents and the build date only"""
    inner = zipfile.ZipFile(src_zip); dt = time.localtime()[:3] + (0, 0, 0); tmp = dst + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
        for n in sorted(x for x in inner.namelist() if not x.endswith('/')):
            zi = zipfile.ZipInfo(n, dt); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16; zf.writestr(zi, inner.read(n))
    os.replace(tmp, dst); open(dst + '.sha256', 'w').write(f'{sha(open(dst, "rb").read())}  {os.path.basename(dst)}\n')

def pack_units(DP=None):
    """every unit: key (zip under public/), kind, stage, current input hash, net (read from the live site), builder info"""
    DP = DP or desk_mod(); U = []
    for z, (slug, ins) in desk_units(DP).items():
        try: fb, net = desk_feeds(DP, slug); h = digest(ins, fb)
        except Exception as e: U.append(dict(key=z, kind='desk', slug=slug, stage='pre', hash=None, net=True, err=repr(e))); continue
        U.append(dict(key=z, kind='desk', slug=slug, stage='pre', hash=h, net=net))
    for z, c in PACKAGES.items():
        if c.get('held'): continue
        U.append(dict(key=z, kind='pkg', stage=c['stage'], hash=digest(c['inputs']), net=False, cfg=c))
    return U

def check_pack_inputs(stale):
    """gate: every pack equals what its inputs now say. Units fed from the live site are checked against the reading refresh took"""
    st = _state(); n = 0; DP = desk_mod()
    for z, (slug, ins) in desk_units(DP).items():
        n += 1; r = st.get(z)
        if not r: stale.append(f'{z}: no input record, run downloads.py refresh'); continue
        if r.get('net'):
            if r['observed'] != r['recorded']: stale.append(f'{z}: its feed moved past the pack, rebuild failed')
        else:
            cur = digest(ins, desk_feeds(DP, slug)[0])
            if cur != r['recorded']: stale.append(f'{z}: a local input differs from what the pack was built from')
    for z, c in PACKAGES.items():
        if c.get('held'): print(f'  HELD {z}: {c["held"]}'); continue
        n += 1; r = st.get(z)
        if not r: stale.append(f'{z}: no input record, run downloads.py refresh'); continue
        if digest(c['inputs']) != r['recorded']: stale.append(f'{z}: an input differs from what the pack was built from')
    return n

def run_builder(u):
    """build into a scratch place and return the built zip path, or None"""
    if u['kind'] == 'desk':
        DP = desk_mod()
        try: d = DP.build_one(u['slug'], place=False)
        except SystemExit as e: print(f'  downloads: {u["key"]} build refused: {str(e)[:120]}'); return None
        except Exception as e: print(f'  downloads: {u["key"]} build failed: {e!r}'); return None
        return d['zip']
    # the builders wipe their own dist/ first, so one that fails would leave the real dist (which build_site.py reads) half made: run a copy of the folder
    c = u['cfg']; import tempfile; tmp = tempfile.mkdtemp(prefix='pkgbuild_'); wd = f'{tmp}/{c["dir"]}'
    shutil.copytree(f'{B}/{c["dir"]}', wd, ignore=shutil.ignore_patterns('dist*', '*bak*', '*.pre-*', '__pycache__', 'public_bak*'))
    r = subprocess.run(['python3', f'{wd}/build_package.py'], capture_output=True, text=True, cwd=wd)
    if r.returncode: print(f'  downloads: {u["key"]} build failed: {(r.stderr or r.stdout).strip().splitlines()[-1:]}'); shutil.rmtree(tmp, ignore_errors=True); return None
    u['scratch'] = wd; return f'{wd}/dist/{c["stem"]}.zip'

def update_ledger_size(z, old, new):
    """ledger edit before surface edit: the pack.size.* row follows the pack. A generated CHECKS entry per change, then ledger.py set / off / on."""
    sz = json.load(open(B + '/tools/desk_packs/pack_sizes.json')); stem = os.path.basename(z)[:-4]; cid = 'pack.size.' + stem
    rows = {}
    for l in open(L + '/ledger.jsonl'):
        if l.strip(): r = json.loads(l); rows[r['id']] = r
    r = rows.get(cid)
    if not r or z not in sz: return False
    row = sz[z]; ov = r['value']; nv = row['size']
    if ov == nv: return False
    now = time.strftime('%Y-%m-%d %H:%M'); ck = B + '/tools/desk_packs/CHECKS.md'
    ent = (f'\n## {now} {row["title"]} rebuilt by ledger/downloads.py: zip size {ov} -> {nv}\npacks: P\n(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)\n'
           f'- I: holds: the pack was rebuilt because a hash of its inputs differed from the hash recorded when it was last made (ledger/pack_inputs.json), and its contents differ from the zip it replaces, so the none is the pack against its own inputs\n'
           f'- II: n/a: no comparison between two runs, one file size read before and after\n- III: n/a: no signed difference is reported, a size is a level of one file\n'
           f'- V: holds: two counts side by side, the zip was opened again and its sha256 sidecar read back ({row["sha256"][:16]}), size {row["bytes"]} bytes\n- VI: n/a: no interval outcome is claimed\n'
           f'- R: holds: size read from the file in public/ by tools/desk_pack.py sizes into tools/desk_packs/pack_sizes.json on {now}, the page prints that file\n'
           f'- P1: n/a: no quoted text is added to any page\n- P2: holds: the size names its zip, linked beside it\n- P3: holds: pack name as built, file name as served\n'
           f'- P4: holds: no cause named, a size and a link only\n- P5: n/a: no intervals on this line\n- P6: holds: the line says what the zip holds, nothing stronger\n'
           f'- P7: holds: the pack.size row is edited before the surface, release through ledger/ship.sh under site_lock\n- P8: holds: rendered pages are read after build, check_ledger drift 0 is required before the ship completes\n'
           f'- P9: holds: plain sentences, no semicolons, no AI statements, Heuremen LLC\n- P10: n/a: no rule set after the data\n')
    open(ck, 'a').write(ent)
    run = lambda *a: subprocess.run(['python3', L + '/ledger.py', *a], check=True, stdout=subprocess.DEVNULL)
    why = f'zip rebuilt {time.strftime("%-d %b %Y")} by downloads.py refresh because an input changed'
    run('set', cid, '--field', 'value', '--to', nv, '--why', why, '--evidence', 'tools/desk_packs/pack_sizes.json', '--checks', 'tools/desk_packs/CHECKS.md')
    run('set', cid, '--field', 'source.grep', '--to', row['line'], '--why', why, '--evidence', 'tools/desk_packs/pack_sizes.json')
    for sf in r['surfaces']:
        t = sf['text']; nt = t[:-len(ov)] + nv if t.endswith(ov) else t.replace(ov, nv)
        run('off', cid, sf['surface'], '--why', why); run('on', cid, sf['surface'], nt)
    print(f'  downloads: ledger {cid}: {ov} -> {nv}'); return True

def sync_ledger_sizes():
    sz = json.load(open(B + '/tools/desk_packs/pack_sizes.json')); n = 0
    for z in sorted(sz): n += bool(update_ledger_size(z, None, None))
    return n

def refresh_packs(stage):
    """returns the number of packs placed"""
    DP = desk_mod(); st = _state(); placed = []; today = time.strftime('%Y-%m-%d')
    for u in pack_units(DP):
        if u['stage'] != stage: continue
        z = u['key']; rec = st.get(z, {})
        if u['hash'] is None: print(f'  downloads: {z}: feed unreadable now ({u["err"][:60]}), kept as is'); st[z] = {**rec, 'observed': rec.get('recorded'), 'net': True, 'recorded': rec.get('recorded')}; continue
        if rec.get('recorded') == u['hash'] and os.path.exists(f'{PUB}/{z}'):
            st[z] = {**rec, 'observed': u['hash'], 'net': u['net']}; continue
        bz = run_builder(u)
        if not bz: st[z] = {**rec, 'observed': u['hash'], 'net': u['net']}; continue   # build refused: the gate reads recorded != observed on net units
        old = zip_inner(f'{PUB}/{z}') if os.path.exists(f'{PUB}/{z}') else None
        new = zip_inner(bz); same = old is not None and {k: v for k, v in old.items() if k not in VOLATILE} == {k: v for k, v in new.items() if k not in VOLATILE}
        if same: print(f'  downloads: {z}: inputs moved, contents unchanged, pack kept')
        else:
            oldsize = os.path.getsize(f'{PUB}/{z}') if old is not None else None
            if u['kind'] == 'desk':
                shutil.copy2(bz, f'{PUB}/{z}'); shutil.copy2(bz + '.sha256', f'{PUB}/{z}.sha256')
                D = os.path.join(DP.OUT, u['slug'] + '-data-pack'); d = f'{PUB}/{u["slug"]}'
                if os.path.exists(f'{d}/{u["slug"]}_outcomes.csv') and os.path.exists(f'{D}/results/{u["slug"]}_outcomes.csv'): shutil.copy2(f'{D}/results/{u["slug"]}_outcomes.csv', f'{d}/{u["slug"]}_outcomes.csv')
                if os.path.exists(f'{d}/{u["slug"]}-data-pack-LICENSE.txt'): shutil.copy2(f'{D}/LICENSE.txt', f'{d}/{u["slug"]}-data-pack-LICENSE.txt')
            else:
                repack(bz, f'{PUB}/{z}'); rd_ = f'{B}/{u["cfg"]["dir"]}/dist'; shutil.rmtree(rd_, ignore_errors=True); shutil.copytree(u['scratch'] + '/dist', rd_)   # the real dist follows the placed pack
            placed.append((z, oldsize)); print(f'  downloads: {z}: rebuilt {today} (an input changed)')
        st[z] = dict(recorded=u['hash'], observed=u['hash'], net=u['net'], built=today if not same else rec.get('built', today), pack_sha=sha(open(f'{PUB}/{z}', 'rb').read()))
    json.dump(st, open(IN_STATE, 'w'), indent=1, sort_keys=True)
    if placed:
        run = lambda *a: subprocess.run(list(a), check=True, stdout=subprocess.DEVNULL)
        run('python3', B + '/tools/desk_pack.py', 'sizes')
        sz = json.load(open(B + '/tools/desk_packs/pack_sizes.json'))
    sync_ledger_sizes()
    return len(placed)

def gate():
    stale = []; n = 0
    for rel, k, src in copy_rows():
        n += 1
        if not os.path.exists(P(src)): stale.append(f'{rel}: source {src} is missing'); continue
        if not os.path.exists(f'{PUB}/{rel}') or rd(src) != open(f'{PUB}/{rel}', 'rb').read(): stale.append(f'{rel}: differs from its source {src}')
    n += check_pack_integrity(stale); n += check_pack_inputs(stale); n += check_listpacks(stale); n += check_qia_pkg(stale); n += check_removed(stale)
    for s in stale: print('  STALE', s)
    print(f'downloads gate: {n} files; stale: {len(stale)}'); return len(stale)

def place(dist_zip, pub_rel):
    dst = f'{PUB}/{pub_rel}'; shutil.copy2(dist_zip, dst)
    open(dst + '.sha256', 'w').write(f'{sha(open(dst, "rb").read())}  {os.path.basename(dst)}\n')

def refresh(post=False):
    if post:   # 11 Nov: after build_site.py, the packs made from built pages (OY). Exit 10 = one was rebuilt, ship.sh builds the site once more so its sizes and rows agree
        return 10 if refresh_packs('post') else 0
    run = lambda *a: subprocess.run(list(a), check=True, stdout=subprocess.DEVNULL)
    run('python3', L + '/copies.py', 'publish'); print('  downloads: plain copies re-made from their sources')
    changed = False; st = []; check_listpacks(st)
    need = sorted({s.split('/')[0] for s in st})
    if need:
        run('python3', B + '/list_packs/build_packs.py')
        for div in need: place(f'{B}/list_packs/dist/{div}-list-pack.zip', f'{div}/{div}-list-pack.zip'); print(f'  downloads: {div} List pack rebuilt from the published list.json')
        changed = True
    st = []; check_qia_pkg(st)
    if st:
        r = subprocess.run(['python3', B + '/qia_package/build_package.py'], capture_output=True, text=True)
        if r.returncode: print('  downloads: QIA Research Package rebuild FAILED:', (r.stderr or r.stdout).strip().splitlines()[-1:])
        else: place(B + '/qia_package/dist/qia-research-package.zip', 'qia/qia-research-package.zip'); print('  downloads: QIA Research Package rebuilt'); changed = True
    if changed: run('python3', L + '/copies.py', 'publish'); run('python3', B + '/tools/desk_pack.py', 'sizes'); print('  downloads: pack sizes re-read')
    refresh_packs('pre'); run('python3', L + '/copies.py', 'publish'); run('python3', B + '/tools/desk_pack.py', 'sizes'); sync_ledger_sizes()
    return 0

DATED = 'rebuilt by downloads.py refresh whenever a hash of its inputs differs from the recorded one (ledger/pack_inputs.json), gate: every pack equals its inputs'
def classify(rel):
    n = os.path.basename(rel); cp = {r: (k, s) for r, k, s in copy_rows()}
    if rel in cp: return ('a', cp[rel][1], f'copies.json set {cp[rel][0]}, re-made every ship', 'gate: equals source')
    if re.search(r'\.(bak|pre)-', n): return ('d', '-', 'stray backup file in the served folder', 'orphan, left for a decision')
    if n.endswith('.zip.sha256'): return ('b', 'its zip', 'written with the zip by the pack builder', 'gate: matches its zip')
    if n.endswith('-LICENSE.txt'): return ('b', 'tools/desk_pack.py', 'tools/desk_pack.py build, with its pack', DATED)
    if n.endswith('_outcomes.csv'): return ('b', 'tools/desk_pack.py', 'tools/desk_pack.py build, with its pack', 'gate: equals the copy inside the pack')
    if n.endswith('-list-pack.zip'): return ('b', f'{n[:n.index("-")]}/list.json via list_packs/build_packs.py', 'ledger/downloads.py refresh', 'gate: inner list.json, csv rows, bib entries equal the published List')
    if n == 'qia-research-package.zip': return ('b', 'qia_package/src, public_mirror, heuremen.org PDFs, iris check-block', 'qia_package/build_package.py via ledger/downloads.py refresh', 'gate: every input file equals its copy inside the zip')
    if n.endswith('.zip') and '/runs/' in rel: return ('b', 'run folders', 'qia_leads/matrix_page/bundle_runs.py, iris_index/matrix_page/bundle_iris.py', 'frozen record of a finished run, integrity-checked')
    if n.endswith('.zip') and rel in PACKAGES: return ('b', 'inputs listed in downloads.py PACKAGES', PACKAGES[rel]['dir'] + '/build_package.py via downloads.py refresh', DATED)
    if n.endswith('.zip'): return ('b', 'tools/desk_pack.py, the desk feed and rows file', 'tools/desk_pack.py via downloads.py refresh', DATED)
    if rel.startswith('receipts/stamps/'): return ('c', 'ledger/stamps.py', 'stamps.py release', 'rewritten by the ship')
    if rel.startswith('brand/'): return ('c', 'indahl-ai/brands.py', 'brands.py via build_site.py every ship', 'brands.py --gate')
    if n in ('changes.xml', 'calendar.ics', 'feeds.opml', 'changelog.xml', 'feed.xml') or rel.startswith('newsletter/'): return ('c', 'ledger/changes_feed.py, indahl-ai/notify.py', 'build_site.py every ship', 'notify.py --gate parses it')
    if n in ('corrections.csv', 'corrections.xml'): return ('c', 'indahl-ai/corrections.py', 'build_site.py every ship', 'corrections.py --gate')
    if rel == 'r/sitemap.txt': return ('c', 'ledger/receipts.py', 'receipts.py build every ship', 'receipts.py check')
    if rel in ('sw.js', 'qia/probe.py', 'e/index.json', 'og/cards.json', 'darkwave/clock.json', 'e/search.js') or rel.startswith(('oy/', 'vault/', 'hermes/model/')) or rel == 'TERMS_DATA.txt' or rel == 'receipts/stamps/index.json':
        return ('d', '-', 'authored or placed by hand, no builder in the ship', 'orphan, left for a decision')
    if n in ('offchain.json', 'manifest.webmanifest') or n.endswith('.js'): return ('c', 'indahl-ai/build_site.py and the desk scripts', 'build_site.py every ship', 'rewritten by the ship')
    if rel.startswith('predictions/'): return ('c', 'now_index/freeze.py, build_page.py', 'now_index tick', 'feed written by its tick')
    if rel.startswith('atlas/') and n.endswith('.json'): return ('c', 'atlas/build_atlasmap.py', 'ATLAS builders', 'feed written by its builder')
    if rel.startswith('qia/') or rel.startswith('iris/'): return ('d', '-', 'no builder found', 'orphan, left for a decision')
    return ('d', '-', 'no builder found', 'orphan, left for a decision')

def inventory():
    import contextlib
    skip = re.compile(r'\.(html|png|jpg|svg|ico|woff2)$')
    files = sorted(os.path.relpath(os.path.join(r, f), PUB) for r, _, fs in os.walk(PUB) for f in fs if not skip.search(f))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): gate()
    gate_stale = {m.group(1) for m in (re.match(r'  STALE (\S+?):', l) for l in buf.getvalue().splitlines()) if m}
    cnt = {}; rows = []
    for rel in files:
        c, src, prod, chk = classify(rel); cnt[c] = cnt.get(c, 0) + 1
        mt = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(f'{PUB}/{rel}')))
        sync = 'NO' if rel in gate_stale else ('yes' if c == 'a' else 'yes (gated)' if c == 'b' and chk.startswith('gate') else 'n/a')
        rows.append((rel, c, src, prod, mt, sync, chk))
    names = {'a': 'plain copy of a source file', 'b': 'built by a script', 'c': 'generated by build_site.py, a stamp or a feed tick', 'd': 'orphan, hand placed or no builder found'}
    out = ['# Downloads on indahl.ai', '', f'Written by ledger/downloads.py inventory on {time.strftime("%Y-%m-%d %H:%M")}. Folder: cloudflare-workers/heuremen-door/public (pages, images and fonts left out).', '', '## Counts', '']
    out += [f'- {k}, {names[k]}: {cnt.get(k, 0)}' for k in 'abcd'] + [f'- total: {len(files)}', '', '## How a download stays fresh', '',
            '- a: listed in ledger/copies.json. ship.sh step 1 runs downloads.py refresh, which runs copies.py publish first, so the file is re-made from its source on every ship.',
            '- b: built by the named script. downloads.py refresh rebuilds the List packs and the QIA Research Package when a file inside no longer equals its source. Desk packs are dated snapshots and run bundles are frozen, both integrity-checked.',
            '- c: written by build_site.py, receipts.py, stamps.py or a desk tick and checked by the gate in the last column.',
            '- d: no builder or no second copy. Listed for a decision, nothing deleted.',
            '- The gate (downloads.py gate, step 3 of ship.sh) stops the ship when a copy differs from its source, a zip or its .sha256 is broken, a List pack disagrees with the published List, the QIA Research Package holds an older file than its source, or a removed-at-request entry is in the lists.', '',
            '## Table', '', '| path | cat | source | producer | last modified | in sync now | check |', '|---|---|---|---|---|---|---|']
    out += [f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |' for r in rows]
    open(L + '/DOWNLOADS.md', 'w').write('\n'.join(out) + '\n'); print('DOWNLOADS.md:', len(files), 'files', cnt)

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'gate'
    if a == 'gate': sys.exit(1 if gate() else 0)
    if a == 'refresh': sys.exit(refresh('--post' in sys.argv))
    if a == 'inventory': inventory()
