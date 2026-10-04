"""Rebuild geometry, checks, STL/STEP, generic 3MF and mesh-based previews."""
from pathlib import Path
from collections import Counter
import datetime, hashlib, importlib.metadata, json, struct, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import cadquery as cq
import folio as c

OUT=Path(__file__).resolve().parents[1]
for d in ('reports','models','stl','plates','previews','logs'): (OUT/d).mkdir(exist_ok=True)
report={'physical_acceptance':False,'checks':{},'environment':{m:importlib.metadata.version(m) for m in ('cadquery','cadquery-ocp','numpy','matplotlib')},
        'baseline':'88bc668a1752b2dbc1a2edfc967dcbb525b6f4d0',
        'command':'python v17-compact-folio/source/build.py','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'piece_package':'v16 existing 19.5 x 19.5 x 8 printed flats; pieces/cat-capstone.step and witch-capstone.step',
        'slicing':'unavailable: ElegooSlicer is not installed; generic 3MF is unsliced',
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}

def check(name,ok,detail):
    report['checks'][name]={'pass':bool(ok),'detail':detail}
    (OUT/'reports/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(('PASS ' if ok else 'FAIL ')+name+': '+str(detail),flush=True)
    if not ok: raise RuntimeError(name)

def ov(a,b): return a.intersect(b).Volume()
def dims(s):
    b=s.BoundingBox();return [round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)]

parts={'shell':c.shell(),'retaining-lid':c.retaining_lid(),'board-A':c.board('A'),'board-B':c.board('B'),
       'grid-A':c.grid('A'),'grid-B':c.grid('B')}
check('valid-solids',all(p.isValid() and len(p.Solids())==1 for p in parts.values()),{n:dims(p) for n,p in parts.items()})
fixed=[parts['shell'],parts['retaining-lid'],parts['board-A'],parts['grid-A']]
check('assembled-part-clearances',max(ov(a,b) for i,a in enumerate(fixed) for b in fixed[i+1:])<.01,'shell, independent roof and board A')
movement={}
for angle in range(0,181,5):
    b=[c.fold(parts[n],angle) for n in ('board-B','grid-B')]
    movement[angle]=round(max(ov(a,q) for a in fixed for q in b),6)
check('fold-sweep',max(movement.values())<.01,movement)
closed=fixed+[c.fold(parts[n],180) for n in ('board-B','grid-B')]
check('board-playability',c.P-20.>=15.,{'pitch_mm':c.P,'field_mm':5*c.P,'gap_for_20mm_flat':c.P-20.,'grid_flush':True,'board_thickness_mm':c.BOARD})
fit={}
for size in (19.5,20.):
    stones=c.pieces(size)[:42]; caps=c.real_caps()
    allpieces=stones+caps
    fit[size]={'max_shell_or_roof_overlap_mm3':round(max(ov(p,q) for p in allpieces for q in fixed),6),
               'min_roof_clearance_mm':round(c.SHELL_H-max(p.BoundingBox().zmax for p in allpieces),3),
               'piece_to_piece_overlap_mm3':round(max(ov(p,q) for i,p in enumerate(allpieces) for q in allpieces[i+1:]),6)}
check('42-flats-and-real-pawns',all(r['max_shell_or_roof_overlap_mm3']<.01 and r['piece_to_piece_overlap_mm3']<.01 and r['min_roof_clearance_mm']>=1 for r in fit.values()),fit)
check('transport-retention',c.SHELL_H-20.5<c.THICK and .4<c.THICK,
      {'normal_wall_to_roof_gap_mm':c.SHELL_H-20.5,'scallop_to_lid_tongue_gap_mm':.4,
       'minimum_flat_dimension_mm':8.,'cap_minimum_envelope_mm':19.4,
       'limits':'Closed rigid roof blocks overtopping; screws hold all leaves. This is a geometric barrier check, not a shake/strength test.'})
# Translation attempts demonstrate walls and roof blocking migration of an
# upright leading stone, including its finger scallop. Tipping is bounded by
# the roof gap but is not an exhaustive rigid-body configuration-space proof.
probe=c.pieces()[0]
blocked={str(v):round(ov(probe.translate(v),c.shell())+ov(probe.translate(v),c.retaining_lid()),4)
         for v in ((0,-2.,0),(0,0,2.),(-2.,0,0),(2.,0,0))}
check('representative-escape-attempts',all(v>.01 for v in blocked.values()),blocked)
# Actual M3 screw shaft and head envelopes, closed; thread engagement and
# clamp strength require the physical hardware coupon.
hardware=[]
for x,y in c.SCREWS:
    shaft=c.cylinder(1.5,16.,32.,x,y)
    head=c.cylinder(3.,32.,35.,x,y)
    hardware.extend([shaft,head])
