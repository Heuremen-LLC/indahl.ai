"""Minimal stdlib xlsx reader. Usage: python3 -I xlsx_dump.py FILE [grep-regex]
Prints sheet name, then row number (Excel 1-based) and cell values (col letter=value)."""
import sys, re, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for sh in wb.find("m:sheets", NS):
        tgt = rmap[sh.get(RNS)].lstrip("/")
        if not tgt.startswith("xl/"):
            tgt = "xl/" + tgt
        root = ET.fromstring(z.read(tgt))
        rows = []
        for row in root.iter("{%s}row" % NS["m"]):
            cells = {}
            for c in row.findall("m:c", NS):
                ref = c.get("r")
                col = re.match(r"[A-Z]+", ref).group(0)
                t = c.get("t")
                v = c.find("m:v", NS)
                if t == "s" and v is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
                else:
                    val = v.text if v is not None else None
                if val not in (None, ""):
                    cells[col] = val
            rows.append((int(row.get("r")), cells))
        out.append((sh.get("name"), rows))
    return out


if __name__ == "__main__":
    pat = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    for name, rows in read(sys.argv[1]):
        print("== sheet:", name)
        for i, (rn, cells) in enumerate(rows):
            line = " | ".join(f"{k}={v}" for k, v in cells.items())
            if pat is None or i < 3 or pat.search(line):
                print(rn, line)
