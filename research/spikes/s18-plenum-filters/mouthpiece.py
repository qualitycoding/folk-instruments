"""Spike S18b: mouthpiece area for the flow-limited breath mode (D-041): A4 level with 1, 4 and 8 keys held, velocity 0.7."""
import json, plenum as P, metrics as m
out = {}
for A_m in (40e-6, 25e-6):
    lv, pp = [], []
    for notes in ([69], [69, 60, 64, 67], [69, 60, 62, 64, 65, 67, 71, 72]):
        us, fs, p = P.run_chord(notes, 1250 * 0.7 ** 1.5, 1, A_m=A_m, T=0.9)
        y = P.dudt_48k(us[:, 0], fs); lv.append(round(float(m.peak_near(y[int(0.5 * 48000):int(0.85 * 48000)], 48000, 440.0, 25)[1]), 2)); pp.append(round(float(p), 1))
    out[f"A_m_{A_m * 1e6:.0f}mm2"] = dict(A4_level_dB=lv, plenum_Pa=pp, steps_dB=[round(lv[0] - lv[1], 2), round(lv[1] - lv[2], 2)]); print(out, flush=True)
json.dump(out, open("mouthpiece_output.json", "w"), indent=1)
