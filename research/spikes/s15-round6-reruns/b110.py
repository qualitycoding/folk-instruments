import json, sys
sys.argv=["x"]; exec(open("breath.py").read().split('if __name__')[0])
from multiprocessing import Pool
fr = lambda mi: 440*2**((mi-69)/12)
with Pool(4) as pl:
    for o in pl.imap(job, [(fr(45), b) for b in (0.25, 0.4, 0.55, 0.7, 0.85, 1.0)] + [(fr(28), 0.25)]):
        print(json.dumps({k: o.get(k) for k in ("f","b","level_db","amp_over_x0_tail","cents","half_level_time_s")}), flush=True)
