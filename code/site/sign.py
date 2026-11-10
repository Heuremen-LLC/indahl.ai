#!/usr/bin/env python3
"""sign.py (10 Nov 2026): Ed25519 signatures for indahl.ai, local side.

The public key is in signing_key.json (kid, x as base64url, PEM), served at /.well-known/indahl-signing-key and /.well-known/jwks.json.
The private key lives in two places only: the worker secret SIGNING_KEY_PEM (the worker signs feeds, /api/v1 answers and alert receipts as
it serves them, indahl-ai/security.js) and ~/Documents/Heuremen LLC/ACCOUNTS/indahl_ed25519_private.pem (mode 600, for the local senders).
It is never printed, logged or tracked.

  sign(data: bytes) -> base64url signature (no padding)      verify(data, sig) -> bool against the published key
  webhook_headers(ts, body) -> {'x-indahl-signature-ed25519': ..., 'x-indahl-key-id': ...}   the message is b"<ts>." + body, as the HMAC
  python3 sign.py selftest     sign and verify a random message with the local key and the published key (prints only ok or FAIL)

Works on the bus python (3.9, standard library only): it uses the cryptography package when present, else node's crypto (one short
process per call, key path and message passed by file descriptor and stdin, never on a command line)."""
import base64, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KEYFILE = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/indahl_ed25519_private.pem')
PUB = json.load(open(os.path.join(HERE, 'signing_key.json')))
KID = PUB['kid']
NODE = next((p for p in ('/opt/homebrew/bin/node', '/usr/local/bin/node') if os.path.exists(p)), 'node')
b64u = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()
unb64u = lambda s: base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))

_JS_SIGN = "const c=require('crypto'),fs=require('fs');const k=c.createPrivateKey(fs.readFileSync(process.env.K));" \
           "const m=fs.readFileSync(0);process.stdout.write(c.sign(null,m,k).toString('base64url'))"
_JS_VERIFY = "const c=require('crypto'),fs=require('fs');const k=c.createPublicKey({key:{kty:'OKP',crv:'Ed25519',x:process.env.X},format:'jwk'});" \
             "const m=fs.readFileSync(0);process.stdout.write(c.verify(null,m,k,Buffer.from(process.env.S,'base64url'))?'1':'0')"


def sign(data):
    if isinstance(data, str): data = data.encode()
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        return b64u(load_pem_private_key(open(KEYFILE, 'rb').read(), None).sign(data))
    except ImportError: pass
    r = subprocess.run([NODE, '-e', _JS_SIGN], input=data, capture_output=True, env={'K': KEYFILE, 'PATH': '/usr/bin:/bin'}, timeout=30)
    if r.returncode or not r.stdout: raise RuntimeError('sign: node signing failed')
    return r.stdout.decode().strip()


def verify(data, sig, x=None):
    if isinstance(data, str): data = data.encode()
    x = x or PUB['x']
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        try: Ed25519PublicKey.from_public_bytes(unb64u(x)).verify(unb64u(sig), data); return True
        except Exception: return False
    except ImportError: pass
    r = subprocess.run([NODE, '-e', _JS_VERIFY], input=data, capture_output=True, env={'X': x, 'S': sig, 'PATH': '/usr/bin:/bin'}, timeout=30)
    return r.stdout.decode().strip() == '1'


def webhook_headers(ts, body):
    return {'x-indahl-signature-ed25519': sign(str(ts).encode() + b'.' + body), 'x-indahl-key-id': KID}


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        m = os.urandom(64); s = sign(m)
        ok = verify(m, s) and not verify(m + b'x', s)
        print('sign selftest: ok (kid %s)' % KID if ok else 'sign selftest: FAIL'); sys.exit(0 if ok else 1)
    print(__doc__)
