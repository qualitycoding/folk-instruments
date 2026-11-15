import sys, json, numpy as np, similarity as s
out=[]
for k in (1.0, 0.5, 6.0):
    p=s.reed(k)
    for spp in (110, 400):
        fs=spp*p["f"]
        for p0 in (100, 700, 1500):
            r=s.run(p,p0,fs,T=450/p["f"]); a=s.analyse(p,r,fs)
            if r is not None:
                xs,us=r; m=slice(int(0.7*len(xs)),None); du=np.diff(us[m])*fs
                a.update(xmin_x0=round(float(xs[m].min()/p["x0"]),2), xmax_x0=round(float(xs[m].max()/p["x0"]),2),
                         dudt_rms=float(np.sqrt(np.mean((du-du.mean())**2))), u_rms=float(us[m].std()))
            a.update(k=k,spp=spp,p0=p0); out.append(a); print(json.dumps(a),flush=True)
json.dump(out,open("t1.json","w"),indent=1)
