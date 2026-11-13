"""quake_score.py: the headline cell of quake_index/quake_tick.py (constants, lines 17 to 18, cover_outcome(), lines 60 to 65, the blocks and the
seeded draws, lines 328 to 330, boot() and cover_cell(), lines 331 to 348, and headline_cell, line 360), as written. The rows are the scored rows
that run wrote to data/quake_rows.json.gz. The block list covers every sequence the run read, so it is taken from the sequences block of
summary_quake.json, and the gate result from its gates block. Writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, gzip, math, random, collections as C
import heuremen_kit as K
BOOT = 2000; SEED = 20261110
COVER_CLAIM = 0.95; COVER_BAND = (0.925, 0.975); MIN_ROWS = 30; MIN_BLOCKS = 10
S = json.load(open('summary_quake.json')); GATE = bool(S['gates']['passed'])
rows = json.loads(gzip.open('data/quake_rows.json.gz').read())['rows']
def cover_outcome(lo, hi, n, nb):
    if n < MIN_ROWS or nb < MIN_BLOCKS: return K.CANNOT_TELL
    if hi < COVER_CLAIM: return K.BELOW
    if lo > COVER_CLAIM: return K.ABOVE
    if lo >= COVER_BAND[0] and hi <= COVER_BAND[1]: return K.CONSISTENT
    return K.CANNOT_TELL
SC = [r for r in rows if r['status'] == 'scored']
BLOCKS = sorted(set(q['block'] for q in S['sequences'])); BI = {b: i for i, b in enumerate(BLOCKS)}; NB = len(BLOCKS)
rng = random.Random(SEED); DRAWS = [[rng.randrange(NB) for _ in range(NB)] for _ in range(BOOT)]
def boot(kb, nb):
    sh = []
    for d in DRAWS:
        k = sum(kb[i] for i in d); n = sum(nb[i] for i in d)
        if n: sh.append(k / n)
    if len(sh) < 0.9 * BOOT: return None, None
    sh.sort(); return sh[int(math.floor(0.025 * (len(sh) - 1)))], sh[int(math.ceil(0.975 * (len(sh) - 1)))]
def cover_cell(name, rs):
    rs = [r for r in rs if r['kind'] == 'bin']; kb = [0] * NB; nb = [0] * NB; cnt = C.Counter(r['outcome'] for r in rs)
    for r in rs:
        i = BI[r['block']]; nb[i] += 1; kb[i] += r['outcome'] == K.CONSISTENT
    n = sum(nb); k = sum(kb); wl, wh = K.wilson(k, n); bl, bh = boot(kb, nb) if n else (None, None)
    lo = min(wl, bl) if bl is not None else wl; hi = max(wh, bh) if bh is not None else wh
    nblk = sum(1 for x in nb if x); nseq = len(set(r['seq'] for r in rs))
    o = cover_outcome(lo, hi, n, nblk) if GATE and bl is not None else K.CANNOT_TELL
    return dict(cell=name, scored=n, inside=k, above=cnt[K.ABOVE], below=cnt[K.BELOW], share=round(k / n, 4) if n else None, wilson=[round(wl, 4), round(wh, 4)],
                boot=[round(bl, 4), round(bh, 4)] if bl is not None else None, lo=round(lo, 4), hi=round(hi, 4), claim=COVER_CLAIM, outcome=o, sequences=nseq, blocks=nblk)
BIN = [r for r in SC if r['kind'] == 'bin']
json.dump(dict(headline_cell=cover_cell('M3 and above, every window', [r for r in BIN if r['mag'] == 3.0])), open('out.json', 'w'), indent=1)
