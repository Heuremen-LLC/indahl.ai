#!/usr/bin/env python3
"""trece.py -- COINYO'S THIRTEEN on the floor (19 Oct 2026, Wayfinder and Bones). Rides COINYOS: one pass per new block.
HIS: "it should be models doing the processing, not pm jobs" / "Thirteen models for thirteen awesome findings" / "we need Coinyo's 13 to disco".
Thirteen models, one per edge (coin/casa/trece/seats.json), on four seats (Mac, Armature, Pi, laptop) -- CPU, so the mining GPUs stay mining.
Each model keeps ONE fixed brief; every block it gets only this block's readings for its edge, so it reads just the new part (the brief's
working state stays loaded in its slot -- the free version of the long-fixed-prompt trick).
This file only CARRIES data: builds each edge's feed, hands it over, writes what comes back. The models do the reading.
Every reading is one of HOLDS / BREAKS / NEITHER / BOTH / CANNOT_TELL; every call is one of COMMITTED / REFUSED / NOTHING_RETURNED.
Writes coin/casa/trece.jsonl (one row per block) and coin/casa/trece_state.json (latest). No odds, no prices."""
import json, os, re, subprocess, sys, threading, time, urllib.request
W = os.path.dirname(os.path.abspath(__file__)); F = os.path.expanduser('~/bones-forge')
C = os.path.join(F, 'coin', 'casa'); CFG = json.load(open(os.path.join(C, 'trece', 'seats.json')))
LOG = os.path.join(C, 'trece.jsonl'); ST = os.path.join(C, 'trece_state.json')
DEADLINE = float(os.environ.get('TRECE_DEADLINE', '55'))   # override only for a cold warm-up; a block is ~60 s; a seat that has not answered by then is NOTHING_RETURNED for this block
NJ = ['ssh', '-i', os.path.expanduser('~/.ssh/outside_seat_ed25519'), '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=6', 'root@64.176.219.98']
STATES = ('HOLDS', 'BREAKS', 'NEITHER', 'BOTH', 'CANNOT_TELL')
ADDR = re.compile(r'\b[R][1-9A-HJ-NP-Za-km-z]{33}\b')

def tail(path, n):
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2); size = f.tell(); f.seek(max(0, size - 200000))
            rows = [l for l in f.read().decode('utf-8', 'replace').splitlines()[1:] if l.strip()]
        out = []
        for l in rows[-n:]:
            try: out.append(json.loads(l))
            except Exception: pass
        return out
    except Exception:
        return []

def jload(path):
    try: return json.load(open(path))
    except Exception: return None

def pick(d, keys): return {k: d.get(k) for k in keys} if isinstance(d, dict) else None

# ---- the feeds: small, raw, this block's readings only ----
CB_TSV = os.path.join(F, 'coin', 'rvn', 'nonces', 'live_coinbase.tsv')
def _cb_rows(n):
    try:
        with open(CB_TSV, 'rb') as f: f.seek(0, 2); f.seek(max(0, f.tell() - 400 * n)); L = f.read().decode('utf8', 'replace').splitlines()[1:]
        return [l.split('\t') for l in L][-n:]
    except Exception: return []
def _diff(bits):   # the chain's own difficulty number for compact bits (diff1 = 0x1d00ffff), a unit change only
    b = int(bits, 16); t = (b & 0xffffff) << (8 * ((b >> 24) - 3)); return round((0xffff << (8 * (0x1d - 3))) / t, 1)
def f_swing(h, x):
    # 19 Oct ~15:40: the courses' live errors only move when a prediction matures (90 blocks on), so this edge was handed the same
    # numbers block after block (council lesson: no input could separate them). It now also gets the swing itself, block by block.
    # A 24-block trail cannot show a swing that lives on a 180-block memory (it read the same every block). The swing's own length:
    # the last 360 blocks in 24 steps of 15 -- each step's difficulty at its end and the mean seconds per block across it.
    r = _cb_rows(361); steps = []
    for i in range(0, len(r) - 15, 15):
        a, b = r[i], r[i + 15]
        steps.append({'to_height': int(b[0]), 'mean_s_per_block': round((int(b[1]) - int(a[1])) / 15, 1), 'difficulty': _diff(b[2])})
    return {'last_360_blocks_in_steps_of_15': steps, 'target_s_per_block': 60,
            'courses': [pick(r, ['tip', 'look_pace_s', 'live_median_err', 'winner']) for r in tail(os.path.join(W, 'big_look.jsonl'), 1)]}
