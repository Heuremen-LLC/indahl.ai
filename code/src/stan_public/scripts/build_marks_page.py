"""Builds the item list for the spot-check marking page (12 Nov 2026). Three sets:
A = the pre-registered 40 (seed 4242, same draw as spot_check.py), B = the ceiling 20 (parsed from spot_check_20.md),
C = 20 of the teacher-PRESENT train rows, seed 1113, not already in A."""
import json, random, re
from common import *
pool = {g['id']: g for g in all_pool()}
silver = list(jl_read(S + '/data/silver_v1/silver_all.jsonl'))
items = []
a = [r for r in silver if r['label']['status'] in ('PRESENT', 'ABSENT')]
random.Random(4242).shuffle(a); a = a[:40]
for k, r in enumerate(a, 1):
    items.append({'set': 'A', 'n': k, 'id': r['id'], 'code': r['code'], 'label': r['label']['status'], 'quote': r['label'].get('quote', ''),
                  'definition': code_block(r['code']), 'text': pool[r['id']]['text'], 'q': 'Does the quote support the label?'})
md = open(S + '/ceiling/spot_check_20.md').read()
for blk in re.split(r'\n## ', md)[1:]:
    head, rest = blk.split('\n', 1)
    m = re.match(r'(\d+)\. (\S+) (F\d)', head)
    g = lambda f: (re.search(r'^' + f + r': ?(.*)$', rest, re.M) or [None, ''])[1]
    ab = rest.split('\nAbstract: ', 1)[1].split('\nPerson', 1)[0]
    items.append({'set': 'B', 'n': int(m.group(1)), 'id': m.group(2), 'code': m.group(3), 'label': g('Judgment'), 'quote': g('Quote'),
                  'definition': 'Recount note: ' + g('Note used'), 'text': ab, 'q': 'Is the judge right about whether the abstract holds the recount\'s evidence?'})
aid = {(r['id'], r['code']) for r in a}
c = [r for r in silver if r.get('split') == 'train' and r['label']['status'] == 'PRESENT' and (r['id'], r['code']) not in aid]
print('teacher-PRESENT train rows not in A:', len(c))
random.Random(1113).shuffle(c)
for k, r in enumerate(c[:20], 1):
    items.append({'set': 'C', 'n': k, 'id': r['id'], 'code': r['code'], 'label': 'PRESENT', 'quote': r['label'].get('quote', ''),
                  'definition': code_block(r['code']), 'text': pool[r['id']]['text'], 'q': 'Does the quote support PRESENT?'})
json.dump(items, open(S + '/review_queue/marks_page/items.json', 'w'), indent=1)
print(len(items), 'items')
