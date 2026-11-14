"""Spike S03b: the (-,+) reed needs V1*L2*w^2/(c0^2*S2) > 1 (Millot & Baumann section 3.1). Compare L1 = 60 mm (ratio 2.5)
with L1 = 10 mm (ratio 0.42) at the same supply velocity."""
import json, numpy as np, reed_sim as r
out = []
for L1 in (0.06, 0.03, 0.02, 0.01):
    ratio = r.S1*L1*r.L2*(2*np.pi*r.fr)**2/(r.c0**2*r.S2)
    a = r.analyse(*r.run(2.0, L1=L1)); a.update(L1_m=L1, condition_ratio=round(float(ratio), 3)); out.append(a)
    print(L1, round(float(ratio), 3), a["oscillates"], a.get("f0_Hz"), a["tip_amplitude_um"], flush=True)
json.dump(out, open("volume_condition_output.json", "w"), indent=1)
