"""A small MCP server over stdio (newline-delimited JSON-RPC), standard library only. Methods: initialize, tools/list, tools/call, ping. Read-only, no network, no model calls."""
import sys, json
from . import __version__
from .prompts import tool_schemas, call_tool
PROTO = '2024-11-05'
def _tools():
    return [dict(name=t['function']['name'], description=t['function']['description'], inputSchema=t['function']['parameters']) for t in tool_schemas()]
def handle(msg):
    """returns a response dict, or None for notifications"""
    m = msg.get('method'); i = msg.get('id')
    if i is None: return None
    if m == 'initialize': return dict(jsonrpc='2.0', id=i, result=dict(protocolVersion=PROTO, capabilities=dict(tools={}), serverInfo=dict(name='faultsguards', version=__version__)))
    if m == 'ping': return dict(jsonrpc='2.0', id=i, result={})
    if m == 'tools/list': return dict(jsonrpc='2.0', id=i, result=dict(tools=_tools()))
    if m == 'tools/call':
        p = msg.get('params') or {}
        try: r = call_tool(p.get('name'), p.get('arguments'))
        except KeyError: return dict(jsonrpc='2.0', id=i, result=dict(isError=True, content=[dict(type='text', text='unknown tool or entry: %s' % p.get('name'))]))
        except Exception as e: return dict(jsonrpc='2.0', id=i, result=dict(isError=True, content=[dict(type='text', text='error: %s' % type(e).__name__)]))
        return dict(jsonrpc='2.0', id=i, result=dict(content=[dict(type='text', text=r if isinstance(r, str) else json.dumps(r, ensure_ascii=False, indent=1))]))
    return dict(jsonrpc='2.0', id=i, error=dict(code=-32601, message='method not found: %s' % m))
def serve(inp=None, out=None):
    inp = inp or sys.stdin; out = out or sys.stdout
    for line in inp:
        line = line.strip()
        if not line: continue
        try: msg = json.loads(line)
        except Exception: out.write(json.dumps(dict(jsonrpc='2.0', id=None, error=dict(code=-32700, message='parse error'))) + '\n'); out.flush(); continue
        r = handle(msg)
        if r is not None: out.write(json.dumps(r, ensure_ascii=False) + '\n'); out.flush()
