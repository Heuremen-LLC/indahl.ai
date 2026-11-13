#!/usr/bin/env python3
"""revise_tick.py: REVISE rider per PLAN.md. First, third and most recent releases of monthly nonfarm payroll change against the BLS's stated 90% interval of 122 thousand.
From 9 Nov 2026 (PLAN.md Addendum 1) every value is read from the BLS itself (bls_source.py), not from the Philadelphia Fed file. Publishes KV revise_live."""
import os, sys, re, json, time, hashlib, subprocess, statistics as S, urllib.request
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/files', exist_ok=True)
VPY = os.path.join(H, 'venv', 'bin', 'python')
if os.path.realpath(sys.executable) != os.path.realpath(VPY) and not os.environ.get('REVISE_VENV'):
    os.execv(VPY, [VPY, os.path.abspath(__file__)] + sys.argv[1:])
import openpyxl, heuremen_kit as K
import openpyxl.reader.excel as _rx
_rp = _rx.ExcelReader.read_properties
def _safe_rp(self):
    try: _rp(self)
    except TypeError: pass   # 2 Nov: Philadelphia Fed file has a malformed created/modified stamp; the data sheets are unaffected
_rx.ExcelReader.read_properties = _safe_rp
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('revise: plan not committed'); sys.exit(0)
UA = {'User-Agent': 'heuremen-revise/0.1 (+https://indahl.ai/revise)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); STATED = 122.0
import bls_source as BS
URL = BS.TABLE
def count(pairs, limit=STATED): return sum(1 for a, b in pairs if abs(b - a) > limit)
gate = count([(0, 122), (0, 123), (0, -123)]) == 2 and [abs(b - a) > STATED for a, b in [(0, 122), (0, 123), (0, -123)]] == [False, True, True]
raw = BS.table_raw(); sha = hashlib.sha256(raw).hexdigest()
fn = 'data/files/cesnaicsrev_%s.htm' % sha[:12]
if not os.path.exists(fn): open(fn, 'wb').write(raw)
flat = BS.flat_raw(); flat_sha = hashlib.sha256(flat).hexdigest()   # 10 Nov 2026: the BLS flat file is kept too, each version by its sha256, so the most recent values can be replayed
ffn = 'data/files/ce_totalnonfarm_%s.txt' % flat_sha[:12]
if not os.path.exists(ffn): open(ffn, 'wb').write(flat)
tab = BS.first_second_third(raw); bc = BS.most_recent(flat)
upd = re.search(r'Last Modified Date:\s*(?:</strong>)?\s*([A-Za-z]+ \d+, \d{4})', raw.decode('utf-8', 'replace')); updated_file = upd.group(1) if upd else ''
rows = [dict(m=m, first=tab[m]['first'], second=tab[m]['second'], third=tab[m]['third'], recent=bc.get(m)) for m in sorted(tab)]
ys = int(updated_file[-4:]) if updated_file else int(time.strftime('%Y')); last_bench = '%04d:03' % (ys - 1)
bench = [r for r in rows if r['recent'] is not None and r['m'] <= last_bench]
# known-good (Addendum 1): the first estimates of the four months opened by hand against the archived releases (Note 1) must read the same here,
# the table must hold every month from 1979, and the flat file must give the current change for every month of the last ten years.
KG = {'2020:03': -701.0, '2021:08': 235.0, '2021:11': 210.0, '2021:12': 199.0}
chk = [abs((tab.get(m) or {}).get('first', 1e9) - v) for m, v in KG.items()]
need = ['%04d:%02d' % (y, mo) for y in range(ys - 10, ys) for mo in range(1, 13)]
gate &= max(chk) <= 0.5 and len(tab) >= 500 and all(m in bc for m in need)
print('revise: gate', 'passed' if gate else 'FAILED', 'first estimates of', len(KG), 'hand-checked months, max difference', round(max(chk), 2), '|', len(tab), 'months in the table', flush=True)
if not gate: sys.exit(0)
t3 = [r for r in rows if r['first'] is not None and r['third'] is not None][-120:]; mr = [r for r in bench if r['first'] is not None][-120:]
import random as _rnd
def yblock(rs, key, reps=4000):
    by = {}
    for r in rs: by.setdefault(r['m'][:4], []).append(abs(r[key] - r['first']) > STATED)
    ys = sorted(by); rg = _rnd.Random(7); bs = []
    for _ in range(reps):
        sm = [x for y in (rg.choice(ys) for _ in ys) for x in by[y]]; bs.append(sum(sm) / len(sm))
    bs.sort(); return len(ys), round(bs[int(0.025 * reps)], 4), round(bs[int(0.975 * reps)], 4)
def block(rs, key):
    prs = [(r['first'], r[key]) for r in rs]; n = len(prs); k = count(prs); lo, hi = K.wilson(k, n); rev = [b - a for a, b in prs]
    # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): 0.10 is a point figure with no tolerance, read as a bound. CONSISTENT is not available, the 0.12 width cap is not a tolerance.
    oc, why = K.read(lo if n else None, hi if n else None, bound=0.10)
    yb, ylo, yhi = yblock(rs, key)
    # 30 Oct (site pass I-10): the same outcome rule applied to the interval over years, shown beside the fixed outcome so the two can be read together. Descriptive, defined after the first read.
    ocy, whyy = K.read(ylo if yb >= 2 else None, yhi if yb >= 2 else None, bound=0.10)
    r13 = K.req13([(oc, why), (ocy, whyy)], nothing_returned=0)   # the two readings printed for this count. Failed reads stop the pass before this point, so none is counted here.
    return dict(outcome_y=ocy, reason_y=whyy, req13=r13, years=yb, share_y=round(k / n, 4), share_y_lo=ylo, share_y_hi=yhi, months=n, first=rs[0]['m'], last=rs[-1]['m'], exceed=k, share=round(k / n, 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, reason=why, rule='bound 0.10, no tolerance, closed edge (PLAN_ADDENDUM_std2.md)', interval='Wilson 95 percent over months', interval_y='percentile bootstrap over calendar years, 4000 resamples, seed 7, 95 percent', median_signed=round(S.median(rev), 1), mean_signed=round(S.mean(rev), 1), median_abs=round(S.median([abs(x) for x in rev]), 1), largest=round(max(rev, key=abs), 1))
a = block(t3, 'third'); b = block(mr, 'recent')
REQ13 = K.req13([(a['outcome'], a['reason']), (a['outcome_y'], a['reason_y']), (b['outcome'], b['reason']), (b['outcome_y'], b['reason_y'])], nothing_returned=0)
HC = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
big = [dict(url=URL, month=r['m'], first=r['first'], third=r['third'], most_recent=r['recent'], note=HC.get(r['m'], 'Not yet read in full')) for r in {x['m']: x for x in t3 + mr}.values() if max(abs((r['third'] or r['first']) - r['first']), abs((r['recent'] or r['first']) - r['first']) if r['m'] <= last_bench else 0) > 300]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed', stated=int(STATED), file_updated=updated_file, sha=sha[:16], flat_sha=flat_sha[:16], checked_months=len(KG),
           counts={'Third release against first': a, 'Most recent, after the annual benchmark, against first': b}, req13=REQ13, standard='Faults and Guards 2.0.0', large=sorted(big, key=lambda x: x['month']))
json.dump(out, open('summary_revise.json', 'w'), indent=1)
with open('data/history.jsonl', 'a') as f: f.write(json.dumps(dict(t=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), sha=sha[:16], flat_sha=flat_sha[:16], third=a, recent=b), sort_keys=True) + '\n')
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'revise_live', '--path', os.path.join(H, 'summary_revise.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('revise:', a['outcome'], a['exceed'], 'of', a['months'], '|', b['outcome'], b['exceed'], 'of', b['months'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
