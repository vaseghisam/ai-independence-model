"""Recreate the data, figures, animation and verification record, offline."""
from pathlib import Path
from dataclasses import replace, asdict
import json, csv, platform, sys
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.animation import FuncAnimation, PillowWriter
from model import BASE, SCENARIOS, LABELS, simulate, flows, summary
from render_standalone import build_standalone
from write_checksums import write_checksums

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures'; DATA=ROOT/'data'
FIG.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
COL={'J_H':'#a85d28','J_A':'#246a91','E_H':'#33846f','E_M':'#875e9c'}
NAMES={'J_H':'Human intellectual material','J_A':'AI investigation',
       'E_H':'Human observations','E_M':'Machine observations'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':16,
 'axes.labelsize':14,'xtick.labelsize':12,'ytick.labelsize':12,
 'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#6a7279',
 'text.color':'#21323f','axes.labelcolor':'#21323f','svg.fonttype':'none',
 'figure.facecolor':'white','savefig.facecolor':'white'})

def save(fig,name):
    for ext in ['svg','png']:
        fig.savefig(FIG/f'{name}.{ext}',dpi=210,bbox_inches='tight',pad_inches=.18)
    plt.close(fig)

def write_csv(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def draw_map():
    fig,ax=plt.subplots(figsize=(14,8.8));ax.set(xlim=(0,1.04),ylim=(-.02,1.02));ax.axis('off')
    ax.set_title('Four routes into a developing AI system',loc='left',pad=20,fontsize=23)
    def box(x,y,w,h,title,body,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.008,rounding_size=.013',
                                    facecolor='#f7f9fa',edgecolor=color,lw=1.7))
        ax.text(x+w/2,y+h-.029,title,ha='center',va='top',fontsize=15,color=color,weight='bold',linespacing=1.3)
        ax.text(x+w/2,y+.036,body,ha='center',va='bottom',fontsize=12.6,linespacing=1.5)
    box(.015,.69,.215,.26,'Human intellectual\nmaterial','Books, code, journalism,\nforums and archives',COL['J_H'])
    box(.26,.69,.215,.26,'Human\nobservations','Experience, reports,\nchoices and preferences',COL['E_H'])
    box(.505,.69,.215,.26,'AI\ninvestigation','Inference, proof search,\nproposed explanations',COL['J_A'])
    box(.75,.69,.215,.26,'Machine\nobservations','Cameras, satellites,\ninstruments and robots',COL['E_M'])
    box(.19,.405,.60,.16,'Assessment and integration','Criteria depend on the task','#47545d')
    box(.26,.13,.46,.15,'Capability and memory','Available for subsequent work','#47545d')
    for x0,x1,c in [(.122,.27,COL['J_H']),(.367,.415,COL['E_H']),(.612,.565,COL['J_A']),(.857,.71,COL['E_M'])]:
        ax.add_patch(FancyArrowPatch((x0,.677),(x1,.579),arrowstyle='-|>',mutation_scale=18,lw=2,color=c))
    ax.add_patch(FancyArrowPatch((.49,.389),(.49,.292),arrowstyle='-|>',mutation_scale=18,lw=2,color='#47545d'))
    ax.plot([.73,1.0,1.0,.612],[.20,.20,.993,.993],color=COL['J_A'],lw=1.6)
    ax.add_patch(FancyArrowPatch((.612,.993),(.612,.958),arrowstyle='-|>',mutation_scale=16,lw=1.6,color=COL['J_A']))
    ax.text(.855,.245,'Feedback to\nAI investigation',ha='center',fontsize=12.5,color=COL['J_A'])
    ax.text(.49,.027,'Every route inherits human knowledge, infrastructure and chosen objectives.',ha='center',fontsize=12)
    save(fig,'figure_1_source_routes')


def draw_scenarios(runs):
    fig,axs=plt.subplots(3,2,figsize=(14,13),sharex=True,sharey=True)
    for ax,(name,(t,x,f)) in zip(axs.ravel(),runs.items()):
        for key in COL:
            ax.plot(t,f[key],color=COL[key],lw=2.3,ls='--' if key.startswith('E') else '-',label=NAMES[key])
        if name=='E_human_renewal':ax.axvline(35,color='#929ba1',ls=':',lw=1.4)
        if name=='F_evidence_interrupted':ax.axvline(40,color='#929ba1',ls=':',lw=1.4)
        ax.set_title(LABELS[name],loc='left',pad=12)
        ax.grid(axis='y',alpha=.18);ax.set(xlim=(0,100),ylim=(-.02,1.12))
    for ax in axs[:,0]:ax.set_ylabel('Useful input / model time')
    for ax in axs[-1]:ax.set_xlabel('Model time (no calendar scale)')
    handles,labels=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.955),ncol=2,frameon=False,fontsize=13)
    fig.suptitle('Six constructed scenarios',x=.075,ha='left',y=.997,fontsize=25)
    fig.subplots_adjust(top=.885,hspace=.30,wspace=.12,bottom=.07,left=.075,right=.99)
    save(fig,'figure_2_scenarios')

