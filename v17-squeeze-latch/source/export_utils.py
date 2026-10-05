from collections import Counter
from pathlib import Path
import struct,zipfile
import numpy as np
import xml.etree.ElementTree as ET
import folio as c
OUT=Path(__file__).resolve().parents[1]
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def render(name,scene,title):
    from matplotlib.colors import to_rgba
    fig=plt.figure(figsize=(11,8)); ax=fig.add_subplot(111,projection='3d')
    faces=[]; colors=[]; vertices=[]
    light=np.array([1.,-1.,2.]);light/=np.linalg.norm(light)
    for sh,col,alpha in scene:
        v,f=mesh(sh); tri=v[f]; vertices.extend(v)
        # Subdivide long planar triangles for reliable depth ordering of roofs.
        for _ in range(5):
            edge=np.max(np.linalg.norm(tri-np.roll(tri,1,axis=1),axis=2),axis=1)
            wide=edge>20
            if not np.any(wide): break
            small=tri[~wide];t=tri[wide]
            a,b,d=t[:,0],t[:,1],t[:,2];ab=(a+b)/2;bd=(b+d)/2;da=(d+a)/2
            tri=np.concatenate([small,np.stack([a,ab,da],axis=1),np.stack([ab,b,bd],axis=1),np.stack([da,bd,d],axis=1),np.stack([ab,bd,da],axis=1)])
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        lengths=np.linalg.norm(normals,axis=1)
        normals/=np.maximum(lengths[:,None],1e-12)
        shade=.65+.35*np.abs(normals@light)
        rgba=np.tile(to_rgba(col,alpha),(len(tri),1));rgba[:,:3]*=shade[:,None]
        faces.extend(tri);colors.extend(rgba)
    # One collection sorts all exported triangles together, avoiding the
    # incorrect whole-actor occlusion of independent matplotlib collections.
    ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolor='none'))
    v=np.array(vertices);lo=v.min(axis=0);hi=v.max(axis=0);extent=np.maximum(hi-lo,1)
    pad=max(extent)*.05
    ax.set_xlim(lo[0]-pad,hi[0]+pad);ax.set_ylim(lo[1]-pad,hi[1]+pad);ax.set_zlim(lo[2]-pad,hi[2]+pad)
    ax.set_box_aspect(extent+2*pad);ax.view_init(40,-55);ax.set_axis_off();ax.set_title(title,pad=8)
    fig.tight_layout();fig.savefig(OUT/'previews'/f'{name}.png',dpi=160);plt.close(fig)
