"""sep_parse.py: parses a September SEP page (Table 1 medians) and the error-range Table 2 (HTML for 2021 on, the minutes PDF before)."""
import re, io, urllib.request, pypdf
UA = {'User-Agent': 'heuremen-fedsep/0.1 (+https://indahl.ai/fedsep)'}
def get(u, binary=False):
    b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read(); return b if binary else b.decode('utf8', 'replace')
def cells(html):
    x = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S); x = re.sub(r'</t[dh]>', '|', x); x = re.sub(r'</tr>', '\n', x); x = re.sub(r'<[^>]+>', '', x)
    x = x.replace('&nbsp;', '').replace('&plusmn;', '±').replace('&ndash;', '-').replace('&#x27;', "'"); return [l for l in (re.sub(r'\s+', ' ', l).strip() for l in x.split('\n')) if l]
def table1(html):
    """-> {variable: [medians by column]} from the flattened cell stream: a label line then numbers, one per line, the first row after a label is the median row"""
    ls = cells(html); out = {}; yrs = None
    # the year header is the first run of four-digit years after 'Variable'
    flat = [c.strip(' |') for l in ls for c in l.split('|')]; flat = [c for c in flat if c != '']
    i = next(k for k, c in enumerate(flat) if c.startswith('Variable'))
    j = i + 1
    while j < len(flat) and not re.match(r'^(Change in real GDP|Unemployment rate|PCE inflation)', flat[j]): j += 1
    hdr = [c for c in flat[i:j] if re.match(r'^\d{4}$', c)]; ny = len(hdr) // 3 or 5
    years = hdr[:ny - 1] if len(hdr) >= 3 else []
    for label in ('Change in real GDP', 'Unemployment rate', 'PCE inflation', 'Federal funds rate'):
        k = next((m for m, c in enumerate(flat) if c.startswith(label) and m > j - 1), None)
        if k is None: continue
        vals = []
        for c in flat[k + 1:k + 1 + ny]:
            try: vals.append(float(c))
            except ValueError: vals.append(None)
        out[label] = vals
    return years, out
def table2_html(html):
    x = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S); x = re.sub(r'<[^>]+>', ' ', x).replace('&plusmn;', '±'); x = re.sub(r'\s+', ' ', x)
    return table2_text(x)
def table2_pdf(b):
    t = ' '.join(p.extract_text() or '' for p in pypdf.PdfReader(io.BytesIO(b)).pages); return table2_text(re.sub(r'\s+', ' ', t))
def table2_text(x):
    i = x.lower().find('table 2. average historical projection error ranges')
    if i < 0: return None, {}
    seg = x[i:i + 1100]; yrs = re.findall(r'\b(20\d\d)\b', seg[:200])[:4]; out = {}
    for label, key in (('Change in real GDP', 'Change in real GDP'), ('Unemployment rate', 'Unemployment rate'), ('Total consumer prices', 'PCE inflation'), ('Short-term interest rates', 'Federal funds rate')):
        m = re.search(re.escape(label) + r'[^±]{0,40}((?:±\s*\d+\.\d+\s*){4})', seg)
        if m: out[key] = [float(v) for v in re.findall(r'±\s*(\d+\.\d+)', m.group(1))]
    return yrs, out
