"""Shared prompt, parse, grounding and call code for STAN. Python 3.9 compatible."""
import json,re,os,time,urllib.request,fcntl
S='/Users/heuremen/bones-forge/stan'
STD=json.load(open('/Users/heuremen/bones-forge/faultsguards/standard_v1/standard_v1.json'))
CODES=['F1','F2','F3','F4','F5','F6','F7']
CT_REASONS={'F1':['METHOD_UNSTATED','NOT_RELEASED','UNREADABLE'],'F2':['NOT_RELEASED','UNREADABLE'],'F3':['NOT_RELEASED','UNREADABLE'],
 'F4':['UNREADABLE'],'F5':['NOT_RELEASED','UNREADABLE','METHOD_UNSTATED'],'F6':['NOT_RELEASED','UNREADABLE'],
 'F7':['NOT_RELEASED','UNREADABLE','STRADDLES_EDGE','TOO_WIDE_TO_RESOLVE','NO_INTERVAL_FORMABLE']}
ALL_REASONS=['NOT_RELEASED','UNREADABLE','METHOD_UNSTATED','STRADDLES_EDGE','TOO_WIDE_TO_RESOLVE','NO_INTERVAL_FORMABLE']
def code_block(code):
    c=[x for x in STD['claim_codes'] if x['code']==code][0]
    ct='; '.join('%s: %s'%(r['reason'],r['when']) for r in c['cannot_tell_when'])
    return ('%s %s. %s\nApplies to: %s\nTest: %s\nPRESENT when: %s\nABSENT when: %s\nCANNOT_TELL reasons: %s\nNOT_APPLICABLE when: %s'
        %(code,c['name'],c['definition'],c['applies_to'],c['test'],c['present_when'],c['absent_when'],ct or 'none',c['not_applicable_when']))
RULES=("You are drafting a checklist for a person to confirm. You are a sorter, not a judge. You see only the title and abstract below, not the full paper or its files. "
 "For each code give a status: PRESENT, ABSENT, CANNOT_TELL (with exactly one reason) or NOT_APPLICABLE. "
 "For PRESENT and ABSENT give a quote copied word for word from the text below, at most 200 characters, that is your evidence. "
 "If you cannot quote evidence from the text, use CANNOT_TELL. CANNOT_TELL and NOT_APPLICABLE need no quote.")
def teacher_prompt(text):
    defs='\n\n'.join(code_block(c) for c in CODES)
    fmt='{"F1": {"status": "PRESENT|ABSENT|CANNOT_TELL|NOT_APPLICABLE", "reason": "reason or empty", "quote": "verbatim quote or empty"}, "F2": {...}, ... "F7": {...}}'
    return RULES+'\n\nCODES\n\n'+defs+'\n\nTEXT\n'+text+'\n\nAnswer with one JSON object only, in this form: '+fmt
def code_prompt(code,text):
    fmt='{"status": "PRESENT|ABSENT|CANNOT_TELL|NOT_APPLICABLE", "reason": "reason or empty", "quote": "verbatim quote or empty"}'
    return RULES+'\n\nCODE\n\n'+code_block(code)+'\n\nTEXT\n'+text+'\n\nAnswer with one JSON object only, in this form: '+fmt
def ws(t): return ' '.join((t or '').split())
def parse_obj(txt):
    txt=re.sub(r'<think>.*?</think>','',txt or '',flags=re.S)
    m=re.search(r'\{.*\}',txt,re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None
def norm_label(code,o,text):
    """Return dict(status,reason,quote,flag). flag in ok, ungrounded, parse_failed."""
    if not isinstance(o,dict) or str(o.get('status','')).upper() not in ('PRESENT','ABSENT','CANNOT_TELL','NOT_APPLICABLE'):
        return {'status':'PARSE_FAILED','reason':'','quote':'','flag':'parse_failed'}
    st=str(o['status']).upper(); rs=str(o.get('reason') or '').upper().strip(); q=str(o.get('quote') or '')
    if st=='CANNOT_TELL':
        if rs not in ALL_REASONS: return {'status':'PARSE_FAILED','reason':'','quote':'','flag':'parse_failed'}
        return {'status':st,'reason':rs,'quote':'','flag':'ok'}
    if st=='NOT_APPLICABLE': return {'status':st,'reason':'','quote':'','flag':'ok'}
    if ws(q) and ws(q) in ws(text): return {'status':st,'reason':'','quote':q,'flag':'ok'}
    return {'status':'CANNOT_TELL','reason':'METHOD_UNSTATED','quote':'','flag':'ungrounded','was':st}
def key(l): return (l['status'],l['reason'])
def ollama(host,model,prompt,n=900,t=600,seed=0):
    body={'model':model,'messages':[{'role':'user','content':prompt}],'stream':False,'think':False,'format':'json',
          'options':{'temperature':0,'seed':seed,'num_predict':n,'num_ctx':8192},'keep_alive':'30m'}
    r=json.load(urllib.request.urlopen(urllib.request.Request(host+'/api/chat',json.dumps(body).encode(),{'Content-Type':'application/json'}),timeout=t))
    return r['message']['content']
GPU_LOCK='/Users/heuremen/bones-forge/sage_library/sage_v/.train.lock'
def gpu_lock():
    f=open(GPU_LOCK,'w'); fcntl.flock(f,fcntl.LOCK_EX); return f
def jl_read(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def all_pool():
    import glob
    p=json.load(open(S+'/data/pool.json'))[:100]
    for f in sorted(glob.glob(S+'/data/slices/slice_*.json')): p+=json.load(open(f))
    return p
def unload_others(host,model):
    try:
        for m in json.load(urllib.request.urlopen(host+'/api/ps',timeout=10))['models']:
            if m['name']!=model and not m['name'].startswith('bge'):
                urllib.request.urlopen(urllib.request.Request(host+'/api/generate',json.dumps({'model':m['name'],'keep_alive':0}).encode()),timeout=60)
    except Exception: pass
