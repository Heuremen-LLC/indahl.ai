import numpy as np, rshp, rgeo
D = '/Users/heuremen/bones-forge/tornado_index/data/raw/'
def build(ox=0.0, oy=0.0):
    f, a, g = rshp.read(D + 'boundaries/cb_2024_us_state_20m.zip')
    xs = np.arange(-3200, 3201, 80.0) + ox; ys = np.arange(-800, 3600, 80.0) + oy
    X, Y = np.meshgrid(xs, ys); X = X.ravel(); Y = Y.ravel(); lon, lat = rgeo.inv(X, Y)
    st = np.array([''] * len(X), dtype=object)
    for at, rings in zip(a, g):
        k = at['STUSPS']
        if k in ('AK', 'HI', 'PR', 'GU', 'AS', 'MP', 'VI'): continue
        sel = (lon > -130) & (lon < -60) & (lat > 20) & (lat < 55) & (st == '')
        idx = np.nonzero(sel)[0]
        m = rgeo.inside_even_odd(lon[idx], lat[idx], rings)
        st[idx[m]] = k
    keep = st != ''
    return X[keep], Y[keep], lon[keep], lat[keep], st[keep]
if __name__ == '__main__':
    X, Y, lon, lat, st = build()
    import collections
    print(len(X), (st == 'KS').sum(), np.isin(st, ['TX','OK','KS','NE','SD','IA']).sum(), 'DC' in set(st))
