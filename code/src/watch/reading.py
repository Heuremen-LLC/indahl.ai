"""reading.py -- SHIM. The canonical module is triangulation/wen_data/reading.py.

9 Oct: this type has to run in TWO places -- in watch/ where the boards read, and ON THE POD where the
exam writes, and the pod only receives wen_data/. Two copies is the fault that left SEVEN defined four
times on disk with four different contents. So there is ONE file, it lives beside dyads.py where the
pod can reach it, and this has no body of its own.

Loaded BY PATH, not by name: a plain `from reading import ...` here resolves to this file, because
watch/ is first on sys.path -- which is a circular import and was the first thing it did.
"""
import importlib.util as _ilu
import os as _os

_CANON = _os.path.expanduser('~/bones-forge/triangulation/wen_data/reading.py')
_spec = _ilu.spec_from_file_location('_reading_canon', _CANON)
_m = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_m)

Reading = _m.Reading
Collapsed = _m.Collapsed
ROW = _m.ROW
as_row = _m.as_row
from_row = _m.from_row
count = _m.count
show = _m.show
demo = _m.demo
CANONICAL_PATH = _CANON
