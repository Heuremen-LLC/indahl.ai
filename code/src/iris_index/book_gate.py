"""book_gate.py: refuse any IRIS book row without a recorded referee verdict (Ralph queue item 1, 25 Oct).
Run before every booking commit: `python3 book_gate.py` exits 1 and names the rows if any lack 'referee'."""
import json, sys, os
B=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'IRIS_BOOK_register.json')))
bad=[r['id'] for r in B if not str(r.get('referee','')).strip()]
if bad: print('REFUSED: rows without a referee verdict:',bad); sys.exit(1)
print('book gate OK:',len(B),'rows, all refereed')
