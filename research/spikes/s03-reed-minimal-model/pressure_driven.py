"""Spike S03c: the plan drives reeds from a pressure (bellows, mouth, plenum), not from a fixed flow. Replace the fixed
supply flow u0 by an inlet orifice between a pressure reservoir p0 and the reed cell V1:
u0 = alpha*A_in*sign(p0-p1)*sqrt(2|p0-p1|/rho). Sweep p0; also check 4x instead of 8x oversampling of 44.1 kHz."""
import json, sys, numpy as np, reed_sim as r
def run(p0, A_in=30e-6, L1=0.06, T=1.0, fs=44100*8, ramp=0.02):
    dt = 1/fs; n = int(T*fs); V1 = r.S1*L1
    x, v, p1, u = r.x0, 0.0, 0.0, 0.0
    xs = np.empty(n); us = np.empty(n); ps = np.empty(n)
    for i in range(n):
        pr = p0*min(1.0, i*dt/ramp); d = pr - p1
        u0 = r.alpha*A_in*np.sign(d)*np.sqrt(2*abs(d)/r.rho)
        vj = (u + r.Sr*v)/(r.alpha*r.Su(x)); p2 = 0.5*r.rho*vj*abs(vj)
        p1 += dt*r.rho*r.c0**2/V1*(u0 - u); u += dt*r.S2/(r.rho*r.L2)*(p1 - p2)
        v += dt*(-r.w0/r.Q*v - r.w0**2*(x - r.x0) - r.mu*p2); x += dt*v
        xs[i], us[i], ps[i] = x, u, p2
    return xs, us, ps, fs
out = []
for fs_mult in (8, 4):
    for p0 in (50, 100, 200, 400, 800, 1500, 3000):
        a = r.analyse(*run(p0, fs=44100*fs_mult)); a.update(p0_Pa=p0, oversampling=fs_mult); out.append(a)
        print(fs_mult, p0, a["oscillates"], a.get("f0_Hz"), a.get("cents_re_fr"), a["tip_amplitude_um"], (a.get("flow_harmonics_dB") or [])[1:4], flush=True)
json.dump(out, open("pressure_driven_output.json", "w"), indent=1)
