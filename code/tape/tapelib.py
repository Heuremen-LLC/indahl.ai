"""tapelib.py: the pieces TAPE and its verifier share. See PLAN.md."""
import hashlib, json
def sha(b): return hashlib.sha256(b).hexdigest()
def leaf_text(label, h): return '%s\t%s' % (label, h)
def merkle(leaves):
    """leaves: list of (label, hash). Binary SHA-256 tree, leaf = H(0x00 + text), node = H(0x01 + l + r), odd node carried up unchanged."""
    lv = [sha(b'\x00' + leaf_text(l, h).encode()) for l, h in sorted(leaves)]
    if not lv: return sha(b'')
    while len(lv) > 1:
        nx = [sha(b'\x01' + bytes.fromhex(lv[i]) + bytes.fromhex(lv[i + 1])) for i in range(0, len(lv) - 1, 2)]
        if len(lv) % 2: nx.append(lv[-1])
        lv = nx
    return lv[0]
def beacon(randomness, feeds_root, prev, qroot=None):
    # a beacon with no quantum entry behind it keeps the three-input form (PLAN Addendum 2, rule 3)
    return sha(('%s:%s:%s' % (randomness, feeds_root, prev) + ((':%s' % qroot) if qroot and qroot != 'NONE' else '')).encode())
FIELDS = ('n', 't', 'kind', 'subject', 'root', 'prev')
def entry_hash(e): return sha(json.dumps({k: e[k] for k in FIELDS}, sort_keys=True, separators=(',', ':')).encode())
