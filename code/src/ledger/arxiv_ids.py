"""arxiv_ids.py -- puts the arXiv identifiers on every surface once arXiv announces (Monday 2 Nov 2026, 20:00 ET).
  python3 arxiv_ids.py --stage                         check today that every edit's old text is found once and every Zenodo and HF target answers
  python3 arxiv_ids.py --darkwave ID --readout ID      dry run: each ID checked against arXiv's own listing (the title must match), every edit printed
  python3 arxiv_ids.py --darkwave ID --readout ID --go apply: page sources, the Hugging Face data cards, the Zenodo records' related identifiers,
                                                       then ship.sh. Either ID may be left out (a paper not yet announced is skipped).
Tokens are read by name inside this script and never printed."""
import argparse, json, os, re, subprocess, sys, tempfile, urllib.request
B = os.path.expanduser('~/bones-forge')
PAPERS = {
    'darkwave': dict(title="A Readout's Kick Is a Turn", zenodo=('record', '23843468'), hf='indahl/darkwave-run-data',
                     card_src=B + '/arxiv_keystone/hf_stage/README.md',
                     edits=[(B + '/arxiv_keystone/site/darkwave.html',
                             'Lasts</i>, submitted to arXiv (quant-ph) on 1 November 2026.',
                             'Lasts</i>, <a href="https://arxiv.org/abs/{ID}">arXiv:{ID}</a> (quant-ph).')]),
    'readout': dict(title='A Readout Is Not an Idle', zenodo=('concept', '23169755'), hf='indahl/readout-run-data', card_src=None,
                    edits=[(B + '/heuremen.org/index.html',
                            '<p class="paper"><a href="/a-readout-is-not-an-idle.pdf">Paper (PDF)</a></p>',
                            '<p class="paper"><a href="/a-readout-is-not-an-idle.pdf">Paper (PDF)</a> &middot; <a href="https://arxiv.org/abs/{ID}">arXiv:{ID}</a></p>'),
                           (B + '/indahl-ai/build_site.py',
                            '<i>A Readout Is Not an Idle</i></a> measures',
                            '<i>A Readout Is Not an Idle</i></a> (<a href="https://arxiv.org/abs/{ID}">arXiv:{ID}</a>) measures')]),
}
CARD_OLD = 'License: Creative Commons Attribution 4.0. Cite the paper and the Zenodo record.'
CARD_NEW = 'Paper: arXiv:{ID}, https://arxiv.org/abs/{ID}\n\n' + CARD_OLD
ZTOK = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/zenodo-token')
def get(url, tok=None, method='GET', data=None):
    h = {'Authorization': 'Bearer ' + tok} if tok else {}
    if data is not None: h['Content-Type'] = 'application/json'
    return json.load(urllib.request.urlopen(urllib.request.Request(url, method=method, data=data, headers=h), timeout=120))
def arxiv_title(aid):
    x = urllib.request.urlopen(f'https://export.arxiv.org/api/query?id_list={aid}', timeout=60).read().decode()
    m = re.findall(r'<title>(.*?)</title>', x, re.S); return ' '.join(m[1].split()) if len(m) > 1 else ''
def zenodo_record(kind, rid):
    r = get(f'https://zenodo.org/api/records/{rid}/versions/latest') if kind == 'concept' else get(f'https://zenodo.org/api/records/{rid}')
    return str(r['id']), r['metadata'].get('title', '')
def hf_card(repo):
    from huggingface_hub import hf_hub_download
    return open(hf_hub_download(repo, 'README.md', repo_type='dataset', local_dir=tempfile.mkdtemp())).read()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--darkwave'); ap.add_argument('--readout'); ap.add_argument('--stage', action='store_true'); ap.add_argument('--go', action='store_true')
    a = ap.parse_args(); ids = {k: getattr(a, k) for k in PAPERS if getattr(a, k)}
    if not a.stage and not ids: sys.exit('nothing to do: give --stage or at least one ID')
    for k, v in ids.items():
        if not re.fullmatch(r'\d{4}\.\d{4,5}', v): sys.exit(f'REFUSED: {k} id {v} is not an arXiv id')
        t = arxiv_title(v)
        if PAPERS[k]['title'].lower() not in t.lower(): sys.exit(f'REFUSED: arXiv {v} is titled "{t}", expected "{PAPERS[k]["title"]}"')
        print(f'{k}: arXiv {v} is "{t}"')
    todo = PAPERS if a.stage else {k: PAPERS[k] for k in ids}
    for k, p in todo.items():
        aid = ids.get(k, '0000.00000')
        for f, old, new in p['edits']:
            n = open(f).read().count(old)
            print(f'{k}: {os.path.relpath(f, B)}: old text found {n} time(s)' + ('' if n == 1 else '  <-- MUST BE 1'))
            if n != 1: sys.exit('REFUSED: an edit does not match exactly once')
        card = open(p['card_src']).read() if p['card_src'] else hf_card(p['hf'])
        print(f'{k}: card {p["hf"]}: license line found {card.count(CARD_OLD)} time(s), already has arXiv: {"arxiv.org/abs" in card}')
        if card.count(CARD_OLD) != 1: sys.exit('REFUSED: card line does not match exactly once')
        zid, zt = zenodo_record(*p['zenodo']); print(f'{k}: Zenodo record {zid} "{zt[:70]}"')
        if a.go and k in ids:
            for f, old, new in p['edits']: s = open(f).read(); open(f, 'w').write(s.replace(old, new.format(ID=aid))); print('  edited', os.path.relpath(f, B))
            card = card.replace(CARD_OLD, CARD_NEW.format(ID=aid))
            if p['card_src']: open(p['card_src'], 'w').write(card)
            from huggingface_hub import HfApi
            try: from huggingface_hub import get_stored_tokens
            except ImportError: from huggingface_hub.utils import get_stored_tokens
            HfApi(token=get_stored_tokens()['oauth-indahl']).upload_file(path_or_fileobj=card.encode(), path_in_repo='README.md', repo_id=p['hf'], repo_type='dataset', commit_message=f'Heuremen LLC: arXiv:{aid}')
            print('  card uploaded', p['hf'])
            tok = open(ZTOK).read().strip(); api = f'https://zenodo.org/api/deposit/depositions/{zid}'
            get(api + '/actions/edit', tok, 'POST', b''); d = get(api, tok); m = d['metadata']; ri = m.get('related_identifiers', [])
            if not any(x.get('identifier', '').endswith(aid) for x in ri):
                ri.append({'relation': 'isSupplementTo', 'identifier': f'arXiv:{aid}', 'scheme': 'arxiv', 'resource_type': 'publication-preprint'})
            m['related_identifiers'] = ri; get(api, tok, 'PUT', json.dumps({'metadata': m}).encode()); r = get(api + '/actions/publish', tok, 'POST', b'')
            print('  Zenodo', zid, r.get('state'))
    if a.go and ids:
        msg = 'arXiv identifiers on the pages, data cards and Zenodo records: ' + ', '.join(f'{k} arXiv:{v}' for k, v in ids.items())
        subprocess.run([B + '/ledger/ship.sh', msg], check=True)
    print('stage check passed' if a.stage else ('applied and shipped' if a.go else 'dry run only: add --go to apply'))
if __name__ == '__main__': main()
