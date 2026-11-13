#!/usr/bin/env python3
"""outcomes.py -- THE GATE THAT MAKES AN OUTCOME COLLAPSE IMPOSSIBLE TO EXPRESS.
(Bones, 10 Oct 2026.)

WHY THIS EXISTS, and it is not a flattering reason. On 10 October I published two documents to the
site. One of them lists, as failure mode 20, "four outcomes collapsed into two". The other lists, as
procedure 8, "four outcomes, never two, and the terminating reason on every call". TWO HOURS LATER,
in the next experiment, I collapsed FIVE outcomes into one column called `silent`: a model using the
wrong rung, a model addressing nobody, a model never doing the task, an empty reply, and BOTH OF MY
READERS BEING BLIND TO THE CONSTRUCTION. Four facts about the subject and one about me, in one bin.

Wayfinder: "same lesson, different day. que pasa? you LITERALLY just wrote a pdf about this."

THE ANSWER IS IN THE DOCUMENTS THEMSELVES, which is the uncomfortable part. Las Fallas 41: a guard
will not teach you -- 96 pushbacks over three days, every one acknowledged and corrected, and the
rate stayed flat at 0.79/0.69/0.88 per thousand words. Las Guardas 12: instruction depends on recall
at the moment of writing, and the moment of writing is when context is thinnest. A CATALOGUE IS
REFERENCE MATERIAL. It occupies no position in the pipeline, so it never fires. Knowing mode 20 did
not prevent mode 20; it cannot, and expecting it to is how a guard gets removed for failing a job it
never had.

SO THIS IS A POSITION RATHER THAN A DOCUMENT. Every scoring script declares its outcomes with a
predicate each, and this module refuses the declaration if:

  IT IS NOT EXHAUSTIVE   some row matches nothing. The unmatched rows are NAMED, because an
                         unmatched row is the thing that would otherwise have been swept into a
                         residual bin.
  IT IS NOT DISJOINT     some row matches two. Named likewise.
  A BIN IS A RESIDUAL    a name like none / other / silent / misc / unknown / rest / fail is
                         REFUSED OUTRIGHT, because a bin with no positive definition is exactly where
                         five outcomes go to hide. That check, and only that check, is what would
                         have caught my own error -- my bins were exhaustive and disjoint and one of
                         them simply meant five things.

An outcome about the APPARATUS is declared separately from an outcome about the SUBJECT, because
reading my own configuration as the subject's behaviour is a distinct failure (mode 21) and it has
already happened once today: an output limit consumed a reply's budget, the field came back empty
with no error, and the empty cells were reported as a system declining to answer.

    from outcomes import Outcomes
    O = Outcomes(subject=[('complied', f1), ('wrong_rung', f2), ('no_address', f3)],
                 apparatus=[('off_task', f4), ('empty', f5), ('reader_blind', f6)])
    O.tally(rows)          # raises on a collapse, naming the rows
    print(O.table())
"""
import re

REFUSED = ('none', 'other', 'silent', 'misc', 'unknown', 'rest', 'fail', 'failed', 'bad',
           'na', 'n/a', 'else', 'remainder', 'leftover', 'etc', 'nothing', 'empty_or_other')


class OutcomeCollapse(Exception):
    """raised instead of returning a tidy table, because a tidy table is the failure."""


class Outcomes:
    def __init__(self, subject, apparatus=()):
        self.subject = list(subject)
        self.apparatus = list(apparatus)
        names = [n for n, _ in self.subject] + [n for n, _ in self.apparatus]
        if len(set(names)) != len(names):
            raise OutcomeCollapse('duplicate outcome name in %s' % names)
        for n in names:
            key = re.sub(r'[^a-z/]', '', n.lower())
            if key in REFUSED:
                raise OutcomeCollapse(
                    'REFUSED BIN NAME %r. A residual bin is where several outcomes hide; give it a '
                    'positive definition and its own name. This is the check that catches the '
                    'collapse, because a residual bin is still exhaustive and still disjoint.' % n)
        if not self.subject:
            raise OutcomeCollapse('no subject outcomes declared')
        self.counts = None

    def classify(self, row):
        hits = [n for n, f in self.subject + self.apparatus if f(row)]
        return hits

    def tally(self, rows, label=''):
        unmatched, doubled = [], []
        counts = {n: 0 for n, _ in self.subject + self.apparatus}
        for i, r in enumerate(rows):
            h = self.classify(r)
            if not h:
                unmatched.append(i)
            elif len(h) > 1:
                doubled.append((i, h))
            else:
                counts[h[0]] += 1
        if unmatched:
            raise OutcomeCollapse(
                'NOT EXHAUSTIVE%s: %d of %d rows match no declared outcome (indices %s%s). Each one '
                'is a fact you have not named. Name it; do not add a residual bin.'
                % (' in ' + label if label else '', len(unmatched), len(rows),
                   unmatched[:12], ' ...' if len(unmatched) > 12 else ''))
        if doubled:
            raise OutcomeCollapse(
                'NOT DISJOINT%s: %d rows match more than one outcome, e.g. %s. Two outcomes that can '
                'both be true are one outcome and a condition.'
                % (' in ' + label if label else '', len(doubled), doubled[:4]))
        self.counts = counts
        return counts

    def table(self):
        if self.counts is None:
            raise OutcomeCollapse('tally() first')
        n = sum(self.counts.values())
        out = ['  %-18s%7s%9s   %s' % ('outcome', 'count', 'share', 'about')]
        for grp, who in ((self.subject, 'the subject'), (self.apparatus, 'THE APPARATUS')):
            for name, _ in grp:
                c = self.counts[name]
                out.append('  %-18s%7d%8.1f%%   %s' % (name, c, 100 * c / n if n else 0, who))
        out.append('  %-18s%7d%8.1f%%' % ('total', n, 100.0))
        ap = sum(self.counts[n_] for n_, _ in self.apparatus)
        if ap:
            out.append('  %d of %d rows (%.0f%%) are about THE APPARATUS and say nothing about the '
                       'subject.' % (ap, n, 100 * ap / n))
        return '\n'.join(out)


if __name__ == '__main__':
    print(__doc__.split('\n\n')[0])
    print('\n  self-test: the exact collapse committed on 10 Oct must be refused.\n')
    try:
        Outcomes(subject=[('tu', lambda r: False), ('vos', lambda r: False),
                          ('usted', lambda r: False), ('silent', lambda r: True)])
        print('  FAILED: the residual bin was accepted')
    except OutcomeCollapse as e:
        print('  REFUSED as designed:\n    %s\n' % str(e)[:200])
    O = Outcomes(subject=[('tu', lambda r: r == 'tu'), ('vos', lambda r: r == 'vos')],
                 apparatus=[('empty', lambda r: r == '')])
    try:
        O.tally(['tu', 'vos', '', 'usted'])
        print('  FAILED: a row matching nothing was accepted')
    except OutcomeCollapse as e:
        print('  NOT EXHAUSTIVE caught as designed:\n    %s\n' % str(e)[:190])
    O.tally(['tu', 'vos', '', 'tu'])
    print(O.table())
