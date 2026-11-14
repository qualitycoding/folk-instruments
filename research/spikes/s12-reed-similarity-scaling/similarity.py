"""Spike S12: similarity scaling of the pressure-driven reed model. Round 4 showed that scaling the reference reed like a
real cantilever (or by the first laws of D-012) fails away from 444 Hz. Writing the model in the dimensionless variables
xi = x/x0 and tau = w0*t shows that its behaviour at a given pressure is unchanged if, for a frequency factor k = f/444:
  x0, hmin, er, es  ~ 1/k   (all heights)        Sr ~ 1/k (effective pumping area)     K, Q, Lr, Wr unchanged
  A_in ~ 1/k                V1 ~ 1/k^2           S2/L2 unchanged
(groups: Sr*P/(K*x0); Sr*w0/(alpha*Lp*sqrt(2P/rho)); rho*c0^2*U/(V1*w0*P); S2*P/(rho*L2*w0*U); A_in/(x0*Lp), U ~ x0*Lp).
Check: pitch offset in cents, onset and harmonic content at k = 1/8 .. 12 for several pressures, at 4x and 8x 48 kHz."""
import json, sys, numpy as np
rho, c0, alpha, b = 1.2, 343.0, 0.61, 1.875104
s = np.linspace(0, 1, 201); sig = (np.cosh(b)+np.cos(b))/(np.sinh(b)+np.sin(b))
psi = (np.cosh(b*s)-np.cos(b*s)) - sig*(np.sinh(b*s)-np.sin(b*s)); psi /= psi[-1]; IPSI = float(np.trapezoid(psi, s))
REF = dict(Lr=12.95e-3, Wr=2.1e-3, er=110e-6, es=900e-6, hmin=50e-6, x0=528e-6, K=47.9, Q=95.0, S2=25e-6, L2=20e-3, V1=800e-6*0.06, Ain=30e-6, f=444.0)
def reed(k):
    p = dict(REF); p.update(er=REF["er"]/k, es=REF["es"]/k, hmin=REF["hmin"]/k, x0=REF["x0"]/k, V1=REF["V1"]/k**2, Ain=REF["Ain"]/k, f=REF["f"]*k)
    p["Sr"] = REF["Wr"]*REF["Lr"]*IPSI/k; return p
def table(p, n=2048):
    xt = np.linspace(-6*p["x0"]-p["es"]-p["er"], 6*p["x0"], n); out = np.empty(n)
    for i, x in enumerate(xt):
        d = x*psi; h = np.where(d > 0, d, np.where(d < -(p["es"]+p["er"]), -(d+p["es"]+p["er"]), 0.0))
        out[i] = p["Wr"]*np.hypot(h[-1], p["hmin"]) + 2*p["Lr"]*np.trapezoid(np.hypot(h, p["hmin"]), s)
    return xt, out
def run(p, p0, fs, T, ramp_periods=9):
    xt, St = table(p); w0 = 2*np.pi*p["f"]; mu = p["Sr"]*w0*w0/p["K"]; dt = 1/fs; n = int(T*fs); ramp = ramp_periods/p["f"]
    x, v, p1, u = p["x0"], 0.0, 0.0, 0.0; xs = np.empty(n); us = np.empty(n); lo, hi, m = xt[0], xt[-1], len(xt)-1
    for i in range(n):
        d = p0*min(1.0, i*dt/ramp) - p1; u0 = alpha*p["Ain"]*np.sign(d)*np.sqrt(2*abs(d)/rho)
        t = (x-lo)/(hi-lo)*m; t = 0.0 if t < 0 else (m-1e-9 if t >= m else t); j = int(t); Su = St[j] + (St[j+1]-St[j])*(t-j)
        vj = (u + p["Sr"]*v)/(alpha*Su); p2 = 0.5*rho*vj*abs(vj)
        p1 += dt*rho*c0*c0/p["V1"]*(u0-u); u += dt*p["S2"]/(rho*p["L2"])*(p1-p2)
        v += dt*(-w0/p["Q"]*v - w0*w0*(x-p["x0"]) - mu*p2); x += dt*v
        if not np.isfinite(x) or abs(x) > 1.0: return None
        xs[i] = x; us[i] = u
    return xs, us
def analyse(p, r, fs):
    if r is None: return dict(state="diverged")
    xs, us = r; m = slice(int(0.7*len(xs)), None); amp = (xs[m].max()-xs[m].min())/2/p["x0"]
    if amp < 0.02: return dict(state="silent", amp_over_x0=round(float(amp), 4))
    xx = xs[m]-xs[m].mean(); w = np.hanning(len(xx)); X = np.abs(np.fft.rfft(xx*w, 4*len(xx))); k0 = int(0.5*p["f"]*4*len(xx)/fs)
    k = k0 + X[k0:].argmax(); a_, b_, c_ = np.log(X[k-1:k+2]); f0 = (k + 0.5*(a_-c_)/(a_-2*b_+c_))*fs/(4*len(xx))
    U = np.abs(np.fft.rfft((us[m]-us[m].mean())*w, 4*len(xx))); H = [U[int(round(h*f0*4*len(xx)/fs))-6:int(round(h*f0*4*len(xx)/fs))+7].max() for h in (1, 2, 3)]
    return dict(state="sounds", cents=round(float(1200*np.log2(f0/p["f"])), 2), amp_over_x0=round(float(amp), 3), h2_dB=round(float(20*np.log10(H[1]/H[0])), 1), h3_dB=round(float(20*np.log10(H[2]/H[0])), 1))
if __name__ == "__main__":
    out = []
    for k in (0.125, 0.25, 1.0, 4.0, 8.0, 12.0):
        p = reed(k)
        for mult in (4, 8):
            fs = 48000*mult
            for p0 in (50, 100, 400, 1500):
                a = analyse(p, run(p, p0, fs, T=450/p["f"]), fs); a.update(k=k, f=p["f"], oversampling=mult, p0=p0); out.append(a)
                print(json.dumps(a), flush=True)
    json.dump(out, open("output.json", "w"), indent=1)
