import sys, numpy as np
from PIL import Image
def runs(mask1d, minlen):
    out=[];start=None
    for i,v in enumerate(mask1d):
        if v and start is None: start=i
        if (not v) and start is not None:
            if i-start>=minlen: out.append((start,i-1))
            start=None
    if start is not None and len(mask1d)-start>=minlen: out.append((start,len(mask1d)-1))
    return out
def frames(path, minlen=450):
    a=np.asarray(Image.open(path).convert('L')).astype(int)
    dark=a<110
    H=[];V=[]
    for y in range(a.shape[0]):
        for (x0,x1) in runs(dark[y],minlen): H.append((y,x0,x1))
    for x in range(a.shape[1]):
        for (y0,y1) in runs(dark[:,x],minlen): V.append((x,y0,y1))
    return H,V
if __name__=='__main__':
    H,V=frames(sys.argv[1], int(sys.argv[2]) if len(sys.argv)>2 else 450)
    # merge adjacent rows/cols
    def merge(L):
        L=sorted(L); out=[]
        for t in L:
            if out and abs(t[0]-out[-1][0])<=2 and abs(t[1]-out[-1][1])<8: continue
            out.append(t)
        return out
    print('H lines (y,x0,x1):'); [print(' ',h) for h in merge(H)]
    print('V lines (x,y0,y1):'); [print(' ',v) for v in merge(V)]
