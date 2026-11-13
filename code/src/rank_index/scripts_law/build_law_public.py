"""Build public/law/law_public.json from ABA compilation spreadsheets.
Run: python3 -I build_law_public.py   (reads downloads/, writes law_public.json)"""
import json, os, sys, hashlib
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_dump import read  # noqa: E402

BASE = os.path.expanduser("~/bones-forge/rank_index/public/law")
DL = os.path.join(BASE, "downloads")
API = "https://backend.abarequireddisclosures.org/api/"
FRONT = "https://www.abarequireddisclosures.org/"
DATE = "2026-11-10"

SCHOOLS = [  # (key, display, ABA schoolCode, name as in ABA files)
    ("stanford", "Stanford University", 21, "Stanford University"),
    ("chicago", "University of Chicago", 50, "Chicago, The University of"),
    ("yale", "Yale University", 25, "Yale University"),
    ("penn", "University of Pennsylvania (Carey)", 130, "Pennsylvania, University of"),
    ("uva", "University of Virginia", 153, "Virginia, University of"),
    ("harvard", "Harvard University", 74, "Harvard University"),
    ("duke", "Duke University", 109, "Duke University"),
    ("nyu", "New York University", 105, "New York University"),
    ("columbia", "Columbia University", 101, "Columbia University"),
    ("northwestern", "Northwestern University (Pritzker)", 49, "Northwestern University"),
    ("michigan", "University of Michigan", 76, "Michigan, University of"),
]