check('closed-screw-clearance',max(ov(h,p) for h in hardware for p in closed)<.01,
      {'hardware':'4 M3x16 socket-head screws, 4 DIN934 nuts; nominal 6mm head x 3mm height',
       'screw_tip_z_mm':16.,'nut_seat_z_mm':18.,'nut_thickness_mm':2.4,'shaft_hole_d_mm':3.4})
envelope=cq.Compound.makeCompound(closed+hardware)
ext=dims(envelope)
check('compact-envelope',ext[2]<40.,{'closed_with_screw_heads_mm':ext,'v16_mm':[101.,202.,51.],
      'volume_reduction_percent':round(100*(1-np.prod(ext)/(101*202*51)),1)})
check('bed-fit',all(max(dims(p)[:2])<=250 for p in parts.values()),'256 mm bed; board hinge pair occupies 196 x 202 mm')

def mesh(s):
    vs,fs=s.tessellate(.08,.15)
    return np.array([[v.x,v.y,v.z] for v in vs]),np.array(fs,dtype=int)

def read_stl(path):
    data=path.read_bytes(); count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*count: raise ValueError('unexpected STL encoding')
    tri=np.array([struct.unpack_from('<12f',data,84+50*i)[3:] for i in range(count)]).reshape(-1,3,3)
    vs,ix=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True)
    return vs,ix.reshape(-1,3)

def mesh_check(vs,fs):
    edges=Counter(tuple(sorted((int(a),int(b)))) for f in fs for a,b in zip(f,np.roll(f,-1)))
    winding=Counter()
    for f in fs:
        for a,b in zip(f,np.roll(f,-1)): winding[(int(a),int(b))]+=1
    volume=np.einsum('ij,ij->i',vs[fs[:,0]],np.cross(vs[fs[:,1]],vs[fs[:,2]])).sum()/6
    area=np.linalg.norm(np.cross(vs[fs[:,1]]-vs[fs[:,0]],vs[fs[:,2]]-vs[fs[:,0]]),axis=1)
    return {'triangles':len(fs),'closed':all(n==2 for n in edges.values()),
            'oriented':all(n==winding[(b,a)] for (a,b),n in winding.items()),
            'positive_volume':bool(volume>0),'nondegenerate':bool(np.all(area>1e-10))}

posed={}
for name,s in parts.items():
    cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
    # The independent retention lid prints flat-roof down, tongues upward.
    flip=name=='retaining-lid'
    ps=s.rotate((0,0,0),(1,0,0),180) if flip else s
    # Grid and body retain their common frame in a colour plate below.
    ps=c.pose(ps);posed[name]=ps
    cq.exporters.export(ps,str(OUT/'stl'/f'{name}.stl'),tolerance=.08,angularTolerance=.15)
    v,f=read_stl(OUT/'stl'/f'{name}.stl')
    r=mesh_check(v,f)
    check('mesh-'+name,all(r[k] for k in ('closed','oriented','positive_volume','nondegenerate')),r)
trials=c.fit_trial()
for i,s in enumerate(trials):
    name=f'trial-fastener-{i}';posed[name]=c.pose(s)
    cq.exporters.export(posed[name],str(OUT/'stl'/f'{name}.stl'))
    v,f=read_stl(OUT/'stl'/f'{name}.stl');r=mesh_check(v,f)
    check('mesh-'+name,all(r[k] for k in ('closed','oriented','positive_volume','nondegenerate')),r)
# A two-stone lane with its real roof tongue: supports a small first trial.
lane_trial=c.shell().intersect(c.box(6.5,29.7,7.5,29.,0,23.))
lid_trial=c.retaining_lid().intersect(c.box(6.5,29.7,7.5,29.,12.,24.))
for name,s in [('trial-lane',lane_trial),('trial-lane-roof',lid_trial)]:
    cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
    if name.endswith('roof'): s=s.rotate((0,0,0),(1,0,0),180)
    posed[name]=c.pose(s)
    cq.exporters.export(posed[name],str(OUT/'stl'/f'{name}.stl'))
    v,f=read_stl(OUT/'stl'/f'{name}.stl');r=mesh_check(v,f)
    check('mesh-'+name,all(r[k] for k in ('closed','oriented','positive_volume','nondegenerate')),r)

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def plate(name,items):
    model=ET.Element('{'+NS+'}model',unit='millimeter')
    resources=ET.SubElement(model,'{'+NS+'}resources');build=ET.SubElement(model,'{'+NS+'}build')
    expected=[]
    for i,(label,s) in enumerate(items,1):
        v,f=mesh(s);expected.append((label,v,f))
        ob=ET.SubElement(resources,'{'+NS+'}object',id=str(i),type='model',name=label)
        me=ET.SubElement(ob,'{'+NS+'}mesh');verts=ET.SubElement(me,'{'+NS+'}vertices');tris=ET.SubElement(me,'{'+NS+'}triangles')
        for q in v: ET.SubElement(verts,'{'+NS+'}vertex',**dict(zip(('x','y','z'),map(lambda x:f'{x:.7f}',q))))
        for q in f: ET.SubElement(tris,'{'+NS+'}triangle',**dict(zip(('v1','v2','v3'),map(str,q))))
        ET.SubElement(build,'{'+NS+'}item',objectid=str(i))
    path=OUT/'plates'/f'{name}.3mf'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('3D/3dmodel.model'))
    objects=root.findall('.//{'+NS+'}object')
    ok=len(objects)==len(expected)
    for ob,(label,v,f) in zip(objects,expected):
        vv=np.array([[float(el.attrib[k]) for k in ('x','y','z')] for el in ob.findall('.//{'+NS+'}vertex')])
        ff=np.array([[int(el.attrib[k]) for k in ('v1','v2','v3')] for el in ob.findall('.//{'+NS+'}triangle')])
        ok=ok and ob.attrib['name']==label and np.allclose(vv,v,atol=1e-6) and np.array_equal(ff,f)
        bb=vv.max(axis=0)-vv.min(axis=0)
        ok=ok and max(bb[:2])<=250 and vv[:,:2].min()>=0 and vv[:,:2].max()<=256 and vv[:,2].min()>=-1e-5
    check('3mf-readback-'+name,ok,{'objects':[x[0] for x in expected],'units':'mm','sliced':False})

