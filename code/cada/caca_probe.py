#!/usr/bin/env python3
"""caca_probe.py: one CACA round per PLAN.md, run by Nova's tick bus as a rider. Reads two public feeds, finds domains that are new since our last read,
asks controls and filtered resolvers about them at first sight and at 1 h, 6 h and 24 h, appends every answer to data/queries.jsonl.
DNS queries only. Stdlib only. usage: caca_probe.py [--validate N]"""
import os, sys, json, time, random, socket, struct, urllib.request, ipaddress
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); os.makedirs('data', exist_ok=True)
FEEDS = {'phishing_database': 'https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-ACTIVE.txt', 'cert_pl': 'https://hole.cert.pl/domains/v2/domains.txt'}
CONTROLS = {'cloudflare_1.1.1.1': '1.1.1.1', 'quad9_unfiltered': '9.9.9.10', 'google_8.8.8.8': '8.8.8.8'}
FILTERED = {'cloudflare_malware_1.1.1.2': '1.1.1.2', 'quad9_9.9.9.9': '9.9.9.9', 'opendns': '208.67.222.222', 'adguard_default': '94.140.14.14', 'cleanbrowsing_security': '185.228.168.9', 'dns0_eu': '193.110.81.0', 'controld_malware': '76.76.2.1'}
CPS = [0, 3600, 21600, 86400]; CAP = 40; BLOCKPAGE = [ipaddress.ip_network('146.112.61.0/24')]
def dns(server, name):
    q = os.urandom(2); pkt = q + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + b''.join(bytes([len(p)]) + p.encode() for p in name.split('.')) + b'\x00\x00\x01\x00\x01'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(3)
    try: s.sendto(pkt, (server, 53)); d, _ = s.recvfrom(1500)
    except Exception: return 'TIMEOUT', []
    finally: s.close()
    if d[:2] != q: return 'TIMEOUT', []
    rc = d[3] & 15; an = struct.unpack('!H', d[6:8])[0]; i = 12
    while d[i]: i += d[i] + 1
    i += 5; ips = []
    for _ in range(an):
        while d[i] and not d[i] & 0xC0: i += d[i] + 1
        i += 2 if d[i] & 0xC0 else 1
        t, _, _, l = struct.unpack('!HHIH', d[i:i + 10]); i += 10
        if t == 1 and l == 4: ips.append('.'.join(str(x) for x in d[i:i + 4]))
        i += l
    if rc == 3: return 'NXDOMAIN', []
    if rc == 5: return 'REFUSED', []
    if rc == 2: return 'SERVFAIL', []
    if rc == 0 and ips:
        sink = [ip for ip in ips if ipaddress.ip_address(ip).is_unspecified or ipaddress.ip_address(ip).is_loopback or any(ipaddress.ip_address(ip) in n for n in BLOCKPAGE)]
        return ('SINK' if sink else 'ANSWERED'), ips
    return 'NODATA', []
def feed(name, url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'heuremen-caca/0.1 (+https://indahl.ai)'}), timeout=120) as r: t = r.read().decode('utf-8', 'replace')
    except Exception as e: return None
    out = set()
    for l in t.splitlines():
        l = l.strip().lower()
        if not l or l[0] in '#;!': continue
        l = l.split()[-1]; 
        try: ipaddress.ip_address(l); continue
        except ValueError: pass
        if '.' in l and len(l) < 200: out.add(l)
    return out
def ask(domain, cp, tag):
    now = time.time(); rows = []
    for grp, rs in (('control', CONTROLS), ('filtered', FILTERED)):
        for n, ip in rs.items():
            c, ips = dns(ip, domain); rows.append(dict(at=now, domain=domain, cp=cp, group=grp, resolver=n, cls=c, ips=ips, **tag))
    return rows
def main():
    st = json.load(open('data/state.json')) if os.path.exists('data/state.json') else dict(domains={}, feeds={})
    validate = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == '--validate' else 0; now = time.time(); log = open('data/feed_reads.jsonl', 'a')
    for name, url in FEEDS.items():
        cur = feed(name, url)
        if cur is None: log.write(json.dumps(dict(at=now, feed=name, status='NOTHING_RETURNED')) + '\n'); continue
        kf = f'data/known_{name}.txt'; known = set(open(kf).read().split()) if os.path.exists(kf) else None
        if known is None: log.write(json.dumps(dict(at=now, feed=name, status='COMMITTED', baseline=True, size=len(cur))) + '\n')
        else:
            new = sorted(cur - known); random.Random(int(now) // 60).shuffle(new); take = [d for d in new if d not in st['domains']][:CAP]
            for d in take: st['domains'][d] = dict(first_seen=now, feed=name, done=[], read_gap_s=round(now - st['feeds'].get(name, now))) 
            log.write(json.dumps(dict(at=now, feed=name, status='COMMITTED', size=len(cur), new=len(new), sampled=len(take))) + '\n')
        open(kf, 'w').write('\n'.join(sorted(cur))); st['feeds'][name] = now
        if validate and name == 'cert_pl':
            sample = random.Random(7).sample(sorted(cur), validate); rows = [r for d in sample for r in ask(d, -1, dict(fresh=False, feed=name))]
            with open('data/validation.jsonl', 'a') as f:
                for r in rows: f.write(json.dumps(r) + '\n')
    due = [(d, cp, v) for d, v in st['domains'].items() for cp in CPS if cp not in v['done'] and now >= v['first_seen'] + cp]
    with ThreadPoolExecutor(8) as ex: res = list(ex.map(lambda x: ask(x[0], x[1], dict(fresh=True, feed=x[2]['feed'], first_seen=x[2]['first_seen'])), due))
    with open('data/queries.jsonl', 'a') as f:
        for rows in res:
            for r in rows: f.write(json.dumps(r) + '\n')
    for d, cp, v in due: v['done'].append(cp)
    json.dump(st, open('data/state.json', 'w')); print('caca:', len(due), 'domain checkpoints asked,', sum(len(v['done']) == len(CPS) for v in st['domains'].values()), 'complete,', len(st['domains']), 'tracked')
main()
