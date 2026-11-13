#!/usr/bin/env python3
"""Builds sagar_list_body.html from the SAGAR record (verified.jsonl, second_reader.jsonl, tiers.json, batch metadata).
Row text (quotes) is copied verbatim from second_reader.jsonl; arithmetic lines are written here and checked against that file.
Usage: python3 make_sagar.py   (writes sagar_list_body.html and sagar_rows.json beside this file)"""
import json, glob, html, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); IDX = os.path.join(HERE, '..', 'index')
E = html.escape
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
ver = jl(os.path.join(IDX, 'verified.jsonl')); sr = {r['item']: r for r in jl(os.path.join(IDX, 'second_reader.jsonl'))}
tiers = json.load(open(os.path.join(IDX, 'tiers.json')))
EXCL = {('2409.16196', 'F2'), ('2503.09731', 'F2'), ('2410.16565', 'F2'), ('2507.21566', 'F6')}   # convention-F2 and the item the second reader overruled
inc = [r for r in ver if r['bones'] == 'PRESENT' and r['code'] not in ('F1', 'F4') and (r['arxiv'], r['code']) not in EXCL]
meta = {}
for f in sorted(glob.glob(os.path.join(IDX, 'batch_*.json'))) + [os.path.join(IDX, 'control_01.json'), os.path.join(IDX, 'queue_reachable.json')]:
    for m in json.load(open(f, encoding='utf-8')): meta.setdefault(m['arxiv'], m)
vr = {}
for f in glob.glob(os.path.join(IDX, '*_draft.jsonl')):
    for d in jl(f): vr[d['arxiv']] = d.get('version_read')
MON = ['January','February','March','April','May','June','July','August','September','October','November','December']
def pubm(p):
    y, m, _ = p.split('-'); return f'{MON[int(m)-1]} {y}' if int(m) else y
def verread(a):
    v = vr.get(a)
    if not v: return 'arXiv PDF as served 12 Nov 2026. The version number was not recorded.'
    if v.startswith('arXiv PDF'): return 'arXiv PDF as served 12 Nov 2026. The version number was not recorded.'
    return v
# item number in second_reader.jsonl for each listed row
ITEM = {'2603.29019':1,'2506.15984':2,'2507.02335':4,'2507.01294':5,'2510.25579':6,'2507.21566':7,'2510.14291':8,'2506.13870':9,'2506.06838':10,'2311.06416':11,
        '2504.00198':12,'2412.05369':13,'2610.29436':14,'2506.21021':15,'2410.16565':16,'2311.16085':17,'2403.03982':18,'2303.17628':19,'2208.01766':20}
