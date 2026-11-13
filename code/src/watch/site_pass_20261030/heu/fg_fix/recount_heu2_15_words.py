"""HEU2-15: word counts of the six indahl.ai business pages (index, qia, iris, approach, about, contact) at 23 Oct
commits, three ways: (a) tone_scan.visible, (b) all text outside script/style, (c) (b) minus nav/header/footer."""
import subprocess, sys, re, html
sys.path.insert(0, '/Users/heuremen/bones-forge/heuremen-specbook')
import tone_scan as T
REPO = '/Users/heuremen/bones-forge/indahl-ai'
SIX = ['index.html', 'qia.html', 'iris.html', 'approach.html', 'about.html', 'contact.html']
def show(c, f):
    r = subprocess.run(['git', '-C', REPO, 'show', f'{c}:{f}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ''
def b(s):
    s = re.sub(r'(?s)<(script|style)\b.*?</\1>', ' ', s); s = re.sub(r'(?s)<title>.*?</title>', ' ', s)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s)).split()
def c_(s):
    s = re.sub(r'(?s)<(script|style|nav|footer|header)\b.*?</\1>', ' ', s); s = re.sub(r'(?s)<title>.*?</title>', ' ', s)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s)).split()
for c in sys.argv[1:]:
    A = B = C = 0
    for f in SIX:
        s = show(c, f)
        A += len(T.visible(s).split()); B += len(b(s)); C += len(c_(s))
    print(f'{c}: six pages  (a) {A}  (b) {B}  (c) {C}')
