"""DICE FOR THE PUP, round 2 -- 2026-09-26 (Wayfinder: "give the dog a bone"). One Rigetti Cepheus task: every usable qubit
gets rx(pi/2) (a fair quantum coin) and is measured; 10,000 shots. Raw bits are biased (readout), so they go through the same
extractor as round 1: SHA-256 over 512-bit blocks -> 256 bits out. Output: pup_seeds.bin, 32 bytes per seed, one seed per bark
(the pup grows each bark's randomness from its seed; every seed is used once and then gone).
  qvenv/bin/python dice_refill.py --dry | --submit | --collect
"""
import hashlib, json, math, os, sys, time
import braket_round1_step3 as s3

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 10000
LABEL = 'pup dice refill (rx(pi/2) on many qubits)'

def qubits(dev):
    q = sorted(int(x) for x in dev.properties.paradigm.connectivity.connectivityGraph.keys())
    return q[:80]

def build():
    from braket.circuits import Circuit
    from braket.aws import AwsDevice
    dev = AwsDevice(s3.DEVICE); qs = qubits(dev); c = Circuit()
    for q in qs: c.rx(q, math.pi / 2)
    return dev, Circuit().add_verbatim_box(c), qs

def main():
    m = sys.argv[1] if len(sys.argv) > 1 else '--dry'
    tf = os.path.join(HERE, 'dice_refill_task.json')
    if m in ('--dry', '--submit'):
        cost = s3.PER_TASK + SHOTS * s3.PER_SHOT; L = json.load(open(s3.LEDGER))
        if L['spent_est'] + cost > s3.CAP: raise SystemExit(f'BRAKE: ${cost:.2f} would pass ${s3.CAP:.2f}')
        dev, c, qs = build(); print(f'{LABEL}: {len(qs)} qubits x {SHOTS} shots = ${cost:.2f} (spent ${L["spent_est"]:.2f} / ${s3.CAP:.2f})')
        if m == '--dry': return
        t = dev.run(c, shots=SHOTS, disable_qubit_rewiring=True)
        L['spent_est'] = round(L['spent_est'] + cost, 4)
        L['entries'].append({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'label': LABEL, 'tasks': 1, 'cost_est': round(cost, 4)})
        json.dump(L, open(s3.LEDGER, 'w'), indent=1); json.dump({'arn': t.id, 'qubits': qs, 'shots': SHOTS}, open(tf, 'w'), indent=1)
        print('submitted', t.id[-12:], f'ledger ${L["spent_est"]:.2f}')
    if m == '--collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(tf)); task = AwsQuantumTask(T['arn'])
        if task.state() != 'COMPLETED': print('state', task.state()); return
        r = task.result(); bits = ''.join(''.join(str(int(b)) for b in row) for row in r.measurements)
        ones = bits.count('1') / len(bits)
        raw = int(bits, 2).to_bytes((len(bits) + 7) // 8, 'big')
        out = b''.join(hashlib.sha256(raw[i:i + 64]).digest() for i in range(0, len(raw) - 63, 64))
        open(os.path.join(HERE, 'pup_seeds.bin'), 'wb').write(out)
        prov = {'what': 'qubit seeds for THE PUP (32 bytes each, one per bark)', 'from': f'Rigetti Cepheus-1-108Q, {len(T["qubits"])} qubits x rx(pi/2), {T["shots"]} shots, {time.strftime("%Y-%m-%d")}',
                'arn': T['arn'], 'raw_bits': len(bits), 'ones_fraction_raw': round(ones, 4), 'extractor': 'SHA-256 over 512-bit blocks',
                'seed_bytes': len(out), 'seeds': len(out) // 32}
        json.dump(prov, open(os.path.join(HERE, 'pup_seeds.provenance.json'), 'w'), indent=1); print(json.dumps(prov, indent=1))

if __name__ == '__main__':
    main()
