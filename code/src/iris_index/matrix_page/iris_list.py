"""IRIS List (25 Oct, his word: same format as QIA): study name, IRIS classification, date indexed, receipt. Public at /iris/list and /iris/list.json."""
import json, os, re, html, shutil
B = os.path.expanduser('~/bones-forge/'); I = B + 'iris_index/'; E = html.escape
R = json.load(open(I + 'IRIS_BOOK_register.json')); rows = R if isinstance(R, list) else R.get('rows', list(R.values()))
S = json.load(open(I + 'SCAN_register.json')); srows = S if isinstance(S, list) else S.get('rows', list(S.values()))
sc = {r['id'].replace('arXiv:', ''): r for r in srows}
# 30 Oct 2026 (site pass): plain sentences. The register text carries semicolons, so each one becomes a full stop. Thousands separators and singular nouns for the file counts.
plain = lambda t: re.sub(r';\s*(["\u201c]?)(\w)', lambda m: '. ' + m.group(1) + m.group(2).upper(), t)
def nfiles(n):
    if not n: return 'listed'
    try: n = int(n)
    except Exception: return str(n)
    return f'{n:,} output file' + ('' if n == 1 else 's')
L = []
for r in rows:
    a = r['id'].replace('arXiv:', ''); s_ = sc.get(a, {})
    L.append(dict(study=r['title'], link=f'https://arxiv.org/abs/{a}', classification='Indexed', indexed=r.get('booked', ''),
                  receipt=[f'Read: full text, version {a[-2:]}, and their released files ({nfiles(s_.get("n_output_files", ""))})',
                           'Printed numbers against their released files: ' + plain(r['recount']), 'Measured on our setup: ' + plain(r['priced']), 'Data: /iris/runs/recounts.zip']))
for s_ in srows:
    if s_['status'] != 'MATRIX_ONLY_COMPANY': continue
    a = s_['id']
    L.append(dict(study=s_['title'], link=f'https://arxiv.org/abs/{a}', classification='Indexed', indexed=s_.get('swept', ''),
                  receipt=[f'Read: abstract, author list and released-file list, version {a[-2:]}', f'Released output files listed: {int(s_["n_output_files"]):,}' if str(s_.get('n_output_files', '')).isdigit() else f'Released output files listed: {s_.get("n_output_files", "")}', 'Not recounted']))
L.sort(key=lambda x: x['study'].lower())
json.dump(dict(note='The IRIS List: published language-model studies IRIS has read and indexed, with classification, date indexed and receipt. A classification for indexing, not an assessment.', terms='Free to download and cite with attribution. All rights reserved. Text and data mining and use as AI training data are not permitted: https://indahl.ai/terms#ai-training', studies=L),
          open(I + 'matrix_page/iris_list.json', 'w'), ensure_ascii=False, indent=0)
shutil.copy(I + 'matrix_page/iris_list.json', B + 'cloudflare-workers/heuremen-door/public/iris/list.json')
li = lambda t: f'<li>Data: <a href="{t[6:]}">{E(t[6:])}</a></li>' if t.startswith('Data: /iris/runs/') else f'<li>{E(t)}</li>'
rows_h = ''.join(f'<tr><td><a href="{E(x["link"])}">{E(x["study"])}</a></td><td>{E(x["classification"])}</td><td>{E(x["indexed"])}</td><td><details><summary>receipt</summary><ul>'
                 + ''.join(li(t) for t in x['receipt']) + '</ul></details></td></tr>' for x in L)
body = ('<p class="crumb"><a href="/iris">IRIS</a> &middot; <a href="/iris/list.json">download</a></p><p class="meta">Intervals in the receipts are 95% intervals, by percentile bootstrap over items unless a receipt says otherwise.</p><section><div class="scroll"><table class="mtx list"><thead><tr>'
        '<th>Study</th><th>IRIS classification</th><th>Indexed</th><th>Receipt</th></tr></thead><tbody>' + rows_h + '</tbody></table></div></section>')
open(I + 'matrix_page/iris_list_body.html', 'w').write(body)
print(len(L), sum(x['classification'] == 'Recounted' for x in L))