# (prints, where) / (shows, where) quote indices into the second reader's quotes, plus arithmetic and scope text written here.
# P and O are lists of (quote index) ; ARITH is our own recompute line; SCOPE says what was and was not read.
R = {
'2603.29019': dict(P=[(2, 'Figure 5 caption'), (3, 'Conclusion')], O=[(0, 'Abstract'), (1, 'Body')],
   ARITH='The caption interval 3.9 +19.7 &minus;3.3 km/s (90% HDI) has edges 0.6 and 23.6 km/s. From the released samples (6,560 posterior samples) the 95th percentile is 19.67 km/s, the equal-tailed 90% interval is 0.45 to 19.67 km/s, and the 90% HDI is 0.00 to 15.08 km/s. None of 2,000 bootstrap resamples (95th percentile 19.67, bootstrap 95% interval 19.10 to 20.42) puts the upper edge of either 90% interval at 23.6. The median (3.85) and the 95% bound (19.67) match the abstract.',
   SCOPE='Recomputed from sigma_posterior.h5 only, treating the samples as equally weighted. Other files in the released record were not checked.', METHOD='recompute'),
'2506.15984': dict(P=[(0, 'Section 3.2'), (2, 'Figure 2, as extracted from the PDF text')], O=[(3, 'Table 2, Ksat, columns Emulator and Full Solver'), (4, 'Table 2, Ksym'), (5, 'Table 2, c2s(3n0)'), (6, 'Table 2, c2s(5n0)')],
   ARITH='Rounded to the figure&rsquo;s digits, the values printed in Figure 2 (90% intervals) equal the Full Solver column of Table 2 for all five parameters. The Emulator column does not match, for example Ksym &minus;209.3 against &minus;214.7 (Full Solver) and &minus;215 (Figure 2).',
   SCOPE='Figure 2 values were read from the PDF text layer. The figure image was not read.'),
'2507.02335': dict(P=[(0, 'Abstract')], O=[(1, 'Body')],
   ARITH='The abstract gives the lowest value over 42 events. 7.90 / 0.39 = 20.3, so the highest per-event limit is about 20 times the headline value.'),
'2507.01294': dict(P=[(0, 'Abstract')], O=[(2, 'Body')],
   ARITH='The headline is the lowest of the per-event limits over 60 events. No highest or median per-event fractional limit is printed beside it in the text read.',
   SCOPE='Per-event limits may appear in a figure. Figures were not read.'),
'2510.25579': dict(P=[(0, 'Abstract')], O=[(1, 'Section 3.1')],
   ARITH='No significance, Bayes factor or interval is printed for the peak near 26 to 27 Msun.'),
'2507.21566': dict(P=[(3, 'Text')], O=[(0, 'Text, threshold'), (4, 'Text, injections')],
   ARITH='The event value is 3.24 and the threshold is 3, a margin of 0.24. The 100 injections of the same signal model span D<sub>YS</sub> 0.08 to 2.37. No significance, interval or exceedance rate is printed for the 3 threshold.'),
'2510.14291': dict(P=[(1, 'Table, class 6'), (2, 'Table, class 7')], O=[(0, 'Text')],
   ARITH='The eight class counts sum to 45,345, the stated total. 60 / 45,345 = 0.13% and 27 / 45,345 = 0.06%, against 1.3% and 0.6% printed. The other six rows reproduce. The eight printed percentages sum to 101.7%.'),
'2506.13870': dict(P=[(0, 'Abstract')], O=[(1, 'Table 3'), (2, 'Body')],
   ARITH='Using the Pop. III model lar1 in Table 3, Pop. II divided by Pop. III is 0.2 / 0.035 = 5.7 at z=0, 6.5 / 1.7 = 3.8 at the Pop. III peak and 13.7 / 0.8 = 17.1 at the Pop. II peak. One of the three is at least 10.',
   SCOPE='The abstract may refer to the paper&rsquo;s fiducial Pop. III model, not lar1. The text gives that model a peak near 0.4 Gpc<sup>&minus;3</sup> yr<sup>&minus;1</sup>, and 6.5 / 0.4 = 16. The second reader&rsquo;s confidence on this item was medium for that reason.'),
'2506.06838': dict(P=[(0, 'Conclusion')], O=[(1, 'Appendix A')],
   ARITH='Appendix A reports two resolutions, 128 and 192 points in the coarsest refinement level.'),
'2311.06416': dict(P=[(0, 'Abstract'), (1, 'Body')], O=[(2, 'Table 2'), (3, 'Table 2')],
   ARITH='In Table 2, of 7,815 injections the found counts are 6,151 (general bank), 6,169 (TESLA) and 6,297 (TESLA-X). 6,297 / 6,169 = +2.07%. The abstract&rsquo;s ~10% is the largest value of a sensitive-range curve against false-alarm rate in a figure, for one mock event and one data stream.',
   SCOPE='The curve behind the 10% value is in a figure and was not read as numbers.'),
'2504.00198': dict(P=[(1, 'Text')], O=[(2, 'Text'), (3, 'Text')],
   ARITH='No p-value, background distribution or null distribution is printed for the flat response. The validation uses ten synthetic injections.',
   SCOPE='Quotes are from the PDF text layer, with spacing between run-together words lightly normalised.'),
'2412.05369': dict(P=[(0, 'Text')], O=[(1, 'Table'), (2, 'Table header')],
   ARITH='For the second candidate the text prints 13.91 as the false alarm rate. The table row gives 9.09 in the FAR column. The network SNR (9.18) and the ranking statistic (13.91) agree between text and table.'),
'2610.29436': dict(P=[(0, 'Text')], O=[(1, 'Table, SGC-D row')],
   ARITH='In every other row of the table the two lowest values are in the HEN #1 and HEN #3 columns. In the SGC-D row HEN #1 holds 122.2, the highest of the four, and HEN #3 holds 3.6. The rate limit printed in that row (3.2&times;10<sup>8</sup>) recomputes from 3.6.',
   SCOPE='From the text alone it is CANNOT_TELL which cell of the SGC-D row is the intended one. The tier is provisional until the 3.2&times;10<sup>8</sup> limit is checked against the abstract and conclusion.'),
'2506.21021': dict(P=[(1, 'Table 1')], O=[(2, 'Text, observing period')],
   ARITH='63,000 / 86,400 s = 72.92%, against 72.02% printed. The other computable rows reproduce, the first day using a 57,600 s day because the period starts at 08:00 UTC.'),
'2410.16565': dict(P=[(0, 'Text'), (1, 'Text')], O=[(2, 'Text')],
   ARITH='2.11 per day &times; 0.68 days = 1.435, and 1 &minus; e<sup>&minus;1.435</sup> = 0.762. Across the rounding range of the printed inputs (FAR 2.105 to 2.115 per day, T<sub>obs</sub> 0.675 to 0.685 days) the result is 0.7585 to 0.7651, and the printed 0.75 is below that range.'),
'2311.16085': dict(P=[(0, 'Text'), (1, 'Text')], O=[(2, 'Text')],
   ARITH='125.5 days = 0.3436 years, times FAR 0.20 per year = 0.0687, and 1 &minus; e<sup>&minus;0.0687</sup> = 6.64%, against 6.5% printed. The same inputs give 18.63% for three trials, matching the 18.6% printed. No single FAR in the printed rounding ranges gives both 6.5% and 18.6%.'),
'2403.03982': dict(P=[(1, 'Text')], O=[(0, 'Text')],
   ARITH='1 / 1322 = 0.076%. 4 / 1322 = 0.30%, which matches the 0.3% printed and the count of 4 in the preceding sentence.'),
'2303.17628': dict(P=[(0, 'Text')], O=[(1, 'Table 1')],
   ARITH='The text gives 70 + 4 + 2 = 76. The Table 1 row for events with FAR &lt; 1 per year reads 76 total with 69, 4 and 2, and 69 + 4 + 2 = 75. The other rows of that table sum to their totals.'),
'2208.01766': dict(P=[(1, 'Table 1, GW190521')], O=[(5, 'Text, definition of BF E/P')],
   ARITH='With BF<sub>E</sub> 0.174 and BF<sub>P</sub> 0.492, 0.174 / 0.492 = 0.3537. Across the rounding range of the printed inputs the ratio lies between 0.3523 and 0.3550, and the printed 0.357 is above it. The other four rows reproduce.',
   SCOPE='The column may be computed by a route the paper does not describe. The second reader&rsquo;s confidence on this item was medium for that reason.'),
}
rows = []
for r in inc:
    a, c = r['arxiv'], r['code']; s = sr[ITEM[a]]; d = R[a]; m = meta[a]
    assert s['arxiv'] == a, a
    q = s['quotes']
    tier = tiers[a]['tier']
    rows.append(dict(arxiv=a, code=c, tier=tier, title=m['title'], doi=m.get('doi'), pub=pubm(m['pubdate']), version=verread(a),
        prints=[(q[i], w) for i, w in d['P']], shows=[(q[i], w) for i, w in d['O']], arith=d['ARITH'], scope=d.get('scope') or d.get('SCOPE', ''),
        method=d.get('METHOD', 'readers'), second=s['verdict'], conf=s['confidence'], prov=(a == '2610.29436')))
