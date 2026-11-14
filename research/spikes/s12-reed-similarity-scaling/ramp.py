"""Spike S12b: how fast may the supply pressure rise? Reference reed (k = 1; by similarity the answer in periods holds at
every pitch), 8 x 48 kHz, final pressures 400, 1000 and 1500 Pa, linear ramps of 0.5 to 9 reed periods."""
import json, similarity as s
p = s.reed(1.0); out = []
for p0 in (400, 1000, 1500):
    for rp in (0.5, 1, 2, 3, 5, 9):
        a = s.analyse(p, s.run(p, p0, 384000, T=450/p["f"], ramp_periods=rp), 384000); a.update(p0=p0, ramp_periods=rp); out.append(a)
        print(p0, rp, a["state"], a.get("cents"), a.get("amp_over_x0"), flush=True)
json.dump(out, open("ramp_output.json", "w"), indent=1)
