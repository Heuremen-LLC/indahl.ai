#!/usr/bin/env python3
"""miner_cases.py -- the Pi miner's output as Wen cases (6 Oct 2026, Wayfinder and Bones). Pulls stats.jsonl from the Pi; each block height the Pi hashed on (the chain's own tick) is
one reading: mean leading zero bits of The Bonefish's nonces (ruler 1) beside the plain golden-stride walk (ruler 2), baseline 1.0 bit (SHA-256's
own floor: P(>= k zero bits) = 2^-k), the last windows as the time leg. Labelled by the SAME arithmetic as every Wen case: one ruler -> NEXT; rulers
split > 1.5 widths -> HOLD; moved > 2 widths over the last windows -> HOLD; else COMMIT. Writes miner_cases.jsonl; the stooges read it with
seven_read.py (Pi) or it joins the next pod's train/test."""
import json, math, os, subprocess
import numpy as np
from wen_common import chat, user_text
HERE = os.path.dirname(os.path.abspath(__file__))
subprocess.run(['scp', '-q', '-i', os.path.expanduser('~/.ssh/pi_key'), 'flock@192.168.8.145:~/bonefish_miner/stats.jsonl', os.path.join(HERE, 'miner_stats.jsonl')])
W = [json.loads(l) for l in open(os.path.join(HERE, 'miner_stats.jsonl'))] if os.path.exists(os.path.join(HERE, 'miner_stats.jsonl')) else []
def mw(n, s): return (s / n, math.sqrt(2) / math.sqrt(n)) if n else (None, None)    # zero bits are geometric: sd sqrt(2) bits per hash
# THREE SEATS ON EACH BLOCK (6 Oct, the qubit lessons applied): OBSERVER = the miners' stated stamps (the chain), WITNESS = our own hashing stopwatch on the
# same block, TIME = the height tick. Only WHOLE windows (opened by a chain tick) are read; the first after a (re)start is partial. Shape, as P2-I: ratio or fixed lag.
import datetime as D, urllib.request
CACHE_F = os.path.join(HERE, 'miner_blockcache.json')        # 7 Oct: every block's stamp / pool / tx count read once from mempool.space, kept on disk
try: CACHE = json.load(open(CACHE_F))
except Exception: CACHE = {}
def _block(h):
    k = str(h)
    if k not in CACHE or not CACHE[k].get('ts'):
        try:
            hx = urllib.request.urlopen(f'https://mempool.space/api/block-height/{h}', timeout=20).read().decode()
            b = json.loads(urllib.request.urlopen(f'https://mempool.space/api/v1/block/{hx}', timeout=20).read())
            CACHE[k] = dict(ts=b['timestamp'], pool=(b.get('extras') or {}).get('pool', {}).get('name', '?'), tx=b.get('tx_count'), fees=(b.get('extras') or {}).get('totalFees'))
            json.dump(CACHE, open(CACHE_F, 'w'))
        except Exception: return {}
    return CACHE[k]
def stamp(h): return _block(h).get('ts')
seen = set(); clock = []
for w in W:
    whole = w.get('whole', w['height'] not in (970235, 970236))   # rows written before the flag: 970235 (start) and 970236 (restart 17:29) were partial
    t = w.get('t_unix') or D.datetime.fromisoformat(w['t']).timestamp(); sw = (w.get('stopwatch') or {}).get('block_seconds')
    a, b = stamp(w['height'] - 1), stamp(w['height'])
    if whole and sw and a and b and w['height'] not in seen:
        seen.add(w['height']); clock.append(dict(h=w['height'], stated=b - a, ours=sw, lag=t - b))
