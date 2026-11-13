"""known_good_tara.py CSV -- their released ibm_torino table through OUR analyze(): must give S = 2.7320 +- 0.0119 (|dS| < 5e-4)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0]); import tara
r = tara.analyze(tara.table_entries(sys.argv[1]))
print(f"KNOWN-GOOD their table: S {r['S']:.4f} +- {r['se']:.4f}; E {[[round(v,4) for v in row] for row in r['E']]}; cycle spread ratio {r['spread_ratio']:.2f}")
ok = abs(r['S'] - 2.7320) < 5e-4 and abs(r['se'] - 0.0119) < 5e-4; print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