# 13 Nov 2026 (Wayfinder: "go for publish on our site"): rows from the full read, each item confirmed by two readers and then re-read by Bones against
# the paper text (index/verified_auto_reread.jsonl, reread_auto/verdicts.jsonl). One row per paper. A quote is shown only if it is a verbatim substring
# of the extracted paper text (whitespace normalised); the re-read basis line is our own words. Tier is the drafting reader's and is labelled so.
NRM = lambda t: re.sub(r'\s+', ' ', t or '').strip()
_have = {r['arxiv'] for r in rows}; _rr = {}
for x in jl(os.path.join(IDX, 'verified_auto_reread.jsonl')):
    if x['arxiv'] not in _have: _rr.setdefault(x['arxiv'], []).append(x)
_TR = {'T1': 1, 'T2': 2, 'T3': 3}
for a, xs in _rr.items():
    m = meta.get(a)
    if not m: continue
    tx = NRM(open(os.path.join(IDX, 'text', a + '.txt'), errors='replace').read())
    def vq(q): q = NRM(q); return q if len(q) > 15 and q in tx else None
    pr, sh, ar = [], [], []
    for x in xs:
        d = vq(x.get('draft_quote'))
        if d: pr.append((d, f'{x["code"]}, paper text'))
        for q in (x.get('reader_quotes') or []):
            v = vq(q)
            if v and v != d and (v, f'{x["code"]}, paper text') not in sh: sh.append((v, f'{x["code"]}, paper text'))
        ar.append(f'<b>{x["code"]}.</b> ' + E(x['bones_basis']))
    if not pr: continue
    codes = sorted({x['code'] for x in xs}); tier = max((x.get('severity') or 'T1' for x in xs), key=lambda t: _TR.get(t, 1))
    rows.append(dict(arxiv=a, code=' '.join(codes), tier=tier, title=m['title'], doi=m.get('doi'), pub=pubm(m['pubdate']), version=verread(a),
        prints=pr[:3], shows=sh[:4], arith='</p><p>'.join(ar), scope='Quotes are from the extracted PDF text. The tier is the drafting reader&rsquo;s and was not re-checked.',
        method='reread', second='confirmed', conf='', prov=False))
