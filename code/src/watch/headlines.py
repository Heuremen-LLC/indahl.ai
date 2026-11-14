#!/usr/bin/env python3
"""headlines.py: tick-bus rider. Builds one headline per page from the live feeds (number first, plain words) and publishes headlines.json to the KV key 'headlines'.
The pages' headline.js reads /headlines.json. A page whose feed cannot be read gets no headline this round."""
import os, re, json, time, subprocess, urllib.request, hashlib
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
B = os.path.expanduser('~/bones-forge'); W = B + '/cloudflare-workers/heuremen-door'; NS = 'ecb59d96b07c43bdac14271687eae5af'
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u + ('&' if '?' in u else '?') + 'x=%d' % time.time(), headers={'User-Agent': 'heuremen-headlines/0.1'}), timeout=30).read()
# 10 Nov 2026 (cold read row 5): the riders run in parallel on the bus, and a KV write takes up to a minute to reach the edge, so a headline read
# from the public feed could carry the read before the one the page body shows. A desk that keeps its feed file here is read from that file,
# the same bytes its tick puts to KV, and the HOSTS and QIA queue ticks start this script again right after they publish.
LOCAL = {'hosts': B + '/hosts_index/summary_hosts.json', 'neo': B + '/neo_index/data/neo_live.json', 'quake': B + '/quake_index/data/quake_live.json', 'census': B + '/census_index/data/census_live.json', 'solar': B + '/solar_index/data/solar_live.json', 'cone': B + '/cone_index/data/cone_live.json', 'tornado': B + '/tornado_index/data/tornado_live.json', 'credit': B + '/credit_index/data/credit_live.json'}   # 10 Nov 2026: NEO's feed file is the bytes its tick puts to KV neo_live
def feed(s):
    if s in LOCAL and os.path.exists(LOCAL[s]): return json.load(open(LOCAL[s]))
    return json.loads(get('https://indahl.ai/%s/live.json' % s))
import fcntl as _fc
_lk = open(B + '/watch/.headlines.lock', 'w'); _fc.flock(_lk, _fc.LOCK_EX)   # one build at a time; a second start waits and then builds from the newer files
def ordn(n): n = int(n); return '%d%s' % (n, 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))
def pct(x, d=0): return ('%.' + str(d) + 'f%%') % (100 * x)
def f(n): return '{:,}'.format(int(n))
H = {}
def add(slug, big, line, href=None):
    H[slug] = dict(big=big, line=line, href=href or '/' + slug)
def safe(slug, fn):
    try: fn()
    except Exception as e: print('headlines: skipped', slug, type(e).__name__, str(e)[:60])
def airq():
    d = feed('airq'); c = d['comparison']; a = c['Map reading (atm channels, raw)']; r = c['cf_1 corrected for humidity (Barkjohn 2021)']
    # 10 Nov 2026 (AIRQ Addendum 5): the plan names no headline reading, so the map reading and the corrected reading lead together, with the other tie
    tie = lambda c: (' (%d under the other tie)' % c['n_other_tie']) if c.get('n_other_tie') is not None and c['n_other_tie'] != c['n'] else ''
    # 11 Nov (his "poorly worded ... is there a better, shorter one"): both readings as one range, neither named the headline (Addendum 5); ties and 2025 stay on /airq
    lo, hi = sorted((r['n'], a['n']))
    add('airq', '%d to %d' % (lo, hi), 'of %d EPA monitors had a nearby PurpleAir sensor that missed the EPA accuracy target, %s: %d with the humidity correction, %d on the raw map reading.' % (a['of'], d.get('window') or '1 June to 29 September 2025', r['n'], a['n']))
def hosts():
    d = feed('hosts'); add('hosts', f(d['problems_now']), 'open-weight model endpoints were flagged by OpenRouter or showed 5-minute uptime below 100 percent at the read of %s UTC, out of %s endpoints on %d hosts serving %d models.' % (d['updated'][-5:], f(d['endpoints']), d['hosts'], d['models']))
