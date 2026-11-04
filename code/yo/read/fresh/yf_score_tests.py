"""yf_score_tests.py -- runs yf_score.py on planted answers in a scratch copy and prints the verdict lines. Output saved to yf_score_tests.out."""
import json, os, shutil, subprocess, tempfile
H = os.path.dirname(os.path.abspath(__file__)); BEST = {'DATES': 'YES', 'LINK': 'YES', 'REQUEST': 'NO'}
CASES = {'planted perfect YO Read, self-label always-NO, shuffled best constant (expect REPLICATES and PASS)': (lambda i: i['answer'], lambda i: 'NO', lambda i: BEST[i['q']]),
         'planted null: YO Read always-NO, self-label perfect (expect no replication, not shown)': (lambda i: 'NO', lambda i: i['answer'], lambda i: 'NO'),
         'planted always-YES YO Read (beats always-NO on LINK, must NOT replicate)': (lambda i: 'YES', lambda i: 'NO', lambda i: 'NO')}
for name, (fy, fs, fh) in CASES.items():
    for SET in ('primary', 'full'):
        T = tempfile.mkdtemp(); os.makedirs(T + '/data'); shutil.copy(H + '/yf_score.py', T)
        for f in ('test_items_primary.jsonl', 'test_items_fresh.jsonl'): shutil.copy(H + '/data/' + f, T + '/data/')
        items = [json.loads(l) for l in open(T + '/data/test_items_fresh.jsonl')]
        for arm, fn in (('read', fy), ('self', fs), ('shuf', fh)):
            for s in (1, 2, 3):
                with open(f'{T}/eval_fresh_yo_{arm}{s}.jsonl', 'w') as o:
                    for i in items: p = fn(i); o.write(json.dumps(dict(id=i['id'], paper=i['paper'], q=i['q'], pred=p, score=float(p == i['answer']), out=p)) + '\n')
        out = subprocess.run(['python3', T + '/yf_score.py', SET], capture_output=True, text=True).stdout.strip().splitlines()
        print(f'== {name} [{SET}]'); print('\n'.join(out[-3:])); shutil.rmtree(T)
