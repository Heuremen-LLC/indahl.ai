import os, subprocess, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ENV = dict(os.environ, PYTHONPATH=os.path.join(ROOT, 'src'))
class Examples(unittest.TestCase):
    def test_each_example_runs_offline(self):
        for f in sorted(os.listdir(os.path.join(ROOT, 'examples'))):
            if not f.endswith('.py'): continue
            r = subprocess.run([sys.executable, os.path.join(ROOT, 'examples', f)], capture_output=True, text=True, env=ENV, timeout=60, cwd=ROOT)
            self.assertEqual(r.returncode, 0, f + ' ' + r.stderr[-300:]); self.assertTrue(r.stdout.strip(), f)
    def test_mcp_config_is_valid_json(self):
        import json; d = json.load(open(os.path.join(ROOT, 'examples', '04_mcp_client_config.json'))); self.assertIn('faultsguards', d['mcpServers'])
if __name__ == '__main__': unittest.main()
