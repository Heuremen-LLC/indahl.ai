"""never_read.py -- WEN AS NEVER (Wayfinder, 7 Oct: "Wen is a name but also the timescale they need to use, never. no forward progression, just thoughts no need for output
at the end."). Reads Dreamtime r1 WITHOUT the output: at the answer's first position (nothing emitted), the held mass on COMMIT words vs on HOLD + NEXT words, in every
language's mode words, normalised over the mode words: c = P(commit) / P(all mode words). A seat that reads the case holds more c on LATE items (right = COMMIT) than on
EARLY ones (right = wait). Per cell: mean c early, mean c late, the gap, and the paired share of pairs where late > early (15 pairs; the coin = 50%). Raw."""
import json, os, sys, collections
from scipy.stats import binomtest
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r1')
MW = json.load(open(os.path.join(HERE, 'translations.json')))['modes']
CW = {MW[L]['COMMIT'] for L in MW}; WW = {MW[L][m] for L in MW for m in ('HOLD', 'NEXT')}
A = [json.loads(l) for s in ('en', 'th', 'eu') for l in open(f'{D}/answers_{s}.jsonl')]
cell = collections.defaultdict(dict)
for a in A:
    f = a['first_token_mass']; c = sum(f.get(w, 0) for w in CW); h = sum(f.get(w, 0) for w in WW)
    cell[(a['seat'], a['lang'], a['ruler'])][a['id']] = c / (c + h) if c + h > 1e-9 else float('nan')
print('WEN AS NEVER -- the held weighting at the first position, nothing emitted: c = P(commit) / P(mode words)')
print(f'   {"seat":4} {"lang":4} {"ruler":5} | c early | c late | gap  | pairs late > early | (the spoken answer gap, discrimination.txt)')
spoken = {}
for l in open(f'{D}/discrimination.txt'):
    if 'seat ' in l and '->' in l:
        p = l.split(); spoken[(p[1], p[3], p[5].rstrip(':'))] = p[-1]
tot = [0, 0]
for k, v in sorted(cell.items()):
    pairs = sorted({i[:-1] for i in v}); e = [v[p + 'e'] for p in pairs]; l = [v[p + 'l'] for p in pairs]
    win = sum(b > a for a, b in zip(e, l)); n = len(pairs); tot[0] += win; tot[1] += n
    print(f'   {k[0]:4} {k[1]:4} {k[2]:5} | {sum(e) / n:.3f}   | {sum(l) / n:.3f}  | {sum(l) / n - sum(e) / n:+.3f} | {win:2}/{n} p {binomtest(win, n, 0.5).pvalue:.3f} | spoken {spoken.get(k, "?")}')
print(f'   ALL CELLS: late > early in {tot[0]}/{tot[1]} pairs = {100 * tot[0] / tot[1]:.0f}%  p {binomtest(tot[0], tot[1], 0.5).pvalue:.2e}')
