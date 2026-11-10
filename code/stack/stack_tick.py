#!/usr/bin/env python3
"""stack_tick.py: STACK rider per PLAN.md. Reads the public feeds of the other pages and lines their headline tests up in one table. Adds no reading of its own."""
import os, sys, json, time, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('stack: plan not committed'); sys.exit(0)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def feed(slug):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/%s/live.json?x=%d' % (slug, time.time()), headers={'User-Agent': 'heuremen-stack/0.1'}), timeout=40).read())
    except Exception: return None
def at(d, path):
    for k in path:
        if isinstance(d, dict) and k in d: d = d[k]
        else: return None
    return d
def trials_outcome(lo, hi): return 'ABOVE' if lo > 0.25 else ('CONSISTENT' if hi < 0.10 else 'CANNOT_TELL')
# (page, slug, test, path, of key, failing key, share key, lo key, hi key, outcome key or None)
SPEC = [('SUPPORT', 'support', 'Supported cycles that had stopped releasing', ['all'], 'tested', 'unreleased', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SUPPORT', 'support', 'Products with at least one such cycle', ['product_level', 'Products with at least one unreleased supported cycle'], 'tested', 'unreleased', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('PKGLICENSE', 'pkglicense', 'Stated license against the repository license', ['disagree'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFLICENSE', 'hflicense', 'Models: stated license against the license file', ['comparison', 'Models'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFLICENSE', 'hflicense', 'Datasets: stated license against the license file', ['comparison', 'Datasets'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFSIZE', 'hfsize', 'Size in the name against the weights', ['comparison'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SECRECORDS', 'secrecords', 'HSTS preload header against its own requirements', ['comparison', 'HSTS preload header'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SECRECORDS', 'secrecords', 'SPF record against the 10-lookup limit', ['comparison', 'SPF lookup limit'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('PKGINSTALL', 'pkginstall', 'Install command against pip resolution', ['comparison'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('LINKROT', 'linkrot', 'Stated code links that are gone', ['all'], 'links', 'gone', 'rot_share', 'lo', 'hi', 'outcome'),
        ('TRIALS', 'trials', 'Results due against results posted: records with no results', ['all'], 'n', 'no_results', 'share_no_results', 'lo', 'hi', None),
        ('TRIALS', 'trials', 'Stopped records with no reason given', ['cancelled', 'tests', 'Stopped records with no reason given'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('TRIALS', 'trials', 'Withdrawn records that list participants enrolled', ['cancelled', 'tests', 'Withdrawn records that list participants enrolled'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome')]
SPEC.append(('REVISE', 'revise', 'Payroll: first estimate moved by more than the stated margin by the third release', ['counts', 'Third release against first'], 'months', 'exceed', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('REVISE', 'revise', 'Payroll: first estimate moved by more than the stated margin by the benchmarked value', ['counts', 'Most recent, after the annual benchmark, against first'], 'months', 'exceed', 'share', 'share_lo', 'share_hi', 'outcome'))
for k, name in (('1 A cms-hpt.txt at the root of the domain', 'Hospital website: a cms-hpt.txt at the root'), ('2 The file it links resolves to data', 'Hospital price file: the linked file resolves to data'), ('3 The file starts with the template header', 'Hospital price file: starts with the template header')):
    SPEC.append(('HPT', 'hpt', name, ['comparison', k], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('HOSTS', 'hosts', 'OpenRouter hosts: stated one-day uptime against our own 5-minute record, disagreements', ['headline'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('AIRQ', 'airq', 'PurpleAir sensors near EPA monitors: monitors whose sensor misses the EPA targets, map reading', ['comparison', 'Map reading (atm channels, raw)'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('AIRQ', 'airq', 'PurpleAir sensors near EPA monitors: monitors whose sensor misses the EPA targets, humidity-corrected', ['comparison', 'cf_1 corrected for humidity (Barkjohn 2021)'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('AILUMINATE', 'ailuminate', 'AILuminate results page against its own reports: disagreements', ['headline'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('AILUMINATE', 'ailuminate', 'AILuminate published scores that changed between reads', ['stability'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('WEIGHTS', 'weights', 'Open-weight models: weight files changed between passes', ['headline'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('AIRLINE', 'airline', 'Airlines whose scheduled minus flown time grew, 2026 against 2025 (count, no pooled rule)', ['headline'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('FEDSEP', 'fedsep', 'Federal Reserve projections: outcome outside the stated 70% range, this year', ['pooled', 'This year, September projection'], 'triples', 'outside', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('FEDSEP', 'fedsep', 'Federal Reserve projections: outcome outside the stated 70% range, next year', ['pooled', 'Next year, September projection'], 'triples', 'outside', 'share', 'share_lo', 'share_hi', 'outcome'))
rows = []; cache = {}
for page, slug, test, path, ok, fk, sk, lk, hk, ck in SPEC:
    if slug not in cache: cache[slug] = feed(slug)
    d = at(cache[slug], path) if cache[slug] else None
    if not isinstance(d, dict) or d.get(ok) in (None, 0) and d.get(fk) is None:
        rows.append(dict(page=page, slug=slug, test=test, of=None, n=None, share=None, share_lo=None, share_hi=None, outcome='NOTHING_RETURNED')); continue
    oc = d.get(ck) if ck else (trials_outcome(d[lk], d[hk]) if d.get(lk) is not None else 'NOTHING_RETURNED')
    rows.append(dict(page=page, slug=slug, test=test, of=d.get(ok), n=d.get(fk), share=d.get(sk), share_lo=d.get(lk), share_hi=d.get(hk), outcome=oc or 'NOTHING_RETURNED'))
ORDER = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED']
rows.sort(key=lambda r: (ORDER.index(r['outcome']) if r['outcome'] in ORDER else 9, -(r['share_lo'] or 0)))
tally = {o: sum(1 for r in rows if r['outcome'] == o) for o in ORDER}
# pages that report many separate items: tally by the outcome of each item
def walk(d, out):
    if isinstance(d, dict):
        if isinstance(d.get('outcome'), str): out.append(d['outcome'])
        for v in d.values(): walk(v, out)
    elif isinstance(d, list):
        for v in d: walk(v, out)
items = []
for page, slug in (('TIME', 'time'), ('UPTIME', 'uptime'), ('FORECAST', 'forecast'), ('CADENCE', 'cadence'), ('CADA', 'cada'), ('LAUNCH', 'launch'), ('ARXIVDRIFT', 'arxivdrift')):
    d = feed(slug); o = []; walk(d, o); c = {x: o.count(x) for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
    if slug == 'cadence' and d: c = {'ABOVE': 0, 'BELOW': sum(p['below'] for p in d['portals']), 'CONSISTENT': sum(p['consistent'] for p in d['portals']), 'CANNOT_TELL': sum(p['cannot_tell'] for p in d['portals'])}
    if sum(c.values()): items.append(dict(page=page, slug=slug, **c))

def jget(path):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/%s?x=%d' % (path, time.time()), headers={'User-Agent': 'heuremen-stack/0.1'}), timeout=40).read())
    except Exception: return None
def R(page, what, fn, path):
    d = jget(path)
    try: reading, state = fn(d)
    except Exception as e: reading, state = 'read failed: ' + type(e).__name__, 'NOTHING_RETURNED'
    return dict(page=page, what=what, reading=reading, state=state)
running = [
 R('ARXIVDRIFT', 'Indexed studies whose later arXiv version changed their numbers', lambda d: ('%d of %d (%.1f%%), %d with any revision' % (d['classes']['REVISED_NUMBERS']['n'], d['studies'], 100 * d['classes']['REVISED_NUMBERS']['n'] / d['studies'], d['any_change']['n']), 'Counted, no outcome rule'), 'arxivdrift/live.json'),
 R('CADENCE', 'Datasets updated more slowly than they state', lambda d: ('%d below of %d readable series, plus %d that cannot tell, across %d portals' % (sum(p['below'] for p in d['portals']), sum(p['readable'] for p in d['portals']), sum(p['cannot_tell'] for p in d['portals']), len(d['portals'])), 'Per-series outcomes, tallied below'), 'cadence/live.json'),
 R('CADA', 'Public DNS filters that answer on listed bad domains', lambda d: ('%d domains tracked, %d filters answered' % (d['tracked'], sum(1 for r in d['resolvers'] if any((c or {}).get('n') for c in (r.get('checkpoints') or {}).values()))), 'Running, under its own rule'), 'cada/live.json'),
 R('FORECAST', 'Stated chance of precipitation against what happened', lambda d: ('%d periods scored of %d stored, %d with an event' % (d['periods_scored'], d['periods_stored'], d['floor']['with_event']), 'Cannot tell, under 30 events'), 'forecast/live.json'),
 R('LAUNCH', 'Stated launch time against the time it flew', lambda d: ('%d launches tracked, %d flown, %d waiting' % (d['launches_tracked'], d['flown'], d['waiting']), 'Waiting for flown launches to score'), 'launch/live.json'),
 R('WATER', 'End-of-month lake levels inside the range a 24-Month Study projected six months ahead', lambda d: ('Lake Mead %d of %d, Lake Powell %d of %d, against the 80 percent Reclamation states' % (d['headline_lead6']['mead']['band']['inside'], d['headline_lead6']['mead']['band']['n'], d['headline_lead6']['powell']['band']['inside'], d['headline_lead6']['powell']['band']['n']), 'Lake Mead %s, Lake Powell %s, under its own rule' % (d['headline_lead6']['mead']['band']['outcome'].lower().replace('_', ' '), d['headline_lead6']['powell']['band']['outcome'].lower().replace('_', ' '))), 'water/live.json'),   # 10 Nov: WATER (ATLAS) joins as its page ships
 R('WIKI', 'Population figures in Wikidata citing the World Bank that match a World Bank release', lambda d: ('%s of %s, %s of them the current release' % ('{:,}'.format(d['section1']['WB-POP']['bins']['MATCHES_CURRENT']['k'] + d['section1']['WB-POP']['bins']['MATCHES_AN_OLDER_RELEASE']['k']), '{:,}'.format(d['section1']['WB-POP']['rows']), '{:,}'.format(d['section1']['WB-POP']['bins']['MATCHES_CURRENT']['k'])), 'Counted per figure, read about once a week'), 'wiki/live.json'),   # 10 Nov: WIKI (HERMES) joins as its page ships
 R('CHANGE', 'Vendor shutdown dates that held as they passed', lambda d: ('%d rows read since %s, %d dates have passed' % (d['rows'], d['first_snapshot'], d['test']['of']), 'Cannot tell, under 30 dates'), 'change/live.json'),
 R('SEAT', 'Pages and feeds, seen from an outside runner', lambda d: ('%d probes, %d of %d pages match, %d of %d feeds fresh' % (d['probes'], d['now']['Pages matching the public repository']['n'], d['now']['Pages matching the public repository']['of'], d['now']['Feeds younger than their limit']['n'], d['now']['Feeds younger than their limit']['of']), list(d['rolling'].values())[0]['outcome']), 'seat/live.json'),
 R('QIA', 'Published qubits with T2 above 2.5 times T1', lambda d: ('%d qubits on %d processors' % (len(d['flagged']), len({f['backend'] for f in d['flagged']})), 'Counted from IBM records, no outcome rule'), 'qia/audit.json'),
 R('QIA', 'T1 and T2 measured together on flagged qubits', lambda d: (' '.join(('%s %s' % (p['backend'].replace('ibm_', '').capitalize(), p.get('state', '')[:34]) + ('' if 'qubits' not in p else ': ' + ', '.join('q%d %s' % (q['qubit'], q['reading'].lower().replace('_', ' ')) for q in p['qubits']))).rstrip('.') + '.' for p in d['processors']), 'Per-qubit readings, four outcomes'), 'qia/t1t2.json'),
 R('QIA', 'Jobs pending at each processor', lambda d: (', '.join('%s %s' % (p['backend'].replace('ibm_', ''), p['pending']) for p in d['processors']), 'Hourly, analysis rule committed'), 'qia/queue.json'),
 R('QIA', 'Stability of IBM published calibration over time', lambda d: ('%d processors, %d to %d records each' % (len(d['processors']), min(p['records'] for p in d['processors']), max(p['records'] for p in d['processors'])), 'Waiting for 20 records and 14 days'), 'qia/stability.json')]

GROUP = {'REVISE': 'A stated number against its record', 'AIRLINE': 'A stated number against its record', 'WEIGHTS': 'A stated number against its record', 'AILUMINATE': 'A stated number against its record', 'AIRQ': 'A stated number against its record', 'HOSTS': 'A stated number against its record', 'FEDSEP': 'A stated number against its record', 'SECRECORDS': 'A stated number against its record', 'HFSIZE': 'A stated number against its record', 'PKGLICENSE': 'A stated number against its record', 'HFLICENSE': 'A stated number against its record', 'TRIALS': 'A stated number against its record',
         'LINKROT': 'A promised file or link', 'PKGINSTALL': 'A promised file or link', 'HPT': 'A promised file or link', 'ARXIVDRIFT': 'A promised file or link',
         'SUPPORT': 'A stated date or window', 'CHANGE': 'A stated date or window', 'CADENCE': 'A stated date or window', 'LAUNCH': 'A stated date or window', 'FORECAST': 'A stated date or window',
         'SEAT': 'Checks on ourselves, time and uptime', 'TIME': 'Checks on ourselves, time and uptime', 'UPTIME': 'Checks on ourselves, time and uptime', 'CADA': 'Checks on ourselves, time and uptime', 'COIN': 'Checks on ourselves, time and uptime'}
stacks = {}
for r in rows:
    g = GROUP.get(r['page'])
    if g and r['share'] is not None: stacks.setdefault(g, []).append(dict(page=r['page'], test=r['test'], of=r['of'], n=r['n'], share=r['share'], share_lo=r['share_lo'], share_hi=r['share_hi'], outcome=r['outcome']))
for g in stacks: stacks[g].sort(key=lambda x: -x['share'])
def dv(path):
    return jget(path)
qs, ir, irl, aud = dv('qia/list.json'), dv('iris/live.json'), dv('iris/list.json'), dv('qia/audit.json')
# 30 Oct (site pass I-14): the desks under each division are read from the HOME map in the site builder, so a new desk is listed without anyone typing it here.
import re, ast
try: HOME = ast.literal_eval(re.search(r'^HOME = (\{.*?\})\s*$', open(os.path.expanduser('~/bones-forge/indahl-ai/build_site.py')).read(), re.S | re.M).group(1))
except Exception: HOME = {}
def desks(div): return [k[1:].upper() for k, v in HOME.items() if v == div]
def nl(xs): return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else '')
divisions = [
 dict(name='QIA', link='/qia', holds='IBM calibration audited against itself, T1 and T2 runs on flagged qubits, the processor queue, and every quantum study we have indexed', reading=('%d studies indexed, %d qubits flagged by the audit' % (len(qs['studies']), len(aud['flagged']))) if qs and aud else ''),
 dict(name='IRIS', link='/iris', holds='Language-model evaluations, the Faults and Guards bench, a lab queue, the evaluation studies we have indexed, and the desks ' + nl(desks('/iris')), reading=('%d studies indexed, lab runs: %d running, %d next, %d done' % (len(irl['studies']), len(ir['running']), len(ir['next']), len(ir['done']))) if irl and ir else ''),
 dict(name='OY', link='/oy', holds='What colleges publish about measuring their own AI policies, with a source for every row' + (', and the desk ' + nl(desks('/oy')) if desks('/oy') else ''), reading='Static tables, and the desk ' + nl(desks('/oy')) if desks('/oy') else 'Static tables, read on the page'),
 dict(name='ATLAS', link='/atlas', holds='Built infrastructure, mapped from open sources, and the desks ' + nl(desks('/atlas')), reading='Static map and tables, and the live desks'),
 dict(name='HERMES', link='/hermes', holds='Held Every Record, Measured Every Statement: claims by vendors and public institutions against the record, and every desk under it', reading='Desks: ' + ', '.join(['MODEL'] + desks('/hermes')))]
rows_out = [dict(r, test_key=i) for i, r in enumerate(rows)]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), tests=len(rows), tally={o: dict(n=tally[o]) for o in ORDER if tally[o]}, rows=[dict(page=r['page'], test=r['test'], of=r['of'], n=r['n'], share=r['share'], share_lo=r['share_lo'], share_hi=r['share_hi'], outcome=r['outcome']) for r in rows],
           items={i['page']: {k: v for k, v in i.items() if k not in ('page', 'slug')} for i in items}, running=running, divisions=divisions, stacks=stacks)
json.dump(out, open('summary_stack.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'stack_live', '--path', os.path.join(H, 'summary_stack.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('stack:', len(rows), 'tests;', out['tally'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
