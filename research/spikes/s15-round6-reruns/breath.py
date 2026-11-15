import sys, json, math, importlib.util
import numpy as np
from multiprocessing import Pool
spec = importlib.util.spec_from_file_location("sim", "/home/user/folk-instruments/research/spikes/s12-reed-similarity-scaling/similarity.py")
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
rho, c0, alpha = sim.rho, sim.c0, sim.alpha
R = 4; C = 110; FS = 48000; TAU = 0.015
def runb(f, b, T=1.6):
    p = sim.reed(f/444); m = math.ceil(C*f/(R*FS)); fb = R*FS; dt = 1/(fb*m)
    xt, St = sim.table(p); w0 = 2*np.pi*p["f"]; mu = p["Sr"]*w0*w0/p["K"]; lo, hi, M = xt[0], xt[-1], len(xt)-1
    x, v, p1, u = p["x0"], 0.0, 0.0, 0.0; bs = 0.0; a = 1-math.exp(-1/(fb*TAU))
    n = int(T*fb); xs = np.empty(n); us = np.empty(n)
    for i in range(n):
        bs += a*(b-bs); P0 = 1250*bs**1.5          # smoothing updated per base-rate sample
        for _ in range(m):
            d = P0 - p1; u0 = alpha*p["Ain"]*math.copysign(math.sqrt(2*abs(d)/rho), d)
            t = (x-lo)/(hi-lo)*M; t = 0.0 if t < 0 else (M-1e-9 if t >= M else t); j = int(t); Su = St[j]+(St[j+1]-St[j])*(t-j)
            vj = (u+p["Sr"]*v)/(alpha*Su); p2 = 0.5*rho*vj*abs(vj)
            p1 += dt*rho*c0*c0/p["V1"]*(u0-u); u += dt*p["S2"]/(rho*p["L2"])*(p1-p2)
            v += dt*(-w0/p["Q"]*v - w0*w0*(x-p["x0"]) - mu*p2); x += dt*v
            if not math.isfinite(x) or abs(x) > 1.0: return p, None, fb
        xs[i] = x; us[i] = u
    return p, (xs, us), fb
def job(a):
    f, b = a; p, r, fb = runb(f, b)
    out = dict(f=round(f,2), b=b, p0_final=round(1250*b**1.5,1))
    if r is None: out["state"] = "diverged"; return out
    xs, us = r; du = np.diff(us)*fb
    seg = du[int(0.6*fb):int(1.6*fb)-1]; out["dudt_rms"] = float(np.sqrt(np.mean(seg**2)))
    out["level_db"] = round(20*math.log10(out["dudt_rms"]+1e-300), 2)
    q = du[int(0.5*fb):int(1.5*fb)]; out["rms_0.5_1.5_db"] = round(20*math.log10(np.sqrt(np.mean(q**2))+1e-300), 1)
    out["amp_over_x0_tail"] = round(float((xs[int(1.2*fb):].max()-xs[int(1.2*fb):].min())/2/p["x0"]), 4)
    an = sim.analyse(p, (xs, us), fb); out["state"] = an["state"]; out["cents"] = an.get("cents")
    # onset: 10 ms rms windows, 1 ms hop
    w = int(0.010*fb); h = int(0.001*fb); env = np.array([np.sqrt(np.mean(du[k:k+w]**2)) for k in range(0, int(0.8*fb), h)])
    st = np.sqrt(np.mean(du[int(0.8*fb):int(1.4*fb)]**2)); idx = np.argmax(env >= 0.5*st) if (env >= 0.5*st).any() else -1
    out["half_level_time_s"] = None if idx < 0 else round(idx*0.001 + 0.005, 4)
    return out
if __name__ == "__main__":
    fr = lambda mi: 440*2**((mi-69)/12)
    jobs = [(fr(mi), b) for mi in (28, 100) for b in (0.02, 0.08, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0)] + [(440.0, b) for b in (0.02, 0.08, 0.25, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.85, 1.0)]
    with Pool(4) as pl:
        for o in pl.imap(job, jobs): print(json.dumps(o), flush=True)
