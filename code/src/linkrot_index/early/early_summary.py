#!/usr/bin/env python3
"""early_summary.py: summary and page fragments for the LINKROT broader samples (PLAN.md Addendum 3 and 4).
Reads data/early/reads.json. Writes summary_early.json (aggregates only), data/early.json (one row per unit, no page text, no name
servers, no final address of a parked page), section_early.html and, when landmark reads exist, data/landmarks.json and
section_landmarks.html. A unit's state is its latest read. Repeat reads count only toward the repeat floor."""
import os, sys, json, math, time, html, re, urllib.parse, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); sys.path.insert(0, H); sys.path.insert(0, ROOT)
import heuremen_kit as K, linkstate as L
D = os.path.join(ROOT, 'data'); STORE = os.path.join(D, 'early', 'reads.json')
ST = L.STATES
rows_by_g = {}
LABEL = {'LIVE_SAME': 'Answers, same as first capture', 'LIVE_CHANGED': 'Answers, changed', 'LIVE_NO_BASELINE': 'Answers, never captured',
         'REDIRECTED_ELSEWHERE': 'Sent to another domain', 'PARKED_OR_FOR_SALE': 'Parked or for sale', 'ROBOTS_DISALLOWED': 'robots.txt asks us not to read',
         'DEAD_DNS': 'Name no longer resolves', 'DEAD_CONNECT': 'No connection', 'DEAD_HTTP': 'HTTP error', 'TIMEOUT': 'Timed out',
         'NOTHING_RETURNED': 'Our checker failed'}
LIVE = ('LIVE_SAME', 'LIVE_CHANGED', 'LIVE_NO_BASELINE')
ERAS = {'ncsa': ['1993-1996'], 'dmoz': ['1996-2001', '2002-2008', '2009-2017', 'no capture before the dump'],
        'rfc': ['1993-1996', '1997-2001', '2002-2008', '2009-2017'], 'fedreg': ['1995-1996', '1997-2001', '2002-2008', '2009-2017'],
        'landmarks': ['1994-1996', '1997-2001', '2002-2008', '2009 and later'], 'suggested': ['suggested by readers']}
TITLE = {'ncsa': "NCSA What's New, 1993 to 1996", 'dmoz': 'The final Open Directory (DMOZ), March 2017', 'rfc': 'Addresses cited in RFCs, 1993 to 2017',
         'fedreg': 'Addresses in Federal Register documents, 1995 to 2017', 'landmarks': 'Landmarks of the early web', 'suggested': 'Suggested by readers'}
PERSONAL_PATH = re.compile(r'(~|/(people|users|user|staff|faculty|homes|home|members|personal|students|student)(/|$))', re.I)
PERSONAL_HOSTS = ('geocities.com', 'tripod.com', 'angelfire.com', 'fortunecity.com', 'xoom.com', 'homestead.com', 'blogspot.com', 'wordpress.com', 'livejournal.com')
PERSONAL_HOSTNAMES = ('members.aol.com', 'home.earthlink.net')

def dmoz_era(first):
    if not first or first[:8] >= '20170313': return 'no capture before the dump'
    y = int(first[:4])
    return '1996-2001' if y <= 2001 else ('2002-2008' if y <= 2008 else '2009-2017')

def era_of(u, last):
    if u['sample'] == 'dmoz':   # the era needs the first capture; until the archive answers, the unit is era pending, never "no capture"
        if not last or 'first_capture' not in last or (last.get('archive_err') and not last.get('first_capture')): return None
        return dmoz_era(last.get('first_capture'))
    return u.get('era')

def wil(k, n):   # 10 Nov (referee): kept at 6 places so the page rounds once
    lo, hi = K.wilson(k, n); return [round(k / n, 6) if n else None, round(lo, 6), round(hi, 6)]

