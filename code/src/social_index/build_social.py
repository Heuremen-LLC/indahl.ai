#!/usr/bin/env python3
"""build_social.py: the assembled SOCIAL page (staging). Writes social.html and summary_social.json in this folder.

What it does
- Reads each cleared section's section_<key>.html and summary_<key>.json and places the section on the page as it is, byte for byte.
  The assembler changes no section text and prints no number of its own: every number outside the sections (the headline, the
  outcomes table, the scored stamps) is read from a summary_<key>.json by a path that is written to summary_social.json ("numbers").
- Bluesky: a slot that says the section is being read. The Bluesky folder is opened ONLY when this script is run with
  --bluesky-cleared, and then section_bluesky.html and summary_bluesky.json must both exist. Without the flag nothing in bluesky/ or
  bluesky_referee/ is read or listed, whatever is in there.
- Headline: drawn only from rows that read ABOVE, BELOW or CONSISTENT and do not rest on a rule defined after the data. A section gives a
  headline only if its summary counts those rows (HEADLINE_READERS). Rows that are CANNOT_TELL or NOTHING_RETURNED, and readings
  defined after the data, never give one. If no section qualifies the page ships without a headline block.
- Head, header/nav, footer and tab bar are copied from indahl-ai/launch.html as they are (as wiki_index/build_page.py does). Only the
  page's own title, description, canonical URL and structured data are changed. indahl-ai/build_site.py takes the <main> of
  social.html at ship (see SHIP_PLAN.md), so the nav, division line, footer and reference code come from page().

Nothing is published by this script. Run check_social.py after it.
  python3 -I build_social.py                    three cleared sections, Bluesky slot "being read"
  python3 -I build_social.py --bluesky-cleared  after the Bluesky referee says ship
"""
import os, re, sys, json, html, time, hashlib

H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser('~/bones-forge/indahl-ai/launch.html')
E = lambda s: html.escape(str(s), quote=True)
BLUESKY = '--bluesky-cleared' in sys.argv[1:]

TITLE = 'SOCIAL | Platform Reports Against the Filings | Heuremen LLC'
HERO = '<b class="ac">SOCIAL</b> &middot; Platform Reports Against the Filings'
DESC = ('SOCIAL: what large platforms state about their own conduct, read against public filings that cover the same activity. '
        'EU moderation reports against the DSA Transparency Database, Google\'s political ad library against FEC filings, '
        'TikTok\'s quarterly report against its EU filings, and Bluesky\'s transparency report against its signed label stream.')
FEED = '/social/summary.json'
OUTS = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED']
DECIDED = ['ABOVE', 'BELOW', 'CONSISTENT']

# key, folder, nav label, what one row is, path of the outcome tally in the summary, path of the row count, path of the scored stamp
SECTIONS = [
    dict(key='dsa', label='EU moderation reports', row='A platform, a half-year and a measure',
         outcomes='outcomes', rows='comparison_rows', stamp='updated_utc', gate='gate_passed', req13='req13'),
    dict(key='adspend', label='Political ad spend', row='A matched committee, or group of committees, and an election cycle',
         outcomes='outcomes.cycle_rows.all', rows='totals.cycle_rows', stamp='updated', gate='gate_ok', req13='outcomes.req13_cycle'),
    dict(key='tiktok', label='TikTok quarterly report', row='A quarter and a measure, for the EU total or for one market',
         outcomes='outcomes', rows='rows', stamp='updated', gate='gate_passed', req13='req13_all'),
]
BLUESKY_SEC = dict(key='bluesky', label='Bluesky', row='A figure in Bluesky\'s transparency report and a year',
                   outcomes='outcomes', rows='row_count', stamp='updated', gate='gate_passed', req13='req13')

def sha(b): return hashlib.sha256(b).hexdigest()
def get(d, path):
    for p in path.split('.'): d = d[p]
    return d

NUMBERS = []          # every number the assembler prints outside the sections: text as printed, value, summary file, path
def num(key, summ, path):
    v = get(summ, path)
    assert isinstance(v, int) and not isinstance(v, bool), f'{key} {path}: not a whole number ({v!r})'
    t = f'{v:,}'
    NUMBERS.append(dict(text=t, value=v, file=f'{key}/summary_{key}.json', path=path))
    return t
