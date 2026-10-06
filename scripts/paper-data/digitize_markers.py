"""Colour-segmentation helper used to read the paper's Fig. 16 / 17 markers.
See README.md in this folder for the procedure and the calibration numbers."""
import numpy as np, json, sys
from PIL import Image, ImageDraw

SERIES = {  # name -> (color predicate)
 'blue':   lambda r,g,b: (r<90)&(g<90)&(b>190),
 'red':    lambda r,g,b: (r>200)&(g<70)&(b<70),
 'cyan':   lambda r,g,b: (r<90)&(g>150)&(g<215)&(b>215),
 'magenta':lambda r,g,b: (r>200)&(g<90)&(b>190),
 'green':  lambda r,g,b: (r<90)&(g>140)&(g<200)&(b>50)&(b<140),
 'gold':   lambda r,g,b: (r>230)&(g>165)&(g<215)&(b<90),
 'orange': lambda r,g,b: (r>215)&(g>95)&(g<150)&(b>25)&(b<100),
}
def load(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(int)

def clusters(col_mask, gap=2):
    ys=np.where(col_mask)[0]; out=[]
    if len(ys)==0: return out
    start=prev=ys[0]
    for y in ys[1:]:
        if y-prev>gap: out.append((start,prev)); start=y
        prev=y
    out.append((start,prev)); return out

def extract(a, panel, ycal, xcal, pressures, halfw=6, minpx=18):
    """panel=(x0,y0,x1,y1) plot frame; ycal(ypx)->value; xcal(psi)->xpx. Returns {series:{psi:[(value,npx,ycenter)...]}}"""
    x0,y0,x1,y1=panel
    res={}
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    for name,pred in SERIES.items():
        m=pred(R,G,B); res[name]={}
        for p in pressures:
            xc=int(round(xcal(p)))
            win=m[y0+3:y1-3, xc-halfw:xc+halfw+1]
            colmask=win.sum(1)>=3     # need >=3 of the 13 columns colored on that row
            cl=clusters(colmask)
            items=[]
            for (s,e) in cl:
                npx=int(win[s:e+1].sum())
                if npx<minpx: continue
                yc=y0+3+(s+e)/2
                items.append((round(float(ycal(yc)),4), int(npx), round(float(yc),1), int(e-s+1)))
            if items: res[name][p]=items
    return res
