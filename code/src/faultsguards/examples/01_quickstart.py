"""Quickstart: look things up, then build the preflight that goes ahead of a task. No model, no network."""
import faultsguards as fg
print('Families of faults:'); [print(' ', f['part'], '->', len(f['numbers']), 'faults') for f in fg.families('faults')]
print('\nFaults that mention a baseline:'); [print(' ', h['number'], h['title']) for h in fg.search('baseline', 'faults')[:5]]
print('\nGuard 8, in full:\n'); g = fg.get_guard(8); print(g['title'] + '\n' + g['text'][:400] + ' ...')
print('\nPreflight ahead of a task (titles only):\n'); print(fg.preflight('Compare our model against the vendor claim and report the gap.')[:900])
