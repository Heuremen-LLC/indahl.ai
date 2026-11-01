"""Talk to the MCP server the way a client does: start it, initialize, list tools, call one."""
import json, subprocess, sys
p = subprocess.Popen([sys.executable, '-m', 'faultsguards', 'mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def ask(i, method, params=None):
    p.stdin.write(json.dumps(dict(jsonrpc='2.0', id=i, method=method, params=params or {})) + '\n'); p.stdin.flush(); return json.loads(p.stdout.readline())
print(ask(1, 'initialize')['result']['serverInfo']); print([t['name'] for t in ask(2, 'tools/list')['result']['tools']])
print(ask(3, 'tools/call', dict(name='get_fault', arguments=dict(number=20)))['result']['content'][0]['text'][:500]); p.stdin.close(); p.wait()
