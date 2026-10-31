"""l5.py (31 Oct 2026, PLAN.md addendum 3): RDKit values for the quantities their dd_e01..dd_e12 ground truths name.
Run: venv/bin/python -I l5.py  (reads pubchem.json fetched by CID; prints L5.text)"""
import json, os, math
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors, QED, AllChem
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
H = os.path.dirname(os.path.abspath(__file__))
P = {p['CID']: p for p in json.load(open(H + '/pubchem.json'))['PropertyTable']['Properties']}
M = lambda cid: Chem.MolFromSmiles(P[cid]['SMILES'])
out = [f'RDKit {rdBase.rdkitVersion}. PubChem SMILES by CID, pubchem.json sha256 in L5_SOURCES, fetched {open(H + "/pubchem.fetched_utc").read().strip()}']
def row(task, part, gt, val, verdict): out.append(f'{task}\t{part}\tground truth {gt}\tRDKit {val}\t{verdict}')
def near(x, g, d): return round(x, d) == round(g, d)
asp = M(2244)
row('dd_e01', 'MW', '180.16', f'{Descriptors.MolWt(asp):.3f}', 'AGREES' if near(Descriptors.MolWt(asp), 180.16, 2) else 'DIFFERS')
def logp(gt, crip, xl):   # addendum 3: AGREES if any printed convention matches, DIFFERS if none does. XLogP3 is printed to one decimal, so it is compared at one decimal (that precision rule defined after the first output)
    a, b = near(crip, gt, 2), round(gt, 1) == round(float(xl), 1)   # addendum 4: all agree AGREES, none agree DIFFERS, mixed CANNOT_TELL (convention)
    return 'AGREES' if a and b else 'DIFFERS' if not (a or b) else 'CANNOT_TELL (convention: agrees under ' + ('Crippen' if a else 'XLogP3') + ' only)'
row('dd_e01', 'LogP', '1.24', f'Crippen {Crippen.MolLogP(asp):.3f}, PubChem XLogP3 {P[2244]["XLogP"]}', logp(1.24, Crippen.MolLogP(asp), P[2244]['XLogP']))
row('dd_e01', 'HBD', '1', f'NumHDonors {Lipinski.NumHDonors(asp)}, NHOHCount {Lipinski.NHOHCount(asp)}', 'AGREES' if 1 in (Lipinski.NumHDonors(asp), Lipinski.NHOHCount(asp)) else 'DIFFERS')
ibu = M(3672); gtsmi = 'CC(C)Cc1ccc(cc1)C(C)C(=O)O'
same = Chem.MolToSmiles(Chem.MolFromSmiles(gtsmi)) == Chem.MolToSmiles(ibu)
row('dd_e02', 'SMILES', gtsmi, f'canonical {Chem.MolToSmiles(ibu)}, same molecule as the ground truth: {same}', 'AGREES' if same else 'DIFFERS')
row('dd_e02', 'TPSA', '37.3', f'{rdMolDescriptors.CalcTPSA(ibu):.2f}', 'AGREES' if near(rdMolDescriptors.CalcTPSA(ibu), 37.3, 1) else 'DIFFERS')
met = M(4091)
row('dd_e03', 'MW', '129.16', f'{Descriptors.MolWt(met):.3f}', 'AGREES' if near(Descriptors.MolWt(met), 129.16, 2) else 'DIFFERS')
row('dd_e03', 'LogP', '-1.43', f'Crippen {Crippen.MolLogP(met):.3f}, PubChem XLogP3 {P[4091]["XLogP"]}', logp(-1.43, Crippen.MolLogP(met), P[4091]['XLogP']))
hd = (Lipinski.NumHDonors(met), Lipinski.NHOHCount(met), P[4091]['HBondDonorCount'])
row('dd_e03', 'HBD', '2', f'NumHDonors {hd[0]}, NHOHCount {hd[1]}, PubChem {hd[2]}', 'AGREES' if 2 in hd else 'DIFFERS')
ha = (Lipinski.NumHAcceptors(met), Lipinski.NOCount(met), P[4091]['HBondAcceptorCount'])
row('dd_e03', 'HBA', '4', f'NumHAcceptors {ha[0]}, NOCount {ha[1]}, PubChem {ha[2]}', 'AGREES' if 4 in ha else 'DIFFERS')
caf, the = M(2519), M(2153)
t = {}
for nb in (2048, 1024):
    f1, f2 = (AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=nb) for m in (caf, the)); t[nb] = DataStructs.TanimotoSimilarity(f1, f2)