def counterfactuals():
    fig,axs=plt.subplots(1,3,figsize=(15,5.2),sharey=True)
    result={}
    specs=[('B_human_observations','Human observation route',{'human_stop':60.0}),
           ('C_sensor_handoff','Sensor observation route',{'human_stop':60.0}),
           ('A_formal','Integration of AI results',{'gamma_a_stop':60.0})]
    for ax,(name,title,change) in zip(axs,specs):
        p=SCENARIOS[name];t,x,f=simulate(p);tt,xx,ff=simulate(replace(p,**change))
        ax.plot(t,x[1],color='#246a91',lw=2.6,label='Baseline')
        ax.plot(tt,xx[1],color='#a85d28',lw=2.5,ls='--',label='After intervention')
        ax.axvline(60,color='#929ba1',ls=':',lw=1.4)
        ax.set_title(title,loc='left');ax.set_xlabel('Model time');ax.set_xlim(0,100);ax.grid(axis='y',alpha=.18)
        result[name]={'intervention':change,'baseline_C_final':float(x[1,-1]),
            'intervention_C_final':float(xx[1,-1]),'ratio':float(xx[1,-1]/x[1,-1])}
        write_csv(DATA/f'counterfactual_{name}.csv',[{'t':float(ti),'C_baseline':float(a),
            'C_intervention':float(b)} for ti,a,b in zip(t,x[1],xx[1])])
    axs[0].set_ylabel('Capability index C')
    axs[0].legend(frameon=False,fontsize=12,loc='upper left')
    fig.suptitle('Testing dependence by removing an input',x=.075,ha='left',fontsize=24,y=1.04)
    fig.tight_layout(w_pad=2)
    save(fig,'figure_3_removal_experiments')
    return result

def sensitivity():
    # Vectorized fixed-step RK4 independently of the adaptive trajectory solver.
    q=np.linspace(0,1,61);ph=np.linspace(0,.5,61)
    Q,P=np.meshgrid(q,ph,indexing='ij')
    r=np.full_like(Q,BASE.r_init);c=np.full_like(Q,BASE.c_init)
    def flow(r,c):
        yh=r/(r+1);ya=Q*c*c/(c*c+.64);s=1/(1+np.exp(-8*(ya-yh)))
        return (1-s)*yh,s*ya
    def fun(r,c):
        jh,ja=flow(r,c)
        return P-jh,.09*(jh+ja)-.015*c
    step=.025
    for _ in range(round(100/step)):
        a,b=fun(r,c);d,e=fun(r+step*a/2,c+step*b/2)
        g,h=fun(r+step*d/2,c+step*e/2);j,k=fun(r+step*g,c+step*h)
        r+=step*(a+2*d+2*g+j)/6;c+=step*(b+2*e+2*h+k)/6
    jh,ja=flow(r,c);fraction=jh/(jh+ja)
    fig,ax=plt.subplots(figsize=(10,7.0))
    im=ax.pcolormesh(ph,q,100*fraction,cmap='cividis',vmin=0,vmax=100,shading='nearest')
    cs=ax.contour(ph,q,100*fraction,levels=[5,50],colors=['white','#111111'],linewidths=1.9)
    ax.clabel(cs,fmt={5:'5% human share',50:'50% human share'},inline=True,fontsize=12)
    ax.set_xlabel(r'Useful human replenishment rate $p_H$');ax.set_ylabel('Verified useful fraction q')
    ax.set_title('Residual human share at model time 100',loc='left',pad=16,fontsize=22)
    cb=fig.colorbar(im,ax=ax,pad=.035);cb.set_label('Human share of intellectual input (%)')
    fig.tight_layout();save(fig,'figure_4_sensitivity')
    write_csv(DATA/'sensitivity.csv',[{'q':float(Q[i,j]),'p_H':float(P[i,j]),
        'human_intellectual_share_final':float(fraction[i,j]),'C_final':float(c[i,j]),
        'R_final':float(r[i,j])} for i in range(len(q)) for j in range(len(ph))])
    error=0
    for i,j in [(0,0),(6,18),(30,24),(54,2),(60,60)]:
        _,xx,ff=simulate(replace(BASE,q=float(q[i]),p_h=float(ph[j])),tight=True)
        error=max(error,float(abs(xx[0,-1]-r[i,j])),float(abs(xx[1,-1]-c[i,j])))
    assert error<1e-5
    return error

