"""copies.py check|publish [NAME]|live -- the ledger for FILES (23 Oct 2026, his "faults and guards are in three places now ... set it up so it
updates across the board, no over-exposing cloud worker"). copies.json lists every file published in more than one place.
  check    every copy byte-identical to its canonical, and no source edited after its canonical was made  (run by the pre-commit hooks)
  publish  copy each canonical over all its copies (run after rendering a new canonical); then commit + deploy as usual
  live     fetch every public URL and compare it with the canonical (after a deploy)"""
import json, sys, os, hashlib, shutil, urllib.request
B = os.path.expanduser('~/bones-forge'); M = json.load(open(os.path.join(B, 'ledger', 'copies.json')))
P = lambda p: p if p.startswith('/') else os.path.join(B, p)
h = lambda b: hashlib.sha256(b).hexdigest()[:12]
def items(): return [(k, v) for k, v in M.items() if not k.startswith('_') and (len(sys.argv) < 3 or k == sys.argv[2])]
def check():
    bad = 0
    for k, v in items():
        c = open(P(v['canonical']), 'rb').read(); hc = h(c)
        if v.get('source') and os.path.getmtime(P(v['source'])) > os.path.getmtime(P(v['canonical'])) + 1:
            print(f'  STALE    {k}: {v["source"]} edited after {v["canonical"]} was made -- render it'); bad += 1
        for cp in v['copies']:
            if not os.path.exists(P(cp)): print(f'  MISSING  {k}: {cp}'); bad += 1
            elif h(open(P(cp), 'rb').read()) != hc: print(f'  DIFFERS  {k}: {cp} != {v["canonical"]} ({hc})'); bad += 1
    print(f'copies: {sum(len(v["copies"]) + 1 for _, v in items())} files in {len(items())} sets; drift: {bad}'); return bad
def publish():
    for k, v in items():
        for cp in v['copies']: shutil.copy2(P(v['canonical']), P(cp)); print(f'  copied {k} -> {cp}')
    return check()
def live():
    bad = 0
    for k, v in items():
        hc = h(open(P(v['canonical']), 'rb').read())
        for u in v.get('live', []):
            try: b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'copies.py'}), timeout=20).read(); hl = h(b)
            except Exception as e: hl = 'ERR ' + type(e).__name__
            ok = hl == hc; bad += not ok; print(f'  {"LIVE OK " if ok else "LIVE OFF"} {k}: {u} {hl}')
    print(f'live drift: {bad}'); return bad
if __name__ == '__main__':
    sys.exit(1 if {'check': check, 'publish': publish, 'live': live}[sys.argv[1] if len(sys.argv) > 1 else 'check']() else 0)
