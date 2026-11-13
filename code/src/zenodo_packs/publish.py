import json, os, re, html, hashlib, sys, urllib.request
B="/Users/heuremen/bones-forge"
T=open("/Users/heuremen/Documents/Heuremen LLC/ACCOUNTS/zenodo-token").read().strip()
API="https://zenodo.org/api"
def call(method,url,data=None,raw=None,ctype="application/json"):
    h={"Authorization":"Bearer "+T}
    body=None
    if data is not None: body=json.dumps(data).encode(); h["Content-Type"]="application/json"
    if raw is not None: body=raw; h["Content-Type"]="application/octet-stream"
    req=urllib.request.Request(url,data=body,headers=h,method=method)
    try:
        r=urllib.request.urlopen(req); b=r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {url.split('?')[0]} -> {e.code} {e.read()[:600]!r}")
    return json.loads(b) if b else {}
def md(s):
    s=html.escape(s)
    s=re.sub(r"`([^`]+)`",r"<code>\1</code>",s)
    s=re.sub(r"(https?://[^\s<>)]+[^\s<>).,:])",r'<a href="\1">\1</a>',s)
    return s
def readme_paras(path,n):
    L=open(path).read().split("\n\n")
    out=[]
    for p in L[1:]:
        p=" ".join(p.split())
        if not p or p.startswith("#") or p.startswith("Heuremen LLC ·") or p.startswith("- ") or p.startswith("1."): 
            if out: break
            continue
        out.append(p)
        if len(out)>=n: break
    return out
