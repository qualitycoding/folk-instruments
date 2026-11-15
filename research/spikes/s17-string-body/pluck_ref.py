"""Spike S17: reference implementation of the plucked-string engine as decided in D-060 to D-064 (after cold read 1).
It is the reference the C++ engine of step S-240 must reproduce, in the way spike S12 is for the reeds.
One course, one note: partials of each string, greedy pairing, a complex bridge admittance from the body modes with a
cap on the bridge loss, pitch compensation, exact 2x2 matrix-exponential steps, body modes driven by the bridge force,
a direct path, and the output gain. Run as a script to check the frozen tests it affects (pitch, double decay, body)."""
import numpy as np, json, sys
E_, RHO = 200e9, 7850.0
ETA_B_CAP = 8e-3
def hz(m, a4=440.0): return a4 * 2 ** ((m - 69) / 12)
def eta_air(d, f): M = d / 4 * np.sqrt(2 * np.pi * f / 1.5e-5); return 1.2 / RHO * (2 * np.sqrt(2) * M + 1) / M ** 2
def eta_bend(d, L, f1, n, etaE): return E_ * np.pi ** 2 * d * d * n * n * etaE / (64 * RHO * L ** 4 * f1 ** 2 + E_ * np.pi ** 2 * d * d * n * n)
def Yhat(f, modes):
    """Normalised body admittance: sum_k g_k (i w/w_k) / (1 - (w/w_k)^2 + i w/(w_k Q_k))."""
    w = np.asarray(f, dtype=float)[..., None]; fk = np.array([m["hz"] for m in modes]); q = np.array([m["q"] for m in modes]); g = np.array([m["gain"] for m in modes])
    r = w / fk; return (g * (1j * r) / (1 - r * r + 1j * r / q)).sum(-1)
class String:
    def __init__(self, s, L, fret, target_hz, damping):
        """s: dict(midi, diameter_m (outer), core_m, wound, linear_density). target_hz: equal-tempered fretted pitch (with detune)."""
        self.mu = s["linear_density"]; self.T = self.mu * (2 * L * hz(s["midi"])) ** 2; self.Y0 = 1 / np.sqrt(self.T * self.mu)
        Lf = L / 2 ** (fret / 12); self.B = np.pi ** 3 * E_ * s["core_m"] ** 4 / (64 * self.T * Lf * Lf); self.f1 = target_hz
        n = np.arange(1, 81); f = target_hz * n * np.sqrt((1 + self.B * n * n) / (1 + self.B)); keep = f < 18000
        self.n, self.f = n[keep], f[keep]; etaE = 4e-3 if s["wound"] else 1e-3
        self.eta_i = eta_air(s["diameter_m"], self.f) + eta_bend(s["core_m"], Lf, target_hz, self.n, etaE) + damping * 2e-3
def pair_partials(a, b):
    """Greedy nearest-partner matching within 60 cents; ties go to the lower partial of a; each partial used once."""
    cand = []
    for i, fa in enumerate(a.f):
        j = int(np.argmin(np.abs(np.log2(b.f / fa)))); c = abs(1200 * np.log2(b.f[j] / fa))
        if c <= 60: cand.append((c, i, j))
    cand.sort(); used_a, used_b, pairs = set(), set(), []
    for c, i, j in cand:
        if i not in used_a and j not in used_b: pairs.append((i, j)); used_a.add(i); used_b.add(j)
    return pairs, used_a, used_b
def bridge_terms(st, idx, Y):
    """z = i * 2 * f1 * Y / Y0, with Y scaled so that eta_b = 2 Re(Y)/(pi n Y0) does not exceed the cap."""
    Yn = Y / st.Y0; eta_b = 2 * Yn.real / (np.pi * st.n[idx]); scale = np.where(eta_b > ETA_B_CAP, ETA_B_CAP / np.maximum(eta_b, 1e-30), 1.0)
    return 1j * 2 * st.f1 * Yn * scale
