"""Spike S01: recompute the computed tables of the owner's input file from first principles.
Formulas (to be corroborated in research; here only arithmetic is checked):
  cantilever: f1 = (lam^2 / (2 pi L^2)) * sqrt(E t^2 / (12 rho)),  lam = 1.875104
  beat:       fb = f0 (2^(c/1200) - 1)
  string:     T = mu (2 L f0)^2, mu = rho pi d^2/4, B = pi^3 E d^4 / (64 T L^2),
              f_n = n f0 sqrt(1 + B n^2), stretch(n) = 1200 log2(sqrt(1+B n^2)) cents
"""
import math, json
out = {}
lam = 1.875104
def L_reed(f, E, rho, t): return math.sqrt(lam**2 / (2*math.pi*f) * math.sqrt(E*t*t/(12*rho)))
mats = {"brass": (105e9, 8490), "phosphor bronze": (110e9, 8800), "stainless steel": (195e9, 7900)}
file_reed = {"brass": [[25.52,32.95,41.68],[13.92,17.97,22.73],[9.02,11.65,14.74]],
             "phosphor bronze": [[25.59,33.04,41.79],[13.95,18.01,22.79],[9.05,11.68,14.78]],
             "stainless steel": [[30.34,39.16,49.54],[16.54,21.35,27.01],[10.73,13.85,17.51]]}
worst = 0; rows = []
for m,(E,rho) in mats.items():
    for i,f in enumerate([130.81,440.0,1046.50]):
        for j,t in enumerate([0.15e-3,0.25e-3,0.40e-3]):
            L = L_reed(f,E,rho,t)*1e3; d = L - file_reed[m][i][j]; worst = max(worst,abs(d))
            rows.append((m,f,t*1e3,round(L,2),file_reed[m][i][j]))
out["reed_table_max_abs_diff_mm"] = round(worst,3)
out["steel_vs_brass_length_ratio"] = round(L_reed(440,195e9,7900,0.25e-3)/L_reed(440,105e9,8490,0.25e-3),4)
beat_file = {2:[0.13,0.25,0.51,1.02,2.03],4:[0.25,0.51,1.02,2.04,4.07],10:[0.64,1.27,2.55,5.10,10.20],
             15:[0.96,1.91,3.83,7.66,15.32],18:[1.15,2.30,4.60,9.20,18.39],25:[1.60,3.20,6.40,12.80,25.60]}
bw = 0
for c,vals in beat_file.items():
    for f,v in zip([110,220,440,880,1760],vals):
        bw = max(bw, abs(f*(2**(c/1200)-1) - v))
out["beat_table_max_abs_diff_hz"] = round(bw,4)
out["cents_of_444_vs_440"] = round(1200*math.log2(444/440),3)
out["cents_of_1hz_at_A3_A5"] = [round(1200*math.log2(221/220),2), round(1200*math.log2(881/880),2)]
E_s, rho_s = 200e9, 7850
def string(Lmm, f0, gauge_in):
    d = gauge_in*0.0254; L = Lmm/1e3; mu = rho_s*math.pi*d*d/4; T = mu*(2*L*f0)**2
    B = math.pi**3*E_s*d**4/(64*T*L*L)
    st = lambda n: 1200*math.log2(math.sqrt(1+B*n*n))
    return dict(mu_g_per_m=round(mu*1e3,3), T_N=round(T,1), T_kgf=round(T/9.80665,2), B=float(f"{B:.4g}"), st10=round(st(10),2), st20=round(st(20),2))
file_str = [("mand F E5",352.4,659.26,.011,0.481,103.9,4.576e-5,3.95,15.70),("mand F A4",352.4,440,.015,0.895,86.1,1.910e-4,16.38,63.74),
 ("mand bowl E5",330,659.26,.010,0.398,75.3,4.918e-5,4.25,16.86),("mand bowl A4",330,440,.014,0.780,65.7,2.164e-4,18.53,71.86),
 ("gr D4",680,293.66,.011,0.481,76.8,1.663e-5,1.44,5.74),("gr A3",680,220,.014,0.780,69.8,4.801e-5,4.15,16.47),("gr C4",680,261.63,.011,0.481,60.9,2.096e-5,1.81,7.23),
 ("ir long D4",650,293.66,.011,0.481,70.1,1.992e-5,1.72,6.87),("ir long A3",650,220,.016,1.018,83.3,7.511e-5,6.48,25.62),
 ("ir short D4",560,293.66,.013,0.672,72.7,5.051e-5,4.36,17.32),("ir short A3",560,220,.020,1.591,96.6,2.130e-4,18.25,70.78)]
sw = []
for name,L,f,g,mu,T,B,s10,s20 in file_str:
    r = string(L,f,g)
    sw.append(dict(name=name, computed=r, file=dict(mu=mu,T=T,B=B,st10=s10,st20=s20),
                   rel_B_diff=round(r["B"]/B-1,4), st20_diff=round(r["st20"]-s20,2)))
out["strings"] = sw
out["string_max_rel_B_diff"] = max(abs(x["rel_B_diff"]) for x in sw)
print(json.dumps(out, indent=1))
