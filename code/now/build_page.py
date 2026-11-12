#!/usr/bin/env python3
"""build_page.py: the NOW page body (now.html), rendered from the frozen reading data/page_reading.json (written by freeze.py from
summary_now.json and the log at ship time) and data/fortune.json. Every number on the page comes from those files. build_site.py takes
the headline block and the body from now.html, so nav, division line, footer and reference code come from page()."""
import os, sys, json, html, datetime as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heuremen_kit as K   # 12 Nov 2026 (Faults and Guards 2.0): the page reads the frozen numbers of 10 Nov under the 2.0 rule, PLAN_ADDENDUM_std2.md. The frozen file itself is not changed.

H = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(H, 'data', 'page_reading.json')))
F = json.load(open(os.path.join(H, 'data', 'fortune.json')))
E = lambda s: html.escape('' if s is None else str(s), quote=True)
S = R['summary']; ENTS = {e['id']: e for e in R['entries']}
WORD = {'RIGHT': 'right', 'WRONG': 'wrong', 'CANNOT_TELL': 'cannot tell', 'HAPPENED': 'happened', 'DID_NOT_HAPPEN': 'did not happen',
        'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent'}
VERDICT = {'SAID': 'Said', 'SAID_DIFFERENTLY': 'Said differently', 'NO_PRIMARY_SOURCE_FOUND': 'No primary source found', 'CONTRADICTED': 'Contradicted by the same person',
           'NOT_SCOREABLE': 'Not scoreable'}
KINDW = {'own text': 'own text', 'contemporaneous report': 'report at the time', 'platform record': 'platform record'}


def n(x): return f'{x:,}'
def bin_read(b):
    """2.0 reading of a frozen bin from its own numbers: under 30 is TOO_WIDE_TO_RESOLVE (O3), otherwise the mean stated chance is a bound with no tolerance."""
    return (K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE) if b['n'] < 30 else K.read(b['lo'], b['hi'], bound=b['mean_stated'])
def rw(o, r): return WORD[o] + (f' ({r})' if o == 'CANNOT_TELL' and r else '')
NR = [x for x in (S.get('stale') or []) if str(x).startswith('manifold')]
def pc(x, d=1): return '' if x is None else f'{100 * x:.{d}f}'
def ld(iso):
    if not iso: return ''
    try: d = D.date.fromisoformat(str(iso)[:10]); return f'{d.day} {d.strftime("%b %Y")}'
    except Exception: return E(iso)
def link(url, text): return f'<a href="{E(url)}">{E(text)}</a>' if url else E(text)
def arch(e):
    return f' &middot; <a href="{E(e["archive_url"])}">archived</a>' if e.get('archive_url') else ''
def prob(p):
    if p is None: return ''
    if isinstance(p, dict): return f'{pc(p.get("lo"), 0)} to {pc(p.get("hi"), 0)} percent'
    return f'{pc(p, 0) if abs(p * 100 - round(p * 100)) < 1e-9 else pc(p)} percent'
def who(e):
    w = E(e['who'])
    if e.get('speaker') and e['speaker'] != e['who']: w += f'<br><span class="srckind">{E(e["speaker"])}</span>'
    return w
def src(e):
    k = KINDW.get(e.get('source_kind'), e.get('source_kind') or '')
    t = e.get('outlet') or e.get('source_title') or 'source'
    return f'{link(e["source_url"], t)}{arch(e)}<br><span class="srckind">{E(k)}</span>'
def evid(o):
    out = []
    for v in (o.get('evidence') or [])[:3]:
        a = f' (<a href="{E(v["archive_url"])}">archived</a>)' if v.get('archive_url') else ''
        out.append(f'{link(v.get("url"), v.get("what") or "record")}{a}')
    return '<br>'.join(out)
