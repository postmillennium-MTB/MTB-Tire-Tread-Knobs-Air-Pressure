"""Builds the paper's fitted curves (Fig. 6 and 12) as small tables: x in degrees (positive side only; the tool mirrors
them as odd functions), y normalized by load. Fig. 6 series are traced from the plot's pixels (line_traces below);
Fig. 12 series are read at the markers (the lines of one colour overlap too much to trace)."""
import json, numpy as np
from scipy.interpolate import PchipInterpolator
S='/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad'
raw=json.load(open(S+'/fig6_curves_raw.json'))
SLIP_GRID=np.round(np.arange(0,5.01,0.5),2); CAMB_GRID=np.round(np.arange(0,25.01,2.5),2)

def from_trace(panel,sid,grid,half,xmax=None,end_zero=None):
    pts=[(x,y) for x,y in raw[panel][sid]['pts'] if y is not None]
    xs=np.array([p[0] for p in pts]); ys=np.array([p[1] for p in pts])
    vals=[]
    for g in grid:
        sel=(xs>=g-half)&(xs<=g+half)
        vals.append(float(np.median(ys[sel])) if sel.sum()>=1 and g>0 else (0.0 if g==0 else np.nan))
    vals=np.array(vals); ok=~np.isnan(vals)
    if xmax is not None: ok&=grid<=xmax+1e-9
    g=grid[ok]; v=vals[ok]
    if end_zero is not None: g=np.append(g,end_zero); v=np.append(v,0.0)
    f=PchipInterpolator(g,v)
    gg=grid[(grid<=g.max()+1e-9)]
    out=[[float(x),round(float(f(x)),5)] for x in gg]
    if end_zero is not None: out.append([float(end_zero),0.0])   # the curve ends where it crosses zero
    return out

def from_markers(pts,grid,xmax=None):
    xs=np.array([p[0] for p in pts]); ys=np.array([p[1] for p in pts])
    f=PchipInterpolator(xs,ys)
    top=xs.max() if xmax is None else xmax
    gg=[x for x in grid if x<=top+1e-9]
    if gg[-1]<top-1e-9: gg.append(top)
    return [[float(x),round(float(f(x)),5)] for x in gg]

C={}
# ---- Fig. 6 (traced): 27.5x2.8 @20 psi, 29x3.0 @20 psi, 26x4.0 @15 psi
for sid in ['k275_38','k29_45','k26_86']:
    C[sid]={'psi':{'k275_38':20,'k29_45':20,'k26_86':15}[sid],'src':'Fig. 6'}
C['k275_38'].update(fy=from_trace('a_fy_slip','k275_38',SLIP_GRID,0.25), fc=from_trace('b_fy_camber','k275_38',CAMB_GRID,1.25), mz=from_trace('c_mz_slip','k275_38',SLIP_GRID,0.25))
C['k29_45'].update(fy=from_trace('a_fy_slip','k29_45',SLIP_GRID,0.25), fc=from_trace('b_fy_camber','k29_45',CAMB_GRID,1.25), mz=from_trace('c_mz_slip','k29_45',SLIP_GRID,0.25,xmax=2.5,end_zero=2.7))
C['k26_86'].update(fy=from_trace('a_fy_slip','k26_86',SLIP_GRID,0.25,xmax=3.0), fc=from_trace('b_fy_camber','k26_86',CAMB_GRID,1.25), mz=from_trace('c_mz_slip','k26_86',SLIP_GRID,0.25))
# ---- Fig. 12 (markers): 29x2.3 bald, 29x2.5 file-tread, 29x2.5 bald, all @25 psi on 25 mm
M={
 'b23_25':{'fy':[(0,0),(1,.338),(2,.538),(3,.635),(4,.675),(5,.700)],
           'fc':[(0,0),(5,.1855),(10,.367),(15,.536),(20,.692),(25,.84)],
           'mz':[(0,0),(1,-.0083),(2,-.0109),(3,-.0078),(4,-.0030),(4.6,0.0)]},
 'f25_25':{'fy':[(0,0),(1,.290),(2,.525),(3,.701),(4,.820),(5,.902)],
           'fc':[(0,0),(5,.138),(10,.275),(15,.408),(20,.537),(25,.654)],
           'mz':[(0,0),(1,-.0060),(2,-.0087),(3,-.0100),(4,-.0108),(5,-.0113)]},
 'b25_25':{'fy':[(0,0),(1,.310),(2,.5775),(3,.787),(4,.925),(4.8,1.0)],     # leaves the plot's 1.0 limit at ~4.8 deg
           'fc':[(0,0),(5,.152),(10,.302),(15,.4409),(20,.567),(25,.6757)],
           'mz':[(0,0),(1,-.0071),(2,-.0098),(3,-.0083),(4,-.0047),(5,-.0010)]},
}
for sid,d in M.items():
    C[sid]={'psi':25,'src':'Fig. 12','fy':from_markers(d['fy'],SLIP_GRID),'fc':from_markers(d['fc'],CAMB_GRID),'mz':from_markers(d['mz'],SLIP_GRID)}
json.dump(C,open(S+'/curves_by_config.json','w'))
for k,v in C.items(): print(k,v['src'],'psi',v['psi'],'fy pts',len(v['fy']),'to',v['fy'][-1],'| fc to',v['fc'][-1],'| mz to',v['mz'][-1])
