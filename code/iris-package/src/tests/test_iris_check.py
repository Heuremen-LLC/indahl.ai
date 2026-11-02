#!/usr/bin/env python3
"""Tests for iris_check.py on the synthetic dataset in tests/data/, where the answers are planted. Run: python tests/test_iris_check.py"""
import warnings; warnings.simplefilter('ignore', ResourceWarning)
import os, sys, json, csv, glob, shutil, subprocess, tempfile, hashlib, unittest, re
H = os.path.dirname(os.path.abspath(__file__)); TOOL = os.path.join(os.path.dirname(H), 'iris_check.py'); D = os.path.join(H, 'data')
PLANTED = json.load(open(os.path.join(D, 'PLANTED.json')))
def run(*args, ok=True):
    r = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)
    if ok: assert r.returncode == 0, r.stderr
    return r
def latest(out, pat): return sorted(glob.glob(os.path.join(out, pat)))[-1]
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.data = os.path.join(self.tmp, 'data'); shutil.copytree(D, self.data); self.out = os.path.join(self.tmp, 'out')
    def tearDown(self): shutil.rmtree(self.tmp)
    def rep(self, *a, **kw): return run('repeat', *a, '--id-field', 'id', '--correct-field', 'correct', '--out', self.out, **kw)
    def f(self, n): return os.path.join(self.data, n + '.jsonl')
    def report(self): return json.load(open(latest(self.out, 'repeat_*.json')))
    def test_repeat_floor(self):
        self.rep(self.f('A1'), self.f('A2')); r = self.report()['repeat_A'][0]; p = PLANTED['A1_vs_A2']
        self.assertEqual((r['right_to_wrong'], r['wrong_to_right'], r['net']), (p['right_to_wrong'], p['wrong_to_right'], p['net']))
        self.assertAlmostEqual(r['repeat_floor'], p['repeat_floor'], places=4)
    def test_outcomes(self):
        for a, b, out in (('A1', 'B1', 'ABOVE'), ('B1', 'A1', 'BELOW'), ('A1', 'C1', 'CONSISTENT'), ('A1', 'E1', 'CANNOT_TELL')):
            shutil.rmtree(self.out, ignore_errors=True); self.rep(self.f(a), '--vs', self.f(b)); c = self.report()['comparison'][0]
            self.assertEqual(c['outcome'], out, (a, b, c))
            if (a, b) == ('A1', 'B1'): self.assertEqual((c['A_right_B_wrong'], c['A_wrong_B_right']), (60, 10)); self.assertLess(c['mcnemar_exact_p'], 1e-6)
            if (a, b) == ('A1', 'E1'): self.assertEqual((c['A_right_B_wrong'], c['A_wrong_B_right']), (14, 6)); self.assertAlmostEqual(c['mcnemar_exact_p'], 0.115318, places=5)
    def test_margin_moves_outcome(self):
        self.rep(self.f('A1'), '--vs', self.f('C1'), '--margin', '0.001'); self.assertEqual(self.report()['comparison'][0]['outcome'], 'CANNOT_TELL')
    def test_inputs_unchanged_and_hashed(self):
        before = sha(self.f('A1')); self.rep(self.f('A1'), self.f('A2')); self.assertEqual(before, sha(self.f('A1')))
        j = self.report(); self.assertTrue(all(i['sha256_before'] == i['sha256_after'] for i in j['inputs'])); self.assertEqual(j['inputs'][0]['sha256_before'], before)
        self.assertIn('unchanged', open(latest(self.out, 'repeat_*.html')).read())
    def test_out_inside_input_folder_refused(self):
        r = run('repeat', self.f('A1'), self.f('A2'), '--id-field', 'id', '--correct-field', 'correct', '--out', os.path.join(self.data, 'reports'), ok=False)
        self.assertNotEqual(r.returncode, 0); self.assertIn('inside the folder of an input', r.stderr); self.assertFalse(os.path.exists(os.path.join(self.data, 'reports')))
    def test_unmatched_ids_counted(self):
        short = os.path.join(self.data, 'short.jsonl'); lines = open(self.f('A2')).read().splitlines()[:390]; open(short, 'w').write('\n'.join(lines) + '\n')
        self.rep(self.f('A1'), short); j = self.report(); self.assertEqual((j['items'], j['left_out']), (390, 10))
    def sample(self, *extra): return run('sample', self.f('parser'), '--reply-field', 'reply', '--extracted-field', 'pred', '--label-field', 'family', '--id-field', 'id', '--out', self.out, *extra)
    def sheet(self):
        with open(latest(self.out, 'sample_*.csv'), newline='') as f: return list(csv.DictReader(f))
    def test_sample_shape_seed_and_fields(self):
        self.sample(); rows = self.sheet(); self.assertEqual(len(rows), 30)
        for fam in ('good', 'bad', 'edge'): self.assertEqual(sum(r['label'] == fam for r in rows), 10)
        src = {json.loads(l)['id']: json.loads(l) for l in open(self.f('parser'))}
        for r in rows: self.assertEqual((r['reply'], r['extracted']), (src[r['id']]['reply'], src[r['id']]['pred']))
        first = {r['id'] for r in rows}; shutil.rmtree(self.out); self.sample(); self.assertEqual(first, {r['id'] for r in self.sheet()})
        shutil.rmtree(self.out); self.sample('--seed', '2'); self.assertNotEqual(first, {r['id'] for r in self.sheet()})
        self.assertIn('misparsed', rows[0]); self.assertIn('cannot tell (parser)', open(latest(self.out, 'sample_*.html')).read())
    def test_sample_small_group_and_n(self):
        self.sample('-n', '70'); self.assertEqual(len(self.sheet()), 180)   # groups hold 60 each, so all of them
        shutil.rmtree(self.out); self.sample('-n', '3'); self.assertEqual(len(self.sheet()), 9)
    def test_tally_rule_on_planted_parser_errors(self):
        self.sample(); rows = self.sheet(); src = {json.loads(l)['id']: json.loads(l) for l in open(self.f('parser'))}
        for r in rows:   # the reader's verdict: the answer is the last number in the reply
            ans = re.findall(r'\d+', r['reply'])[-1]; r['misparsed'] = 'x' if ans != r['extracted'] else ''
        os.makedirs(os.path.join(self.tmp, 'sheets')); sheet = os.path.join(self.tmp, 'sheets', 'filled.csv')
        with open(sheet, 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        out2 = os.path.join(self.tmp, 'tally'); run('sample', '--tally', sheet, '--out', out2)
        t = {r['label']: r for r in json.load(open(latest(out2, 'tally_*.json')))['tally']}
        self.assertEqual((t['good']['misparsed'], t['good']['reading']), (0, 'rate can be read'))
        self.assertEqual((t['bad']['misparsed'], t['bad']['reading']), (10, 'cannot tell (parser)'))
        k = sum(src[r['id']]['pred'] != str(int(r['id'].split('-')[1])) for r in rows if r['label'] == 'edge'); self.assertEqual(t['edge']['misparsed'], k)
        self.assertEqual(t['edge']['reading'], 'cannot tell (parser)' if k > 1 else 'rate can be read')
    def test_tally_boundary_one_of_ten_and_two_of_ten(self):
        for k, want in ((1, 'rate can be read'), (2, 'cannot tell (parser)')):
            os.makedirs(os.path.join(self.tmp, 'sheets'), exist_ok=True); sheet = os.path.join(self.tmp, 'sheets', f'b{k}.csv')
            with open(sheet, 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['label', 'id', 'reply', 'extracted', 'misparsed'])
                for i in range(10): w.writerow(['L', i, 'r', 'e', 'x' if i < k else ''])
            o = os.path.join(self.tmp, f'o{k}'); run('sample', '--tally', sheet, '--out', o)
            self.assertEqual(json.load(open(latest(o, 'tally_*.json')))['tally'][0]['reading'], want)
if __name__ == '__main__': unittest.main(verbosity=2)
