"""Adversarial re-run of S03c with scaled reeds. Same equations as reed_sim.py / pressure_driven.py,
but all reed parameters are arguments. Cantilever scaling: f ~ e/L^2, K ~ W e^3/L^3, M ~ W e L, x0 ~ L."""
import numpy as np, json, sys
rho, c0, alpha = 1.2, 343.0, 0.61
b = 1.875104; s = np.linspace(0, 1, 201)
sig = (np.cosh(b)+np.cos(b))/(np.sinh(b)+np.sin(b))
psi = (np.cosh(b*s)-np.cos(b*s)) - sig*(np.sinh(b*s)-np.sin(b*s)); psi /= psi[-1]
def make(kL=1., ke=1., kW=1., kf=1., kV=1., kAin=1., Q=95., hmin=50e-6, es=900e-6, kx0=None, kL2S2=1., K_override=None):
    Lr, Wr, er = 12.95e-3*kL, 2.1e-3*kW, 110e-6*ke
    x0 = 528e-6*(kL if kx0 is None else kx0); fr = 444.0*kf
    K = 47.9*kW*ke**3/kL**3 if K_override is None else K_override; w0 = 2*np.pi*fr; M = K/w0**2
    Sr = Wr*Lr*np.trapezoid(psi, s); mu = Sr/M
    xt = np.linspace(-12e-3*kL, 12e-3*kL, 6001)
    def Su_exact(x):
        d = x*psi; h = np.where(d > 0, d, np.where(d < -(es+er), -(d+es+er), 0.0))
        return Wr*np.hypot(h[-1], hmin) + 2*Lr*np.trapezoid(np.hypot(h, hmin), s)
    Sut = np.array([Su_exact(x) for x in xt])
    S1, L1, L2, S2 = 800e-6, 0.06, 20e-3*kL2S2, 25e-6
    V1 = S1*L1*kV
    return dict(Lr=Lr, Wr=Wr, er=er, x0=x0, fr=fr, K=K, M=M, w0=w0, Sr=Sr, mu=mu, xt=xt, Sut=Sut, V1=V1, L2=L2, S2=S2,
                Ain=30e-6*kAin, Q=Q, es=es, cond=V1*L2*w0**2/(c0**2*S2))
def run(P, p0, fs=48000*4, T=1.0, ramp=0.02):
    import os; fs = int(os.environ.get('FS', fs))
    dt = 1/fs; n = int(T*fs); x, v, p1, u = P['x0'], 0., 0., 0.
    xs = np.empty(n); us = np.empty(n)
    xt, Sut = P['xt'], P['Sut']; Sr, w0, Q, mu = P['Sr'], P['w0'], P['Q'], P['mu']
    k1 = dt*rho*c0**2/P['V1']; k2 = dt*P['S2']/(rho*P['L2']); aA = alpha*P['Ain']
    for i in range(n):
        pr = p0*min(1.0, i*dt/ramp); d = pr - p1
        u0 = aA*np.sign(d)*np.sqrt(2*abs(d)/rho)
        vj = (u + Sr*v)/(alpha*np.interp(x, xt, Sut)); p2 = 0.5*rho*vj*abs(vj)
        p1 += k1*(u0 - u); u += k2*(p1 - p2)
        v += dt*(-w0/Q*v - w0**2*(x - P['x0']) - mu*p2); x += dt*v
        xs[i], us[i] = x, u
        if not np.isfinite(x) or abs(x) > 1: return xs[:i+1], us[:i+1], fs, True
    return xs, us, fs, False
def analyse(P, xs, us, fs, blew):
    if blew: return dict(blew_up=True)
    m = slice(int(0.6*len(xs)), None); xx = xs[m]-xs[m].mean(); amp = (xs[m].max()-xs[m].min())/2
    res = dict(blew_up=False, tip_amp_um=round(amp*1e6, 1), x_mean_um=round(float(xs[m].mean())*1e6, 1),
               x_min_um=round(float(xs[m].min())*1e6,1), x_max_um=round(float(xs[m].max())*1e6,1))
    if amp < 5e-6*P['Lr']/12.95e-3: res['oscillates'] = False; return res
    w = np.hanning(len(xx)); X = np.abs(np.fft.rfft(xx*w)); k = X[5:].argmax()+5
    a_, b_, c_ = np.log(X[k-1:k+2]); f0 = (k + 0.5*(a_-c_)/(a_-2*b_+c_))*fs/len(xx)
    seg = us[m]-us[m].mean(); U = np.abs(np.fft.rfft(seg*w)); H = []
    for h in (1, 2, 3):
        kk = int(round(h*f0*len(xx)/fs)); H.append(U[kk-3:kk+4].max())
    res.update(oscillates=True, f0=round(float(f0), 2), cents=round(1200*np.log2(f0/P['fr']), 1),
               u_h2_dB=round(20*np.log10(H[1]/H[0]), 1), through_plate=bool(xs[m].min() < -(P['es']+P['er'])),
               table_edge_hit=bool(xs[m].max() > P['xt'][-1] or xs[m].min() < P['xt'][0]))
    return res
CASES = {
 'ref_A4_444':        dict(),
 'high_3520_reed_only': dict(kf=3520/444, kL=0.45, ke=(3520/444)*0.45**2, kW=0.85),
 'high_3520_reed+cell': dict(kf=3520/444, kL=0.45, ke=(3520/444)*0.45**2, kW=0.85, kV=0.25, kAin=0.4),
 'low_111_reed_only':   dict(kf=0.25, kL=2.0, ke=1.0, kW=1.4),
 'low_111_reed+cell_V4': dict(kf=0.25, kL=2.0, ke=1.0, kW=1.4, kV=4, kAin=2.8),
 'low_111_reed+cell_V16': dict(kf=0.25, kL=2.0, ke=1.0, kW=1.4, kV=16, kAin=2.8),
 'low_111_reed+cell_V4_L2x4': dict(kf=0.25, kL=2.0, ke=1.0, kW=1.4, kV=4, kAin=2.8, kL2S2=4),
}
if __name__ == '__main__':
    out = {}
    names = sys.argv[1:] or list(CASES)
    for name in names:
        P = make(**CASES[name]); out[name] = dict(params=CASES[name], fr=P['fr'], K=round(P['K'],2), x0_um=round(P['x0']*1e6,1),
              Lr_mm=round(P['Lr']*1e3,2), e_um=round(P['er']*1e6,1), cond_ratio=round(float(P['cond']),3), runs={})
        for p0 in (50, 100, 400, 1500, 3000):
            a = analyse(P, *run(P, p0)); out[name]['runs'][p0] = a
            print(name, p0, a, flush=True)
    json.dump(out, open('/tmp/claude-0/-home-user/33848ac0-9924-5fbc-b8d6-b9a90c833f8d/scratchpad/adv4/scaled_out_%s.json' % ('all' if not sys.argv[1:] else sys.argv[1]), 'w'), indent=1)