def stamp(key, summ, path):
    """the scored stamp as the summary holds it, YYYY-MM-DD HH:MM, printed with UTC"""
    s = str(get(summ, path)); m = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})( UTC)?$', s)
    assert m, f'{key} {path}: stamp {s!r} is not YYYY-MM-DD HH:MM'
    NUMBERS.append(dict(text=m.group(1), value=s, file=f'{key}/summary_{key}.json', path=path))
    return m.group(1) + ' UTC'

def req13_text(key, summ, path):
    """12 Nov 2026, Faults and Guards 2.0 REQ-13: the NOTHING_RETURNED count, then the CANNOT_TELL share split by reason, every number read from the section's summary by a recorded path."""
    r = get(summ, path); sp = ', '.join(f'{num(key, summ, path + ".cannot_tell_by_reason." + k)} {k}' for k in sorted(r['cannot_tell_by_reason'])) or 'none'
    return f'{num(key, summ, path + ".nothing_returned")} NOTHING_RETURNED. CANNOT_TELL {num(key, summ, path + ".cannot_tell")} of {num(key, summ, path + ".n_readings")} ({sp}).'
def load(sec):
    k = sec['key']; d = os.path.join(H, k)
    hb = open(os.path.join(d, f'section_{k}.html'), 'rb').read(); sb = open(os.path.join(d, f'summary_{k}.json'), 'rb').read()
    frag = hb.decode('utf-8').strip('\n')
    m = re.match(r'<section id="([a-z0-9-]+)"(?: class="[a-z0-9 -]+")?>', frag)   # Bluesky's section carries class="social-section"
    assert m and frag.endswith('</section>') and frag.count('<section') == 1, f'{k}: section file is not one <section id=...> block'
    assert '<h1' not in frag and '<main' not in frag and '<script' not in frag, f'{k}: section file carries page chrome or a script'
    return dict(sec, frag=frag, anchor=m.group(1), summ=json.loads(sb), section_sha256=sha(hb), summary_sha256=sha(sb))

secs = [load(s) for s in SECTIONS]
S = {s['key']: s for s in secs}
bsky = load(BLUESKY_SEC) if BLUESKY else None

# ------------------------------------------------------------------------------------------------ headline (decided rows only)
def headline_adspend(s):
    """Rows that read above, below or consistent and whose outcome does not turn on the timing band, on the itemization rule set after the
    data, on a name match or on a note. The summary counts them (outcomes.decided_cycle_rows.robust_id_no_flags)."""
    summ = s['summ']; dec = summ['outcomes']['decided_cycle_rows']; allc = summ['outcomes']['cycle_rows']['all']
    assert dec['n'] == sum(allc[o] for o in DECIDED), 'adspend: decided rows do not add up to above, below and consistent'
    if not dec['robust_id_no_flags']: return None
    big = f'{num("adspend", summ, "outcomes.decided_cycle_rows.robust_id_no_flags")} of {num("adspend", summ, "totals.cycle_rows")}'
    line = ('matched political committees and election cycles read above, below or consistent, on Google\'s stated election ad spend against the '
            'committee\'s FEC filings, with an outcome that holds under both timing bands, does not turn on the itemization rule set after the data, '
            'rests on an FEC ID match alone and carries no note. '
            f'In all {num("adspend", summ, "outcomes.decided_cycle_rows.n")} read above, below or consistent and '
            f'{num("adspend", summ, "outcomes.cycle_rows.all.CANNOT_TELL")} read cannot tell. For all cycle rows, {req13_text("adspend", summ, "outcomes.req13_cycle")}')
    return dict(big=big, line=line, section='adspend')
# A section without a reader here gives no headline. DSA: summary_dsa.json counts its decided rows but not which of them use no rule set
# after the data, so it has no reader. TikTok: no row is decided under its committed rules. Bluesky: add a reader once its summary is read.
HEADLINE_READERS = [('adspend', headline_adspend)]

headline = None
for k, fn in HEADLINE_READERS:
    s = S.get(k)
    if s and get(s['summ'], s['gate']) is True:
        n0 = len(NUMBERS); headline = fn(s)
        if headline: break
        del NUMBERS[n0:]
HL_NUMBERS = list(NUMBERS)

