src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
import random
labels = C.Counter()
files = dict(rsga_files())
for s_, tx in files.items():
    for part, start in (('III', r'^III\.'), ('VI', r'^VI\.')):
        m = re.search(start, tx, re.M)
        if not m: continue
        end = tx.find('\nIV.', m.start()) if part == 'III' else len(tx)
        for ln in tx[m.start():end].splitlines()[1:]:
            mm = re.match(r'^(\S[^0-9]*?)\s+(\d+/\d+/\d+)\s*$', ln)
            if mm: labels[(part, mm[1].strip())] += 1
print('distinct triple labels:', dict(labels))
kg = json.load(open(D + '/known_good_rows.json')); print('known_good rows:', json.dumps(kg)[:600])
random.seed(5)
keys = [k for k in files if '20210315' in k or '20240425' in k or '20260314' in k or '20230719' in k or '20251002' in k or '20220222' in k]
for k in keys:
    tx = files[k]; print('=====', k)
    for ln in tx.splitlines():
        if re.match(r'^(:Issued|SDF Number|III\.|Class [MX]|Proton|VI\.|A\.  Middle|B\.  High|Active|Minor|Major)', ln): print('  RAW:', ln)
    r = [x for x in allparsed if x['src'] == k][0]
    print('  PARSED: day', r['day'], 'issued', r['iss'], 'd1', r['d1'], 'M', r['M'], 'X', r['X'], 'P', r['P'], 'mid minor/major', r['mid_mi'], r['mid_ma'], 'hi minor/major', r['hi_mi'], r['hi_ma'])
