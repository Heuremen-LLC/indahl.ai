"""novatable_arrival.py -- watch for Novatable's installer to come up, on HER ticks (15 Oct 2026, Wayfinder and Bones).
Rides ON_HER_NEXT_TICK: each run sweeps both house networks for an SSH port that is not one already known, tries the
novatable key (BatchMode, never a password), logs what it saw, and re-queues itself for her next tick until it finds
Novatable or has ridden MAX_TICKS of hers. Four outcomes per row: FOUND_KEY_OK / FOUND_KEY_REFUSED / NEW_PORT_NOT_SSH / NOTHING_NEW."""
import json, os, socket, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
W = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(W, 'novatable_arrival.jsonl'); ST = os.path.join(W, 'novatable_arrival_state.json')
M = os.path.join(W, 'ON_HER_NEXT_TICK.json'); KEY = os.path.expanduser('~/.ssh/novatable_key')
KNOWN = {'10.0.0.183', '10.0.0.198', '192.168.8.123', '192.168.8.145', '192.168.8.158', '192.168.8.174'}; MAX_TICKS = 300   # 16 Oct morning: rides through his screen session (was 150 overnight 15-16 Oct); KVM, Admin Panel, laptop, Pi, Armature, Mac; MAX_TICKS = 20

def open22(h):
    try:
        with socket.create_connection((h, 22), timeout=1.0) as s:
            s.settimeout(2); return h, s.recv(64).decode('ascii', 'replace').strip()
    except Exception: return None

def try_key(h):
    for user in ('root', 'wayfinder'):
        r = subprocess.run(['ssh', '-i', KEY, '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=6', '-o', 'StrictHostKeyChecking=no',
                            '-o', 'UserKnownHostsFile=/dev/null', '%s@%s' % (user, h),
                            'hostname; cat /run/novatable_pick.txt 2>/dev/null; cat /etc/novatable.autoinstalled 2>/dev/null; uptime'],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0: return user, r.stdout.strip()[:400]
    return None, r.stderr.strip()[-160:]

NOVA_MAC = '00:e0:67:09:bf:29'   # 16 Oct: Novatable's network card. A host is named by its MAC, never by IP + timing (15 Oct, .179).

def mac_seen():
    """-> IPs whose arp entry is Novatable's MAC (macOS prints octets without leading zeros). Only the Mac's own LAN has MACs here."""
    out = subprocess.run(['arp', '-an'], capture_output=True, text=True, timeout=20).stdout
    hits = []
    for l in out.splitlines():
        w = l.split()
        if len(w) > 3 and ':'.join(x.zfill(2) for x in w[3].split(':')).lower() == NOVA_MAC: hits.append(w[1].strip('()'))
    return hits

def main():
    s = json.load(open(ST)) if os.path.exists(ST) else {'n': 0}
    hosts = ['%s.%d' % (n, i) for n in ('10.0.0', '192.168.8') for i in range(2, 255)]
    with ThreadPoolExecutor(max_workers=128) as ex: got = [g for g in ex.map(open22, hosts) if g]
    new = [(h, b) for h, b in got if h not in KNOWN and h not in s.get('ignore', [])]
    row = {'at': time.strftime('%FT%T'), 'n': s['n'], 'ssh_ports': [h for h, _ in got], 'new': new}
    try: row['novatable_mac_at'] = mac_seen()   # beside SSH, not instead: the card can answer DHCP before sshd is up
    except Exception as e: row['novatable_mac_at'] = 'error: %s' % str(e)[:60]
    if not new: row['outcome'] = 'NOTHING_NEW'
    else:
        h, b = new[0]
        if not b.startswith('SSH-'): row['outcome'] = 'NEW_PORT_NOT_SSH'
        else:
            user, out = try_key(h)
            row.update(host=h, banner=b, user=user, said=out, outcome='FOUND_KEY_OK' if user else 'FOUND_KEY_REFUSED')
    s['n'] += 1; json.dump(s, open(ST, 'w')); open(LOG, 'a').write(json.dumps(row) + '\n')
    if row['outcome'] != 'FOUND_KEY_OK' and s['n'] < MAX_TICKS and not os.path.exists(M):
        json.dump({'cmd': [sys.executable, os.path.abspath(__file__)], 'log': os.path.join(W, 'novatable_arrival.out'),
                   'why': 'Novatable installer arrival, ride %d of %d' % (s['n'] + 1, MAX_TICKS)}, open(M, 'w'))

if __name__ == '__main__':
    main()