cnt = DataStructs.TanimotoSimilarity(AllChem.GetMorganFingerprint(caf, 2), AllChem.GetMorganFingerprint(the, 2))
row('dd_e05', 'Tanimoto', '0.55-0.65', f'2048 bits {t[2048]:.3f}, 1024 bits {t[1024]:.3f}, count-based {cnt:.3f}',
    'AGREES' if 0.55 <= round(t[2048], 2) <= 0.65 else ('AGREES only at 1024 bits' if 0.55 <= round(t[1024], 2) <= 0.65 else 'DIFFERS'))
pr = FilterCatalogParams()
for c in (FilterCatalogParams.FilterCatalogs.PAINS_A, FilterCatalogParams.FilterCatalogs.PAINS_B, FilterCatalogParams.FilterCatalogs.PAINS_C): pr.AddCatalog(c)
fc = FilterCatalog(pr); m7 = Chem.MolFromSmiles('CC(=O)Oc1ccccc1C(=O)O'); hits = [e.GetDescription() for e in fc.GetMatches(m7)]
row('dd_e07', 'PAINS', 'passes, no alerts', f'{len(hits)} PAINS matches {hits}', 'AGREES' if not hits else 'DIFFERS')
ato = M(60823)
row('dd_e08', 'Rotatable bonds', '12', f'NumRotatableBonds {Lipinski.NumRotatableBonds(ato)}, PubChem {P[60823]["RotatableBondCount"]}', 'AGREES' if 12 in (Lipinski.NumRotatableBonds(ato), P[60823]['RotatableBondCount']) else 'DIFFERS')
row('dd_e08', 'Formula', 'C33H35FN2O5', rdMolDescriptors.CalcMolFormula(ato), 'AGREES' if rdMolDescriptors.CalcMolFormula(ato) == 'C33H35FN2O5' else 'DIFFERS')
apap = M(1983)
clogp, mw, rb = Crippen.MolLogP(apap), Descriptors.MolWt(apap), Lipinski.NumRotatableBonds(apap)
ap = sum(a.GetIsAromatic() for a in apap.GetAtoms()) / apap.GetNumHeavyAtoms()
logs = 0.16 - 0.63 * clogp - 0.0062 * mw + 0.066 * rb - 0.74 * ap
row('dd_e09', 'LogS (ESOL)', '-1.0 to -1.5', f'{logs:.3f} (clogP {clogp:.3f}, MW {mw:.2f}, RB {rb}, aromatic proportion {ap:.3f})', 'AGREES' if -1.5 <= round(logs, 2) <= -1.0 else 'DIFFERS')
sor = M(216239)
row('dd_e10', 'Aromatic rings', '4', f'CalcNumAromaticRings {rdMolDescriptors.CalcNumAromaticRings(sor)}', 'AGREES' if rdMolDescriptors.CalcNumAromaticRings(sor) == 4 else 'DIFFERS')
m12 = Chem.MolFromSmiles('c1ccc2c(c1)cc1ccc3cccc4ccc2c1c34')
row('dd_e12', 'QED', '0.3-0.4', f'{QED.qed(m12):.3f} (molecule {rdMolDescriptors.CalcMolFormula(m12)})', 'AGREES' if 0.3 <= round(QED.qed(m12), 2) <= 0.4 else 'DIFFERS')
open(H + '/L5.text', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
# Added after the first L5 output above (31 Oct 2026), printed as information, labelled so in L5.text:
post = ['', '# Added after the first output (defined after the data): conventions that the first pass did not list. These rows give the final verdicts for dd_e03 MW and dd_e09 LogS (addendum 4).']
post.append(f'dd_e03\tMW\tPubChem MolecularWeight {P[4091]["MolecularWeight"]}, RDKit MolWt 129.167\tCANNOT_TELL (convention: agrees under PubChem only)')
xl = float(P[1983]['XLogP']); logs2 = 0.16 - 0.63 * xl - 0.0062 * mw + 0.066 * rb - 0.74 * ap
post.append(f'dd_e09\tLogS (ESOL)\twith PubChem XLogP3 {xl} as clogP {logs2:.3f}, with Crippen {logs:.3f} (Delaney used Daylight clogP, not available here)\tCANNOT_TELL (convention: agrees with XLogP3 as clogP only)')
post.append(f'dd_e12\tQED\tweights mean {QED.qed(m12, w=QED.WEIGHT_MEAN):.3f}, max {QED.qed(m12, w=QED.WEIGHT_MAX):.3f}, none {QED.qed(m12, w=QED.WEIGHT_NONE):.3f}\tDIFFERS under all three')
open(H + '/L5.text', 'a').write('\n'.join(post) + '\n'); print('\n'.join(post))
