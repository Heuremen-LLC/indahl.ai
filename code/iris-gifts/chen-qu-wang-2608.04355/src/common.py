"""Shared loaders for the recount. Our own code. Reads the authors' files as data only (JSON/JSONL text, Fernet-sealed JSON).
Nothing under ../theirs is executed or imported."""
import json, os, glob, hashlib, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "theirs", "repo_35851b8"))
DATA = os.path.join(REPO, "data")
PLACEHOLDERS = ("<answer>", "<letter>", "<number>")   # paper 4.9: "None or a literally echoed placeholder token"


def load_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def is_bad(ans):
    """Paper 4.9: bad = None or echoed placeholder."""
    if ans is None:
        return True
    return isinstance(ans, str) and any(p in ans for p in PLACEHOLDERS)


def category(r):
    a, f = is_bad(r.get("a0_answer")), is_bad(r.get("yf_answer"))
    if a:
        return "dead" if f else "recover"
    return "loss" if f else "bothok"


def decompose(rows):
    """Paper 3.3 / Appendix B, exact identity over all n rows. Returns a dict."""
    n = len(rows)
    cats = [category(r) for r in rows]
    y0 = np.array([r["y0"] for r in rows]); yf = np.array([r["yf"] for r in rows])
    c = np.array(cats)
    bo = c == "bothok"
    n_bo = int(bo.sum())
    helpful = int((bo & (y0 == 0) & (yf == 1)).sum())
    harmful = int((bo & (y0 == 1) & (yf == 0)).sum())
    chg = np.array([str(r["a0_answer"]).strip() != str(r["yf_answer"]).strip() if cc == "bothok" else False
                    for r, cc in zip(rows, cats)])
    d_content = (helpful - harmful) / n
    d_rec = int(((c == "recover") & (yf == 1)).sum()) / n
    d_loss = -int(((c == "loss") & (y0 == 1)).sum()) / n
    d_total = float(yf.mean() - y0.mean())
    assert abs(d_total - (d_content + d_rec + d_loss)) < 1e-12
    acc0 = (bo & (y0 == 1)).sum() / max(n_bo, 1)
    accf = (bo & (yf == 1)).sum() / max(n_bo, 1)
    orc = (bo & ((y0 == 1) | (yf == 1))).sum() / max(n_bo, 1)
    return dict(n=n, n_bothok=n_bo, a0_bad=float(((c == "recover") | (c == "dead")).sum() / n),
                yf_bad=float(((c == "loss") | (c == "dead")).sum() / n),
                d_total=d_total, d_content=d_content, d_recover=d_rec, d_loss=d_loss,
                d_format=d_rec + d_loss,
                change_rate=float((bo & chg).sum() / max(n_bo, 1)),
                harm_rate=float(harmful / max(n_bo, 1)),
                headroom=float(orc - max(acc0, accf)), acc0_bo=float(acc0), accf_bo=float(accf),
                n_recover=int((c == "recover").sum()), n_loss=int((c == "loss").sum()), n_dead=int((c == "dead").sum()),
                helpful=helpful, harmful=harmful)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_sealed(name, holdout_dir=None):
    """Decrypt a sealed holdout half with the released key (Fernet). Our own call to the cryptography package."""
    from cryptography.fernet import Fernet
    d = holdout_dir or os.path.join(DATA, "holdout")
    key = open(os.path.join(d, f"{name}.holdout.key"), "rb").read()
    tok = open(os.path.join(d, f"{name}.holdout.sealed"), "rb").read()
    return json.loads(Fernet(key).decrypt(tok).decode())


# ---- comparison helpers (printed strings vs our floats) ----
def fmt_s3(x):
    """signed 3-decimal string, zero shown as 0.000 (the paper prints 0.000 and +0.000 both)."""
    s = f"{x:+.3f}"
    return "0.000" if s in ("+0.000", "-0.000") else s


def fmt_u3(x):
    s = f"{x:.3f}"
    return "0.000" if s == "-0.000" else s


def printed_norm(s):
    s = s.strip().replace("−", "-")
    if s in ("+0.000", "-0.000", "0.000"):
        return "0.000"
    return s


_BOUNDARY = [False]


def _num(printed):
    return float(printed_norm(printed).replace("%", ""))


def same_s3(printed, x):
    """Match if the printed 3-decimal value lies within the rounding interval of x (inclusive). Flags exact half-point cases."""
    d = abs(_num(printed) - x)
    ok = d <= 0.0005 + 1e-9
    if ok and d >= 0.0005 - 1e-9:
        _BOUNDARY[0] = True
    return ok


def same_u3(printed, x):
    return same_s3(printed, x)


class Report:
    """Collects (id, status, printed, ours, note) lines; status in REBUILT / NOT REBUILT / NO FILE."""
    def __init__(self):
        self.rows = []

    def add(self, rid, ok, printed, ours, note=""):
        if _BOUNDARY[0]:
            note = (note + " " if note else "") + "[half-point: printed digit is the half-up rounding of an exact .5]"
            _BOUNDARY[0] = False
        self.rows.append((rid, "REBUILT" if ok else "NOT REBUILT", str(printed), str(ours), note))
        return ok

    def nofile(self, rid, printed, note=""):
        self.rows.append((rid, "NO FILE", str(printed), "", note))

    def dump(self, path=None, title=""):
        out = []
        if title:
            out.append(f"# {title}")
        for r in self.rows:
            out.append("\t".join(r))
        n_ok = sum(1 for r in self.rows if r[1] == "REBUILT")
        n_no = sum(1 for r in self.rows if r[1] == "NOT REBUILT")
        n_nf = sum(1 for r in self.rows if r[1] == "NO FILE")
        out.append(f"# SUMMARY REBUILT={n_ok} NOT_REBUILT={n_no} NO_FILE={n_nf} total={len(self.rows)}")
        txt = "\n".join(out)
        if path:
            open(path, "w").write(txt + "\n")
        return txt


CELL_FILES = {}
def cell_path(label):
    """Map the paper's cell label ('0.8B x ARC', '4B x GSM8K (v2)', 'Gemma 12B x MMLU') to the stage2 file."""
    import re
    lab = label.strip()
    m = re.match(r"^(Gemma 12B|0\.8B|2B|4B|9B) x (.+?)(?: \((v2|v3|exception)\))?$", lab)
    scale, task, var = m.group(1), m.group(2), m.group(3)
    tmap = {"ARC": "arc", "GSM8K": "gsm8k", "MMLU": "mmlu", "MATH": "math", "CommonsenseQA": "commonsenseqa",
            "TruthfulQA-MC1": "truthfulqa_mc1", "TriviaQA": "triviaqa", "HumanEval": "humaneval", "MBPP": "mbpp"}
    t = tmap[task]
    if scale == "Gemma 12B":
        fn = f"stage2_gemma4_12b_{t}.jsonl"
    else:
        fn = f"stage2_qwen35_{scale.lower()}_{t}" + (f"_r{var}" if var in ("v2", "v3") else "") + ".jsonl"
    return os.path.join(DATA, fn)
