#!/usr/bin/env python3
"""Render a Quantum Idle Audit bill from its data file.

    python3 render_bill.py QIA-2026-001.json            -> QIA-2026-001.html + QIA-2026-001.pdf

Edit only the JSON. Layout, fonts, page breaks and house style live here and in head.html.
The script refuses to build when the data breaks a house rule, and it fits the pages itself:
no section heading alone at the bottom of a page, no footer alone on a page.
"""
import html, json, os, re, subprocess, sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
FOOTER = 'Heuremen LLC<br>“We found it.”'
COLS_FX = '<colgroup><col style="width:4%"><col style="width:19%"><col style="width:15%"><col style="width:62%"></colgroup>'
COLS = '<colgroup><col style="width:4%"><col style="width:19%"><col style="width:15%"><col style="width:24%"><col style="width:38%"></colgroup>'

# Words that never go on a bill (framework vocabulary, narrative, hashes, guesses about money).
BANNED = [r'\bphi\b', r'golden', r'Bonefish', r'\bNova\b', r'[Dd]arkwave', r'12/11', r'Spooky', r'\bGalleta\b',
          r'prepared by', r'\bAI\b', r'Claude', r'SHA-?256', r'\bhash\b', r'\$\s?\d', r'\bUSD\b', r'invoice total']


def lint(text, where):
    """Return a list of house-style problems in one cell of text."""
    errs = []
    plain = re.sub(r'<[^>]+>', '', text)
    if re.search(r"[A-Za-z]'[A-Za-z]", plain):
        errs.append(f"{where}: straight apostrophe (use ’)")
    if re.search(r'\d\s?[–-]\s?\d+(\.\d+)?\s?(kHz|MHz|µs|us|h|%|Sep|Oct|days)', plain) and 'log-log' not in plain:
        m = re.search(r'\d\s?[–-]\s?\d+(\.\d+)?\s?(kHz|MHz|µs|us|h|%|Sep|Oct|days)', plain)
        errs.append(f"{where}: dash range '{m.group(0)}' (write 'a to b')")
    for b in BANNED:
        if re.search(b, plain):
            errs.append(f"{where}: banned word /{b}/")
    if re.search(r'(prepared|verified|stuck|held) in [01]\b', plain):
        errs.append(f"{where}: state written as a bare digit (use |0⟩ or |1⟩)")
    return errs


def cell(text, cls=None):
    c = f' class="{cls}"' if cls else ''
    return f'<td{c}>{text}</td>'


def body(d, fx_pt, fx_break=False, rn_break=False):
    # one grid for every table, so every page reads the same: # | what | chip / IBM states | documentation / IBM states | what was found
    out = [f'<style>table{{font-size:7.9pt;table-layout:fixed}} tr{{break-inside:avoid}} table.fx{{font-size:{fx_pt}pt}} '
           'td.h,div.h{color:var(--ink-mid);font-size:7.2pt} div.h{margin-top:4px} '
           'div.v{font-weight:600;color:#8b1a10;margin-top:4px} div.st{margin-top:4px;color:var(--ink-mid)} '
           'td.q{font-style:italic;font-size:7.2pt}</style>',
           '<div class="case" style="margin-top:-8px"><div style="font:600 13pt/1.2 Cinzel,serif;letter-spacing:.12em;'
           f'color:var(--ink)">{d["case"]}</div>',
           f'<div class="meta" style="font-size:9.5pt;color:var(--ink-mid);margin-top:4px">{d["date"]} · '
           f'{", ".join(d["chips"])}</div></div>', '']
    dev = d['deviations']
    out.append('<h2>Deviations from stated figures</h2>')
    out.append('<table class="dev">' + COLS)
    out.append('<tr><th>#</th><th>IBM stated figure</th><th>Chip</th><th>IBM’s own documentation</th>'
               '<th>Delivered [95 % interval where given]</th></tr>')
    for r in dev:
        out.append('<tr>' + cell(r['n']) + cell(r['figure'] + f'<div class="st">IBM states: {r["ibm_states"]}</div>') + cell(r['chip']) +
                   cell(r.get('ibm_doc', '—'), 'q') +
                   cell(r['delivered'] + f'<div class="v">{r["deviation"]}</div><div class="h">{r["how"]}</div>') + '</tr>')
    out += ['</table>', '', ('<h2 style="page-break-before:always;break-before:page">Record notes</h2>' if rn_break else '<h2 style="page-break-after:avoid;break-after:avoid">Record notes</h2>'), '<table>' + COLS,
            '<tr><th>#</th><th>Record</th><th>Chip</th><th>IBM’s own documentation</th><th>What IBM’s record shows</th></tr>']
    for r in d['record_notes']:
        out.append('<tr>' + cell(r['n']) + cell(r['record']) + cell(r['chip']) + cell(r.get('ibm_doc', '—'), 'q') + cell(r['shows']) + '</tr>')
    out += ['</table>', '', ('<h2 style="page-break-before:always;break-before:page">Not in any stated figure</h2>' if fx_break else '<h2 style="page-break-after:avoid;break-after:avoid">Not in any stated figure</h2>'), '<table class="fx">' + COLS_FX,
            '<tr><th>#</th><th>Effect</th><th>IBM states</th><th>Delivered [95 % interval where given]</th></tr>']
    for r in d['effects']:
        out.append('<tr>' + cell(r['n']) + cell(r['effect']) + cell(r['ibm_states']) +
                   cell(r['delivered'] + f'<div class="h">{r["how"]}</div>') + '</tr>')
    out += ['</table>', '', f'<p class="small">{html.escape(d["method"], quote=False)}</p>',
            '<div style="margin-top:8px;text-align:left;font:10pt/1.3 Lora,Georgia,serif;color:var(--ink-mid)">'
            f'{FOOTER}</div>']
    return '\n'.join(out)


