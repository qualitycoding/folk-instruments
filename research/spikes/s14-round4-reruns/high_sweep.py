import sys, json, numpy as np
from scaled_reed import make, run, analyse
base = dict(kf=3520/444, kL=0.45, ke=(3520/444)*0.45**2, kW=0.85)
variants = {'x0/2': dict(kx0=0.225), 'x0/4': dict(kx0=0.1125), 'Q30': dict(Q=30.), 'V/16': dict(kV=1/16), 'V/64': dict(kV=1/64),
            'V/64,L2/4': dict(kV=1/64, kL2S2=0.25), 'x0/4,V/16': dict(kx0=0.1125, kV=1/16), 'thin_e(L*0.6)': dict(kL=0.6, ke=(3520/444)*0.36, kx0=0.6),
            'x0/4,Q30,V/16': dict(kx0=0.1125, Q=30., kV=1/16),
 'x0=40um,hmin15': dict(kx0=40/528, hmin=15e-6), 'x0=40um,hmin15,V/16': dict(kx0=40/528, hmin=15e-6, kV=1/16),
 'x0=20um,hmin5,Q30': dict(kx0=20/528, hmin=5e-6, Q=30.), 'L2/16': dict(kL2S2=1/16), 'L2/64': dict(kL2S2=1/64), 'L2/16,x0=80um,hmin20': dict(kL2S2=1/16, kx0=80/528, hmin=20e-6), 'light_reed_K47.9': dict(kL=1, ke=1, kW=1, K_override=47.9), 'x0=40um,hmin15,p_es0.5': dict(kx0=40/528, hmin=15e-6, es=500e-6)}
sel = sys.argv[1:]
for name in sel:
    P = make(**{**base, **variants[name]})
    for p0 in (200, 1000, 3000):
        a = analyse(P, *run(P, p0, T=0.4)); print(name, 'cond=%.2f' % P['cond'], p0, a, flush=True)
