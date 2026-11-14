#!/usr/bin/env python3
"""Spike S08: a test oracle. An idealised additive-synthesis stand-in for folk-render that follows the command-line
contract (plan/DECISIONS.md, D-092) and the intended behaviour of each instrument. It is NOT the product and not a
reference implementation: it exists to show that the frozen Python tests are satisfiable and measure what they claim
(lessons: unsatisfiable frozen assertions; a DSP test that measured the wrong quantity). Run the suite against it with
FOLK_RENDER pointing at a wrapper script that calls this file."""
import json, sys, math
import numpy as np
import soundfile as sf

COMMON = [("level", 0, 1, 0.7, 0), ("a4_hz", 415, 466, 440, 0)]
REED = [("breath", 0, 1, 0.5, 0), ("breath_source", 0, 2, 0, 3), ("vibrato_rate_hz", 0, 10, 5.5, 0), ("vibrato_depth", 0, 1, 0, 0), ("air_noise", 0, 1, 0.2, 0)]
PLUCK = [("pick_position", 0.03, 0.5, 0.12, 0), ("pick_stiffness", 0, 1, 0.6, 0), ("pair_detune_cents", 0, 8, 1.5, 0), ("course_mode", 0, 1, 0, 2),
         ("body_coupling", 0, 1, 1, 0), ("damping", 0, 1, 0.3, 0), ("tremolo", 0, 1, 0, 2), ("tremolo_rate_hz", 4, 20, 12, 0), ("bend_range", 0, 12, 2, 13)]
OWN = {"harmonica": [("variant", 0, 1, 0, 2), ("key", 0, 11, 0, 12), ("wah", 0, 1, 0, 0), ("airtightness", 0, 1, 0.9, 0), ("valve_buzz", 0, 1, 0, 0)],
       "accordion": [("register", 0, 11, 1, 12), ("cassotto", 0, 1, 0, 2), ("musette_cents", 0, 25, 15, 0), ("musette_scaling", 0, 1, 0, 2), ("bend_cents", 0, 25, 25, 0), ("sordina", 0, 1, 0, 2), ("key_noise", 0, 1, 0.1, 0)],
       "melodion": [("range", 0, 2, 1, 3), ("body", 0, 2, 0, 3), ("breath_mode", 0, 1, 0, 2), ("moisture", 0, 1, 0, 0)],
       "mandolin": [("body", 0, 2, 0, 3)], "bouzouki": [("variant", 0, 2, 1, 3), ("octave_order", 0, 1, 0, 2)]}
def table(ins): return COMMON + (PLUCK if ins in ("mandolin", "bouzouki") else REED) + OWN[ins]
class Usage(Exception): pass
class BadEvents(Exception): pass
RHO, E_STEEL = 7850.0, 200e9
def hz(m, a4=440.0): return a4 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ harmonica tables (D-020, D-021, D-023)
BLOW = [60, 64, 67, 72, 76, 79, 84, 88, 91, 96]; DRAW = [62, 67, 71, 74, 77, 81, 83, 86, 89, 93]
DBEND = [1, 2, 3, 1, 0, 1, 0, 0, 0, 0]; BBEND = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2]
def harp_base(key): return (60 if key <= 6 else 48) + key - 60
def diatonic(key, midi):
    """returns (kind, maxbend) for the note; kind in natural, bend, overbend, None"""
    n = midi - harp_base(key)
    for h in range(10):
        if BLOW[h] == n: return "natural", BBEND[h]
        if DRAW[h] == n: return "natural", DBEND[h]
    for h in range(10):
        for b in range(1, DBEND[h] + 1):
            if DRAW[h] - b == n: return "bend", 0
        for b in range(1, BBEND[h] + 1):
            if BLOW[h] - b == n: return "bend", 0
    for h in (0, 3, 4, 5):
        if DRAW[h] + 1 == n: return "overbend", 0
    for h in (6, 8, 9):
        if BLOW[h] + 1 == n: return "overbend", 0
    return None, 0
RANKS = [("H",), ("M",), ("L",), ("M", "H"), ("M", "M+"), ("M", "M+", "H"), ("M-", "M", "M+"), ("L", "H"), ("L", "M", "H"), ("L", "M"), ("L", "M", "M+"), ("L", "M", "M+", "H")]
MEL_RANGE = [(53, 84), (53, 89), (41, 64)]

