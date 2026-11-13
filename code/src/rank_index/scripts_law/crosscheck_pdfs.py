"""Cross-check law_public.json against the ABA individual school PDFs (text extraction).
Run: python3 -I crosscheck_pdfs.py"""
import json, os, re
import pypdf

BASE = os.path.expanduser("~/bones-forge/rank_index/public/law")
J = json.load(open(os.path.join(BASE, "law_public.json")))


def text(p):
    r = pypdf.PdfReader(p)
    return "\n".join(pg.extract_text() for pg in r.pages)


def after(t, label, n=1):
    i = t.find(label)
    if i < 0:
        return None
    toks = t[i + len(label):].split()
    return toks[:n]


def pct(v):
    return v.rstrip("%")


bad = 0
for key, s in J["schools"].items():
    F = s["figures"]
    code = s["aba_school_code"]
    t = text(os.path.join(BASE, "downloads/individual", f"509_2025_school{code}.pdf"))
    t1 = t.replace("\n", " ")
    chk = {
        "applications": after(t1, "Completed Applications")[0],
        "offers": after(t1, "Offers of Admission")[0],
        "acceptance_rate_aba_pct": pct(after(t1, "Acceptance Rate (Percent)")[0]),
    }
    u = t1.find("UGPA All")
    chk["median_ugpa_all"] = after(t1[u:], "50th Percentile")[0]
    l = t1.find("LSAT", u + 10)
    chk["median_lsat_all"] = after(t1[l:], "50th Percentile")[0]
    for k, v in chk.items():
        pub = F[k]["value"]
        same = (float(v) == float(pub))
        if not same:
            bad += 1
        print(f"{key:12} 509 {k:24} xlsx={pub:8} pdf={v:8} {'OK' if same else 'MISMATCH'}")
    for rep, yrs in [("2025", ["2024", "2023"]), ("2026", ["2025"])]:
        tb = text(os.path.join(BASE, "downloads/individual", f"bar_{rep}_school{code}.pdf"))
        toks = tb.split()
        for yr in yrs:
            # first-time table row: year then 13 values; find first occurrence followed by numbers
            for i, tok in enumerate(toks):
                if tok == yr and i + 13 < len(toks) and toks[i + 9].endswith("%"):
                    row = toks[i:i + 14]
                    break
            g = F[f"first_time_grads_{yr}"]
            pdf_vals = (row[7], row[8], pct(row[9]), pct(row[10]), pct(row[11]))
            xl = (g["takers"]["value"], g["passers"]["value"], pct(g["school_pass_pct"]["value"]),
                  pct(g["aba_weighted_avg_pass_pct"]["value"]), pct(g["difference_pct"]["value"]))
            same = all(float(a) == float(b) for a, b in zip(pdf_vals, xl))
            bad += (not same)
            print(f"{key:12} bar report {rep} grads {yr}: xlsx={xl} pdf={pdf_vals} {'OK' if same else 'MISMATCH'}")
        # ultimate
        uy = str(int(rep) - 3)
        ui = tb.find("Two-Year Ultimate")
        ut = tb[ui:].split()
        for i, tok in enumerate(ut):
            if tok == uy and ut[i + 6].endswith("%"):
                urow = ut[i:i + 9]
                break
        g = F[f"ultimate_{uy}_graduates"]
        pv = (urow[4], urow[5], pct(urow[6]))
        xv = (g["takers"]["value"], g["passers"]["value"], pct(g["pass_pct"]["value"]))
        same = all(float(a) == float(b) for a, b in zip(pv, xv))
        bad += (not same)
        print(f"{key:12} ultimate {uy} grads (report {rep}): xlsx={xv} pdf={pv} {'OK' if same else 'MISMATCH'}")
print("MISMATCHES:", bad)