def render(courses_strings, L, fret, midi, vel, modes, coupling, Y_ref, sr=48000, dur=1.5, detune_c=1.5, beta=0.12, stiff=0.6, damping=0.3,
           course_mode=0, second_delay=True, out_gain=1.0, tap=None):
    n = int(dur * sr); t = np.arange(n) / sr; F = np.zeros(n)
    if tap is None:
        strs = courses_strings[:1] if course_mode == 1 else courses_strings
        S = []
        for j, s in enumerate(strs):
            target = hz(midi + (s["midi"] - courses_strings[0]["midi"])) * (2 ** (detune_c / 1200) if j == 1 and s["midi"] == courses_strings[0]["midi"] else 1.0)
            S.append(String(s, L, fret, target, damping))
        amp = [vel ** 1.5 * np.sin(st.n * np.pi * beta) / st.n * np.exp(-st.n * 0.15 * (1 - stiff)) * np.exp(-st.n * 0.1 * (1 - vel)) * (0.9 if j else 1.0) for j, st in enumerate(S)]
        delay = int(round(0.15e-3 * (1.5 - vel) * sr)) if (len(S) > 1 and second_delay) else 0
        Yfull = [coupling * Y_ref * Yhat(st.f, modes) for st in S]
        z = [bridge_terms(st, np.arange(len(st.n)), Yfull[j]) for j, st in enumerate(S)]
        w = [2 * np.pi * st.f for st in S]
        if len(S) == 2:
            pairs, ua, ub = pair_partials(S[0], S[1])
            for (i, k) in pairs:
                z12 = np.sqrt(z[0][i] * z[1][k])
                d1 = w[0][i] - z[0][i].real - z12.real; d2 = w[1][k] - z[1][k].real - z12.real    # pitch compensation
                Om = np.array([[d1 * (1 + 1j * S[0].eta_i[i] / 2) + z[0][i], z12], [z12, d2 * (1 + 1j * S[1].eta_i[k] / 2) + z[1][k]]])
                lam, V = np.linalg.eig(Om); a0 = np.array([amp[0][i], 0], complex); c = np.linalg.solve(V, a0)
                a1 = np.array([0, amp[1][k]], complex); c1 = np.linalg.solve(V, a1)
                for m in range(2):
                    F += np.real((V[0, m] + V[1, m]) * (c[m] * np.exp(1j * lam[m] * t)))
                    td = np.clip(t - delay / sr, 0, None); F += np.real((V[0, m] + V[1, m]) * (c1[m] * np.exp(1j * lam[m] * td))) * (t >= delay / sr)
            singles = [(0, i) for i in range(len(S[0].n)) if i not in ua] + [(1, k) for k in range(len(S[1].n)) if k not in ub]
        else:
            singles = [(0, i) for i in range(len(S[0].n))]
        for (j, i) in singles:
            d = w[j][i] - z[j][i].real; lam = d * (1 + 1j * S[j].eta_i[i] / 2) + z[j][i]
            td = t - (delay / sr if j == 1 else 0); F += np.real(amp[j][i] * np.exp(1j * lam * np.clip(td, 0, None))) * (td >= 0) * 0 + np.real(amp[j][i] * 1j * np.exp(1j * lam * np.clip(td, 0, None))).__neg__() * 0 + amp[j][i] * np.exp(-lam.imag * np.clip(td, 0, None)) * np.sin(lam.real * np.clip(td, 0, None)) * (td >= 0)
    else:
        F[0] = tap * sr / 1000.0
    # body: v_k'' + (w_k/Q_k) v_k' + w_k^2 v_k = g_k (w_k/Q_k) F'  (velocity of mode k; resonant gain g_k), bilinear transform
    out = np.zeros(n)
    for mo in modes:
        wk = 2 * np.pi * mo["hz"]; q = mo["q"]; g = mo["gain"]; K = 2 * sr
        b = np.array([g * wk / q * K, 0, -g * wk / q * K]); a = np.array([K * K + wk / q * K + wk * wk, 2 * (wk * wk - K * K), K * K - wk / q * K + wk * wk])
        from scipy.signal import lfilter
        out += lfilter(b / a[0], a / a[0], F)
    from scipy.signal import butter, sosfilt
    out += sosfilt(butter(2, 1500, "highpass", fs=sr, output="sos"), F)
    return out * out_gain, sr
def Y_ref_for(top_string, L, modes):
    st = String(top_string, L, 0, hz(top_string["midi"]), 0.3); Yh = Yhat(np.array([st.f1]), modes)[0]
    return 2e-3 * np.pi * 1 * st.Y0 / (2 * Yh.real) if Yh.real > 0 else 0.0
