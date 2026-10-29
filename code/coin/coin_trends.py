#!/usr/bin/env python3
"""coin_trends.py: Ravencoin pool shares over time and batch payouts, exactly as PLAN_TRENDS.md (+Addenda 1 and 2). Reads data/rvn_*.jsonl and data/tx_rows.jsonl, writes summary_trends.json.
The linkage reading is CANNOT_TELL because the Bitcoin positive control (AntPool and BTC.com) held no batch payouts: the known-good gate of Addendum 2 cannot pass."""
import json, glob, math, re, statistics as S, collections as C, binascii, datetime as D
rows = {}
for f in sorted(glob.glob('data/rvn_*.jsonl')):
    for l in open(f):
        r = json.loads(l)
        if r.get('coinbase_vout') and r.get('time') and r.get('height', 0) >= 4000000: rows[r['height']] = r
R = [rows[h] for h in sorted(rows)]
def addr(r):
    a = r['coinbase_vout'][0].get('a'); return a[0] if a else None
def tag(r):
    try: s = binascii.unhexlify(r['coinbase_hex']).decode('latin1')
    except Exception: return None
    m = re.search(r'[A-Za-z][A-Za-z0-9.\-_]{3,}', s); return m.group(0) if m else None
for r in R: r['_a'] = addr(r); r['_t'] = tag(r)
span_days = (R[-1]['time'] - R[0]['time']) / 86400
top_addr = [a for a, _ in C.Counter(r['_a'] for r in R if r['_a']).most_common(10)]
top_tag = [t for t, _ in C.Counter(r['_t'] for r in R if r['_t']).most_common(6)]
B = 6 * 3600; b0 = R[0]['time'] // B
buckets = C.defaultdict(list)
for r in R: buckets[r['time'] // B].append(r)
keys = sorted(buckets)
series = [('address', a) for a in top_addr] + [('tag', t) for t in top_tag]
out_series = []; tests_all = flags_all = 0
for kind, name in series:
    f = (lambda r: r['_a'] == name) if kind == 'address' else (lambda r: r['_t'] == name)
    flags = []; tests = 0
    for i, k in enumerate(keys):
        bl = buckets[k]; n = len(bl)
        if i == 0 or n < 10: continue
        prior = [r for kk in keys[:i] if kk >= k - 28 for r in buckets[kk]]          # 28 six-hour buckets = 7 days, or all earlier data while fewer exist
        if len(prior) < 100: continue
        p = sum(1 for r in prior if f(r)) / len(prior)
        if p <= 0 or p >= 1: continue
        z = (sum(1 for r in bl if f(r)) / n - p) / math.sqrt(p * (1 - p) / n); tests += 1
        if abs(z) >= 3: flags.append(dict(bucket=D.datetime.fromtimestamp(k * B, D.timezone.utc).strftime('%d %b %H:%M'), z=round(z, 2), n=n))
    exp = tests * 0.0027
    oc = 'CANNOT_TELL' if span_days < 14 else ('ABOVE' if len(flags) > exp + 2 * math.sqrt(exp) else 'CONSISTENT')
    tot = sum(1 for r in R if f(r))
    out_series.append(dict(kind=kind, name=name if kind == 'tag' else name[:6] + '...' + name[-4:], blocks=tot, share=round(tot / len(R), 4), tests=tests, flags=len(flags), expected=round(exp, 3), outcome=oc, flag_buckets=flags[:6]))
conc = [dict(bucket=D.datetime.fromtimestamp(k * B, D.timezone.utc).strftime('%d %b %H:%M'), blocks=len(buckets[k]),
             top1=round(max(C.Counter(r['_a'] for r in buckets[k]).values()) / len(buckets[k]), 3), top3=round(sum(v for _, v in C.Counter(r['_a'] for r in buckets[k]).most_common(3)) / len(buckets[k]), 3)) for k in keys if len(buckets[k]) >= 10]
# batch payouts
tx = [json.loads(l) for l in open('data/tx_rows.jsonl')]; watched = set(top_addr); pay = C.defaultdict(list)
for t in tx:
    if t['n_out'] >= 20 and len(set(t['in_addrs'])) == 1 and t['in_addrs'][0] in watched: pay[t['in_addrs'][0]].append(t)
batch = []
for a in top_addr:
    ps = sorted(pay.get(a, []), key=lambda t: t['time'])
    if not ps: batch.append(dict(address=a[:6] + '...' + a[-4:], payouts=0)); continue
    gaps = [(y['time'] - x['time']) / 3600 for x, y in zip(ps, ps[1:])]; vol = C.Counter()
    for t in ps:
        for ad, v in t.get('outs', []): vol[ad] += v
    tv = sum(vol.values()) or 1
    batch.append(dict(address=a[:6] + '...' + a[-4:], payouts=len(ps), median_gap_h=round(S.median(gaps), 1) if gaps else None, gap_spread_h=[round(min(gaps), 1), round(max(gaps), 1)] if gaps else None,
                      median_outputs=S.median([t['n_out'] for t in ps]), median_total_rvn=round(S.median([t['total_out'] for t in ps]), 1), recipients=len(vol), top5_share=round(sum(v for _, v in vol.most_common(5)) / tv, 3)))
rec = {a: {ad for t in pay.get(a, []) for ad, _ in t.get('outs', [])} for a in top_addr}
pairs = []; paid_between = 0
for i, a in enumerate(top_addr):
    for b in top_addr[i + 1:]:
        if rec[a] and rec[b]:
            j = len(rec[a] & rec[b]) / len(rec[a] | rec[b]); pairs.append(dict(a=a[:6] + '...' + a[-4:], b=b[:6] + '...' + b[-4:], recipients_shared=len(rec[a] & rec[b]), jaccard=round(j, 3)))
        if b in rec[a] or a in rec[b]: paid_between += 1
pairs.sort(key=lambda p: -p['jaccard'])
res = dict(updated=D.datetime.now(D.timezone.utc).strftime('%d %b %H:%M'), blocks=len(R), span_days=round(span_days, 2), first_height=R[0]['height'], last_height=R[-1]['height'], buckets=len(keys),
           tx_scanned=len(tx), series=out_series, concentration=conc[-12:], batches=batch, linkage=dict(outcome='CANNOT_TELL', why='the Bitcoin positive control (AntPool and BTC.com) held no batch payouts in 14 days, so the known-good gate cannot pass',
           control={'antpool': 0, 'btccom': 0}, descriptive_pairs=pairs[:8], payments_between_watched=paid_between))
json.dump(res, open('summary_trends.json', 'w'), indent=1)
print('blocks', len(R), 'span days', res['span_days'], 'buckets', len(keys)); [print(s['kind'], s['name'], 'blocks', s['blocks'], 'tests', s['tests'], 'flags', s['flags'], 'expected', s['expected'], s['outcome']) for s in out_series]
print('batches', [(b['address'], b['payouts']) for b in batch]); print('pairs', pairs[:3], 'between', paid_between)

# public progress file: what is held, what is read, no raw data
import shutil, os
pub = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai/code/coin')
if os.path.isdir(pub):
    shutil.copy('summary_trends.json', pub)
    lines = ['# COIN trends: progress', '', 'Updated %s UTC.' % res['updated'], '', 'Blocks held: %d (heights %d to %d), %.2f days.' % (res['blocks'], res['first_height'], res['last_height'], res['span_days']),
             'Transactions scanned: %d.' % res['tx_scanned'], '',
             'Pool share-move test: needs 14 days held. %s' % ('Window is long enough, outcomes are in summary_trends.json.' if res['span_days'] >= 14 else 'Window is still shorter, every series reads CANNOT_TELL.'),
             'Linkage test: %s. %s.' % (res['linkage']['outcome'], res['linkage']['why']), '',
             'Plan, committed before any series: PLAN_TRENDS.md. Scripts: rvn_history.py, rvn_txs.py, coin_trends.py, btc_control.py. Output: summary_trends.json.']
    open(os.path.join(pub, 'PROGRESS.md'), 'w').write('\n'.join(lines) + '\n')
