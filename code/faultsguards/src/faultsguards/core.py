"""Data access for the Faults and Guards. The data is generated from the published sources (tools/extract.py) and never edited by hand."""
import json, os, re
_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
_cache = {}
def load(which):
    """which is 'faults' or 'guards'. Returns the whole document: intro, parts, entries, sections."""
    if which not in ('faults', 'guards'): raise ValueError("which must be 'faults' or 'guards'")
    if which not in _cache: _cache[which] = json.load(open(os.path.join(_D, which + '.json'), encoding='utf-8'))
    return _cache[which]
def faults(): return load('faults')['entries']
def guards(): return load('guards')['entries']
def _get(entries, n):
    for e in entries:
        if e['number'] == int(n): return e
    raise KeyError(n)
def get_fault(n): return _get(faults(), n)
def get_guard(n): return _get(guards(), n)
def families(which='faults'):
    """The parts of the document in order, each with its entry numbers."""
    out = []
    for e in load(which)['entries']:
        if not out or out[-1]['part'] != e['part']: out.append(dict(part=e['part'], numbers=[]))
        out[-1]['numbers'].append(e['number'])
    return out
def search(query, which=None):
    """Entries whose title or text contain every word of the query, case-insensitive. which: 'faults', 'guards' or None for both."""
    words = [w for w in re.findall(r'\w+', query.lower()) if w]; hits = []
    for w in ((which,) if which else ('faults', 'guards')):
        for e in load(w)['entries']:
            hay = (e['title'] + ' ' + e['text']).lower()
            if all(x in hay for x in words): hits.append(dict(document=w, number=e['number'], title=e['title'], part=e['part']))
    return hits
def source_info():
    return dict(faults='https://heuremen.org/faults.pdf', guards='https://heuremen.org/guards.pdf', publisher='Heuremen LLC')
