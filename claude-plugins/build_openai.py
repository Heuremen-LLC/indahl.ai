#!/usr/bin/env python3
"""Builds the ChatGPT plugin directory packages (OpenAI) from the same directory copies the Anthropic directory gets (13 Nov 2026,
Wayfinder: "keep it an indahl bundle like on anthropic, indahl-data yadda yadda yadda"). One package per plugin in plugins/ (the parts and
the indahl bundle): openai/<name>/ with .codex-plugin/plugin.json (interface block for the listing), skills, commands, .mcp.json where the
part has the indahl.ai connector, assets/logo.png and assets/icon.png, and openai/<name>.zip ready to upload. Plugins with the connector also
get openai/<name>.chatgpt-app-submission.json (every tool's hints and justifications, five positive and three negative tests).
Never edit openai/ by hand.   python3 build_openai.py"""
import json, os, re, shutil, urllib.request, zipfile
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, 'plugins'); O = os.path.join(H, 'openai')
ICONS = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/public/icons')
ORDER = ['indahl', 'indahl-data', 'standards', 'eval-check', 'reproduce', 'qia-calibration', 'darkwave-correction', 'prereg', 'readcheck', 'triangulate', 'batch', 'cannot-tell', 'both', 'outside-ruler', 'number-check', 'quote-check', 'source-check', 'controls', 'slack', 'correct', 'clause']
SUB = {   # subtitle (30 characters or fewer) and three starter prompts per listing
 'indahl': ('Stated vs. delivered, measured', ['What does indahl.ai measure?', "Is IBM's published T1 for ibm_kingston current?", 'Check this paper against the Standards.']),
 'indahl-data': ('Query every indahl.ai desk', ['List the indahl.ai divisions.', 'Do top Hugging Face licenses match their files?', 'Show every live test side by side.']),
 'standards': ('Check papers vs. the Standards', ['Check this paper against the Standards.', 'Which claim codes apply to this abstract?', 'Give me a recount card for this result.']),
 'eval-check': ('Check an LLM eval claim', ['Check this benchmark claim.', 'Is this eval run comparable to the vendor number?', 'Run the twelve eval checks on this result.']),
 'reproduce': ('Rerun an indahl.ai desk kit', ['List the desks with reproduce kits.', 'Reproduce the FLU desk.', 'Show what the TIME kit would run.']),
 'qia-calibration': ('Check an IBM Quantum run', ['Check this calibration record before my run.', 'Which records were in force during my run?', 'Run the same-job T1/T2 check.']),
 'darkwave-correction': ('Correct IBM Quantum readout', ['Check my backend for the Darkwave kit.', 'What would the Darkwave measurement cost?', 'Correct these counts with the kit.']),
 'prereg': ('Was the plan pushed first?', ['Was my plan pushed before the first run?', 'List what ran that the plan did not cover.', 'Check this repository for a pre-registration.']),
 'triangulate': ('Three blind reads, one verdict', ['Triangulate: is this claim right?', 'Get three independent reads on this decision.', 'Check this number against three seats.']),
 'batch': ('Big audits, batched', ['Audit every page of this site in batches.', 'Apply batch to this.', 'Show batch on an example.']),
 'cannot-tell': ("Say can't-tell, usefully", ["Is this claim right, or can't we tell yet?", 'Apply cannot tell to this.', 'Show cannot tell on an example.']),
 'both': ('Keep two explanations alive', ['Hold both explanations and tell me what separates them.', 'Apply both to this.', 'Show both on an example.']),
 'outside-ruler': ('Referee it before it ships', ['Referee this draft before I publish it.', 'Apply outside ruler to this.', 'Show outside ruler on an example.']),
 'number-check': ('Trace every figure', ['Check every number in this report against its source.', 'Run number check on this.', 'Show number check on an example.']),
 'quote-check': ('Every quote, verbatim', ['Check every quote in this draft against its source.', 'Run quote check on this.', 'Show quote check on an example.']),
 'source-check': ('Do the citations say it?', ['Check that every citation in this exists and says what is claimed.', 'Run source check on this.', 'Show source check on an example.']),
 'controls': ('Can your test actually fail?', ['Audit the controls of this study before we run it.', 'Run controls on this.', 'Show controls on an example.']),
 'slack': ('How far before it breaks?', ['How much slack does this prediction have?', 'Run slack on this.', 'Show slack on an example.']),
 'correct': ('Fix it beside, not over', ['Log this correction properly.', 'Run correct on this.', 'Show correct on an example.']),
 'clause': ('The sentence reviewers catch', ['Check the claims in this results paragraph.', 'Run clause on this.', 'Show clause on an example.']),
 'readcheck': ('Check blocks for readings', ['Make a check block for this reading.', 'Verify the check block in this folder.', 'List staged readings without a check block.']),
}
CAT = 'Education & Research'

