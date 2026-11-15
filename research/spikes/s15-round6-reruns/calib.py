import json, importlib.util
from multiprocessing import Pool
spec = importlib.util.spec_from_file_location("sim", "/home/user/folk-instruments/research/spikes/s12-reed-similarity-scaling/similarity.py")
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
def job(a):
    name, fx, fh, fq, spp, p0 = a
    p = sim.reed(1.0); p["x0"] *= fx; p["hmin"] *= fh; p["Q"] *= fq
    fe = spp*p["f"]; an = sim.analyse(p, sim.run(p, p0, fe, T=300/p["f"]), fe); an.update(case=name, spp=spp, p0=p0); return an
jobs = [(n, fx, fh, fq, spp, p0) for (n, fx, fh, fq) in (("x0x0.75", .75, 1, 1), ("hminx2", 1, 2, 1), ("Qx0.3", 1, 1, .3), ("Qx3", 1, 1, 3), ("x0x2", 2, 1, 1))
        for spp in (110, 400) for p0 in (50, 100, 400, 1500, 1800)]
with Pool(4) as pl:
    for o in pl.imap(job, jobs): print(json.dumps({k: o.get(k) for k in ("case", "spp", "p0", "state", "cents", "amp_over_x0")}), flush=True)
