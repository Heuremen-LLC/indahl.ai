"""yo6_publish_post.py (1 Nov 2026): puts the refereed YO v6 post (yo6_post_draft.md, draft 2) in its places, the way the v5 post went:
the results table block (yo2_result.json, after the v5 block, before YO v3), yo6_result.json, the plan erratum, the model-card section, and
the IRIS lab one-liner sentence (indahl-ai/build_site.py). Refuses on any mismatch. Ledger rows and ship follow."""
import json, os, re, shutil
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge/')
d = open(f'{H}/yo6_post_draft.md').read()
A = d.split('## A.')[1].split('## B.')[0]
rows = [list(m) for m in re.findall(r'^\d+\. "(.*?)" \| "(.*?)" \| "(.*?)"\s*$', A, re.M)]
assert len(rows) == 19, len(rows)
one = re.search(r'## B\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
card = re.search(r'## C\..*?\n"(.*?)"\s*\n', d, re.S).group(1)
erratum = re.search(r'## D\..*?\n"(.*?)"\s*$', d, re.S).group(1)
# 1 results table
r = json.load(open(f'{H}/yo2_result.json')); shutil.copy(f'{H}/yo2_result.json', f'{H}/yo2_result.json.pre-v6')
i = next(k for k, x in enumerate(r['rows']) if x[0].startswith('YO v3, which continued training YO v2'))
assert r['rows'][i - 1][0].startswith('Two seeds are a small sample. The comparison is to YO v4 as trained with seed 44. No run c'), r['rows'][i - 1][0][:60]
assert not any(x[0].startswith('YO v6 continued') for x in r['rows'])
r['rows'] = r['rows'][:i] + rows + r['rows'][i:]; json.dump(r, open(f'{H}/yo2_result.json', 'w'), indent=1, ensure_ascii=False)
# 2 result marker (stops the panel following v6 training logs)
json.dump(dict(read='2026-11-01', rule='YO v4 stays at work; YO v6 seeds 49 and 50 reported as tried', source='yo6_results.text'), open(f'{H}/yo6_result.json', 'w'))
# 3 plan erratum (appended)
p = open(f'{H}/PLAN_YO_V6.md').read()
if 'ERRATUM (1 Nov 2026' not in p: open(f'{H}/PLAN_YO_V6.md', 'a').write('\n## ' + erratum + '\n')
# 4 model card section after "YO v5, tried"
cp = f'{H}/release/hf_card/README.md'; c = open(cp).read(); shutil.copy(cp, cp + '.pre-v6')
if '## YO v6, tried' not in c:
    j = c.index('## YO v5, tried'); k = c.find('\n## ', j + 5); k = len(c) if k < 0 else k
    c = c[:k].rstrip('\n') + '\n\n## YO v6, tried\n\n' + card + '\n' + c[k:]; open(cp, 'w').write(c)
# 5 IRIS lab one-liner: the v6 sentence after the v5 sentence
bs = B + 'indahl-ai/build_site.py'; s = open(bs).read(); shutil.copy(bs, bs + '.pre-yo6-20261101')
anchor = 'Seed 47 was below YO v4 on the share of its flags that were right and seed 48 on the verdicts, so YO v4 stays at work.'
assert s.count(anchor) == 1
sent = one.replace("'", '&rsquo;').replace('’', '&rsquo;')
if 'YO v6, trained further' not in s: s = s.replace(anchor, anchor + ' ' + sent); open(bs, 'w').write(s)
print('table rows', len(r['rows']), '| card, erratum, one-liner placed')
