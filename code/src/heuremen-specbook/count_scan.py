"""count_scan.py -- finds COUNTS in titles, headings, lead lines, descriptions and labels (23 Oct, his: "stop putting fucking numbers in titles").
A count = a number (digits or a spelled number) followed by a plural noun, after removing leading section numbers and dates."""
import re, html, glob, os, sys
B = os.path.expanduser('~/bones-forge')
SPELLED = r'(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred|dozen)'
MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)'
NOUNS = r'(?:modes|failure modes|ways|guards|procedures|claims|findings|processors|devices|chips|qubits|runs|experiments|families|entries|faults|catches|rows|jobs|documents|lines|items|readings|deviations|models|studies|tests|pages|desks)'   # 9 Nov 2026 (site pass M5): models, studies, tests, pages, desks
COUNT = re.compile(r'(?i)\b(?:\d[\d,]*|' + SPELLED + r'(?:-' + SPELLED + r')?)[\s-]+(?:[A-Za-z]+[\s-]+)?' + NOUNS + r'\b')
SPOTS = re.compile(r'<title>(.*?)</title>|<h[1-6][^>]*>(.*?)</h[1-6]>|<p class="(?:title|lead|kicker|sub)">(.*?)</p>|name="description" content="(.*?)"|<li><b>[^<]*:</b>(.*?)</li>', re.S)
def clean(t):
    t = ' '.join(html.unescape(re.sub('<[^>]+>', ' ', t)).split())
    t = re.sub(r'^\s*\d+[a-z]?\s*[.·:)]\s*', '', t)                      # section numbers
    t = re.sub(r'\b\d{1,2}(?:\s+(?:to|and|-|–)\s+\d{1,2})?\s+' + MONTHS + r'\b(?:\s+\d{4})?', ' DATE ', t)
    t = re.sub(MONTHS + r'\s+\d{1,2}(?:,\s*\d{4})?', ' DATE ', t); t = re.sub(r'\b(19|20)\d{2}\b', ' YEAR ', t)
    return t
def scan(paths):
    hits = []
    for p in paths:
        s = open(p, encoding='utf-8', errors='replace').read()
        for m in SPOTS.finditer(s):
            raw = next(g for g in m.groups() if g is not None); t = clean(raw)
            for c in COUNT.finditer(t): hits.append((os.path.relpath(p, B), c.group(0), t[:120]))
    return hits
if __name__ == '__main__':
    files = [p for p in glob.glob(B + '/heuremen.org/**/*.html', recursive=True) if '.pre-' not in p and '.bak' not in p]   # 30 Oct (HEU1-12): experiment pages included + [B + '/indahl-ai/index.html'] + [B + '/ligera/' + f for f in ('FAULTS.html', 'GUARDS.html')]
    h = scan(files)
    for r in h: print(f'  {r[0][:55]:55} | {r[1]!r:22} | {r[2]}')
    print(f'count scan: {len(files)} pages; counts in titles/headings/labels: {len(h)}')
