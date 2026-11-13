"""yo7_publish_post.py (1 Nov 2026): puts the refereed YO v7 post (yo7_post_draft.md, draft 2, every flag in REFEREE_YO_V7_POST.md acted on)
in its places, the way the v6 post went: the results table block (yo2_result.json, after the v6 block, before YO v3), yo7_result.json, the
model-card section, the IRIS lab one-liner (indahl-ai/build_site.py), and the live reader's gate (LIVE_READER_ON -> adapters/v7, by the
PLAN_YO_V7S rule). Refuses on any mismatch. Ledger rows and ship follow."""
import json, os, re, shutil, hashlib
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge/')
d = open(f'{H}/yo7_post_draft.md').read()
A = d.split('## A.')[1].split('## B.')[0]
rows = [list(m) for m in re.findall(r'^\d+\. "(.*?)" \| "(.*?)" \| "(.*?)"\s*$', A, re.M)]
assert len(rows) == 13, len(rows)
one = re.search(r'## B\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
card = re.search(r'## C\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
# 1 results table, after the v6 block (whose last row starts "Two seeds are a small sample. The comparison is to YO v4 ... v6")
r = json.load(open(f'{H}/yo2_result.json')); shutil.copy(f'{H}/yo2_result.json', f'{H}/yo2_result.json.pre-v7')
assert not any(x[0].startswith('YO v7 continued') for x in r['rows'])
i = next(k for k, x in enumerate(r['rows']) if x[0].startswith('YO v3, which continued training YO v2'))
assert 'v6' in r['rows'][i - 1][0], r['rows'][i - 1][0][:80]
r['rows'] = r['rows'][:i] + rows + r['rows'][i:]; json.dump(r, open(f'{H}/yo2_result.json', 'w'), indent=1, ensure_ascii=False)
# 2 result marker
json.dump(dict(read='2026-11-01', rule='YO v7 seed 51 replaces YO v4 (PLAN_YO_V7S: seeds 53, 54, 55 all pass)', source='yo7s_results.text'), open(f'{H}/yo7_result.json', 'w'))
# 3 model card section after "YO v6, tried"
cp = f'{H}/release/hf_card/README.md'; c = open(cp).read(); shutil.copy(cp, cp + '.pre-v7')
if '## YO v7, at work' not in c:
    j = c.index('## YO v6, tried'); k = c.find('\n## ', j + 5); k = len(c) if k < 0 else k
    c = c[:k].rstrip('\n') + '\n\n## YO v7, at work\n\n' + card + '\n' + c[k:]; open(cp, 'w').write(c)
# 4 IRIS lab one-liner: model at work, and the v7 sentence after the v6 sentence
bs = B + 'indahl-ai/build_site.py'; s = open(bs).read(); shutil.copy(bs, bs + '.pre-yo7-20261101')
a1 = "'YO v4 is the model at work. In its planned test on IBM records held"
a2 = 'one seed was below YO v4 on whole-window recall and the other found fewer stale neighbours, so YO v4 stays at work.'
assert s.count(a1) == 1 and s.count(a2) == 1
s = s.replace(a1, "'YO v7 is the model at work. In YO v4&rsquo;s planned test on IBM records held")
sent = one.replace("'", '&rsquo;').replace('’', '&rsquo;')
if 'YO v7, trained again' not in s: s = s.replace(a2, a2 + ' ' + sent)
open(bs, 'w').write(s)
# 5 live reader gate -> adapters/v7 (hash checked against ADAPTERS_YO_V7.sha256)
h = hashlib.sha256(open(f'{H}/adapters/v7/adapters.safetensors', 'rb').read()).hexdigest()
assert h in open(f'{H}/ADAPTERS_YO_V7.sha256').read(), 'adapter hash does not match the record'
shutil.copy(f'{H}/LIVE_READER_ON', f'{H}/LIVE_READER_ON.pre-v7')
open(f'{H}/LIVE_READER_ON', 'w').write(f'adapters/v7 {h[:16]}\n')
print('table rows', len(r['rows']), '| card, one-liner, gate placed; gate now', open(f'{H}/LIVE_READER_ON').read().strip())