# ------------------------------------------------------------------ string data (D-072, D-073)
def plain(midi, gauge_in): d = gauge_in * 0.0254; return dict(midi=midi, diameter_m=d, wound=False, linear_density=RHO * math.pi * d * d / 4, core_m=d)
def wound(midi, gauge_in, L): # linear density from an assumed tension of 100 N; core assumed 0.4 x outer diameter (A-021)
    d = gauge_in * 0.0254; return dict(midi=midi, diameter_m=d, wound=True, linear_density=100.0 / (2 * L * hz(midi)) ** 2, core_m=0.4 * d)
def courses(ins, v):
    if ins == "mandolin":
        L = 0.330 if v == 2 else 0.3524; g = (0.038, 0.024, 0.014, 0.010) if v == 2 else (0.040, 0.026, 0.015, 0.011)
        return L, [[wound(55, g[0], L)] * 2, [wound(62, g[1], L)] * 2, [plain(69, g[2])] * 2, [plain(76, g[3])] * 2], 24
    if v == 0: L = 0.680; return L, [[wound(50, 0.022, L), plain(62, 0.011)], [plain(57, 0.014)] * 2, [plain(62, 0.011)] * 2], 27
    if v == 1: L = 0.680; return L, [[wound(48, 0.024, L), plain(60, 0.011)], [wound(53, 0.020, L), plain(65, 0.010)], [plain(57, 0.014)] * 2, [plain(62, 0.011)] * 2], 27
    L = 0.650; return L, [[wound(43, 0.040, L)] * 2, [wound(50, 0.028, L)] * 2, [plain(57, 0.016)] * 2, [plain(62, 0.011)] * 2], 24
def string_B(s, L):
    T = s["linear_density"] * (2 * L * hz(s["midi"])) ** 2
    return math.pi ** 3 * E_STEEL * s["core_m"] ** 4 / (64 * T * L * L)
BODY = {("mandolin", 0): [313, 464, 570, 824, 886, 1117], ("mandolin", 1): [209, 398, 482, 575, 775, 918, 1149], ("mandolin", 2): [200, 550, 740],
        ("bouzouki", 0): [180, 445, 695], ("bouzouki", 1): [180, 445, 695], ("bouzouki", 2): [110, 205, 330]}
def model(ins, P):
    v = int(P["body"] if ins == "mandolin" else P["variant"]); L, cs, maxfret = courses(ins, v)
    return dict(scale_length_m=L, young_modulus_pa=E_STEEL, max_fret=maxfret,
                courses=[dict(strings=[dict(midi=s["midi"], diameter_m=s["diameter_m"], wound=s["wound"], linear_density=s["linear_density"], core_m=s["core_m"], B=string_B(s, L)) for s in c]) for c in cs],
                body_modes=[dict(hz=float(f), q=30.0, gain=1.0 / (i + 1)) for i, f in enumerate(BODY[(ins, v)])])

# ------------------------------------------------------------------ event file
def parse_events(path, ins, ids):
    try: raw = open(path, "rb").read()
    except OSError as e: raise OSError(str(e))
    try: text = raw.decode("utf-8")
    except UnicodeDecodeError: raise BadEvents("line 1: the event file is not UTF-8 text")
    ev, last, end = [], 0.0, None
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("#"): continue
        if end is not None: raise BadEvents(f"line {i}: text after the end event")
        if len(line) > 1000: raise BadEvents(f"line {i}: line longer than 1000 characters")
        w = s.split()
        try: t = float(w[0])
        except ValueError: raise BadEvents(f"line {i}: bad time '{w[0][:20]}'")
        if not math.isfinite(t) or t < 0: raise BadEvents(f"line {i}: time must be a finite number >= 0")
        if t < last: raise BadEvents(f"line {i}: time goes backwards")
        last = t
        if len(w) < 2: raise BadEvents(f"line {i}: missing event kind")
        k, a = w[1], w[2:]
        try:
            if k == "on" and len(a) == 2: ev.append((t, "on", int(a[0]), float(a[1])))
            elif k == "off" and len(a) == 1: ev.append((t, "off", int(a[0]), 0.0))
            elif k == "cc" and len(a) == 2: ev.append((t, "cc", int(a[0]), float(a[1])))
            elif k == "bend" and len(a) == 1: ev.append((t, "bend", 0, float(a[0])))
            elif k == "tap" and len(a) == 1: ev.append((t, "tap", 0, float(a[0])))
            elif k == "set" and len(a) == 2:
                if a[0] not in ids: raise BadEvents(f"line {i}: unknown parameter '{a[0]}'")
                ev.append((t, "set", a[0], float(a[1])))
            elif k == "end" and len(a) == 0: end = t
            else: raise BadEvents(f"line {i}: unknown event '{k}' or wrong number of arguments")
        except ValueError: raise BadEvents(f"line {i}: bad number")
    if end is None: raise BadEvents("the event file has no end event")
    return ev, end