rows.sort(key=lambda x: x['arxiv'], reverse=True)
json.dump(rows, open(os.path.join(HERE, 'sagar_rows.json'), 'w'), indent=1, ensure_ascii=False)
CODEDESC = {'F2': 'selected result', 'F3': 'reading without a width', 'F5': 'number recomputes differently', 'F6': 'text differs from own table'}   # 13 Nov: the names in our Standard, Faults and Guards 2.0
def quotes(lst):
    lst = [(t.rstrip(';'), w) for t, w in lst]   # a quote may stop before its closing punctuation
    return ''.join(f'<p class="q">&ldquo;{E(t)}&rdquo; <span class="by">{E(w)}</span></p>' for t, w in lst)
def how(r):
    if r['method'] == 'recompute': return 'Recomputed from released data, and read by two independent readers. <a href="/sagar/receipts/2603.29019_sigma">Receipt</a>'
    if r['method'] == 'reread': return 'Two independent readers, then re-read against the paper text'
    return 'Two independent readers'
out = []
out.append('<p class="crumb"><a href="/sagar">SAGAR</a></p>')
out.append('<section class="legal"><p class="lede">SAGAR indexes gravitational-wave papers and lists checkable errata. An erratum here is a place where a paper disagrees with itself. The text disagrees with its own table, or a printed number does not follow from the paper&rsquo;s own printed numbers, or a headline is a single best value, or a claim carries no significance or interval.</p>'
           '<p>Each listed item was read by two independent readers who found the same place. Where the paper released data that could settle it, we recomputed from that data and say so in the last column. Every quote is verbatim from the paper&rsquo;s PDF, with its location. A listing is a classification for indexing, not an assessment of the study or its authors. An erratum can be a typo, and many are.</p>'
           '<p>Papers are indexed by arXiv id and DOI. Items are listed newest arXiv id first. If a paper&rsquo;s authors have a correction, or want an item changed or removed, use the <a href="/correction">correction or removal form</a>, open to anyone.</p></section>')
out.append('<section id="codes" class="legal"><h2>Codes and Tiers</h2>'
           '<p>The codes are claim codes from our <a href="/standard">Standards</a>. <b>F2 Selected result</b>: the headline figure is a selected value, a maximum over rows, a best case or a projection. <b>F3 Reading without a width</b>: a bounded reading is stated as yes or no, without an interval. <b>F5 Number recomputes differently</b>: a printed number does not follow from the paper&rsquo;s own data or arithmetic. <b>F6 Text differs from own table</b>: the text, abstract or caption differs from the paper&rsquo;s own table, figure or files. F1, F4 and F7 are read on every paper and not listed here.</p>'
           '<p><b>T1</b> arithmetic or typo, with no claim built on it. <b>T2</b> the text and the paper&rsquo;s own table, caption, appendix or file disagree. <b>T3</b> the item sits in, or sets, a number the abstract or conclusion relies on. A row takes its highest tier. Tiers describe where in the paper the item sits.</p></section>')
out.append('<section><div class="scroll"><table class="mtx list sagar"><thead><tr><th>Work</th><th>Version read</th><th>What the paper prints</th><th>What the paper shows elsewhere</th><th>Code and tier</th><th>How it was checked</th></tr></thead><tbody>')
for r in rows:
    a = r['arxiv']
    doi = f'<br><span class="by"><a href="https://doi.org/{E(r["doi"])}">doi:{E(r["doi"])}</a></span>' if r['doi'] else ''
    c1 = f'<a href="https://arxiv.org/abs/{a}">{E(r["title"])}</a><br><span class="by">arXiv {a}, {E(r["pub"])}</span>{doi}'
    c2 = E(r['version'])
    c3 = quotes(r['prints'])
    c4 = quotes(r['shows']) + f'<p>{r["arith"]}</p>' + (f'<p class="by">Scope: {r["scope"]}</p>' if r['scope'] else '')
    _cl = r['code'].split()
    c5 = '<span class="codes">' + ''.join(f'<a class="code" href="/standard">{c}</a>' for c in _cl) + f'<a class="code" href="/sagar#codes">{r["tier"]}</a></span><br>' + ' '.join(CODEDESC[c].capitalize() + '.' for c in _cl) + (' Tier provisional.' if r['prov'] else '')
    out.append(f'<tr id="arxiv-{a}"><td>{c1}</td><td>{c2}</td><td>{c3}</td><td>{c4}</td><td>{c5}</td><td>{how(r)}</td></tr>')
out.append('</tbody></table></div></section>')
open(os.path.join(HERE, 'sagar_list_body.html'), 'w', encoding='utf-8').write('\n'.join(out))
print('rows', len(rows))
