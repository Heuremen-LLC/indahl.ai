import numpy as np
rng=np.random.default_rng(0)
N=200000
b=1+rng.normal(0,.15,N); z=1+rng.normal(0,.12,N)
c=(b-1)*(z-1)
def table(truth,sd=.02):
    if truth=='prod': y=b*z
    elif truth=='sum': y=b+z-1
    else: y=b*z+(c)*0.5   # midpoint
    y=y+rng.normal(0,sd,N)
    r=y-b*z; win=np.abs(r)<np.abs(r+c)
    ratio=np.abs(c)/sd
    q=np.quantile(ratio,[.2,.4,.6,.8]); k=np.digitize(ratio,q)
    return [round(win[k==i].mean(),3) for i in range(5)], round(win.mean(),3)
for t in ('prod','mid','sum'): print(t,table(t))
