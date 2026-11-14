"""Spike S04: two strings of a course coupled through a shared bridge, one partial at a time (Weinreich 1977;
Woodhouse 2021 eq. (1)). Complex modal amplitudes a = (a1, a2), da/dt = i*Omega*a,
Omega = [[w1*(1+i*eta1/2)+z, z], [z, w2*(1+i*eta2/2)+z]],  z = i*2*f1*Y/Y0  (Y bridge admittance, Y0 string wave admittance),
so one string alone decays with loss factor eta_i + eta_b, eta_b = 2*Re(Y)/(pi*n*Y0).
Bridge force is proportional to a1 + a2. Checks: (1) unison, both plucked equally -> single fast decay (2*eta_b + eta_i);
(2) unison, one string plucked -> two-stage decay: fast rate then slow intrinsic rate; (3) detuned, weak coupling -> beats at |f1-f2|."""
import numpy as np, json
def modes(f1, cents, eta_i, etab, n=1):
    w1 = 2*np.pi*f1*n; w2 = w1*2**(cents/1200)
    z = 1j*etab*w1/2           # purely resistive bridge: z = i*eta_b*w/2
    Om = np.array([[w1*(1+1j*eta_i/2)+z, z],[z, w2*(1+1j*eta_i/2)+z]])
    lam, V = np.linalg.eig(Om); return lam, V
def envelope(f1, cents, eta_i, etab, a0, T=3.0, fs=2000):
    lam, V = modes(f1, cents, eta_i, etab); c = np.linalg.solve(V, np.array(a0, complex))
    t = np.arange(int(T*fs))/fs
    a = (V[:, :, None]*(c[:, None]*np.exp(1j*lam[:, None]*t))[None, :, :]).sum(1)
    return t, np.abs(a[0]+a[1])
def rate(t, e, t0, t1):  # dB/s
    m = (t >= t0) & (t < t1); return float(np.polyfit(t[m], 20*np.log10(e[m]+1e-300), 1)[0])
f1, eta_i, etab = 660.0, 2e-4, 2e-3
out = {}
single = -20*np.log10(np.e)*2*np.pi*f1*(eta_i+etab)/2
t, e = envelope(f1, 0, eta_i, etab, [1, 1]); out["unison_both"] = dict(rate_dB_s=rate(t, e, 0, 0.3), expected=-20*np.log10(np.e)*2*np.pi*f1*(eta_i+2*etab)/2)
t, e = envelope(f1, 0, eta_i, etab, [1, 0]); out["unison_one"] = dict(early=rate(t, e, 0, 0.1), late=rate(t, e, 1.5, 2.5), expected_late=-20*np.log10(np.e)*2*np.pi*f1*eta_i/2, single_string=single)
for cents in (2, 8):
    t, e = envelope(f1, cents, eta_i, etab/20, [1, 1], T=4, fs=4000)
    d = e/np.exp(np.polyval(np.polyfit(t, np.log(e+1e-300), 1), t)) - 1; X = np.abs(np.fft.rfft(d*np.hanning(len(d)))); k = X[2:].argmax()+2
    out[f"detuned_{cents}c_weak"] = dict(beat_Hz=float(k*4000/len(d)), expected=float(f1*(2**(cents/1200)-1)))
lam, _ = modes(f1, 3, eta_i, etab); out["3c_strong_coupling_mode_split_Hz"] = float(abs(lam[0].real-lam[1].real)/2/np.pi); out["3c_uncoupled_split_Hz"] = float(f1*(2**(3/1200)-1))
print(json.dumps(out, indent=1)); json.dump(out, open("output.json", "w"), indent=1)
# Added after the first run: with exact unison the antisymmetric mode exerts no bridge force, so no aftersound is heard
# in a one-polarisation model. The aftersound needs a slight mistuning (Weinreich). Check a 1-cent mistuning.
out2 = {}
for cents, a0 in ((1.0, [1, 0]), (1.0, [1, 0.7]), (0.3, [1, 0])):
    t, e = envelope(f1, cents, eta_i, etab, a0, T=6, fs=2000)
    out2[f"mistuned_{cents}c_a0_{a0}"] = dict(early_dB_s=rate(t, e, 0, 0.08), late_dB_s=rate(t, e, 3, 5), level_at_knee_dB=float(20*np.log10(e[int(1.0*2000)]/e[0])))
out2["reference_rates_dB_s"] = dict(symmetric=out["unison_both"]["expected"], intrinsic=out["unison_one"]["expected_late"], single=out["unison_one"]["single_string"])
print(json.dumps(out2, indent=1)); out.update(out2); json.dump(out, open("output.json", "w"), indent=1)
