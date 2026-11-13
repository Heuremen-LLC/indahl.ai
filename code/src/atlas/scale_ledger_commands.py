"""scale_ledger_commands.py (30 Oct 2026): writes the ledger.py commands for every public number the ATLAS cost-to-scale section prints, from electricity/scale_rows_text.txt.
Output: electricity/scale_ledger_commands.txt. It only writes text, it never runs ledger.py. Run after build_atlasmap.py: python3 -I scale_ledger_commands.py"""
import os,json
H=os.path.dirname(os.path.abspath(__file__))+'/'
L=[l.rstrip('\n') for l in open(H+'electricity/scale_rows_text.txt',encoding='utf-8')]
CK='--checks atlas/electricity/CHECKS.md'; LED='python3 ~/bones-forge/ledger/ledger.py'; SRC='atlas/electricity/scale_rows_text.txt'
def q(t): return t.replace('\\','\\\\').replace('"','\\"').replace('$','\\$')
out=[]
def add(i,claim,value,src,grep,snips):
    out.append(f'{LED} add {i} --claim "{q(claim)}" --value "{q(value)}" --outcome RECORD --source {src} --grep "{q(grep)}" '+' '.join(f'--on atlas "{q(s)}"' for s in snips)+f' {CK}')
n=0; m=0; k=0; u=0
T=next(l for l in L if l.startswith('TOTAL ')); C=next(l for l in L if l.startswith('COUNTS ')); X=next(l for l in L if l.startswith('EXAMPLE ')); TC=next(l for l in L if l.startswith('TOTALCOMMERCIAL '))
for l in L:
    if l.startswith('SITE '):
        n+=1; r=l[5:]; add(f'atlas.scale.row.site.{n:03d}','Row of the cost-to-scale table on the ATLAS page: one Epoch AI site, stated power times 8,760 hours at the state industrial price in 2024 from EIA-861',r,SRC,l,[r])
    elif l.startswith('UNPLACED '):
        u+=1; r=l[9:]; add(f'atlas.scale.row.unplaced.{u:03d}','Row of the table of sites with a stated power that are not in the cost-to-scale total, from Epoch AI',r,SRC,l,[r])
    elif l.startswith('STATE '):
        k+=1; r=l[6:]; add(f'atlas.scale.row.state.{k:03d}','Row of the state prices table on the ATLAS page: EIA-861 2024 industrial and commercial prices, sites and stated power in the state, annual cost at the industrial price',r,SRC,l,[r])
tot=T.split()  # TOTAL counted mw twh musd
counted,mw,twh,musd=tot[1],tot[2],tot[3],tot[4]
add('atlas.scale.total.row','Total row of the cost-to-scale table: sites, stated power, annual cost at the state industrial price',f'{counted} sites, {mw} MW, {musd} million dollars',SRC,T,[f'Total {counted} sites {mw} {musd}'])
add('atlas.scale.total.lead','Cost to scale, lead sentence: one year at full stated power at the state industrial price, in dollars, megawatts and terawatthours',f'{musd} million dollars, {mw} MW, {twh} TWh',SRC,T,[f'That is {musd} million dollars for {mw} megawatts and {twh} terawatthours, across {counted} sites'])
bu=f"{float(musd.replace(',',''))/1000:.1f}"
add('atlas.scale.total.billion','Cost to scale, headline figure in billions of dollars',f'{bu} billion dollars',SRC,T,[f'comes to {bu} billion dollars'])
cm=TC.split()[1]
add('atlas.scale.commercial','Cost to scale at each state commercial price instead of the industrial price, millions of dollars',f'{cm} million dollars',SRC,TC,[f'the same arithmetic gives {cm} million dollars'])
c=C.split()  # COUNTS us power placed counted notcounted mwnot notplaced nopower
add('atlas.scale.count.sites','Epoch AI sites in the United States and how many state a power',f'{c[1]} sites, {c[2]} state a power, {c[8]} do not',SRC,C,[f'lists {c[1]} data centers in the United States. {c[2]} state a power and {c[8]} do not'])
add('atlas.scale.count.counted','Sites with a stated power that sit in a state we could place, which the total covers',f'{c[4]} of {c[2]}',SRC,C,[f'{c[4]} of the {c[2]} that state a power are in a state we could place, and the total covers those {c[4]}'])
add('atlas.scale.count.unplaced','Sites with a stated power not in the total, their stated power, and sites not placed in a state at all',f'{c[5]} sites, {c[6]} MW, {c[7]} sites not placed',SRC,C,[f'The other {c[5]}, Google Mesa, Google Kansas City East and Google Storey County, state {c[6]} megawatts between them',f'{c[7]} of the {c[1]} sites could not be placed in a state at all'])
xt=X.split(); ename=' '.join(xt[1:-4]); emw,emwh,erate,ecost=xt[-4:]
add('atlas.scale.example','Worked example in the cost-to-scale text: stated power times 8,760 hours, then the state industrial price',f'{ename} {emw} MW {emwh} MWh {erate} cents {ecost} million dollars',SRC,X,[f'{ename}: {emw} MW × 8,760 hours = {emwh} MWh, and {emwh} MWh × {erate} cents per kilowatthour = {ecost} million dollars'])
# legends: the five bins of each shading layer, from the same json the state maps use
EJ=json.load(open(H+'electricity/electricity.json')); CJ=json.load(open(H+'electricity/carbon.json'))
for key,lg,src,idn in (('industrial',EJ['legend']['industrial'],'atlas/electricity/electricity.json','industrial'),('commercial',EJ['legend']['commercial'],'atlas/electricity/electricity.json','commercial'),('carbon',CJ['legend'],'atlas/electricity/carbon.json','carbon')):
    add(f'atlas.map.legend.{idn}',f'Bin edges of the {key} shading layer on the ATLAS map (five groups of states with equal counts)',', '.join(lg),src,'"'+lg[0]+'"',[' '.join(lg)])
add('atlas.map.outline','State outline simplification on the ATLAS map: tolerance and the island size below which rings are not drawn','about 1.7 km, about 10 square kilometers','atlas/atlasmap_report.txt','tolerance 0.35 px = about 1.7 km; islands under 0.4 square pixels = about 10 square kilometers',['simplified to within about 1.7 kilometers and leaves out islands under about 10 square kilometers'])
out.append('# Existing rows that now also print on the ATLAS page (the map legend says how the plants were thinned):')
out.append(f'{LED} on atlas.pl.drawn atlas "which leaves 4,634 of the 14,280 operating plants"')
out.append(f'{LED} on atlas.pl.plants atlas "of the 14,280 operating plants"')
out.append(f'{LED} on atlas.pn.drawn atlas "which leaves 979 of the 1,608 planned plants"')
out.append(f'{LED} on atlas.pn.gw atlas "of the 1,608 planned plants"')
open(H+'electricity/scale_ledger_commands.txt','w',encoding='utf-8').write('\n'.join(out)+'\n'); print(len(out),'lines')
