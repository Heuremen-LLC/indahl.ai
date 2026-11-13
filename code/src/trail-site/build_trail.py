#!/usr/bin/env python3
"""build_trail.py -- thetrailtothepast.com: the full Seven canon (from SEVEN.html) followed by the correction log (corrections.html, newest day first),
written to custom_html.html. With --apply it PATCHes custom_html + custom_css into sage_node_config (service key) and checks stored == file.
Rebuild Seven first: SEVEN.md -> SEVEN.html (build_disco_pdf.build)."""
import json, os, re, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
SEVEN = '/Users/heuremen/bones-forge/parallax/darkwave_disco/SEVEN.html'
HASH_NOTE = '''  <footer>
    <p>The run ledger is kept in-house. Through section 273 (5 October 2026, night) its SHA-256 is:</p>
    <p class="hash">6d75650a5847add8f5a9dc8b02307f06e393a4705b4334013f66427ca239d826</p>
    <p>A later copy can be checked against it. Updated 5 October 2026.</p>
  </footer>'''


def seven_body():
    h = open(SEVEN, encoding='utf-8').read(); b = h[h.index('<body>') + 6:h.index('</body>')]
    b = re.sub(r'<p class="foot">.*?</p>', '', b).replace('<h1>Seven</h1>', '<h2 class="seventitle">Seven</h2>', 1)
    return re.sub(r'<h2>(.*?)</h2>', r'<h3>\1</h3>', b)


def main():
    log = open(os.path.join(HERE, 'corrections.html'), encoding='utf-8').read()
    html = f'''<div id="trail">
  <header>
    <h1>The Trail to the Past</h1>
    <p class="lede">The findings, in full, and every correction to them in the order we made them. Each correction says what we said, what the record showed, and what changed.</p>
  </header>

  <section class="seven">
{seven_body()}
  </section>

  <h2 class="part">Corrections</h2>

{log}
  <p class="more">Corrections from 28 September to 2 October are being added in order.</p>

{HASH_NOTE}
</div>
'''
    sys.path.insert(0, '/Users/heuremen/bones-forge/parallax'); import public_voice   # 7 Oct: names off, the collaboration line, and the footer, on every build
    html = public_voice.public(html)
    if 'A collaboration between organic and inorganic intelligences.<br>' not in html:
        html = html.replace('  </footer>', '    <p class="heuremen-foot" style="text-align:center;font-style:italic;margin-top:1.6rem">' + public_voice.FOOT_HTML + '</p>\n  </footer>', 1)
    open(os.path.join(HERE, 'custom_html.html'), 'w', encoding='utf-8').write(html); print('custom_html.html', len(html), 'chars')
    if '--apply' in sys.argv:
        KEY = open('/Users/heuremen/bones-forge/.supabase_service_key').read().strip(); URL = 'https://yxsttnwqiyxlyfnmqzof.supabase.co/rest/v1/sage_node_config'
        H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
        for key, f in (('custom_html', 'custom_html.html'), ('custom_css', 'custom.css')):
            val = open(os.path.join(HERE, f), encoding='utf-8').read()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(f'{URL}?node=eq.thetrailtothepast.com&key=eq.{key}', data=json.dumps({'value': val}).encode(), method='PATCH', headers=H), timeout=30).read())
            print(key, 'stored == file:', bool(r) and r[0]['value'] == val)


if __name__ == '__main__':
    main()
