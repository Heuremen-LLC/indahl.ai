# K-Veritas README (kveritas-go commit 521070c, 26 Oct 2026) held against the saved outputs of three local tests. python3 -I check_claims_kveritas.py
# The tests (kveritas/test_tamper.sh, test_siblings.sh, test_canary.sh) were run offline in local mode with the network blocked, on synthetic scripts. This file reads their saved outputs.
import json, hashlib, re
FILES = ['kveritas/outputs/tamper.txt', 'kveritas/outputs/siblings.txt', 'kveritas/outputs/canary.txt']; RAW = {f: open(f).read() for f in FILES}
def mk(i, q, calc, st, got, out, note): return dict(id=i, quote=q, calc=calc, stated=st, delivered=got, outcome=out, note=note, label_mismatch=False)
T, S, C = (RAW[f] for f in FILES)
orig = T.split('### original')[1].split('###')[0]
tam = re.findall(r'^### (.+)\n\s+(TAMPERED|[A-Z-]+)', T.split('### original')[1], re.M)
n_t = sum(1 for _, v in tam if v == 'TAMPERED')
K = []
K.append(mk('KV1', 'these numbers came from this code, at this time, unchanged.', 'five edits to a sealed local-mode report, each verified offline', 'a sealed result cannot be changed without detection',
            f'{n_t} of {len(tam)} edits read TAMPERED: ' + '; '.join(t for t, _ in tam), 'CONSISTENT' if n_t == len(tam) else 'BELOW',
            'The edits were a metric value, the invocation count, a kept run exit code, the visible page text and the self-reported signer history. The report reads SELF-ATTESTED, which the tool prints as "signed with an author-supplied key, not K-Veritas". The code and time claims were not tested.'))
failed_msg = 'not kept in the report' in T
shows = bool(re.search(r'Total invocations|Total runs', orig)) or 'mention a failed attempt or an invocation count: True' in T
K.append(mk('KV2', 'every run is recorded, failed ones too, so an attempt shows.', 'a local-mode session with two kept runs and one failed run, sealed and verified offline', 'a failed attempt shows in the report',
            'The failed run printed "It is not kept in the report, but the server still counts it in the run history." The verify output lists Runs: 2 and no line for the failed attempt. The visible pages name no failed attempt. The embedded record holds 2 runs and an invocation count of 3' + ('' if not shows else ' (a line naming it was found)'),
            'BELOW' if failed_msg and not shows else 'CONSISTENT',
            'Verify prints a total of invocations only when a hosted seal supplies one (cmd/kveritas/main.go line 2305). The hosted service was not used for this row, so the sentence is not tested in the mode it describes.'))
K.append(mk('KV3', 'Every run anchored at the server when it ends, failed ones too.', 'needs the hosted service, which these tests did not use', 'every run, failed ones too, is anchored at the server', 'not run: the tests ran in local mode with the network blocked', 'CANNOT_TELL',
            'About ten sessions with a single print each were registered at the hosted service from this Mac by mistake before the network was blocked. A hosted registration sends a session id, a hashed machine id and run digests, with no script text.'))
blocks = {m.group(1): m.group(2) for m in re.finditer(r'### (\w+)\n(.*?)(?=\n### |\Z)', S, re.S)}
hidden = [n for n in ('clean_A', 'delete_session_ledger', 'delete_signer_key_and_ledger') if re.search(r'1 started, 1 sealed, 0 never sealed', blocks.get(n, ''))]
refused = [n for n in ('control_abandon_A', 'delete_A_folder') if 'still open on this machine' in blocks.get(n, '')]
K.append(mk('KV4', 'each report lists sessions started but never sealed.', 'five local-mode scenarios: an abandoned session A, then a second session B sealed and verified', 'a report lists every session started and not sealed',
            f'{len(refused)} of 2 scenarios refused to start B while A was open ({", ".join(refused)}). {len(hidden)} of 3 ended with "1 started, 1 sealed, 0 never sealed" with A absent ({", ".join(hidden)})',
            'BELOW' if len(hidden) == 3 else 'CONSISTENT',
            'kveritas clean is documented to erase a session so that no later report lists it. Deleting the local session file or the signer key does the same. The report prints "New signer: no earlier history, other attempts cannot be ruled out" in those cases, as it does for any first report. The sibling list for a hosted seal was not tested.'))
c1, c2 = C.split('### canary 2')[0], C.split('### canary 2')[1]
fab = 'Compute [FABRICATION-IMPOSSIBLE]' in c1; nov = 'Compute [' not in c2
K.append(mk('KV5', 'Declared FLOPs vs time, energy, memory. PASS / REVIEW / FABRICATION-IMPOSSIBLE / N/A.', 'two canary scripts that print the same result line and take 0.13 seconds', 'the compute check returns one of four verdicts',
            'Canary 1 declared a 7B model for 3 epochs of 1,000,000 examples and read Compute [FABRICATION-IMPOSSIBLE]. Canary 2 declared a 1,000-parameter model and 100 examples and printed no compute line (certificate not applicable, from the source), with the claim val_acc = 0.9713 sealed',
            'CONSISTENT' if fab and nov else 'BELOW', 'A result printed by a script that declares a workload below the compute floor earns no flag, which the tool describes as outside its scope ("Not that the experiment is correct").'))
mem = re.search(r'peak_gpu_memory_mb.*?(\d{4,5}(?:\.\d)?)', C)
K.append(mk('KV6', 'on every run: time, CPU, memory, GPU, energy.', 'peak GPU memory recorded for a run that prints one line; source read for how the counter is sampled on macOS', 'GPU is measured on every run',
            'A script that prints one line recorded peak GPU memory of about 12,400 MB and 100% GPU use. The source reads the system-wide ioreg counters "In use system memory" and "Device Utilization %" (internal/hardware/vendors.go lines 158 to 176)', 'CANNOT_TELL',
            'The sentence does not say whether GPU figures are per process or system-wide. Other jobs were using the GPU on this Mac during the tests, so the recorded figure is not the script\'s own. The compute check uses the same peak figure in its memory review.'))
json.dump(dict(source=FILES + ['raw/kveritas_readme.txt'], sha256=[hashlib.sha256(RAW[f].encode()).hexdigest() for f in FILES], claims=K), open('claims_kveritas.json', 'w'), indent=1)
for c in K: print(c['id'], c['outcome'], '|', c['delivered'][:210])
