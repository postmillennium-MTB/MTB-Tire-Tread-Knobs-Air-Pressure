"""Turns the hand-checked tables (fig17_table.py + the Fig. 16 table below) into the CONFIGS block pasted into index.html.
Run from this folder:  python3 gen_configs.py   ->  writes configs.js"""
from fig17_table import T
# Fig 16: (area cm2, void %, length mm, width mm) — read from Fig 16; (*) = printed in Fig 5 at nominal pressure
P = {
 'k23':  {10:(66,81,155,55), 15:(53.5,81.5,137,50), 20:(45,81,134,43), 25:(34.5,78.1,122,36), 30:(30.5,76.5,121,32), 35:(29.5,76.5,119,31), 40:(26.5,75.5,112,30), 50:(24.5,75,108,28.5)},
 'f25':  {10:(55,75.5,165,42.5), 15:(38,69.5,144,33.5), 20:(31.5,67.5,130,31.5), 25:(28,66,116,30.5), 30:(23.5,62,111,27.5), 35:(22,61,104.5,26.5), 40:(19.5,59,101,24.5), 50:(17.5,56.5,96.5,23)},
 'b25':  {10:(50,20,166,38), 15:(37.5,19,145,32.5), 20:(29.8,17.5,129,29), 25:(27.5,19.5,121,27.5), 30:(22.3,16.5,114,25), 40:(17.8,14.5,104,21.5), 50:(15.2,11.5,96,19.5)},
 'b23':  {10:(52,5.5,156,43), 15:(39,3.5,141,35.5), 20:(31,3,132,30.5), 25:(26,2,116,27.5), 30:(22.5,1.5,110.5,26), 40:(18,3.5,100.5,22.5), 50:(15,4,94.5,20)},
 'k23n': {10:(58.7,77,146,51), 25:(32,70.5,115.5,35)},
 'f25n': {10:(43,71.5,161,34), 25:(26.8,71.5,119,29)},
 'k275': {10:(62.5,77,141,56.5), 20:(35.8,76.1,117,39)},
 'k29p': {10:(66.5,74.8,152,55.3), 20:(39.2,69.7,127,39)},
 'k26':  {10:(70,82.2,150,59), 15:(58.4,80.6,130,57)},
}
# registry: key, id, wheel, width, tread, rim, nominal psi, measured slip max (deg), measured camber max (deg), t_w, t_w source, printed points
META = [
 ('k23',  'k23_25',  '29',   2.3, 'knobby',     25, 25, 2.4, 20, -2.118, 'printed',   {25:('stiffness','patch')}),
 ('b23',  'b23_25',  '29',   2.3, 'bald',       25, 25, 2.0, 13,  0.0,   'estimated', {}),
 ('k23n', 'k23_22',  '29',   2.3, 'knobby',     22, 25, 2.4, 20, -2.118, 'assumed',   {}),
 ('f25',  'f25_25',  '29',   2.5, 'file-tread', 25, 25, 2.0, 19, -0.4,   'estimated', {}),
 ('b25',  'b25_25',  '29',   2.5, 'bald',       25, 25, 1.7, 19,  1.9,   'estimated', {}),
 ('f25n', 'f25_22',  '29',   2.5, 'file-tread', 22, 25, 2.0, 19, -0.4,   'assumed',   {}),
 ('k29p', 'k29_45',  '29',   3.0, 'knobby',     45, 20, 1.5, 15,  7.0,   'estimated', {20:('patch',)}),
 ('k275', 'k275_38', '27.5', 2.8, 'knobby',     38, 20, 2.3, 22, -1.2,   'estimated', {20:('patch',)}),
 ('k26',  'k26_86',  '26',   4.0, 'knobby',     86, 15, 1.0, 15, -1.1,   'estimated', {15:('patch',)}),
]
out=[]
for key,id_,wheel,width,tread,rim,nom,sm,cm,tw,twsrc,printed in META:
    pts=[]
    for psi in sorted(T[key]):
        c=T[key][psi]; a=P[key][psi]
        pts.append("%d:[%s,%s,%s,%s, %s,%s,%s,%s]"%(psi,c[0],c[1],c[2],c[3],a[0],a[1],a[2],a[3]))
    pr = "{"+", ".join("%d:[%s]"%(k,",".join("'%s'"%x for x in v)) for k,v in printed.items())+"}"
    fit = ""
    if key=='k23':
        fit = ",\n    fit:{ psi:25, slip:{B:8.46,C:0.96,D:1.295,E:0.19}, camber:{B:2.1,C:0.34,D:1.295,E:-1}, selfAlign:{B:0.62,C:71.95,D:-0.0044,E:0} }"
    out.append("  { id:'%s', wheel:'%s', width:%s, tread:'%s', rim:%d, nominal:%d, slipMax:%s, camberMax:%s,\n    tw:%s, twSrc:'%s', printed:%s,\n    pts:{ %s }%s },"%(id_,wheel,width,tread,rim,nom,sm,cm,tw,twsrc,pr,",\n          ".join(pts),fit))
open('configs.js','w').write("const CONFIGS = [\n"+"\n".join(out)+"\n];\n")
print("\n".join(out)[:1800])
