"""Prompt and checklist builders. The text of each fault and guard is exactly as published. The wrapper sentences here are the package's own and are marked as such."""
from .core import load, faults, guards, get_fault, get_guard
OUTCOMES = ('COMMITS', 'AVOIDS', 'CANNOT_TELL', 'NOT_APPLICABLE')
CREDIT = 'Faults and Guards, Heuremen LLC, https://heuremen.org/faults.pdf and https://heuremen.org/guards.pdf. Use at answer time is permitted. Use as training data is not.'
def _fmt(e, full):
    return '%d. %s\n%s' % (e['number'], e['title'], e['text']) if full else '%d. %s' % (e['number'], e['title'])
def checklist(part=None, full=False):
    """Guards as an ordered list. part: None for all, or a roman numeral prefix such as 'I' (procedures that run before the work), 'II', 'III', 'IV'. full=True includes each guard's whole text."""
    es = guards()
    if part: es = [e for e in es if (e['part'] or '').split(' ')[0] == part]
    return '\n\n'.join(_fmt(e, full) for e in es)
def preflight(task=None, full=False):
    """The guards that run before the work, to place ahead of a task. The package line is ours, the numbered guards are as published."""
    head = 'Package line: before you compute or state any number for the task below, work through these procedures in order.\n\n'
    body = checklist('I', full)
    tail = ('\n\nTask:\n' + task) if task else ''
    return head + body + tail + '\n\nSource: ' + CREDIT
def system_prompt(full=False, parts=('I', 'II', 'III', 'IV')):
    """A system prompt that lists the guards. Titles only by default, which is short. full=True includes every guard's text (long)."""
    head = 'Package line: the procedures below come from Faults and Guards. They apply before a number is stated, not after. Four outcomes only for any result: ABOVE, BELOW, CONSISTENT, CANNOT_TELL.\n\n'
    body = '\n\n'.join('Part %s\n%s' % (p, checklist(p, full)) for p in parts)
    return head + body + '\n\nSource: ' + CREDIT
def review_prompt(text, numbers=None, full=True):
    """A prompt asking a model to review text against faults. numbers: fault numbers to use, default all. The four labels are the package's own."""
    fs = [get_fault(n) for n in numbers] if numbers else faults()
    head = ('Package line: review the text under REVIEW against each fault below. For each fault answer with one label, %s, and quote the sentence that decides it. '
            'COMMITS means the text commits the fault. AVOIDS means it addresses it. CANNOT_TELL means the text does not show either. NOT_APPLICABLE means the fault does not apply to this kind of text. Do not fold CANNOT_TELL into COMMITS.\n\n') % ', '.join(OUTCOMES)
    return head + 'FAULTS\n' + '\n\n'.join(_fmt(e, full) for e in fs) + '\n\nREVIEW\n' + text + '\n\nSource: ' + CREDIT
def tool_schemas():
    """Function-calling schemas (JSON Schema parameters) for list, get, search, preflight and review, usable with any tool-calling API."""
    S = lambda name, desc, props, req=(): dict(type='function', function=dict(name=name, description=desc, parameters=dict(type='object', properties=props, required=list(req))))
    return [S('list_faults', 'List the failure modes in Faults: number, title, family.', {}), S('list_guards', 'List the procedures in Guards: number, title, part.', {}),
            S('get_fault', 'The full published text of one fault.', {'number': {'type': 'integer'}}, ['number']), S('get_guard', 'The full published text of one guard.', {'number': {'type': 'integer'}}, ['number']),
            S('search', 'Search faults and guards by words.', {'query': {'type': 'string'}}, ['query']), S('preflight', 'The guards that run before the work, optionally ahead of a task.', {'task': {'type': 'string'}, 'full': {'type': 'boolean'}}),
            S('review_prompt', 'A prompt that reviews a text against the faults.', {'text': {'type': 'string'}, 'numbers': {'type': 'array', 'items': {'type': 'integer'}}}, ['text'])]
def call_tool(name, args):
    """Runs one tool by name and returns a JSON-serialisable result."""
    a = args or {}
    if name == 'list_faults': return [dict(number=e['number'], title=e['title'], family=e['part']) for e in faults()]
    if name == 'list_guards': return [dict(number=e['number'], title=e['title'], part=e['part']) for e in guards()]
    if name == 'get_fault': e = get_fault(a['number']); return dict(number=e['number'], title=e['title'], family=e['part'], text=e['text'], source=CREDIT)
    if name == 'get_guard': e = get_guard(a['number']); return dict(number=e['number'], title=e['title'], part=e['part'], text=e['text'], source=CREDIT)
    if name == 'search':
        from .core import search; return search(a['query'])
    if name == 'preflight': return preflight(a.get('task'), bool(a.get('full')))
    if name == 'review_prompt': return review_prompt(a['text'], a.get('numbers'))
    raise KeyError(name)
