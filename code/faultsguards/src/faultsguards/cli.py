"""python -m faultsguards COMMAND. faults, guards, show, search, prompt, preflight, review, tools, mcp."""
import sys, json, argparse
from . import __version__
from .core import faults, guards, get_fault, get_guard, search, families
from .prompts import system_prompt, preflight, review_prompt, tool_schemas
def main(argv=None):
    ap = argparse.ArgumentParser(prog='faultsguards', description='Faults and Guards, Heuremen LLC. https://heuremen.org/faults.pdf')
    ap.add_argument('--version', action='version', version=__version__); sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('faults', help='list the failure modes'); sub.add_parser('guards', help='list the procedures')
    s = sub.add_parser('show', help='print one entry in full'); s.add_argument('which', choices=['fault', 'guard']); s.add_argument('number', type=int)
    s = sub.add_parser('search', help='search by words'); s.add_argument('query', nargs='+')
    s = sub.add_parser('prompt', help='a system prompt listing the guards'); s.add_argument('--full', action='store_true')
    s = sub.add_parser('preflight', help='the guards that run before the work'); s.add_argument('--task'); s.add_argument('--full', action='store_true')
    s = sub.add_parser('review', help='a prompt reviewing a text file against the faults'); s.add_argument('file'); s.add_argument('--numbers', type=int, nargs='*')
    sub.add_parser('tools', help='function-calling schemas as JSON'); sub.add_parser('mcp', help='run the MCP server over stdio')
    a = ap.parse_args(argv)
    if a.cmd == 'faults':
        for f in families('faults'):
            print(f['part']); [print('  %d. %s' % (e['number'], e['title'])) for e in faults() if e['number'] in f['numbers']]
    elif a.cmd == 'guards':
        for f in families('guards'):
            print(f['part']); [print('  %d. %s' % (e['number'], e['title'])) for e in guards() if e['number'] in f['numbers']]
    elif a.cmd == 'show': e = (get_fault if a.which == 'fault' else get_guard)(a.number); print('%d. %s\n%s\n\n%s' % (e['number'], e['title'], e['part'], e['text']))
    elif a.cmd == 'search':
        for h in search(' '.join(a.query)): print('%s %d. %s' % (h['document'], h['number'], h['title']))
    elif a.cmd == 'prompt': print(system_prompt(a.full))
    elif a.cmd == 'preflight': print(preflight(a.task, a.full))
    elif a.cmd == 'review': print(review_prompt(open(a.file, encoding='utf-8').read(), a.numbers))
    elif a.cmd == 'tools': print(json.dumps(tool_schemas(), indent=1))
    elif a.cmd == 'mcp':
        from .mcp_server import serve; serve()
    else: ap.print_help()
    return 0
if __name__ == '__main__': sys.exit(main())
