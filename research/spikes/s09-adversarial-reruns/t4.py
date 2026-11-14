import sys,json,numpy as np; sys.path.insert(0,'.')
import reed2 as M
res=M.run(2.0,L1=0.02,T=4.0); xs=res[0]; fs=res[3]
for a,b in ((0.5,1),(1,2),(2,3),(3,4)):
    s=xs[int(a*fs):int(b*fs)]; print('L1=20mm',a,b,'amp_um',(s.max()-s.min())/2*1e6,flush=True)
for hi in (4.0,5.0,6.0):
    prof=lambda t,hi=hi: 3.5*min(1,t/0.05) if t<0.5 else min(hi,3.5+(hi-3.5)*(t-0.5)/0.3)
    print('slow rise 3.5->',hi,json.dumps(M.an(M.run(0,T=1.4,vprof=prof))),flush=True)