def f_phase(h, x):   return [pick(r, ['tip', 'look_pace_s', 'lanes']) for r in tail(os.path.join(W, 'big_look.jsonl'), 8)]
def f_heartbeat(h, x): return {'maker_look': tail(os.path.join(W, 'maker_look.jsonl'), 2), 'pools_heartbeat': tail(os.path.join(W, 'heartbeat_lane.jsonl'), 2)}
def f_look(h, x):
    looks = [pick(r, ['at', 'who', 'look']) for r in tail(os.path.join(W, 'look_ledger.jsonl'), 6)]
    casa = jload(os.path.join(C, 'casa_state.json')) or {}
    return {'looks': looks, 'rigs': casa.get('hashers'), 'look_rule': 'a look is placed when frac(height/pi) < 0.5', 'frac_height_over_pi': round((h / 3.141592653589793) % 1, 4) if h else None}
def f_nolook(h, x):
    mw = jload(os.path.join(W, 'mining_watch_state.json')) or {}
    casa = jload(os.path.join(C, 'casa_state.json')) or {}
    return {'box': casa.get('hashers'), 'bridge': casa.get('bridge'), 'chain': {k: mw.get(k) for k in ('solo_block', 'node_on_chain', 'mac_hash')}}
def f_bloom(h, x):
    hsh = x.get('hash'); rows = [r for r in tail(os.path.join(F, 'coin', 'p2p', 'p2p_mac.jsonl'), 4000)
                                 if r.get('chain') == 'rvn' and r.get('ev') == 'BLOCK_INV' and r.get('hash') == hsh]
    ts = sorted(r['t_ns'] for r in rows)
    gaps = [round((b - a) / 1e6, 1) for a, b in zip(ts, ts[1:])]
    return {'block_hash': hsh, 'peers_announced': len(ts), 'gaps_ms_in_order': gaps[:40]}
def f_firsthear(h, x):
    fh = tail(os.path.join(W, 'first_hear.jsonl'), 1)
    return {'this_block': tail(os.path.join(W, 'heartbeat_lane.jsonl'), 2), 'first_tellers': pick(fh[0], ['top', 'conns', 'held']) if fh else None,
            'note': 'times are seconds after the network first word; ours = when our cards got the new job'}
def f_null(h, x):
    bl = tail(os.path.join(W, 'big_look.jsonl'), 2)
    return {'courses': [pick(r, ['tip', 'live_median_err', 'winner', 'scored_total']) for r in bl],
            'box_vs_outside': [pick(r, ['worker', 'box_shares', 'pool_moved', 'box_minus_pool_s']) for r in tail(os.path.join(W, 'gap_ledger.jsonl'), 3)]}
NT = ['ssh', '-i', os.path.expanduser('~/.ssh/novatable_key'), '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=6', 'wayfinder@192.168.8.140']
BRIDGE_READ = r'''
import json,time
t0=time.time()-120; rows=[]
for l in open(__import__("os").path.expanduser("~/rvn/bridge.jsonl"),errors="replace").readlines()[-1500:]:
    try: d=json.loads(l)
    except Exception: continue
    if d.get("ev")=="SHARE" and d.get("t",0)>t0: rows.append(d)
nz=lambda g:len(g)-len(g.lstrip("0")) if g else None
seen={}; 
for d in rows: seen.setdefault(d.get("nonce"),[]).append(d.get("job"))
best=sorted([d.get("digest") for d in rows if d.get("digest")])[:3]
print(json.dumps({"window_s":120,"shares":len(rows),"unique_nonces":len(seen),"same_nonce_again":sum(len(v)-1 for v in seen.values()),
 "stale_job":sum(1 for d in rows if d.get("outcome")=="STALE_JOB"),"check_failed":sum(1 for d in rows if d.get("outcome")=="CHECK_FAILED"),
 "node_said_block":sum(1 for d in rows if str(d.get("node_says")).lower()=="true"),"best_digests":best,"best_leading_zero_hex":[nz(g) for g in best]}))
'''
def f_nearmiss(h, x):
    """19 Oct: was coin/rvn/shares.jsonl -- the RETIRED pool's counts (all zero while the rigs hashed into our bridge). Now the bridge's own shares."""
    casa = jload(os.path.join(C, 'casa_state.json')) or {}
    try:
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'armature', 'python -'], input=BRIDGE_READ, capture_output=True, text=True, timeout=12)
        lane = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else {'outcome': 'NOTHING_RETURNED'}
    except Exception as e:
        lane = {'outcome': 'CANNOT_TELL', 'why': type(e).__name__}
    return {'bridge_shares_last_2min': lane, 'house_mh': casa.get('house_mh'), 'note': 'a share is a guess that met the share target but not the block target'}
