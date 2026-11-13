import json,os,re,html,subprocess
B=os.path.expanduser("~/bones-forge/rank_index/public/nj_claims")
def norm(s):
    s=html.unescape(s).replace('’',"'").replace('–','-').replace('—','-').replace('\xa0',' ')
    s=re.sub(r'(\d)\s+(st|nd|rd|th)\b',r'\1\2',s)
    return re.sub(r'\s+',' ',s).lower()
cache={}
def folder_text(folder):
    if folder in cache: return cache[folder]
    txt=""
    for f in os.listdir(folder) if os.path.isdir(folder) else []:
        fp=os.path.join(folder,f)
        if f.endswith(".pdf"):
            txt+=subprocess.run(["python3","-I","-c","import sys,pypdf;print(' '.join(p.extract_text() or '' for p in pypdf.PdfReader(sys.argv[1]).pages))",fp],capture_output=True,text=True).stdout
        else:
            txt+=open(fp,errors="ignore").read()
    cache[folder]=norm(re.sub(r'<[^>]+>',' ',txt)); return cache[folder]
for kind in ("claims","schedules"):
    d=json.load(open(f"{B}/{kind}.json"))
    for it in d:
        t=folder_text(os.path.dirname(os.path.join(B,it.get("saved_copy") or "")))
        q=norm(re.sub(r'\([^)]*\)','',it["quote"]))
        parts=[x.strip(" .;…'\"•") for x in re.split(r'\.\.\.|…|;| / |•',q) if len(x.strip())>6]
        miss=[x for x in parts if x not in t]
        if miss:
            q2=norm(it["quote"]); parts=[x.strip(" .;…'\"•") for x in re.split(r'\.\.\.|…|;| / |•',q2) if len(x.strip())>6]
            miss=[x for x in parts if x not in t]
        it["quote_check"]="verbatim" if not miss else ("partial: "+str(len(parts)-len(miss))+"/"+str(len(parts))+" segments found")
        if miss: print(kind,"|",it["school"],"|",it["quote_check"],"|",miss[:2])
    json.dump(d,open(f"{B}/{kind}.json","w"),indent=1,ensure_ascii=False)
