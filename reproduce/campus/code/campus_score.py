"""campus_score.py: the state_now step of campus_index/campus_tick.py (stnow(), lines 126 to 131, and state_now and sources in out, lines 136 to 138),
as written, over the items of the newest pass in data/reads.jsonl. Writes out.json."""
import json, collections
last = None
for l in open('data/reads.jsonl'):
    if l.strip(): last = json.loads(l)
items = last['items']
def stnow(it):
    s = it['status']
    if s == 200: return 'resolves'
    if s in (401, 403, 429): return 'blocked'
    if s in (404, 410): return 'gone'
    return 'error'
now_c = collections.Counter(stnow(v) for v in items.values())
json.dump(dict(sources=len(items), state_now={'Opens (HTTP 200)': now_c['resolves'], 'Blocked (401, 403, 429)': now_c['blocked'], 'Not found (404, 410)': now_c['gone'], 'Other error or no answer': now_c['error']}), open('out.json', 'w'), indent=1)
