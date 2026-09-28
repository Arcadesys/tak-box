"""Render selected paths from the actual protected-case trial G-code."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

OUT=Path(__file__).resolve().parent.parent
PLATE='00-smooth-case-fit-trial'
# CAD-coordinate crops, converted with both saved 3MF transforms below.
VIEWS=[
 ('fit-protected-hinge-frame',5.4,(-21,1,76,88),'HINGE / moving gap'),
 ('fit-recessed-catch-B',15.0,(217,227,30,55),'RELEASE / tongue and stop'),
 ('fit-recessed-catch-B',24.6,(217,227,30,55),'RELEASE / window roof'),
 ('fit-recessed-catch-B',27.2,(217,227,30,55),'CATCH / ramp and tooth'),
]
p=OUT/'gcode'/('plate'+PLATE+'.gcode')
r=json.loads((OUT/'reports/package-report.json').read_text())['plates'][PLATE]
g=json.loads((OUT/'reports/geometry.json').read_text())['parts']
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def apply(pt,t):return [sum(pt[i]*t[3*i+j] for i in range(3))+t[9+j] for j in range(3)]
def crop(stem,b):
    tr=next(t for t in r['geometry']['object_transforms_and_bounds'] if '/'+stem+'.stl_' in t['path'])
    with ZipFile(OUT/r['3mf']) as z:
        doc=ET.fromstring(z.read(tr['path'].lstrip('/')))
        vs=doc.findall('.//m:vertex',ns)
        mv=[min(float(v.attrib[a]) for v in vs) for a in 'xyz']
    cad=g[stem]['bounds']
    ct=tr['component_matrix']+tr['component_translation_mm']
    bt=tr['build_item_matrix']+tr['build_item_translation_mm']
    pts=[apply(apply([x-cad[0]+mv[0],y-cad[2]+mv[1],mv[2]],ct),bt) for x in b[:2] for y in b[2:]]
    return min(t[0] for t in pts),max(t[0] for t in pts),min(t[1] for t in pts),max(t[1] for t in pts)
levels=set(v[1] for v in VIEWS);paths={h:[] for h in levels}
x=y=z=e=0.;relative=True;feature='';support=0
for raw in p.open():
    if raw.startswith(';TYPE:'):feature=raw[6:].strip()
    s=raw.split(';')[0].strip();cmd=s.split(' ')[0]
    if cmd=='M83':relative=True
    if cmd=='M82':relative=False
    if cmd=='G92' and 'E' in s:e=float(re.search(r'E([-\d.]+)',s)[1])
    if cmd not in ('G0','G1'):continue
    vals={a:float(b) for a,b in re.findall(r'([XYZE])([-\d.]+)',s)}
    nx,ny,nz=vals.get('X',x),vals.get('Y',y),vals.get('Z',z)
    de=vals.get('E',0) if relative else vals.get('E',e)-e
    if 'E' in vals:e=vals['E'] if not relative else e+vals['E']
    if de>0 and (nx!=x or ny!=y) and feature!='Custom':
        if 'Support' in feature:support+=1
        for h in levels:
            if abs(nz-h)<.005:paths[h].append(((x,y),(nx,ny)))
    x,y,z=nx,ny,nz
fig,axes=plt.subplots(2,2,figsize=(16,10),facecolor='#101722');rows=[]
for ax,(stem,h,b,title) in zip(axes.flat,VIEWS):
    x0,x1,y0,y1=crop(stem,b)
    seg=[seg for seg in paths[h] if any(x0<=x<=x1 and y0<=y<=y1 for x,y in seg)]
    assert seg,(stem,h,'empty crop')
    ax.set_facecolor('#101722');ax.add_collection(LineCollection(seg,colors='#ffffff',linewidths=1))
    ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal')
    ax.set_title(title+f' / Z {h:.1f} mm',fontsize=18,color='white',fontweight='bold')
    ax.tick_params(colors='#d3dfeb',labelsize=12)
    for sp in ax.spines.values():sp.set_color('#637087')
    rows.append({'source':stem,'layer_mm':h,'crop_printer_xy_mm':[x0,x1,y0,y1],'visible_segments':len(seg)})
fig.suptitle('SMOOTH CASE / ACTUAL TRIAL TOOLPATHS',fontsize=25,color='white',fontweight='bold')
fig.text(.5,.025,'White: deposited material. Physical hinge release, bridging and catch flex remain untested.',ha='center',fontsize=15,color='white')
fig.tight_layout(rect=[0,.05,1,.95]);(OUT/'previews').mkdir(exist_ok=True)
fig.savefig(OUT/'previews/05-toolpath-checks.png',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)
assert support==0,support
report={'gcode_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'support_extrusion_segments':support,'views':rows,'physical_acceptance':False}
(OUT/'reports/toolpath-preview.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
