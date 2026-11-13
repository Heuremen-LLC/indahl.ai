"""make_short.py (13 Nov 2026, night ladder): detection-only targets. From data_bal/, every positive answer becomes {"errors": [{"code": X}]}
(the codes it had, quotes and arithmetic dropped), negatives stay {"errors": []}. Same rows, same split, same eval (a flag is a non-empty
errors list), so it tests whether the collapse comes from the long verbatim-quote targets."""
import json, sys
from pathlib import Path
D = Path(__file__).parent; src = D / sys.argv[1] if len(sys.argv) > 1 else D / 'data_bal'; dst = D / (sys.argv[2] if len(sys.argv) > 2 else 'data_short'); dst.mkdir(exist_ok=True)
def short(row):
    a = row['messages'][-1]['content']
    try: e = json.loads(a).get('errors', [])
    except Exception: return row
    if e: row['messages'][-1]['content'] = json.dumps({'errors': [{'code': x.get('code', 'F6')} for x in e]})
    return row
for f in ('train', 'valid'):
    rows = [short(json.loads(l)) for l in open(src / f'{f}.jsonl')]
    with open(dst / f'{f}.jsonl', 'w') as o:
        for r in rows: o.write(json.dumps(r) + '\n')
print('written', dst)
