import sys, json, numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad')
from digitize import SERIES, load
a=load('/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad/img/im-011.png')
R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
PANELS={ # name: (x0px,x1px,xmax_data, y_at_0px, y_at_top_px, ymax_data)
 'a_fy_slip':   dict(box=(142,588,10,444),  x1=5,  y0=444, y1=10,  v1=1.0),
 'b_fy_camber': dict(box=(735,1188,10,444), x1=25, y0=444, y1=10,  v1=1.0),
 'c_mz_slip':   dict(box=(142,590,556,987), x1=5,  y0=556, y1=987, v1=-0.02),
 'd_tw_camber': dict(box=(735,1188,556,987),x1=25, y0=987, y1=556, v1=0.02),
}
SER={'k23_25':'blue','k275_38':'green','k29_45':'gold','k26_86':'orange'}
out={}
for pn,P in PANELS.items():
    x0,x1,ya,yb=P['box']; 
    out[pn]={}
    for sid,col in SER.items():
        m=SERIES[col](R,G,B)
        mm=np.zeros_like(m); mm[ya+2:yb-1, x0+2:x1-1]=m[ya+2:yb-1, x0+2:x1-1]
        if pn=='b_fy_camber': mm[:215, 790:]=False       # legend box
        ys,xs=np.where(mm)
        xd=(xs-x0)/(x1-x0)*P['x1']
        yd=(P['y0']-ys)/(P['y0']-P['y1'])*P['v1']
        step=0.1 if P['x1']==5 else 0.5
        bins=np.arange(0,P['x1']+step,step)
        pts=[];cov=[]
        for b in bins:
            sel=(xd>=b-step/2)&(xd<b+step/2)
            ncols=len(set(xs[sel].tolist()))
            exp=step/P['x1']*(x1-x0)
            cov.append(round(ncols/exp,2))
            pts.append((round(float(b),2), round(float(np.median(yd[sel])),5) if sel.sum()>=3 else None))
        out[pn][sid]={'pts':pts,'cov':cov}
json.dump(out,open('/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad/fig6_curves_raw.json','w'))
for pn in out:
    print('==',pn)
    for sid,d in out[pn].items():
        p=d['pts']; 
        print(sid,[ (x,y) for x,y in p if (x*10)%5==0 or (x%5==0)][:14])
