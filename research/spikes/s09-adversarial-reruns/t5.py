import sys,json,numpy as np; sys.path.insert(0,'.')
import reed_orig as R, reed2 as M
for fr in (1760.0, 3520.0):
    R.fr=fr; R.w0=2*np.pi*fr  # same mass M, stiffer reed (numerical stress test only)
    for fs in (44100, 88200, 352800):
        r=M.an(M.run(2.5,fs=fs,T=0.6)); print(fr,fs,json.dumps({k:r.get(k) for k in ('oscillates','f0_Hz','cents_re_fr','tip_amplitude_um','flowH2','diverged')}),flush=True)
