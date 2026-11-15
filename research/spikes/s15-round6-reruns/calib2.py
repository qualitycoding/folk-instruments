import json, importlib.util
from multiprocessing import Pool
spec = importlib.util.spec_from_file_location("sim", "/home/user/folk-instruments/research/spikes/s12-reed-similarity-scaling/similarity.py")
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
def job(a):
    name, fx, fq, spp, p0 = a
    p = sim.reed(1.0); p["x0"] *= fx; p["Q"] *= fq
    fe = spp*p["f"]; an = sim.analyse(p, sim.run(p, p0, fe, T=300/p["f"]), fe); return dict(case=name, spp=spp, p0=p0, state=an["state"], cents=an.get("cents"))
jobs = [(n, fx, fq, spp, p0) for (n, fx, fq) in (("Qx3", 1, 3), ("x0x2", 2, 1), ("Qx1.5", 1, 1.5), ("x0x1.5", 1.5, 1)) for spp in (110, 135, 160, 220) for p0 in (1500, 1800)]
with Pool(4) as pl:
    for o in pl.imap(job, jobs): print(json.dumps(o), flush=True)
