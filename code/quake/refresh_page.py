#!/usr/bin/env python3
"""refresh_page.py (11 Nov 2026): keeps the QUAKE desk page tables and their ledger rows in step with the latest desk run.

The tick rider moves summary_quake.json about every six hours. Before this, quake.html and the quake.* ledger rows stayed at the
shipped run, so the next automatic ship would refuse. ship.sh step 1 runs this before build_site.py:
  if summary_quake.json changed since the last refresh: build_page.py (page from the summary), then make_rows.py --update
  (ledger rows from the same summary and page, ledger before the surface). Unchanged: does nothing.
State: data/refresh_state.json (sha256 of the summary last rendered). Exit 1 if a step fails, so the ship refuses loudly."""
import hashlib, json, os, subprocess, sys

H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.join(H, 'data', 'refresh_state.json')


def main():
    h = hashlib.sha256(open(os.path.join(H, 'summary_quake.json'), 'rb').read()).hexdigest()
    st = json.load(open(ST)) if os.path.exists(ST) else {}
    if st.get('summary') == h:
        print('quake refresh: summary unchanged since the last page build'); return 0
    for cmd in (['build_page.py'], ['make_rows.py', '--update']):
        r = subprocess.run([sys.executable, os.path.join(H, cmd[0])] + cmd[1:], cwd=H, capture_output=True, text=True)
        if r.returncode != 0:
            print('quake refresh: %s failed (rc %d): %s' % (' '.join(cmd), r.returncode, (r.stdout + r.stderr)[-600:])); return 1
        print('quake refresh: ' + ((r.stdout.strip().splitlines() or ['ok'])[-1]))
    json.dump({'summary': h}, open(ST, 'w')); return 0


if __name__ == '__main__':
    sys.exit(main())