def blockinfo(h): b = _block(h); return {k: b.get(k) for k in ('pool', 'tx', 'fees')} if b else {}
if clock:
    # THE SEVEN'S LESSONS, APPLIED (6 Oct): two rulers on every reading (per block AND per span -- a stamp's offset cancels across a span); the ruler's own
    # behaviour printed (robust median beside mean, so one stamp cannot carry a fit); outliers are ROWS, never discards (a stamp far off = that miner's maker look,
    # named with its pool); everyone else's clock beside ours (who mined it, how many transactions); our looks counted (hashes); the call for these rows was hashed
    # before this reader ran (darkwave_disco/calls/MINER_ROWS_CALL_20261006.txt).
    st = np.array([c['stated'] for c in clock], float); ou = np.array([c['ours'] for c in clock], float); lag = np.array([c['lag'] for c in clock])
    med = float(np.median(lag)); mad = float(np.median(np.abs(lag - med))) * 1.4826 or 1.0
    print(f'block clock, {len(clock)} whole blocks. RULER 1, per block: ours/stated mean {np.mean(ou / st):.4f}, median {np.median(ou / st):.4f} | lag median {med:.1f} s (robust spread {mad:.1f})')
    hs = [c['h'] for c in clock]; runs, cur = [], [clock[0]]
    for c in clock[1:]:
        if c['h'] == cur[-1]['h'] + 1: cur.append(c)
        else: runs.append(cur); cur = [c]
    runs.append(cur)
    adj = [c for c in clock if c['h'] - 1 in hs]                  # blocks whose predecessor we also witnessed whole: both lags known, the identity checks
    print(f'   RULER 2, the whole span: ours / stated {ou.sum() / st.sum():.4f} over {st.sum():.0f} s | by consecutive runs ({len(runs)} runs; offsets cancel inside each, '
          f'not across gaps): ' + ', '.join(f"{sum(c['ours'] for c in r) / sum(c['stated'] for c in r):.4f}" for r in runs if sum(c['stated'] for c in r) > 0))
    if adj: print(f"   RULER 2b, adjacent blocks only ({len(adj)} with a witnessed predecessor): ours / stated {sum(c['ours'] for c in adj) / sum(c['stated'] for c in adj):.4f}"
                  f" over {sum(c['stated'] for c in adj):.0f} s  (7 Oct, the triangle: one row with no predecessor carried most of the span's excess)")
    for c in clock:
        if abs(c['lag'] - med) > 3 * mad:
            bi = blockinfo(c['h']); c['stamp_row'] = round(med - c['lag'], 1)
            npool = sum(1 for x in clock if blockinfo(x['h']).get('pool') == bi.get('pool'))
            print(f"   STAMP ROW: block {c['h']} stamped {med - c['lag']:+.0f} s from where our clock puts it (pool {bi.get('pool')}: 1 of its {npool} witnessed blocks -- an event, not a policy; {bi.get('tx')} tx) -- kept as a row")
    for c in clock: c.update({k: v for k, v in blockinfo(c['h']).items()})
    json.dump(clock, open(os.path.join(HERE, 'miner_block_clock.json'), 'w'))
import numpy as np
out, means = [], []
for w in W:
    b, bw = mw(w['bonefish'][0], w['bonefish'][1]); k, kw = mw(w['walk'][0], w['walk'][1])
    if b is None: continue
    rulers = f'the plain walk: {k:.3f} bits +- {kw:.3f} bits (best {w["walk"][2]})' if k is not None else ''
    ser = ', '.join(f'{x:.3f} bits' for x in means[-3:])
    split = k is not None and abs(b - k) / math.hypot(bw, kw) > 1.5; moved = len(means) >= 2 and abs(b - means[-1]) / bw > 2
    mode = 'NEXT' if k is None else ('HOLD' if split or moved else 'COMMIT')
    sw = w.get('stopwatch') or {}
    first = f"mean leading zero bits of The Bonefish's nonces on a live Bitcoin header, block height {w['height']}, the Pi: {b:.3f} bits +- {bw:.3f} bits (best {w['bonefish'][2]})" + \
            (f"; our looks timed: first Bonefish look {sw['bonefish_first_ms']:.1f} ms after the job landed, each look {sw['look_ns_median']} ns, the block lasted {sw['block_seconds']} s of our hashing" if sw else '')
    out.append(dict(name=f"miner window {w['t']}", kind='miner', mode=mode, source='~/bonefish_miner/stats.jsonl on the Pi',
                    messages=chat(user_text(first, '1.000 bits (SHA-256 with no structure)', ser, rulers)) + [{'role': 'assistant', 'content': mode}]))
    means.append(b)
# THE STOOGES' TRIANGLE PER BLOCK (6 Oct night): shep (sequential, the reference) against moe / larry / curly -- every seat's mean zero bits and best hash
st_rows = [w for w in W if w.get('stooges') and w.get('whole')]
if st_rows:
    tot = {}
    for w in st_rows:
        for k, v in w['stooges'].items():
            a = tot.setdefault(k, [0, 0, 0]); a[0] += v['samples']; a[1] += v['zero_bits']; a[2] = max(a[2], v['best'])
    print(f"stooges over {len(st_rows)} whole blocks: " + ' | '.join(f"{k} {a[1] / a[0]:.4f} +- {math.sqrt(2 / a[0]):.4f} zero bits (best {a[2]})" for k, a in tot.items() if a[0]))
with open(os.path.join(HERE, 'miner_cases.jsonl'), 'w') as f:
    for r in out: f.write(json.dumps(r) + '\n')
print(f'{len(W)} windows -> {len(out)} miner cases:', {m: sum(r["mode"] == m for r in out) for m in ('COMMIT', 'HOLD', 'NEXT')})
