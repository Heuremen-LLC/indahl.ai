import json,sys
rows=[json.loads(l) for l in open('/Users/heuremen/bones-forge/ledger/ledger.jsonl')]
surf=sys.argv[1]
for r in rows:
    if r.get('status')!='live': continue
    for s in r['surfaces']:
        if s['surface']==surf:
            print(f"{r['id']}\t{s['text']}")