# ------------------------------------------------------------------ synthesis
def clampP(tab, P):
    for (i, lo, hi, de, st) in tab:
        v = min(max(P[i], lo), hi); P[i] = float(round(v)) if st else v
def smooth(x, sr, tau):
    if tau <= 0: return x
    a = math.exp(-1 / (tau * sr)); y = np.empty_like(x); s = x[0]
    for i in range(len(x)): s = a * s + (1 - a) * x[i]; y[i] = s
    return y
def reed_note(ins, P, midi, vel, t_on, t_off, sr, n_total, breath_curve, vib_curve, bend, nkeys, attack=True, seed=0):
    a4 = P["a4_hz"]; out = np.zeros(n_total); ranks = [("M", 1.0, 0.0)]; pitch_semi = 0.0
    if ins == "harmonica":
        if int(P["variant"]) == 1:
            if not 60 <= midi <= 97: return out
            pitch_semi = min(bend, 0.0)
        else:
            kind, maxbend = diatonic(int(P["key"]), midi)
            if kind is None: return out
            pitch_semi = min(bend, 0.0) * maxbend if kind == "natural" else 0.0
    elif ins == "accordion":
        c = P["musette_cents"]; d_hz = 440.0 * (2 ** (c / 1200) - 1); f = hz(midi, a4); ranks = []
        for r in RANKS[int(P["register"])]:
            if r == "L": ranks.append((r, 0.5, 0.0))
            elif r == "H": ranks.append((r, 2.0, 0.0))
            elif r == "M": ranks.append((r, 1.0, 0.0))
            else:
                sgn = 1 if r == "M+" else -1
                ranks.append((r, 2 ** (sgn * c / 1200), 0.0) if int(P["musette_scaling"]) == 0 else (r, 1.0, sgn * d_hz))
        pitch_semi = min(bend, 0.0) * P["bend_cents"] / 100.0
    elif ins == "melodion":
        lo, hi = MEL_RANGE[int(P["range"])]
        if not lo <= midi <= hi: return out
    i0, i1 = int(round(t_on * sr)), min(int(round(t_off * sr)), n_total); rel = int(0.25 * sr); i2 = min(i1 + rel, n_total)
    if i2 <= i0: return out
    t = np.arange(i2 - i0) / sr; b = breath_curve[i0:i2] if breath_curve is not None else np.full(i2 - i0, vel)
    amp = np.where(b < 0.08, 0.0, (np.clip(b - 0.08, 0, 1) / 0.92) ** 1.6)
    tau = 0.01 + 0.12 * (1 - float(np.clip(b[0] if breath_curve is None else np.mean(b), 0, 1))) ** 2
    if ins == "melodion" and P["moisture"] > 0: amp = amp * 10 ** (-10 * P["moisture"] / 20)
    env = (1 - np.exp(-t / tau)) if attack else np.ones_like(t)
    if i1 - i0 < len(t): env[i1 - i0:] *= np.exp(-(t[i1 - i0:] - t[i1 - i0]) / 0.008)
    env = env * (1 + 0.1 * vib_curve[i0:i2] * np.sin(2 * np.pi * P["vibrato_rate_hz"] * (t + t_on)))
    if ins == "melodion" and int(P["breath_mode"]) == 1: env = env / math.sqrt(nkeys)
    bmean = float(np.clip(np.mean(b), 0, 1)); tilt = 2.0 - 1.0 * bmean
    if ins == "harmonica": tilt += 1.0 * P["wah"]
    if ins == "melodion": tilt += (0.0, 0.5, -0.2)[int(P["body"])]
    cents = -4.0 * (bmean - 0.6); rng = np.random.default_rng(1000 * midi + seed); sig = np.zeros_like(t)
    for (name, mult, add_hz) in ranks:
        f0 = (hz(midi + pitch_semi, a4) * mult + add_hz) * 2 ** (cents / 1200); ph = rng.uniform(0, 2 * np.pi)
        for n in range(1, 41):
            fn = n * f0
            if fn > 18000: break
            g = n ** (-tilt)
            if ins == "accordion" and fn > 2000: g *= (0.4 if P["cassotto"] else 1.0) * (0.4 if P["sordina"] else 1.0)
            sig += g * np.sin(2 * np.pi * fn * (t + t_on) + n * ph)
    sig = 0.12 * sig * amp * env
    if ins == "accordion" and attack: k = int(0.015 * sr); sig[:k] += 0.02 * P["key_noise"] * rng.standard_normal(k)[:len(sig[:k])]
    out[i0:i2] += sig; return out
