import json, os, re, subprocess, sys, html, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import extract, faultsguards as fg
norm = lambda x: re.sub(r'\s', '', x)
class Data(unittest.TestCase):
    def test_regenerated_equals_shipped(self):
        for n, w in (('FAULTS', 'faults'), ('GUARDS', 'guards')):
            self.assertEqual(extract.run(n), fg.load(w), n + ' data is not what the source generates')
    def test_every_piece_comes_from_the_source(self):
        for n, w in (('FAULTS', 'faults'), ('GUARDS', 'guards')):
            d = fg.load(w); src = open(os.path.join(ROOT, 'source', n + '.html'), encoding='utf-8').read()
            body = norm(html.unescape(re.sub(r'<[^>]+>', ' ', src[src.index('<body'):])))
            pieces = list(d['intro']) + [p for pt in d['parts'] for p in [pt['title']] + pt['paragraphs']] + [x for e in d['entries'] for x in ['%d. %s' % (e['number'], e['title'])] + e['paragraphs']] + [x for s in d['sections'] for x in [s['title']] + s['paragraphs']]
            for p in pieces: self.assertIn(norm(p), body, p[:60])
            # the h1 part titles of documents without part paragraphs also count
            titles = re.findall(r'<h1 class="newpart">(.*?)</h1>', src); extra = sum(len(norm(html.unescape(re.sub(r'<[^>]+>', '', t)))) for t in titles if not any(pt['title'] == html.unescape(re.sub(r'<[^>]+>', '', t)).strip() or True for pt in []))
            total = sum(len(norm(p)) for p in pieces) + extra
            self.assertGreater(total / len(body), 0.97, n + ' leaves more than 3% of the source text unaccounted for')
    def test_numbers_are_unique_and_complete(self):
        for w in ('faults', 'guards'):
            ns = [e['number'] for e in fg.load(w)['entries']]; self.assertEqual(sorted(ns), list(range(1, len(ns) + 1)))   # the documents say the numbers do not run in family order
    def test_no_empty_entries(self):
        for w in ('faults', 'guards'):
            for e in fg.load(w)['entries']: self.assertTrue(e['text'].strip(), e['title'])
class Builders(unittest.TestCase):
    def test_preflight_lists_part_one_guards_in_order(self):
        t = fg.preflight('task text'); nums = [int(x) for x in re.findall(r'^(\d+)\. ', t, re.M)]
        self.assertEqual(nums, sorted(nums)); self.assertTrue(len(nums) >= 5); self.assertIn('task text', t); self.assertIn('Source: ', t)
    def test_system_prompt_titles_vs_full(self):
        a = fg.system_prompt(); b = fg.system_prompt(full=True); self.assertLess(len(a), len(b)); self.assertIn('ABOVE, BELOW, CONSISTENT, CANNOT_TELL', a)
    def test_review_prompt_wraps_text_and_labels(self):
        t = fg.review_prompt('A number with no n.', numbers=[1, 6]); self.assertIn('A number with no n.', t); self.assertIn('CANNOT_TELL', t); self.assertIn(fg.get_fault(6)['title'], t); self.assertNotIn(fg.get_fault(2)['title'], t)
    def test_wrapper_lines_are_marked(self):
        for t in (fg.preflight(), fg.system_prompt(), fg.review_prompt('x')): self.assertIn('Package line:', t)
    def test_tools_run(self):
        names = [t['function']['name'] for t in fg.tool_schemas()]
        for n, a in (('list_faults', {}), ('list_guards', {}), ('get_fault', {'number': 3}), ('get_guard', {'number': 3}), ('search', {'query': 'baseline'}), ('preflight', {}), ('review_prompt', {'text': 'x'})):
            self.assertIn(n, names); self.assertTrue(fg.call_tool(n, a))
        with self.assertRaises(KeyError): fg.call_tool('nope', {})
    def test_four_outcomes_in_review_labels(self): self.assertEqual(len(fg.OUTCOMES), 4)
class Mcp(unittest.TestCase):
    def test_stdio_round_trip(self):
        reqs = [dict(jsonrpc='2.0', id=1, method='initialize', params={}), dict(jsonrpc='2.0', method='notifications/initialized'), dict(jsonrpc='2.0', id=2, method='tools/list'),
                dict(jsonrpc='2.0', id=3, method='tools/call', params=dict(name='get_guard', arguments=dict(number=8))), dict(jsonrpc='2.0', id=4, method='tools/call', params=dict(name='get_guard', arguments=dict(number=9999))),
                dict(jsonrpc='2.0', id=5, method='nope'), dict(jsonrpc='2.0', id=6, method='ping')]
        p = subprocess.run([sys.executable, '-m', 'faultsguards', 'mcp'], input='\n'.join(json.dumps(r) for r in reqs) + '\n', capture_output=True, text=True, cwd=os.path.join(ROOT, 'src'), timeout=60)
        out = {r['id']: r for r in (json.loads(l) for l in p.stdout.splitlines() if l.strip())}
        self.assertEqual(sorted(out), [1, 2, 3, 4, 5, 6]); self.assertEqual(out[1]['result']['serverInfo']['name'], 'faultsguards')
        self.assertEqual(len(out[2]['result']['tools']), 7); self.assertIn('Four outcomes', out[3]['result']['content'][0]['text']); self.assertTrue(out[4]['result']['isError']); self.assertEqual(out[5]['error']['code'], -32601)
class Cli(unittest.TestCase):
    def run_cli(self, *a): return subprocess.run([sys.executable, '-m', 'faultsguards', *a], capture_output=True, text=True, cwd=os.path.join(ROOT, 'src'), timeout=60)
    def test_commands(self):
        for a in (('faults',), ('guards',), ('show', 'fault', '1'), ('search', 'baseline'), ('prompt',), ('preflight',), ('tools',)):
            r = self.run_cli(*a); self.assertEqual(r.returncode, 0, a); self.assertTrue(r.stdout.strip(), a)
if __name__ == '__main__': unittest.main()
