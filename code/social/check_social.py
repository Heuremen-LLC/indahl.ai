#!/usr/bin/env python3
"""check_social.py: checks social.html against the section files and their summaries. Read only. Exit 1 on any FAIL.

A  Each cleared section_<key>.html sits in social.html byte for byte, once, in order, and the section and summary files still have the
   hashes that summary_social.json recorded at build time (a section changed after the build fails here).
B  Every number in the page outside the sections (headline, outcomes table, stamps, slot, footer lines) is found in a summary_<key>.json.
   The outcomes table is read cell by cell against paths written here, not taken from the builder. The builder's own list of numbers
   (summary_social.json "numbers") is resolved again, path by path.
C  Each section's outcome cells against its own summary: DSA outcome cells by class, the ad spend table by cycle, the TikTok decided cells.
D  Every number inside the sections is looked up in that section's summary, then among the sums and ratios of summary fields written out in
   derived() below, then in that section's data files (the rows the section was rendered from). A number found in none of them fails.
   A match is to half a unit of the last printed digit, as a value or as a percent. This is a lookup, not a recount: it shows every printed
   number exists in the section's own files, and the cell-by-cell recount of each section is its referee's page check. Dates, years,
   period labels and regulation numbers are not counted as numbers.
E  Headline rule: the headline comes from a cleared section whose gate passed, its numbers are the summary's decided rows that do not rest on
   a rule defined after the data, and no reading defined after the data is in it.
F  Bluesky: the slot says being read unless the build was run with --bluesky-cleared. This script opens nothing in bluesky/ unless
   summary_social.json says the section was placed.
G  Copy rules on the assembler's own text (hard) and on the whole page (semicolons hard, the rest printed for review).
H  Site gate pre-flight, read only: the tone scan, count scan and forbidden patterns that ledger/ship.sh runs, run on social.html. Hits are
   printed as SHIP BLOCKER and fail this script only with --gate, since they are about the ship gate and not about the numbers.

  python3 -I check_social.py [--list] [--gate]
"""
import os, re, sys, json, html, hashlib, bisect

H = os.path.dirname(os.path.abspath(__file__))
LIST = '--list' in sys.argv[1:]
OUTS = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED']; DECIDED = OUTS[:3]
# written here on purpose, apart from build_social.py: label on the page, outcome tally, row count, stamp, gate, the section's data files (published rows first)
CFG = {'dsa': ('EU moderation reports', 'outcomes', 'comparison_rows', 'updated_utc', 'gate_passed', ['dsa/public/dsa.json', 'dsa/public/dsa_automation_monthly.json', 'dsa/data/automation_period.json']),
       'adspend': ('Political ad spend', 'outcomes.cycle_rows.all', 'totals.cycle_rows', 'updated', 'gate_ok', ['adspend/data/adspend_public.json', 'adspend/data/adspend.json']),
       'tiktok': ('TikTok quarterly report', 'outcomes', 'rows', 'updated', 'gate_passed', ['tiktok/data/tiktok.json', 'tiktok/data/components.json'])}
if json.load(open(os.path.join(H, 'summary_social.json'), encoding='utf-8'))['sections'].get('bluesky', {}).get('status') == 'cleared':
    CFG['bluesky'] = ('Bluesky', 'outcomes', 'row_count', 'updated', 'gate_passed', ['bluesky/data/bsky.json'])
ORDER = ['dsa', 'adspend', 'tiktok']
fails, notes = [], []
def FAIL(tag, msg): fails.append(f'{tag}: {msg}'); print(f'  FAIL {tag}: {msg}')
def OK(tag, msg): print(f'  ok   {tag}: {msg}')
def get(d, path):
    for p in path.split('.'): d = d[p]
    return d
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def vis(h):
    t = re.sub(r'(?is)<script.*?</script>', ' ', h); t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t))