FILES = {
    "509_2025": ("comp509_2025_FirstYearClass.xlsx",
                 API + "AnnualQuestionnaire/GetAllCompilationData?year=2025&scetionName=First%20Year%20Class"),
    "ft_2024": ("bar_2024_First_Time_Bar_Passage.xlsx",
                API + "BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2024&sectionName=First%20Time%20Bar%20Passage"),
    "ft_2025": ("bar_2025_First_Time_Bar_Passage.xlsx",
                API + "BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2025&sectionName=First%20Time%20Bar%20Passage"),
    "ft_2026": ("bar_2026_First_Time_Bar_Passage.xlsx",
                API + "BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2026&sectionName=First%20Time%20Bar%20Passage"),
    "ub_2025": ("bar_2025_Two-Year_Ultimate_Bar_Passage.xlsx",
                API + "BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2025&sectionName=Two-Year%20Ultimate%20Bar%20Passage"),
    "ub_2026": ("bar_2026_Two-Year_Ultimate_Bar_Passage.xlsx",
                API + "BarPassageOutcomes/GenerateBarPassageCompilationReport?year=2026&sectionName=Two-Year%20Ultimate%20Bar%20Passage"),
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def table(fname):
    """First sheet as list of (rownum, {header: value}) plus header col map."""
    sheets = read(os.path.join(DL, fname))
    name, rows = sheets[0]
    hdr = rows[0][1]
    out = []
    for rn, cells in rows[1:]:
        out.append((rn, {hdr[c]: v for c, v in cells.items() if c in hdr}, cells))
    return name, hdr, out


def find(tbl, school):
    name, hdr, rows = tbl
    hits = [r for r in rows if r[1].get("School Name", r[1].get("SchoolName")) == school]
    assert len(hits) == 1, (name, school, len(hits))
    return hits[0]


def col_of(hdr, header):
    return [c for c, h in hdr.items() if h == header][0]


def fig(value, period, key, tbl, row, header, note=None):
    fname, url = FILES[key]
    d = {
        "value": value,
        "period": period,
        "url": url,
        "front_end": FRONT,
        "file": "public/law/downloads/" + fname,
        "sheet": tbl[0],
        "row": row,
        "column": f"{col_of(tbl[1], header)} ({header})",
        "date_read": DATE,
    }
    if note:
        d["note"] = note
    return d


def main():
    T = {k: table(f) for k, (f, _) in FILES.items()}
    out = {
        "desk": "RANK / law, public record only",
        "built": DATE,
        "publisher_of_figures": "American Bar Association, Section of Legal Education and Admissions to the Bar (required disclosures)",
        "files": {k: {"file": "public/law/downloads/" + f, "url": u, "sheet": T[k][0],
                      "sha256": sha(os.path.join(DL, f))} for k, (f, u) in FILES.items()},
        "definitions": {
            "509_2025": "ABA Standard 509 Information Report 2025, section 'First Year Class' (entering class of fall 2025). 'All' = full-time and part-time entrants combined; 'FT' = full-time only.",
            "acceptance_rate_aba": "AcceptanceRate column as published by the ABA in the compilation file (percent).",
            "acceptance_rate_computed": "Offers / Applications x 100, rounded half-up to one decimal, computed by us from the same row.",
            "first_time": "ABA First-Time Bar Admission (compilation sheet 'FirstTimeBarPassage'). Rows are by CALENDAR YEAR OF GRADUATION, not exam year. Report year 2025 = graduates in calendar year 2024; report year 2024 = graduates in 2023; report year 2026 = graduates in 2025. 'AvgStatePassPercent' is what the ABA's individual school report labels 'ABA weighted average bar pass rate'.",
            "ultimate": "ABA Two-Year Ultimate Bar Admission. Report year 2025 = '2022 Graduates'; report year 2026 = '2023 Graduates'.",
        },
        "schools": {},
    }
    for key, disp, code, nm in SCHOOLS:
        s = {"name": disp, "aba_name": nm, "aba_school_code": code,
             "individual_reports_saved": {
                 "509_2025": f"public/law/downloads/individual/509_2025_school{code}.pdf",
                 "bar_2024": f"public/law/downloads/individual/bar_2024_school{code}.pdf",
                 "bar_2025": f"public/law/downloads/individual/bar_2025_school{code}.pdf",
                 "bar_2026": f"public/law/downloads/individual/bar_2026_school{code}.pdf"},
             "figures": {}}
        F = s["figures"]
        t = T["509_2025"]
        rn, r, _ = find(t, nm)
        per = "Standard 509 report 2025 (entering class fall 2025)"
        for label, h in [("median_ugpa_all", "All50thPercentileUGPA"), ("median_ugpa_ft", "FT50thPercentileUGPA"),
                         ("median_ugpa_pt", "PT50thPercentileUGPA"),
                         ("median_lsat_all", "All50thPercentileLSAT"), ("median_lsat_ft", "FT50thPercentileLSAT"),
                         ("applications", "Applications"), ("offers", "Offers"),
                         ("acceptance_rate_aba_pct", "AcceptanceRate"),
                         ("entrants_total", "TotalEnrollees"), ("entrants_ft", "FTEnrollees"),
                         ("entrants_pt", "PTEnrollees")]:
            F[label] = fig(r[h], per, "509_2025", t, rn, h)
        apps, offs = Decimal(r["Applications"]), Decimal(r["Offers"])
        comp = (offs / apps * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        F["acceptance_rate_computed_pct"] = {
            "value": str(comp), "period": per, "computed": "Offers / Applications x 100, one decimal (half-up)",
            "inputs": [F["applications"]["column"], F["offers"]["column"]],
            "file": F["applications"]["file"], "row": rn, "date_read": DATE}
        if r.get("PTEnrollees") == "0":
            F["median_ugpa_pt"]["note"] = "No part-time entrants (PTEnrollees = 0); ABA prints 0.00."
        for k, yr in [("ft_2024", "2023"), ("ft_2025", "2024"), ("ft_2026", "2025")]:
            t = T[k]
            rn, r, _ = find(t, nm)
            per = f"Graduates in calendar year {yr} (ABA bar admission report {k[-4:]})"
            g = F.setdefault(f"first_time_grads_{yr}", {})
            for label, h in [("takers", "Total First Time Takers"), ("passers", "Total First Time Passers"),
                             ("school_pass_pct", "AvgSchoolPassPercent*"),
                             ("aba_weighted_avg_pass_pct", "AvgStatePassPercent**"),
                             ("difference_pct", "TotalDifferencePercent***")]:
                g[label] = fig(r[h], per, k, t, rn, h)
            hN = [h for h in t[1].values() if h.startswith("Pass % including")][0]
            g["pass_pct_incl_alt_pathways"] = fig(r[hN], per, k, t, rn, hN)
        for k, yr in [("ub_2025", "2022"), ("ub_2026", "2023")]:
            t = T[k]
            rn, r, _ = find(t, nm)
            per = f"{yr} Graduates (ABA Two-Year Ultimate Bar Admission, report {k[-4:]})"
            g = F.setdefault(f"ultimate_{yr}_graduates", {})
            for label, h in [("graduates", f"{yr} Graduates"), ("takers", f"{yr} Takers"),
                             ("passers", f"{yr} Passers"), ("pass_pct", "%Passers"),
                             ("pass_pct_incl_alt_pathways", "Pass % (including Alternative Pathways)")]:
                g[label] = fig(r[h], per, k, t, rn, h)
        out["schools"][key] = s
    with open(os.path.join(BASE, "law_public.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    # compact print
    for key, s in out["schools"].items():
        F = s["figures"]
        v = lambda k: F[k]["value"]
        print(f"{key:12} GPA all {v('median_ugpa_all')} ft {v('median_ugpa_ft')} | LSAT {v('median_lsat_all')} | apps {v('applications')} offers {v('offers')} | acc ABA {v('acceptance_rate_aba_pct')} comp {v('acceptance_rate_computed_pct')} | PT {v('entrants_pt')}")
        for yr in ("2023", "2024", "2025"):
            g = F[f"first_time_grads_{yr}"]
            print(f"   FT{yr}: {g['school_pass_pct']['value']} vs ABA-wtd {g['aba_weighted_avg_pass_pct']['value']} diff {g['difference_pct']['value']} (takers {g['takers']['value']})")
        for yr in ("2022", "2023"):
            g = F[f"ultimate_{yr}_graduates"]
            print(f"   ULT{yr}: {g['pass_pct']['value']} incl-alt {g['pass_pct_incl_alt_pathways']['value']} ({g['passers']['value']}/{g['takers']['value']})")


if __name__ == "__main__":
    main()
