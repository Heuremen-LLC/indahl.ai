"""seat_clocks.py -- every listening seat's clock against the Pi (Leo Lockclocks, GPS PPS), ON HER TICK (17 Oct 2026, Wayfinder and Bones).
Why: the chain ears stamp with their own machine's clock; Armature read +192 ms vs the Pi on 16 Oct. The correction must be
MEASURED beside the data, not assumed after it (Falla I). One row per tick; a failed read is CANNOT_TELL, never zero.
  mac / laptop / pi : chronyc tracking 'System time' (seconds fast/slow of NTP) + reference
  armature          : w32tm /stripchart against 192.168.8.145, one sample (offset of the Pi from Armature)"""
import json, os, re, subprocess, time
W = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(W, 'seat_clocks.jsonl')
def run(cmd, t=25):
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=t); return r.stdout
    except Exception as e: return ''
def chrony(text):
    m = re.search(r'System time\s*:\s*([0-9.]+) seconds (fast|slow)', text); ref = re.search(r'Reference ID\s*:\s*\S+ \(([^)]*)\)', text)
    if not m: return {'state': 'CANNOT_TELL'}
    v = float(m.group(1)) * (1 if m.group(2) == 'fast' else -1)
    return {'state': 'READ', 'fast_of_ref_us': round(v * 1e6, 1), 'ref': ref.group(1) if ref else None}
def main():
    row = {'at': time.strftime('%FT%T'), 't': time.time()}
    row['mac'] = chrony(run([('/opt/homebrew/bin/chronyc' if os.path.exists('/opt/homebrew/bin/chronyc') else 'chronyc'), 'tracking']))   # 17 Oct: the bus PATH has no Homebrew
    row['laptop'] = chrony(run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'c-train-express', 'chronyc tracking']))
    row['pi'] = chrony(run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'flock-pi', 'chronyc tracking']))
    # 17 Oct: outside seats. No GPS there -- chrony on public NTS; root delay/dispersion logged so the bound rides beside the offset.
    for name, host in (('virginia', 'ubuntu@132.145.162.229'), ('newjersey', 'root@64.176.219.98')):   # 18 Oct: Tokyo destroyed
        txt = run(['ssh', '-i', os.path.expanduser('~/.ssh/outside_seat_ed25519'), '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', host, 'chronyc tracking'])
        row[name] = chrony(txt)
        m = re.search(r'Root dispersion\s*:\s*([0-9.]+)', txt); m2 = re.search(r'Root delay\s*:\s*([0-9.]+)', txt)
        if m and m2: row[name]['bound_ms'] = round((float(m2.group(1)) / 2 + float(m.group(1))) * 1000, 2)
    t = run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'armature', 'w32tm //stripchart //computer:192.168.8.145 //samples:1 //dataonly'])
    m = re.search(r', ([+-][0-9.]+)s', t)
    row['armature'] = {'state': 'READ', 'pi_minus_armature_us': round(float(m.group(1)) * 1e6, 1)} if m else {'state': 'CANNOT_TELL'}
    open(LOG, 'a').write(json.dumps(row) + '\n'); return row
if __name__ == '__main__':
    print(json.dumps(main()))
