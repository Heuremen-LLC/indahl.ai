"""dead_man_block.py -- THE DEAD-MAN IS A TRIANGLE: THE CHAIN NOTICES HER SILENCE (15 Oct 2026, Wayfinder and Bones).
HIS ORDER (/tp VII 4): "a dead-man is a TRIANGLE, not a timer: when her clock stops, another clock in the house is the witness that
notices -- event-driven, never polled." Every rider rides HER tick, so none of them can see her stop. The chain does not ride her:
monerod runs this on EVERY NEW BLOCK (--block-notify '/usr/bin/python3 <this> %s'). Nothing here waits, sleeps or polls.
Each block: count the blocks since her last tick (ticks.log, her stamp is our clock) and write the raw row with its RANK in the
measured record. THE BAR, derived and stated 15 Oct 11:1x: in the last 1500 blocks (50.2 h, 721 of her tick-to-tick gaps) the blocks
between two of her ticks ran 0..7 unbroken (141/182/180/107/55/35/13/4), then jumped to 11, 24, 30, 56 -- four real silences, the
longest 1.8 h. So SILENT_BAR = 7: more blocks than any gap in that unbroken run raises DEAD_MAN.txt (and a FLAG.txt line, which
stays put while she is silent because the bus that rewrites it rides her). Her next tick clears DEAD_MAN.txt and logs that too."""
import json, os, sys, time
W = os.path.dirname(os.path.abspath(__file__))
TICKS = os.path.join(W, 'ticks.log'); ST = os.path.join(W, 'dead_man_state.json'); LOG = os.path.join(W, 'dead_man.jsonl')
DM = os.path.join(W, 'DEAD_MAN.txt'); FLAG = os.path.join(W, 'FLAG.txt')
SILENT_BAR = 7
RECORD = {0: 141, 1: 182, 2: 180, 3: 107, 4: 55, 5: 35, 6: 13, 7: 4, 11: 1, 24: 1, 30: 1, 56: 1}   # n = 721, measured 15 Oct
def rank(n): return sum(v for k, v in RECORD.items() if k >= n)

def last_tick():
    with open(TICKS, 'rb') as f:
        f.seek(0, 2); f.seek(max(0, f.tell() - 4096)); line = f.read().decode(errors='replace').splitlines()[-1].split()
    return int(line[0]), float(line[3])

def main(block_hash):
    s = json.load(open(ST)) if os.path.exists(ST) else {}
    cyc, t = last_tick()
    if cyc != s.get('cycle'):
        s['cycle'] = cyc; s['blocks_since'] = 0
        if os.path.exists(DM):
            os.remove(DM); s['cleared'] = time.strftime('%FT%T')
    else:
        s['blocks_since'] = s.get('blocks_since', 0) + 1
    n = s['blocks_since']
    row = {'at': time.strftime('%FT%T'), 'block': (block_hash or '')[:16], 'her_cycle': cyc, 'her_tick_age_s': round(time.time() - t),
           'blocks_since_her_tick': n, 'as_long_in_record': '%d of 721' % rank(n)}
    if n > SILENT_BAR:
        row['dead_man'] = True
        msg = '[%s] DEAD_MAN: %d blocks since her last tick (cycle %d, %d s ago); %d of 721 measured gaps were this long. The chain noticed.' % (
            time.strftime('%H:%M'), n, cyc, row['her_tick_age_s'], rank(n))
        open(DM, 'w').write(msg + '\n')
        if n == SILENT_BAR + 1:
            open(FLAG, 'a').write(msg + '\n')
    open(LOG, 'a').write(json.dumps(row) + '\n'); json.dump(s, open(ST, 'w'))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '')
