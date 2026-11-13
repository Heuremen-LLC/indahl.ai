"""build.py: stages the indahl.ai datasets for Hugging Face (27 Oct 2026, his word: only what is on indahl.ai). Output: stage/<repo>/ with README.md (dataset card) and the files."""
import os, re, json, html, shutil, glob, sys
sys.path.insert(0, os.path.expanduser('~/bones-forge/indahl-ai')); from hlcref import ref
B = os.path.expanduser('~/bones-forge/'); P = B + 'cloudflare-workers/heuremen-door/public/'; S = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stage')
shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
TERMS = ("Free to download, read and cite with attribution (Heuremen LLC, with a link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted. "
         "Names of authors appear as published in their own papers. To have a name or a study removed: https://indahl.ai/contact . Policy: https://indahl.ai/terms#ai-training")
def card(title, desc, tags, body):
    return ("---\nlicense: other\nlicense_name: heuremen-attribution-no-ai-training\nlicense_link: https://indahl.ai/terms#ai-training\npretty_name: \"" + title + "\"\ntags:\n" + ''.join(f"- {t}\n" for t in tags) + "---\n\n# " + title + "\n\n" + desc + "\n\n" + body + "\n\n## Terms\n\n" + TERMS + " Reference " + ref("hf:" + title) + ".\n\nPublished by Heuremen LLC. Source: https://indahl.ai . We found it.\n")
# 9 Nov 2026 (his word: link the site to HF): each card links back to the indahl.ai page its data comes from.
PAGE = {'qia-list': 'https://indahl.ai/qia/list', 'qia-calibrated-studies': 'https://indahl.ai/qia', 'qia-run-data': 'https://indahl.ai/qia', 'iris-list': 'https://indahl.ai/iris/list',
        'iris-run-data': 'https://indahl.ai/iris', 'iris-training-runs': 'https://indahl.ai/iris/lab', 'iris-judge-counts': 'https://indahl.ai/iris', 'oy-schools': 'https://indahl.ai/oy'}
def repo(name, files, title, desc, tags, body):
    d = os.path.join(S, name); os.makedirs(d)
    if name in PAGE: body = body + '\n\nPage on indahl.ai: ' + PAGE[name] + ' .'
    for src, dst in files: os.makedirs(os.path.dirname(os.path.join(d, dst)) or d, exist_ok=True); shutil.copy(src, os.path.join(d, dst))
    open(os.path.join(d, 'README.md'), 'w').write(card(title, desc, tags, body))
def jl(path, rows): open(path, 'w', encoding='utf-8').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n')
# QIA list
q = json.load(open(P + 'qia/list.json')); T = os.path.join(S, '_t'); os.makedirs(T)
rows = q['studies']; jl(T + '/list.jsonl', rows)
repo('qia-list', [(P + 'qia/list.json', 'list.json'), (T + '/list.jsonl', 'list.jsonl')], 'QIA List: indexed quantum hardware studies',
     'Every published quantum hardware study QIA has read and indexed, with its QIA classification, the date indexed and a receipt of what was read. A classification for indexing, not an assessment of any study or its authors.',
     ['quantum-computing', 'ibm-quantum', 'reproducibility', 'research-integrity'], 'One row per study in `list.jsonl` (the same rows as `list.json`). Codes are explained at https://indahl.ai/qia/key .')
# calibrated studies from the QIA page table
body = open(B + 'qia_leads/matrix_page/qia_body.html', encoding='utf-8').read(); i = body.index('Calibrated Studies: Corporate'); seg = body[i:body.index('Inventory of Published Studies')]
def txt(h): return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
cal = []
for m in re.finditer(r'<tr>(.*?)</tr>', seg, re.S):
    c = re.findall(r'<td>(.*?)</td>', m.group(1), re.S)
    if len(c) != 6: continue
    link = re.findall(r'href="(https?://[^"]+)"', c[1]); codes = re.findall(r'class="code" href="/qia/key#([A-Z]\d+)"', c[4])
    cal.append(dict(organisation=txt(c[0]), work=txt(c[1]), source_link=link[0] if link else '', published=txt(c[2]), measured_or_recounted=txt(c[3]), qia_codes=codes, qia_calibration=txt(re.sub(r'<span class="codes">.*?</span>', '', c[4], flags=re.S)), how=txt(c[5])))
jl(T + '/calibrated.jsonl', cal)
repo('qia-calibrated-studies', [(T + '/calibrated.jsonl', 'calibrated.jsonl')], 'QIA calibrated studies',
     'Published quantum studies whose numbers change under a QIA calibration, with what the paper states, what was measured or recounted, and the fix.',
     ['quantum-computing', 'ibm-quantum', 'reproducibility', 'calibration'], 'One row per calibrated study in `calibrated.jsonl`. Page per study: https://indahl.ai/qia . Codes: https://indahl.ai/qia/key .')
repo('qia-run-data', [(f, 'runs/' + os.path.basename(f)) for f in sorted(glob.glob(P + 'qia/runs/*.zip'))], 'QIA run data',
     'One zip per study or run behind the QIA tables: released files, our reading and the scripts that produced each figure. Each zip carries its own TERMS.txt.', ['quantum-computing', 'ibm-quantum', 'reproducibility'], 'Files are in `runs/`. Each zip is named by the study it belongs to.')
