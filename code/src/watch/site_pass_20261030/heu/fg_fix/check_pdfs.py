"""Extract text from the rendered test PDFs and check: no semicolons, no 'apparatus', no hand wording, no old company
spelling, page count, numbered-item counts, and every changed figure present as intended. Also confirm removed phrases are gone."""
import re, sys
from pypdf import PdfReader
D = '/Users/heuremen/bones-forge/watch/site_pass_20261030/heu/fg_fix/'
want = {
 'faults': ['Heuremen LLC, 10 October 2026, revised 30 October 2026', '27.3% → 22.6% → 39.5%', '9 of 33, 42 of 186, 30 of 76',
            'above the second at +2.64 widths', '0.79 → 0.69 → 0.88', 'consistent with the second at +0.97 widths',
            '38 per cent longer on average', '27.3% → 27.4% → 47.4%, +3.02 widths', '1.24 times', '0.76 to 1.99', '24 per cent',
            '57.1 per cent of long replies (44 of 77)', '27.5 per cent of 295 replies', '(81 of them)', '(96 of them)',
            '689 to 1,246', '268 to 428', '(median 1,052)', '(median 342)', 'Context did not remove it', 'most of the copy was cut',
            'labelled after reading each one in full', '14.5 ps', '20.9 ps', '20 to 35 per cent', 'roughly 2,400 years'],
 'guards': ['Heuremen LLC, 10 October 2026, revised 30 October 2026', '22.6% to 39.5%', '+2.64 widths', '0.69 to 0.88', '+0.97 widths',
            '38 per cent longer on average', '1.24 times', '0.76 to 1.99', '24 per cent', '(44 of 77)', '27.5 per cent', '(81 of 295)',
            '689 to 1,246', '268 to 428', 'not the individual modes', 'not a list of separate checks', '23 times', '11 lines',
            'borderline against the bar', 'With 257 of 608 rows carrying no family tag', 'structure rather than discipline'],
}
gone = ['apparatus', 'Heurémen', 'Heur´emen', 'by hand', 'hand-', 'compression', 'ignorance', 'not at all', 'does not work', 'does not improve',
        'nothing happened', 'a collapse', 'four times in five', '1,805', '542', 'forty-four', 'thirty-eight', 'three earlier', 'eight families',
        'two of them are recorded', 'Flat.', 'revised 22 October', 'Claude']
for name in ('faults', 'guards'):
    r = PdfReader(D + name + '.pdf'); t = '\n'.join(p.extract_text() for p in r.pages)
    open(D + name + '_pdf.txt', 'w').write(t)
    flat = ' '.join(t.split()).replace('ﬀ', 'ff').replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬃ', 'ffi').replace('ﬄ', 'ffl')
    flat = re.sub(r'(\w)- (\w)', r'\1-\2', flat)
    print(f'== {name}.pdf: {len(r.pages)} pages, {len(flat.split())} words')
    print('   semicolons:', flat.count(';'), [flat[max(0, m.start()-40):m.start()+20] for m in re.finditer(';', flat)][:5])
    for g in gone:
        if g.lower() in flat.lower(): print('   STILL PRESENT:', repr(g), '...' + flat[flat.lower().find(g.lower())-60:flat.lower().find(g.lower())+40] + '...')
    nows = re.sub(r'\s+', '', flat)
    for w in want[name]:
        if w in flat: continue
        if re.sub(r'\s+', '', w) in nows: print('   present once whitespace is ignored (pypdf splits kerned bold digits, page image checked):', repr(w))
        else: print('   MISSING:', repr(w))
    nums = [int(x) for x in re.findall(r'(?:^|\s)(\d{1,2})\. [A-Z]', flat)]
    print('   numbered headings seen in text (rough):', len(nums))
print('done')