def decided_note(s):
    k, summ = s['key'], s['summ']; oc = get(summ, s['outcomes'])
    d = {o: oc.get(o, 0) for o in DECIDED}
    if k == 'adspend':
        dec = summ['outcomes']['decided_cycle_rows']
        return dict(decided_as_printed=d, decided_not_resting_on_a_rule_after_the_data=dec['robust_id_no_flags'], headline_eligible=True,
                    note='robust_id_no_flags: decided, same outcome on the second timing ruler, same outcome with unseen money counted in full '
                         '(the itemization rule set after the data), no name match in the tier, no flag')
    if k == 'tiktok':
        ph = summ.get('eu_rows_outcomes_defined_after_the_data', {})
        return dict(decided_as_printed=d, decided_not_resting_on_a_rule_after_the_data=sum(d.values()), headline_eligible=False,
                    defined_after_the_data_decided={o: ph[o] for o in DECIDED if ph.get(o)},
                    note='no row is decided under the committed rules. The readings defined after the data are a separate column and give no headline')
    if k == 'dsa':
        return dict(decided_as_printed=d, decided_not_resting_on_a_rule_after_the_data=None, headline_eligible=False,
                    note='summary_dsa.json does not count the decided rows that use no rule set after the data, so this section gives no headline')
    return dict(decided_as_printed=d, decided_not_resting_on_a_rule_after_the_data=None, headline_eligible=False, note='no headline reader for this section')

# ------------------------------------------------------------------------------------------------ page body
parts = []
parts.append('<p>Large platforms describe their own conduct in more than one public record. A report or a library gives totals. '
             'A regulator&rsquo;s database or a campaign finance file holds entries one by one. SOCIAL reads one public record against another '
             'that covers the same activity over the same period, and prints where the two agree as well as where they differ.</p>')
parts.append('<p>Each section below is one pair of records, with its own plan, rules, sources and data. Every row reads above, below, consistent '
             'or cannot tell, and every cannot tell carries one reason, STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE or NO_INTERVAL_FORMABLE. A row where one side holds no figure reads cannot tell with the reason NO_INTERVAL_FORMABLE. NOTHING_RETURNED is the status of a failed read of a source and is not an outcome. A reading that uses a rule set after the data says so '
             'on its row or in its column. We measure gaps and name no cause.</p>')
nav = [f'<a href="#{E(s["anchor"])}">{E(s["label"])}</a>' for s in secs]
nav.append(f'<a href="#{E(bsky["anchor"]) if bsky else "social-bluesky"}">{E(BLUESKY_SEC["label"])}</a>')
parts.append('<p class="meta">On this page: ' + ' &middot; '.join(nav) + '</p>')

rows = []
for s in secs + ([bsky] if bsky else []):
    k, summ = s['key'], s['summ']; oc = get(summ, s['outcomes'])
    assert set(oc) <= set(OUTS), f'{k}: an outcome outside the five ({sorted(set(oc) - set(OUTS))})'
    assert sum(oc.values()) == get(summ, s['rows']), f'{k}: outcomes do not add up to the row count'
    cells = ''.join(f'<td class="n">{num(k, summ, s["outcomes"] + "." + o) if o in oc else "0"}</td>' for o in OUTS[:4])
    rows.append(f'<tr><td><a href="#{E(s["anchor"])}">{E(s["label"])}</a></td><td>{E(s["row"])}</td>{cells}<td>{stamp(k, summ, s["stamp"])}</td></tr>')
rows.append(f'<tr><td>{E(BLUESKY_SEC["label"])}</td><td colspan="6">Being read</td></tr>' if not bsky else '')
parts.append('<h2>Outcomes by section</h2>')
parts.append('<div class="scroll"><table class="mtx"><thead><tr><th>Section</th><th>One row is</th><th>Above</th><th>Below</th><th>Consistent</th>'
             '<th>Cannot tell</th><th>Scored</th></tr></thead><tbody>\n' + '\n'.join(r for r in rows if r) + '\n</tbody></table></div>')
parts.append('<p class="bench-note">Each count is the outcome printed on the row in its section. Rows read with a rule set after the data say so in '
             'their section and are counted as printed. The TikTok column of readings defined after the data is not counted here.</p>')
parts.append('<p class="bench-note">Counts beside these rows, with the status NOTHING_RETURNED counted apart and outside every share. ' + ' '.join(f'{s["label"]}: {req13_text(s["key"], s["summ"], s["req13"])}' for s in secs + ([bsky] if bsky else [])) + '</p>')

for s in secs: parts.append(s['frag'])
if bsky: parts.append(bsky['frag'])
else:
    parts.append('<section id="social-bluesky">\n<h2>Bluesky</h2>\n<p class="meta">This section is being read. It appears here when the reading is complete.</p>\n</section>')

parts.append('<p class="meta">Named here and want to answer a row? <a href="/respond?u=social-all">Respond</a></p>')
parts.append(f'<p class="meta">Each section lists its own sources. The outcome counts and headline of this page are in <a href="{FEED}">{FEED}</a>.</p>')
parts.append('<section id="replies" data-prefix="social"></section><script src="/replies.js" defer></script>')

