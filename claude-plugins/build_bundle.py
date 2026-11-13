#!/usr/bin/env python3
"""Builds plugins/indahl, the one-install bundle of every Heuremen LLC plugin, from the plugins in plugins/ (13 Nov 2026, Wayfinder: "can we
make this all a bundle too?"). Every skill, command, script, the readcheck gate hook and the indahl.ai connector, copied unchanged; each
plugin's own license kept under licenses/<plugin>/. Run before every release (push_public.sh calls it); never edit plugins/indahl by hand.
  python3 build_bundle.py [--check]   (--check: exit 1 if plugins/indahl is not what this script would build)"""
import json, os, shutil, sys, filecmp, tempfile
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, 'plugins'); OUT = os.path.join(P, 'indahl')
PARTS = ['standards', 'eval-check', 'indahl-data', 'qia-calibration', 'reproduce', 'darkwave-correction', 'prereg', 'readcheck', 'triangulate']
SKIP = ('.v1', '.v2', '.v3', '.v4', '.v5', '.v6', '.pyc', '.DS_Store'); SKIP_DIRS = {'__pycache__', '.claude-plugin'}
LIC = {'LICENSE', 'LICENSE.txt', 'LICENSE-STANDARD.txt', 'NOTICE.txt'}

def build(dst, PARTS=PARTS, NAME='indahl-full', DESC=None, BASE=None):
    BASE = BASE or os.path.join(H, 'src')
    os.makedirs(os.path.join(dst, '.claude-plugin'), exist_ok=True)
    versions, hooks, mcp, seen = {}, None, {}, {}
    for p in PARTS:
        src = os.path.join(BASE, p); m = json.load(open(os.path.join(src, '.claude-plugin', 'plugin.json'))); versions[p] = m.get('version')
        for d, ds, fs in os.walk(src):
            ds[:] = [x for x in ds if x not in SKIP_DIRS]
            for f in fs:
                if f.endswith(SKIP) or '.v' in os.path.splitext(f)[1]: continue
                rel = os.path.relpath(os.path.join(d, f), src)
                if rel in LIC: tgt = os.path.join('licenses', p, rel)
                elif rel == 'README.md': tgt = os.path.join('docs', p, 'README.md')
                elif rel == 'hooks/hooks.json': hooks = json.load(open(os.path.join(d, f))); continue
                elif rel == '.mcp.json': mcp.update(json.load(open(os.path.join(d, f))).get('mcpServers', {})); continue
                else: tgt = rel
                if tgt in seen and not filecmp.cmp(seen[tgt], os.path.join(d, f), shallow=False):
                    sys.exit(f'bundle: {tgt} comes from two plugins with different content ({seen[tgt]} and {os.path.join(d, f)})')
                seen[tgt] = os.path.join(d, f); os.makedirs(os.path.dirname(os.path.join(dst, tgt)), exist_ok=True); shutil.copy2(os.path.join(d, f), os.path.join(dst, tgt))
    if hooks: os.makedirs(os.path.join(dst, 'hooks'), exist_ok=True); json.dump(hooks, open(os.path.join(dst, 'hooks', 'hooks.json'), 'w'), indent=2)
    if mcp: json.dump({'mcpServers': mcp}, open(os.path.join(dst, '.mcp.json'), 'w'), indent=2)
    shutil.copy2(os.path.join(H, 'src', 'standards', '.claude-plugin', 'icon.png'), os.path.join(dst, '.claude-plugin', 'icon.png'))
    json.dump({'name': NAME, 'version': '1.0.0',
               'description': DESC or 'Every Heuremen LLC plugin in one install: check papers and LLM eval claims against the Standards, gate readings with a check block, query and reproduce every indahl.ai desk, check and correct IBM Quantum runs, and test whether a plan was pushed before the first run. Includes the indahl.ai data connector.',
               'author': {'name': 'Heuremen LLC', 'url': 'https://indahl.ai'}, 'homepage': 'https://indahl.ai/plugins',
               'repository': 'https://github.com/Heuremen-LLC/indahl.ai', 'license': 'SEE licenses/',
               'keywords': ['research', 'standards', 'evaluation', 'reproducibility', 'quantum', 'data'], 'icon': '.claude-plugin/icon.png'},
              open(os.path.join(dst, '.claude-plugin', 'plugin.json'), 'w'), indent=2)
    lines = [f'# {NAME}', '', (DESC or 'Every Heuremen LLC plugin in one install.'), '', '```', f'/plugin install {NAME} --marketplace Heuremen-LLC/indahl.ai', '```', '', 'Built by build_bundle.py from the plugins beside it; the parts and their versions:', '']
    lines += [f'- {p} {v}' for p, v in versions.items()]
    lines += ['', '## Services this bundle contacts', '',
              '- indahl.ai (https://indahl.ai/mcp and https://indahl.ai/qia/audit.json): our own public read-only data. Nothing is stored.',
              ] + ([] if set(PARTS) <= {'standards', 'eval-check', 'indahl-data'} else [
              '- GitHub (github.com/Heuremen-LLC/indahl.ai and api.github.com): reproduce kit fetches and public repository activity for prereg.',
              '- IBM Quantum (quantum.cloud.ibm.com), only through your own account and only when you ask; nothing is submitted without your explicit yes.']) + [
              '', 'Nothing else is contacted. No personal data is read or stored. Fetched text is treated as data, not instructions.',
              '', 'Each part keeps its own license, under licenses/<part>/. Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.',
              'Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins', '']
    open(os.path.join(dst, 'README.md'), 'w').write('\n'.join(lines))

LITE = PARTS   # 13 Nov: the directory copies in plugins/ (built by build_plugins.py: no .py, no command hooks, scripts fetched at pinned sha256)
LITE_DESC = 'Every Heuremen LLC plugin in one install: check papers and LLM eval claims against the Standards, query and reproduce every indahl.ai desk, check and correct IBM Quantum runs, test whether a plan was pushed before the first run, and check readings for a complete check block. Includes the indahl.ai data connector. Scripts are fetched from the public indahl.ai repository at pinned sha256; the version with bundled scripts and the automatic readcheck commit gate is indahl-full in the Heuremen-LLC/indahl.ai marketplace.'
FULL = os.path.join(P, 'indahl-full')
if '--check' in sys.argv:
    t = tempfile.mkdtemp(); build(t, LITE, 'indahl', LITE_DESC, P); c = filecmp.dircmp(t, OUT)
    def diff(c): return bool(c.left_only or c.right_only or c.diff_files) or any(diff(s) for s in c.subdirs.values())
    shutil.rmtree(t); sys.exit(1 if diff(c) else 0)
for out, parts, name, desc, base in ((FULL, PARTS, 'indahl-full', None, os.path.join(H, 'src')), (OUT, LITE, 'indahl', LITE_DESC, P)):
    shutil.rmtree(out, ignore_errors=True); build(out, parts, name, desc, base)
    n = sum(len(fs) for _, _, fs in os.walk(out)); print(f'  bundle: plugins/{name} built from {len(parts)} plugins, {n} files')
