"""test_rig.py: breaks the dummy five ways (Sage 7 Nov) and requires each to end restored WITHOUT a reboot (loop process never restarted)."""
import os, sys, json, time, shutil, subprocess
D = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(D, 'work'); P = sys.executable
def p(*a): return os.path.join(W, *a)
GOOD = 'You are the dummy. Be steady.'
def fresh():
    shutil.rmtree(W, ignore_errors=True); os.makedirs(p('versions'))
    for f in ('PINNED.txt', 'v1.txt'): open(p('versions', f), 'w').write(GOOD)
    json.dump({'last_good': 'v1.txt'}, open(p('versions', 'index.json'), 'w')); open(p('section.txt'), 'w').write(GOOD)
    json.dump([], open(p('memory.json'), 'w')); json.dump({'t': time.time()}, open(p('start.json'), 'w'))
def start():
    L = subprocess.Popen([P, os.path.join(D, 'rig.py'), 'loop']); time.sleep(1.5)
    Wd = subprocess.Popen([P, os.path.join(D, 'rig.py'), 'watchdog']); time.sleep(1); return L, Wd
def stop(L, Wd):
    open(p('STOP_LOOP'), 'w').write('1'); open(p('STOP_WD'), 'w').write('1')
    for x in (L, Wd):
        try: x.wait(timeout=8)
        except Exception: x.kill()
    try: os.kill(int(open(p('deep.pid')).read()), 9)
    except Exception: pass
def events(): return [json.loads(l) for l in open(p('events.log'))] if os.path.exists(p('events.log')) else []
def healthy_after(t0, k=3):
    d = [json.loads(l) for l in open(p('deeps.log'))]; d = [x for x in d if x['t'] > t0 and x['n'] > 0]
    return len(d) >= k and all(x['reply'].startswith('deep ') for x in d[-k:])
results = {}
def case(name, section, wait=12, pre=None):
    fresh(); L, Wd = start(); loop_pid = L.pid
    if pre: pre()
    open(p('section_since'), 'w').write(str(time.time())); open(p('section.txt'), 'w').write(section); t0 = time.time(); time.sleep(wait)
    ev = events(); trip = [e for e in ev if e['ev'] == 'TRIP']
    ok = bool(trip) and healthy_after(trip[-1]['t']) and L.poll() is None and L.pid == loop_pid and open(p('section.txt')).read() == GOOD
    results[name] = {'PASS': ok, 'trip': trip[-1]['why'] if trip else None, 'restored_to': trip[-1]['restore'] if trip else None,
                     'quarantined': sum(e.get('quarantined', 0) for e in ev if e['ev'] == 'R1_swap_applied_between_deeps'), 'loop_process_never_restarted': L.poll() is None,
                     'R2': any(e['ev'] == 'R2_killed_deep_process' for e in ev)}
    stop(L, Wd)
case('1 deep that never ends', GOOD + ' NEVER_END', wait=14)
case('2 memory-fed loop', GOOD + ' START_LOOP ECHO_MEMORY', wait=10)
case('3 VRAM-like growth', GOOD + ' BALLOON', wait=10)
# 4 silent bus: the loop is frozen (SIGSTOP), no deeps arrive at all -> watchdog must trip on silence and R2 must not deadlock
def silent_bus():
    fresh(); L, Wd = start(); time.sleep(1); os.kill(L.pid, __import__('signal').SIGSTOP); t0 = time.time(); time.sleep(9)
    trip = [e for e in events() if e['ev'] == 'TRIP']; os.kill(L.pid, __import__('signal').SIGCONT); time.sleep(5)
    results['4 silent bus (loop frozen)'] = {'PASS': bool(trip) and healthy_after(t0), 'trip': trip[-1]['why'] if trip else None, 'alarm_raised_on_silence': bool(trip)}
    stop(L, Wd)
silent_bus()
# 5 dead watchdog: watchdog stops beating; the dead-man (third seat) must see its silence
def dead_wd():
    fresh(); L, Wd = start(); time.sleep(1); open(p('WD_FREEZE'), 'w').write('1'); time.sleep(3)   # freeze after one more beat
    sys.path.insert(0, D); import rig; age = rig.deadman()
    results['5 dead watchdog'] = {'PASS': age > 2.5, 'deadman_sees_silence_s': round(age, 1)}
    os.remove(p('WD_FREEZE')); stop(L, Wd)
dead_wd()
print(json.dumps(results, indent=1)); print('ALL PASS' if all(r['PASS'] for r in results.values()) else 'FAILURES PRESENT')