# IRIS
iq = json.load(open(P + 'iris/list.json')); jl(T + '/iris_list.jsonl', iq['studies'])
repo('iris-list', [(P + 'iris/list.json', 'list.json'), (T + '/iris_list.jsonl', 'list.jsonl')], 'IRIS List: indexed language-model evaluation studies',
     'Published language-model evaluation studies IRIS has read and indexed, with classification, date indexed and receipt. A classification for indexing, not an assessment.',
     ['llm-evaluation', 'reproducibility', 'benchmarks', 'research-integrity'], 'One row per study in `list.jsonl`. Codes L1 to L9: https://indahl.ai/iris/key .')
repo('iris-run-data', [(f, 'runs/' + os.path.basename(f)) for f in sorted(glob.glob(P + 'iris/runs/*.zip'))], 'IRIS run data',
     'Zips behind the IRIS tables: model runs on open-weight models, study recounts and the matrix rounds, with the scripts that made each figure. Each zip carries its own TERMS.txt.', ['llm-evaluation', 'reproducibility', 'benchmarks'], 'Files are in `runs/`.')
repo('iris-training-runs', [(B + 'iris_index/training_counts/summary.json', 'summary.json'), (B + 'iris_index/training_counts/training_counts.py', 'training_counts.py')], 'IRIS fine-tuning run numbers',
     'Numbers from the logs and configs of our own LoRA fine-tuning of one open model: per-session validation loss curves, iterations, tokens, sessions that reached a loss that was not a number, adapter folder and checkpoint counts, and two candidate-against-live evaluations with the promotion bar. Numbers only. The training text, the adapter weights and the logs are not published.',
     ['fine-tuning', 'lora', 'reproducibility'], 'Files: `summary.json` (every session with its validation curve, plus totals) and `training_counts.py` (the script that produced it from the logs). One caveat: until 26 August the validation step scored a random 100 of 489 examples. Context and key: https://indahl.ai/iris .')

# ATLAS data centers (27 Oct 2026). Own card: the data carries the sources' licences (ODbL 1.0 for the OpenStreetMap part, CC BY 4.0 for Epoch AI), not the house terms.
_d = os.path.join(S, 'atlas-datacenters'); os.makedirs(_d)
for _src, _dst in [(B + 'atlas/datacenters.json', 'datacenters.json'), (B + 'atlas/summary.json', 'summary.json'), (B + 'atlas/build_atlas.py', 'build_atlas.py'), (B + 'atlas/geocode_epoch.py', 'geocode_epoch.py')]: shutil.copy(_src, os.path.join(_d, _dst))
open(os.path.join(_d, 'README.md'), 'w').write("---\nlicense: odbl\npretty_name: \"ATLAS: United States data centers\"\ntags:\n- data-centers\n- infrastructure\n- openstreetmap\n- geospatial\n---\n\n# ATLAS: United States data centers\n\n"
 "Sites mapped in two open sources, pulled 2026-10-28: features tagged as data centers in OpenStreetMap (merged when within 250 m with the same name), and the United States AI data centers in Epoch AI's dataset, with coordinates added by us from the US Census geocoder and OpenStreetMap Nominatim. This is what those sources hold, not a count of every data center. Map and context: https://indahl.ai/atlas .\n\n"
 "Files: `datacenters.json` (records with their source), `summary.json` (counts), `build_atlas.py` and `geocode_epoch.py` (the scripts).\n\n"
 "Licences: the OpenStreetMap part is (c) OpenStreetMap contributors under the ODbL 1.0 (https://www.openstreetmap.org/copyright), and this combined database is shared under the ODbL 1.0. The Epoch AI fields are CC BY 4.0: Epoch AI, 'AI data centers', epoch.ai/data/ai-data-centers.\n\nReference: " + ref('dataset:atlas-datacenters') + "\n")
repo('oy-schools', [(B + 'oy_index/schools.json', 'schools.json'), (B + 'oy_index/build_schools.py', 'build_schools.py'), (B + 'oy_index/smallpass/course_pass.py', 'course_pass.py'), (B + 'oy_index/smallpass/small_pass.py', 'small_pass.py'), (B + 'oy_index/smallpass/ROSTER.csv', 'ROSTER.csv'), (B + 'oy_index/smallpass/ROSTER22.csv', 'ROSTER22.csv')], 'OY small private colleges: what a script read on their public pages',
     'One record per small private liberal arts college (federal IPEDS directory, Carnegie 2021 classes Arts & Sciences focus and Diverse fields): whether the site could be read by script, sentences on the school\'s own pages that name AI with a number or study word, and public catalog course titles on AI, technology and society and related topics. Script reads, not hand-checked recounts. Not an assessment of any school.',
     ['education', 'higher-education', 'ai-policy', 'reproducibility'], 'Files: `schools.json` (one record per school), `ROSTER.csv` and `ROSTER22.csv` (the school lists from IPEDS HD2024), and the scripts that read the sites. Context: https://indahl.ai/oy .')
repo('iris-judge-counts', [(B + 'iris_index/judge_counts/summary.json', 'summary.json'), (B + 'iris_index/judge_counts/judge_counts.py', 'judge_counts.py')], 'IRIS judge and orchestration counts',
     'Counts from the judge and orchestration logs of our own pipeline: verdict mix, how often a judge model repeats itself on the same item, and how often the orchestrating model had to be forced to make a call. Counts only. The logs themselves are not published.',
     ['llm-evaluation', 'llm-as-judge', 'reproducibility'], 'Files: `summary.json` (every number with its 95% interval) and `judge_counts.py` (the script that produced it from the logs). Context and key: https://indahl.ai/iris .')
shutil.rmtree(T)
for r in sorted(os.listdir(S)): print(r, sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(S, r)) for f in fs) // 1024, 'KB')
