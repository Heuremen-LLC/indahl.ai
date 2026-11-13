"""Recompute σ_global summaries for arXiv:2603.29019 from Zenodo 10.5281/zenodo.21221337 sigma_posterior.h5. Needs h5py, numpy.
Usage: python 2603.29019_sigma.py path/to/sigma_posterior.h5"""
import sys,h5py,numpy as np
f=h5py.File(sys.argv[1],'r'); cols=[c.decode() for c in f['posterior/block0_items'][:]]
x=np.sort(f['posterior/block0_values'][:,cols.index('sigma')]/1e5)  # cm/s -> km/s
n=len(x); k=int(np.ceil(0.9*n)); i=np.argmin(x[k-1:]-x[:n-k+1]); m=np.median(x)
print('n %d  median %.2f  p95 %.2f  equal-tailed 90%% [%.2f, %.2f] (+%.1f -%.1f)  90%% HDI [%.2f, %.2f]'%(n,m,np.percentile(x,95),np.percentile(x,5),np.percentile(x,95),np.percentile(x,95)-m,m-np.percentile(x,5),x[i],x[i+k-1]))
