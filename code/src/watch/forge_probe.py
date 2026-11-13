"""forge_probe.py -- one look at Novatable (the old Forge, 192.168.8.140) on her tick (15 Oct 2026, Wayfinder and Bones).
Raw only: ping answered or not, which ports answer, and sshd's own banner line if 22 answers. No login attempted."""
import json, os, socket, subprocess, time
W = os.path.dirname(os.path.abspath(__file__)); H = '192.168.8.140'
row = {'at': time.strftime('%FT%T'), 'host': H}
row['ping'] = subprocess.run(['ping', '-c1', '-W', '1000', H], capture_output=True).returncode == 0
row['open'] = []
for p in (22, 80, 3389, 5900, 11434):
    try:
        s = socket.create_connection((H, p), 2)
        row['open'].append(p)
        if p == 22:
            s.settimeout(3)
            try: row['banner'] = s.recv(200).decode(errors='replace').strip()
            except Exception as e: row['banner'] = 'no banner: %s' % type(e).__name__
        s.close()
    except Exception as e:
        row.setdefault('closed', {})[p] = type(e).__name__
open(os.path.join(W, 'forge_probe.jsonl'), 'a').write(json.dumps(row) + '\n')