def eta_air(d, f): M = d / 4 * np.sqrt(2 * np.pi * f / 1.5e-5); return 1.2 / RHO * (2 * math.sqrt(2) * M + 1) / M ** 2
def string_sound(mdl, P, course_i, midi, vel, t_on, t_end_nat, t_off, sustain, sr, n_total, bend):
    """one pluck of a course: per partial, a coupled pair (S04) or a single string; returns array of n_total"""
    L = mdl["scale_length_m"]; strs = mdl["courses"][course_i]["strings"]; a4 = P["a4_hz"]
    fret = midi - min(s["midi"] for s in strs); semis = bend * P["bend_range"]
    i0 = int(round(t_on * sr)); i1 = min(int(round(t_end_nat * sr)), n_total)
    if i1 <= i0: return np.zeros(n_total)
    t = np.arange(i1 - i0) / sr; out = np.zeros(i1 - i0); beta = P["pick_position"]; stiff = P["pick_stiffness"]; cpl = P["body_coupling"]
    dampf = 1 + 4 * P["damping"]; single = int(P["course_mode"]) == 1 or len(strs) == 1
    def partial_set(s, detune_c):
        f1 = hz(s["midi"] + fret + semis, a4) * 2 ** (detune_c / 1200); Lf = L / 2 ** (fret / 12)
        T = s["linear_density"] * (2 * L * hz(s["midi"])) ** 2; B = math.pi ** 3 * E_STEEL * s["core_m"] ** 4 / (64 * T * Lf * Lf)
        n = np.arange(1, 81); f = f1 * n * np.sqrt((1 + B * n * n) / (1 + B)); keep = f < 18000; n, f = n[keep], f[keep]
        amp = np.sin(n * np.pi * beta) / n * np.exp(-n * (1 - stiff) * 0.15) * np.exp(-n * (1 - vel) * 0.1) * vel ** 1.5
        eta_i = (eta_air(s["diameter_m"], f) + 1e-3 * B * n * n / (1 + B * n * n)) * dampf
        eta_b = 2e-3 * cpl / np.sqrt(n)
        return n, f, amp, eta_i, eta_b
    A = partial_set(strs[0], 0.0)
    if single:
        n, f, amp, ei, eb = A
        for k in range(len(n)): out += amp[k] * np.exp(-np.pi * f[k] * (ei[k] + eb[k]) * t) * np.sin(2 * np.pi * f[k] * t)
    else:
        ratio = round(2 ** ((strs[1]["midi"] - strs[0]["midi"]) / 12)); Bs = partial_set(strs[1], P["pair_detune_cents"])
        nA, fA, aA, eiA, ebA = A; nB, fB, aB, eiB, ebB = Bs; used = set()
        for j in range(len(nB)):
            k = ratio * (j + 1) - 1
            if k >= len(nA): out += 0.8 * aB[j] * np.exp(-np.pi * fB[j] * (eiB[j] + ebB[j]) * t) * np.sin(2 * np.pi * fB[j] * t); continue
            used.add(k); w1, w2 = 2 * np.pi * fA[k], 2 * np.pi * fB[j]; z = 1j * ebA[k] * w1 / 2
            Om = np.array([[w1 * (1 + 1j * eiA[k] / 2) + z, z], [z, w2 * (1 + 1j * eiB[j] / 2) + z]]); lam, V = np.linalg.eig(Om)
            c = np.linalg.solve(V, np.array([aA[k], 0.8 * aB[j]], complex))
            out += np.imag((c[0] * (V[0, 0] + V[1, 0])) * np.exp(1j * lam[0] * t) + (c[1] * (V[0, 1] + V[1, 1])) * np.exp(1j * lam[1] * t))
        for k in range(len(nA)):
            if k not in used: out += aA[k] * np.exp(-np.pi * fA[k] * (eiA[k] + ebA[k]) * t) * np.sin(2 * np.pi * fA[k] * t)
    for bm in mdl["body_modes"]:   # the pluck also knocks the body
        out += 0.03 * cpl * vel * bm["gain"] * np.exp(-np.pi * bm["hz"] / bm["q"] * t) * np.sin(2 * np.pi * bm["hz"] * t)
    out *= np.minimum(1.0, t / 0.0015)   # 1.5 ms pick release
    if t_off is not None and not sustain and t_off < t_end_nat:
        k = max(0, int(round((t_off - t_on) * sr)))
        if k < len(out): out[k:] *= np.exp(-(t[k:] - t[k]) / 0.03)
    full = np.zeros(n_total); full[i0:i1] = 0.5 * out; return full
