#!/usr/bin/env python3
"""make_exam.py -- Wen-data's exam, from the 74 logged misses (receipts_dataset/data/receipts.jsonl). TEST SET ONLY:
that prose was written by Bones (Claude), so it never becomes training text or targets (Anthropic Consumer Terms).
Each miss with a recorded correction gives two items:
  early: the reading as it stood when it was mis-labelled (one ruler)        -> right answer: do NOT commit (HOLD or NEXT)
  late:  the reading plus what the other rulers showed                        -> right answer: COMMIT
A model that always holds fails every late item; one that always commits fails every early item."""
import json, os
SRC = os.path.expanduser('~/bones-forge/parallax/darkwave_disco/receipts_dataset/data/receipts.jsonl')
out = []
for r in map(json.loads, open(SRC, encoding='utf-8')):
    w, rec = (r.get('wrong_read') or '').strip(), (r.get('record_showed') or '').strip()
    if len(w) < 25 or len(rec) < 25:
        continue
    out.append(dict(id=r['id'] + 'e', stage='early', mode_ok=['HOLD', 'NEXT'], failure_mode=r['failure_mode'],
                    reading=w, rulers=''))
    out.append(dict(id=r['id'] + 'l', stage='late', mode_ok=['COMMIT'], failure_mode=r['failure_mode'],
                    reading=w, rulers=rec))
json.dump(out, open('exam.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out), 'items from', len(out) // 2, 'misses')
