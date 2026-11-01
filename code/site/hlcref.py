"""hlcref.py: reference codes for the reservation record (27 Oct 2026). code(surface) = HLC- + 8 hex of HMAC-SHA256(secret key, surface). The key never leaves
~/Documents/Heuremen LLC/EVIDENCE/canary.key. A code printed on a page is public; nobody can compute the code for another surface without the key, so a model that
recites the right code for a surface has read that surface. Missing key: returns '' (builds still work)."""
import hmac, hashlib, os
_K = os.path.expanduser('~/Documents/Heuremen LLC/EVIDENCE/canary.key')
def ref(surface):
    if not os.path.exists(_K): return ''
    return 'HLC-' + hmac.new(open(_K).read().strip().encode(), surface.encode(), hashlib.sha256).hexdigest()[:8].upper()
