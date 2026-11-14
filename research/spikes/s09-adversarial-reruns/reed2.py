import numpy as np, math, json, sys
import reed_orig as R
xt=R.xt; Sut=R.Sut; x_lo=xt[0]; dxt=xt[1]-xt[0]; SutL=Sut.tolist(); N=len(SutL)
def Su(x):
    f=(x-x_lo)/dxt
    if f<=0: return SutL[0]
    if f>=N-1: return SutL[-1]
    i=int(f); a=f-i; return SutL[i]*(1-a)+SutL[i+1]*a
def run(v0, L1=0.06, T=1.2, fs=44100*8, ramp=0.05, scheme='semi', vprof=None):
    rho,c0,alpha,S0,S1,L2,S2,Sr,mu,w0,Q,x0=R.rho,R.c0,R.alpha,R.S0,R.S1,R.L2,R.S2,R.Sr,R.mu,R.w0,R.Q,R.x0
    dt=1/fs; n=int(T*fs); V1=S1*L1
    x,v,p1,u=x0,0.0,0.0,0.0
    xs=np.empty(n); us=np.empty(n); ps=np.empty(n)
    def deriv(x,v,p1,u,u0):
        up=-Sr*v; vj=(u-up)/(alpha*Su(x)); p2=0.5*rho*vj*abs(vj)
        return v, -w0/Q*v-w0*w0*(x-x0)-mu*p2, rho*c0*c0/V1*(u0-u), S2/(rho*L2)*(p1-p2), p2
    for i in range(n):
        if vprof: v0e=vprof(i*dt)
        else: v0e=v0*min(1.0,i*dt/ramp)
        u0=S0*v0e
        if scheme=='semi':
            up=-Sr*v; vj=(u-up)/(alpha*Su(x)); p2=0.5*rho*vj*abs(vj)
            p1+=dt*rho*c0*c0/V1*(u0-u); u+=dt*S2/(rho*L2)*(p1-p2)
            a=-w0/Q*v-w0*w0*(x-x0)-mu*p2; v+=dt*a; x+=dt*v
        else: # RK4
            k1=deriv(x,v,p1,u,u0); p2=k1[4]
            k2=deriv(x+dt/2*k1[0],v+dt/2*k1[1],p1+dt/2*k1[2],u+dt/2*k1[3],u0)
            k3=deriv(x+dt/2*k2[0],v+dt/2*k2[1],p1+dt/2*k2[2],u+dt/2*k2[3],u0)
            k4=deriv(x+dt*k3[0],v+dt*k3[1],p1+dt*k3[2],u+dt*k3[3],u0)
            x+=dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); v+=dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
            p1+=dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2]); u+=dt/6*(k1[3]+2*k2[3]+2*k3[3]+k4[3])
        if not (abs(x)<1): return None
        xs[i],us[i],ps[i]=x,u,p2
    return xs,us,ps,fs
def an(res):
    if res is None: return {'diverged':True}
    r=R.analyse(*res); return {k:r.get(k) for k in ('oscillates','f0_Hz','cents_re_fr','tip_amplitude_um','reed_h2_dB','goes_through_plate','mean_p2_Pa')} | {'flowH2':(r.get('flow_harmonics_dB') or [None,None])[1]}