def render(ins, P0, events, end, sr):
    tab = table(ins); P = dict(P0); n_total = int(round(end * sr)); y = np.zeros(n_total)
    reed = ins in ("harmonica", "accordion", "melodion")
    # controller curves
    def cc_curve(num, default):
        c = np.full(n_total, default); 
        for (t, k, a, b) in events:
            if k == "cc" and a == num: c[int(round(t * sr)):] = min(max(b, 0.0), 1.0)
        return c
    sets = [(t, a, b) for (t, k, a, b) in events if k == "set"]; bends = [(t, b) for (t, k, a, b) in events if k == "bend"]
    def params_at(t):
        Q = dict(P)
        for (ts, a, b) in sets:
            if ts <= t: Q[a] = b
        clampP(tab, Q); return Q
    def bend_at(t):
        v = 0.0
        for (tb, b) in bends:
            if tb <= t: v = min(max(b, -1.0), 1.0)
        return v
    ons = [(t, a, b) for (t, k, a, b) in events if k == "on" and 0 <= a <= 127]
    def off_time(t_on, midi):
        c = [t for (t, k, a, b) in events if k == "off" and a == midi and t >= t_on] + [t for (t, a, b) in ons if a == midi and t > t_on]
        return min(c) if c else end
    if reed:
        mod = cc_curve(1, 0.0); set_times = sorted({ts for (ts, a, b) in sets if ts > 0})
        for (t_on, midi, vel) in ons:
            t_off = off_time(t_on, midi); cuts = [t_on] + [s for s in set_times if t_on < s < t_off] + [t_off]
            for si in range(len(cuts) - 1):
                Q = params_at(cuts[si]); src = int(Q["breath_source"])
                bc = None if src == 0 else smooth(cc_curve(2 if src == 1 else 11, 0.0), sr, 0.02)
                vib = np.clip(Q["vibrato_depth"] + mod, 0, 1); mid = 0.5 * (cuts[si] + cuts[si + 1])
                nkeys = sum(1 for (t2, m2, v2) in ons if t2 <= mid < off_time(t2, m2))
                seg = reed_note(ins, Q, midi, min(max(vel, 0.0), 1.0), cuts[si], cuts[si + 1], sr, n_total, bc, vib, bend_at(cuts[si]), max(nkeys, 1), attack=(si == 0), seed=si)
                if si > 0 or si < len(cuts) - 2:   # short cross-fades at parameter changes
                    pass
                y += seg * Q["level"] / 0.7
    else:
        mod = cc_curve(1, 0.0); sus = cc_curve(64, 0.0); plucks = []
        for (t_on, midi, vel) in ons:
            Q = params_at(t_on); mdl = model(ins, Q); cs = mdl["courses"]; ci = -1
            for i, c in enumerate(cs):
                lo = min(s["midi"] for s in c["strings"])
                if lo <= midi and midi - lo <= mdl["max_fret"]: ci = i
            if ci < 0: continue
            t_off = off_time(t_on, midi); trem = int(Q["tremolo"]) == 1 or mod[min(int(round(t_on * sr)), n_total - 1)] >= 0.5
            times = [t_on]
            if trem:
                k = 1
                while t_on + k / Q["tremolo_rate_hz"] < t_off - 1e-9: times.append(t_on + k / Q["tremolo_rate_hz"]); k += 1
            for j, ts in enumerate(times): plucks.append([ts, ci, midi, min(max(vel, 0.0), 1.0), t_off if j == len(times) - 1 else None, Q, mdl])
        plucks.sort(key=lambda p: p[0])
        for i, p in enumerate(plucks):
            nxt = [q[0] for q in plucks[i + 1:] if q[1] == p[1]]; t_cut = min(nxt) if nxt else end
            sustain = sus[min(int(round((p[4] if p[4] is not None else p[0]) * sr)), n_total - 1)] >= 0.5
            seg = string_sound(p[6], p[5], p[1], p[2], p[3], p[0], end, p[4], sustain, sr, n_total, bend_at(p[0]))
            if t_cut < end:   # the next stroke on the course stops this one (4 ms)
                k = int(round(t_cut * sr)); fade = np.exp(-np.arange(n_total - k) / (0.004 * sr)); seg[k:] *= fade
            y += seg * p[5]["level"] / 0.7
        for (t, k, a, b) in events:
            if k == "tap":
                Q = params_at(t); mdl = model(ins, Q); i0 = int(round(t * sr)); tt = np.arange(n_total - i0) / sr
                for bm in mdl["body_modes"]: y[i0:] += 0.3 * b * bm["gain"] * np.exp(-np.pi * bm["hz"] / bm["q"] * tt) * np.sin(2 * np.pi * bm["hz"] * tt) * Q["level"] / 0.7
    return np.tanh(y)
