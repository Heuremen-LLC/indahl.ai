"""QIA queue probe, from Heuremen LLC (https://indahl.ai/qia). How long does a job wait on an IBM quantum processor right now?

Two things you can check with your own IBM Quantum account:
  python probe.py --front          jobs in front on every processor your account sees. Free: nothing is sent.
  python probe.py ibm_fez          sends the smallest real job (one qubit, X, measure, one shot) to ibm_fez, waits for it,
                                   and prints how long it waited from creation to running, and what IBM charged.

Cost: a probe is charged IBM's minimum, 2 seconds of your plan (measured 30 October 2026, also for a job that fails at the front).
A job you cancel while it is still queued is not charged, but IBM then records no start time, so it carries no wait.
On the Open plan your wait follows the shared line. On a paid plan a job can start well ahead of the jobs in front.

Needs Python 3.9 or newer and:  pip install qiskit qiskit-ibm-runtime
  (https://pypi.org/project/qiskit/ , https://pypi.org/project/qiskit-ibm-runtime/ , https://github.com/Qiskit/qiskit-ibm-runtime)
Your key, never written to disk by this script:
  export IBM_QUANTUM_TOKEN=your_api_key
  export IBM_QUANTUM_INSTANCE=your_instance_crn      (optional: leave unset to use the default instance of the key)
"""
import os, sys, time
from datetime import datetime


def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = os.environ.get('IBM_QUANTUM_TOKEN')
    if not tok: sys.exit('Set IBM_QUANTUM_TOKEN to your IBM Quantum API key first.')
    ins = os.environ.get('IBM_QUANTUM_INSTANCE')
    return QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=ins) if ins else QiskitRuntimeService(channel='ibm_quantum_platform', token=tok)


def front(s):
    print('%-18s %s' % ('processor', 'jobs in front'))
    for b in sorted(s.backends(operational=True, simulator=False), key=lambda b: b.name):
        print('%-18s %s' % (b.name, b.status().pending_jobs))


def probe(s, name):
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import SamplerV2
    be = s.backend(name); n = be.status().pending_jobs
    qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0)
    job = SamplerV2(mode=be).run([transpile(qc, be, optimization_level=1)], shots=1)
    print('sent to %s with %d jobs in front, job %s. Waiting (Ctrl-C leaves it in the queue).' % (name, n, job.job_id()), flush=True)
    t0 = time.time()
    while str(job.status()) not in ('RUNNING', 'DONE', 'ERROR', 'CANCELLED'):
        time.sleep(10); print('  still queued after %d s' % (time.time() - t0), flush=True)
    while str(job.status()) not in ('DONE', 'ERROR', 'CANCELLED'): time.sleep(2)
    m = job.metrics(); ts = m.get('timestamps') or {}
    if not ts.get('running'): print('no start time recorded (status %s)' % job.status()); return
    c, r = (datetime.fromisoformat(str(ts[k]).replace('Z', '+00:00')) for k in ('created', 'running'))
    print('%s: waited %.1f s from creation to running; charged %s s' % (name, (r - c).total_seconds(), (m.get('usage') or {}).get('qpu_charge_time_seconds')))


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    s = service()
    if sys.argv[1] == '--front': front(s)
    else: probe(s, sys.argv[1])
