# Safe reader for PyTorch zip checkpoints. Parses data.pkl with a restricted unpickler that never imports or calls anything
# from the file: every global becomes an inert stub, tensors become (zip entry, offset, shape, stride, dtype) records, and the
# raw bytes are read with zipfile + numpy only. Run callers with python3 -I. No torch, no execution of checkpoint content.
import collections, io, pickle, struct, zipfile
import numpy as np

DT = {"FloatStorage": ("<f4", 4), "DoubleStorage": ("<f8", 8), "HalfStorage": ("<f2", 2), "BFloat16Storage": ("bf16", 2),
      "LongStorage": ("<i8", 8), "IntStorage": ("<i4", 4), "ShortStorage": ("<i2", 2), "CharStorage": ("i1", 1),
      "ByteStorage": ("u1", 1), "BoolStorage": ("?", 1)}

class Stub:
    """Inert placeholder for any global named in the pickle. Accepts any construction and any state, executes nothing."""
    def __init__(self, *a, **k): self.args, self.kw, self.state = a, k, None
    def __setstate__(self, st): self.state = st
    def __call__(self, *a, **k): return Stub(*a, **k)

class StorageType:
    def __init__(self, name): self.name = name

class Ref:
    def __init__(self, key, dtype, numel): self.key, self.dtype, self.numel = key, dtype, numel

class TensorRef:
    def __init__(self, ref, offset, size, stride): self.ref, self.offset, self.size, self.stride = ref, offset, tuple(size), tuple(stride)

def _rebuild_tensor_v2(storage, offset, size, stride, *rest): return TensorRef(storage, offset, size, stride)
def _rebuild_parameter(data, *rest): return data

class Unp(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "collections" and name == "OrderedDict": return collections.OrderedDict
        if module == "torch._utils" and name == "_rebuild_tensor_v2": return _rebuild_tensor_v2
        if module == "torch._utils" and name == "_rebuild_parameter": return _rebuild_parameter
        if module == "torch" and name in DT: return StorageType(name)
        if module == "torch" and name == "Size": return lambda *a: tuple(a[0]) if a else ()
        return Stub                                                       # everything else is inert
    def persistent_load(self, pid):
        assert pid[0] == "storage"
        st = pid[1]; name = st.name if isinstance(st, StorageType) else getattr(st, "__name__", str(st))
        return Ref(str(pid[2]), name, pid[4])

class PT:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        names = self.z.namelist()
        pk = [n for n in names if n.endswith("data.pkl")]
        assert len(pk) == 1, pk
        self.prefix = pk[0][: -len("data.pkl")]
        self.obj = Unp(io.BytesIO(self.z.read(pk[0]))).load()
        self.compressed = any(i.compress_type != 0 for i in self.z.infolist())

    def find_state_dict(self):
        o = self.obj
        if isinstance(o, dict) and any(isinstance(v, TensorRef) for v in o.values()): return o
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, dict) and sum(isinstance(x, TensorRef) for x in v.values()) > 10: return v
        raise ValueError("no state dict found")

    def load(self, t, as_float32=True):
        """Return the tensor as a numpy array (float32 if as_float32, else native storage dtype; bf16 as uint16)."""
        code, isz = DT[t.ref.dtype]
        raw = self.z.read(f"{self.prefix}data/{t.ref.key}")
        n_el = 1
        for d in t.size: n_el *= d
        if code == "bf16":
            u = np.frombuffer(raw, dtype="<u2")
        else:
            u = np.frombuffer(raw, dtype=code)
        # contiguous only (checked), otherwise use strides
        exp = []
        acc = 1
        for d in reversed(t.size): exp.append(acc); acc *= d
        assert tuple(reversed(exp)) == t.stride or n_el <= 1, (t.size, t.stride)
        a = u[t.offset: t.offset + n_el].reshape(t.size)
        if not as_float32: return a
        if code == "bf16": return (a.astype(np.uint32) << 16).view(np.float32)
        return a.astype(np.float32)

def bf16_bits_from_f32(f):
    """bf16 bit pattern of float32 values by truncation of the low 16 bits (exact when the value is bf16-representable)."""
    return (f.view(np.uint32) >> 16).astype(np.uint16)
