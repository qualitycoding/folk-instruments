"""Spike S07: what the TinySOL accordion notes contain, measured with the frozen metrics module, and the spread between
neighbouring notes, from which the reference thresholds of T-200 are derived (lesson: check a threshold against the
reference spread before freezing it). Usage: analyse.py <TinySOL root> ; writes output.json (no audio is copied)."""
import sys, csv, json, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tests" / "py"))
import metrics as m
root = pathlib.Path(sys.argv[1])
rows = [r for r in csv.DictReader(open(root / "TinySOL_metadata.csv")) if r["Instrument (abbr.)"] == "Acc" and r["Needed digital retuning"] == "FALSE" and r["Dynamics"] in ("pp", "mf", "ff")]
notes = {}
for r in rows:
    p = root / r["Path"]; midi = int(r["Pitch ID"]); f0 = 440 * 2 ** ((midi - 69) / 12)
    try:
        x, sr = m.load_mono(p)
    except Exception as e:
        continue
    dur = len(x) / sr
    if dur < 1.2 or f0 * 0.5 < 20: continue
    a, b = 0.3 * dur, min(0.3 * dur + 1.0, 0.8 * dur)
    if (b - a) * f0 < 25: continue
    s = m.seg(x, sr, a, b)
    try:
        f, lv = m.peak_near(s, sr, f0, 80)
        prof = m.harmonic_profile_db(s, sr, f, 10) if 10 * f < 0.45 * sr else None
        sub = m.peak_near(s, sr, f / 2, 40)[1] - lv if (b - a) * f / 2 >= 20 else None
        mod = m.modulation_frequency(m.seg(x, sr, 0.25 * dur, 0.85 * dur), sr) if 0.6 * dur > 1.0 else (None, None)
        t, e = m.envelope_db(x, sr, 0.002); pk = e.max(); first = float(t[np.nonzero(e > pk - 40)[0][0]]); t50 = float(t[np.nonzero(e > m.rms_db(s) - 6)[0][0]])
    except AssertionError:
        continue
    notes[(midi, r["Dynamics"], r["Instance ID"])] = dict(midi=midi, dyn=r["Dynamics"], dur=dur, cents=float(m.cents(f, f0)), level=float(m.rms_db(s)),
        centroid_ratio=float(m.spectral_centroid(s, sr) / f), profile=None if prof is None else [float(v) for v in prof], sub_octave_db=None if sub is None else float(sub),
        mod_hz=mod[0], mod_depth=mod[1], first_sound_s=first, rise_to_minus6dB_s=t50 - first, sr=sr)
N = list(notes.values())
def q(v, ps=(10, 50, 90)): v = np.array([a for a in v if a is not None]); return [round(float(np.percentile(v, p)), 3) for p in ps] if len(v) else None
out = {"notes_analysed": len(N), "sample_rates": sorted({n["sr"] for n in N})}
for d in ("pp", "mf", "ff"):
    D = [n for n in N if n["dyn"] == d]
    out[d] = dict(count=len(D), midi_range=[min(n["midi"] for n in D), max(n["midi"] for n in D)], duration_s=q([n["dur"] for n in D]), cents_q10_50_90=q([n["cents"] for n in D]),
                  level_db=q([n["level"] for n in D]), centroid_ratio=q([n["centroid_ratio"] for n in D]), sub_octave_db=q([n["sub_octave_db"] for n in D]),
                  mod_depth=q([n["mod_depth"] for n in D]), mod_hz=q([n["mod_hz"] for n in D]), first_sound_s=q([n["first_sound_s"] for n in D]), rise_s=q([n["rise_to_minus6dB_s"] for n in D]),
                  harmonics_within_60dB=q([sum(1 for v in n["profile"] if v > -60) for n in D if n["profile"]]),
                  mean_profile=[round(float(np.mean([n["profile"][k] for n in D if n["profile"]])), 1) for k in range(10)])
    # leave-one-out neighbour prediction: mean profile of the notes one semitone below and above, same dynamics
    by = {}
    for n in D:
        if n["profile"]: by.setdefault(n["midi"], []).append(n)
    mad, cr, lv = [], [], []
    for midi, L in by.items():
        if midi - 1 in by and midi + 1 in by:
            pred = np.mean([x["profile"][:8] for x in by[midi - 1] + by[midi + 1]], axis=0)
            pc = np.mean([x["centroid_ratio"] for x in by[midi - 1] + by[midi + 1]]); pl = np.mean([x["level"] for x in by[midi - 1] + by[midi + 1]])
            for n in L:
                mad.append(float(np.mean(np.abs(np.array(n["profile"][:8]) - pred)))); cr.append(n["centroid_ratio"] / pc); lv.append(n["level"] - pl)
    out[d]["neighbour_harmonic_mad_db_q50_q90_q95"] = q(mad, (50, 90, 95)); out[d]["neighbour_centroid_ratio_q5_q50_q95"] = q(cr, (5, 50, 95)); out[d]["neighbour_level_diff_db_q5_q50_q95"] = q(lv, (5, 50, 95)); out[d]["neighbour_pairs"] = len(mad)
# dynamics: level and centroid differences ff - pp per pitch
P = {}
for n in N: P.setdefault(n["midi"], {}).setdefault(n["dyn"], []).append(n)
dl = [np.mean([x["level"] for x in v["ff"]]) - np.mean([x["level"] for x in v["pp"]]) for v in P.values() if "ff" in v and "pp" in v]
dc = [np.mean([x["centroid_ratio"] for x in v["ff"]]) / np.mean([x["centroid_ratio"] for x in v["pp"]]) for v in P.values() if "ff" in v and "pp" in v]
dp = [np.mean([x["cents"] for x in v["ff"]]) - np.mean([x["cents"] for x in v["pp"]]) for v in P.values() if "ff" in v and "pp" in v]
out["ff_minus_pp"] = dict(pitches=len(dl), level_db=q(dl), centroid_ratio=q(dc), cents=q(dp), share_brighter=float(np.mean(np.array(dc) > 1)), share_flatter=float(np.mean(np.array(dp) < 0)))
print(json.dumps(out, indent=1)); json.dump(out, open(pathlib.Path(__file__).with_name("output.json"), "w"), indent=1)