def airline():
    d = feed('airline'); rows = [(k, v) for k, v in d['now_vs_2025'].items() if v.get('outcome') == 'ABOVE']; rows.sort(key=lambda kv: -kv[1]['change'])
    top = ', '.join('%s +%d min' % (k.split(' (')[0], round(v['change'])) for k, v in rows[:3])
    _fa = d.get('faa', {}); faa = _fa.get('airports_listed', _fa.get('airports_now')); prog = _fa.get('airports_now'); tail = (' Right now the FAA lists a delay or closure notice at %d airport%s, %d with a delay program.' % (faa, '' if faa == 1 else 's', prog or 0)) if faa is not None else ''   # 30 Oct 2026 (site pass I-4): the count includes closures until nas_tick.py counts programs only
    add('airline', '%d of %d' % (len(rows), d['headline']['of']), 'airlines widened the gap between scheduled and flown time on their median route, %s 2026 against 2025: %s.%s' % (d.get('months') or 'January to August', top, tail) + ((' Airlines read: ' + d['headline']['req13']['line']) if (d['headline'].get('req13') or {}).get('line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)   # 9 Nov 2026 (site pass M2): a median over routes, not each route
def weights():
    d = feed('weights'); h = d['headline']; e = d.get('ever') or h   # 30 Oct site pass I-3: changes on any pass, not netted to the latest pair
    add('weights', '%d of %s' % (e['n'], f(e['of'])), 'popular Hugging Face models changed their weight files on at least one of our reads, %d between the last two. Last read %s UTC.' % (h['n'], d['updated'][-5:]))
def ailuminate():
    d = feed('ailuminate'); v = [r['overall'] for r in d['table'].values()]
    add('ailuminate', '%d to %d' % (min(v), max(v)), 'the percentile range of overall safety scores across the %d systems MLCommons published, on the same 12 hazard categories.' % len(v))
def campus():
    d = feed('campus'); s = d['state_now']; add('campus', '%d of %d' % (s['Opens (HTTP 200)'], d['sources']), 'sources behind the OY page open today. %d are not found and %d refuse automated reads.' % (s['Not found (404, 410)'], s['Blocked (401, 403, 429)']))
def hpt():
    d = feed('hpt'); c = d['comparison']; k2 = [v for k, v in c.items() if k.startswith('2')][0]
    add('hpt', '%d of %d' % (k2['n'], k2['of']), 'hospital price files linked from hospital websites do not open as data. We read %s hospital websites for the file the federal rule asks for.' % f(d['domains']))
def secrecords():
    d = feed('secrecords'); c = d['comparison']; a = c['HSTS preload header']; b = c['SPF lookup limit']
    add('secrecords', pct(a['share']), 'of top sites that send an HSTS preload header miss the preload list\'s own requirements (%d of %d). %d of %d SPF records break the 10-lookup limit.' % (a['n'], a['of'], b['n'], b['of']) + (' HSTS: ' + a['req13_line'] if a.get('req13_line') else '') + (' SPF: ' + b['req13_line'] if b.get('req13_line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13): the counts beside each headline share
def hfsize():
    d = feed('hfsize'); c = d['comparison']; add('hfsize', '%d of %d' % (c['n'], c['of']), 'popular Hugging Face models weigh outside the size in their name.' + (' ' + c['req13_line'] if c.get('req13_line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)
def pkglicense():
    # 30 Oct 2026 (site pass I-21): say what the disagreements are. Our hand notes show some are a classifier that differs from the license field, or a package in a subfolder of a repository with another root license.
    d = feed('pkglicense'); c = d['classes']; n = c['DISAGREE']['n']; of = c['AGREE']['n'] + n
    soft = sum(1 for r in d.get('disagree_list', []) if 'classifier' in r.get('reason', '') or 'subfolder' in r.get('reason', ''))
    add('pkglicense', '%d of %d' % (n, of), 'PyPI projects state a license that differs from the license GitHub reports for their repository.' + ((' We read each in full. %d of them are a classifier that differs from the license field, or a package in a subfolder of a repository with another root license.' % soft) if soft else '') + (' ' + d['disagree']['req13_line'] if d.get('disagree', {}).get('req13_line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)
def support():
    d = feed('support'); a = d['all']; add('support', pct(a['share']), 'of release cycles stated as supported had no release in more than a year (%d of %d).' % (a['unreleased'], a['tested']))
def trials():
    # 10 Nov 2026 (TRIALS Addendum 5): records 13 to 15 months past completion are the plan's lag zone and are not scored
    d = feed('trials'); a = d['all']; add('trials', pct(a['share_no_results'], 1), 'of ClinicalTrials.gov trials of FDA-regulated drugs and devices that reached primary completion at least 15 months ago have no results on the record (%s of %s).' % (f(a['no_results']), f(a['n'])) + ((' Records 13 to 15 months past completion are shown apart and not scored (%s).' % f(d['lag_zone']['n'])) if d.get('lag_zone') else ''))
def revise():
    d = feed('revise'); c = d['counts']; k = [v for kk, v in c.items() if kk.startswith('Most recent')][0]; t = [v for kk, v in c.items() if kk.startswith('Third')][0]
    OC = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}   # 10 Nov 2026 (newsletter audit): both intervals, and which one the plan names
    RW = lambda o, r: OC.get(o, o) + ((' (%s)' % r) if o == 'CANNOT_TELL' and r else '')   # 12 Nov 2026 (Faults and Guards 2.0): the reason stands beside every cannot tell
    add('revise', '%d of %d' % (k['exceed'], k['months']), 'monthly jobs numbers moved by more than the BLS\'s stated margin once benchmarked. %d of %d moved that far by the third release. On the interval over months, which the plan names, the benchmarked count reads %s. On the interval over calendar years it reads %s.' % (t['exceed'], t['months'], RW(k['outcome'], k.get('reason')), RW(k.get('outcome_y'), k.get('reason_y'))) + ((' Beside the benchmarked count: ' + k['req13']['line']) if (k.get('req13') or {}).get('line') else ''))
def fedsep():
    d = feed('fedsep'); p = d['pooled']; n = [v for k, v in p.items() if k.startswith('Next')][0]; t = [v for k, v in p.items() if k.startswith('This')][0]
    add('fedsep', '%d of %d' % (n['outside'], n['triples']), 'next-year Fed projections landed outside the 70 percent range the Fed states. This year, %d of %d.' % (t['outside'], t['triples']) + ((' Read against 0.30 with no tolerance, next year reads cannot tell (%s). %s' % (n.get('reason'), n['req13']['line'])) if (n.get('req13') or {}).get('line') and n.get('outcome') == 'CANNOT_TELL' else ((' ' + n['req13']['line']) if (n.get('req13') or {}).get('line') else '')))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)
def change():
    d = feed('change'); L = d['lifespan']; g = L.get('Google, names with preview') or L['Google']; o = L.get('Google, other names')   # 30 Oct site pass I-2: all of the short-lived ones are previews
    add('change', '%d of %d' % (g['under180'], g['n']), 'Google preview models with a shutdown date ran under six months. Their median is %s days.%s' % (('%g' % g['median']), (' Of %d other Google models, %d did (median %s days).' % (o['n'], o['under180'], '%g' % o['median'])) if o else ''))
def cadence():
    # 10 Nov 2026 (newsletter audit): never round an age up to a whole year. 5,782 days is 15.8 years, printed as nearly 16 years.
    d = feed('cadence'); m = d['most_overdue'][0]; y = m['age_days'] / 365.25; n = round(y)
    add('cadence', ('nearly %d years' if n > y else 'over %d years') % n, 'since a US government dataset that states a daily update was last modified (%.1f years): %s, %s.' % (y, m['title'], m['portal']) + ((' Across all series read: ' + d['req13']['line']) if (d.get('req13') or {}).get('line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)
def linkrot():
    d = feed('linkrot'); a = d['all']; add('linkrot', pct(a['rot_share'], 1), 'of code and data links in arXiv papers are gone (%d of %s).' % (a['gone'], f(a['links'])))
def _watched_flown():
    # launches that flew after we first read them: some snapshot of the launch was taken before it flew. Launches already flown at our first read cannot be scored.
    f = B + '/launch_index/data/snapshots.jsonl'
    if not os.path.exists(f): return None
    hist = {}
    for l in open(f):
        try: s = json.loads(l)
        except Exception: continue
        hist.setdefault(s['id'], []).append(s)
    FL = {'Success', 'Failure', 'Partial Failure'}; n = 0
    for hs in hist.values():
        if hs[-1]['status'] in FL and any(h['status'] not in FL for h in hs): n += 1
    return n
def launch():
    # 30 Oct 2026 (site pass H-4): the first reads already held 100 flown launches, which were never watched before they flew and cannot be scored.
    d = feed('launch'); w = _watched_flown()
    if w is None: add('launch', '%d' % d['waiting'], 'tracked launches are waiting to fly. Each stated launch time is scored against the actual one once the launch has flown.'); return
    add('launch', '%d' % w, 'launches have flown since we began reading them. %d more are waiting to fly. The other %d flown launches were already in the record at our first read and are not scored. Each stated launch time is scored against the actual one.' % (d['waiting'], d['flown'] - w))
def pkginstall():
    d = feed('pkginstall'); c = d['comparison']; add('pkginstall', '%d of %d' % (c['of'] - c['n'], c['of']), 'install commands in popular Python packages resolve on a clean install. Only the %d of %s projects with a comparable command are counted.' % (c['of'], f(d.get('projects', 1000))) + (' ' + c['req13_line'] if c.get('req13_line') else ''))   # 12 Nov 2026 (Faults and Guards 2.0, REQ-13)
def oy():
    # 10 Nov 2026 (newsletter audit): the headline is built with the page by oy_index/matrix_page/build_matrix_page.py from the rows (two readings,
    # the rule written before the read first, the rule set after 41 schools beside it). Read from that file, never scraped or typed here.
    h = json.load(open(B + '/oy_index/matrix_page/oy_headline.json', encoding='utf-8')); add('oy', h['big'], h['line'])
def tape():
    # 30 Oct 2026 (site pass I-28): lead on the age of the newest entry, not on a count of our own entries
    d = feed('tape'); h = d['head']; b = d['beacon']
    import calendar; age = max(0, time.time() - calendar.timegm(time.strptime(h['t'][:19], '%Y-%m-%dT%H:%M:%S')))
    add('tape', _dur(age), 'since the newest entry was chained to the tape, at %s UTC. Each entry is hashed onto the one before, and the beacon now begins %s.' % (h['t'][11:16], b['value'][:8]))
def atlas():
    # 30 Oct 2026 (site pass A-16): ATLAS has its own headline, from its own map data, and no longer borrows the SECRECORDS reading
    # 30 Oct 2026 (his "the data headline is the cost to scale"): once /atlas/scale.json is live the headline is the cost to scale, arithmetic on Epoch AI's stated power and EIA-861 state prices. Until then the count line below stands.
    try:
        t = json.loads(get('https://indahl.ai/atlas/scale.json'))['totals']
        add('atlas', '$%s billion' % t['total_busd'], 'for one year of electricity at the full stated power of the %d AI data centers in Epoch AI\'s dataset that state a power and sit in a state, at each state\'s average 2024 industrial price from EIA-861. It is arithmetic on published figures, not a forecast and not any site\'s bill.' % t['counted'], '/atlas')
        return
    except Exception: pass
    d = json.loads(get('https://indahl.ai/atlas/datacenters.json'))
    add('atlas', f(len(d['osm'])), 'features tagged as data centers in OpenStreetMap in the United States, and %d AI data centers in Epoch AI\'s dataset, pulled %s. This is what these two sources hold, not a count of every data center.' % (len(d['epoch']), d['pulled']), '/atlas')
def _dur(x):
    x = float(x); return '%d s' % round(x) if x < 90 else ('%d min' % round(x / 60) if x < 5400 else '%.1f h' % (x / 3600))
def _open_rates():
    # 30 Oct 2026 (his "labs should check QIA for the fez wait time"): Open plan probes pair the jobs in front at sending with the measured wait
    rows = [json.loads(l) for l in open(B + '/qia_queue/data/probes_open.jsonl')] if os.path.exists(B + '/qia_queue/data/probes_open.jsonl') else []
    out = {}
    for r in rows:
        if r.get('wait_s') is None: continue
        out.setdefault(r['backend'], []).append((r.get('front_at_send') or 0, r['wait_s']))
    return out
def _probes(name):
    f = B + '/qia_queue/data/' + name
    return [json.loads(l) for l in open(f)] if os.path.exists(f) else []
def qia():
    # 30 Oct 2026 (his "labs should check QIA for the fez wait time ... every us east and europe plan"): jobs in front from IBM (free), the wait our
    # latest one-shot probe saw on each processor (paid plans, every hour), and the Open plan approximation from its own probes.
    d = json.load(open(B + '/qia_queue/summary.json')); ps = [dict(backend=p['backend'], pending=p['pending']) for p in d['processors'] if p.get('pending') is not None]
    eu = _probes('probes_eu.jsonl')
    if eu and eu[-1].get('front_at_send') is not None and not any(p['backend'] == eu[-1]['backend'] for p in ps): ps.append(dict(backend=eu[-1]['backend'], pending=eu[-1]['front_at_send']))
    ps.sort(key=lambda p: -p['pending']); b = ps[0]; avg = sum(p['pending'] for p in ps) / len(ps); now = time.time()
    latest = {}
    for r in _probes('probes.jsonl') + eu:
        if r.get('state') != 'NOT_FOUND': latest[r['backend']] = r   # files are in send order, so the last row per processor is the newest (11 Nov: a job IBM cannot find carries no wait)
    def wait_now(n):
        r = latest.get(n)
        if not r: return 'first probe pending'
        if r.get('wait_s') is not None: return _dur(r['wait_s'])
        import calendar; t = calendar.timegm(time.strptime(r['sent'], '%Y-%m-%dT%H:%M:%SZ'))   # the stamp is UTC
        return 'waiting ' + _dur(max(0, now - t)) + ' so far'
    OPENP = ('ibm_fez', 'ibm_kingston', 'ibm_marrakesh'); rates = _open_rates()
    def approx(p):
        if p['backend'] not in OPENP: return '\u2014'
        v = rates.get(p['backend'], [])
        if not v: return 'pending'
        rs = sorted(w / f for f, w in v if f > 0)
        if not rs: return _dur(max(w for f, w in v))
        return 'about ' + _dur(p['pending'] * rs[len(rs) // 2])
    add('qia', f(b['pending']), 'jobs in front at %s, the longest IBM queue. Last read %s.' % (b['backend'], d['updated']))
    # 11 Nov 2026 (his "make qubit 85 a data headline on QIA"): the lead is boston qubit 85 from its newest joint T1/T2 run, while IBM's T2 reads ABOVE
    # the 2 x T1 ceiling; the queue keeps its table below. Read from t1t2_check/summary_t1t2.json, the bytes publish_results.py puts to KV qia_t1t2.
    try:
        tt = json.load(open(B + '/t1t2_check/summary_t1t2.json'))
        runs = sorted([(p['ran'], q) for p in tt['processors'] if p['backend'] == 'ibm_boston' and p.get('state') == 'ran' for q in p['qubits'] if q['qubit'] == 85])
        if runs and runs[-1][1].get('ibm_t2_vs_now') == 'ABOVE':
            ran, q = runs[-1]; day = time.strftime('%-d %b', time.strptime(ran[:10], '%Y-%m-%d'))
            line = ('is the T2 IBM publishes for qubit 85 on ibm_boston. Our run on %s measured its T1 at %.1f \u00b5s (95%% interval %.1f to %.1f), so no T2 on that qubit could be above %.1f \u00b5s.'
                    % (day, q['t1'], q['t1_ci'][0], q['t1_ci'][1], q['t2_max_now']))
            # 11 Nov (his "put both in the headline"): the other qubit in the same job, when IBM's T1 for it reads ABOVE or BELOW our measured interval
            same = [p for p in tt['processors'] if p['backend'] == 'ibm_boston' and p.get('ran') == ran]
            for c in (same[0]['qubits'] if same else []):
                if c['qubit'] != 85 and c.get('ibm_t1_vs_now') in ('ABOVE', 'BELOW'):
                    line += (' In the same job, the T1 IBM publishes for qubit %d (%.0f \u00b5s) is %s what we measured, %.0f \u00b5s (95%% interval %.0f to %.0f).'
                             % (c['qubit'], c['pub_t1'], 'below' if c['ibm_t1_vs_now'] == 'BELOW' else 'above', c['t1'], c['t1_ci'][0], c['t1_ci'][1]))
            add('qia', '%.1f \u00b5s' % q['pub_t2'], line, href='/qia#t1t2-live')
    except Exception as e: print('headlines: qia qubit 85 lead skipped', type(e).__name__, str(e)[:60])
    # 11 Nov (his "we never have wait times for the open plan"): the Open plan column shows only while its probes have a wait from the last 7 days
    _op = [r for r in _probes('probes_open.jsonl') if r.get('wait_s') is not None and r.get('sent', '') >= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now - 7 * 86400))]
    _cols = ['Processor', 'Jobs in front', 'Wait now, paid plan'] + (['Approx. wait, Open plan'] if _op else [])
    H['qia']['table'] = dict(cols=_cols, rows=[[p['backend'], f(p['pending']), wait_now(p['backend'])] + ([approx(p)] if _op else []) for p in ps],
                             foot=['Average', f(round(avg)), ''] + ([''] if _op else []), note='Wait now: the wait of our latest calibration job on a paid plan, from sending to running (or how long it has waited so far). A job is not sent to every processor every hour.' + (' Approx. wait on the Open plan, the free line most labs use, is our own estimate: jobs in front now times the seconds per job in front measured by our probes there (\u2014 not on the Open plan).' if _op else '') + ' IBM publishes no wait estimate.')
    H['qia']['table']['cta'] = dict(text='Check a wait yourself: probe.py', href='/qia/probe.py', rest=' One Python file and your own IBM key. Jobs in front are free, a timed probe costs 2 s of your plan. Source also on ', link2='GitHub', href2='https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/qia/probe.py', tail=', needs qiskit-ibm-runtime (PyPI).')
def lab():
    # 11 Nov 2026 (his "ANY training we do is live on the lab page ... every page should have a live something at top and a data headline"): the newest
    # paired test of a the council lane seat, and every seat's stage now, from sage_library/council/live_export.json (the allow-listed bytes live_export.py puts to KV council_live).
    if os.path.exists(B + '/sage_library/council/PAUSE') and os.path.exists(B + '/stan/results/baseline_dev.json'):
        # 12 Nov 2026 (his "close it out on the lab too and make sure Stan is live"): the council lane is paused for STAN, so the lab leads with STAN. Every number is computed from
        # stan/results/baseline_dev.json: the untrained base's pooled agreement with the answer key (development half), and the pooled majority-class rate
        # (n-weighted mean of the per-code rates). Ledger rows stan.baseline.base and stan.baseline.majority.
        # 12 Nov 2026 (Sage break 1): the agreement headline counted CANNOT_TELL as agreeing with an unflagged recount, so it measured abstention.
        # The lab now leads with the decided share (calls a model commits to), from stan/results/decided_summary.json. Ledger rows stan.v1.decided, stan.base.decided.
        ds = json.load(open(B + '/stan/results/decided_summary.json'))
        if 'test_stan' in ds:
            add('iris/lab', '%d%%' % round(100 * ds['test_stan']['decided_share']),
                'of checklist calls STAN v1 committed to on the test half of our answer key. It answered cannot tell on every one, so it was not kept. Its untrained base committed on %d%%. Next: test whether the evidence the recounts used is in an abstract at all, before training on full text.'
                % round(100 * ds['test_base']['decided_share']), href='/iris/lab#stan')
        names = {'base': 'Untrained base (Qwen3-1.7B)', 'llama': 'Llama 3.1 8B', 'mistral': 'Mistral 7B', 'gemma': 'Gemma 3 4B'}
        rows = [[names.get(k[4:], k[4:]), '%d%%' % round(100 * v['decided_share']), str(v['calls'])] for k, v in ds.items() if k.startswith('dev_')]
        H['iris/lab']['table'] = dict(cols=['Model', 'Calls committed to', 'Calls'], rows=rows,
                                      note='Development half of the answer key, seven codes pooled. A call is committed when it is present, absent or not applicable rather than cannot tell. the council lane is paused so the machines can train STAN.',
                                      cta=dict(text='Watch STAN live', href='/iris/lab#stan', rest=' Results as data: ', link2='GitHub', href2='https://github.com/Heuremen-LLC/stan', tail='.'))
        return
    d = json.load(open(B + '/sage_library/council/live_export.json'))
    pr = sorted([x for x in d.get('paired') or [] if x.get('grounded') and len(x['grounded']) == 4 and None not in x['grounded']], key=lambda x: x['ts'])
    ev = sorted(d.get('events') or [], key=lambda x: x['ts'])
    def outcome(seat, ts):
        for e in ev:
            if e['seat'] == seat and e['ts'] >= ts and e['event'] in ('went live', 'rolled back after the paired eval', 'rolled back', 'champion kept'):
                return {'went live': 'The new adapter went live.', 'champion kept': 'The adapter already serving was kept over it.',
                        'rolled back': 'The new adapter was rolled back.', 'rolled back after the paired eval': 'The new adapter was rolled back on its test.'}[e['event']]
        return 'Its release is being decided.'
    def ago(ts):
        m = int((time.time() - time.mktime(time.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')) + time.timezone) // 60)
        return '%d min ago' % m if m < 120 else '%d h ago' % (m // 60)
    if pr:
        x = pr[-1]; g = x['grounded']
        add('iris/lab', '%d%%' % round(100 * g[1]),
            "of %s's claims carried a quote the code found in the passage it was shown, with this turn's adapter, against %d%% for the base model, on %d held-out prompts (difference %d to %d points, 95%% interval). %s Tested %s."
            % (x['seat'], round(100 * g[0]), x['n'], round(100 * g[2]), round(100 * g[3]), outcome(x['seat'], x['ts']), ago(x['ts'])), href='/iris/lab/live')
    else:
        return
    def short(seat, ts):
        o = outcome(seat, ts)
        return {'The new adapter went live.': 'went live', 'The adapter already serving was kept over it.': 'kept the serving adapter', 'The new adapter was rolled back.': 'rolled back',
                'The new adapter was rolled back on its test.': 'rolled back on its test'}.get(o, 'deciding')
    NOW = {'harvest': 'collecting examples', 'SFT': 'training', 'DPO': 'preference training', 'paired eval': 'testing', 'idle': 'idle'}
    SERV = {'released': 'its own adapter', 'serving, not released': 'adapter on trial', 'base model': 'base model', 'paused': 'paused'}
    last = {}
    for y in pr: last[y['seat']] = y
    rows = []
    for st in d.get('seats') or []:
        y = last.get(st['seat'])
        rows.append([st['seat'], ('%d%% to %d%%' % (round(100 * y['grounded'][0]), round(100 * y['grounded'][1]))) if y else '\u2014',
                     (short(st['seat'], y['ts']) + ', ' + ago(y['ts'])) if y else 'no test yet',
                     NOW.get(st.get('stage'), st.get('stage') or ''), SERV.get(st.get('status'), st.get('status') or '')])
    H['iris/lab']['table'] = dict(cols=['Seat', 'Quoted claims, base to adapter', 'Last test', 'Now', 'Serving'], rows=rows,
                                  note='Cycle %d of the council. Every turn collects examples, trains a LoRA adapter, then tests it against its own base model on held-out prompts. Updated %s UTC. Every result is also in the public repository.' % (d.get('cycle') or 0, d['updated'][11:16]),
                                  cta=dict(text='Watch every turn live', href='/iris/lab/live', rest=' Results as data: ', link2='GitHub', href2='https://github.com/Heuremen-LLC/council/tree/main/results', tail='.'))
def iris():
    d = feed('hosts'); add('iris', f(d['endpoints']), 'host endpoints serve %d open-weight models. %d were flagged by OpenRouter or showed 5-minute uptime below 100 percent at the last read, %s UTC.' % (d['models'], d['problems_now'], d['updated'][-5:]))
def water():
    # 10 Nov 2026: WATER (ATLAS). The six-month band cells against the 80 percent Reclamation states in its Minimum and Maximum reports, with the plan's
    # intervals, the Most Probable cells read against a median (our reading), and the ruler note where an after-data ruler gives another outcome.
    d = feed('water'); h = d['headline_lead6']; m, p = h['mead'], h['powell']; OC = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
    def dep(b): return any(v.get(k) and v[k] != b['outcome'] for v in (b.get('checks_after_data') or {}).values() for k in ('outcome', 'outcome_unrounded'))
    em, ep = round(0.8 * m['band']['n']), round(0.8 * p['band']['n'])
    seg = lambda b, nm: '%d to %d percent for %s' % (round(100 * b['lo']), round(100 * b['hi']), nm) + (', whose reading depends on the ruler' if dep(b) else '')
    sm, sp = seg(m['band'], 'Lake Mead'), seg(p['band'], 'Lake Powell')
    mo, po = m['mp']['outcome'], p['mp']['outcome']
    tell = lambda o, r=None: ('cannot tell' + (' (%s)' % r if r else '')) if o == 'CANNOT_TELL' else 'read ' + OC.get(o, o.lower())   # 12 Nov 2026: the closed reason beside cannot tell
    rm, rp = m['mp'].get('reason'), p['mp'].get('reason')
    rq = ''.join(' %s %s' % (nm, x['req13']['line']) for nm, x in (('Lake Mead band at six months:', m['band']), ('Lake Powell band at six months:', p['band'])) if x.get('req13'))   # REQ-13 beside the headline cells
    add('water', '%d of %d' % (m['band']['inside'], m['band']['n']),
        'Lake Mead end-of-month levels measured six months after a 24-Month Study fell inside the range between its Probable Minimum and Probable Maximum projections. Lake Powell: %d of %d. '
        'Reclamation\'s reports say \u201cThere is approximately an 80%% probability that a future elevation will fall inside the range of the minimum and maximum inflow scenarios.\u201d '
        'At that rate about %s would have. Counted on water years, the 95%% intervals are %s%s%s. '
        'Six months ahead the lake ended above the Most Probable projection in %d of %d Lake Mead and %d of %d Lake Powell projections. Read against a median, which is our reading, %s.%s'
        % (p['band']['inside'], p['band']['n'], ('%d of each' % em) if em == ep else ('%d and %d' % (em, ep)), sm, ', and ' if dep(m['band']) else ' and ', sp,
           m['mp']['above'], m['mp']['n'], p['mp']['above'], p['mp']['n'], ('both ' + tell(mo, rm)) if (mo, rm) == (po, rp) else ('Lake Mead %s and Lake Powell %s' % (tell(mo, rm), tell(po, rp))), (' Rows behind the band cells,' + rq) if rq else ''))
def solar():
    # 10 Nov 2026: SOLAR (ATLAS). The line comes from solar_index/solar_headline.py, the same function that writes the page (PLAN headline row: M-class flares, day one).
    import sys as _s; _s.path.insert(0, B + '/solar_index'); from solar_headline import headline
    big, line = headline(feed('solar')); add('solar', big, line)
def tornado():
    # 10 Nov 2026: TORNADO (HERMES). The line comes from tornado_index/tornado_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/tornado_index'); from tornado_headline import headline as _h
    big, line = _h(feed('tornado')); add('tornado', big, line)
def credit():
    # 10 Nov 2026: CREDIT (HERMES). The line comes from credit_index/credit_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/credit_index'); from credit_headline import headline as _h
    big, line = _h(feed('credit')); add('credit', big, line)
def flu():
    # 10 Nov 2026: FLU (HERMES). The line comes from flu_index/flu_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/flu_index'); from flu_headline import headline as _h
    big, line = _h(feed('flu')); add('flu', big, line)
def steo():
    # 10 Nov 2026: STEO (HERMES). The line comes from steo_index/steo_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/steo_index'); from steo_headline import headline as _h
    big, line = _h(feed('steo')); add('steo', big, line)
def seasonal():
    # 10 Nov 2026: SEASONAL (HERMES). The line comes from seasonal_index/seasonal_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/seasonal_index'); from seasonal_headline import headline as _h
    big, line = _h(feed('seasonal')); add('seasonal', big, line)
def neo():
    # 10 Nov 2026: NEO (ATLAS). The line comes from neo_index/neo_headline.py, the same function that writes the page, so the page and this headline
    # say the same thing: the plan's all-leads cell, the split by lead, and the dependence on one archived copy (referee R4, neo_index_referee/REFEREE.md).
    import sys as _s; _s.path.insert(0, B + '/neo_index'); from neo_headline import headline
    big, line = headline(feed('neo')); add('neo', big, line)
def cone():
    # 10 Nov 2026: CONE (ATLAS). The line comes from cone_index/cone_headline.py, the same function that writes the page. Headline cell fixed in cone_index/PLAN.md.
    import importlib.util as _u
    sp = _u.spec_from_file_location('cone_headline', B + '/cone_index/cone_headline.py'); m = _u.module_from_spec(sp); sp.loader.exec_module(m)
    big, line = m.headline(feed('cone')); add('cone', big, line)
def census():
    # 11 Nov 2026: CENSUS. The line comes from census_index/census_headline.py, the same function that writes the desk page.
    import sys as _s; _s.path.insert(0, B + '/census_index'); from census_headline import headline
    big, line = headline(feed('census')); add('census', big, line)
def quake():
    # 10 Nov 2026: QUAKE (ATLAS). The line comes from quake_index/quake_headline.py, the same function that writes the page.
    import sys as _s; _s.path.insert(0, B + '/quake_index'); from quake_headline import headline
    big, line = headline(feed('quake')); add('quake', big, line)
for n, fn in list(globals().items()):
    if callable(fn) and n in ('airq', 'hosts', 'airline', 'weights', 'ailuminate', 'campus', 'hpt', 'secrecords', 'hfsize', 'pkglicense', 'tape', 'support', 'trials', 'revise', 'fedsep', 'change', 'cadence', 'linkrot', 'launch', 'pkginstall', 'oy', 'qia', 'iris', 'atlas', 'water', 'neo', 'quake', 'census', 'solar', 'cone', 'tornado', 'credit', 'flu', 'steo', 'seasonal', 'lab'): safe(n, fn)
# division pages reuse the strongest desk beneath them
for dv, src in (('hermes', 'trials'),):
    if src in H: H[dv] = dict(H[src], href='/' + dv)
HOME = [s for s in ('airq', 'hosts', 'trials', 'hpt', 'support', 'fedsep', 'airline', 'ailuminate') if s in H]
out = dict(updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), pages=H, home=HOME)
p = B + '/watch/headlines.json'; json.dump(out, open(p, 'w'), indent=1)
fp = hashlib.sha256(json.dumps(out['pages'], sort_keys=True).encode()).hexdigest()[:16]; st = B + '/watch/headlines_state.json'; prev = json.load(open(st)) if os.path.exists(st) else {}
if prev.get('fp') != fp or time.time() - prev.get('t', 0) > 3000:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'headlines', '--path', p, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
    if r.returncode == 0 and _PUBLISH: json.dump(dict(fp=fp, t=time.time()), open(st, 'w'))
    print('headlines:', len(H), 'pages', 'published' if r.returncode == 0 else 'publish FAILED')
else: print('headlines:', len(H), 'pages unchanged')
