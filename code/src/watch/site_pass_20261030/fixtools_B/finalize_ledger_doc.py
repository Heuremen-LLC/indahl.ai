#!/usr/bin/env python3
"""Builds ~/bones-forge/watch/site_pass_20261030/LEDGER_TODO_B.md from LEDGER_TODO_B.rows.md (written by bfix_apply.py), the panel rows and the source.grep moves."""
import json, re, shlex, subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.expanduser('~/bones-forge/watch/site_pass_20261030/')
rows = open(HERE + '/LEDGER_TODO_B.rows.md').read().strip().split('\n')
n_off = sum(1 for l in rows if 'ledger.py off ' in l); n_on = len(rows) - n_off
hdr = f"""# LEDGER_TODO_B (lane B and the lane C items in the same files), 30 Oct 2026
Bones runs these. Nothing here has been run. The ledger reads indahl-ai/qia.html (surface qia_matrix), so the lines in part 1 are for the rebuilt page: run them, then build and ship.
Order: part 1 and part 3 before the build (the surface edit is already in qia_leads/matrix_page/qia_body.html), part 2 after ledger.py gets the five new surface keys.

## Part 1. Re-record the snippets of every qia.* row whose cell text changed ({n_off} rows, {n_on} snippets)
Cause: the cell text of the calibrated rows and the Braket lines was changed at its source (fixes B-11, B-12, B-13, B-18, B-19, B-20, B-24, B-25, B-27 and C-1 to C-14, C-18, C-19, C-22, C-23). Each row gets `off` then one `on` per snippet. A snippet that did not change is re-recorded unchanged, a snippet that did is replaced by the new cell text (found in the new qia_body.html, checked by script: 0 of {n_on} snippets missing).
Rows worth a look before you run them, because the number or the claim moved and not only the wording:
- qia.res.fire_reddy, qia.fix.zenodo:23123273: the ibm_fez reading is now both copies and CANNOT_TELL (RESULT_REDDY lines 4-10). The row's outcome field (CONSISTENT) may want `ledger.py set`.
- qia.res.fire_ktn: descriptive only, one arm failed its known-good check.
- qia.res.fire_2508.16895, qia.fix.2508.16895: pair-level collapse stated for two layouts, code Q17 changed to Q19.
- qia.norun.recount_10.5281/zenodo.21479684, qia.fix.zenodo:21479684: "1.4 sigma at 16,384 shots" is replaced by 0.13 sigma (the record's Table 17.1 puts -0.0010 and +0.0007 under two different columns). Two agents found this independently. THE_BOOK C113 carries the old number.
- qia.res.fill_2605.30676: the "13 to 21%" became "17 to 20%" under one ruler (medians). New computation, script in fixtools_B/agent_out/R2_cauca_medians.py.
- qia.res.run_boussahi: "21 of 21 runs reproduce" left as it is, the audits say 22 in one place (see FIXLOG_B).

```
"""
panel = open(HERE + '/ledger_panel_part.md').read()
# part 3: source.grep moves
L = {json.loads(l)['id']: json.loads(l) for l in open(os.path.expanduser('~/bones-forge/ledger/ledger.jsonl')) if l.strip()}
out = subprocess.run(['python3', os.path.expanduser('~/bones-forge/ledger/check_ledger.py')], capture_output=True, text=True).stdout
ids = [l.split()[1] for l in out.split('\n') if l.strip().startswith('SOURCE') and l.split()[1].startswith('qia.')]
MP = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/'); cmds = []
for i in ids:
    r = L[i]; f = r['source']['file']; g = r['source']['grep']
    old = open(MP + f.split('/')[-1] + '.pre-sitepass-20261030').read(); new = open(os.path.expanduser('~/bones-forge/') + f).read()
    if g not in old: continue
    ol = [l for l in old.split('\n') if g in l][0]
    if f.endswith('.json'):
        olines = old.split('\n'); nlines = new.split('\n'); txt = nlines[olines.index(ol)].strip().strip(',').strip('"')
    else:
        key = ol[:ol.index('dict(')] if 'dict(' in ol else ol[:30]
        nl = [l for l in new.split('\n') if l.startswith(key)][0]
        m = re.search(r"fix='(.*)'\)?,?\s*$", nl) or re.search(r"fix='(.*?)'(?:,|\))", nl); txt = m.group(1) if m else nl
    cand = re.match(r"""[^'"\\]{20,60}""", txt); ng = cand.group(0).rstrip() if cand else None
    if ng and ng in new:
        cmds.append(f"python3 ~/bones-forge/ledger/ledger.py set {i} --field source.grep --to {shlex.quote(ng)} --why 'Site pass 30 Oct 2026: the source text was changed, grep moved to the new text' --evidence {f}")
part3 = f"""
## Part 3. Move the source grep of {len(cmds)} rows whose source text was changed (check_ledger.py shows these as SOURCE drift today)
qia_key.py and abc_reports.json mirror the cell text the page printed, so the fix text was changed there too. Each row's source.grep points at the old words. Each command moves it to the first words of the new text (checked present in the file). No --checks is needed for source.grep.
```
""" + '\n'.join(cmds) + "\n```\n"
open(D + 'LEDGER_TODO_B.md', 'w').write(hdr + '\n'.join(rows) + '\n```\n' + panel + part3)
print('rows', n_off, n_on, 'part3', len(cmds), len(ids))
