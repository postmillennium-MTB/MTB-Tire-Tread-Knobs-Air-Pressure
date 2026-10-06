import sys, json, numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad')
from digitize import SERIES, load, clusters
a=load('/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad/pg/hi-15.png')
R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
PAN={
 'a_fy_slip':  dict(x0=551.5, ppx=129.3, ymap=lambda y:(1111-y)/626.,        top=487, bot=1109, xs=[1,2,3,4,5]),
 'b_fy_camber':dict(x0=1408.5,ppx=26.3,  ymap=lambda y:(1111-y)/626.,        top=487, bot=1109, xs=[5,10,15,20,25]),
 'c_mz_slip':  dict(x0=557.5, ppx=130.1, ymap=lambda y:-(y-1278.5)/31160.,   top=1281,bot=1900, xs=[1,2,3,4,5]),
 'd_tw_camber':dict(x0=1412.5,ppx=26.2,  ymap=lambda y:(1901-y)/31080.,      top=1281,bot=1899, xs=[5,10,15,20,25]),
}
out={}
for pn,P in PAN.items():
    out[pn]={}
    for col in ('blue','red'):
        m=SERIES[col](R,G,B); out[pn][col]={}
        for x in P['xs']:
            xc=int(round(P['x0']+x*P['ppx']))
            win=m[P['top']:P['bot'], xc-6:xc+7]
            if pn=='b_fy_camber': win=m[max(P['top'],700):P['bot'], xc-6:xc+7] if x<=15 else m[P['top']:P['bot'], xc-6:xc+7]
            colmask=win.sum(1)>=3
            off=P['top'] if not (pn=='b_fy_camber' and x<=15) else max(P['top'],700)
            cl=clusters(colmask)
            items=[]
            for (s,e) in cl:
                n=int(win[s:e+1].sum())
                if n<20: continue
                yc=off+(s+e)/2
                items.append((round(float(P['ymap'](yc)),4),n,e-s+1))
            out[pn][col][x]=items
for pn in out:
    print('==',pn)
    for col in out[pn]:
        print(col,{x:v for x,v in out[pn][col].items()})
json.dump(out,open('/tmp/claude-0/-home-user-MTB-Tire-Tread-Knobs-Air-Pressure/54494504-78b0-5fba-88ee-c0ca1e18468b/scratchpad/fig12_raw.json','w'))
