"""pull_blocks.py -- the public record: the last N Bitcoin blocks' winning nonces, timestamps, heights (mempool.space, read-only, no wallet)."""
import json, sys, time, urllib.request
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
tip = int(urllib.request.urlopen('https://mempool.space/api/blocks/tip/height').read())
out, h = [], tip
while len(out) < N:
    bl = json.loads(urllib.request.urlopen(f'https://mempool.space/api/v1/blocks/{h}').read())
    out += [dict(height=b['height'], nonce=b['nonce'], ts=b['timestamp'], bits=b['bits'], version=b['version']) for b in bl]
    h = bl[-1]['height'] - 1; time.sleep(0.25)
out = sorted(out[:N], key=lambda b: b['height'])
json.dump(out, open('blocks.json', 'w')); print(len(out), 'blocks', out[0]['height'], '->', out[-1]['height'])
