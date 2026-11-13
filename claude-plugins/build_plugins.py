#!/usr/bin/env python3
"""Builds every published plugin folder from the originals in src/ (13 Nov 2026, Wayfinder: "fix it, hit it").

  src/<part>        the originals, with their Python scripts and the readcheck commit hook. Our own marketplace serves these.
  plugins/<part>    the plugin directory copies: no .py file and no command hook (the directory accepts those only from Verified
                    organizations). Each script is fetched from the public indahl.ai repository at a pinned commit and run only if its
                    sha256 matches, and the README says so.
  plugins/indahl        the directory bundle: every directory copy in one install, with the indahl.ai connector.
  plugins/indahl-full   the full bundle from src/, scripts and the readcheck gate included. Our marketplace only.

Pins live in pins.json ({path in src: {"commit", "url", "sha256"}}). --pin refreshes them: for each script whose local sha256 differs from
its pin, it finds the newest indahl.ai commit that carries the file and pins it only if the published bytes match. A script with no
matching published copy keeps its old pin and is reported STALE (ship first, then rebuild). Never edit plugins/ by hand.
  python3 build_plugins.py [--pin]"""
import hashlib, json, os, re, shutil, subprocess, sys, urllib.request, filecmp
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(H, 'src'); P = os.path.join(H, 'plugins'); PINS = os.path.join(H, 'pins.json')
REPO = 'Heuremen-LLC/indahl.ai'; RAW = 'https://raw.githubusercontent.com/' + REPO + '/{commit}/{path}'
PARTS = ['standards', 'eval-check', 'indahl-data', 'qia-calibration', 'reproduce', 'darkwave-correction', 'prereg', 'readcheck']
SKIPDIR = {'__pycache__'}; LIC = {'LICENSE', 'LICENSE.txt', 'LICENSE-STANDARD.txt', 'NOTICE.txt'}
sha = lambda b: hashlib.sha256(b).hexdigest()

def scripts():
    out = []
    for p in PARTS:
        for d, ds, fs in os.walk(os.path.join(SRC, p)):
            ds[:] = [x for x in ds if x not in SKIPDIR]
            out += [os.path.relpath(os.path.join(d, f), SRC) for f in fs if f.endswith('.py') and not re.search(r'\.v\d', f)]
    return sorted(out)

def pin():
    pins = json.load(open(PINS)) if os.path.exists(PINS) else {}
    for rel in scripts():
        h = sha(open(os.path.join(SRC, rel), 'rb').read())
        if pins.get(rel, {}).get('sha256') == h: continue
        found = None
        for path in ('claude-plugins/src/' + rel, 'claude-plugins/plugins/' + rel):   # 13 Nov: the first pins point at the pre-move path
            r = subprocess.run(['gh', 'api', f'repos/{REPO}/commits?path={path}&per_page=5', '--jq', '.[].sha'], capture_output=True, text=True)
            for c in r.stdout.split():
                try: b = urllib.request.urlopen(urllib.request.Request(RAW.format(commit=c, path=path), headers={'User-Agent': 'indahl-plugins-build'}), timeout=60).read()
                except Exception: continue
                if sha(b) == h: found = {'commit': c, 'url': RAW.format(commit=c, path=path), 'sha256': h}; break
            if found: break
        if found: pins[rel] = found; print(f'  pin: {rel} -> {found["commit"][:9]}')
        else: print(f'  pin: {rel} STALE (no published copy matches; ship, then rebuild)')
    json.dump(pins, open(PINS, 'w'), indent=1, sort_keys=True)

def fetch_block(entries):
    lines = ['## Get the script first', '',
             'The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its',
             'sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.',
             'Show the user the commands before running them the first time.', '']
    for rel, pinv, local in entries:
        lines += ['```bash', f'F="{local}"',
                  f'[ -f "$F" ] || {{ mkdir -p "$(dirname "$F")" && curl -fsSL "{pinv["url"]}" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],\'rb\').read()).hexdigest() != \'{pinv["sha256"]}\')" "$F.part" && mv "$F.part" "$F"; }}',
                  '```', f'Source: {pinv["url"]} (sha256 {pinv["sha256"]}).', '']
    return '\n'.join(lines) + '\n'

def directory_copy(p, pins):
    src, dst = os.path.join(SRC, p), os.path.join(P, p)
    shutil.rmtree(dst, ignore_errors=True)
    local = {}
    for rel in scripts():
        if rel.startswith(p + '/') and rel in pins:
            inner = rel[len(p) + 1:]; name, ext = os.path.splitext(os.path.basename(inner))
            local[inner] = (rel, pins[rel], f'$HOME/.cache/indahl-plugins/{p}/{name}-{pins[rel]["sha256"][:12]}{ext}')
    for d, ds, fs in os.walk(src):
        ds[:] = [x for x in ds if x not in SKIPDIR]
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), src)
            if f.endswith('.py') or re.search(r'\.v\d', f) or f.endswith('.pyc') or rel == 'hooks/hooks.json': continue
            out = os.path.join(dst, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
            if f.endswith('.md'):
                t = open(os.path.join(d, f)).read(); used = []
                for inner, (srel, pv, loc) in local.items():
                    tok = '${CLAUDE_PLUGIN_ROOT}/' + inner
                    if tok in t: t = t.replace(tok, loc); used.append((srel, pv, loc))
                if used:
                    m = re.match(r'(---\n.*?\n---\n)', t, re.S)
                    head, body = (m.group(1), t[m.end():]) if m else ('', t)
                    t = head + '\n' + fetch_block(used) + body
                open(out, 'w').write(t)
            else: shutil.copy2(os.path.join(d, f), out)
    if p == 'readcheck':   # the commit gate is a command hook; the directory copy keeps the check commands only
        rp = os.path.join(dst, 'README.md')
        open(rp, 'a' if os.path.exists(rp) else 'w').write('\n## In this copy\n\nThe plugin directory accepts command hooks only from Verified organizations, so this copy has the check commands and not the automatic commit gate. The full plugin, gate included, installs from our marketplace: `/plugin marketplace add Heuremen-LLC/indahl.ai` then `/plugin install indahl-readcheck@heuremen`.\n')
    if local:
        rp = os.path.join(dst, 'README.md'); t = open(rp).read() if os.path.exists(rp) else f'# indahl-{p}\n'
        t += '\n## How the scripts arrive\n\nThis copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:\n\n'
        t += ''.join(f'- {pv["url"]}\n  sha256 {pv["sha256"]}\n' for _, pv, _ in local.values())
        t += '\nThe same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).\n'
        open(rp, 'w').write(t)
    missing = [rel for rel in scripts() if rel.startswith(p + '/') and rel not in pins]
    if missing: print(f'  plugins/{p}: NO PIN for {missing} (run --pin after the scripts are published)')

if __name__ == '__main__':
    if '--pin' in sys.argv: pin()
    pins = json.load(open(PINS)) if os.path.exists(PINS) else {}
    for p in PARTS: directory_copy(p, pins)
    leftover = [os.path.join(dp, f) for p in PARTS for dp, _, fs in os.walk(os.path.join(P, p)) for f in fs if f.endswith('.py')]
    if leftover: sys.exit(f'  build: a .py file reached a directory copy: {leftover}')
    print(f'  plugins: {len(PARTS)} directory copies built from src/ (no .py, no command hooks)')