def checks(runs):
    out={}
    for name,(t,x,f) in runs.items():
        p=SCENARIOS[name];tt,xx,ff=simulate(p,tight=True)
        error=float(np.max(np.abs(xx-x)));assert error<1e-5
        assert np.min(x)>=-1e-9
        assert np.all((f['s']>=0)&(f['s']<=1))
        assert np.max(abs(f['B']+p.cost_h*f['E_H']+p.cost_m*f['E_M']-p.budget))<1e-12
        stock_error=float(np.max(abs(x[0]-p.r_init-x[6]+x[2])))
        assert stock_error<1e-7
        out[name]={'max_state_refinement_difference':error,'max_stock_balance_residual':stock_error}
    _,x,f=simulate(replace(BASE,r_init=0,c_init=0,p_h=0))
    assert np.all(x==0)
    _,x,f=simulate(replace(BASE,q=0));assert np.all(f['J_A']==0)
    _,x,f=simulate(replace(BASE,empirical=1));assert np.all(f['J_A']==0)
    for r in [.1,.5,2.0]:
        yh=r/(1+r);c=BASE.c_mid*(yh/(BASE.q*BASE.a_a-yh))**(1/BASE.n)
        z=flows(0,[r,c],BASE);assert abs(z['y_a']-z['y_h'])<1e-12
    out['boundary_checks']='empty seed; zero q; no observations with lambda=1; analytic yield equality: passed'
    return out

def animate(runs):
    t,x,f=runs['C_sensor_handoff']
    fig,ax=plt.subplots(figsize=(10,5.9))
    for key in COL:ax.plot(t,f[key],color=COL[key],lw=1.2,alpha=.14)
    lines={key:ax.plot([],[],color=COL[key],lw=2.6,ls='--' if key.startswith('E') else '-',label=NAMES[key])[0] for key in COL}
    cursor=ax.axvline(0,color='#737d84',lw=1,ls=':')
    ax.set(xlim=(0,100),ylim=(0,1.12),xlabel='Model time (no calendar scale)',ylabel='Useful input / model time')
    ax.set_title('A constructed handoff from human reports to sensors',loc='left',pad=17,fontsize=19)
    ax.legend(frameon=False,fontsize=11,loc='upper left');ax.grid(axis='y',alpha=.18)
    fig.tight_layout()
    def update(i):
        k=min(i*10,len(t)-1)
        for key,line in lines.items():line.set_data(t[:k+1],f[key][:k+1])
        cursor.set_xdata([t[k],t[k]])
        return [*lines.values(),cursor]
    ani=FuncAnimation(fig,update,frames=101,interval=100,blit=True)
    ani.save(FIG/'animation_sensor_handoff.gif',writer=PillowWriter(fps=10),dpi=100)
    plt.close(fig)

def main():
    runs={name:simulate(p) for name,p in SCENARIOS.items()}
    res={name:summary(*runs[name],p) for name,p in SCENARIOS.items()}
    for name,(t,x,f) in runs.items():
        write_csv(DATA/f'{name}.csv',[{'t':float(ti),'R':float(x[0,i]),'C':float(x[1,i]),
           **{key:float(v[i]) for key,v in f.items()}} for i,ti in enumerate(t)])
    validation=checks(runs)
    draw_map();draw_scenarios(runs)
    res['counterfactuals']=counterfactuals()
    validation['sensitivity_grid_max_state_error']=sensitivity()
    animate(runs)
    validation['standalone_exhibits']=build_standalone(runs)
    res['status']='Illustrative parameter choices; uncalibrated; time is not calendar time.'
    (DATA/'results.json').write_text(json.dumps(res,indent=2)+'\n')
    (DATA/'verification.json').write_text(json.dumps(validation,indent=2)+'\n')
    (DATA/'environment.json').write_text(json.dumps({'python':sys.version,'numpy':np.__version__,
        'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'Pillow':__import__('PIL').__version__,'platform':platform.platform()},indent=2)+'\n')
    write_checksums(ROOT)
    print(json.dumps({'verification':validation,'counterfactuals':res['counterfactuals']},indent=2))

if __name__=='__main__':main()
