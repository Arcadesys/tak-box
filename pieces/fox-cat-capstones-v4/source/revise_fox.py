"""Tail-only surface fullness; retain existing connected carved geometry.

No new tail mesh, detached tufts or global scale. The existing tail planes
expand through a smooth spatial mask; upper body and base stay exact.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from build import write_3mf

ROOT=Path(__file__).resolve().parents[1]

def smoothstep(a):
    a=np.clip(a,0,1)
    return a*a*(3-2*a)

def revise(mesh):
    # One exact planar subdivision lets the continuous deformation follow the
    # existing broad planes without coarse triangle corners becoming spikes.
    mesh=mesh.subdivide()
    original=mesh.vertices.copy()
    x,y,z=original.T
    # Tail fan is on the forward lower-right surface. Its crown follows the
    # existing curled outline; protect torso beyond that crown and all back.
    crown=np.interp(x,[-9,-7,-5,-3,-1,1,3,5,7,9],[1,2.1,2.9,3.9,5.2,7.3,9.0,7.5,5.0,1])
    mask=smoothstep((crown-z)/2.6)*smoothstep((-y-.1)/2.2)*smoothstep((z-.8)/2.0)
    radial=np.column_stack([x,y,np.zeros(len(x))])
    radial/=np.maximum(np.linalg.norm(radial,axis=1)[:,None],.1)
    # Three broad fullness lobes follow the existing fan; no striped ridges.
    tufts=sum(np.exp(-((x-cx)/3.2)**2-((z-cz)/1.6)**2) for cx,cz in [(3.1,6.6),(4.5,4.4),(4.5,2.6)])
    amount=mask*(.68+.48*tufts)
    radius=np.linalg.norm(original[:,:2],axis=1)
    amount=np.minimum(amount,np.maximum(9.05-radius,0))
    displacement=radial*amount[:,None]
    displacement[:,2]=mask*.28*smoothstep((z-1.0)/2.0)
    mesh.vertices=original+displacement
    # Smooth only the moved surface to remove small creases introduced by
    # deformation, with the same continuous mask retaining broad source cuts.
    fair=mesh.copy()
    trimesh.smoothing.filter_taubin(fair,lamb=.45,nu=.46,iterations=10)
    mesh.vertices+= (fair.vertices-mesh.vertices)*mask[:,None]
    mesh.vertices[mask==0]=original[mask==0]
    displacement=mesh.vertices-original
    protected=mask==0
    assert np.array_equal(mesh.vertices[protected],original[protected])
    assert np.array_equal(mesh.vertices[z<=.55],original[z<=.55])
    assert mesh.is_volume
    report={'method':'Continuous tail-only deformation of existing v2 surface; no added component or global scale',
        'source_sha256':hashlib.sha256((ROOT/'raw/fox-v2.stl').read_bytes()).hexdigest(),
        'protected_vertices':int(protected.sum()),'protected_vertex_max_change_mm':0.,'base_vertices_unchanged':True,
        'changed_vertices':int((mask>0).sum()),'max_vertex_displacement_mm':float(np.linalg.norm(displacement,axis=1).max()),
        'dimensions_mm':mesh.extents.tolist(),'original_volume_mm3':float(trimesh.load(ROOT/'raw/fox-v2.stl',force='mesh').volume),
        'revised_volume_mm3':float(mesh.volume),'no_paid_generation':True}
    return mesh,report

if __name__=='__main__':
    m=trimesh.load(ROOT/'raw/fox-v2.stl',force='mesh')
    m,report=revise(m)
    m.export(ROOT/'models/fox-capstone.stl')
    m.export(ROOT/'models/fox-capstone.obj')
    # revise_cat.py runs next and packages both final meshes into the 3MF.
    (ROOT/'reports/tail-revision.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
