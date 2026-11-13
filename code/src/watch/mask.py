"""MASK -- nothing leaves a script unmasked. Wayfinder and Bones, 20 Oct 2026.

WHY THIS EXISTS. 20 Oct, dumping raven.conf to answer "what port is the RVN node on", I wrote a
redaction that masked IP addresses and nothing else. The file contained `miningaddress=` and a
wallet address went straight into the transcript. The standing rule is explicit -- wallet addresses
are masked -- and I had written a masker that enforced only the half of it I happened to be thinking
about.

STRUCTURE, NOT DISCIPLINE (LAS GUARDAS, first principle). A remembered rule about masking failed on
the first file that contained something I was not looking for. So this is the only masker, every
script imports it, and it masks by PATTERN rather than by what the author remembered to worry about.

WHAT IT MASKS, and each one is a line in the house rules:
  base58 addresses   R.../S.../G... and the generic forms   -> <ADDR>
  bech32 addresses   bc1/rc1-style                          -> <ADDR>
  hex keys and JWTs  long opaque strings                    -> <KEY>
  rpcpassword / rpcuser / token / secret / seed assignments  -> <REDACTED>
  IPv4 addresses                                            -> <IP>

AND IT FAILS LOUD RATHER THAN QUIET: `assert_clean` raises if anything that looks like a secret
survives, so a script can refuse to print instead of printing and apologising afterwards.
"""
import re

_ADDR_B58 = re.compile(r'\b[RSG13][1-9A-HJ-NP-Za-km-z]{25,39}\b')
_ADDR_BECH = re.compile(r'\b(?:bc1|rc1|tb1|sc1)[0-9a-z]{20,70}\b', re.I)
_LONGHEX = re.compile(r'\b[0-9a-fA-F]{40,}\b')
_JWT = re.compile(r'\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b')
_ASSIGN = re.compile(
    r'(?i)\b(rpcpassword|rpcuser|rpcauth|password|passwd|pass|token|secret|apikey|api_key|'
    r'privkey|private_key|seed|mnemonic|wif)\s*[:=]\s*\S+')
_IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def mask(s):
    """Mask every secret-shaped thing in a string. Order matters: assignments first, so a password
    that happens to look like hex is caught as a password and not as a key."""
    if s is None:
        return s
    s = str(s)
    s = _ASSIGN.sub(lambda m: '%s=<REDACTED>' % m.group(1), s)
    s = _JWT.sub('<KEY>', s)
    s = _ADDR_BECH.sub('<ADDR>', s)
    s = _ADDR_B58.sub('<ADDR>', s)
    s = _LONGHEX.sub('<KEY>', s)
    s = _IPV4.sub('<IP>', s)
    return s


def say(*parts):
    """print(), but it cannot leak. Use this instead of print in anything that reads a config."""
    print(' '.join(mask(p) for p in parts), flush=True)


def assert_clean(s, why='output'):
    """Refuse to emit rather than emit and apologise. Raises if anything secret-shaped survives."""
    m = mask(s)
    if m != str(s):
        raise AssertionError('REFUSING TO PRINT %s: it still contains something secret-shaped. '
                             'Masked form would be: %s' % (why, m[:200]))
    return s


if __name__ == '__main__':
    # SELF-TEST on the exact line that leaked, plus the things it did not occur to me to guard.
    cases = [
        'miningaddress=RSbRWAWhX7wkmB6yW6P5haVfxZMkEijzFj',
        'rpcpassword=hunter2seventeen',
        'addnode=192.168.8.140:8767',
        'payout to 1BoatSLRHtKNngkdXEeobR76b53LETtpyT today',
        'digest 9939e51d9ca48d596f9252a8e53726b89eeacf8fc556d2323bb6526358491b0b',
        'nothing secret here at all',
    ]
    for c in cases:
        print('%-62s ->  %s' % (c[:60], mask(c)))
    leaked = [c for c in cases[:5] if mask(c) == c]
    assert not leaked, 'SELF-TEST FAILED, these passed through unmasked: %s' % leaked
    assert mask(cases[5]) == cases[5], 'a clean line must pass through untouched'
    try:
        assert_clean('miningaddress=RSbRWAWhX7wkmB6yW6P5haVfxZMkEijzFj')
        raise SystemExit('SELF-TEST FAILED: assert_clean let an address through')
    except AssertionError:
        pass
    print()
    print('ALL SELF-TESTS HELD. the line that leaked is now caught by pattern, not by memory.')
