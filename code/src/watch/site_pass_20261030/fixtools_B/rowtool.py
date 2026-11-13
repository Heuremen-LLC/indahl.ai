#!/usr/bin/env python3
"""rowtool.py (site pass 30 Oct 2026, lane B): edit calibrated rows in book_calibrated.json AND qia_body.html together, from the pristine pre-sitepass copies.
Row <-> body row mapping is by published+measured text (whitespace and quote tolerant), with the study id to break ties."""
import json, re, html, os
MP = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/'); SFX = '.pre-sitepass-20261030'
FIELDS = {'organisation': 0, 'study': 1, 'published': 2, 'measured': 3, 'qia_calibration': 4, 'how': 5}
def esc(s):
    t = html.escape(s, quote=True)
    for a, b in (('“', '&ldquo;'), ('”', '&rdquo;'), ('±', '&plusmn;'), ('×', '&times;'), ('–', '&ndash;'), ('—', '&mdash;'), ('’', '&rsquo;'), ('‘', '&lsquo;'), ('µ', '&micro;'), ('≤', '&le;'), ('−', '&minus;'), ('≥', '&ge;'), ('°', '&deg;')):
        t = t.replace(a, b)
    return t
def txt(c):
    c = re.sub(r'<br>', ' ', c); c = re.sub(r'<[^>]+>', '', c); return html.unescape(c)
def key(s): return re.sub(r'\s+', '', s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-').replace('−', '-'))
def codes_of(t):
    m = re.match(r'^((?:[QF]\d+\s+)+)', t + ' ')
    return m.group(1).split() if m else []
class Rows:
    def __init__(self):
        self.bk = json.load(open(MP + 'book_calibrated.json' + SFX)); self.byid = {r['id']: r for r in self.bk}
        self.orig = {r['id']: dict(r) for r in self.bk}
        body = open(MP + 'qia_body.html' + SFX).read()
        self.pieces = re.split(r'(<tr>(?:(?!</tr>).)*</tr>)', body, flags=re.S)
        self.cells = {}; self.pidx = {}   # row id -> list of 6 cell html ; row id -> piece index
        datarows = []
        for i, p in enumerate(self.pieces):
            if i % 2 == 1:
                cs = re.findall(r'<td>(.*?)</td>', p, re.S)
                if len(cs) == 6: datarows.append((i, cs))
        for r in self.bk:
            hits = [(i, cs) for i, cs in datarows if key(txt(cs[2])) == key(r['published']) and key(txt(cs[3])) == key(r['measured'])]
            if len(hits) > 1 and r['study_id']:
                sid = r['study_id'].replace('zenodo:', ''); h2 = [h for h in hits if sid in h[1][1]]; hits = h2 or hits
            assert len(hits) == 1, (r['id'], len(hits))
            self.pidx[r['id']] = hits[0][0]; self.cells[r['id']] = list(hits[0][1])
        self.log = []   # (finding, id, field, how)
    # ---- renderers
    def render(self, rid, field, text):
        old = self.cells[rid][FIELDS[field]]
        if field in ('published', 'measured', 'organisation'): return esc(text)
        if field == 'qia_calibration':
            cs = codes_of(text); rest = text
            if cs: rest = re.sub(r'^((?:[QF]\d+\s+)+)', '', text + ' ', count=1).strip()
            elif text.startswith('—'): rest = text[1:].strip()
            chips = ' '.join(f'<a class="code" href="/qia/key#{c}">{c}</a>' for c in cs) or '&mdash;'
            return f'<span class="codes">{chips}</span><br>' + esc(rest)
        if field == 'how':
            if '<br><span class="by">' in old:
                main, tail = old.split('<br><span class="by">', 1); tail_t = txt('<span class="by">' + tail).strip()
                t = text[:-len(tail_t)].rstrip() if tail_t and text.endswith(tail_t) else text
                return esc(t) + '<br><span class="by">' + tail
            return esc(text)
        if field == 'study':
            ms = list(re.finditer(r'<a href="[^"]*">[^<]*</a>', old))
            if not ms: return esc(text)
            m = ms[-1]; href = re.match(r'<a href="([^"]*)">', m.group(0)).group(1); label = txt(m.group(0))
            if old.strip() == m.group(0): return f'<a href="{href}">{esc(text)}</a>'
            # corporate work cell: description, then the link kept as it is
            pre = text[:-len(label)].rstrip() if text.endswith(label) else text
            return esc(pre) + f' <a href="{href}">{esc(label)}</a>'
        raise KeyError(field)
    # ---- edits
    def set(self, rid, field, new, finding=''):
        cur = self.byid[rid][field]
        if cur == new: return False
        self.byid[rid][field] = new
        self.cells[rid][FIELDS[field]] = self.render(rid, field, new)
        self.log.append((finding, rid, field)); return True
    def sub(self, rid, field, old_sub, new_sub, finding=''):
        cur = self.byid[rid][field]
        if cur.count(old_sub) != 1: return False
        return self.set(rid, field, cur.replace(old_sub, new_sub), finding)
    def body(self):
        ps = list(self.pieces)
        for rid, i in self.pidx.items():
            ps[i] = '<tr>' + ''.join(f'<td>{c}</td>' for c in self.cells[rid]) + '</tr>'
        return ''.join(ps)
