"""live.py -- the ONLY place that opens the IBM account. Read-only helpers + an HTTP GUARD.

HARD RULES (owner, 2026-10-01): a read of a chip's numbers is a look at that chip. Only the chips this run is about may be touched:
  * ibm_kingston (OURS), the MAKER chip, the BLANK chip -- and only as the run's box allows. The left-alone chip is NEVER touched.
  * In this build pass ONLY ibm_kingston was queried (allowed = {'ibm_kingston'}).
The guard patches requests.Session.request, so nothing in qiskit-ibm-runtime can reach a chip (or submit a job) around it:
  - any URL naming a chip that is not in `allowed` is refused, whatever the call;
  - for a BLIND chip (BLANK, and the MAKER at fire time) only the backend LIST, the static configuration, and the status are allowed; EVERYTHING else naming that chip is refused;
  - POST/PUT/PATCH/DELETE on /jobs (a submission) is refused unless allow_submit=True (never True in a build pass);
  - EVERY request the guard sees (allowed or refused, in every branch) is recorded in GUARD_LOG (method + path, never a header, never a token), which the callers write to the read log.
Tokens are never printed; error text is scrubbed of the token."""
import os, re, json, datetime

CHIPS_NEVER_BY_NAME = ('ibm_boston', 'ibm_phoenix', 'ibm_pittsburgh', 'ibm_kingston')
GUARD_LOG = []
BLIND_ALLOWED_REST = ('/configuration', '/status')      # the ONLY two things a blind chip may be asked: its size-and-timing tick and "is it up"
_state = {'installed': False, 'allowed': set(), 'blind': set(), 'allow_submit': False, 'orig': None}
HOME = os.path.expanduser('~/bones-forge')
CRN_FILE = os.path.join(HOME, '.ibm_quantum_instance_crn')
TOKEN_FILES = [os.path.join(HOME, '.ibm_quantum_key_3'), os.path.join(HOME, '.ibm_quantum_key_parallax')]
READ_LOG = os.environ.get('QTR_READ_LOG') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'account_reads_log.jsonl')


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


class GuardRefused(RuntimeError):
    pass


def install_guard(allowed, blind=(), allow_submit=False):
    """allowed: chip names that may be named in a URL. blind: chips for which calibration/properties/defaults are refused."""
    import requests
    _state['allowed'] = set(allowed); _state['blind'] = set(blind); _state['allow_submit'] = bool(allow_submit)
    if _state['installed']: return
    orig = requests.sessions.Session.request

    def guarded(self, method, url, *a, **kw):
        u = str(url); path = re.sub(r'^https?://[^/]+', '', u); host = re.sub(r'^https?://([^/]+).*$', r'\1', u)
        low = path.lower(); clean = path.split('?')[0]
        def refuse(why, exc):
            GUARD_LOG.append({'at': now_iso(), 'method': method, 'host': host, 'path': clean, 'REFUSED': why}); raise GuardRefused(exc)
        if not (host.endswith('.ibm.com') or host.endswith('.cloud.ibm.com') or host.endswith('.bluemix.net')):
            refuse('host not IBM', f'refused: host {host}')
        for c in CHIPS_NEVER_BY_NAME:
            if c in low and c not in _state['allowed']:
                refuse(f'names chip {c} (not allowed)', f'refused: URL names {c}, which this run may not touch')
        m = re.search(r'/backends/([^/?]+)(/[^?]*)?', path)
        if m:
            nm, rest = m.group(1), (m.group(2) or '')
            if nm not in _state['allowed'] and nm in CHIPS_NEVER_BY_NAME:
                refuse(f'backend {nm} not allowed', f'refused: backend {nm}')
            # FIX G: a BLIND chip (BLANK, and the MAKER at fire time) may have ONLY its static configuration and its status read: nothing else, ever.
            if nm in _state['blind'] and rest.rstrip('/') not in BLIND_ALLOWED_REST:
                refuse('BLIND chip: only configuration and status may be read', f'refused: BLIND chip {nm} may have only its configuration and status read (asked: {rest or "(the chip itself)"})')
        if method.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') and re.search(r'/jobs?\b', low) and not _state['allow_submit']:
            refuse('job submission', 'refused: job submission')
        GUARD_LOG.append({'at': now_iso(), 'method': method, 'path': clean})
        return orig(self, method, url, *a, **kw)
    requests.sessions.Session.request = guarded
    _state['installed'] = True