def table(head, rows):
    return ('<div class="scroll"><table class="mtx"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


B = S['binary']; ALL = B['all']; AFT = B['criterion_after']; BEF = B['criterion_before']
MR = S['probability'].get('manifold_resolved', {})
R13_HEAD = K.req13([('RIGHT', None)] * ALL['RIGHT'] + [('WRONG', None)] * ALL['WRONG'] + [(K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)] * ALL['CANNOT_TELL'], nothing_returned=NR)['line']
R13_BINS = K.req13([bin_read(b) for b in MR.get('bins', []) if b['n']], nothing_returned=NR)['line'] if MR else ''
parts = []
hl_big = f'{n(ALL["RIGHT"])} of {n(ALL["read"])}'
hl_line = (f'on-record predictions whose deadline has passed read right against the record. {n(ALL["WRONG"])} read wrong and {n(ALL["CANNOT_TELL"])} cannot be told '
           f'from the record. The criterion for {"each" if AFT["read"] == ALL["read"] else n(AFT["read"])} of these was written after the deadline, from the quote alone. {R13_HEAD}')
if MR.get('brier') is not None:
    hl_line += (f' For {n(MR["n"])} resolved Manifold AI markets read 30 days before they closed, the Brier score is {MR["brier"]:.3f}, against {MR["brier_base"]:.3f} '
                f'for stating the base rate every time.')

parts.append('<h2>Predictions against their deadline</h2>')
parts.append(
    '<p>NOW keeps a log of public predictions that name an event and a deadline. Each entry holds the exact words, a link to where they were said, '
    'an archived copy where one could be made, the date said, the deadline and a criterion we wrote in plain words. At the deadline we read the record '
    'and the entry reads right, wrong or cannot tell. A cannot tell carries one reason from a closed list, and for an entry it is always NO_INTERVAL_FORMABLE. No test the record can answer, and so no interval, can be formed. A stated probability is kept as stated and read with others from the same source, by bin. '
    'The log only grows. A correction is a new row, and the old row stays. Every row carries the hash of the row before it, and each version of the log '
    'is stamped with OpenTimestamps. The rules were committed before any entry was collected.</p>')
parts.append(
    f'<p>The log holds {n(S["entries"])} entries. {n(S["resolved"])} have a reading. {n(len(S["open"]))} wait for their deadline. '
    f'{n(len(S["pdoom"]))} are statements of a probability of catastrophe from AI, which read cannot tell by design. The entries are those we found. '
    'They are not a sample of predictions in general, and no share on this page describes predictions in general.</p>')

# ---------------------------------------------------------------- come due
done = [e for e in R['entries'] if e['kind'] == 'binary' and e['outcomes']]
done.sort(key=lambda e: (e.get('deadline') or ''))
parts.append('<h3>Come due</h3>')
parts.append(f'<p>Predictions whose deadline has passed, read against the record. Right {n(ALL["RIGHT"])}, wrong {n(ALL["WRONG"])}, cannot tell {n(ALL["CANNOT_TELL"])}. '
             + (f'For {n(BEF["read"])} the criterion was written before the deadline. ' if BEF['read'] else 'Every criterion here was written after the deadline, from the quote alone, and is labelled so. ')
             + 'A reading cites its evidence and names no cause.</p>')
rows = []
for e in done:
    o = e['outcomes'][-1]
    rows.append(f'<tr><td>{who(e)}</td><td>{ld(e["said"])}</td><td><span class="quote">&ldquo;{E(e["quote"])}&rdquo;</span><br>{src(e)}</td><td>{ld(e["deadline"])}</td>'
                f'<td>{E(e["criterion"])}{"" if e.get("criterion_before_deadline") else "<br><span class=srckind>written after the deadline</span>"}</td>'
                f'<td>{rw(o["outcome"], "NO_INTERVAL_FORMABLE")}<br><span class="srckind">{E(o.get("reason"))}</span></td><td>{evid(o)}</td></tr>')
parts.append(table(['Who', 'Said', 'Words', 'Deadline', 'Criterion', 'Reading', 'Record'], rows))

# ---------------------------------------------------------------- calibration
parts.append('<h3>Stated chances against what happened</h3>')
if MR:
    c = MR['counts'] if 'counts' in MR else {}
    parts.append(
        f'<p>Manifold is a public forecasting platform where a question carries a probability set by its traders. We read every yes-or-no market in its AI topic '
        f'with at least 50 traders that closed or resolved from 1 January 2025 to 31 October 2026 and resolved yes or no. The stated chance is the market probability '
        f'30 days before it closed. The market\'s own resolution is the record. {n(MR["n"])} markets were read. Each bin reads above when the share that resolved yes is '
        f'higher than the mean stated chance by more than its 95 percent Wilson interval and below when lower. The mean stated chance is a figure with no tolerance, so no bin reads consistent. '
        f'Any other bin reads cannot tell (STRADDLES_EDGE), and so does a bin under 30 markets (TOO_WIDE_TO_RESOLVE). Until 12 November 2026 the plan read a bin consistent when the stated chance sat inside the interval at any width. '
        f'Three bins were recorded consistent under that rule on 10 November 2026 and are marked below. Markets in one topic are not independent, so the intervals are narrower than the markets justify.</p>')
    rows = []
    for b in MR['bins']:
        if not b['n']: continue
        o2, r2 = bin_read(b); old = (f'<br><span class="srckind">recorded {WORD[b["outcome"]]} on 10 November 2026 under the plan rule</span>' if b['outcome'] != o2 and (b['outcome'], o2) != ('CANNOT_TELL', 'CANNOT_TELL') else '')
        rows.append(f'<tr><td>{E(b["label"])}</td><td class="n">{n(b["n"])}</td><td class="n">{pc(b["mean_stated"])}</td><td class="n">{n(b["happened"])}</td>'
                    f'<td class="n">{pc(b["share"])}</td><td class="n">{pc(b["lo"])} to {pc(b["hi"])}</td><td>{rw(o2, r2)}{old}</td></tr>')
    parts.append(table(['Stated chance', 'Markets', 'Mean stated, %', 'Resolved yes', 'Share yes, %', 'Wilson 95%', 'Reading'], rows))
    parts.append(f'<p class="bench-note">Bins read: {R13_BINS}</p>')
    if MR.get('brier') is not None:
        parts.append(f'<p class="bench-note">Brier score {MR["brier"]:.3f} (lower is closer). Stating the base rate of {pc(MR["base_rate"])} percent for every market scores '
                     f'{MR["brier_base"]:.3f}. Skill, one minus the ratio of the two, is {MR["skill"]:.3f}, with a 95 percent interval of {MR["skill_lo"]:.3f} to {MR["skill_hi"]:.3f} '
                     f'from 2,000 bootstrap draws over markets. Counted and not read: {E(R.get("manifold_counts_line", ""))}</p>')
MO = S['probability'].get('manifold_open', {})
if MO:
    parts.append(f'<p>A second Manifold set was logged on {ld(R["frozen_at"])}: {n(MO["logged"])} open yes-or-no AI markets with at least 50 traders that close from '
                 f'17 November 2026 to the end of 2027, each with the probability we read that day. The rider reads each one when it closes.</p>')

# ---------------------------------------------------------------- p(doom)
pd = [ENTS[i] for i in S['pdoom']]
if pd:
    parts.append('<h3>Stated chances of catastrophe from AI</h3>')
    parts.append('<p>These are logged with the exact words and their source, and every one reads cannot tell (NO_INTERVAL_FORMABLE). One outcome cannot test a probability. '
                 'Whatever happens, a single event is consistent with any stated chance above zero and below one. Only statements whose words we read in a primary source are logged.</p>')
    rows = [f'<tr><td>{who(e)}</td><td>{ld(e["said"])}</td><td><span class="quote">&ldquo;{E(e["quote"])}&rdquo;</span><br>{src(e)}</td><td>{prob(e.get("probability"))}</td>'
            f'<td>{ld(e["deadline"]) if e.get("deadline") else "no period stated"}</td><td>cannot tell (NO_INTERVAL_FORMABLE), by design</td></tr>' for e in pd]
    parts.append(table(['Who', 'Said', 'Words', 'Stated chance', 'Period ends', 'Reading'], rows))

# ---------------------------------------------------------------- open
op = [ENTS[x['id']] for x in S['open'] if ENTS[x['id']]['set'] != 'manifold_open']
parts.append('<h3>Waiting for the deadline</h3>')
parts.append(f'<p>Entries whose deadline is ahead, soonest first. The criterion was written on {ld(R["frozen_at"])}, before the deadline. The rider checks the deadlines every day '
             'and writes a reading row, with its evidence, when an entry comes due.</p>')
rows = [f'<tr><td>{who(e)}</td><td>{ld(e["said"])}</td><td><span class="quote">&ldquo;{E(e["quote"])}&rdquo;</span><br>{src(e)}</td><td>{ld(e["deadline"])}</td>'
        f'<td>{E(e["criterion"])}</td><td>{prob(e.get("probability"))}</td></tr>' for e in op]
parts.append(table(['Who', 'Said', 'Words', 'Deadline', 'Criterion', 'Stated chance'], rows))

# ---------------------------------------------------------------- FORTUNE
parts.append('<h2 id="fortune">FORTUNE</h2>')
tally = {}
for f in F: tally[f['verdict']] = tally.get(f['verdict'], 0) + 1
parts.append('<p>Famous predictions from history, read in two steps. First, were the words said? We give the earliest primary source we found, or say that none was found. '
             'Second, for words that were said and name something checkable, how they landed. A line with no deadline is not scored. '
             + ' '.join(f'{VERDICT[k]}: {n(v)}.' for k, v in sorted(tally.items(), key=lambda kv: -kv[1])) + '</p>')
rows = []
for f in F:
    p = f.get('primary') or {}; ef = f.get('earliest_found') or {}; la = f.get('landed') or {}
    srcs = link(p.get('url'), p.get('title') or 'primary source') + (f' ({E(p.get("date"))})' if p.get('date') else '') if p.get('url') else ''
    if f['verdict'] == 'NO_PRIMARY_SOURCE_FOUND':
        srcs = 'No primary source found.' + (f' Earliest found: {link(ef.get("url"), ef.get("title"))} ({E(ef.get("date"))})' if ef else '')
    if p.get('archive_url'): srcs += f' &middot; <a href="{E(p["archive_url"])}">archived</a>'
    q = f'<br><span class="quote">&ldquo;{E(p["quote"])}&rdquo;</span>' if p.get('quote') else ''
    if f.get('primary_read') is False: q += '<br><span class="srckind">primary not read by us, words as a named secondary source transcribes them</span>'
    landed = WORD.get(la.get('outcome'), '') if la.get('outcome') else ('no deadline stated' if f['verdict'] in ('SAID', 'SAID_DIFFERENTLY') else '')
    if la.get('record'): landed += f'<br><span class="srckind">{E(la["record"])}</span>'
    rows.append(f'<tr><td>{E(f["who"])}<br><span class="srckind">{E(f.get("claimed_date"))}</span></td><td>{('<span class="quote">&ldquo;' + E(f["popular_version"]) + '&rdquo;</span>') if f.get("popular_version") else 'no popular version'}</td>'
                f'<td>{VERDICT[f["verdict"]]}<br><span class="srckind">{E(f.get("summary"))}</span></td><td>{srcs}{q}</td><td>{landed}</td></tr>')
parts.append(table(['Who', 'As repeated', 'Was it said', 'Earliest source', 'How it landed'], rows))

# ---------------------------------------------------------------- the log
st = R.get('stamps') or []
parts.append('<h3>The log</h3>')
parts.append(f'<p>The page shows the log as frozen on {ld(R["frozen_at"])}: {n(R["log_rows"])} rows, last row hash {E(R["log_last_line_sha256"][:16])}, whole-file sha256 '
             f'{E(R["log_sha256"][:16])}. The stamp index and the newest reading are public: <a href="/predictions/stamps.json">stamps</a> and '
             f'<a href="/predictions/live.json">/predictions/live.json</a>, which carries every entry with its words, source, deadline, criterion and reading. The feed is read again every day and can be newer than this page. '
             'An OpenTimestamps proof shows the log existed in that form no later than the Bitcoin block that confirms it.</p>')

body = '\n'.join(parts)
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>NOW | Predictions Against the Record | Heuremen LLC</title></head><body>'
        f'<main class="wrap"><section id="hl-slot" class="hl-slot hl"><div class="hl-big">{E(hl_big)}</div><p class="hl-line">{E(hl_line)}</p></section>'
        '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>\n' + body + '\n<p class="meta">Wayfinder and Bones. Heuremen LLC.</p></main></body></html>')
open(os.path.join(H, 'now.html'), 'w').write(page)
print('now.html', len(page), 'bytes;', hl_big, '|', hl_line[:160])