plate('00-fit-trials',[(n,s.translate((10+i*32,10,0))) for i,(n,s) in enumerate((n,s) for n,s in posed.items() if n.startswith('trial-fastener'))])
plate('00b-lane-retention',[('lane',posed['trial-lane'].translate((10,10,0))),('roof',posed['trial-lane-roof'].translate((45,10,0)))])
plate('01-shell-and-roof',[('shell',posed['shell'].translate((10,10,0))),('roof',posed['retaining-lid'].translate((115,10,0)))])
plate('02-folding-board',[(n,s.translate((25,25,-c.H))) for n,s in parts.items() if n.startswith(('board','grid'))])

# Render triangulated STEP readback, ensuring the preview is generated from
# the exported deliverable rather than an unrelated concept illustration.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
loaded={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in parts}
def render(name,scene,title):
    fig=plt.figure(figsize=(11,8));ax=fig.add_subplot(111,projection='3d')
    vertices=[]
    for s,col,alpha in scene:
        v,f=mesh(s);vertices.extend(v)
        ax.add_collection3d(Poly3DCollection(v[f],facecolor=col,edgecolor='none',alpha=alpha))
    v=np.array(vertices);lo=v.min(axis=0);hi=v.max(axis=0);mid=(lo+hi)/2;span=max(hi-lo)*.58
    ax.set_xlim(mid[0]-span,mid[0]+span);ax.set_ylim(mid[1]-span,mid[1]+span);ax.set_zlim(mid[2]-span,mid[2]+span)
    ax.set_box_aspect((1,1,1));ax.view_init(32,-60);ax.set_axis_off();ax.set_title(title,pad=5)
    fig.tight_layout();fig.savefig(OUT/'previews'/f'{name}.png',dpi=160);plt.close(fig)
colors={'shell':'#48515e','retaining-lid':'#8290a1','board-A':'#303845','board-B':'#303845','grid-A':'#f5ede0','grid-B':'#f5ede0'}
render('01-closed',[(c.fold(s,180) if n.endswith('B') else s,colors[n],1) for n,s in loaded.items()]+[(s,'#bbbbbb',1) for s in hardware],f'v17 compact folio — {ext[0]:g} × {ext[1]:g} × {ext[2]:g} mm incl. screw heads')
render('02-open-board',[(s,colors[n],1) for n,s in loaded.items()],'5 × 5 field, 36 mm pitch — board folds open; storage stays upright')
piece_scene=[(s,'#db8a42' if i<21 else '#916aad',1) for i,s in enumerate(c.pieces()[:42])]
piece_scene +=[(s,'#db8a42' if i==0 else '#916aad',1) for i,s in enumerate(c.real_caps())]
render('03-storage',[(loaded['shell'],colors['shell'],.55)]+piece_scene,'42 flats upright in six channels, plus the two real pawn capstones')
render('04-exploded',[(loaded['shell'],colors['shell'],.7)]+piece_scene+[(loaded['retaining-lid'].translate((0,0,30)),colors['retaining-lid'],1),
       (loaded['board-A'].translate((0,0,60)),colors['board-A'],1),(loaded['grid-A'].translate((0,0,60)),colors['grid-A'],1),
       (c.fold(loaded['board-B'],180).translate((0,0,90)),colors['board-B'],1)],'Shell → independent retaining roof → folding board → four corner screw clamps')
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ('source','models','stl','plates','previews') for p in (OUT/d).glob('*') if p.is_file()}
(OUT/'reports/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALL DIGITAL CHECKS PASS. Physical retention, fit and slicing remain untested.',flush=True)
