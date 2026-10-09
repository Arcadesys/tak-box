"""Build and verify a V24 four-colour boards and affected mechanics; no printer jobs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, platform, sys, xml.etree.ElementTree as ET
import cadquery as cq
import numpy as np
import trimesh
import inlays as c

OUT = c.OUT
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
TAG = '{'+NS+'}'
ET.register_namespace('', NS)
checks = []


def check(name, ok, detail=None):
    checks.append({'name': name, 'pass': bool(ok), 'detail': detail})
    print(name, 'PASS' if ok else 'FAIL', flush=True)
    if not ok:
        raise RuntimeError((name, detail))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh(shape):
    vs, fs = shape.tessellate(.04, .1)
    m = trimesh.Trimesh(vertices=np.round([[v.x,v.y,v.z] for v in vs],6), faces=fs, process=True)
    m.merge_vertices(digits_vertex=6)
    m.remove_unreferenced_vertices()
    check('mesh topology', m.is_watertight and m.is_winding_consistent and m.volume>0,
          {'bodies':m.body_count, 'triangles':len(m.faces)})
    return m


def export(label, shape):
    check(label+' CAD validity', shape.isValid() and shape.Volume()>0)
    if label.endswith('-body'):
        check(label+' one structural solid', len(shape.Solids())==1)
    step = OUT/'models'/f'{label}.step'
    cq.exporters.export(shape, str(step))
    loaded = cq.importers.importStep(str(step)).val()
    check(label+' STEP readback', loaded.isValid() and abs(loaded.Volume()-shape.Volume())<.01)
    m=mesh(loaded)
    stl=OUT/'models'/f'{label}.stl'
    m.export(stl)
    read=trimesh.load_mesh(stl)
    check(label+' STL readback', read.is_watertight and read.is_winding_consistent and abs(read.volume-m.volume)<.01)
    return loaded


def project(name, groups, silk=True):
    root=ET.Element(TAG+'model',unit='millimeter')
    ET.SubElement(root,TAG+'metadata',name='BambuStudio:3mfVersion').text='1'
    resources=ET.SubElement(root,TAG+'resources')
    build=ET.SubElement(root,TAG+'build')
    config=ET.Element('config')
    materials=ET.SubElement(resources,TAG+'basematerials',id='1000')
    for role in ('body','grid','orange','purple'):
        ET.SubElement(materials,TAG+'base',name=role,displaycolor=c.ROLES[role][1]+'FF')
    expected={}; next_id=1; group_bounds=[]
    for label,parts,origin in groups:
        b=parts['body'].BoundingBox()
        # Use actual tessellation bounds; OCC bounding boxes include tolerances.
        bounds=mesh(parts['body']).bounds
        delta=(origin[0]-bounds[0,0],origin[1]-bounds[0,1],-bounds[0,2])
        ids=[]
        for role,s in parts.items():
            shifted=s.translate(delta)
            m=mesh(shifted); expected[next_id]=(label+'-'+role,m)
            check(name+'/'+label+'-'+role+' bed bounds',np.all(m.bounds[0]>=-1e-6) and np.all(m.bounds[1]<=[256,256,250]))
            idx=c.slot(role,silk)-1
            ob=ET.SubElement(resources,TAG+'object',id=str(next_id),type='model',name=label+'-'+role,pid='1000',pindex=str(idx))
            me=ET.SubElement(ob,TAG+'mesh'); verts=ET.SubElement(me,TAG+'vertices');tris=ET.SubElement(me,TAG+'triangles')
            for q in m.vertices:
                ET.SubElement(verts,TAG+'vertex',**{k:f'{v:.7f}' for k,v in zip(('x','y','z'),q)})
            for q in m.faces:
                ET.SubElement(tris,TAG+'triangle',**{k:str(v) for k,v in zip(('v1','v2','v3'),q)})
            ids.append((next_id,role,idx+1)); next_id+=1
        gid=next_id;next_id+=1
        ob=ET.SubElement(resources,TAG+'object',id=str(gid),type='model',name=label)
        comp=ET.SubElement(ob,TAG+'components')
        objcfg=ET.SubElement(config,'object',id=str(gid))
        ET.SubElement(objcfg,'metadata',key='name',value=label)
        for oid,role,slot in ids:
            ET.SubElement(comp,TAG+'component',objectid=str(oid))
            part=ET.SubElement(objcfg,'part',id=str(oid),subtype='normal_part')
            ET.SubElement(part,'metadata',key='name',value=label+'-'+role)
            ET.SubElement(part,'metadata',key='extruder',value=str(slot))
        ET.SubElement(build,TAG+'item',objectid=str(gid))
        group_bounds.append((np.array([origin[0],origin[1]]),np.array([origin[0]+b.xlen,origin[1]+b.ylen])))
    for i,(lo,hi) in enumerate(group_bounds):
        for lo2,hi2 in group_bounds[i+1:]:
            check(name+' group separation',max(*(lo2-hi),*(lo-hi2))>=5)
    path=OUT/'plates'/f'{name}.3mf'
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
        z.writestr('Metadata/model_settings.config',ET.tostring(config,encoding='utf-8',xml_declaration=True))
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="text/xml"/></Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with ZipFile(path) as z:
        check(name+' ZIP CRC',z.testzip() is None)
        read=ET.fromstring(z.read('3D/3dmodel.model'))
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
    check(name+' grouped build readback',len(read.find(TAG+'build'))==len(groups))
    for oid,(label,m) in expected.items():
        ob=read.find(f"{TAG}resources/{TAG}object[@id='{oid}']")
        vv=np.array([[float(v.get(k)) for k in ('x','y','z')] for v in ob.findall('.//'+TAG+'vertex')])
        ff=np.array([[int(v.get(k)) for k in ('v1','v2','v3')] for v in ob.findall('.//'+TAG+'triangle')])
        check(name+'/'+label+' mesh readback',ob.get('name')==label and np.allclose(vv,m.vertices,atol=1e-6) and np.array_equal(ff,m.faces))
        slot=int(cfg.find(f".//part[@id='{oid}']/metadata[@key='extruder']").get('value'))
        role=label.rsplit('-',1)[1]
        check(name+'/'+label+' filament slot',slot==c.slot(role,silk))
    return path


def main():
    loaded={}
    for side in ('left','right'):
        p=c.parts(side)
        loaded[side]={role:export(f'board-{side}-{role}',s) for role,s in p.items()}
        for i,(role,s) in enumerate(p.items()):
            for other,t in list(p.items())[i+1:]:
                check(side+'/'+role+' disjoint from '+other,s.intersect(t).Volume()<1e-5)
        assembled=c.union(list(loaded[side].values()))
        reference=c.case.board(side).fuse(c.grid(side)).clean()
        check(side+' filled board matches original envelope',assembled.cut(reference).Volume()<1e-5 and reference.cut(assembled).Volume()<1e-5)
        interface=c.case.box(-1,197,-1,201,0,c.FACE-c.DEPTH-.001)
        check(side+' all sliding interfaces unchanged',p['body'].intersect(interface).cut(c.case.board(side)).Volume()<1e-5 and c.case.board(side).intersect(interface).cut(p['body']).Volume()<1e-5)
        for role,s in list(p.items())[1:]:
            b=s.BoundingBox()
            check(side+'/'+role+' flush 0.6 mm inlay',abs(b.zmax-c.FACE)<1e-6 and abs(b.zmin-(c.FACE-c.DEPTH))<1e-6)
        field=c.case.box(7.6,188.4,9.6,190.4,c.FACE-c.DEPTH,c.FACE)
        check(side+' art stays within field',all(p[role].cut(field).Volume()<1e-5 for role in ('orange','purple','stars')))
        # Exact original 20x20x8 flats and supplied 8 mm flat capstones in V24 trays.
        from loaded_pieces import loaded as load_pieces
        stones=[s for _,s in load_pieces(side)]
        check(side+' exact stored pieces clear replacement',max(s.intersect(assembled).Volume() for s in stones)<1e-5)
        # Check changed filled geometry along the release/slide and folding paths.
        released=c.complete(side,c.case.BOARD_RELEASE)
        obstacles=[cq.importers.importStep(str(c.OUT.parent/'models'/f'{n}.step')).val()
                   for n in ('housing-left','housing-right')]
        obstacles += [c.case.side_hook(c.case.HOOK_OPEN_ANGLE)]
        obstacles += [c.case.tray(s) for s in ('left','right')]
        obstacles += [s for side2 in ('left','right') for _,s in load_pieces(side2)]
        worst=max(c.case.slide(released,side,t).intersect(o).Volume()
                  for t in list(range(0,107,2))+[106] for o in obstacles)
        check(side+' released slide samples clear housings, loaded trays and parked hook',worst<1e-5,{'max_overlap_mm3':worst,'travel_mm':106,'sample_step_mm':2})
        if side=='right':
            left=c.complete('left')
            # Only changed surfaces need new folding checks; check them against
            # every opposite-half housing, tray, loaded piece and playing face.
            left_obstacles=[left,c.case.housing('left'),c.case.tray('left')]+[s for _,s in load_pieces('left')]
            right_obstacles=[assembled,c.case.housing('right'),c.case.tray('right')]+[s for _,s in load_pieces('right')]
            worst=max(max(c.case.fold(assembled,a).intersect(o).Volume() for o in left_obstacles)
                      for a in range(0,181,5))
            worst=max(worst,max(left.intersect(c.case.fold(o,a)).Volume()
                      for a in range(0,181,5) for o in right_obstacles))
            check('filled boards fold past opposite loaded half 0..180 degree samples',worst<1e-5,{'max_overlap_mm3':worst,'sample_step_degrees':5})
    # Probe every cell, including the split central column, and each grid line.
    union=c.union([s for p in loaded.values() for s in p.values()])
    for i in range(5):
        for j in range(5):
            x=26+36*i+(.5 if i==2 else 0);y=28+36*j
            check(f'cell {i+1},{j+1} surface',union.isInside(cq.Vector(x,y,c.FACE-.01),1e-6))
    white=c.union([p['grid'] for p in loaded.values()])
    for k in range(6):
        for x,y in ((8+36*k,28),(26,10+36*k)):
            check(f'white grid {x},{y}',white.isInside(cq.Vector(x,y,c.FACE-.01),1e-6))
    groups=[('board-'+side,loaded[side],(7 if side=='left' else 121,7)) for side in ('left','right')]
    project('02-boards-black-white-silk',groups,True)
    trial={role:export('coupon-'+role,s) for role,s in c.coupon().items()}
    project('00-inlay-trial-black-white-silk',[('inlay-trial',trial,(8,8))],True)
    sources=list((OUT/'source').rglob('*.py'))+[c.OUT.parent/'source/case.py',c.OUT.parent/'source/loaded_pieces.py']
    report={'checks':checks,'python':sys.version,'cadquery':cq.__version__,'trimesh':trimesh.__version__,
            'numpy':np.__version__,'platform':platform.platform(),
            'sources_sha256':{str(p.relative_to(c.REPO)):sha(p) for p in sources},
            'baseline':'V24 b766181 mechanical board; accepted V23 four-colour artwork; v16 retained celestial CAD',
            'field_mm':[180,180],'pitch_mm':36,'inlay_depth_mm':.6,'physical_acceptance':False,
            'limitations':['Motion sampled, not continuous swept-volume proof.','Physical fit, friction, colour bleed and silk bonding unobserved.','Silk filament brand/profile not selected; silk dry slice is illustrative.']}
    (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board replacements and small colour trial verified.',flush=True)


if __name__=='__main__':
    try:
        main()
    finally:
        (OUT/'reports/checks-latest.json').write_text(json.dumps(checks,indent=2)+'\n')
