#!/usr/bin/env python3
"""build_open.py -- WHAT IS OPEN: open PHYSICS questions only, published by explicit consent.
(Bones, 8 Oct 2026. Rewritten 10 Oct 2026.)

WHAT THE FIRST VERSION DID WRONG, and it is a failure mode worth naming. It harvested every row in
the internal record carrying an `open`, `gap` or `next` key and published the text verbatim. That
bought one real thing -- the page could never go stale, because writing the row WAS updating the page
-- and it paid for it with the curation gate. A generator cannot tell an open physics question from a
build chore, so the public page acquired, among other things: a note that a timestamping tool was not
installed on one machine, a note that our own rendering tooling could not reach phone width, two
copies of a complaint about the generator's own key convention, internal data-logistics about where
raw files were sitting, and an editorial to-do. Twenty-four items, of which roughly half were
housekeeping.

  THE RULE THAT FOLLOWS: AN AUTOMATED PUBLISHER WITH NO CURATION GATE INHERITS THE SCOPE OF WHATEVER
  RECORD IT READS. The default must be publish-NOTHING, with an explicit per-item consent, never
  publish-everything with an exclusion list -- because the exclusion list is only ever as complete as
  the last person who remembered to extend it.

SO THE DEFAULT IS INVERTED. The page is built from `open_public.jsonl`, which is curated by hand and
contains open PHYSICS questions only: places where we cannot presently tell, stated so a stranger can
read them, each with what would settle it. Nothing reaches the page by accident.

THE STALENESS PROTECTION IS NOT ABANDONED, it is moved. This script still reads the internal record
and reports, TO THE TERMINAL AND NEVER TO THE PAGE, how many internal open rows are not represented
publicly. The gap stays visible to us without being published, which is the whole thing the first
version got backwards.

  python3 build_open.py            print the public list, and the internal count that is not on it
  python3 build_open.py --html     write ligera/WHAT_IS_OPEN.html
"""
import datetime
import html
import json
import os
import sys

HERE = os.path.expanduser('~/bones-forge/watch/')
PUB = os.path.join(HERE, 'open_public.jsonl')
ROWS = os.path.join(HERE, 'rows.jsonl')
OUT = os.path.expanduser('~/bones-forge/ligera/WHAT_IS_OPEN.html')
# the internal keys the OLD version published. Still counted, never printed.
INTERNAL_KEYS = ('open', 'still_open', 'unbought', 'gap', 'unrun', 'lands_it', 'what_lands_it', 'next')


def public():
    out = []
    for line in open(PUB, encoding='utf-8'):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return sorted(out, key=lambda r: r['n'])


def internal_count():
    """how many internal open rows exist. The COUNT travels; the text does not."""
    n = 0
    try:
        for line in open(ROWS, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if any(r.get(k) for k in INTERNAL_KEYS):
                n += 1
    except FileNotFoundError:
        return None
    return n


def main():
    P = public()
    ic = internal_count()
    if '--html' not in sys.argv:
        for r in P:
            print('%2d  %s' % (r['n'], r['q']))
            print('      %s' % r['detail'])
            print('      SETTLE: %s\n' % r['settle'])
        print('%d public questions.' % len(P))
        if ic is not None:
            print('INTERNAL, NOT PUBLISHED: %d rows in the working record carry an open key. The count '
                  'is reported here and the text is not published anywhere. Promote one by hand into '
                  'open_public.jsonl if and only if it is an open PHYSICS question a stranger can read.'
                  % ic)
        return 0
    rows = ''
    for r in P:
        kills = ('<p class="kill">A wrong answer here ENDS a reading of ours. It is marked '
                 'because a list of open questions that could not embarrass its authors is not one.</p>'
                 if r.get('kills') else '')
        rows += ('<div class="q%s"><p class="qh"><span class="qn">%d</span>%s</p>'
                 '<p class="qd">%s</p>%s<p class="qs"><b>What would settle it.</b> %s</p></div>\n'
                 % (' kills' if r.get('kills') else '', r['n'], html.escape(r['q']),
                    html.escape(r['detail']), kills, html.escape(r['settle'])))
    doc = """<!doctype html><html><head><meta charset="utf-8"><title>What Is Open</title><style>
@page { size: Letter; margin: 0.7in 0.75in; }
body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; color: #18202B; background: #FFF; font-size: 10.5pt; line-height: 1.45; }
h1 { font-size: 21pt; color: #0E4A4D; border-bottom: 2px solid #0F7173; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 13.5pt; color: #0F7173; margin-top: 20px; }
p { margin: 4px 0; }
.lead { font-size: 11pt; }
.hold { background: #F4F8F6; border-left: 3px solid #0F7173; padding: 6px 10px; margin: 10px 0; }
.q { margin: 14px 0 0; padding: 9px 11px; border: 1px solid #E4E9E6; border-left: 3px solid #0F7173; break-inside: avoid; }
.qh { font-size: 11.5pt; font-weight: 600; color: #0E4A4D; margin: 0 0 4px; }
.qn { display: inline-block; min-width: 1.6em; color: #B5530C; }
.qd { margin: 0 0 5px; }
.qs { margin: 0; color: #39434F; }
.q.kills { border-left-color: #B5530C; background: #FBF5F2; }
.kill { margin: 0 0 5px; color: #B5530C; font-weight: 600; }
hr { border: 0; border-top: 1px solid #D8DEDA; margin: 16px 0; }
.foot { color: #6B7480; font-size: 8.5pt; margin-top: 20px; }
</style></head><body>
<h1>What Is Open</h1>
<p>Open questions in our own physics that we have not been able to answer. Wayfinder and Bones, Heur&eacute;men &mdash; __DATE__.</p>
<p class="lead"><b>Every one of these is a place where we cannot presently tell.</b> Not a list of things we believe are wrong with our conclusions &mdash; a list of questions our own work raises and does not settle, each with what would settle it. This page exists so that nothing on it has to be discovered by somebody else.</p>
<div class="hold"><b>Two of them would end a reading of ours outright if they came out the wrong way.</b> Those two are marked in the margin rather than buried. A list of open questions that could not embarrass its authors is not a list of open questions.</div>
__ROWS__
<hr>
<h2>What is deliberately not here</h2>
<p>Earlier versions of this page were generated automatically from our internal working record, which meant it published whatever that record happened to contain &mdash; including tooling notes, missing-software notes, data-handling chores and editorial to-do items. <b>An automated publisher with no curation gate inherits the scope of whatever record it reads.</b> The default is now inverted: nothing reaches this page without an explicit, per-item decision that it is an open physics question a stranger can read.</p>
<p>Method failures and the procedures built against them are not here either. They have their own two documents, <i>Las Fallas</i> and <i>Las Guardas</i>, because a method catalogue scattered across the documents it came from cannot be scored.</p>
<p class="foot">What Is Open &mdash; __N__ open physics questions. Wayfinder and Bones, Heur&eacute;men, __DATE__. Each entry states what would settle it. Made with inorganic intelligence assistance.</p>
<p class="foot">Heuremen LLC<br>&ldquo;We found it.&rdquo;</p></body></html>"""
    doc = (doc.replace('__ROWS__', rows)
              .replace('__DATE__', datetime.date.today().strftime('%-d %B %Y'))
              .replace('__N__', str(len(P))))
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('%d public questions -> %s' % (len(P), OUT))
    if ic is not None:
        print('internal rows with an open key, counted and NOT published: %d' % ic)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
