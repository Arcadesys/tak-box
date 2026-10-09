"""Retained V24 multipart 3MF writer for V26 exported board geometry.
Original: v24/REFERENCE/board-inlays/source/build.py
Original SHA256: 7ee513fa792edcd82f210ef9c3ffd1e8b7c58395e5de0cd23739a6df2c423612"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parents[1]
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
TAG='{'+NS+'}'
ET.register_namespace('',NS)
ROLES={'body':(1,'#111111'),'grid':(2,'#FFFFFF'),'stars':(2,'#FFFFFF'),'orange':(3,'#D6A54C'),'purple':(4,'#B887DD')}
c=SimpleNamespace(ROLES=ROLES,slot=lambda role,silk:ROLES[role][0])
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail))
 if not ok:raise RuntimeError((name,detail))
def mesh(shape):
    vs, fs = shape.tessellate(.04, .1)
    m = trimesh.Trimesh(vertices=np.round([[v.x,v.y,v.z] for v in vs],6), faces=fs, process=True)
    m.merge_vertices(digits_vertex=6)
    m.remove_unreferenced_vertices()
    check('mesh topology', m.is_watertight and m.is_winding_consistent and m.volume>0,
          {'bodies':m.body_count, 'triangles':len(m.faces)})
    return m


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
