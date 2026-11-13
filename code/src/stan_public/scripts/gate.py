"""Owner order 12 Nov: stamp and go. Before any teacher call: PLAN.md is committed unchanged (git), PLAN.sha256 matches it, and PLAN.sha256.ots exists (submitted).
Bitcoin confirmation is never waited for. ots upgrade runs later in the background."""
import hashlib,os,subprocess,sys
S='/Users/heuremen/bones-forge/stan'
def die(m): print('GATE REFUSED: '+m,flush=True); sys.exit(9)
def check():
    h=hashlib.sha256(open(S+'/PLAN.md','rb').read()).hexdigest()
    rec=open(S+'/PLAN.sha256').read().split()[0] if os.path.exists(S+'/PLAN.sha256') else ''
    if rec!=h: die('PLAN.md does not match PLAN.sha256')
    # 13 Nov 2026 (Wayfinder): no OpenTimestamps, no Bitcoin; the commit is the record
    st=subprocess.run(['git','-C',S,'status','--porcelain','PLAN.md','PLAN.sha256'],capture_output=True,text=True).stdout.strip()
    if st: die('plan files not committed: '+st)
    print('gate ok: plan committed and matches its sha256',flush=True)
