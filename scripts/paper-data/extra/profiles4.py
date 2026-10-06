import sys, json, warnings, numpy as np
warnings.filterwarnings('ignore')
S='/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad'
sys.path.insert(0,S)
from digitize import SERIES, load
from profiles import trace
from skimage.morphology import dilation, disk
from skimage.measure import approximate_polygon
from PIL import Image, ImageDraw
TOL=1.2   # px simplification tolerance (~0.25 mm)

def simplify(path_rc, scale, cx, top, tol=TOL):
    p=approximate_polygon(np.asarray(path_rc,float), tolerance=tol)
    pts=[[round((c-cx)/scale,1), round((r-top)/scale,1)] for r,c in p]
    return pts[::-1] if pts[0][0]>pts[-1][0] else pts

out={}
# ---------- Fig 4: four knobby tires; scale from each tire's printed tread width
a=load(S+'/img/im-009.png'); R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
for tid,col,wmm,Rmm in [('k23_25','blue',54.0,367.5),('k275_38','green',65.7,360.0),('k29_45','gold',76.0,387.0),('k26_86','orange',100.0,367.0)]:
    path,_=trace(dilation(SERIES[col](R,G,B),disk(1)))
    path=np.array(path)
    wpx=path[:,1].max()-path[:,1].min(); scale=wpx/wmm
    cx=(path[:,1].max()+path[:,1].min())/2; top=path[:,0].min()
    pts=simplify(path,scale,cx,top)
    out[tid]={'widthMm':wmm,'radiusMm':Rmm,'pts':pts,'pxPerMm':round(scale,3)}
    print(tid,'px/mm',round(scale,2),'pts',len(pts),'height mm',round((path[:,0].max()-top)/scale,1))
# ---------- Fig 10: knobby with bald overlay (blue), file-tread (red)
a=load(S+'/img/im-017.png'); R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
raw=json.load(open(S+'/fig10_raw.json'))
from profiles import longest_path
for tid,wmm,Rmm,wb,Rb in [('k23_25',54.0,367.5,53.6,362.5),('f25_25',59.0,370.0,59.5,369.5)]:
    path=np.array(raw[tid]['path']); wpx=path[:,1].max()-path[:,1].min(); scale=wpx/wmm
    cx=(path[:,1].max()+path[:,1].min())/2; top=path[:,0].min()
    d={'widthMm':wmm,'radiusMm':Rmm,'pts':simplify(path,scale,cx,top),'pxPerMm':round(scale,3),'baldWidthMm':wb,'baldRadiusMm':Rb}
    ys,xs=raw[tid]['rest']
    if len(ys)>150:   # bald crown arc exists as separate dashes (file-tread: overlaps the solid, nothing to add)
        ys=np.array(ys);xs=np.array(xs)
        # circle fit to dash pixels -> polar centre
        A=np.c_[2*xs,2*ys,np.ones(len(xs))]; b=xs**2+ys**2; (px_,py_,c0),*_=np.linalg.lstsq(A,b,rcond=None); rad=np.sqrt(c0+px_**2+py_**2)
        ang=np.degrees(np.arctan2(-(ys-py_),xs-px_)); r=np.hypot(xs-px_,ys-py_)
        lo,hi=ang.min(),ang.max()
        bins=np.arange(np.floor(lo),np.ceil(hi)+1,1.0); have=[(b_,np.median(r[(ang>=b_-.5)&(ang<b_+.5)])) for b_ in bins if ((ang>=b_-.5)&(ang<b_+.5)).sum()>=2]
        ba=np.array([h[0] for h in have]); br=np.array([h[1] for h in have])
        full=np.arange(ba.min(),ba.max()+1,2.0); fr=np.interp(full,ba,br)
        arc=[(py_-rr*np.sin(np.radians(t)), px_+rr*np.cos(np.radians(t))) for t,rr in zip(full,fr)]   # (row,col)
        # join: solid sidewall points whose polar angle lies outside the dash range
        sang=np.degrees(np.arctan2(-(path[:,0]-py_),path[:,1]-px_)); sr=np.hypot(path[:,1]-px_,path[:,0]-py_)
        left=[tuple(p) for p,t in zip(path,sang) if (t>hi+1 or t<-90) and p[1]<px_]
        right=[tuple(p) for p,t in zip(path,sang) if (t<lo-1 or t<-90) and p[1]>=px_]
        left=sorted(left,key=lambda p:-p[0]); right=sorted(right,key=lambda p:p[0])
        bald=left+arc[::-1]+right
        bald=np.array(bald); d['baldPts']=simplify(bald,scale,cx,top,tol=1.0)
        print(tid,'bald pts',len(d['baldPts']),'angle range',round(lo),round(hi))
    out[tid+'_fig10']=d
    print(tid,'fig10 px/mm',round(scale,2),'pts',len(d['pts']))
json.dump(out,open(S+'/profiles_final.json','w'))
# overlay check on Fig 4 and Fig 10
for imgname,keys,sc in [('im-009',['k23_25','k275_38','k29_45','k26_86'],None)]:
    pass
