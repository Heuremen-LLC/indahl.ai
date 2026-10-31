"""Compare data/trajectories (251) to trajectories (372): same ids? identical bytes? usage: python3 -I compare_data_vs_trajectories.py <hf_root>"""
import sys, os, json, hashlib, collections
root = sys.argv[1]
A = {f: open(os.path.join(root,"trajectories",f),"rb").read() for f in os.listdir(os.path.join(root,"trajectories")) if f.endswith(".json")}
B = {f: open(os.path.join(root,"data/trajectories",f),"rb").read() for f in os.listdir(os.path.join(root,"data/trajectories")) if f.endswith(".json")}
print("in data/ not in trajectories/:", len(set(B)-set(A)))
print("in both:", len(set(A)&set(B)))
same = sum(1 for f in set(A)&set(B) if A[f]==B[f])
print("byte-identical among shared:", same)
diff = [f for f in set(A)&set(B) if A[f]!=B[f]]
print("differing:", len(diff))
for f in sorted(diff)[:5]:
    a=json.loads(A[f]); b=json.loads(B[f])
    ks=[k for k in a if a[k]!=b.get(k)]
    print(" ", f, "differs in top keys:", ks)