P=[
 dict(key="QIA Research Package",d="qia_package/dist/qia-research-package",t="software",page="https://indahl.ai/qia/package",dl="https://indahl.ai/qia/qia-research-package.zip",n=1,
  kw=["quantum computing","calibration","IBM Quantum","T1","T2","reproducibility"],
  lic="The package is free to download, read and cite with attribution to Heuremen LLC and a link to the page it came from. All rights are reserved. Text and data mining, and use to train, fine-tune or build AI models, are not permitted. Full terms are in LICENSE.txt in the zip.",
  tested="The before check was compared with the separate audit code behind our public IBM mirror on the latest calibration record of seven IBM processors, and the flags agreed qubit for qubit. It was recounted with separate code on 362 saved ibm_kingston records and every count agreed. The after check and the pull path were run on a real ibm_kingston run on 2 November 2026. The part that lists records stamped during a run was exercised on test files only, because no record was stamped in that window. The YO reader was not yet tested inside this package."),
 dict(key="Darkwave Correction Kit",d="darkwave_kit/dist/darkwave-correction-kit",t="software",page="https://indahl.ai/darkwave/kit",dl="https://indahl.ai/darkwave/darkwave-correction-kit.zip",n=1,
  kw=["quantum computing","mid-circuit measurement","virtual Z","IBM Quantum","spectator qubits"],
  rel=[{"identifier":"10.5281/zenodo.23843468","relation":"isSupplementTo","scheme":"doi"}],
  lic="The kit is free to download, read and cite with attribution to Heuremen LLC and a link to the page it came from. All rights are reserved. Text and data mining, and use to train, fine-tune or build AI models, are not permitted. Full terms are in LICENSE.txt in the zip.",
  tested="The kit has a self-test on a simulator that plants a known turn on five qubits and checks that it is measured and corrected within 1 degree. It was also tested on ibm_kingston on 2 November 2026 under plans committed before each job. Version 1.0 failed the test because its correction gave back only 0.264 of the turn. Version 1.1, this one, gave back 1.012 [0.993, 1.027] of the turn over 113 targets, on one chip and one calibration snapshot, on the second attempt after the fix. A tail of targets keeps part of the turn, and 12 percent kept more than 1 degree per readout. Both runs, with their plans and raw data, are in the hardware-check folder of the zip."),
 dict(key="IRIS Research Package",d="iris_package/dist/iris-research-package",t="software",page="https://indahl.ai/iris/package",dl="https://indahl.ai/iris/iris-research-package.zip",n=1,
  kw=["language models","evaluation","benchmarks","LLM-as-judge","reproducibility","parser check"],
  lic="The code in the package may be run, copied and changed by anyone for any purpose with attribution to Heuremen LLC and https://indahl.ai/iris, and is provided without warranty. The text and data in the package are free to download, read and cite with attribution. For that text and data all rights are reserved, and text and data mining and use to train, fine-tune or build AI models are not permitted. Full terms are in LICENSE.txt in the zip.",
  tested="42 unit tests run on a synthetic dataset with planted answers and passed on Python 3.9, 3.12 and 3.14 on macOS. On our own two-machine FaultsBench round of 29 and 30 October 2026 the repeat command gave 1, 4, 11 and 10 flips, equal to the counts from separate code of ours, which shows two implementations agree and is not a check by anyone else. A reading sheet on 30 real replies had 29 extractions correct. Not tested are other harness output formats, files of more than 100,000 items on real data, Windows and Linux, and the model run of parser-check."),
 dict(key="ATLAS Data Pack",d="atlas_package/dist/atlas-data-pack",t="dataset",page="https://indahl.ai/atlas/data-pack",dl="https://indahl.ai/atlas/atlas-data-pack.zip",n=1,
  kw=["data centers","power plants","electricity prices","carbon intensity","OpenStreetMap","EIA","GeoJSON"],
  lic="This pack mixes data from several sources and each part keeps the licence of its source. OpenStreetMap-derived files are under the Open Database License (ODbL) 1.0, © OpenStreetMap contributors. Epoch AI-derived files are under CC BY 4.0. US government data from the EIA and EPA is in the public domain. Heuremen LLC adds no restriction to any of them. The files are listed by licence in LICENSE.txt in the zip. The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.",
  tested="On 2 November 2026 the files were opened with pandas 3.1 and with geopandas 1.2, and every count was compared with the live ATLAS pages and matched, including 77 Epoch AI data centers, 1,649 OpenStreetMap data centers, 14,280 operating plants and 1,608 planned plants. All GeoJSON files read as points in EPSG:4326. The file verify.py compares every CSV and GeoJSON cell with the JSON."),
 dict(key="OY Data Pack",d="oy_package/dist/oy-data-pack",t="dataset",page="https://indahl.ai/oy/data-pack",dl="https://indahl.ai/oy/oy-data-pack.zip",n=1,
  kw=["higher education","AI policy","generative AI","learning outcomes","colleges and universities","course catalogs"],
  lic="This pack mixes text from several sources and each part keeps the terms of its source. Sentences, course titles and quotations belong to the schools and authors of the pages named in each row. Directory data from IPEDS is US government data. Heuremen LLC's own labels, counts, notes, README and code may be used with attribution to Heuremen LLC and https://indahl.ai/oy, and its own text is reserved against text and data mining and AI training. Full terms by file are in LICENSE.txt in the zip. The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.",
  tested="On 1 November 2026 every CSV was opened with pandas 3.1.0 and the live OY page and all 389 school pages were fetched and compared. Every count matched, including 148 listed colleges and universities, 8 chatbot citations, 14 findings, 61 school sentences and 291 course titles. The file verify.py compares every CSV cell with the JSON. Excel and LibreOffice were not tested, and outside links were compared with the page but not opened again."),
 dict(key="MODEL Data Pack",d="model_package/dist/model-data-pack",t="dataset",page="https://indahl.ai/hermes/model/data-pack",dl="https://indahl.ai/hermes/model-data-pack.zip",n=1,
  kw=["MLPerf","MLCommons","AI hardware","vendor statements","inference","benchmarks"],
  lic="This pack mixes data from several sources and each part keeps the terms of its source. MLPerf results published by MLCommons Association are under the Apache License 2.0, and the text is in APACHE-2.0.txt in the zip. Vendor sentences are quoted from the sources named in each row. Heuremen LLC's own compilation, labels and text may be used with attribution to Heuremen LLC and https://indahl.ai/hermes/model. Full terms by file are in LICENSE.txt in the zip. The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.",
  tested="On 1 November 2026 every CSV was opened with pandas 3.1.0 and the live MODEL page and its 74 source pages were fetched and compared. Every count matched, including 531 statements with 8 ABOVE, 51 BELOW, 368 CONSISTENT and 104 CANNOT_TELL, and 1,727 results by accelerator in 569 groups. One note on a Nebius storage row differed from the page, and the published file was corrected on 2 November 2026 and the pack carries the corrected file. Excel and LibreOffice were not tested, and the MLCommons files were not downloaded again."),
 dict(key="QIA List Pack",d="list_packs/dist/qia-list-pack",t="dataset",page="https://indahl.ai/qia/list",dl="https://indahl.ai/qia/qia-list-pack.zip",n=1,
  kw=["quantum computing","IBM Quantum","bibliography","reference list","reproducibility"],
  lic="The pack is free to download, read and cite with attribution to Heuremen LLC and a link to the page it came from. All rights are reserved. Text and data mining, and use to train, fine-tune or build AI models, are not permitted. The studies listed keep their own terms. Full terms are in LICENSE.txt in the zip.",
  tested="On 2 November 2026 the pack was opened with pandas 3.1, rispy and bibtexparser 2.1. The study counts equal the live list.json in every file, the RIS titles equal the list.csv titles, and the BibTeX file parsed with no failures and every key is unique. The BibTeX file was not compiled with LaTeX."),
 dict(key="IRIS List Pack",d="list_packs/dist/iris-list-pack",t="dataset",page="https://indahl.ai/iris/list",dl="https://indahl.ai/iris/iris-list-pack.zip",n=1,
  kw=["language models","evaluation","bibliography","reference list","reproducibility"],
  lic="The pack is free to download, read and cite with attribution to Heuremen LLC and a link to the page it came from. All rights are reserved. Text and data mining, and use to train, fine-tune or build AI models, are not permitted. The studies listed keep their own terms. Full terms are in LICENSE.txt in the zip.",
  tested="On 2 November 2026 the pack was opened with pandas 3.1, rispy and bibtexparser 2.1. The study counts equal the live list.json in every file, the RIS titles equal the list.csv titles, and the BibTeX file parsed with no failures and every key is unique. The BibTeX file was not compiled with LaTeX."),
]
out_path=B+"/zenodo_packs/dois.json"
res=json.load(open(out_path)) if os.path.exists(out_path) else {}
only=sys.argv[1:]
for p in P:
    k=p["key"]
    if k in res or (only and k not in only): continue
    try:
        d=f"{B}/{p['d']}"
        zipf=d+".zip"; shaf=zipf+".sha256"
        cff=open(d+"/CITATION.cff").read()
        ver=re.search(r"^version:\s*\"?([^\"\n]+)",cff,re.M).group(1).strip()
        dt=re.search(r"^date-released:\s*\"?([0-9-]+)",cff,re.M).group(1)
        title=re.match(r"#\s*(.+)",open(d+"/README.md").read()).group(1).strip()
        paras=readme_paras(d+"/README.md",p["n"])
        desc="".join(f"<p>{md(x)}</p>" for x in paras)
        desc+=f'<p>Page: <a href="{p["page"]}">{p["page"]}</a></p>'
        desc+=f"<p><b>How it was tested.</b> {md(p['tested'])}</p><p><b>Terms.</b> {md(p['lic'])}</p>"
        txt=re.sub("<[^>]+>"," ",desc)
        assert ";" not in html.unescape(txt), k
        assert "by hand" not in txt
        zsha=hashlib.sha256(open(zipf,"rb").read()).hexdigest()
        assert zsha==open(shaf).read().split()[0], "sha mismatch "+k
        zmd5=hashlib.md5(open(zipf,"rb").read()).hexdigest()
        rel=[{"identifier":p["dl"],"relation":"isIdenticalTo","scheme":"url"},{"identifier":p["page"],"relation":"isDocumentedBy","scheme":"url"}]+p.get("rel",[])
        meta={"upload_type":p["t"],"title":title,"creators":[{"name":"Heuremen LLC"}],"description":desc,"access_right":"open","license":"other-at","version":ver,"publication_date":dt,"keywords":p["kw"],"related_identifiers":rel}
        dep=call("POST",API+"/deposit/depositions",{})
        did=dep["id"]; bucket=dep["links"]["bucket"]
        for f in (zipf,shaf):
            call("PUT",bucket+"/"+os.path.basename(f),raw=open(f,"rb").read())
        call("PUT",f"{API}/deposit/depositions/{did}",{"metadata":meta})
        pub=call("POST",f"{API}/deposit/depositions/{did}/actions/publish")
        files=call("GET",f"{API}/deposit/depositions/{did}/files")
        zf=[f for f in files if f["filename"]==os.path.basename(zipf)][0]
        ok=zf["checksum"]==zmd5
        res[k]={"doi":pub["doi"],"url":pub["links"]["record_html"],"zip_sha256":zsha,"zenodo_md5":zf["checksum"],"md5_match":ok,"version":ver,"deposition_id":did}
        json.dump(res,open(out_path,"w"),indent=1)
        print("OK",k,pub["doi"],ok)
    except Exception as e:
        print("FAIL",k,repr(e)[:700])
