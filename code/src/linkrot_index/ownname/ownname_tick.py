#!/usr/bin/env python3
"""ownname_tick.py: "Our own name" (PLAN.md Addendum 3, sample N1). Rerunnable, no timers.
Every indahl.<ending> on the fixed list is read by the same rules as every other link (early/linkstate.py, first capture and change
history for every row). Registration: RDAP through the IANA bootstrap file, keyless, read only for registered or not and the expiry
date. Where the bootstrap file lists no RDAP service, registration reads from DNS delegation (NS records), which shows no expiry.
Nothing about a registrant, owner or contact is read into our files: the RDAP answer is reduced to two fields in memory.
Writes data/ownname.json and section_ownname.html. indahl.ai is listed first, the rest in alphabetical order of the ending."""
import os, sys, json, time, html, fcntl, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); sys.path.insert(0, os.path.join(ROOT, 'early')); sys.path.insert(0, ROOT)
import linkstate as L, gate as G, heuremen_kit as K
ENDINGS = ['ai', 'com', 'net', 'org', 'io', 'co', 'dev', 'app', 'us', 'uk', 'co.uk', 'de', 'no', 'se', 'dk', 'fi', 'is', 'nl', 'be', 'at', 'ch', 'eu',
           'fr', 'it', 'es', 'pl', 'ca', 'au', 'nz', 'info', 'biz', 'me', 'xyz', 'tech', 'online', 'site', 'store', 'cloud', 'tv', 'cc']
D = os.path.join(ROOT, 'data'); CACHE = os.path.join(D, 'ownname_cache'); OUT = os.path.join(D, 'ownname.json')
LABEL = {'LIVE_SAME': 'Answers, same as first capture', 'LIVE_CHANGED': 'Answers, changed', 'LIVE_NO_BASELINE': 'Answers, never captured',
         'REDIRECTED_ELSEWHERE': 'Sends readers to another domain', 'PARKED_OR_FOR_SALE': 'Parked or for sale', 'ROBOTS_DISALLOWED': 'robots.txt asks us not to read',
         'DEAD_DNS': 'Name does not resolve', 'DEAD_CONNECT': 'No connection', 'DEAD_HTTP': 'HTTP error', 'TIMEOUT': 'Timed out', 'NOTHING_RETURNED': 'Our checker failed'}

def bootstrap():
    p = os.path.join(CACHE, 'iana_rdap_dns.json')
    if not os.path.exists(p) or time.time() - os.path.getmtime(p) > 7 * 86400:
        os.makedirs(CACHE, exist_ok=True)
        raw = urllib.request.urlopen(urllib.request.Request('https://data.iana.org/rdap/dns.json', headers={'User-Agent': L.UA}), timeout=30).read()
        open(p + '.tmp', 'wb').write(raw); os.replace(p + '.tmp', p)
    m = {}
    for tlds, urls in json.load(open(p))['services']:
        for t in tlds: m[t] = urls[0] if urls[0].endswith('/') else urls[0] + '/'
    return m

def rdap_min(domain, boot):
    """Registered or not and the expiry date, nothing else. Returns dict(source, registered, expiry) or a failure note."""
    tld = domain.rsplit('.', 1)[1]; base = boot.get(tld)
    if not base:
        r = L.doh(domain, 'NS')
        if r is None: return dict(source='DNS', registered=None, expiry=None, note='resolver unreachable')
        st, ans = r   # NOERROR or SERVFAIL: the parent zone delegates the name. NXDOMAIN: it does not.
        return dict(source='DNS', registered=(st in (0, 2)) if st in (0, 2, 3) else None, expiry=None)
    for attempt in range(3):
        try:
            time.sleep(1.5)
            d = json.loads(urllib.request.urlopen(urllib.request.Request(base + 'domain/' + domain, headers={'User-Agent': L.UA, 'Accept': 'application/rdap+json'}), timeout=30).read())
            exp = next((e.get('eventDate') for e in d.get('events', []) if e.get('eventAction') == 'expiration'), None)
            return dict(source='RDAP', registered=True, expiry=exp[:10] if exp else None)
        except urllib.error.HTTPError as e:
            if e.code == 404: return dict(source='RDAP', registered=False, expiry=None)
            if e.code in (429, 500, 502, 503, 504): time.sleep(10); continue
            return dict(source='RDAP', registered=None, expiry=None, note='RDAP answered %s' % e.code)
        except Exception as e:
            time.sleep(5)
    return dict(source='RDAP', registered=None, expiry=None, note='RDAP unreachable')

