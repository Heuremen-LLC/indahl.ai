"""plan_gate.py -- a pre-registered run may not be committed to heuremen.org until its design has been RUN, not described.
Wayfinder, 22 Oct 2026: "your rule for running designs and not describing them is you talking about your rule and not saving it anywhere".
Usage: python3 plan_gate.py <experiment folder> ...   (exit 1 and name every failure; exit 0 only if every folder passes)
Called by heuremen.org/.git/hooks/pre-commit on every experiments/ folder whose PLAN*.md.text is staged.
A folder passes only if:
  1. PLAN*.md.text, PLAN*.sha256.text and CODE*.sha256.text are all present;
  2. the plan has a filled REQUIRED FIELD line starting 'KNOWN-GOOD:' naming the real-hardware case where the answer is already
     known and what this analysis must read on it (or 'KNOWN-GOOD: none possible -- <reason>'); an empty field fails;
  3. at least one synthetic output (synth*.text or *synth*results*.text) is present -- the analysis was RUN on planted data;
  4. every file listed in CODE*.sha256.text that sits in the folder matches its hash."""
import glob, hashlib, os, re, sys
def check(d):
    bad = []
    plans = glob.glob(os.path.join(d, 'PLAN*.md.text'))
    if not plans: bad.append('no PLAN*.md.text')
    if not glob.glob(os.path.join(d, 'PLAN*.sha256.text')): bad.append('no PLAN*.sha256.text')
    codes = glob.glob(os.path.join(d, 'CODE*.sha256.text'))
    if not codes: bad.append('no CODE*.sha256.text')
    for p in plans:
        kg = [l for l in open(p, errors='replace') if l.strip().startswith('KNOWN-GOOD:')]
        if not kg: bad.append('%s: no KNOWN-GOOD: line (required field)' % os.path.basename(p))
        elif any(len(l.strip()) < len('KNOWN-GOOD:') + 20 for l in kg): bad.append('%s: KNOWN-GOOD: field is empty' % os.path.basename(p))
    if not [f for f in glob.glob(os.path.join(d, '*.text')) if re.search(r'synth', os.path.basename(f), re.I)]:
        bad.append('no synthetic output (synth*.text): the analysis was never run on planted data')
    for c in codes:
        for line in open(c):
            parts = line.split()
            if len(parts) != 2: continue
            h, name = parts
            if '/' in name: continue  # a file outside this folder (e.g. ../run1/x.py) is not checked against a same-named file here
            f = os.path.join(d, name)
            if os.path.exists(f) and hashlib.sha256(open(f, 'rb').read()).hexdigest() != h: bad.append('%s does not match %s' % (os.path.basename(f), os.path.basename(c)))
    return bad
if __name__ == '__main__':
    fail = False
    for d in sys.argv[1:]:
        b = check(d)
        print(('PASS ' if not b else 'FAIL ') + d)
        for x in b: print('   - ' + x)
        fail |= bool(b)
    sys.exit(1 if fail else 0)
