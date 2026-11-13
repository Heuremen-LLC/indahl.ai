import json, hashlib, urllib.request, sys
def sha(b): return hashlib.sha256(b).hexdigest()
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'siteaudit'}), timeout=30); return r.read()
live = json.load(open('tape_live.json'))
E = live['entries']
E_sorted = sorted(E, key=lambda e: e['n'])
print('entries', len(E), 'n range', E_sorted[0]['n'], E_sorted[-1]['n'], 'count field', live['count'])
# 1 chain recompute
bad = []
prev = '0'*64
for e in E_sorted:
    h = sha(json.dumps({k: e[k] for k in ('n','t','kind','subject','root','prev')}, sort_keys=True, separators=(',',':')).encode())
    if h != e['entry']: bad.append(('hash', e['n']))
    if e['prev'] != prev: bad.append(('prev', e['n'], e['prev'][:10], prev[:10]))
    prev = e['entry']
print('chain problems:', bad)
print('head matches', live['head']['entry'] == E_sorted[-1]['entry'], 'gaps in n', [E_sorted[i]['n'] for i in range(1,len(E_sorted)) if E_sorted[i]['n'] != E_sorted[i-1]['n']+1])
# times monotone
tl = [e['t'] for e in E_sorted]; print('times monotone', tl == sorted(tl))
# 2 local tape.jsonl vs live
loc = [json.loads(l) for l in open('/Users/heuremen/bones-forge/tape_index/tape.jsonl')]
lm = {e['n']: e for e in loc}
diff = [e['n'] for e in E_sorted if e['n'] not in lm or any(lm[e['n']].get(k) != e[k] for k in ('t','kind','subject','root','prev','entry'))]
print('local vs live diffs:', diff, 'local count', len(loc))
# 3 leaves from public GitHub for chosen entries
import random
GH = 'https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/main/code/tape/leaves/%d.json'
def merkle(leaves):
    lv = [sha(b'\x00' + ('%s\t%s' % (l, h)).encode()) for l, h in sorted(leaves)]
    if not lv: return sha(b'')
    while len(lv) > 1:
        nx = [sha(b'\x01' + bytes.fromhex(lv[i]) + bytes.fromhex(lv[i+1])) for i in range(0, len(lv)-1, 2)]
        if len(lv) % 2: nx.append(lv[-1])
        lv = nx
    return lv[0]
sample = [85, 84, 83, 82, 81, 80, 75, 60, 40, 23, 22, 21, 1]
byn = {e['n']: e for e in E_sorted}
for n in sample:
    try:
        L = json.loads(get(GH % n))
    except Exception as ex:
        print(n, 'GitHub leaf fetch failed', ex); continue
    e = byn[n]
    out = {'kind_match': L['kind'] == e['kind']}
    if L['kind'] == 'beacon':
        d = dict(L['leaves'])
        qr = d.get('qbits_root')
        s = '%s:%s:%s' % (d['drand_randomness'], d['feeds_root'], d['prev_entry']) + ((':' + qr) if qr and qr != 'NONE' else '')
        out['beacon_recompute'] = sha(s.encode()) == e['root']
    else:
        out['merkle_recompute'] = merkle([tuple(x) for x in L['leaves']]) == e['root']
    print(n, e['kind'], out)
