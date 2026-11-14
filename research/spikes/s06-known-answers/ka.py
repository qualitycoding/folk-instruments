"""Spike S06: independent known-answer values for the frozen C++ formula tests (tests/cpp/test_strings.cpp)."""
import numpy as np, json
E_, rho = 200e9, 7850.0
d = 0.015*0.0254; L = 0.3524; f0 = 440.0
mu = rho*np.pi*d*d/4; T = mu*(2*L*f0)**2; B = np.pi**3*E_*d**4/(64*T*L*L)
out = dict(mu=mu, T=T, B=B, partial10=10*f0*np.sqrt(1+B*100))
def eta_air(d, rho_s, f, ra=1.2, nu=1.5e-5):
    M = d/4*np.sqrt(2*np.pi*f/nu); return ra/rho_s*(2*np.sqrt(2)*M+1)/M**2
def eta_bend(E, d, rho_s, L, f1, n, etaE): return E*np.pi**2*d*d*n*n*etaE/(64*rho_s*L**4*f1**2 + E*np.pi**2*d*d*n*n)
out["eta_air_440"] = eta_air(d, rho, 440.0); out["eta_air_4400"] = eta_air(d, rho, 4400.0)
out["eta_bend_n1"] = eta_bend(E_, d, rho, L, f0, 1, 1e-3); out["eta_bend_n20"] = eta_bend(E_, d, rho, L, f0, 20, 1e-3)
Y0 = 1/np.sqrt(T*mu); out["Y0"] = Y0; out["eta_bridge_n1_G1e-4"] = 2*1e-4/(np.pi*1*Y0)
def pair(w1, w2, e1, e2, yr, fref):
    z = 1j*2*fref*yr; Om = np.array([[w1*(1+1j*e1/2)+z, z],[z, w2*(1+1j*e2/2)+z]]); lam, V = np.linalg.eig(Om)
    o = np.argsort(-lam.imag); return lam[o], V[:, o]
w = 2*np.pi*660.0
lam, V = pair(w, w, 2e-4, 2e-4, 1e-3*np.pi, 660.0)   # z = i*2*660*pi*1e-3 = i*eta_b*w/2 with eta_b = 2e-3
out["pair_unison"] = dict(fast=[lam[0].real, lam[0].imag], slow=[lam[1].real, lam[1].imag], fast_shape_abs=[abs(V[0,0]), abs(V[1,0])])
w2 = w*2**(4/1200)
lam, V = pair(w, w2, 2e-4, 2e-4, 1e-5*np.pi, 660.0)
out["pair_4c_weak"] = dict(split_hz=abs(lam[0].real-lam[1].real)/(2*np.pi), expected_uncoupled=660*(2**(4/1200)-1), im=[lam[0].imag, lam[1].imag])
print(json.dumps(out, indent=1)); json.dump(out, open(__file__.replace("ka.py", "output.json"), "w"), indent=1)
