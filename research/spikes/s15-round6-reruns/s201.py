import sys, json, math, importlib.util
from multiprocessing import Pool
spec = importlib.util.spec_from_file_location("sim", "/home/user/folk-instruments/research/spikes/s12-reed-similarity-scaling/similarity.py")
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
R = 4; C = 110
def job(a):
    midi, fs, p0, rp = a
    f = 440*2**((midi-69)/12); k = f/444; p = sim.reed(k)
    m = math.ceil(C*f/(R*fs)); fe = R*fs*m; spp = fe/f
    r = sim.run(p, p0, fe, T=300/f, ramp_periods=rp); an = sim.analyse(p, r, fe)
    an.update(midi=midi, host_rate=fs, p0=p0, m=m, spp=round(spp,1), ramp_periods=rp)
    return an
if __name__ == "__main__":
    rp = float(sys.argv[1])
    jobs = [(mi, fs, p0, rp) for mi in (28, 69, 100, 112) for fs in (44100, 48000) for p0 in (50, 100, 400, 1500, 1800)]
    with Pool(8) as pl:
        for a in pl.imap(job, jobs): print(json.dumps(a), flush=True)
