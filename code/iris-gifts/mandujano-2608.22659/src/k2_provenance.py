#!/usr/bin/env python3
"""K2 (PLAN d4ec250): his 1,497 rows against TIGER-Lab's released per-item outputs. Upstream correct = pred equals answer; items with no
extracted letter (pred None) are their own bin, never folded into right or wrong. Reads both as data only."""
import csv, json, zipfile, os, collections
H = os.path.dirname(os.path.abspath(__file__)); T = H + '/../theirs'
UP = {'Mistral-7B-Instruct-v0.1': 'Mistral-7B-Instruct-v0.1', 'Mistral-7B-Instruct-v0.2': 'Mistral-7B-Instruct-v0.2', 'Mistral-7B-v0.1': 'Mistral-7B-v0.1',
      'Qwen1.5-7B-Chat': 'Qwen1.5-7B-Chat', 'Yi-6B': 'Yi-6B', 'Yi-6B-Chat': 'Yi-6b-Chat'}
his = collections.defaultdict(dict); hcat = {}
for r in csv.DictReader(open(T + '/mmlu_pro_real_data.csv')): his[r['model']][r['question_id']] = int(r['correct']); hcat[r['question_id']] = r['category']
print('model                      his rows | letter&agree  letter&disagree | no letter: his 1 / his 0 | not upstream | category mismatch')
for m, u in UP.items():
    z = zipfile.ZipFile(T + '/upstream/%s.zip' % u); d = json.loads(z.read(z.infolist()[0].filename)); up = {str(x['question_id']): x for x in d}
    c = collections.Counter()
    for q, v in his[m].items():
        x = up.get(q)
        if x is None: c['missing'] += 1; continue
        if x.get('category') != hcat[q]: c['catmis'] += 1
        if x.get('pred') is None: c['none1' if v else 'none0'] += 1; continue
        c['agree' if (x['pred'] == x['answer']) == bool(v) else 'disagree'] += 1
    print('%-26s %5d    | %6d        %6d          | %5d / %-5d           | %5d        | %d' % (m, len(his[m]), c['agree'], c['disagree'], c['none1'], c['none0'], c['missing'], c['catmis']))