def listing_name(p):
    return 'Indahl' if p == 'indahl' else ('Indahl ' + {'indahl-data': 'Data', 'qia-calibration': 'QIA Calibration', 'darkwave-correction': 'Darkwave', 'eval-check': 'Eval Check', 'cannot-tell': 'Cannot Tell', 'outside-ruler': 'Outside Ruler', 'number-check': 'Number Check', 'quote-check': 'Quote Check', 'source-check': 'Source Check'}.get(p, p.replace('-', ' ').title()))

def build(p):
    src = os.path.join(P, p); m = json.load(open(os.path.join(src, '.claude-plugin', 'plugin.json')))
    name = 'indahl' if p == 'indahl' else ('indahl-' + p if not p.startswith('indahl') else p)
    name = {'indahl-darkwave-correction': 'indahl-darkwave'}.get(name, name)
    dst = os.path.join(O, name); shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.claude-plugin', '__pycache__', '*.pyc'))
    os.makedirs(os.path.join(dst, '.codex-plugin'), exist_ok=True); os.makedirs(os.path.join(dst, 'assets'), exist_ok=True)
    shutil.copy(os.path.join(ICONS, 'icon-512.png'), os.path.join(dst, 'assets', 'logo.png')); shutil.copy(os.path.join(ICONS, 'icon-192.png'), os.path.join(dst, 'assets', 'icon.png'))
    sub, prompts = SUB[p]; assert len(sub) <= 30, sub
    desc = m['description']; has_mcp = os.path.exists(os.path.join(dst, '.mcp.json'))
    man = {'name': name, 'version': m.get('version', '1.0.0'), 'description': desc, 'author': {'name': 'Heuremen LLC', 'url': 'https://indahl.ai'},
           'homepage': 'https://indahl.ai/plugins', 'repository': 'https://github.com/Heuremen-LLC/indahl.ai', 'license': m.get('license', 'SEE LICENSE'),
           'keywords': m.get('keywords', []), 'skills': './skills/',
           'interface': {'displayName': listing_name(p), 'shortDescription': sub, 'longDescription': desc, 'developerName': 'Heuremen LLC', 'category': CAT,
                         'capabilities': [], 'websiteURL': 'https://indahl.ai', 'supportURL': 'https://indahl.ai/contact',
                         'privacyPolicyURL': 'https://indahl.ai/privacy', 'termsOfServiceURL': 'https://indahl.ai/terms', 'defaultPrompt': prompts,
                         'brandColor': '#111111', 'composerIcon': './assets/icon.png', 'logo': './assets/logo.png'}}
    if has_mcp: man['mcpServers'] = './.mcp.json'
    json.dump(man, open(os.path.join(dst, '.codex-plugin', 'plugin.json'), 'w'), indent=2)
    z = os.path.join(O, name + '.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for d, _, fs in os.walk(dst):
            for f in fs:
                if f == '.DS_Store': continue
                fp = os.path.join(d, f); zf.write(fp, os.path.relpath(fp, dst))
    return name, has_mcp, desc

def submission(name, desc):
    r = urllib.request.urlopen(urllib.request.Request('https://indahl.ai/mcp', data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}).encode(),
                               headers={'content-type': 'application/json', 'user-agent': 'indahl-openai-build'}), timeout=60)
    tools = json.load(r)['result']['tools']; names = {t['name'] for t in tools}; T = {}
    for t in tools:
        a = t['annotations']; assert a.get('readOnlyHint') is True and a.get('destructiveHint') is False and a.get('openWorldHint') is False, t['name']
        T[t['name']] = {'annotations': {'readOnlyHint': True, 'openWorldHint': False, 'destructiveHint': False},
                        'justifications': {'read_only_justification': "Only retrieves indahl.ai's own published measurements for this desk and returns them; nothing is created, changed or stored.",
                                           'open_world_justification': "Reads only indahl.ai's own public data and never writes to the internet or to any third-party system.",
                                           'destructive_justification': 'Cannot delete, overwrite, send or revoke anything; repeated calls return the same published data.'}}
    pos = [('Start with the list of what the app covers.', 'What does indahl.ai measure? List its divisions.', 'list_divisions', 'Lists each division with a one-line description and its page, and explains the four outcomes.'),
           ("Read IBM's published calibration for one processor.", 'What is the median T1 and T2 on ibm_kingston right now?', 'ibm_calibration', 'Returns the newest record stamp, qubit count and median T1, T2, readout and two-qubit error for ibm_kingston, with the record time.'),
           ('Check license claims for popular models.', 'How often do the most downloaded Hugging Face models state a license that differs from their license file?', 'huggingface_license_claims', 'Returns the disagreement share with its 95% interval and outcome, the counts by class, and examples read in full.'),
           ('Search the indexed studies.', 'Find studies on quantum error mitigation that QIA has indexed.', 'find_study', 'Returns matching studies with title, link, classification codes, date indexed and the receipt of what was read.'),
           ('Compare all live tests side by side.', 'Show every live test on indahl.ai in one table, ordered by outcome.', 'all_tests_side_by_side', 'Returns one row per live page with what was compared, failures, share with 95% interval and outcome, ordered by outcome.')]
    for x in pos: assert x[2] in names, x[2]
    neg = [('Do not trigger for general coding help.', 'Write a Python function that sorts a list of dictionaries by date.'),
           ('Do not trigger for personal scheduling.', 'What meetings do I have tomorrow, and can you move the 3pm?'),
           ('Do not trigger for stock trading advice.', 'Should I buy IBM stock this week?')]
    s = {'$schema': 'https://developers.openai.com/apps-sdk/schemas/chatgpt-app-submission.v1.json', 'schema_version': 1,
         'app_info': {'display_name': listing_name(name if name != 'indahl-data' else 'indahl-data'), 'subtitle': SUB['indahl' if name == 'indahl' else 'indahl-data'][0],
                      'description': desc, 'category': 'EDUCATION'},
         'tools': T,
         'test_cases': [{'description': d, 'user_prompt': u, 'file_attachment_urls': None, 'tools_triggered': tn, 'expected_output': e, 'expected_output_url': None} for d, u, tn, e in pos],
         'negative_test_cases': [{'description': d, 'user_prompt': u, 'file_attachment_urls': None, 'tools_triggered': None,
                                  'expected_output': "The app should not be invoked because the request is outside indahl.ai's published measurements.", 'expected_output_url': None} for d, u in neg]}
    json.dump(s, open(os.path.join(O, name + '.chatgpt-app-submission.json'), 'w'), indent=2)
    return len(T)

if __name__ == '__main__':
    shutil.rmtree(O, ignore_errors=True); os.makedirs(O)
    for p in ORDER:
        name, mcp, desc = build(p)
        extra = f', submission JSON for {submission(name, desc)} tools' if mcp else ''
        print(f'  openai: {name}.zip ({listing_name(p)}){extra}')