def pages(pdf):
    try:
        import pypdf
    except ImportError:
        sys.exit('pypdf is needed for the page-fit check (pip install pypdf)')
    return [' '.join((p.extract_text() or '').split()) for p in pypdf.PdfReader(pdf).pages]


def main(path):
    d = json.load(open(path))
    stem = os.path.splitext(path)[0]
    # 1. numbering and house-style checks
    errs = []
    n_all = [r['n'] for s in ('deviations', 'record_notes', 'effects') for r in d[s]]
    if n_all != list(range(1, len(n_all) + 1)):
        errs.append(f'row numbers are not 1..{len(n_all)} in order: {n_all}')
    for s in ('deviations', 'record_notes', 'effects'):
        for r in d[s]:
            for k, v in r.items():
                if isinstance(v, str):
                    errs += lint(v, f'{s} #{r["n"]} {k}')
    errs += lint(d['method'], 'method')
    if errs:
        print('REFUSED, fix the data file:'); [print('  -', e) for e in errs]; sys.exit(1)
    # 2. build, shrinking only the effects table until the footer shares page 2
    head = open(os.path.join(HERE, 'head.html')).read().replace('__TITLE__', d['case'])
    fx_break = rn_break = False
    for fx in (7.6, 7.6, 7.6, 7.4, 7.2, 7.0, 6.8, 6.6, 6.4):
        full = head + body(d, fx, fx_break, rn_break) + '\n</body></html>'
        open(stem + '.html', 'w').write(full)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000',
                        f'--print-to-pdf={stem}.pdf', 'file://' + os.path.abspath(stem + '.html')],
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        pg = pages(stem + '.pdf')
        footer_alone = len(pg[-1]) < 60 and 'found it' in pg[-1]
        tail_alone = len(pg[-1]) < 600 and pg[-1].startswith('Method')   # only the method line and footer spilled over
        orphan_head = any(t.rstrip().endswith('i t') and 'Not in any stat' in t[-400:] for t in pg[:-1])   # effects heading + header row left alone at a page foot
        if orphan_head and not fx_break:
            fx_break = True; continue
        rn_orphan = any(t.rstrip().endswith('s h ow s') for t in pg[:-1])   # record-notes heading + header row alone at a page foot
        if rn_orphan and not rn_break:
            rn_break = True; continue
        if not (footer_alone or tail_alone):
            break
    else:
        sys.exit('could not fit the method line and footer onto the last page of tables; shorten the effects text')
    print(f'{stem}.pdf: {len(pg)} pages (effects table at {fx} pt)')
    for i, t in enumerate(pg, 1):
        print(f'  page {i}: starts "{t[:50]}" ... ends "{t[-60:]}"')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'QIA-2026-001.json')
