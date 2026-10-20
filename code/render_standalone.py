"""Standalone Exhibits 7–12, calculated with the repository's canonical model."""
from pathlib import Path
import csv
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter
from PIL import Image
from messi_style import COLORS, SANS, SANS_BOLD, SERIF_BOLD
from model import SCENARIOS, simulate, flows

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures' / 'standalone'
DATA = ROOT / 'data'
SERIES_COLORS = dict(JH='#a85d28', JA='#246a91', EH='#33846f', EM='#875e9c')
LABELS = dict(JH='Human intellectual material', JA='AI investigation',
              EH='Human observations', EM='Machine observations')
CASES = {
 'A': dict(number=7, title='Formal-task crossover'),
 'B': dict(number=8, title='Human observations persist'),
 'C': dict(number=9, title='Sensors take over observation'),
 'D': dict(number=10, title='Low verified yield'),
 'E': dict(number=11, title='Human material is replenished', switch=35.),
 'F': dict(number=12, title='Fresh evidence is interrupted', switch=40.),
}

def decorate_svg(path, case):
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    root = ET.parse(path).getroot()
    root.set('role','img')
    root.set('aria-labelledby','chart-title chart-desc')
    title = ET.Element(f'{{{ns}}}title', {'id':'chart-title'})
    title.text = f"Case {case}: {CASES[case]['title']}"
    desc = ET.Element(f'{{{ns}}}desc', {'id':'chart-desc'})
    desc.text = ('Calculated illustrative model v0.2. Four input-rate trajectories '
                 'from model time zero to one hundred: human intellectual material, '
                 'AI investigation, human observations and machine observations. '
                 'Both axes use normalised model units. Assumed parameters are '
                 'not empirical estimates. All six exhibits use the same scales.')
    root.insert(0, title)
    root.insert(1, desc)
    # Keep portable editable text with appropriate font fallback families.
    for e in root.iter():
        st = e.get('style')
        if st:
            st = st.replace("'DejaVu Sans'", "'DejaVu Sans', Arial, Helvetica, sans-serif")
            st = st.replace("'DejaVu Serif'", "'DejaVu Serif', Georgia, 'Times New Roman', serif")
            e.set('style', st)
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)