page = open(os.path.join(H, 'social.html'), encoding='utf-8').read()
SS = json.load(open(os.path.join(H, 'summary_social.json'), encoding='utf-8'))
main = page[page.index('<main class="wrap">') + len('<main class="wrap">'):page.index('</main>')]
SUM = {k: json.load(open(os.path.join(H, k, f'summary_{k}.json'), encoding='utf-8')) for k in ORDER}
FRAG = {k: open(os.path.join(H, k, f'section_{k}.html'), encoding='utf-8').read().strip('\n') for k in ORDER}
bsky_in = SS['sections'].get('bluesky', {}).get('status') == 'cleared'
if bsky_in:
    ORDER.append('bluesky'); SUM['bluesky'] = json.load(open(os.path.join(H, 'bluesky', 'summary_bluesky.json'), encoding='utf-8'))
    FRAG['bluesky'] = open(os.path.join(H, 'bluesky', 'section_bluesky.html'), encoding='utf-8').read().strip('\n')

# ---------------------------------------------------------------------------------------------- A  sections byte for byte
print('A  sections byte for byte')
pos = -1; outside = main
for k in ORDER:
    c = main.count(FRAG[k]); i = main.find(FRAG[k])
    if c != 1: FAIL('A', f'{k}: section file found {c} times in social.html (want 1)'); continue
    if i < pos: FAIL('A', f'{k}: out of order')
    pos = i; outside = outside.replace(FRAG[k], f'\n[[{k}]]\n')
    e = SS['sections'].get(k, {})
    for f, key in ((f'{k}/section_{k}.html', 'section_sha256'), (f'{k}/summary_{k}.json', 'summary_sha256')):
        if sha(os.path.join(H, f)) != e.get(key): FAIL('A', f'{f} changed since the build (hash differs from summary_social.json). Rebuild')
    else: OK('A', f'{k}: section in the page byte for byte ({len(FRAG[k]):,} chars), section and summary hashes as built')
n_sec = len(re.findall(r'<section id="(?!hl-slot|replies)', main))
if n_sec != len(ORDER) + (0 if bsky_in else 1): FAIL('A', f'{n_sec} content sections in main, want {len(ORDER) + (0 if bsky_in else 1)}')

# ---------------------------------------------------------------------------------------------- number tools
MONTH = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
def strip_dates(t):
    t = re.sub(r'\b\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}(?::\d{2})?)?\b', ' ', t)             # 2026-11-10 04:19
    t = re.sub(r'\b\d{4}-\d{2}\b', ' ', t)                                                # 2023-09
    t = re.sub(r'\b(?:19|20)\d{2}/\d{3,4}\b', ' ', t)                                    # Regulation (EU) 2024/2835, 2022/2065
    t = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', ' ', t)                                      # 6/8/2026 (a platform's own date)
    t = re.sub(r'\b\d{1,2} (?:to \d{1,2} )?' + MONTH + r'\b', ' ', t)                     # 9 November, 30 September
    t = re.sub(r'\b' + MONTH + r' \d{1,2}\b(?!,?\d)', ' ', t)
    t = re.sub(r'\b(?:19|20)\d{2}(?:H[12]|Q[1-4])?\b(?![,.]\d)', ' ', t)                  # years and period labels
    return t
TOK = re.compile(r'(?<![\w.,])\d[\d,]*(?:\.\d+)?(?![\w])')
def tokens(text):
    out = []
    for m in TOK.finditer(strip_dates(text)):
        s = m.group(0).rstrip(','); body = s.replace(',', '')
        if not re.fullmatch(r'\d+(\.\d+)?', body): continue
        d = len(body.split('.')[1]) if '.' in body else 0
        out.append((s, float(body), d))
    return out