def f_bigpools(h, x): return [pick(r, ['tip', 'groups_now', 'winner', 'lanes']) for r in tail(os.path.join(W, 'big_look.jsonl'), 3)]
def f_wake(h, x):     return [pick(r, ['tip', 'wake_ratio_2h', 'lanes', 'live_median_err', 'groups_now']) for r in tail(os.path.join(W, 'big_look.jsonl'), 4)]
def f_headers(h, x):
    hb = tail(os.path.join(W, 'heartbeat_lane.jsonl'), 1)
    return {'nj_header': x.get('nj'), 'network_and_jobs': hb[0] if hb else None}
def f_hashnum(h, x):
    nj = x.get('nj') or {}
    out = {'height': h, 'block_hash': x.get('hash'), 'header_raw': nj.get('raw'), 'bits': nj.get('bits'), 'time': nj.get('time')}
    # 19 Oct ~15:40: raw hex cannot be laid beside 0.618 by eye (11 of 11 NEITHER). Carried as plain numbers too, unit changes only:
    try:
        b = int(nj['bits'], 16); t = (b & 0xffffff) << (8 * ((b >> 24) - 3)); out['hash_share_of_target'] = round(int(x['hash'], 16) / t, 6)
    except Exception: pass
    try:
        n64 = next((r[3] for r in _cb_rows(6) if int(r[0]) == h), None)
        if n64: out['nonce64'] = n64; out['nonce_place_in_range'] = round(int(n64, 16) / 2 ** 64, 6)
    except Exception: pass
    return out
FEEDS = {'swing': f_swing, 'phase': f_phase, 'heartbeat': f_heartbeat, 'look': f_look, 'nolook': f_nolook, 'bloom': f_bloom,
         'firsthear': f_firsthear, 'null': f_null, 'nearmiss': f_nearmiss, 'bigpools': f_bigpools, 'wake': f_wake, 'headers': f_headers, 'hashnum': f_hashnum}

def nj_header(h):
    """NJ's ear logs every header whole: first arrival of THIS height's header, from how many peers."""
    if not h: return None
    try:
        r = subprocess.run(NJ + [f'tail -6000 /root/seat/p2p_newjersey.jsonl | grep BLOCK_HDR | grep \'"height": {h},\''], capture_output=True, text=True, timeout=10)
        rows = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
        if not rows: return {'outcome': 'NOTHING_RETURNED'}
        rows.sort(key=lambda d: d['t_ns'])
        return {'first_heard_t': round(rows[0]['t_ns'] / 1e9, 3), 'peers': len({d['peer'] for d in rows}), 'raw': rows[0].get('raw'),
                'bits': rows[0].get('bits'), 'time': rows[0].get('time'), 'spread_ms': round((rows[-1]['t_ns'] - rows[0]['t_ns']) / 1e6, 1)}
    except Exception as e:
        return {'outcome': 'CANNOT_TELL', 'why': type(e).__name__}

def ask(seat, edge, e, payload, prev, out):
    t0 = time.time(); S = CFG['seats'][seat]
    system = CFG['house_rules'] + '\n\nYOUR EDGE -- ' + e['name'] + ':\n' + e['brief']
    prompt = f'BLOCK {payload["height"]}\nYOUR LAST READING: {prev or "none yet"}\nTHIS BLOCK\'S READINGS:\n' + ADDR.sub('<ADDR>', json.dumps(payload['feed'], separators=(',', ':')))
    body = {'model': e['model'], 'system': system, 'prompt': prompt, 'stream': False, 'keep_alive': -1,
            'options': {'num_ctx': 4096, 'num_predict': 120, 'temperature': 0.2, 'num_gpu': S['num_gpu'], 'num_thread': S['num_thread']}}
    if e['model'].startswith('qwen3'): body['think'] = False
    try:
        left = DEADLINE - (time.time() - out['_t0'])
        if left < 3: out[edge] = {'outcome': 'NOTHING_RETURNED', 'why': 'no time left this block (seat busy with the edges before it)'}; return
        r = urllib.request.urlopen(urllib.request.Request(S['url'] + '/api/generate', json.dumps(body).encode(), {'Content-Type': 'application/json'}), timeout=left)
        d = json.loads(r.read()); txt = (d.get('response') or '').strip(); txt_raw = txt
        txt = re.sub(r'[*_`#]+', '', txt)   # markdown dressing off before reading the form (ministral bolds its lines)
        m = re.search(r'STATE:\s*([A-Z_]+)', txt); rd = re.search(r'READ:\s*(.+)', txt); od = re.search(r'ODD:\s*(.+)', txt)
        st = m.group(1) if m else None
        if not st:   # a bare state word alone on the first line is the answer, just off the label (kept as 'form': 'BARE')
            first = (txt.splitlines() or [''])[0].strip().strip('*').strip()
            if first in STATES: st = first
        form = 'LABELLED' if m else ('BARE' if st else 'OFF_FORM')
        row = {'state': st if st in STATES else 'CANNOT_TELL', 'read': rd.group(1).strip()[:300] if rd else None, 'odd': od.group(1).strip()[:300] if od else None,
               'outcome': 'COMMITTED' if st in STATES else 'REFUSED', 'form': form, 'seat': seat, 'model': e['model'], 's': round(time.time() - t0, 1),
               'prompt_n': d.get('prompt_eval_count'), 'prompt_ms': round((d.get('prompt_eval_duration') or 0) / 1e6), 'gen_ms': round((d.get('eval_duration') or 0) / 1e6)}
        if form != 'LABELLED': row['raw'] = txt_raw[:300]   # answered off the three-line form -- kept, never coerced into a state
        out[edge] = row
    except Exception as ex:
        out[edge] = {'outcome': 'NOTHING_RETURNED', 'why': f'{type(ex).__name__}: {str(ex)[:120]}', 'seat': seat, 'model': e['model'], 's': round(time.time() - t0, 1)}

