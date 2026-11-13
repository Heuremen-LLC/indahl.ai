"""parse_payload.py -- turns the SAVED RAW JOB PAYLOAD into the arrays the analysis reads. THIS FILE IS OUTSIDE THE FREEZE.

WHY IT IS OUTSIDE (said plainly): the real kerneled result for a circuit with three measurements on the same qubits has never been parsed by anyone, here or
(as far as the documentation says) elsewhere. The shape / field names we assume below may be wrong. If the parser lived inside common.py it would be part of the
freeze hash, and repairing a wrong assumption would change the hash and make the run unscorable. The raw payload is saved untouched BEFORE this file runs
(common.fetch_and_save_payload), so a repair here cannot change what the machine returned, only how we read it. Every results file records the sha256 of
the payload and of THIS file (meta.parser_sha256); the report prints both. What stays inside the freeze is the VALIDATION (common.verify_arrays: shape, dtype,
finite, and the exact set of looks in the ledger), which a parser cannot loosen.

parse(raw_text, order, specs, shots, nq) -> {'<key>__L<k>': complex array (shots, nq)}. It refuses anything odd and says what it saw (describe()) instead of guessing.
`python parse_payload.py PAYLOAD.json` prints the structure of a payload (no arrays), to help repair this file."""
import json, sys
import numpy as np


def decode(raw):
    """The SDK's own decoder (what job.result() applies to the raw text)."""
    from qiskit_ibm_runtime import RuntimeDecoder
    return json.loads(raw, cls=RuntimeDecoder)


def describe(res, depth=0):
    """A short plain description of the decoded result's structure (types, shapes, dtypes). No values."""
    try:
        out = [f'result: {type(res).__name__}, {len(res)} pub result(s)']
        for i, pr in enumerate(list(res)[:3]):
            d = pr.data
            out.append(f'  pub {i}: data fields ' + ', '.join(f'{k}: {type(v).__name__}{getattr(np.asarray(v), "shape", "")} {np.asarray(v).dtype}' for k, v in d.items()))
        return '\n'.join(out)
    except Exception as ex:
        return f'(could not describe: {type(ex).__name__}: {ex}) type={type(res).__name__}'


def parse(raw, order, specs, shots, nq):
    res = decode(raw)
    if res is None or isinstance(res, str): raise RuntimeError(f'the payload did not decode to a result object (got {type(res).__name__}); nothing saved')
    if len(res) != len(order): raise RuntimeError(f'result has {len(res)} pubs, expected {len(order)}\n' + describe(res))
    arrays = {}
    for pi, key in enumerate(order):
        nl = len(next(sp for sp in specs if sp['key'] == key)['pre_waits_us'])
        data = res[pi].data
        for k in range(nl):
            name = f'L{k + 1}'
            if hasattr(data, name): a = getattr(data, name)
            elif hasattr(data, name + '_iq'): a = getattr(data, name + '_iq')
            else: raise RuntimeError(f'{key}: no register {name} in result data\n' + describe(res))
            if hasattr(a, 'get_bitstrings') or hasattr(a, 'num_shots'): raise RuntimeError(f'{key} {name}: got a BitArray (classified 0/1), not raw I/Q. Nothing saved.')
            a = np.asarray(a)
            if not np.iscomplexobj(a): raise RuntimeError(f'{key} {name}: dtype {a.dtype} is not complex I/Q\n' + describe(res))
            if a.shape != (shots, nq): raise RuntimeError(f'{key} {name}: shape {a.shape}, expected ({shots}, {nq})\n' + describe(res))
            arrays[f'{key}__L{k + 1}'] = a
    return arrays


if __name__ == '__main__':
    print(describe(decode(open(sys.argv[1]).read())))
