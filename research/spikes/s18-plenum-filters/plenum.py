"""Spike S18: (1) the melodion's shared breath (D-041) with several similarity-scaled reeds (S12) drawing from one plenum,
in two breath modes; (2) the body, cassotto and sordina filters of D-032 and D-040 applied to a reed's source signal
(du/dt at 48 kHz), measured as the frozen tests T-122 and T-134 measure them."""
import sys, json, numpy as np
sys.path.insert(0, "../s12-reed-similarity-scaling"); sys.path.insert(0, "../../../tests/py")
import similarity as s, metrics as m
from scipy.signal import sosfilt, resample_poly
rho, c0, alpha = 1.2, 343.0, 0.61
def hz(n): return 440 * 2 ** ((n - 69) / 12)
def run_chord(notes, p0, mode, A_m=120e-6, Vp=200e-6, fs=48000 * 8, T=1.0):
    P = [s.reed(hz(n) * 2 ** (23.1 / 1200) / 444.0) for n in notes]          # natural frequency set 23 cents above the target
    tabs = [s.table(q) for q in P]; N = len(P); dt = 1 / fs; n = int(T * fs)
    x = np.array([q["x0"] for q in P]); v = np.zeros(N); p1 = np.zeros(N); u = np.zeros(N); pp = 0.0
    w0 = np.array([2 * np.pi * q["f"] for q in P]); K = np.array([q["K"] for q in P]); Sr = np.array([q["Sr"] for q in P]); mu = Sr * w0 * w0 / K
    V1 = np.array([q["V1"] for q in P]); Ain = np.array([q["Ain"] for q in P]); x0 = x.copy(); Q = 95.0; S2, L2 = s.REF["S2"], s.REF["L2"]
    us = np.zeros((n, N)); ramp = 0.02
    for i in range(n):
        src = p0 * min(1.0, i * dt / ramp)
        if mode == 0: pp = src
        dI = pp - p1; u0 = alpha * Ain * np.sign(dI) * np.sqrt(2 * np.abs(dI) / rho)
        if mode == 1:
            dm = src - pp; ub = alpha * A_m * np.sign(dm) * np.sqrt(2 * abs(dm) / rho); pp += dt * rho * c0 * c0 / Vp * (ub - u0.sum())
        Su = np.array([np.interp(x[k], tabs[k][0], tabs[k][1]) for k in range(N)])
        vj = (u + Sr * v) / (alpha * Su); p2 = 0.5 * rho * vj * np.abs(vj)
        p1 += dt * rho * c0 * c0 / V1 * (u0 - u); u += dt * S2 / (rho * L2) * (p1 - p2)
        v += dt * (-w0 / Q * v - w0 * w0 * (x - x0) - mu * p2); x += dt * v; us[i] = u
    return us, fs, pp
def dudt_48k(u, fs): d = np.diff(u, prepend=u[0]) * fs; return resample_poly(d, 1, fs // 48000)
def shelf(f0, gain_db, sr, high=True, S=1.0):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2); c = np.cos(w)
    if high: b = [A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al)]; a = [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al]
    return np.array([b + a]) / a[0] if False else np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])
def peak(f0, gain_db, Q, sr):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / (2 * Q); c = np.cos(w)
    b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]; return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])
if __name__ == "__main__":
    out = {}
    for mode in (0, 1):
        lv = []
        for notes in ([69], [69, 60, 64, 67], [69, 60, 62, 64, 65, 67, 71, 72]):
            us, fs, pp = run_chord(notes, 1250 * 0.7 ** 1.5, mode)
            y = dudt_48k(us[:, 0], fs); seg = y[int(0.6 * 48000):int(0.95 * 48000)]
            lv.append(round(float(m.peak_near(seg, 48000, 440.0, 25)[1]), 2)); out.setdefault(f"mode{mode}_plenum_Pa", []).append(round(float(pp), 1))
            print(mode, notes[:3], lv[-1], round(float(pp), 1), flush=True)
        out[f"mode{mode}_A4_level_dB"] = lv
    us, fs, _ = run_chord([69], 1250 * 0.6 ** 1.5, 0, T=1.2); y = dudt_48k(us[:, 0], fs)[int(0.6 * 48000):int(1.1 * 48000)]; sr = 48000
    c0_ = m.spectral_centroid(y, sr)
    rel = lambda z: m.band_energy_db(z, sr, 2000, 10000) - m.band_energy_db(z, sr, 20, 20000)
    out["melodion_centroid_plastic"] = c0_
    out["wood_-5dB_shelf_2k_ratio"] = m.spectral_centroid(sosfilt(shelf(2000, -5, sr), y), sr) / c0_
    out["metal_+3dB_shelf_3k_ratio"] = m.spectral_centroid(sosfilt(shelf(3000, 3, sr), y), sr) / c0_
    cas = np.vstack([peak(700, 3, 0.9, sr), shelf(1600, -9, sr)]); out["cassotto_rel_2_10k_change_dB"] = rel(sosfilt(cas, y)) - rel(y)
    out["sordina_rel_2_10k_change_dB"] = rel(sosfilt(shelf(1200, -8, sr), y)) - rel(y)
    out["harmonics_within_60dB"] = m.harmonic_count_above(y, sr, 440.0, -60.0, 20)
    print(json.dumps(out, indent=1)); json.dump(out, open("output.json", "w"), indent=1)