MINERS = ('mac', 'armature')   # seats that also hash: in a STRIKE tide nothing extra runs on them
def tide():
    try:
        m = json.load(open(os.path.join(C, 'marea.json')))
        return m.get('tide') if time.time() - m.get('t', 0) < 600 else 'CANNOT_TELL'
    except Exception:
        return 'CANNOT_TELL'

def run_seat(seat, edges, payloads, prev, out):
    if out.get('_tide') == 'STRIKE' and seat in MINERS:
        for edge in edges: out[edge] = {'outcome': 'HELD', 'why': 'STRIKE tide: the miners stay untouched', 'seat': seat, 'model': CFG['edges'][edge]['model']}
        return
    for edge in edges:   # one seat answers its edges in turn (all its threads on one model at a time)
        ask(seat, edge, CFG['edges'][edge], payloads[edge], prev.get(edge), out)

def main():
    h = os.environ.get('COINYOS_HEIGHT'); h = int(h) if h and h.isdigit() else None
    x = {'hash': os.environ.get('COINYOS_HASH')}; x['nj'] = nj_header(h)
    prev = {}
    try: prev = {k: (f"{v.get('state')} -- {v.get('read')}" if v.get('outcome') == 'COMMITTED' else None) for k, v in (jload(ST) or {}).get('readings', {}).items()}
    except Exception: pass
    payloads = {}
    for edge, e in CFG['edges'].items():
        try: payloads[edge] = {'height': h, 'feed': FEEDS[e['feed']](h, x)}
        except Exception as ex: payloads[edge] = {'height': h, 'feed': {'outcome': 'CANNOT_TELL', 'why': f'feed failed: {type(ex).__name__}'}}
    by_seat = {}
    for edge, e in CFG['edges'].items(): by_seat.setdefault(e['seat'], []).append(edge)
    for seat, order in ((k[:-6], v) for k, v in CFG.items() if k.endswith('_order')):   # a seat's answer order, when the map sets one
        if seat in by_seat: by_seat[seat] = [e for e in order if e in by_seat[seat]] + [e for e in by_seat[seat] if e not in order]
    out = {'_t0': time.time(), '_tide': tide()}
    th = [threading.Thread(target=run_seat, args=(s, eds, payloads, prev, out), daemon=True) for s, eds in by_seat.items()]
    for t in th: t.start()
    for t in th: t.join(DEADLINE + 5)
    readings = {e: out.get(e, {'outcome': 'NOTHING_RETURNED', 'why': 'seat thread still running at the deadline'}) for e in CFG['edges']}
    row = {'at': time.strftime('%FT%T'), 'height': h, 'hash': x['hash'], 'tide': out['_tide'], 'readings': readings,
           'tally': {s: sum(1 for r in readings.values() if r.get('state') == s and r.get('outcome') == 'COMMITTED') for s in STATES},
           'outcomes': {o: sum(1 for r in readings.values() if r.get('outcome') == o) for o in ('COMMITTED', 'HELD', 'REFUSED', 'NOTHING_RETURNED')},
           'took_s': round(time.time() - out['_t0'], 1)}
    with open(LOG, 'a') as f: f.write(json.dumps(row) + '\n')
    # OY'S CORPUS (his, 19 Oct: "set the training loop up as we're wiring it"): the raw inputs each edge got this block, beside
    # what the thirteen said (trece.jsonl). The chain's own numbers, not the token models' words, are what Oy learns from.
    with open(os.path.join(C, 'trece_feeds.jsonl'), 'a') as f: f.write(json.dumps({'height': h, 'hash': x['hash'], 'at': row['at'], 'nj': x['nj'], 'feeds': {e: p['feed'] for e, p in payloads.items()}}) + '\n')
    json.dump(row, open(ST + '.tmp', 'w'), indent=1); os.replace(ST + '.tmp', ST)

if __name__ == '__main__':
    main()