def yrs(ts, t):   # 10 Nov (referee): years from the capture time (UTC) to the read, unrounded, so the page rounds once
    import calendar
    try: return (t - calendar.timegm(time.strptime((ts + '000000')[:14], '%Y%m%d%H%M%S'))) / (365.2425 * 86400)   # the capture's full UTC timestamp
    except (ValueError, TypeError): return None

def median_ci(xs):
    """Median with a distribution-free 95% interval from order statistics (exact binomial). None when n < 6."""
    xs = sorted(xs); n = len(xs)
    if not n: return None
    med = xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    if n < 6: return dict(n=n, median=round(med, 6), lo=None, hi=None)
    cdf, l = 0.0, 0
    for j in range(n + 1):
        cdf += math.comb(n, j) / 2 ** n
        if cdf > 0.025: l = j; break
    return dict(n=n, median=round(med, 6), lo=round(xs[max(l - 1, 0)], 6), hi=round(xs[min(n - l, n - 1)], 6))

def http_class(r):
    s = r.get('status'); w = r.get('why', '')
    if s in (404, 410): return '404 or 410'
    if s in (401, 403, 429): return '401, 403 or 429'
    if s and 300 <= s < 400 or 'redirect' in w.lower() or 'loop' in w.lower(): return 'redirect loop'
    if s and 400 <= s < 500: return 'other 4xx'
    if s and s >= 500: return '5xx'
    return 'other'

def cell(rows):
    c = collections.Counter(r['state'] for r in rows); n = len(rows)
    out = dict(read=n, counts={s: c[s] for s in ST}, shares={s: wil(c[s], n) for s in ST}, too_few=n < 30)
    dom = collections.Counter(r.get('regdom') or '' for r in rows)
    out['distinct_domains'] = len(dom); out['largest_domain_count'] = max(dom.values()) if dom else 0
    out['dead_http_split'] = dict(collections.Counter(http_class(r) for r in rows if r['state'] == 'DEAD_HTTP'))
    sims = [r['similarity'] for r in rows if r['state'] in ('LIVE_SAME', 'LIVE_CHANGED') and r.get('similarity') is not None]
    out['sensitivity'] = {'compared': len(sims), 'same_at_0.50': sum(1 for x in sims if x >= 0.5), 'same_at_0.80': sum(1 for x in sims if x >= 0.8), 'same_at_0.95': sum(1 for x in sims if x >= 0.95)}
    live = [r for r in rows if r['state'] in LIVE]
    hist = [r for r in live if r['state'] != 'LIVE_NO_BASELINE' and not r.get('archive_err')]
    yl = [yrs(r['unchanged_since'], r['t']) for r in hist if r.get('unchanged_since')]
    lm = []
    for r in live:
        if r.get('last_modified'):
            try:
                t = time.mktime(time.strptime(r['last_modified'][5:16], '%d %b %Y'))
                if r['t'] - t > 86400: lm.append(round((r['t'] - t) / (365.2425 * 86400), 2))
            except ValueError: pass
    out['unchanged'] = dict(live=len(live), live_with_history=len(hist), dated=len(yl), median_years=median_ci(yl),
                            ten_years=wil(sum(1 for y in yl if y >= 10), len(hist)) + [sum(1 for y in yl if y >= 10), len(hist)],
                            last_modified=median_ci(lm), changed_since_newest_version=sum(1 for r in hist if r.get('last_change') and r.get('unchanged_since') is None))
    return out

def shown(u):
    """Public form of an example address (PLAN.md note 6): scheme and host, the rest shortened, so no file or folder name reaches the page."""
    p = urllib.parse.urlsplit(u); rest = (p.path or '/') + ('?' + p.query if p.query else '')
    return '%s://%s/%s' % (p.scheme, p.netloc, '\u2026' if rest not in ('/', '') else '')

def personal(u):
    p = urllib.parse.urlsplit(u); h = (p.hostname or '').lower()
    return bool(PERSONAL_PATH.search(p.path or '')) or h in PERSONAL_HOSTNAMES or any(h == d or h.endswith('.' + d) for d in PERSONAL_HOSTS)

