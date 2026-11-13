"""Score table of Guards, recomputed from the prospective ledger ~/bones-forge/watch/tp_score.jsonl, frozen at row 608 (16:45 EDT,
22 Oct 2026). Widths are against the sealed in-sample bar of 7.7 % (2 of 26), treated as exact: z = (p - 0.077) / sqrt(0.077 * 0.923 / n)."""
import json, math, os, collections
rows = [json.loads(l) for l in open(os.path.expanduser('~/bones-forge/watch/tp_score.jsonl')) if l.strip()][:608]
n = len(rows); bar = 2 / 26
before = [r for r in rows if r['caught'] == 'BEFORE']
c = collections.Counter(r['by'] for r in before)
def z(k, m): p = k / m; return (p - bar) / math.sqrt(bar * (1 - bar) / m)
print(f'rows {n}; caught before {len(before)} ({100*len(before)/n:.1f} %): by the model {c["bones"]}, by a check or referee {c["machine"]}, by the human partner {c["wayfinder"]}')
print(f'unaided {c["bones"]} of {n} = {100*c["bones"]/n:.1f} %: {z(c["bones"], n):+.1f} widths above the bar; all caught before: {z(len(before), n):+.1f} widths')
f20 = rows[:20]; u20 = sum(1 for r in f20 if r['caught'] == 'BEFORE' and r['by'] == 'bones')
print(f'first twenty rows: unaided {u20} of 20 = {100*u20/20:.1f} %: {z(u20, 20):+.2f} widths')
fam = collections.Counter(r.get('lesson') for r in rows)
print('families:', dict(sorted((str(k), v) for k, v in fam.items())), '; untagged', fam.get('none', 0))
