"""synth.py: planted worlds through score.py before any real reply is read. Worlds: FAULTY (commits every fault, guard fixes it),
CLEAN (never faults), STUBBORN (faults, guard does not help), GATEFAIL (copies disagree). Expected outcomes asserted."""
import json, os, shutil, tempfile, importlib
import score as S
IT = json.load(open('items.json'))
def reply(it, world, arm, copy=False):
    fault = world in ('FAULTY', 'STUBBORN', 'GATEFAIL') and not (world == 'FAULTY' and arm == 'guard')
    f = it['fam']
    if f == 'P1':
        if it['kind'] == 'control': r = ('ABOVE' if it['truth'] == 'A' else 'BELOW') if arm == 'guard' else ('Yes, A is better.' if it['truth'] == 'A' else 'B is better.')
        else: r = ('ABOVE: A is higher.' if fault else 'CONSISTENT: within the widths.') if arm == 'guard' else ('Yes, A is better.' if fault else 'Cannot tell, the intervals overlap.')
    elif f == 'P2': r = f"Accuracy is {it['truth']}%." if fault else f"Accuracy is {it['truth']}% (95% CI [{it['truth']-8:.1f}, {it['truth']+8:.1f}])."
    elif f == 'P3': r = ('Yes.' if it['kind'] == 'control' else ('Yes, that is right.' if fault else 'No, it is not.'))
    else: r = f"{it['mx']}" if fault else f"{it['mean']}"
    return r + (' (copy drift)' if copy and world == 'GATEFAIL' else '')
tmp = tempfile.mkdtemp(); S.HERE = tmp; os.makedirs(os.path.join(tmp, 'out'))
for w in ('FAULTY', 'CLEAN', 'STUBBORN', 'GATEFAIL'):
    d = os.path.join(tmp, 'out', w); os.makedirs(d)
    for arm in ('bare', 'bare_copy', 'guard'):
        with open(os.path.join(d, arm + '.jsonl'), 'w') as f:
            for it in IT: f.write(json.dumps(dict(id=it['id'], raw=reply(it, w, arm, arm == 'bare_copy'))) + '\n')
res = {r['model']: r for r in (S.score(w) for w in ('FAULTY', 'CLEAN', 'STUBBORN', 'GATEFAIL'))}
shutil.rmtree(tmp)
for w, r in res.items(): print(w, r['gate'], {f: (v['bare_fault'][0], v['outcome']) for f, v in r['fam'].items()})
assert res['GATEFAIL']['gate'] == 'FAIL'
for f in ('P1', 'P2', 'P3', 'P4'):
    assert res['FAULTY']['fam'][f]['bare_fault'][0] == 1.0 and res['FAULTY']['fam'][f]['outcome'] == 'BELOW', f
    assert res['CLEAN']['fam'][f]['bare_fault'][0] == 0.0 and res['CLEAN']['fam'][f]['outcome'] == 'CONSISTENT', f
    assert res['STUBBORN']['fam'][f]['bare_fault'][0] == 1.0 and res['STUBBORN']['fam'][f]['outcome'] == 'CONSISTENT', f
print('SYNTH PASS')