def load_credentials():
    """(token, crn, which_file_name). token_3 first, fallback parallax. Never printed."""
    crn = open(CRN_FILE).read().strip()
    out = []
    for p in TOKEN_FILES:
        if os.path.exists(p): out.append((open(p).read().strip(), os.path.basename(p)))
    if not out: raise RuntimeError('no token file found (.ibm_quantum_key_3 / .ibm_quantum_key_parallax)')
    return crn, out


def scrub(msg, secrets):
    for s in secrets:
        if s: msg = msg.replace(s, '<token>')
    return msg[:300]


def open_service(note='', log=True):
    """Connect with the instance CRN and the token (key_3, fallback key_parallax). Returns (service, which_token_file, crn_is_loaded).
    The constructor lists the backend NAMES (one REST list call); it does not fetch any chip's configuration or calibration."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    crn, toks = load_credentials(); errs = []
    for tok, name in toks:
        try:
            svc = QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=crn)
            return svc, name
        except Exception as e:
            errs.append(f'{name}: {type(e).__name__}: {scrub(str(e), [tok, crn])}')
    raise RuntimeError('could not connect with any token file: ' + ' | '.join(errs))


def list_backend_names(svc, crn=None):
    """Backend NAMES only (the one /backends REST list call; no per-chip configuration, no calibration)."""
    crn = crn or svc._account.instance
    return svc._discover_backends_from_instance(crn)


def log_read(label, detail=None, touched_a_bit=False, guard_from=0):
    """Append one line to the read log. Every account/calibration read made in a build pass or at freeze/fire time goes here."""
    rec = {'at': now_iso(), 'what': label, 'touched_a_bit': bool(touched_a_bit), 'detail': detail or {}, 'requests': GUARD_LOG[guard_from:]}
    with open(READ_LOG, 'a') as f: f.write(json.dumps(rec, default=str) + '\n')
    return rec


def classify_request(r, chip):
    """Plain-words kind of one logged request (for the look ledger). Chip-naming requests are the ones that count as looks at that chip."""
    path = r.get('path') or ''; m = re.search(r'/backends/([^/?]+)(/[^?]*)?', path)
    if r.get('REFUSED'): return 'refused'
    if m and m.group(1) == chip:
        rest = (m.group(2) or '').rstrip('/')
        if rest == '/configuration': return 'chip_configuration'
        if rest == '/status': return 'chip_status'
        if re.search(r'propert|calib|default|target|pulse', rest.lower()): return 'chip_properties'
        return 'chip_other'
    if re.search(r'/jobs?\b', path.lower()): return 'job'
    if 'usage' in path.lower(): return 'account_usage'
    if re.search(r'/backends/?$', path.lower()): return 'backend_names'
    return 'account'


KIND_WORDS = {
    'chip_configuration': "THE CHIP'S SIZE AND TIMING TICK (its static configuration: qubit count, dt, rep_delay range): needed to lay the circuits; a read of the chip",
    'chip_status': 'IS IT UP (the status the SDK fetches at submit): a read of the chip',
    'chip_properties': "THE CHIP'S CALIBRATION / PROPERTIES (the maker's published numbers): a read of the chip",
    'chip_other': 'ANOTHER REQUEST NAMING THE CHIP (should not exist)',
}


def ledger_reads(reqs, chip):
    """Turn a slice of GUARD_LOG into look-ledger entries: one per chip-naming request (plain words), plus one line for the account-level requests."""
    out, acct = [], []
    for r in reqs:
        k = classify_request(r, chip)
        if k in KIND_WORDS: out.append({'at': r.get('at'), 'what': KIND_WORDS[k], 'request': f"{r['method']} {r.get('path')}", 'touched_a_bit': False, 'chip': chip, 'kind': k})
        else: acct.append(f"{r['method']} {r.get('path', r.get('host'))}" + (f" REFUSED({r['REFUSED']})" if r.get('REFUSED') else ''))
    if acct: out.insert(0, {'at': reqs[0].get('at') if reqs else None, 'what': 'ACCOUNT-LEVEL requests (identity, instance lookup, backend NAMES, usage, job); not a read of any chip', 'requests': acct, 'touched_a_bit': False, 'chip': None, 'kind': 'account'})
    return out
