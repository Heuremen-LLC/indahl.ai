"""yo8_publish_post.py (2 Nov 2026): puts the refereed YO v8 post (yo8_post_draft.md) in its places: the results table block
(yo2_result.json, after the YO v7 block, before YO v3), yo8_result.json, the model-card section after "YO v7, at work", and the
IRIS lab one-liner (indahl-ai/build_site.py) after the YO v7 sentence. The live reader's gate is not touched (YO v7 stays).
Refuses on any mismatch. Ledger rows and ship follow."""
import json, os, re, shutil
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge/')
d = open(f'{H}/yo8_post_draft.md').read()
A = d.split('## A.')[1].split('## B.')[0]
rows = [list(m) for m in re.findall(r'^\d+\. "(.*?)" \| "(.*?)" \| "(.*?)"\s*$', A, re.M)]
assert len(rows) == 13, len(rows)
one = re.search(r'## B\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
card = re.search(r'## C\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
r = json.load(open(f'{H}/yo2_result.json')); shutil.copy(f'{H}/yo2_result.json', f'{H}/yo2_result.json.pre-v8')
assert not any(x[0].startswith('YO v8 continued') for x in r['rows'])
i = next(k for k, x in enumerate(r['rows']) if x[0].startswith('YO v3, which continued training YO v2'))
assert r['rows'][i - 1][0].startswith('Seed 54 wrote one reply'), r['rows'][i - 1][0][:80]
r['rows'] = r['rows'][:i] + rows + r['rows'][i:]; json.dump(r, open(f'{H}/yo2_result.json', 'w'), indent=1, ensure_ascii=False)
json.dump(dict(read='2026-11-02', rule='YO v7 seed 51 stays at work (PLAN_YO_V8: no seed of 56, 57, 58 passes)', source='yo8_results.text'), open(f'{H}/yo8_result.json', 'w'))
cp = f'{H}/release/hf_card/README.md'; c = open(cp).read(); shutil.copy(cp, cp + '.pre-v8')
if '## YO v8, tried' not in c:
    j = c.index('## YO v7, at work'); k = c.find('\n## ', j + 5); k = len(c) if k < 0 else k
    c = c[:k].rstrip('\n') + '\n\n## YO v8, tried\n\n' + card + '\n' + c[k:]; open(cp, 'w').write(c)
bs = B + 'indahl-ai/build_site.py'; s = open(bs).read(); shutil.copy(bs, bs + '.pre-yo8-20261102')
a2 = 'so by the rule written before training YO v7 seed 51 now does the live reads (one of the first two seeds failed).'
assert s.count(a2) == 1
sent = one.replace("'", '&rsquo;').replace('’', '&rsquo;')
if 'YO v8, trained further' not in s: s = s.replace(a2, a2 + ' ' + sent)
open(bs, 'w').write(s)
print('table rows', len(r['rows']), '| card and one-liner placed; live gate unchanged:', open(f'{H}/LIVE_READER_ON').read().strip())