class Leaves:
    def __init__(self, obj):
        xs = []
        def walk(o):
            if isinstance(o, bool) or o is None: return
            if isinstance(o, (int, float)): xs.append(abs(float(o)))
            elif isinstance(o, str):
                for _, v, _d in tokens(o): xs.append(v)
                for m in re.finditer(r'\d+(?:\.\d+)?', o): xs.append(float(m.group(0)))
            elif isinstance(o, dict):
                for k, v in o.items(): walk(k); walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(obj); self.a = sorted(set(xs)); self.b = sorted(set(100 * x for x in xs))
    @staticmethod
    def _near(arr, v, tol):
        i = bisect.bisect_left(arr, v - tol); return i < len(arr) and arr[i] <= v + tol
    def has(self, v, d):
        tol = 0.5 * 10 ** -d + 1e-9          # half a unit of the last printed digit (a whole number matches a leaf that rounds to it)
        return self._near(self.a, v, tol) or self._near(self.b, v, tol)
LSUM = {k: Leaves(SUM[k]) for k in ORDER}
def derived(k):
    """figures a section prints that are sums or ratios of its summary's leaves. Each formula is written here and worked from the summary."""
    s = SUM[k]; d = {}
    if k == 'adspend':
        c = s['match_gate']['counts']; sp = s['match_gate']['stated_spend']; f = s['match_gate']['unmatched_public_id_forms']
        d['matched advertisers = A_id + A_candidate_id + B_name'] = c['A_id'] + c['A_candidate_id'] + c['B_name']
        d['matched by ID = A_id + A_candidate_id'] = c['A_id'] + c['A_candidate_id']
        d['unmatched advertisers = us_advertisers - matched'] = s['google']['us_advertisers'] - (c['A_id'] + c['A_candidate_id'] + c['B_name'])
        d['unmatched stated spend = sum of unmatched_* stated_spend'] = sum(v for kk, v in sp.items() if kk.startswith('unmatched_'))
        d['tax ID or state registration only = EIN + state registration'] = f['EIN'] + f['state registration']
        assert d['unmatched advertisers = us_advertisers - matched'] == sum(v for kk, v in c.items() if kk.startswith('unmatched_'))
    if k == 'tiktok':
        for r in s['eu_rows']:
            if r['measure'] in ('videos_removed', 'automated_removals') and r.get('stated'):
                for g in (r.get('gap'), (r.get('defined_after_the_data') or {}).get('gap')):
                    for i, x in enumerate(g or []):
                        if x is not None: d[f'{r["quarter"]} {r["measure"]} gap {i} over stated, percent, {len(d)}'] = 100 * x / r['stated']
    if k == 'bluesky':
        # the year table: labels served and negations served per year, the sum of the summary's daily series [day, applied, negated, seq_used]
        for y in sorted({r[0][:4] for r in s['series']}):
            d[f'{y} labels served = sum of series applied'] = sum(r[1] for r in s['series'] if r[0][:4] == y)
            d[f'{y} negations served = sum of series negated'] = sum(r[2] for r in s['series'] if r[0][:4] == y)
    return d
DER = {k: derived(k) for k in ORDER}; LDER = {k: Leaves(list(DER[k].values())) for k in ORDER}

