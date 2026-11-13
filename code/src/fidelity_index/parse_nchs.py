"""parse_nchs.py: NCHS state counts from the pdftotext dumps in raw/ (state names then 24 tokens, 2000..2023). Prints a self-check; writes data/nchs_counts.json."""
import re, json, sys
def parse(path, n):
    toks = open(path).read().split('\n'); names = None; out = {}; i = 0
    L = [l.strip() for l in toks]
    j = L.index('State') + 1
    cur = None; vals = []
    def flush():
        if cur: out[cur] = vals[:]
    for l in L[j:]:
        if not l or l.startswith('Number of') or l.startswith('- Not'): continue
        if re.fullmatch(r'[\d,\- ]+', l):
            for t in l.split(): vals.append(None if t == '-' else int(t.replace(',', '')))
        else:
            flush(); cur = l; vals = []
    flush(); bad = {k: len(v) for k, v in out.items() if len(v) != n}
    return out, bad
if __name__ == '__main__':
    res = {}
    for ev, f in (('divorce', 'raw/div23.pdf.txt'), ('marriage', 'raw/mar23.pdf.txt')):
        d, bad = parse(f, 24); print(ev, len(d), 'states', 'bad', bad); res[ev] = d
    json.dump(res, open('data/nchs_counts.json', 'w'), indent=0)