def public_row(uid, u, last):
    r = dict(id=uid, sample=u['sample'], era=era_of(u, last), url=u['url'], state=last['state'] if last else None)
    for k in ('month', 'year', 'rfc', 'doc', 'date', 'family', 'sources', 'first_listed', 'name'):
        if k in u: r[k] = u[k]
    if last:
        r.update(t=last['t'], status=last.get('status'), first_capture=last.get('first_capture'), last_change=last.get('last_change'),
                 unchanged_since=last.get('unchanged_since'), similarity=last.get('similarity'), tls_invalid=last.get('tls_invalid'))
        if last['state'] == 'DEAD_HTTP': r['http_class'] = http_class(last)
        if last['state'] == 'REDIRECTED_ELSEWHERE': r['ends_on'] = L.regdom(urllib.parse.urlsplit(last.get('final') or '').hostname or '')
        if last['state'] == 'PARKED_OR_FOR_SALE': r['signal_families'] = sorted({s.split(':')[0] for s in last.get('park_signals') or []})
    return r

def build(store):
    units = store['units']; rows_by = collections.defaultdict(list); pub = []
    for uid, u in units.items():
        last = u['reads'][-1] if u['reads'] else None
        if not last: continue
        pub.append(public_row(uid, u, last))
        e = era_of(u, last); grp = (u['sample'], e, u.get('family'))
        rows_by[grp].append(last)
    global rows_by_g; rows_by_g = rows_by
    summ = dict(updated=time.strftime('%d %b %Y %H:%M UTC', time.gmtime()), samples={})
    last_gate = store['passes'][-1] if store.get('passes') else None
    summ['gate'] = 'passed' if last_gate and last_gate['passed'] else 'FAILED'
    for sname in ERAS:
        cols = {}
        for e in ERAS[sname]:
            fams = [None] if sname != 'rfc' else ['other', 'ietf']
            for fam in fams:
                rows = rows_by.get((sname, e, fam), [])
                if rows or sname != 'rfc': cols[e if fam is None else '%s|%s' % (e, fam)] = cell(rows)
        tot = [r for (s, e, f), rows in rows_by.items() if s == sname for r in rows]
        if not tot: continue
        summ['samples'][sname] = dict(title=TITLE[sname], read=len(tot), drawn=sum(1 for u in units.values() if u['sample'] == sname), cols=cols,
                                      era_pending=len(rows_by.get((sname, None, None), [])))
        # second ruler for every sample, defined after the data: each registered domain once (its first unit in draw order),
        # because addresses on one domain tend to live or die together and are not independent units
        bd = {}
        for colname in cols:
            e, fam = (colname.split('|') + [None])[:2]
            us = sorted([u for u in units.values() if u['sample'] == sname and u['reads'] and era_of(u, u['reads'][-1]) == e and (fam is None or u.get('family') == fam)], key=lambda u: u['key'])
            first = {}
            for u in us: first.setdefault(u['reads'][-1].get('regdom') or u['url'], u['reads'][-1])
            bd[colname] = cell(list(first.values()))
        summ['samples'][sname]['by_domain'] = bd
        if sname == 'fedreg':   # second ruler, defined after the data: documents that share a drawn address are not independent units
            byaddr, dup = {}, {}
            for e in ERAS[sname]:
                us = [u for u in units.values() if u['sample'] == 'fedreg' and u.get('era') == e and u['reads']]
                per = collections.Counter(u['url'] for u in us); one = {}
                for u in us: one.setdefault(u['url'], u['reads'][-1])
                byaddr[e] = cell(list(one.values())); dup[e] = dict(documents=len(us), distinct_addresses=len(per), largest_repeat=max(per.values()) if per else 0)
            summ['samples'][sname]['by_address'] = byaddr; summ['samples'][sname]['duplication'] = dup
    # repeat floor
    pairs = collections.Counter(); n_rep = 0
    for u in units.values():
        fv = next((r for r in u['reads'] if r['state'] != 'NOTHING_RETURNED'), None)
        if u.get('repeat') and fv:   # the second read is compared with the first valid read, the one it was timed from
            a, b = fv['state'], u['repeat']['state']; pairs[(a, b)] += 1; n_rep += 1
    flips = sum(v for (a, b), v in pairs.items() if a != b)
    summ['repeat_floor'] = dict(read_twice=n_rep, flips=flips, flip_share=wil(flips, n_rep), pairs={'%s -> %s' % k: v for k, v in sorted(pairs.items()) if k[0] != k[1]},
                                unchanged={k[0]: v for k, v in pairs.items() if k[0] == k[1]})
    by_s = collections.defaultdict(lambda: [0, 0])   # 10 Nov (resume): the same count per sample, item by item
    for u in units.values():
        fv = next((r for r in u['reads'] if r['state'] != 'NOTHING_RETURNED'), None)
        if u.get('repeat') and fv:
            by_s[u['sample']][0] += 1; by_s[u['sample']][1] += fv['state'] != u['repeat']['state']
    summ['repeat_floor']['by_sample'] = {k: dict(read_twice=v[0], flips=v[1], flip_share=wil(v[1], v[0]), eligible=sum(1 for u in units.values() if u['sample'] == k and u['key'][0] in '012')) for k, v in by_s.items()}
    # examples: six smallest keys per sample among read units, personal pages removed
    ex = {}
    for sname in ERAS:
        if sname in ('landmarks', 'suggested'): continue
        c = sorted((u['key'], uid) for uid, u in units.items() if u['sample'] == sname and u['reads'] and not personal(u['url']))
        ex[sname] = [public_row(uid, units[uid], units[uid]['reads'][-1]) for _, uid in c[:6]]
    summ['examples'] = ex
    hc = os.path.join(D, 'early', 'handcheck_parked.json')
    if os.path.exists(hc): summ['parked_handcheck'] = json.load(open(hc)).get('result')
    return summ, pub

