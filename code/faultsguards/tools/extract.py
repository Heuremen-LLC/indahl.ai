#!/usr/bin/env python3
"""extract.py: generates src/faultsguards/data/{faults,guards}.json from source/FAULTS.html and source/GUARDS.html. Nothing is retyped (PLAN.md rule 1).
Each numbered h3 becomes an entry with its family or part (the h1 above it), its plain text and its original inline html. Each h2 becomes a section. Paragraphs before the first h1 are the intro."""
import os, re, sys, json, html
from html.parser import HTMLParser
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
BLOCK = {'p', 'div', 'ul', 'ol', 'table', 'blockquote', 'pre'}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False); self.items = []; self.cur = None; self.depth = 0; self.buf = []; self.tag = None; self.cls = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.cur is None and (tag in ('h1', 'h2', 'h3') or tag in BLOCK) and self.depth == 0:
            self.cur = tag; self.cls = a.get('class', ''); self.buf = []; self.depth = 1; return
        if self.cur is not None:
            if tag == self.cur: self.depth += 1
            self.buf.append(self.get_starttag_text())
    def handle_endtag(self, tag):
        if self.cur is None: return
        if tag == self.cur:
            self.depth -= 1
            if self.depth == 0:
                self.items.append((self.cur, self.cls, ''.join(self.buf).strip())); self.cur = None; return
        self.buf.append('</%s>' % tag)
    def handle_data(self, d):
        if self.cur is not None: self.buf.append(d)
    def handle_entityref(self, n):
        if self.cur is not None: self.buf.append('&%s;' % n)
    def handle_charref(self, n):
        if self.cur is not None: self.buf.append('&#%s;' % n)
def plain(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).replace(' ,', ',').replace(' .', '.').replace(' ;', ';').replace(' :', ':').replace('( ', '(').replace(' )', ')').strip()
def run(name):
    src = open(os.path.join(ROOT, 'source', name + '.html'), encoding='utf-8').read(); body = src[src.index('<body'):]; p = P(); p.feed(body)
    title = None; intro = []; part = None; sec = None; entries = []; sections = []; cur = None; parts = {}
    for tag, cls, h in p.items:
        if tag == 'h1' and cls != 'newpart': title = plain(h); continue
        if tag == 'h1': part = plain(h); cur = None; sec = None; continue
        if tag == 'h2': sec = dict(title=plain(h), part=part, paragraphs=[]); sections.append(sec); cur = None; continue
        if tag == 'h3':
            t = plain(h); m = re.match(r'(\d+)\.\s*(.*)', t)
            cur = dict(number=int(m.group(1)) if m else None, title=m.group(2) if m else t, part=part, paragraphs=[], html=[]); entries.append(cur); sec = None; continue
        txt = dict(text=plain(h), html=h, kind=cls or tag)
        if cur is not None: cur['paragraphs'].append(txt['text']); cur['html'].append(h)
        elif sec is not None: sec['paragraphs'].append(txt['text'])
        elif part is None: intro.append(txt['text'])
        else:
            parts.setdefault(part, []).append(txt['text'])
    for e in entries: e['text'] = '\n\n'.join(e['paragraphs'])
    return dict(document=title, source=name + '.html', intro=intro, parts=[dict(title=k, paragraphs=v) for k, v in parts.items()], entries=entries, sections=sections)
if __name__ == '__main__':
    out = os.path.join(ROOT, 'src', 'faultsguards', 'data'); os.makedirs(out, exist_ok=True)
    for n, f in (('FAULTS', 'faults.json'), ('GUARDS', 'guards.json')):
        d = run(n); json.dump(d, open(os.path.join(out, f), 'w', encoding='utf-8'), indent=1, ensure_ascii=False); print(f, 'entries', len(d['entries']), 'numbers', [e['number'] for e in d['entries']][:6], '...', 'parts', len(d['parts']), 'sections', len(d['sections']), 'intro paragraphs', len(d['intro']))
