#!/usr/bin/env python3
"""build_future.py -- BACK TO THE FUTURE: the forward half of the trail (Bones, 8 Oct 2026).

The Trail to the Past holds the findings and every correction to them, in the order we made them -- backward.
This holds what was written BEFORE its data: the rulers, the calls hashed before their runs, the open
questions with their sizes, and what comes next. SEPARATE SECTION, separate page, same voice.

  python3 build_future.py              build + preview only (default; touches nothing live)
  python3 build_future.py --apply      PATCH custom_html + custom_css into the live node, then verify

NOT APPLIED on 8 Oct 2026. Built, previewed to ~/Desktop/BACK_TO_THE_FUTURE.pdf, and left off the wire
until Wayfinder says. Publishing is outward-facing and his call, not mine.
"""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
NODE = os.environ.get('FUTURE_NODE', 'thetrailtothepast.com')      # the node + key this section is served from
KEYNAME = os.environ.get('FUTURE_KEY', 'custom_html_future')


def main():
    body = open(os.path.join(HERE, 'back_to_the_future.html'), encoding='utf-8').read()
    css = open(os.path.join(HERE, 'future.css'), encoding='utf-8').read()
    sys.path.insert(0, '/Users/heuremen/bones-forge/parallax')
    import public_voice                                            # names off, the collaboration line, the footer
    body = public_voice.public(body)
    if 'A collaboration between organic and inorganic intelligences.<br>' not in body:
        body = body.replace('  </footer>', '    <p class="heuremen-foot" style="text-align:center;font-style:italic;margin-top:1.6rem">'
                            + public_voice.FOOT_HTML + '</p>\n  </footer>', 1)
    open(os.path.join(HERE, 'back_to_the_future.built.html'), 'w', encoding='utf-8').write(body)
    open(os.path.join(HERE, 'preview.html'), 'w', encoding='utf-8').write(
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Back to the Future</title><style>body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;'
        'color:#18202b;background:#fff;margin:0}@page{size:Letter;margin:.7in}' + css + '</style></head><body>' + body + '</body></html>')
    print('built:', len(body), 'chars  ->  back_to_the_future.built.html + preview.html')
    if '--apply' not in sys.argv:
        print('NOT applied. Nothing live was touched. Pass --apply when Wayfinder says.')
        return
    KEY = open('/Users/heuremen/bones-forge/.supabase_service_key').read().strip()
    URL = 'https://yxsttnwqiyxlyfnmqzof.supabase.co/rest/v1/sage_node_config'
    H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
    for key, val in ((KEYNAME, body), (KEYNAME + '_css', css)):
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'{URL}?node=eq.{NODE}&key=eq.{key}', data=json.dumps({'value': val}).encode(),
            method='PATCH', headers=H), timeout=30).read())
        print(key, 'stored == file:', bool(r) and r[0]['value'] == val)


if __name__ == '__main__':
    main()