if __name__ == "__main__":
    sys.path.insert(0, "../../../tests/py"); import metrics as m
    def plain(midi, g): d = g * 0.0254; return dict(midi=midi, diameter_m=d, core_m=d, wound=False, linear_density=RHO * np.pi * d * d / 4)
    def wound(midi, g, L): d = g * 0.0254; return dict(midi=midi, diameter_m=d, core_m=0.4 * d, wound=True, linear_density=100.0 / (2 * L * hz(midi)) ** 2)
    L = 0.3524; C = [[wound(55, .040, L)] * 2, [wound(62, .026, L)] * 2, [plain(69, .015)] * 2, [plain(76, .011)] * 2]
    BODY = [dict(hz=f, q=30.0, gain=1 / (i + 1)) for i, f in enumerate([272, 313, 464, 570, 824, 886, 1117])]
    Yr = Y_ref_for(C[3][0], L, BODY); res = {"Y_ref": Yr}
    worst = 0; rows = []
    for ci, op in enumerate([55, 62, 69, 76]):
        for fret in (0, 1, 5, 7, 8, 12, 24):
            if ci < 3 and fret >= 7: continue
            midi = op + fret; x, sr = render(C[ci], L, fret, midi, 0.7, BODY, 1.0, Yr, detune_c=0)
            c = float(m.cents(m.peak_near(m.seg(x, sr, 0.05, 0.5), sr, hz(midi), 60)[0], hz(midi))); worst = max(worst, abs(c)); rows.append((midi, round(c, 2)))
    res["T154_like_pitch_cents"] = rows; res["worst_abs_cents"] = worst
    # without compensation, for comparison (single note on the 313 Hz mode: D#4 = 311 Hz on the D course, fret 1)
    BOW = [dict(hz=f, q=30.0, gain=1 / (i + 1)) for i, f in enumerate([200, 550, 740])]
    Lb = 0.330; Cb = [[wound(55, .038, Lb)] * 2, [wound(62, .024, Lb)] * 2, [plain(69, .014)] * 2, [plain(76, .010)] * 2]
    Yb = Y_ref_for(Cb[3][0], Lb, BOW)
    x, sr = render(Cb[3], Lb, 0, 76, 0.8, BOW, 1.0, Yb, dur=3.1)
    te, e = m.band_envelope_db(x, sr, hz(76)); early, late = m.decay_rate_db_per_s(te, e, 0.03, 0.25), m.decay_rate_db_per_s(te, e, 1.2, 2.5)
    x1, _ = render(Cb[3], Lb, 0, 76, 0.8, BOW, 1.0, Yb, dur=3.1, course_mode=1)
    te, e = m.band_envelope_db(x1, sr, hz(76)); e1, l1 = m.decay_rate_db_per_s(te, e, 0.03, 0.25), m.decay_rate_db_per_s(te, e, 1.2, 2.5)
    res["T144_pair_early_late"] = [early, late, early / late]; res["T144_single_early_late"] = [e1, l1, e1 / l1]
    x, sr = render(None, L, 0, 0, 0, BODY, 1.0, Yr, dur=1.0, tap=1.0)
    lv = [m.peak_near(m.seg(np.concatenate([np.zeros(4800), x])[:48000], sr, 0.05, 0.25), sr, f, 35)[1] for f in (272, 313, 464)]
    res["T146_levels"] = lv
    x, sr = render(C[3], L, 0, 76, 0.8, BODY, 0.02, Yr, dur=4.6, detune_c=4)
    t, e = m.band_envelope_db(m.seg(x, sr, 0.1, 4.5), sr, hz(76), frame_s=0.01); lin = 10 ** (e / 20); d = lin / np.exp(np.polyval(np.polyfit(t, np.log(lin + 1e-12), 1), t)) - 1
    sp = np.abs(np.fft.rfft(d * np.hanning(len(d)), 8 * len(d))); fr = np.arange(len(sp)) * 100 / (8 * len(d)); sel = (fr > .5) & (fr < 6); res["T143_beat_hz"] = float(fr[sel][np.argmax(sp[sel])])
    print(json.dumps(res, indent=1, default=float)); json.dump(res, open("output.json", "w"), indent=1, default=float)
