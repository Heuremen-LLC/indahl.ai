#!/usr/bin/env python3
"""yo_tide.py -- YO trains only when it's dear (19 Oct 2026, Wayfinder and Bones). Rides COINYOS: one look at the tide per block.
HIS: "when the tide is pulling back and it's a high difficulty time we do this shit, but when that moment comes we need Coinyo to strike."
YO (Qwen3-1.7B LoRA, coin/yo/) trains on the Mac's GPU, which the Mac's miner also uses (training cost the Mac ~15% of its hash in the
smoke test). So: tide STRIKE (cheap) -> the trainer is FROZEN in place (SIGSTOP: GPU released at once, nothing lost); tide LOOK (dear) ->
it carries on (SIGCONT). Unknown tide -> frozen (the miner comes first). Every change is one row in coin/yo/yo_tide.jsonl.
19 Oct: THE BRACKET (coin/yo/bracket_plan.json) -- see bracket_rule(); every bracket block is one row in coin/yo/bracket.jsonl."""
import json, math, os, signal, subprocess, sys, time
Y = os.path.expanduser('~/bones-forge/coin/yo'); PID = os.path.join(Y, 'trainer.pid'); LOG = os.path.join(Y, 'yo_tide.jsonl')
MAREA = os.path.expanduser('~/bones-forge/coin/casa/marea.json')
BRACKET = os.path.join(Y, 'bracket.json'); BLOG = os.path.join(Y, 'bracket.jsonl')   # 19 Oct (his /tp + "hit it!"): THE BRACKET

def bracket_rule(h):
    """THE BRACKET (coin/yo/bracket_plan.json, fixed before it ran): inside its blocks, in a LOOK tide only, YO is FROZEN when
    frac(floor(h / seg) / pi) < 0.5 and THAWED otherwise. Returns (active, frozen) -- active False outside the bracket's blocks."""
    try: b = json.load(open(BRACKET))
    except Exception: return False, None, None
    if not h or not (b['start_height'] <= h < b['start_height'] + b['blocks']): return False, None, b
    return True, ((math.floor(h / b['seg']) / math.pi) % 1.0) < 0.5, b

def state(pid):
    try:
        with open(f'/proc/{pid}/stat') as f: return f.read().split()[2]
    except Exception:
        import subprocess
        r = subprocess.run(['ps', '-o', 'stat=', '-p', str(pid)], capture_output=True, text=True)
        return r.stdout.strip() or None

def main():
    try: pid = int(open(PID).read().strip())
    except Exception: return
    st = state(pid)
    if not st: return                                   # no trainer running: nothing to steer
    try:
        m = json.load(open(MAREA)); tide = m.get('tide') if time.time() - m.get('t', 0) < 600 else 'CANNOT_TELL'
    except Exception: tide = 'CANNOT_TELL'
    frozen = st.startswith('T')
    want_frozen = tide != 'LOOK'; why = 'tide'
    try: h = int(os.environ.get('COINYOS_HEIGHT') or 0)
    except ValueError: h = 0
    active, b_frozen, b = bracket_rule(h)
    if active and tide == 'LOOK':                       # the bracket only ever steers inside a LOOK tide; STRIKE/unknown stay frozen
        want_frozen = b_frozen; why = 'bracket'
    elif b and not active and h and h >= b['start_height'] + b['blocks'] and not b.get('ended_at_height'):
        why = 'bracket_end'                             # the first block after the bracket: back to the tide, and launch the read once
        b['ended_at_height'] = h; json.dump(b, open(BRACKET + '.tmp', 'w'), indent=1); os.replace(BRACKET + '.tmp', BRACKET)
        subprocess.Popen([sys.executable, os.path.join(Y, 'bracket_read.py'), '--read'], stdout=open(os.path.join(Y, 'bracket_read.log'), 'a'),
                         stderr=subprocess.STDOUT, start_new_session=True)
    act = 'FROZE' if (want_frozen and not frozen) else 'THAWED' if (not want_frozen and frozen) else None
    if act == 'FROZE': os.kill(pid, signal.SIGSTOP)
    elif act == 'THAWED': os.kill(pid, signal.SIGCONT)
    now = time.time()
    if active or why == 'bracket_end':
        with open(BLOG, 'a') as f: f.write(json.dumps({'height': h, 't': round(now, 3), 'tide': tide, 'want_frozen': want_frozen, 'was_frozen': frozen,
                                                        'act': act, 'why': why, 'pid': pid}) + '\n')
    if act is None: return
    with open(LOG, 'a') as f: f.write(json.dumps({'at': time.strftime('%FT%T'), 't': round(now, 3), 'height': h, 'tide': tide, 'act': act, 'why': why, 'pid': pid}) + '\n')

if __name__ == '__main__':
    main()