def years_text(rec):
    st = rec['state']
    if not rec.get('first_capture') and not rec.get('last_change'): return 'no capture'
    if st in ('LIVE_SAME', 'LIVE_CHANGED', 'LIVE_NO_BASELINE'):
        if rec.get('unchanged_since'): return '%.1f' % L.years_since(rec['unchanged_since'], rec['t'])
        if rec.get('last_change'): return "changed since the archive's newest version"
        return 'no capture'
    if rec.get('last_change'): return '%.1f' % L.years_since(rec['last_change'], rec['t'])
    return 'no capture'

def main():
    lock = open(os.path.join(D, 'ownname.lock'), 'w')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('ownname: another run holds the lock'); return
    if not K.plan_committed(os.path.join(ROOT, 'PLAN.md')): print('ownname: PLAN.md not committed, refusing to read'); return
    ok, rows = G.run()
    if not ok: print('ownname: gate FAILED', [r for r in rows if r[1] != r[2]]); return
    boot = bootstrap(); out = []; evidence = {}
    order = ['ai'] + sorted(e for e in ENDINGS if e != 'ai')
    for e in order:
        dom = 'indahl.' + e
        rec = L.check('http://%s/' % dom, first='all', history='all')
        reg = rdap_min(dom, boot)
        out.append(dict(domain=dom, state=rec['state'], parked=rec['state'] == 'PARKED_OR_FOR_SALE', park_signal_families=sorted({s.split(':')[0] for s in rec.get('park_signals') or []}),
                        first_capture=rec.get('first_capture'), last_change=rec.get('last_change'), unchanged_since=rec.get('unchanged_since'), years_since_change=years_text(rec),
                        registered=reg.get('registered'), registration_source=reg['source'], expiry=reg.get('expiry'), registration_note=reg.get('note'), t=rec['t']))
        evidence[dom] = dict(why=rec['why'], status=rec.get('status'), final=rec.get('final'), title=rec.get('title'), snippet=rec.get('snippet'), signals=rec.get('park_signals'), ns=rec.get('ns'))
        print(dom, rec['state'], reg, flush=True)
    doc = dict(updated=time.strftime('%d %b %Y %H:%M UTC', time.gmtime()), gate='passed', rows=out)
    json.dump(doc, open(OUT + '.tmp', 'w'), indent=1); os.replace(OUT + '.tmp', OUT)
    os.makedirs(CACHE, exist_ok=True); json.dump(evidence, open(os.path.join(CACHE, 'evidence_private.json'), 'w'), indent=1)   # for the hand-check only, never published
    write_fragment(doc)

def write_fragment(doc, expiry=True, name='section_ownname.html'):
    e = lambda s: html.escape(str(s), quote=True)
    P = ['<section id="linkrot-ownname">', '<h2>Our own name</h2>',
         '<p>Our name is indahl.ai. We read every indahl domain by the same rules as every other link, our own included.</p>',
         '<table class="mtx"><thead><tr><th>Domain</th><th>Answers</th><th>Parked or for sale</th><th>Years since the content last changed</th><th>Registered</th>%s</tr></thead><tbody>' % ('<th>Expiry date</th>' if expiry else '')]
    for r in doc['rows']:
        reg = 'not read' if r['registered'] is None else ('yes' if r['registered'] else 'no')
        if r['registration_source'] == 'DNS' and r['registered'] is not None: reg += ' (DNS)'
        ex = ('<td>%s</td>' % e(r['expiry'] or ('not published' if r['registered'] else ''))) if expiry else ''
        P.append('<tr><td>%s</td><td>%s</td><td>%s</td><td class="n">%s</td><td>%s</td>%s</tr>' % (e(r['domain']), e(LABEL.get(r['state'], r['state'])), 'yes' if r['parked'] else 'no',
                 e(r['years_since_change']), e(reg), ex))
    P.append('</tbody></table>')
    P.append('<p class="bench-note">Each address is read at http://indahl.&lt;ending&gt;/ with the same states, parking detector and robots.txt rule as the samples above. Years since the content last changed come from the newest distinct version the Wayback Machine holds. For a domain that answers today the years count only when today&rsquo;s page is byte for byte that version. %s</p>' % (
        'Registered and expiry come from the registry&rsquo;s RDAP service. Where a registry offers none, registered reads from DNS delegation, marked DNS, which cannot show an expiry date.' if expiry else
        'Registered comes from the registry&rsquo;s RDAP service. Where a registry offers none, it reads from DNS delegation, marked DNS.'))
    P.append('<p class="meta">The ending list was fixed before the first read (PLAN.md, Addendum 3). Updated %s.</p>' % e(doc['updated']))
    P.append('</section>')
    open(os.path.join(ROOT, name), 'w').write('\n'.join(P) + '\n')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fragment':
        d = json.load(open(OUT)); write_fragment(d); write_fragment(d, expiry=False, name='section_ownname_noexpiry.html')
    else: main()
