"""Writes the data block pasted into index.html (CONFIGS, STATIC_STIFFNESS, KNOB_MODEL, PROFILES)."""
import json, sys
from paper_tables import T, P, META, STATIC, KNOB
HERE=sys.argv[1] if len(sys.argv)>1 else '.'
curves=json.load(open(HERE+'/curves_by_config.json')); prof=json.load(open(HERE+'/profiles_final.json'))
def arr(a): return '['+','.join('[%g,%g]'%(x,y) for x,y in a)+']'
out=[]
for key,id_,wheel,width,tread,rim,nom,sm,cm,tw,twsrc,printed in META:
    pts=[]
    for psi in sorted(T[key]):
        c=T[key][psi]; a=P[key][psi]
        pts.append("%d:[%s,%s,%s,%s, %s,%s,%s,%s]"%(psi,c[0],c[1],c[2],c[3],a[0],a[1],a[2],a[3]))
    pr="{"+", ".join("%d:[%s]"%(k,",".join("'%s'"%x for x in v)) for k,v in printed.items())+"}"
    extra=""
    if key=='k23':
        extra=",\n    fit:{ psi:25, slip:{B:8.46,C:0.96,D:1.295,E:0.19}, camber:{B:2.1,C:0.34,D:1.295,E:-1}, selfAlign:{B:0.62,C:71.95,D:-0.0044,E:0} }"
    if id_ in curves:
        c=curves[id_]
        extra=",\n    curves:{ psi:%d, src:'%s',\n      fy:%s,\n      fc:%s,\n      mz:%s }"%(c['psi'],c['src'],arr(c['fy']),arr(c['fc']),arr(c['mz']))
    out.append("  { id:'%s', wheel:'%s', width:%s, tread:'%s', rim:%d, nominal:%d, slipMax:%s, camberMax:%s,\n    tw:%s, twSrc:'%s', printed:%s,\n    pts:{ %s }%s },"%(id_,wheel,width,tread,rim,nom,sm,cm,tw,twsrc,pr,",\n          ".join(pts),extra))
js="const CONFIGS = [\n"+"\n".join(out)+"\n];\n\n"
js+="/* Fig. 8 (PRINTED): static stiffness of the four knobby tires at their nominal rim and pressure, N/m.\n   The paper prints 60,365 for BOTH the 27.5×2.8″ and the 29×3.0″ radial bars; kept as printed. */\n"
js+="const STATIC_STIFFNESS = [\n"+"\n".join("  { id:'%s', lateral:%d, radial:%d },"%s for s in STATIC)+"\n];\n\n"
js+="/* Fig. 14 + 18: the paper's knobs-as-springs model for the 29×2.3″ knobby on 25 mm. Knobs act as springs IN PARALLEL (tread\n   stiffness = n × kKnob) and that tread sits IN SERIES with the bald carcass (Eq. 7: 1/K = 1/Kcarcass + 1/Ktread).\n   kKnob and the 25 psi values are printed; n is read (whole knobs); carcass at the other pressures is read (±5 %). */\n"
js+="const KNOB_MODEL = { kKnob:%d, psi:%s, nKnobs:%s, carcass:%s, measured25:%d, printed25:{ tread:118047, carcass:39912, measured:27710, calc:29827 } };\n\n"%(KNOB['k_knob'],KNOB['psi'],KNOB['n_knobs'],KNOB['carcass'],KNOB['measured_25'])
js+="/* Fig. 4 + 10: tire cross-section outlines traced from the paper (mm; x from the tread centreline, y downward from the crown).\n   Scale per outline = its pixel width ÷ the tread width the paper prints (±0.5 mm). Outlines were measured on the paper's rims. */\n"
pj={}
for k,v in prof.items():
    key=k.replace('_fig10','')
    if k.endswith('_fig10'):
        if key=='k23_25': pj.setdefault(key,{}).update(bald={'widthMm':v['baldWidthMm'],'radiusMm':v['baldRadiusMm'],'pts':v.get('baldPts',[])})
        if key=='f25_25': pj[key]={'widthMm':v['widthMm'],'radiusMm':v['radiusMm'],'pts':v['pts'],'bald':{'widthMm':v['baldWidthMm'],'radiusMm':v['baldRadiusMm'],'pts':[]},'src':'Fig. 10'}
    else:
        pj[key]={'widthMm':v['widthMm'],'radiusMm':v['radiusMm'],'pts':v['pts'],'src':'Fig. 4'}
def pts(a): return '['+','.join('[%g,%g]'%(x,y) for x,y in a)+']'
lines=[]
for k,v in pj.items():
    b=v.get('bald'); bs=''
    if b: bs=",\n    bald:{ widthMm:%g, radiusMm:%g, pts:%s }"%(b['widthMm'],b['radiusMm'],pts(b['pts']))
    lines.append("  %s:{ src:'%s', widthMm:%g, radiusMm:%g,\n    pts:%s%s }"%(k,v['src'],v['widthMm'],v['radiusMm'],pts(v['pts']),bs))
js+="const PROFILES = {\n"+",\n".join(lines)+"\n};\n"
open(HERE+'/data_block.js','w').write(js)
print(len(js),'chars; profile keys',list(pj))
