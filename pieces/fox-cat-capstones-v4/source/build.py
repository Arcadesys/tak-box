"""Finish approved reconstructions locally; no paid API calls on rebuild.

Y-up OBJ -> Z-up, weld UV/normal seams, repair topology, uniformly scale,
trim a shallow base plane, and package labeled STL/3MF objects in millimetres.
Never replace a reconstruction with a primitive or a legacy capstone.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import numpy as np
import pymeshfix
import trimesh

ROOT=Path(__file__).resolve().parents[1]
LIMIT=np.array([18.6,18.6,24.4])

def write_3mf(meshes, path):
    resources=[]
    items=[]
    for i,(name,mesh) in enumerate(meshes,1):
        verts=''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in mesh.vertices)
        faces=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in mesh.faces)
        resources.append(f'<object id="{i}" type="model" name="{name}"><mesh><vertices>{verts}</vertices><triangles>{faces}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Title">Fox and Cat Tak capstones - geometry only</metadata><resources>'+''.join(resources)+'</resources><build>'+''.join(items)+'</build></model>'
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',model)

def finish(species):
    review=ROOT/'reports'/'meshy-v2-fidelity-review.json'
    if json.loads(review.read_text())[species]['status']!='VISUAL REVIEW PASSED':
        raise RuntimeError(f'{species.title()} requires actual-mesh visual review before finishing.')
    path=ROOT/'raw'/f'{species}.obj'
    m=trimesh.load(path,force='mesh')
    rawfaces=len(m.faces)
    m.merge_vertices(merge_tex=True,merge_norm=True)
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    before=m.copy()
    f=pymeshfix.MeshFix(m.vertices,m.faces)
    f.repair(joincomp=True,remove_smallest_components=True)
    m=trimesh.Trimesh(f.points,f.faces,process=True)
    trimesh.repair.fix_normals(m,multibody=True)
    assert m.is_watertight and m.is_volume
    scale=float(np.min(LIMIT/m.extents))
    m.apply_scale(scale)
    m.apply_translation([-m.bounds[:,0].mean(),-m.bounds[:,1].mean(),-m.bounds[0,2]])
    base_trim=.35
    cutter=trimesh.creation.box([100,100,100],transform=trimesh.transformations.translation_matrix([0,0,50+base_trim]))
    m=trimesh.boolean.intersection([m,cutter],engine='manifold')
    m.apply_translation([0,0,-base_trim])
    # All storage-axis rolls must fit as well as the nominal pose. Preserve
    # proportions by applying the stricter rectangular/radial uniform scale.
    radial_diameter=2*float(np.linalg.norm(m.vertices[:,:2],axis=1).max())
    finalscale=min(float(np.min(LIMIT/m.extents)),18.6/radial_diameter)
    m.apply_scale(finalscale)
    m.apply_translation([-m.bounds[:,0].mean(),-m.bounds[:,1].mean(),-m.bounds[0,2]])
    assert m.is_volume and np.all(m.extents<=LIMIT+1e-6)
    m.export(ROOT/'models'/f'{species}-capstone.stl')
    m.export(ROOT/'models'/f'{species}-capstone.obj')
    # Compare repaired surface to original before base trimming (deterministic sample).
    repair=trimesh.Trimesh(f.points,f.faces,process=True)
    sample=repair.vertices[::max(1,len(repair.vertices)//3000)]
    _,dist,_=trimesh.proximity.closest_point(before,sample)
    report={'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_faces':rawfaces,
            'repair_method':'MeshFix seam weld, join components, remove tiny islands, close holes',
            'repair_to_source_distance_mm':{'sample_count':len(sample),'p95':float(np.percentile(dist,95)*scale),'max':float(dist.max()*scale)},
            'base_trim_before_final_scale_mm':base_trim,'uniform_scale_total':scale*finalscale,
            'dimensions_mm':m.extents.tolist(),'faces':len(m.faces),'volume_mm3':float(m.volume)}
    return m,report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--species',nargs='+',default=['fox','cat'],choices=['fox','cat'])
    args=p.parse_args()
    report={}
    built=[]
    for species in args.species:
        mesh,report[species]=finish(species)
        mesh.apply_translation([20+40*len(built),20,0])
        built.append((f'{species.title()} capstone',mesh))
    write_3mf(built,ROOT/'models'/('fox-cat-capstones.3mf' if len(built)==2 else f'{args.species[0]}-capstone.3mf'))
    (ROOT/'reports'/'finishing.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
