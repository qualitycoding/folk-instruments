"""Spike S03: does the minimal free-reed model (reed ODE + Bernoulli jet + pumped flow + upstream volume and
inertance; Millot & Baumann 2007, arXiv:2401.01606, sections 2 and 3.1, Tables 2 and 3) self-oscillate when
integrated with a simple explicit scheme, and how do pitch, level and harmonic content depend on the supply flow?
Useful section: Debut/Millot form (front + two sides, zero local opening while the reed is inside the plate).
Coordinate x: height of the reed's lower face at the tip above the plate's upper face (upstream side positive).
A (-,+) reed is pushed towards and through the plate by upstream over-pressure."""
import numpy as np, json, sys
rho, c0, alpha = 1.2, 343.0, 0.61
Lr, Wr, er, es, hmin = 12.95e-3, 2.1e-3, 110e-6, 900e-6, 50e-6
x0, fr, K, Q = 528e-6, 444.0, 47.9, 95.0
S0, S1, L2, S2 = 30e-6, 800e-6, 20e-3, 25e-6
w0 = 2*np.pi*fr; M = K/w0**2
s = np.linspace(0, 1, 201); b = 1.875104
sig = (np.cosh(b)+np.cos(b))/(np.sinh(b)+np.sin(b))
psi = (np.cosh(b*s)-np.cos(b*s)) - sig*(np.sinh(b*s)-np.sin(b*s)); psi /= psi[-1]
Sr = Wr*Lr*np.trapezoid(psi, s); mu = Sr/M
def Su_exact(x):
    d = (x - x0)*psi + x0*psi  # local height of lower face: rest shape is also first-mode shaped => x*psi
    h = np.where(d > 0, d, np.where(d < -(es+er), -(d+es+er), 0.0))
    return Wr*np.hypot(h[-1], hmin) + 2*Lr*np.trapezoid(np.hypot(h, hmin), s)
xt = np.linspace(-4e-3, 4e-3, 4001); Sut = np.array([Su_exact(x) for x in xt])
def Su(x): return np.interp(x, xt, Sut)
def run(v0, L1=0.06, T=1.2, fs=44100*8, ramp=0.05):
    dt = 1/fs; n = int(T*fs); V1 = S1*L1
    x, v, p1, u = x0, 0.0, 0.0, 0.0
    xs = np.empty(n); us = np.empty(n); ps = np.empty(n)
    for i in range(n):
        u0 = S0*v0*min(1.0, i*dt/ramp)
        up = -Sr*v                       # reed moving down pumps air downstream
        vj = (u - up)/(alpha*Su(x))
        p2 = 0.5*rho*vj*abs(vj)
        # semi-implicit Euler
        p1 += dt*rho*c0*c0/V1*(u0 - u)
        u  += dt*S2/(rho*L2)*(p1 - p2)
        a = -w0/Q*v - w0*w0*(x - x0) - mu*p2
        v += dt*a; x += dt*v
        xs[i], us[i], ps[i] = x, u, p2
    return xs, us, ps, fs
def analyse(xs, us, ps, fs):
    m = slice(int(0.7*len(xs)), None); seg = us[m] - us[m].mean(); xx = xs[m] - xs[m].mean()
    amp = (xs[m].max()-xs[m].min())/2
    if amp < 5e-6: return dict(oscillates=False, tip_amplitude_um=round(amp*1e6,2), mean_p2_Pa=round(float(ps[m].mean()),1))
    w = np.hanning(len(xx)); X = np.abs(np.fft.rfft(xx*w)); k = X[5:].argmax()+5
    a_, b_, c_ = np.log(X[k-1:k+2]); f0 = (k + 0.5*(a_-c_)/(a_-2*b_+c_))*fs/len(xx)
    U = np.abs(np.fft.rfft(seg*w)); H = []
    for h in range(1, 13):
        kk = int(round(h*f0*len(xx)/fs)); H.append(U[kk-3:kk+4].max())
    H = 20*np.log10(np.array(H)/H[0]+1e-12)
    X2 = []
    for h in range(1, 4):
        kk = int(round(h*f0*len(xx)/fs)); X2.append(X[kk-3:kk+4].max())
    return dict(oscillates=True, f0_Hz=round(float(f0),2), cents_re_fr=round(1200*np.log2(f0/fr),1), tip_amplitude_um=round(amp*1e6,1),
                mean_p2_Pa=round(float(ps[m].mean()),1), flow_harmonics_dB=[round(float(h),1) for h in H],
                reed_h2_dB=round(float(20*np.log10(X2[1]/X2[0])),1), reed_h3_dB=round(float(20*np.log10(X2[2]/X2[0])),1),
                goes_through_plate=bool(xs[m].min() < -(es+er)))
if __name__ == "__main__":
    out = {"Sr_mm2": Sr*1e6, "mu": mu, "Su_rest_mm2": float(Su(x0))*1e6, "Su_min_mm2": float(Sut.min())*1e6, "runs": []}
    for v0 in [float(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 6, 8, 12]:
        r = analyse(*run(v0)); r["v0_m_per_s"] = v0; out["runs"].append(r); print(json.dumps(r), flush=True)
    json.dump(out, open("output.json", "w"), indent=1)
