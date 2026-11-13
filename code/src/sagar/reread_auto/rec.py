"""rec.py: append Bones re-read verdicts for verified_auto items. stdin: lines 'NNN|PRESENT|ABSENT|CANNOT_TELL|basis'."""
import json,sys,time
items=json.load(open('/Users/heuremen/bones-forge/sagar/reread_auto/items.json'))
done={json.loads(l)['n'] for l in open('verdicts.jsonl')} if __import__('os').path.exists('verdicts.jsonl') else set()
with open('verdicts.jsonl','a') as f:
    for ln in sys.stdin:
        if not ln.strip(): continue
        n,v,b=ln.strip().split('|',2); n=int(n); x=items[n]
        assert v in ('PRESENT','ABSENT','CANNOT_TELL'); assert n not in done, n
        f.write(json.dumps({'n':n,'arxiv':x['arxiv'],'code':x['code'],'bones':v,'basis':b,'severity':x.get('severity'),'date':time.strftime('%Y-%m-%dT%H:%M')})+'\n')
print(sum(1 for _ in open('verdicts.jsonl')),'recorded')
