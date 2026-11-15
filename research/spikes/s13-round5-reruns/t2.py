import sys, json, math, numpy as np, similarity as s
R=4; out=[]
cases=[(44100,27.5),(44100,176400/110*1.0001),(44100,176400*3/110*1.0001),(48000,192000*3/110*1.0001),(44100,6000.0),(48000,6000.0)]
for fs,f in cases:
    m=math.ceil(110*f/(R*fs)); rate=R*fs*m; k=f/444.0; p=s.reed(k)
    for p0 in (1500,1800):
        T=(120 if f<100 else 450)/f
        a=s.analyse(p,s.run(p,p0,rate,T=T),rate); a.update(fs=fs,f=round(f,2),m=m,spp=round(rate/f,2),p0=p0); out.append(a); print(json.dumps(a),flush=True)
json.dump(out,open("t2.json","w"),indent=1)
