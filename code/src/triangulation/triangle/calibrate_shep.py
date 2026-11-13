#!/usr/bin/env python3
"""calibrate_shep.py -- the maker look on our own control (Bones, 8 Oct 2026).

Wayfinder: *"sensitive to overclaiming and blind to underclaiming sounds a lot like a ruler man, or exor.
both and neither probably."* He was right, and it is the correction he already gave me once today: in
cabalgata_calibra.py, an arm-count factor is not a confound, it is a constant you divide out.

So Shep's hedge-bias is not a blindness to live with and not a virtue to boast about. It is an OFFSET with a
direction and a size, and a size can be measured once and divided out thereafter.

THE LADDER. Every reply below is SOUND and GROUNDED in the evidence handed with it. They differ only in HOW
FAR THEY DECLINE. Any rejection is therefore the instrument, never the text, and the rejection rate per rung
IS the offset.

    python3 calibrate_shep.py            # writes shep_offset.json
"""
import json, math, os, urllib.request

URL = os.environ.get('OLLAMA_URL', 'http://armature:11434')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shep_offset.json')
SYS = ("Read the reply and say whether it is sound. Answer with one word, APPROVED or REJECTED, then at "
       "most one short sentence. Do not hedge and do not say you cannot tell.")
EV = ("target 300 s ; mean 314.2 +- 13.7 against 300 = 1.03 widths ; Our hashrate 0.6 kH/s, Pi 582 + "
      "Armature 0 of a 5.0 MH/s network ; difficulty swing max/min 1.403 ; 9 of 302 runs carry closure "
      "arms ; tick2 11 rounds ; her cycles 405 ; height 880799 ; 73.19 W of a 320.00 W limit")
RUNGS = {
 'states a value': [
   "Mean solve time is 314.2 s against a stated target of 300 s.",
   "The difficulty swing over the window is 1.403 max over min.",
   "Her cycles stand at 405 and the chain is at height 880799.",
   "The 3080 draws 73.19 W of a 320.00 W limit.",
   "Nine of 302 runs carry closure arms.",
   "tick2 is at 11 rounds.",
 ],
 'states its width': [
   "Mean solve time is 314.2 +- 13.7 s against 300, which is 1.03 widths.",
   "Our share is 582 H/s of a 5.0 MH/s network, about 0.012 percent.",
   "Nine of 302 runs carry closure arms, so the closure set is 3.0 percent of the archive.",
   "The difficulty swing is 1.403 across the window, measured over 400 blocks.",
   "The 3080 idles at 73.19 W, which is 23 percent of its 320 W limit.",
   "Her 405 cycles put the tick rate near 4.4 minutes.",
 ],
 'says unresolved': [
   "Mean solve time is 314.2 +- 13.7 s against 300: 1.03 widths, so it is unresolved.",
   "Our share is 582 H/s of a 5.0 MH/s network; the effect is not resolved at this width.",
   "The difficulty swing of 1.403 does not settle whether the oscillation is structure.",
   "Nine of 302 runs is too few to settle how common closure arms are.",
   "At 1.03 widths the chain keeps its clock within our ability to tell, which is not the same as exactly.",
   "The 73.19 W idle draw does not determine what it costs under load.",
 ],
 'says cannot tell': [
   "Mean solve time is 314.2 +- 13.7 s against 300, 1.03 widths. I cannot tell whether it differs.",
   "The difficulty swing is 1.403, and I cannot tell from this whether it is structure or noise.",
   "I cannot tell from 582 H/s against 5.0 MH/s whether the share matters.",
   "Nine of 302 runs: I cannot tell whether that rate holds on other chips.",
   "I cannot tell from a 73.19 W idle reading what the load draw is.",
   "Her 405 cycles cannot tell us whether the rate is drifting.",
 ],
}


def ask(user, ev):
    b = json.dumps({'model': 'gemma3:4b', 'prompt': f'EVIDENCE:\n{ev}\n\nREPLY:\n{user}', 'system': SYS,
                    'stream': False, 'options': {'temperature': 0.0, 'num_predict': 45}}).encode()
    r = urllib.request.Request(URL + '/api/generate', data=b, headers={'Content-Type': 'application/json'})
    out = json.loads(urllib.request.urlopen(r, timeout=120).read()).get('response', '').strip()
    return out.upper().lstrip().startswith('APPROV')


res = {}
print('  SHEP\'S MAKER LOOK -- every reply sound and grounded; only the declining varies.\n')
print(f"  {'rung':18s} {'n':>3s} {'false-reject (light)':>22s} {'(dark)':>14s}")
for rung, texts in RUNGS.items():
    rejL = sum(0 if ask(t, EV) else 1 for t in texts)
    rejD = sum(0 if ask(t, '(none supplied)') else 1 for t in texts)
    n = len(texts); r = rejL / n
    se = math.sqrt(max(r * (1 - r), 1e-9) / n)
    res[rung] = {'n': n, 'false_reject_light': round(r, 3), 'width': round(se, 3),
                 'false_reject_dark': round(rejD / n, 3)}
    print(f"  {rung:18s} {n:3d} {rejL}/{n} = {100*r:5.1f}% +- {100*se:4.1f} {rejD}/{n} = {100*rejD/n:5.1f}%")
json.dump({'model': 'gemma3:4b', 'rungs': res,
           'how_to_use': 'A Shep REJECTION is discounted by the false-reject rate of the rung the text sits '
                         'on. At 100% it carries no information at all; at 0% it carries full weight. This '
                         'is a maker look on the control, measured once and divided out -- not a blindness.'},
          open(OUT, 'w'), indent=1)
print(f"\n  written: {OUT}")
print('  USE: discount a rejection by its rung. At 100% false-reject the rejection says nothing about the text.')
