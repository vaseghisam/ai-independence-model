"""QJ knowledge-source model v0.2. Illustrative, not fitted; no calendar time.

Run python code/run_all.py from the package root for all outputs.
Units: R in effective learning units; C in capability-index units;
E, J, p in learning units/time; B in resource units/time.
All scalar state proxies refer to one specified domain and objective.
"""
from dataclasses import dataclass, asdict, replace
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit


@dataclass(frozen=True)
class Parameters:
    budget: float = 1.0
    a_h: float = 1.0
    a_a: float = 1.0
    q: float = 0.90
    K: float = 1.0
    c_mid: float = 0.8
    n: float = 2.0
    beta: float = 8.0
    p_h: float = 0.015
    gamma_h: float = 0.09
    gamma_a: float = 0.09
    gamma_e: float = 0.03
    delta: float = 0.015
    e_h: float = 0.0
    e_m: float = 0.0
    cost_h: float = 0.6
    cost_m: float = 0.2
    empirical: float = 0.0
    e_mid: float = 0.2
    r_init: float = 6.0
    c_init: float = 0.15
    p_after: float | None = None
    renewal_time: float = 35.0
    sensor_handoff: bool = False
    sensor_time: float = 35.0
    sensor_width: float = 5.0
    sensor_final: float = 0.60
    observation_stop: float | None = None
    human_stop: float | None = None
    gamma_a_stop: float | None = None


BASE = Parameters()
SCENARIOS = {
    "A_formal": BASE,
    "B_human_observations": replace(BASE, a_a=1.8, empirical=1.0, e_h=.35, e_m=.03),
    "C_sensor_handoff": replace(BASE, a_a=1.8, empirical=1.0, e_h=.35, e_m=.03,
                                 sensor_handoff=True),
    "D_low_verified_yield": replace(BASE, q=.08, p_h=.15, e_h=.05),
    "E_human_renewal": replace(BASE, p_after=.75),
    "F_evidence_interrupted": replace(BASE, a_a=1.8, empirical=1.0, e_h=.35, e_m=.03,
                                      observation_stop=40.0),
}
LABELS = {
    "A_formal": "A  Formal-task crossover",
    "B_human_observations": "B  Human observations persist",
    "C_sensor_handoff": "C  Sensors take over observation",
    "D_low_verified_yield": "D  Low verified yield",
    "E_human_renewal": "E  Human material is replenished",
    "F_evidence_interrupted": "F  Fresh evidence is interrupted",
}


def observations(t, p):
    eh, em = p.e_h, p.e_m
    if p.sensor_handoff:
        lo = expit(-p.sensor_time / p.sensor_width)
        u = (expit((t-p.sensor_time)/p.sensor_width)-lo)/(1-lo)
        u = np.clip(u, 0, 1)
        eh = p.e_h * (1-u)
        em = p.e_m + (p.sensor_final-p.e_m)*u
    if p.observation_stop is not None and t >= p.observation_stop:
        eh, em = 0.0, 0.0
    if p.human_stop is not None and t >= p.human_stop:
        eh = 0.0
    return eh, em


def flows(t, state, p):
    r, c = state[:2]
    eh, em = observations(t, p)
    b = p.budget - p.cost_h*eh - p.cost_m*em
    if b < -1e-12:
        raise ValueError("Specified observation costs exceed total budget")
    b = max(0.0, b)
    yh = p.a_h * r/(r+p.K)
    cn = c ** p.n
    gate = 1-p.empirical + p.empirical*(eh+em)/(eh+em+p.e_mid)
    ya = p.q*p.a_a * cn/(cn+p.c_mid**p.n)*gate
    s = expit(p.beta*(ya-yh))
    ph = p.p_h if p.p_after is None or t < p.renewal_time else p.p_after
    if p.human_stop is not None and t >= p.human_stop:
        s, ph = 1.0, 0.0
    jh, ja = b*(1-s)*yh, b*s*ya
    ga = p.gamma_a if p.gamma_a_stop is None or t < p.gamma_a_stop else 0.0
    return dict(y_h=yh, y_a=ya, s=s, J_H=jh, J_A=ja, E_H=eh, E_M=em,
                p_H=ph, B=b, G=gate, gamma_a=ga)


