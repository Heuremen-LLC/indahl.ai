#!/usr/bin/env python3
"""build_pdfs.py: renders source/FAULTS.html and source/GUARDS.html to PDF with headless Chrome or Chromium. usage: build_pdfs.py OUT_DIR
Chrome is found from $CHROME, or the usual names and macOS path. In CI the sandbox flag is added."""
import os, sys, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def chrome():
    for c in (os.environ.get('CHROME'), shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if c and os.path.exists(c): return c
    sys.exit('no Chrome or Chromium found; set CHROME')
def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'build'); os.makedirs(out, exist_ok=True); c = chrome(); flags = ['--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=4000']
    if os.environ.get('CI'): flags.append('--no-sandbox')
    for n, o in (('FAULTS', 'faults.pdf'), ('GUARDS', 'guards.pdf')):
        dst = os.path.join(out, o); r = subprocess.run([c, *flags, '--print-to-pdf=' + dst, 'file://' + os.path.join(ROOT, 'source', n + '.html')], capture_output=True, text=True)
        if not os.path.exists(dst) or os.path.getsize(dst) < 1000: sys.exit('Chrome wrote nothing for %s: %s' % (n, r.stderr[-300:]))
        print(o, os.path.getsize(dst), 'bytes')
if __name__ == '__main__': main()
