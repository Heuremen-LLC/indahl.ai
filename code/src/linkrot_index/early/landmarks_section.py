"""landmarks_section.py: data/landmarks.json and section_landmarks.html for the landmarks sample (PLAN.md Addendum 4).
Called by early_summary.py. The public table names each site read, with its state, years since its content last changed and its first
200 capture. No owner data, no prices, no commentary, and a parked or for-sale site is shown as text, never as a link."""
import os, json, html, collections
import early_summary as S, linkstate as L
ROOT = S.ROOT; D = S.D
SRC = {'wikipedia': 'Wikipedia list', 'webby': 'Webby winner', 'picks': 'Yahoo! Picks or Cool Site of the Day', 'suggested by readers': 'suggested by readers'}

def years(r):
    if not r: return ''
    st = r['state']
    if st in S.LIVE:
        if r.get('unchanged_since'): return '%.1f' % S.yrs(r['unchanged_since'], r['t'])
        if r.get('last_change'): return 'changed since the archive&rsquo;s newest version'
        return 'no capture'
    if r.get('last_change'): return '%.1f' % S.yrs(r['last_change'], r['t'])
    return 'no capture' if r.get('first_capture') is None and 'first_capture' in r else ''

def fc(r):
    v = (r or {}).get('first_capture')
    if v: return '%s-%s-%s' % (v[:4], v[4:6], v[6:8])
    return 'none' if r and 'first_capture' in r and not r.get('archive_err') else 'not read yet'

def write(store, summ, pub):
    units = store['units']
    rows = [r for r in pub if r['sample'] in ('landmarks', 'suggested')]
    lm = [(uid, u) for uid, u in units.items() if u['sample'] in ('landmarks', 'suggested') and u['reads']]
    if not lm: return
    data = []
    for uid, u in sorted(lm, key=lambda x: x[1]['key']):
        r = u['reads'][-1]
        data.append(dict(site=u.get('name'), address=u['url'], sample=u['sample'], era=u.get('era'), first_listed=u.get('first_listed'), sources=u.get('sources'),
                         state=r['state'], years_since_change=years(r).replace('&rsquo;', "'"), first_capture=r.get('first_capture'), last_change=r.get('last_change'), read=r['t']))
    sp = os.path.join(D, 'landmarks', 'sample_landmarks.json'); fr = json.load(open(sp)) if os.path.exists(sp) else {}
    sg = os.path.join(D, 'landmarks', 'sample_suggested.json'); sgd = json.load(open(sg)) if os.path.exists(sg) else {}
    by_src = {}
    for src in ('wikipedia', 'webby', 'picks'):
        rr = [units[uid]['reads'][-1] for uid, u in lm if u['sample'] == 'landmarks' and src in (u.get('sources') or [])]
        if rr: by_src[src] = S.cell(rr)
    doc = dict(updated=summ['updated'], frame_count=fr.get('frame_count'), read=sum(1 for _, u in lm if u['sample'] == 'landmarks'),
               suggested_in_rule=sgd.get('in_rule'), suggested_not_in_rule=sgd.get('not_in_rule'),
               by_era=summ['samples'].get('landmarks', {}).get('cols'), by_source=by_src, rows=data)
    json.dump(doc, open(os.path.join(D, 'landmarks.json.tmp'), 'w'), indent=1); os.replace(os.path.join(D, 'landmarks.json.tmp'), os.path.join(D, 'landmarks.json'))
    e = lambda s: html.escape(str(s), quote=True)
    P = ['<section id="linkrot-landmarks">', '<h2>Landmarks of the early web</h2>',
         '<p>Famous sites of the 1990s and 2000s, taken by rule from public lists: the Webby Award winners of 1997 to 2008, the Yahoo! Picks and Cool Site of the Day columns as the Wayback Machine holds them, and Wikipedia&rsquo;s List of Internet phenomena from 2004 to 2010 and today. A site counts when a list points at the front page of a domain of its own. Each is read by the same rules as every other address on this page. The table names every site read so far, in the order of the random draw.</p>']
    if 'landmarks' in summ['samples']:
        P.append(S.table_states(summ['samples']['landmarks']))
        P.append('<p class="bench-note">Columns group sites by the year a list first named them. Each cell gives the count and its share of the sites read in that column, with a Wilson 95%% interval in brackets. A column with fewer than 30 sites read shows counts only.%s</p>' % (
            ' The frame holds %s sites and %s have been read so far, in draw order.' % (S.fmt(doc['frame_count']), S.fmt(doc['read'])) if doc.get('frame_count') else ''))
    P.append('<details><summary>Every site read so far, in draw order</summary>')
    P.append('<table class="mtx"><thead><tr><th>Site</th><th>First listed</th><th>Listed by</th><th>State</th><th>Years since the content last changed</th><th>First capture</th></tr></thead><tbody>')
    for uid, u in sorted(lm, key=lambda x: (x[1]['sample'] != 'landmarks', x[1]['key'])):
        r = u['reads'][-1]
        P.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="n">%s</td><td>%s</td></tr>' % (
            e(u.get('name') or u['url']), e(u.get('first_listed') or ''), e(', '.join(SRC.get(x, x) for x in (u.get('sources') or []))), e(S.LABEL.get(r['state'], r['state'])), years(r), fc(r)))
    P.append('</tbody></table></details>')
    if sgd.get('not_in_rule') or sgd.get('in_rule'):
        got = sum(1 for _, u in lm if u['sample'] == 'suggested')
        nir = sgd.get('not_in_rule') or []; ir = sgd.get('in_rule') or []
        txt = ('Readers named %s before the list rule was written. %s' % (', '.join(nir + ir), 'None of them comes out of the rule.' if not ir else '%s %s out of the rule.' % (', '.join(ir), 'comes' if len(ir) == 1 else 'come')))
        txt += ' Sites that do not come out of the rule are read by the same rules in rows marked suggested by readers and are kept out of the rates above.'
        if got < len(nir): txt += ' The read in draw order has reached %s of them so far.' % got
        P.append('<p class="bench-note">%s</p>' % e(txt))
    P.append('<p class="bench-note">Coverage: every Webby winners page for 1997 to 2008, every Yahoo! Picks weekly page, every Cool Site of the Day monthly page from August 1994 to November 2019, and Wikipedia&rsquo;s list in monthly versions from May 2004 to January 2010 and today. Yahoo! Picks one-day pages for 672 days between November 2004 and January 2008 were not read in this version of the list.</p>')
    P.append('<p class="bench-note">Years since the content last changed come from the newest distinct version the Wayback Machine holds. For a site that answers today they count only when today&rsquo;s page is byte for byte that version. First capture is the earliest 200 capture of the address.</p>')
    P.append('<p class="meta">The list rule was committed before any landmark was read (PLAN.md, Addendum 4). Updated %s.</p>' % e(summ['updated']))
    P.append('</section>')
    out = '\n'.join(P) + '\n'
    hc = summ.get('parked_handcheck')
    if hc and not hc.get('trusted'):   # PLAN.md Addendum 3: the parked column carries the hand-check result beside it
        out = out.replace('<td>Parked or for sale</td>', '<td>Parked or for sale (the detector failed the full reading above)</td>')
    open(os.path.join(ROOT, 'section_landmarks.html'), 'w').write(out)
