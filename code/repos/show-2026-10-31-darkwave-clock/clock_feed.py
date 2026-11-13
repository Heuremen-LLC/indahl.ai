"""clock_feed.py -- writes the Darkwave clock feed for indahl.ai/now (9 Nov 2026, site pass M16).
Takes the newest fire per chip that has a results_clock.text, and prints the plan's own reading of it: the 31 October table's share given
back against the fresh table's, and the FINAL label of "share M31 minus share MT" under the committed rule (PLAN_CLOCK.md.text). No words are
added beyond the rule's label. A fire whose UNREAD marker is still in its folder is marked as read by code only, not yet read in full and
refereed (the watch keeps flagging it until that is done). Writes clock_feed.json here and publishes it to KV key dwclock, which the worker
serves at /darkwave/clock.json. Run by clock_daily.py at the end of every pass. It publishes only when a row changed (--force publishes anyway).
--dry-run writes the file and publishes nothing.
"""
import os, sys, re, glob, json, subprocess, datetime as dt
H = os.path.dirname(os.path.abspath(__file__)); CHIPS = ('ibm_kingston', 'ibm_marrakesh')
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); NS = 'ecb59d96b07c43bdac14271687eae5af'
LABEL = {'CANNOT_TELL': 'cannot tell by the plan’s rule', 'BELOW': 'below by the plan’s rule', 'ABOVE': 'above by the plan’s rule',
         'CONSISTENT': 'inside the 0.05 margin by the plan’s rule'}
NUM = r'([+-]?\d+\.\d+)'

def day_label(stamp):   # '20261108_1303' -> '8 Nov 2026', '12:03 UTC'
    t = dt.datetime.strptime(stamp, '%Y%m%d_%H%M'); return '%d %s %d' % (t.day, t.strftime('%b'), t.year), t.strftime('%H:%M UTC'), t

def read(d):
    s = open(os.path.join(d, 'results_clock.text'), encoding='utf-8').read()
    m_fire = re.search(r'fire (\d{8}_\d{4}) UTC', s); m_age = re.search(r'31 Oct table \(M31\) ' + r'(\d+(?:\.\d+)?) h', s)
    m31 = re.search(r'share given back M31 vs 0\.5: ' + NUM, s); mt = re.search(r'share given back MT vs 0\.5: ' + NUM, s)
    fin = re.search(r'share M31 minus share MT \(margin 0\.05\): .*?FINAL (\w+)', s); kg = re.search(r'KNOWN-GOOD.*-> (\w+)', s)
    if not all((m_fire, m_age, m31, mt, fin, kg)) or kg.group(1) != 'PASS' or fin.group(1) not in LABEL: return None
    day, hm, t = day_label(m_fire.group(1))
    text = '%s fire, 31 Oct table %d hours old: %.2f against %.2f fresh, %s.' % (day[:-5], round(float(m_age.group(1))), float(m31.group(1)), float(mt.group(1)), LABEL[fin.group(1)])
    if os.path.exists(os.path.join(d, 'UNREAD')): text += ' Read by code only, not yet read in full.'
    return dict(chip=None, text=text, at=t.strftime('%Y-%m-%dT%H:%MZ'), day=day)

def main():
    rows = []
    for chip in CHIPS:
        for d in sorted(glob.glob(os.path.join(H, 'day_*_' + chip)), reverse=True):
            if os.path.exists(os.path.join(d, 'results_clock.text')):
                r = read(d)
                if r: r['chip'] = chip; rows.append(r); break
    if not rows: print('clock feed: no fire read yet'); return 1
    newest = max(rows, key=lambda r: r['at'])
    out = dict(fire=newest['day'], updated=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
               note='The newest fire on each chip, as the committed plan reads it. Each fire read in full is on the Darkwave page.',
               rows=[dict(chip=r['chip'], text=r['text'], at=r['at']) for r in sorted(rows, key=lambda r: r['at'])])
    p = os.path.join(H, 'clock_feed.json'); pub = os.path.join(H, '.clock_feed_published.json')
    prev = json.load(open(pub, encoding='utf-8')) if os.path.exists(pub) else {}
    same = {k: v for k, v in prev.items() if k != 'updated'} == {k: v for k, v in out.items() if k != 'updated'}
    json.dump(out, open(p + '.tmp', 'w', encoding='utf-8'), ensure_ascii=False); os.replace(p + '.tmp', p)
    print('clock feed:', out['fire'], '|', ' | '.join(r['chip'] + ': ' + r['text'] for r in out['rows']))
    if '--dry-run' in sys.argv: return 0
    if same and '--force' not in sys.argv: print('clock feed: unchanged, not published'); return 0
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'dwclock', '--path', p, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode == 0: json.dump(out, open(pub, 'w', encoding='utf-8'), ensure_ascii=False)
    print('clock feed: published' if r.returncode == 0 else 'clock feed: publish FAILED ' + r.stderr[-300:]); return 0 if r.returncode == 0 else 1

if __name__ == '__main__': sys.exit(main())
