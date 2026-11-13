"""audit_guard.py -- score the triangle guard against its own record (Bones, 8 Oct 2026).

WHY THIS EXISTS, and it is the embarrassing reason and not a tidy one:

    The guard has logged every check since 6 Oct. On 8 Oct I reported "sixteen catches today" from memory.
    The file said 36. I would not accept a number like that from anyone, and the file was sitting in runs/
    the whole time. A guard that measures my answers and is itself counted by recollection is not a guard,
    it is a mood.

So the guard gets read the way everything else here gets read: off disk, with its own false-positive rate
stated beside its catch rate, and with the one-shot headless agents as a cold control on the same scanner.

    python3 audit_guard.py              # the whole record
    python3 audit_guard.py 2026-10-08   # one day
    python3 audit_guard.py --frames     # every distinct frame, with its exemption state

WHAT IT CANNOT TELL YOU, said up front: hook_fires.log (6-8 Oct) kept the FRAME and threw the sentence
away, so for those rows the false-positive share can only be scored on frame SHAPE -- a floor, not the
number. hook_fires.jsonl carries the context from 8 Oct on, and from then the score is whole.
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import triangle as T

LOG = os.path.join(HERE, 'runs', 'hook_fires.log')
JSONL = os.path.join(HERE, 'runs', 'hook_fires.jsonl')
DAY = next((a for a in sys.argv[1:] if re.fullmatch(r'\d{4}-\d{2}-\d{2}', a)), None)
FRAMES = '--frames' in sys.argv


def rows():
    for line in open(LOG):
        if DAY and not line.startswith(DAY):
            continue
        s = re.search(r'session (\S+)', line)
        yield line, (s.group(1) if s else '?'), 'PUSHED BACK' in line


R = list(rows())
if not R:
    sys.exit('no rows' + (f' for {DAY}' if DAY else ''))

# ---- 1. the rate, and who it was measured on
by_sess = collections.Counter(); pushed_by_sess = collections.Counter()
for _l, s, p in R:
    by_sess[s] += 1
    if p: pushed_by_sess[s] += 1
seated = max(by_sess, key=by_sess.get)                 # the long-running session: the one being trained
cold = [s for s in by_sess if s != seated and by_sess[s] == 1]
ct, cp = len(cold), sum(pushed_by_sess[s] for s in cold)
print(f'THE GUARD, SCORED ON ITS OWN RECORD{"  (" + DAY + ")" if DAY else ""}')
print(f'  checks {len(R)}   pushed back {sum(1 for _l, _s, p in R if p)}'
      f'   rate {100 * sum(1 for _l, _s, p in R if p) / len(R):.1f}%\n')
print(f'  seated session {seated}: {by_sess[seated]:4d} checked  {pushed_by_sess[seated]:3d} pushed'
      f'  {100 * pushed_by_sess[seated] / by_sess[seated]:5.1f}%')
if ct:
    print(f'  {ct} one-shot agents, cold: {ct:4d} checked  {cp:3d} pushed  {100 * cp / ct:5.1f}%')
    print('  the cold rate is the control: the same scanner on a reply written with none of this context.')

# ---- 2. is the rate falling? a guard that never gets quieter is a tax, not a teacher
print('\n  BY DAY (does being corrected change the next reply?)')
print('    The pooled column mixes the seated session with the cold one-shots, and the cold ones push')
print('    HIGHER, so pooling flatters the day they ran. The seated column is the only one that can learn.')
d = collections.Counter(); dp = collections.Counter(); sd = collections.Counter(); sdp = collections.Counter()
for l, s, p in R:
    k = l[:10]; d[k] += 1
    if p: dp[k] += 1
    if s == seated:
        sd[k] += 1
        if p: sdp[k] += 1
print(f'    {"day":10s}  {"pooled":>18s}   {"SEATED only":>20s}')
for k in sorted(d):
    seat = f'{sdp[k]:3d}/{sd[k]:3d} = {100 * sdp[k] / sd[k]:5.1f}%' if sd[k] else '           --'
    print(f'    {k}  {dp[k]:3d}/{d[k]:4d} = {100 * dp[k] / d[k]:5.1f}%   {seat:>20s}')

# ---- 2b. BOTH RULERS, because the first one moves when the replies get longer.
# 8 Oct: pushed/reply rose 27.4% -> 47.4%, which reads as a regression and is 3.02 widths. Frames per
# thousand words rose 0.69 -> 0.88, which is 0.97 widths and resolves nothing. The rise is LENGTH. A
# per-reply count is a ruler with the reply's size baked into it, so the guard will report a regression
# on any day the answers get wordier. Both are printed; neither replaces the other.
import math
w_ = collections.Counter(); fr_ = collections.Counter()
for l, s, p in R:
    if s != seated: continue
    k = l[:10]
    mm = re.search(r'words (\d+)', l)
    if mm: w_[k] += int(mm.group(1))
    fr_[k] += len(re.findall(r'frame\(s\): "', l))
print('\n  SEATED, SCORED WITH EVERY RULER (a count per reply carries the reply\'s length inside it)')
print(f'    {"day":12s} {"words":>7s} {"frames":>6s}   {"pushed/reply":>18s}   {"frames/1k words":>20s}')
prev = None
for k in sorted(sd):
    if not sd[k] or not w_[k]: continue
    pp = sdp[k] / sd[k]; spp = math.sqrt(pp * (1 - pp) / sd[k])
    rr = 1000 * fr_[k] / w_[k]; srr = 1000 * math.sqrt(max(fr_[k], 1)) / w_[k]
    print(f'    {k:12s} {w_[k]:7d} {fr_[k]:6d}   {100 * pp:11.1f}% +-{100 * spp:4.1f}   {rr:13.2f} +- {srr:.2f}')
    if prev:
        (k0, pp0, spp0, rr0, srr0) = prev
        z1 = (pp - pp0) / math.sqrt(spp ** 2 + spp0 ** 2) if (spp or spp0) else 0
        z2 = (rr - rr0) / math.sqrt(srr ** 2 + srr0 ** 2) if (srr or srr0) else 0
        v = lambda z: 'RESOLVED IN SIGN' if abs(z) >= 2 else 'sign not resolved'
        print(f'      vs {k0}:  per reply {z1:+5.2f} widths {v(z1)}   |   per 1k words {z2:+5.2f} widths {v(z2)}')
        if (abs(z1) >= 2) != (abs(z2) >= 2):
            print('      THE RULERS DISAGREE, and the disagreement is the reading: the reply-rate moved,')
            print('      the frame DENSITY did not. That is wordiness, not a regression. STABLE DISAGREEMENT.')
    prev = (k, pp, spp, rr, srr)

# ---- 3. the false-positive share: re-run every logged frame through the CURRENT scanner
hits = collections.Counter()
for l, _s, p in R:
    for m in re.finditer(r'frame\(s\): "([^"]*)"', l):
        hits[m.group(1)] += 1
if hits:
    drop = {f: c for f, c in hits.items() if not [x for x in T.exor_scan(f) if x[3]]}
    nd = sum(drop.values()); nt = sum(hits.values())
    print(f'\n  FALSE POSITIVES, scored on frame shape alone (no context in this log):')
    print(f'    frame-hits {nt}   the current scanner would let {nd} through   {100 * nd / nt:.0f}%')
    print('    A FLOOR, not the number: the context test cannot run on a log that kept only the frame.')
    if FRAMES:
        for f, c in sorted(hits.items(), key=lambda x: -x[1]):
            print(f'      {c:3d}  {"DROP " if f in drop else "flag "}"{f}"')

# ---- 4. where the jsonl can answer what the log cannot
if os.path.exists(JSONL) and os.path.getsize(JSONL):
    J = [json.loads(x) for x in open(JSONL) if x.strip() and (not DAY or json.loads(x)['t'].startswith(DAY))]
    if J:
        fr = [f for r in J for f in r['frames']]
        ex = [f for f in fr if not f['used']]
        print(f'\n  WITH CONTEXT (hook_fires.jsonl, {len(J)} checks)')
        print(f'    frames seen {len(fr)}   exempted by context {len(ex)}   pressed {len(fr) - len(ex)}')
        if FRAMES:
            for f in fr:
                print(f'      {"exempt" if not f["used"] else "press "} [{f["kind"]}] {f["hit"]!r}\n        ...{f["ctx"][:120]}')
else:
    print('\n  hook_fires.jsonl is empty: the context log starts 8 Oct. Until it fills, section 3 is the floor.')