def main(argv):
    opt = {"--sr": "48000", "--block": "256"}; sets = []; flags = set(); i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--list-params", "--dump-model", "--version", "--help"): flags.add(a); i += 1
        elif a in ("--instrument", "--events", "--out", "--sr", "--block", "--set"):
            if i + 1 >= len(argv): raise Usage(f"{a} needs a value")
            if a == "--set": sets.append(argv[i + 1])
            else: opt[a] = argv[i + 1]
            i += 2
        else: raise Usage(f"unknown option {a}")
    if "--version" in flags: print("folk-render 0.0.0-oracle"); return 0
    if "--help" in flags: print("usage: folk-render --instrument <name> --events <file> --out <file.wav> [--sr <Hz>] [--block <n>] [--set id=value]... | --list-params | --dump-model | --version"); return 0
    ins = opt.get("--instrument")
    if ins not in OWN: raise Usage(f"unknown instrument {ins}")
    tab = table(ins); ids = [r[0] for r in tab]; P = {r[0]: float(r[3]) for r in tab}
    for s in sets:
        if "=" not in s: raise Usage("--set needs id=value")
        k, v = s.split("=", 1)
        if k not in ids: raise Usage(f"unknown parameter {k}")
        try: P[k] = float(v)
        except ValueError: raise Usage(f"bad value for {k}")
        if not math.isfinite(P[k]): raise Usage(f"bad value for {k}")
    clampP(tab, P)
    if "--list-params" in flags:
        for r in tab: print("\t".join([r[0], repr(float(r[1])), repr(float(r[2])), repr(float(r[3])), str(r[4])]))
        return 0
    if "--dump-model" in flags:
        print(json.dumps(model(ins, P) if ins in ("mandolin", "bouzouki") else {"instrument": ins})); return 0
    try: sr, block = int(opt["--sr"]), int(opt["--block"])
    except ValueError: raise Usage("bad --sr or --block")
    if not 44100 <= sr <= 96000 or not 1 <= block <= 8192: raise Usage("--sr must be 44100..96000 and --block 1..8192")
    if "--events" not in opt or "--out" not in opt: raise Usage("--events and --out are required")
    events, end = parse_events(opt["--events"], ins, ids)
    if end > 600: raise BadEvents("the end time is beyond 600 s")
    y = render(ins, P, events, end, sr).astype(np.float32)
    sf.write(opt["--out"], np.stack([y, y], axis=1), sr, subtype="FLOAT"); return 0
if __name__ == "__main__":
    try: sys.exit(main(sys.argv[1:]))
    except Usage as e: sys.stderr.write(f"folk-render: {e}\n"); sys.exit(2)
    except BadEvents as e: sys.stderr.write(f"folk-render: {e}\n"); sys.exit(3)
    except (OSError, sf.LibsndfileError) as e: sys.stderr.write(f"folk-render: {e}\n"); sys.exit(4)
