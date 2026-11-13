#!/usr/bin/env python3
"""Builds the results table for the IRIS page from the scorer and paired.py, and adds one ledger row per printed cell.
Writes falcon_results.txt (source lines for the ledger) and falcon_results.html (fragment included by build_site.py)."""
import os, sys, json, subprocess
B = os.path.dirname(os.path.abspath(__file__)); IB = os.path.join(B, '..'); LED = os.path.expanduser('~/bones-forge/ledger')
FAM = [('P1', 'Forced verdict', 'Fault 19'), ('P2', 'Verdict without a width', 'Fault 25'), ('P3', 'Unchecked equals sign', 'Fault 29'), ('P4', 'Best of n', 'Fault 3')]
MODELS = [('falcon3_base', 'Untouched model'), ('falcon3_trained', 'Trained on the Standards'), ('falcon3_mixed', 'Trained with mixed labels (control)')]
R = {}; NR = {}   # NR: replies read and items asked per set, model and family (30 Oct 2026: counts printed under each cell)
for s in ('tA', 'tB'):
    d = os.path.join(IB, 'faultsbench_' + s); sys.path.insert(0, d); sys.modules.pop('score', None)
    import score as S; sys.path.pop(0)
    for m, _ in MODELS:
        r = S.score(m)
        for f, _, _ in FAM:
            v = r['fam'][f]; o = str(v['outcome'])
            ct = r['model_gate'] != 'pass' or o.startswith('CANNOT_TELL (family') or o.startswith('CANNOT_TELL (repeat')
            p = v['bare_fault']; R[(s, m, f)] = None if ct else f"{round(p[0]*100)}% [{round(p[1]*100)}, {round(p[2]*100)}]"
            NR[(s, m, f)] = (v['n_read'], sum(1 for k_, i_ in S.IT.items() if i_['fam'] == f and i_.get('kind') not in ('control', 'gw')))
paired = json.load(open(os.path.join(B, 'paired_results.json')))
W = {'AHEAD': 'ahead', 'BEHIND': 'behind', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}; G = {'GAIN': 'gain', 'NO GAIN': 'no gain', 'CANNOT_TELL': 'cannot tell'}
lines, rows, cells = [], [], {}
def cell(m, f):
    a, b = R[('tA', m, f)], R[('tB', m, f)]
    return f"A {a or 'cannot tell'}, B {b or 'cannot tell'}"
def hcell(m, f):   # the cell as printed: the ledger text first, then how many replies could be read (the ledger snippet is the start of this text)
    (ra, na), (rb, nb) = NR[('tA', m, f)], NR[('tB', m, f)]
    return cell(m, f) + f'<span class="by"> Replies read: A {ra} of {na}, B {rb} of {nb}</span>'
for f, name, fn in FAM:
    for m, mn in MODELS:
        c = cell(m, f); cells[(f, m)] = c
        for s in ('tA', 'tB'): lines.append(f"{s} {f} {m} {R[(s, m, f)] or 'cannot tell'}")
        for s in ('tA', 'tB'): lines.append(f"read {s} {f} {m} {NR[(s, m, f)][0]} of {NR[(s, m, f)][1]}")   # 30 Oct 2026: replies read per cell, source of the counts printed under each rate
    for ref in ('falcon3_base', 'falcon3_mixed'):
        p = [x for x in paired if x['family'] == f and x['vs'] == ref][0]
        t = f"A {W[p['A']['outcome']]}, B {W[p['B']['outcome']]}: {G[p['gain']]}"; cells[(f, ref + '_vs')] = t
        lines.append(f"paired {f} trained vs {ref} {t}")
open(os.path.join(B, 'falcon_results.txt'), 'w').write('\n'.join(lines) + '\n')
h = ['<div class="scroll"><table class="mtx"><thead><tr><th>Fault</th><th>Untouched model</th><th>Trained on the Standards</th><th>Trained with mixed labels</th><th>Trained against untouched</th><th>Trained against mixed labels</th></tr></thead><tbody>']
for f, name, fn in FAM:
    h.append(f"<tr><td>{name}<span class=\"by\"> {fn}</span></td><td>{hcell('falcon3_base', f)}</td><td>{hcell('falcon3_trained', f)}</td><td>{hcell('falcon3_mixed', f)}</td><td>{cells[(f,'falcon3_base_vs')]}</td><td>{cells[(f,'falcon3_mixed_vs')]}</td></tr>")
h.append('</tbody></table></div>')
note = ('<p class="bench-note">Share of readable replies that commit the Fault with the plain prompt, with the 95% Wilson interval, on evaluation set A and set B. Under each rate is how many of the family\'s replies could be read. Cannot tell: that model failed its repeat check or the Fault\'s check items, so no rate is shown. '
        'The last two columns are the paired difference per item with a 2,000-sample bootstrap. Ahead means fewer Faults. A gain is called only where trained is ahead in both sets. The mixed-label model is a control trained on partly wrong labels, so a gain against it can come from the control doing worse. Against the untouched model no family shows a gain. '
        'Replies with no readable answer are left out of the rates. These are one training run per model. No ranking.</p>')
open(os.path.join(B, 'falcon_results.html'), 'w').write(''.join(h) + note)
def run(*a): return subprocess.run(['python3', 'ledger.py', *a], capture_output=True, text=True, cwd=LED)
n = 0
for f, name, fn in FAM:
    for m, mn in MODELS:
        g = f"A {R[('tA',m,f)] or 'cannot tell'}"; src = f"tA {f} {m} {R[('tA',m,f)] or 'cannot tell'}"
        r = run('add', f"iris.falcon.{f.lower()}.{m.split('_')[1]}", '--claim', f"Falcon training, {name}, {mn}: share of readable replies committing the Fault, bare prompt, sets A and B", '--value', cells[(f, m)], '--outcome', 'RECORD', '--source', 'iris_index/falcon_train/falcon_results.txt', '--grep', src, '--on', 'iris_matrix', cells[(f, m)])
        if r.returncode: print(f, m, (r.stdout + r.stderr).strip()[:140])
        else: n += 1
    for ref in ('base', 'mixed'):
        t = cells[(f, f'falcon3_{ref}_vs')]
        r = run('add', f"iris.falcon.{f.lower()}.vs_{ref}", '--claim', f"Falcon training, {name}: trained against {ref} paired reading, sets A and B", '--value', t, '--outcome', 'RECORD', '--source', 'iris_index/falcon_train/falcon_results.txt', '--grep', f"paired {f} trained vs falcon3_{ref} {t}", '--on', 'iris_matrix', t)
        if r.returncode: print(f, ref, (r.stdout + r.stderr).strip()[:140])
        else: n += 1
print('ledger rows added', n)
for l in lines[:6]: print(l)
print(open(os.path.join(B, 'falcon_results.txt')).read()[-700:])
