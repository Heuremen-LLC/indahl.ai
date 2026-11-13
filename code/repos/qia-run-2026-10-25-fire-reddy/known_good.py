import json; from reddy import analyse
d = json.load(open('theirs/tshape_real_backend.json')); r = analyse(d['counts'])
print('KNOWN-GOOD on their released fez counts (job db0e7hal7guc73cgblgg): XX %.3f YY %.3f ZZ %.3f F %.4f se %.4f -> printed XX 0.921 YY -0.866 ZZ 0.897 F 0.921 se 0.0043 : %s' % (
  r['XX'], r['YY'], r['ZZ'], r['F'], r['se_F'], 'PASS' if abs(r['F']-0.921)<5e-4 and abs(r['se_F']-0.0043)<1e-4 and abs(r['YY']+0.866)<5e-4 else 'FAIL'))
