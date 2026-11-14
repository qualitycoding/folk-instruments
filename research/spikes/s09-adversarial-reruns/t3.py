import numpy as np, scipy.linalg as sl
f1,eta_i,etab=660.0,2e-4,2e-3
def Om(c):
    w1=2*np.pi*f1; w2=w1*2**(c/1200); z=1j*etab*w1/2
    return np.array([[w1*(1+1j*eta_i/2)+z,z],[z,w2*(1+1j*eta_i/2)+z]])
# exceptional point: (w2-w1)/2 = etab*w1/2 approx
for c in (1,3,3.4,3.45,3.4624,3.47,4,8):
    O=Om(c); lam,V=np.linalg.eig(O); ca=np.linalg.cond(V)
    a0=np.array([1,0],complex); cc=np.linalg.solve(V,a0)
    t=np.linspace(0,3,6001)
    am=(V@(cc[:,None]*np.exp(1j*lam[:,None]*t)))
    ex=np.array([sl.expm(1j*O*tt)@a0 for tt in t[::200]])
    err=np.abs(am[:,::200].T-ex).max()
    print(f"cents {c}: cond(V)={ca:.3g}  |dlam|/2pi={abs(lam[0]-lam[1])/2/np.pi:.4g} Hz  max err modal vs expm={err:.2e}  max|coef|={abs(cc).max():.3g}")
