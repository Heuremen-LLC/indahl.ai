import re,html,sys,os,unicodedata
def clean(fn):
    t=open(fn,errors='replace').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    # keep alttext of math
    t=re.sub(r'<annotation[^>]*>.*?</annotation>','',t,flags=re.S)
    t=re.sub(r'<[^>]+>',' ',t)
    t=html.unescape(t)
    t=unicodedata.normalize('NFKC',t)
    for a,b in (('−','-'),('–','-'),('—','-'),('‘',"'"),('’',"'"),('“','"'),('”','"'),(' ',' ')):
        t=t.replace(a,b)
    return re.sub(r'\s+',' ',t)
def find(id,phrases):
    out={}
    docs={k:clean(f'{id}_{k}.html') for k in ('abs','html')}
    for p in phrases:
        pn=unicodedata.normalize('NFKC',p)
        for a,b in (('−','-'),('–','-'),('“','"'),('”','"'),('’',"'")): pn=pn.replace(a,b)
        pn=re.sub(r'\s+',' ',pn)
        sq=lambda s: re.sub(r'[^0-9a-z]','',s.lower())
        res=[]
        for k,d in docs.items():
            i=d.lower().find(pn.lower())
            if i>=0: res.append((k,'EXACT',d[max(0,i-40):i+len(pn)+40]))
            elif sq(pn) in sq(d): res.append((k,'SQUASH',''))
        out[p]=res
    return out
if __name__=='__main__':
    checks={
     '2605.08251':['reflects shot noise within each job rather than drift between jobs'],
     '2603.13949':['6%','admits a fixed linear form','linear extrapolation remains effective'],
     '2607.25998':['these methods can be extended to regimes where classical verification is unavailable'],
     '2509.17715':['relative gain of up to ~34%','relative gain of up to'],
     '2603.14485':['2D random mirror circuits of up to 49 qubits and circuit depth 80'],
     '2604.24397':['+70.7%'],
     '2609.34411':['the same reported two-qubit gate error of 2.03','measured γ of 0.68 and 0.20'],
     '2610.18124':['up to two'],
     '2609.16108':['largely settle','only as a weak competing dissipator'],
     '2606.30606':['both error detection and correction improve readout fidelity on every device and generation tested'],
     '2510.24509':['surpassing reasoning-native systems such as o3-high and DeepSeek R1 by up to +9 pp'],
     '2609.33255':['three later batches, each on a new calibration and a different set of qubits, removed the gap','removed the gap'],
     '2610.19544':['excludes a drift'],
     '2603.13536':['consistently achieves substantially lower median absolute energy errors'],
     '2506.03636':['quantifying the systematic underestimation of the effect of noise'],
    }
    for id,ph in checks.items():
        r=find(id,ph)
        for p,res in r.items():
            print(id,'|',p[:80],'|',[(k,t) for k,t,_ in res] or 'NOT FOUND')
            for k,t,c in res:
                if t=='EXACT': print('      ',k,':',c[:200]); break