slot = (f'<section id="hl-slot" class="hl-slot hl"><div class="hl-big">{E(headline["big"])}</div><p class="hl-line">{E(headline["line"])}</p></section>'
        if headline else '')
main = '<main class="wrap">' + slot + '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>\n' + '\n'.join(parts) + '</main>'

# ------------------------------------------------------------------------------------------------ chrome from launch.html
# 12 Nov 2026: if the LAUNCH page has moved on since 10 Nov (its head now carries dataset JSON-LD and the page's own words), the chrome is taken from the social.html already built, and only <main> is replaced.
# indahl-ai/build_site.py takes the <main> of social.html at ship, so the chrome here never reaches the live page.
try:
    src = open(SRC, encoding='utf-8').read()
    head, rest = src.split('<body>', 1)
    old_title = re.search(r'<title>(.*?)</title>', head).group(1)
    old_desc = re.search(r'<meta name="description" content="(.*?)">', head).group(1)
    head = head.replace(old_title, TITLE).replace(old_desc, html.escape(DESC, quote=True))
    head = head.replace('https://indahl.ai/launch/live.json', 'https://indahl.ai' + FEED).replace('https://indahl.ai/launch', 'https://indahl.ai/social')
    head = head.replace('"name": "LAUNCH"', '"name": "SOCIAL"')
    head = re.sub(r'"dateModified": "\d{4}-\d{2}-\d{2}"', '"dateModified": "' + time.strftime('%Y-%m-%d', time.gmtime()) + '"', head)
    head = head.replace(html.escape(old_desc, quote=False), html.escape(DESC, quote=True))
    head = head.replace(old_desc.replace('&#x27;', "'"), DESC.replace('"', '\\"'))      # JSON-LD carries the description unescaped
    assert 'launch' not in head.lower().replace('/launch">launch', ''), 'chrome: the LAUNCH page\'s own words are still in the head'
    hdr = rest.split('<section class="hero slim">', 1)[0]
    foot = rest.split('</main>', 1)[1]
    hero = f'<section class="hero slim"><div class="wrap"><h1>{HERO}</h1></div></section>\n'
    page = head + '<body>' + hdr + hero + main + foot
except AssertionError:
    _old = open(os.path.join(H, 'social.html'), encoding='utf-8').read()
    page = _old.split('<main class="wrap">', 1)[0] + main + _old.split('</main>', 1)[1]
open(os.path.join(H, 'social.html'), 'w', encoding='utf-8').write(page)

# ------------------------------------------------------------------------------------------------ summary_social.json
out = dict(
    desk='social', page='/social', division='/hermes', built_utc=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()),
    status='complete' if bsky else 'staging: the Bluesky section is being read',
    headline=(dict(big=headline['big'], line=headline['line'], href='/social', section=headline['section'], numbers=HL_NUMBERS) if headline else None),
    headline_rule=('Only rows that read ABOVE, BELOW or CONSISTENT and do not rest on a rule defined after the data. CANNOT_TELL rows '
                   'and readings defined after the data give no headline. A section gives one only if its own summary counts those rows.'),
    sections={}, numbers=NUMBERS)
for s in secs + ([bsky] if bsky else []):
    k = s['key']; e = dict(status='cleared', anchor=s['anchor'], section_file=f'{k}/section_{k}.html', section_sha256=s['section_sha256'],
                           summary_file=f'{k}/summary_{k}.json', summary_sha256=s['summary_sha256'])
    if 'outcomes' in s:
        summ = s['summ']
        e.update(scored=get(summ, s['stamp']), gate_passed=get(summ, s['gate']), rows=get(summ, s['rows']),
                 outcomes={o: get(summ, s['outcomes']).get(o, 0) for o in OUTS}, **decided_note(s))
    else: e.update(headline_eligible=False, note='placed as cleared. No outcome reader or headline reader has been written for this section yet')
    out['sections'][k] = e
if not bsky: out['sections']['bluesky'] = dict(status='being read', anchor='social-bluesky', headline_eligible=False)
json.dump(out, open(os.path.join(H, 'summary_social.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('social.html written,', len(page), 'chars. Sections:', ', '.join(s['key'] for s in secs) + (', bluesky' if bsky else ', bluesky slot (being read)'))
print('headline:', (headline['big'] + ' | ' + headline['line']) if headline else 'none')