def pct(x): return '' if x is None else ('%.1f%%' % (100 * x))
def esc(s): return html.escape(str(s), quote=True)
def fmt(n): return '{:,}'.format(n)

def table_states(s):
    cols = list(s['cols'].items())
    head = ''.join('<th>%s</th>' % esc(k.replace('|other', ', other hosts').replace('|ietf', ', IETF and IANA hosts').replace('-', ' to ')) for k, _ in cols)
    out = ['<table class="mtx"><thead><tr><th>State</th>%s</tr></thead><tbody>' % head]
    out.append('<tr><td>Addresses read</td>%s</tr>' % ''.join('<td class="n">%s%s</td>' % (fmt(c['read']), ' (too few to read as a share)' if c['too_few'] and c['read'] else '') for _, c in cols))
    for st in ST:
        tds = []
        for _, c in cols:
            k = c['counts'][st]; sh = c['shares'][st]
            tds.append('<td class="n">%s</td>' % (fmt(k) if c['too_few'] else '%s (%s [%s, %s])' % (fmt(k), pct(sh[0]), pct(sh[1]), pct(sh[2]))))
        out.append('<tr><td>%s</td>%s</tr>' % (esc(LABEL[st]), ''.join(tds)))
    out.append('</tbody></table>'); return ''.join(out)