def render(case, rows):
    c = CASES[case]
    filename = f"Exhibit_{c['number']:02d}_Case_{case}"
    plt.rcParams.update({'font.family':'DejaVu Sans', 'svg.fonttype':'none',
                         'axes.unicode_minus':False, 'path.simplify':False})
    fig = plt.figure(figsize=(16,9), dpi=200, facecolor=COLORS['background'])
    fig.text(.06,.949,'ILLUSTRATIVE MODEL  ·  SCENARIO '+case,
             fontproperties=SANS_BOLD, fontsize=13, color=COLORS['muted_dark'])
    fig.text(.06,.889,c['title'], fontproperties=SERIF_BOLD,
             fontsize=29, color=COLORS['ink'])
    ax = fig.add_axes([.105,.285,.845,.535])
    handles = []
    for key in ['JH','JA','EH','EM']:
        line, = ax.plot([r['t'] for r in rows], [r[key] for r in rows],
                        color=SERIES_COLORS[key], linewidth=2.7,
                        linestyle='-' if key in ['JH','JA'] else (0,(5,3)),
                        label=LABELS[key], solid_capstyle='round', zorder=3)
        handles.append(line)
    ax.set_xlim(0,100)
    ax.set_ylim(-.025,1.12)
    ax.set_xticks(np.arange(0,101,20))
    ax.set_yticks(np.arange(0,1.01,.2))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.set_xlabel('Model time (no calendar scale)', fontsize=20,
                  labelpad=12, color=COLORS['ink'], fontproperties=SANS)
    ax.set_ylabel('Useful input / model time', fontsize=20,
                  labelpad=14, color=COLORS['ink'], fontproperties=SANS)
    ax.tick_params(axis='both',labelsize=18,colors=COLORS['muted_dark'],
                   length=4,width=.8,pad=8)
    ax.grid(axis='y',color=COLORS['line'],linewidth=.8,zorder=0)
    for side in ['top','right']:
        ax.spines[side].set_visible(False)
    for side in ['bottom','left']:
        ax.spines[side].set_color(COLORS['muted'])
        ax.spines[side].set_linewidth(.9)
    if 'switch' in c:
        ax.axvline(c['switch'],linestyle=(0,(1,2)), color=COLORS['muted'],
                   linewidth=1.3,zorder=1)
        event = ('Replenishment increases' if case == 'E'
                 else 'Observation supply stops')
        ax.text(c['switch']+1.5,1.075,event+'\n'+f"t = {int(c['switch'])}",
                fontsize=14.5,color=COLORS['muted_dark'],ha='left',va='top',
                bbox=dict(facecolor='white',edgecolor='none',pad=1.5))
    legend = fig.legend(handles=handles, loc='lower center',
                        bbox_to_anchor=(.54,.069), ncol=2,
                        fontsize=19.5, frameon=False, handlelength=2.7,
                        columnspacing=2.1, labelspacing=.55,
                        handletextpad=.7, labelcolor=COLORS['ink'])
    fig.lines.append(Line2D([.06,.95],[.056,.056],transform=fig.transFigure,
                            color=COLORS['line'],linewidth=.8))
    fig.text(.06,.019,'Normalised model units; illustrative parameters, not empirical estimates.',
             fontsize=13, fontproperties=SANS,color=COLORS['muted'])
    # Check text extents against canvas and legend against chart/x-axis label.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = fig.bbox
    text_artists = (fig.texts + list(ax.get_xticklabels()) + list(ax.get_yticklabels())
                    + [ax.xaxis.label,ax.yaxis.label] + list(ax.texts)
                    + list(legend.get_texts()))
    for artist in text_artists:
        b = artist.get_window_extent(renderer)
        if b.width and b.height:
            assert b.x0>=0 and b.y0>=0 and b.x1<=bbox.x1 and b.y1<=bbox.y1, artist.get_text()
    assert legend.get_window_extent(renderer).y1 < ax.xaxis.label.get_window_extent(renderer).y0
    png = FIG / (filename+'.png')
    svg = FIG / (filename+'.svg')
    temporary_png = png.with_suffix('.tmp.png')
    fig.savefig(temporary_png,dpi=200,facecolor='white',metadata={'Title':f"Case {case}: {c['title']}",
                      'Description':'Calculated illustrative scenario from article model v0.2.'})
    with Image.open(temporary_png) as check:
        check.load()
        assert check.size == (3200,1800)
    temporary_png.replace(png)
    fig.savefig(svg,facecolor='white')
    decorate_svg(svg,case)
    plt.close(fig)
    with Image.open(png) as im:
        assert im.size == (3200,1800)
        im.load()
    return filename

def build_standalone(baseline_runs=None):
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(exist_ok=True)
    comparison = {}
    for name, p in SCENARIOS.items():
        case = name[0]
        t, x, f = simulate(p, dt=.05, tight=True)
        rows = []
        for i, ti in enumerate(t):
            base = dict(t=float(ti), R=float(x[0,i]), C=float(x[1,i]))
            # Include the left-hand limit at the observation interruption.
            # The following ordinary row is its right-hand limit at the same t.
            if p.observation_stop is not None and ti == p.observation_stop:
                left = flows(np.nextafter(ti,-np.inf), x[:,i], p)
                rows.append({**base, **{k.replace('_',''):float(left[k])
                               for k in ['J_H','J_A','E_H','E_M']}})
            rows.append({**base, **{k.replace('_',''):float(f[k][i])
                             for k in ['J_H','J_A','E_H','E_M']}})
        filename = render(case, rows)
        with (DATA/(filename+'.csv')).open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        if baseline_runs is not None:
            endpoint_error=float(np.max(np.abs(x[:2,-1]-baseline_runs[name][1][:2,-1])))
            assert endpoint_error < 1e-7
            comparison[name]={'max_endpoint_difference_from_baseline':endpoint_error,
                              'plotted_samples':len(rows)}
    return comparison

if __name__=='__main__':
    build_standalone()
