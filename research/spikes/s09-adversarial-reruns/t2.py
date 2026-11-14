import sys,json,numpy as np; sys.path.insert(0,'.')
import reed2 as M
for v0 in (4.0,6.0,10.0): print('semi v0',v0,json.dumps(M.an(M.run(v0))),flush=True)
for v0 in (1.5,2.5,4.0): print('rk4 v0',v0,json.dumps(M.an(M.run(v0,scheme='rk4'))),flush=True)
# L1=30mm longer
res=M.run(2.0,L1=0.03,T=4.0); xs=res[0]; fs=res[3]
for a,b in ((0.5,1),(1,2),(2,3),(3,4)):
    s=xs[int(a*fs):int(b*fs)]; print('L1=30mm window',a,b,'amp_um',(s.max()-s.min())/2*1e6,flush=True)
# hysteresis: rise to 2.0 then hold at 1.0 / 0.8
for lo in (1.0,0.8):
    prof=lambda t,lo=lo: (2.0*min(1,t/0.05) if t<0.6 else lo)
    print('hyst down to',lo,json.dumps(M.an(M.run(0,T=1.4,vprof=prof))),flush=True)
