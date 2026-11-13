"""preflight.py (6 Nov 2026, Wayfinder: "confirm the emails are live, that's what gets us toasted"). Checks the next N unsent queue items:
live MX for the domain (dig, fresh), not on any bounce list (rolodex, 5 Nov Gmail bounces, every bounced line in send.log), not already
sent to by any channel (rolodex SENT/DELIVERED rows for the same address + same notice subject), not sent by this queue before.
Writes PREFLIGHT_HOLD.json (keys the sender must skip) and prints counts. Run: python3 -I preflight.py N"""
import json, os, sys, subprocess, csv, glob, re, collections
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.expanduser('~/bones-forge/rolodex')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
done = set(open(H + '/sent.progress').read().split())
todo = [it for it in (json.loads(l) for l in open(H + '/queue.jsonl')) if it['key'] not in done][:N]
bounced = {l.strip().lower() for l in open(R + '/BOUNCED_ADDRESSES.txt') if '@' in l}
for f in [H + '/BOUNCED_gmail_20261105.txt'] + glob.glob(R + '/BOUNCES_FULLREAD_*.txt'):
    bounced |= {m.lower() for m in re.findall(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', open(f, errors='ignore').read())}
for l in open(H + '/send.log'):
    if 'bounce' in l.lower() or 'STOPPED' in l: bounced |= {m.lower() for m in re.findall(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', l)}
bounced -= {'indahl@heuremen.com', 'kindahl@heuremen.com'}
sentto = collections.defaultdict(set)
for x in csv.DictReader(open(R + '/rolodex.csv')):
    if x['status'].startswith(('SENT', 'DELIVERED')): sentto[x['address'].lower()].add(x['subject'][:60])
mx = {}
def has_mx(d):
    if d not in mx:
        o = subprocess.run(['dig', '+short', '+time=4', '+tries=2', 'MX', d], capture_output=True, text=True).stdout.strip()
        if not o: o = subprocess.run(['dig', '+short', '+time=4', '+tries=2', 'A', d], capture_output=True, text=True).stdout.strip()   # RFC 5321 implicit MX
        mx[d] = bool(o)
    return mx[d]
hold, why = {}, collections.Counter()
for it in todo:
    for a in [a.lower() for a in it['to']]:
        r = 'bounced before' if a in bounced else 'no mail server' if not has_mx(a.split('@')[1]) else 'already sent this notice' if it['subject'][:60] in sentto.get(a, set()) else None
        if r: hold[it['key']] = f'{a}: {r}'; why[r] += 1; break
json.dump(hold, open(H + '/PREFLIGHT_HOLD.json', 'w'), indent=1)
print(f'checked {len(todo)} next in queue: {len(todo) - len(hold)} clear, {len(hold)} held {dict(why)}')
for k, v in hold.items(): print('  HOLD', k, v)