def frag_early(summ):
    S = summ['samples']; P = []
    P.append('<section id="linkrot-early">')
    P.append('<h2>Beyond arXiv: early web links, standards and official documents</h2>')
    P.append('<p>The arXiv census above is one sample. Beside it we read random samples of addresses from the early web and from documents that cite the web: the monthly What&rsquo;s New column at NCSA from 1993 to 1996, the final Open Directory listing of March 2017, the reference sections of RFCs, and Federal Register documents. For each address the stated side is the address as it was listed or cited. The delivered side is what answers there today. Each sample was drawn with a public random seed after the rules were committed, and no address was chosen outside the draw.</p>')
    P.append('<p>Every address gets exactly one state. It answers with the same content as its earliest capture in the Wayback Machine, answers with changed content, or answers with no capture to compare. It sends readers to a different domain. It shows a parking page or a sale listing. Its robots.txt asks automated readers not to read it, and we do not. Its name no longer resolves, it refuses the connection, it answers with an HTTP error, or it does not answer in time. When our own checker fails, the address reads as our failure and is read again on the next pass. It never counts as gone.</p>')
    for sname in ('ncsa', 'dmoz', 'rfc', 'fedreg'):
        if sname not in S: continue
        s = S[sname]; P.append('<h3>%s</h3>' % esc(s['title'])); P.append(table_states(s))
        note = {'ncsa': 'Addresses from every monthly column page the Wayback Machine holds, gopher, ftp and telnet links left out, read in a random draw.',
                'dmoz': 'Columns group addresses by the year of their earliest capture in the Wayback Machine. The last column holds addresses with no capture before the directory closed.',
                'rfc': 'Only reference sections count. Later RFCs cite other RFCs through the RFC Editor&rsquo;s own site, so addresses on IETF and IANA hosts are drawn and shown apart. The earliest era holds very few cited addresses.',
                'fedreg': 'One address drawn from each document drawn. Federal Register documents published in each era that contain a web address.'}[sname]
        P.append('<p class="bench-note">%s Each cell gives the count and its share of the addresses read in that column, with a Wilson 95%% interval in brackets. A column with fewer than 30 addresses read shows counts only.</p>' % note)
        if s.get('era_pending'):   # 10 Nov (resume): units with no era yet (our checker failed before the archive gave a first capture) are counted here, never dropped
            pend = collections.Counter(r['state'] for (sn, e, f), rows in rows_by_g.items() if sn == sname and e is None for r in rows)
            P.append('<p class="bench-note">%s of the %s addresses drawn have no column yet, because our checker failed before their earliest capture could be looked up: %s. They are read again on the next pass.</p>' % (
                fmt(s['era_pending']), fmt(s['drawn']), ', '.join('%s read as %s' % (fmt(v), esc(LABEL[k]).lower()) for k, v in pend.most_common())))
        if sname == 'fedreg' and s.get('by_address'):
            d = s['duplication']
            P.append('<p class="bench-note">Documents can share a drawn address. %s So documents are not independent units, and the table below counts each distinct address once (defined after the data).</p>' % ' '.join(
                'In %s, %s documents give %s distinct addresses, and the most frequent address was drawn from %s of them.' % (e.replace('-', ' to '), fmt(v['documents']), fmt(v['distinct_addresses']), fmt(v['largest_repeat'])) for e, v in d.items() if v['documents']))
            P.append(table_states(dict(cols=s['by_address'])).replace('<th>State</th>', '<th>State, each distinct address once</th>').replace('Addresses read', 'Distinct addresses read'))
        if sname == 'rfc' and s.get('by_domain'):
            big = max((c['largest_domain_count'], k) for k, c in s['cols'].items())
            P.append('<p class="bench-note">Addresses on one domain tend to live or die together. In the column %s, a single registered domain holds %s of %s addresses. The table below counts each registered domain once, taking its first address in draw order (defined after the data).</p>' % (
                esc(big[1].replace('|other', ', other hosts').replace('|ietf', ', IETF and IANA hosts').replace('-', ' to ')), fmt(big[0]), fmt(s['cols'][big[1]]['read'])))
            P.append(table_states(dict(cols=s['by_domain'])).replace('<th>State</th>', '<th>State, each registered domain once</th>').replace('Addresses read', 'Domains read'))
        split = collections.Counter()
        for c in s['cols'].values(): split.update(c['dead_http_split'])
        if split:
            names = {'404 or 410': 'answered 404 or 410', '401, 403 or 429': 'answered 401, 403 or 429', 'other 4xx': 'answered another 4xx status', '5xx': 'answered a 5xx status', 'redirect loop': 'ended on a redirect answer (a loop, more than 10 redirects, or a redirect we could not follow)', 'other': 'gave another non-2xx answer'}
            items = ['%s %s' % (fmt(v), names.get(k, k)) for k, v in sorted(split.items(), key=lambda x: -x[1])]
            joined = items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]
            P.append('<p class="bench-note">Of the HTTP errors, %s. A 401, 403 or 429 can be a refusal of automated readers rather than a missing page.</p>' % joined)
    P.append('<h3>How long since the content changed</h3>')
    P.append('<table class="mtx"><thead><tr><th>Sample and era</th><th>Answering</th><th>Unchanged since a dated version</th><th>Median years, 95% interval</th><th>Unchanged 10 years or more, share, Wilson 95% interval</th></tr></thead><tbody>')
    for sname in ('ncsa', 'dmoz', 'rfc', 'fedreg'):
        if sname not in S: continue
        for e, c in S[sname]['cols'].items():
            u = c['unchanged']
            if not u['live']: continue
            m = u['median_years']; mt = '' if not m else ('%.1f' % m['median'] + (' [%.1f, %.1f]' % (m['lo'], m['hi']) if m.get('lo') is not None else ' (too few for an interval)'))
            t = u['ten_years']; tt = '' if not u['live_with_history'] else '%s of %s (%s [%s, %s])' % (fmt(t[3]), fmt(t[4]), pct(t[0]), pct(t[1]), pct(t[2]))
            P.append('<tr><td>%s, %s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (esc(S[sname]['title'].split(',')[0]), esc(e.replace('|other', ', other hosts').replace('|ietf', ', IETF and IANA hosts').replace('-', ' to ')), fmt(u['live']), fmt(u['dated']), mt, tt))
    P.append('</tbody></table>')
    P.append('<p class="bench-note">A version is dated by the first capture of the newest distinct content the Wayback Machine holds. A page counts as unchanged since that version only when its bytes today equal it. Pages whose bytes differ changed after the archive&rsquo;s newest version, so they carry no date. The ten-year share is of answering pages the archive holds a history for. The median interval is the distribution-free 95% interval from order statistics.</p>')
    rf = summ.get('repeat_floor', {})
    if rf.get('read_twice'):
        fs = rf['flip_share']
        P.append('<h3>Repeat floor</h3><p>Every address whose draw key begins with 0, 1 or 2 is read a second time, at least three hours after its first read, by the same code and against the same stored capture. Each sample is the smallest keys of a much larger list, so this takes every address in the NCSA, Open Directory and Federal Register samples and most of the RFC sample%s. %s of %s addresses read twice changed state between the two reads (%s, Wilson 95%% interval %s to %s). A difference between two columns smaller than this is within what a second read alone can move.</p>' % (', and about three in sixteen landmarks, whose keys span the whole range' if (rf.get('by_sample') or {}).get('landmarks') else '', fmt(rf['flips']), fmt(rf['read_twice']), pct(fs[0]), pct(fs[1]), pct(fs[2])))
        bs = rf.get('by_sample') or {}
        if bs:
            P.append('<table class="mtx"><thead><tr><th>Sample</th><th>Read twice</th><th>Changed state</th><th>Share, Wilson 95% interval</th><th>Still due a second read</th></tr></thead><tbody>')
            for sname in ('ncsa', 'dmoz', 'rfc', 'fedreg', 'landmarks'):
                b = bs.get(sname)
                if not b or not b['read_twice']: continue
                P.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s [%s, %s]</td><td class="n">%s</td></tr>' % (esc(TITLE[sname].split(',')[0]), fmt(b['read_twice']), fmt(b['flips']), pct(b['flip_share'][0]), pct(b['flip_share'][1]), pct(b['flip_share'][2]), fmt(b['eligible'] - b['read_twice'])))
            P.append('</tbody></table>')
        if rf.get('pairs'):
            items = sorted(rf['pairs'].items(), key=lambda x: -x[1])
            P.append('<p class="bench-note">Still due counts addresses with a key beginning 0, 1 or 2 that have no second read yet, mostly because their first good read came in the latest pass. They are read again once three hours have passed since it. The table below gives the changes between the two reads, by pair of states.</p>')
            P.append('<table class="mtx"><thead><tr><th>First read</th><th>Second read</th><th>Addresses</th></tr></thead><tbody>' + ''.join('<tr><td>%s</td><td>%s</td><td class="n">%s</td></tr>' % (esc(LABEL[a.split(' -> ')[0]]), esc(LABEL[a.split(' -> ')[1]]), fmt(v)) for a, v in items) + '</tbody></table>')
    hc = summ.get('parked_handcheck')
    if hc:
        P.append('<h3>The parking detector, read in full</h3><p>%s</p>' % esc(hc['sentence']))
    ex = summ.get('examples', {})
    if any(ex.values()):
        P.append('<h3>Examples drawn at random</h3><p class="bench-note">The first addresses in draw order from each sample, after removing personal pages and personal hosting services. Each is shown as its host only, with the rest of the address shortened, and as text, not as a link.</p>')
        P.append('<table class="mtx"><thead><tr><th>Sample</th><th>Listed address</th><th>Era</th><th>State</th><th>First capture</th></tr></thead><tbody>')
        for sname in ('ncsa', 'dmoz', 'rfc', 'fedreg'):
            for r in ex.get(sname, []):
                fc = r.get('first_capture'); fc = '%s-%s-%s' % (fc[:4], fc[4:6], fc[6:8]) if fc else 'none'
                P.append('<tr><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(TITLE[sname].split(',')[0]), esc(shown(r['url'])), esc((r.get('era') or '').replace('-', ' to ')), esc(LABEL.get(r['state'], r['state'])), fc))
        P.append('</tbody></table>')
    P.append('<p class="meta">Rules, frames, states, the parking detector, the seed and the example draw were committed before the first address in these samples was read (PLAN.md, Addendum 3). Sources: the <a href="https://web.archive.org">Wayback Machine</a>, the <a href="https://www.rfc-editor.org">RFC Editor</a>, the <a href="https://www.federalregister.gov/developers/documentation/api/v1">Federal Register API</a> and the <a href="https://drand.love">drand</a> beacon for the seed. Updated %s.</p>' % esc(summ['updated']))
    P.append('</section>')
    out = '\n'.join(P) + '\n'
    if hc and not hc.get('trusted'):   # PLAN.md Addendum 3: the parked column carries the hand-check result beside it
        out = out.replace('<td>Parked or for sale</td>', '<td>Parked or for sale (the detector failed the full reading below)</td>')
    return out

def main():
    store = json.load(open(STORE)); summ, pub = build(store)
    json.dump(summ, open(os.path.join(ROOT, 'summary_early.json.tmp'), 'w'), indent=1); os.replace(os.path.join(ROOT, 'summary_early.json.tmp'), os.path.join(ROOT, 'summary_early.json'))
    early = [r for r in pub if r['sample'] not in ('landmarks', 'suggested')]
    json.dump(early, open(os.path.join(D, 'early.json.tmp'), 'w'), indent=1); os.replace(os.path.join(D, 'early.json.tmp'), os.path.join(D, 'early.json'))
    open(os.path.join(ROOT, 'section_early.html'), 'w').write(frag_early(summ))
    try:
        import landmarks_section; landmarks_section.write(store, summ, pub)
    except ImportError: pass
    print('early summary:', {k: v['read'] for k, v in summ['samples'].items()}, 'repeat floor', summ['repeat_floor']['read_twice'], 'gate', summ['gate'])

if __name__ == '__main__':
    main()
