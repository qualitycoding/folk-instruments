# D-010 table range [-4x0,4x0] with a stiff spring beyond, vs spike table
import json, numpy as np, similarity as s
rho,c0,alpha=s.rho,s.c0,s.alpha
def table4(p,n=2048):
    xt=np.linspace(-4*p["x0"],4*p["x0"],n); out=np.empty(n)
    for i,x in enumerate(xt):
        d=x*s.psi; h=np.where(d>0,d,np.where(d<-(p["es"]+p["er"]),-(d+p["es"]+p["er"]),0.0))
        out[i]=p["Wr"]*np.hypot(h[-1],p["hmin"])+2*p["Lr"]*np.trapezoid(np.hypot(h,p["hmin"]),s.s)
    return xt,np.maximum(out,out.min())
def run(p,p0,fs,T,spring):
    xt,St=table4(p); w0=2*np.pi*p["f"]; mu=p["Sr"]*w0*w0/p["K"]; dt=1/fs; n=int(T*fs); ramp=9/p["f"]
    x,v,p1,u=p["x0"],0.0,0.0,0.0; xs=np.empty(n); us=np.empty(n); lo,hi,m=xt[0],xt[-1],len(xt)-1
    for i in range(n):
        d=p0*min(1.0,i*dt/ramp)-p1; u0=alpha*p["Ain"]*np.sign(d)*np.sqrt(2*abs(d)/rho)
        t=(x-lo)/(hi-lo)*m; t=0.0 if t<0 else (m-1e-9 if t>=m else t); j=int(t); Su=St[j]+(St[j+1]-St[j])*(t-j)
        vj=(u+p["Sr"]*v)/(alpha*Su); p2=0.5*rho*vj*abs(vj)
        p1+=dt*rho*c0*c0/p["V1"]*(u0-u); u+=dt*p["S2"]/(rho*p["L2"])*(p1-p2)
        F=0.0
        if spring and x>hi: F=-spring*w0*w0*(x-hi)
        if spring and x<lo: F=-spring*w0*w0*(x-lo)
        v+=dt*(-w0/p["Q"]*v-w0*w0*(x-p["x0"])-mu*p2+F); x+=dt*v
        if not np.isfinite(x) or abs(x)>1: return None
        xs[i]=x; us[i]=u
    return xs,us
p=s.reed(1.0); fs=400*444
for spring in (0,100):
    for p0 in (100,400,700,1500):
        r=run(p,p0,fs,450/444,spring); a=s.analyse(p,r,fs); a.update(table="[-4x0,4x0]",spring_factor=spring,p0=p0); print(json.dumps(a),flush=True)