def rhs(t, state, p):
    f=flows(t,state,p)
    dc=p.gamma_h*f['J_H'] + f['gamma_a']*f['J_A'] + p.gamma_e*(f['E_H']+f['E_M']) - p.delta*state[1]
    return [f['p_H']-f['J_H'], dc, f['J_H'], f['J_A'], f['E_H'], f['E_M'], f['p_H']]


def simulate(p=BASE, horizon=100.0, dt=.1, tight=False):
    # Segment every externally imposed discontinuity. The endpoint derivative
    # is evaluated on the interior side to avoid crossing an intervention.
    breaks=[0.0,horizon]
    if p.p_after is not None: breaks.append(p.renewal_time)
    breaks += [x for x in [p.observation_stop,p.human_stop,p.gamma_a_stop] if x is not None]
    breaks=sorted(set(x for x in breaks if 0 <= x <= horizon))
    grid=np.unique(np.r_[np.arange(0,horizon+dt/2,dt),breaks])
    grid=grid[grid<=horizon]
    state=np.array([p.r_init,p.c_init,0.,0.,0.,0.,0.])
    ts, xs=[],[]
    for left,right in zip(breaks[:-1],breaks[1:]):
        chosen=grid[(grid>=left)&(grid<=right)]
        def fun(t,x):
            # nextafter selects the intended one-sided parameter values.
            tt=max(np.nextafter(left,right),min(t,np.nextafter(right,left)))
            return rhs(tt,x,p)
        sol=solve_ivp(fun,(left,right),state,t_eval=chosen,
                      rtol=1e-10 if tight else 1e-8,
                      atol=1e-12 if tight else 1e-10,
                      max_step=.10 if tight else .25)
        if not sol.success: raise RuntimeError(sol.message)
        state=sol.y[:,-1]
        start=1 if ts else 0
        ts.extend(sol.t[start:]); xs.append(sol.y[:,start:])
    t=np.array(ts); x=np.concatenate(xs,axis=1)
    fs=[flows(u,v,p) for u,v in zip(t,x.T)]
    f={key:np.array([row[key] for row in fs]) for key in fs[0]}
    total=f['J_H']+f['J_A']+f['E_H']+f['E_M']
    intellectual=f['J_H']+f['J_A']
    f['human_intellectual_share']=np.divide(f['J_H'],intellectual,out=np.zeros_like(total),where=intellectual>0)
    f['human_direct_share']=np.divide(f['J_H']+f['E_H'],total,out=np.zeros_like(total),where=total>0)
    f['total']=total
    return t,x,f


def crossing_times(t, diff, discontinuities=()):
    out=[]
    for i in range(len(t)-1):
        if diff[i]*diff[i+1]<0:
            z=t[i]-diff[i]*(t[i+1]-t[i])/(diff[i+1]-diff[i])
            for jump in discontinuities:
                if jump is not None and t[i] < jump <= t[i+1]: z=jump
            out.append({'time':float(z),'direction':'AI leads' if diff[i+1]>0 else 'human leads'})
    return out


def summary(t,x,f,p):
    # Sustained means every sampled point over a final 10-unit interval.
    tail=t>=t[-1]-10
    return {'parameters':asdict(p),
            'yield_crossings':crossing_times(t,f['y_a']-f['y_h'],[p.observation_stop,p.human_stop]),
            'C_final':float(x[1,-1]),'R_final':float(x[0,-1]),
            'human_intellectual_share_final':float(f['human_intellectual_share'][-1]),
            'human_direct_share_final':float(f['human_direct_share'][-1]),
            'human_share_below_5pct_final_interval':bool(np.all(f['human_intellectual_share'][tail]<.05) and np.all(f['J_A'][tail]>.001)),
            'J_H_final':float(f['J_H'][-1]),'J_A_final':float(f['J_A'][-1]),
            'E_H_final':float(f['E_H'][-1]),'E_M_final':float(f['E_M'][-1]),
            'budget_final':float(f['B'][-1])}
