import json, math, numpy as np, similarity as s
R=4
for fs,f in [(44100,176400/110*0.9999),(44100,176400*3/110*0.9999),(48000,192000*4/110*0.9999)]:
    m=math.ceil(110*f/(R*fs)); rate=R*fs*m; p=s.reed(f/444)
    for p0 in (1500,1800):
        a=s.analyse(p,s.run(p,p0,rate,T=450/f),rate); a.update(fs=fs,f=round(f,2),m=m,spp=round(rate/f,3),p0=p0); print(json.dumps(a),flush=True)