# ---------------------------------------------------------------------------------------------- B  numbers outside the sections
print('B  numbers outside the sections, against the summaries')
out_txt = vis(outside)
stamps = set(re.findall(r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}\b', out_txt))
known = {re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', str(get(SUM[k], CFG[k][3]))).group(0): k for k in CFG}
for s in sorted(stamps):
    if s not in known: FAIL('B', f'stamp {s} is in no summary')
if re.search(r'\b(?:19|20)\d{2}\b', re.sub(r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}\b', ' ', out_txt)): FAIL('B', 'a year or date outside the sections that is not a summary stamp')
bad = [s for s, v, d in tokens(out_txt) if not (v == 0 or any(L.has(v, d) for L in LSUM.values()))]
if bad: FAIL('B', f'numbers outside the sections found in no summary: {bad}')
else: OK('B', f'{len(tokens(out_txt))} numbers and {len(stamps)} stamps outside the sections, each found in a summary')
tab = re.search(r'(?s)<h2>Outcomes by section</h2>.*?<tbody>(.*?)</tbody>', outside)
if not tab: FAIL('B', 'outcomes table not found')
else:
    seen = set()
    for tr in re.findall(r'(?s)<tr>(.*?)</tr>', tab.group(1)):
        tds = [vis(x).strip() for x in re.findall(r'(?s)<td[^>]*>(.*?)</td>', tr)]
        k = next((k for k in CFG if CFG[k][0] == tds[0]), None)
        if k is None:
            if tds[0] == 'Bluesky' and not bsky_in and tds[1:] == ['Being read']: continue
            if bsky_in and tds[0] == 'Bluesky': notes.append('B: the Bluesky row of the outcomes table has no reader in check_social.py yet'); continue
            FAIL('B', f'outcomes table: unknown row {tds[0]!r}'); continue
        seen.add(k); oc = get(SUM[k], CFG[k][1])
        want = [f'{oc.get(o, 0):,}' for o in OUTS] + [re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', str(get(SUM[k], CFG[k][3]))).group(0) + ' UTC']
        if tds[2:] != want: FAIL('B', f'outcomes table {k}: page {tds[2:]} summary {want}')
        elif sum(oc.values()) != get(SUM[k], CFG[k][2]): FAIL('B', f'{k}: outcomes do not add up to the summary row count')
        else: OK('B', f'outcomes table {k}: five outcome cells and the stamp equal the summary, and add up to {get(SUM[k], CFG[k][2]):,} rows')
    if seen != set(CFG): FAIL('B', f'outcomes table is missing {sorted(set(CFG) - seen)}')
for e in SS.get('numbers', []):
    k = e['file'].split('/')[0]; v = get(SUM[k], e['path'])
    if v != e['value'] or (isinstance(v, int) and f'{v:,}' != e['text']): FAIL('B', f'builder number {e["text"]} is not {e["file"]} {e["path"]} ({v!r})')
    if e['text'] not in out_txt: FAIL('B', f'builder number {e["text"]} ({e["path"]}) is not on the page outside the sections')
OK('B', f'{len(SS.get("numbers", []))} numbers the builder recorded resolve to the same summary paths') if not any(f.startswith('B') for f in fails) else None

# ---------------------------------------------------------------------------------------------- C  section outcome cells against the summaries
print('C  section outcome cells against their summaries')
f = FRAG['dsa']; oc = SUM['dsa']['outcomes']
got = {o: len(re.findall(r'<td class="o-%s"' % o, f)) for o in OUTS[:4]}
if got != {o: oc.get(o, 0) for o in OUTS[:4]}: FAIL('C', f'dsa: outcome cells {got} summary {oc}')
else: OK('C', f'dsa: outcome cells by class equal the summary ({got})')
f = FRAG['adspend']; t = re.search(r'(?s)<h3>Outcomes by cycle</h3>.*?<tbody>(.*?)</tbody>', f)
okc = bool(t)
for tr in (re.findall(r'(?s)<tr>(.*?)</tr>', t.group(1)) if t else []):
    tds = [vis(x).strip() for x in re.findall(r'(?s)<td[^>]*>(.*?)</td>', tr)]; cyc = SUM['adspend']['outcomes']['cycle_rows'].get(tds[0])
    if not cyc or tds[1:] != [f'{cyc[o]:,}' for o in OUTS]: FAIL('C', f'adspend cycle {tds[0]}: page {tds[1:]} summary {cyc}'); okc = False
allc = SUM['adspend']['outcomes']['cycle_rows']
if any(sum(allc[c][o] for c in allc if c != 'all') != allc['all'][o] for o in OUTS): FAIL('C', 'adspend: cycles do not add up to all'); okc = False
if okc: OK('C', 'adspend: outcomes by cycle equal the summary, and the cycles add up to the all-cycles tally')
f = FRAG['tiktok']; s = SUM['tiktok']; ph = s.get('eu_rows_outcomes_defined_after_the_data', {})
cells = {o: len(re.findall(r'<td>%s</td>' % w, f)) for o, w in zip(DECIDED, ('Above', 'Below', 'Consistent'))}
com = {o: sum(1 for r in s['eu_rows'] if r['outcome'] == o) for o in DECIDED}
if any(com.values()) or any(s['outcomes'].get(o) for o in DECIDED): FAIL('C', f'tiktok: a committed row is decided ({com}); the builder and this check assume none')
want = {o: ph.get(o, 0) for o in DECIDED}
# a quarter's row can print in more than one table (the latest-quarter table repeats it), so the page may hold more cells than rows, never fewer and never a kind the summary lacks
if any((cells[o] > 0) != (want[o] > 0) or cells[o] < want[o] for o in DECIDED): FAIL('C', f'tiktok: decided cells {cells}, summary readings defined after the data {want}')
else: OK('C', f'tiktok: no committed row decided. Decided cells on the page {cells} are the readings defined after the data {want}')

# ---------------------------------------------------------------------------------------------- D  numbers inside the sections
print('D  numbers inside the sections: summary, then the data files of the section')
unexplained = {}
for k in ORDER:
    if k not in CFG: notes.append(f'D: {k} has no rows file named in check_social.py, numbers looked up in its summary only'); rowsL = None
    else: rowsL = Leaves([json.load(open(os.path.join(H, f_), encoding='utf-8')) for f_ in CFG[k][5]])
    tk = tokens(vis(FRAG[k])); a = b = c_ = 0; un = []
    for s_, v, d in tk:
        if LSUM[k].has(v, d): a += 1
        elif any(abs(abs(x) - v) <= 0.5 * 10 ** -d + 1e-9 for x in DER[k].values()): c_ += 1
        elif rowsL and rowsL.has(v, d): b += 1
        else: un.append(s_)
    unexplained[k] = un
    print(f'  {"FAIL" if un else "ok  "} D: {k}: {len(tk):,} numbers. {a:,} in the summary, {c_:,} worked from summary fields by a formula in this script, {b:,} in its data files ({", ".join(CFG[k][5]) if k in CFG else "none"}), {len(un):,} in neither')
    if un:
        u = sorted(set(un), key=un.index); print('         in neither: ' + ', '.join(u if LIST else u[:25]) + ('' if LIST or len(u) <= 25 else f' ... ({len(u)} distinct, --list prints all)'))
        fails.append(f'D: {k}: {len(un)} numbers in neither')

# ---------------------------------------------------------------------------------------------- E  headline rule
print('E  headline rule')
hl = SS.get('headline'); slot = re.search(r'(?s)<section id="hl-slot"[^>]*><div class="hl-big">(.*?)</div><p class="hl-line">(.*?)</p></section>', main)
if not hl:
    if slot: FAIL('E', 'the page has a headline block and summary_social.json has no headline')
    else: OK('E', 'no headline (no section qualifies)')
else:
    k = hl['section']
    if not slot or html.unescape(slot.group(1)) != hl['big'] or html.unescape(slot.group(2)) != hl['line']: FAIL('E', 'headline on the page is not the headline in summary_social.json')
    if not main.startswith('<section id="hl-slot"'): FAIL('E', 'the headline block is not first in <main> (build_site.py takes it from there)')
    if SS['sections'][k]['status'] != 'cleared' or get(SUM[k], CFG[k][4]) is not True: FAIL('E', f'headline section {k} is not cleared or its gate did not pass')
    if k == 'adspend':
        dec = SUM[k]['outcomes']['decided_cycle_rows']; allc = SUM[k]['outcomes']['cycle_rows']['all']
        want_big = f'{dec["robust_id_no_flags"]:,} of {SUM[k]["totals"]["cycle_rows"]:,}'
        if hl['big'] != want_big: FAIL('E', f'headline {hl["big"]!r}, decided rows not resting on a rule after the data {want_big!r}')
        if dec['n'] != sum(allc[o] for o in DECIDED): FAIL('E', 'adspend decided rows are not above plus below plus consistent')
        if not (0 < dec['robust_id_no_flags'] <= dec['n'] - max(dec['unseen_rule_sensitive'], dec['timing_sensitive'])): FAIL('E', 'adspend robust count is outside what the decided rows allow')
        allowed = {dec['robust_id_no_flags'], SUM[k]['totals']['cycle_rows'], dec['n'], allc['CANNOT_TELL']}
    else: FAIL('E', f'headline from {k}: check_social.py has no rule written for that section'); allowed = set()
    extra = [s_ for s_, v, d in tokens(hl['big'] + ' ' + hl['line']) if v not in allowed]
    if extra: FAIL('E', f'headline carries numbers outside its decided-row counts: {extra}')
    if re.search(r'(?i)tiktok|bluesky|after the data, (?:above|below)', hl['big'] + hl['line']): FAIL('E', 'headline names a section with no decided committed row')
    if not any(f.startswith('E') for f in fails): OK('E', f'headline "{hl["big"]}" is from {k}: decided rows that do not rest on a rule defined after the data, gate passed. No reading defined after the data in it')
for k in ORDER:
    e = SS['sections'][k]
    if e.get('headline_eligible') and e.get('decided_not_resting_on_a_rule_after_the_data') in (None, 0): FAIL('E', f'{k} marked headline eligible with no such rows')

# ---------------------------------------------------------------------------------------------- F  Bluesky slot
print('F  Bluesky slot')
slot_b = re.search(r'(?s)<section id="social-bluesky">(.*?)</section>', main)
if bsky_in: OK('F', 'Bluesky section placed (built with --bluesky-cleared)') if 'being read' not in out_txt.lower() else FAIL('F', 'Bluesky is placed and the page still says being read')
elif not slot_b or 'being read' not in vis(slot_b.group(1)) or tokens(vis(slot_b.group(1))): FAIL('F', 'the Bluesky slot is missing, does not say being read, or carries a number')
elif SS['sections'].get('bluesky', {}).get('status') != 'being read': FAIL('F', 'summary_social.json does not mark Bluesky as being read')
else: OK('F', 'slot says being read, carries no number, and summary_social.json marks it being read. Nothing in bluesky/ was opened')

# ---------------------------------------------------------------------------------------------- G  copy rules
print('G  copy rules')
title = re.search(r'<title>(.*?)</title>', page).group(1); desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', page).group(1))
heads_all = [vis(h).strip() for h in re.findall(r'(?is)<h[1-3][^>]*>(.*?)</h[1-3]>', page)]
heads_own = [vis(h).strip() for h in re.findall(r'(?is)<h[1-3][^>]*>(.*?)</h[1-3]>', page.replace(main, outside))]
lead = out_txt.split('On this page:')[0]; lead = lead.split('Division: HERMES', 1)[-1]
own = [(r';', 'semicolon'), (r'\b(AI|artificial intelligence|Claude|language model|LLM|assistant)\b', 'AI statement'), (r'\bbecause\b|\bdue to\b|\bcaused?\b(?! for)', 'cause word'),
       (r'\bI\b|\bmy\b', 'first person singular'), (r'\bIndahl\b', 'Indahl in copy'), (r'\b(wrong|error|errors|mistake|misleading|false|failed to|careless)\b', 'judgement word'),
       (r'\bindependent review', 'independent reviewer')]
h = 0
for pat, name in own:
    for txt, where in ((out_txt, 'assembler text'), (title, 'title'), (desc, 'description')):
        for m in re.finditer(pat, txt):
            if name == 'cause word' and 'name no cause' in txt[max(0, m.start() - 12):m.end() + 4]: continue
            FAIL('G', f'{name} in the {where}: ...{txt[max(0, m.start() - 60):m.end() + 60]}...'); h += 1
for x in heads_own + [title]:
    if re.search(r'\d', x): FAIL('G', f'digit in a title or heading of the assembler: {x!r}'); h += 1
if tokens(lead): FAIL('G', f'number in the lead: {tokens(lead)}'); h += 1
if 'Heuremen LLC' not in title: FAIL('G', 'title does not say Heuremen LLC'); h += 1
if not h: OK('G', f'assembler text, title and description: no semicolon, AI statement, cause word, first person singular or judgement word. No digit in its {len(heads_own)} headings, the title or the lead')
allv = vis(main); sc = [allv[max(0, m.start() - 50):m.end() + 20] for m in re.finditer(';', allv)]
if sc: FAIL('G', f'{len(sc)} semicolons in the visible page text, first: ...{sc[0]}...')
else: OK('G', 'no semicolon in the visible text of the whole page')
for pat, name in ((r'\b(AI|artificial intelligence|LLM)\b', 'AI term inside a section (review: must be a platform\'s own category or quote)'),):
    c = {}
    for k in ORDER:
        n_ = len(re.findall(pat, vis(FRAG[k])))
        if n_: c[k] = n_
    if c: notes.append(f'G: {name}: {c}')
hd = [x for x in heads_all if x not in heads_own and re.search(r'\d', x)]
if hd: notes.append(f'G: section headings with a digit (review: dates and periods, not counts of our own things): {hd}')

# ---------------------------------------------------------------------------------------------- H  site gate pre-flight (read only)
print('H  site gate pre-flight: the scans ledger/ship.sh runs on every indahl.ai page, run here on social.html')
gate_hits = []
try:
    import importlib.util as _u, collections as _c
    SB = os.path.expanduser('~/bones-forge/heuremen-specbook')
    def _mod(n):
        sp = _u.spec_from_file_location(n, os.path.join(SB, n + '.py')); m = _u.module_from_spec(sp); sp.loader.exec_module(m); return m
    P = os.path.join(H, 'social.html')
    for kind, hit in _mod('tone_scan').scan(P): gate_hits.append(f'tone {kind}: {hit.lower()}')
    for rel, hit, ctx in _mod('count_scan').scan([P]): gate_hits.append(f'count in a title, heading or label: {hit}')
    for f_ in json.load(open(os.path.join(SB, 'site_rules.json')))['forbid']:
        if f_['where'] in ('all', 'indahl.ai') and re.search(f_['pattern'], page): gate_hits.append(f'forbid {f_["rule"]}: {f_["why"]}')
    if re.search(r'(?i)\bby hand\b|\bhand[- ](?:read|check|count)|\bhand-?checked\b', page): gate_hits.append('wording: by hand')
    if re.search(r'(?i)\bflock', page): gate_hits.append('wording: flock')
    if gate_hits:
        for h_, c_ in _c.Counter(gate_hits).most_common(): print(f'  SHIP BLOCKER H: {c_} x {h_}')
        print('         the page would be refused by the site gate as it stands. See SHIP_PLAN.md, open items')
    else: OK('H', 'tone scan, count scan, forbidden patterns and wording: no hit')
except Exception as e_: notes.append(f'H: site gate scans could not be run here ({type(e_).__name__}: {e_})')
if gate_hits and '--gate' in sys.argv[1:]: fails.append(f'H: {len(gate_hits)} site gate hits')

print()
for n_ in notes: print('  note', n_)
tot_un = sum(len(v) for v in unexplained.values())
print(f'\ncheck_social: {"FAIL, " + str(len(fails)) + " failing" if fails else "PASS"}. Sections byte for byte: {len(ORDER)}. '
      f'Section numbers found in neither their summary nor their data files: {tot_un:,}.'
      + (f' Site gate pre-flight: {len(gate_hits)} hits, a ship blocker.' if gate_hits else ' Site gate pre-flight: no hit.'))
sys.exit(1 if fails else 0)
