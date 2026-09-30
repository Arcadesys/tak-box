"""Reshape the full neck/shoulder form, preserving protected anatomy."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from scipy.spatial import ConvexHull,cKDTree
from build import write_3mf
ROOT=Path(__file__).resolve().parents[1]

def smoothstep(a):
    a=np.clip(a,0,1);return a*a*(3-2*a)

def revise(mesh):
    mesh=mesh.subdivide()
    original=mesh.vertices.copy();x,y,z=original.T
    # Shoulder strip continues much lower than the previously treated ridge.
    # Blend the broad shoulder and underside into the surrounding neck mass.
    front_offset=np.interp(x,[-2.,0.,2.],[-1.,.9,2.8])
    mask=smoothstep((z-8.4)/3.0)*smoothstep((16.6-z)/2.0)*smoothstep((y+front_offset)/2.6)*smoothstep((7.4-y)/3.2)
    mask*=1-smoothstep((z-13.8)/1.2)*(1-smoothstep((x+.5)/2.0))
    # Protect the entire upper head, including the cheek on the far side.
    # Preserve the anatomical jaw while merging the strap below it.
    # Fill the enclosing neck/shoulder grooves by the convex outline of each
    # horizontal section, rather than just rounding the edge of the strap.
    target=original.copy()
    for height in np.arange(9.,16.,.12):
        ids=np.flatnonzero((np.abs(z-height)<.061)&(mask>0))
        if not len(ids):continue
        section=mesh.section(plane_origin=[0,0,height],plane_normal=[0,0,1])
        if section is None:continue
        points=section.vertices[:,:2];hull=ConvexHull(points);ring=points[hull.vertices]
        a=ring;b=np.roll(ring,-1,axis=0);ab=b-a
        p=original[ids,:2]
        t=np.clip(np.einsum('ijk,jk->ij',p[:,None,:]-a,ab)/np.sum(ab*ab,axis=1),0,1)
        candidates=a[None,:,:]+t[:,:,None]*ab[None,:,:]
        nearest=np.argmin(np.linalg.norm(candidates-p[:,None,:],axis=2),axis=1)
        closest=candidates[np.arange(len(ids)),nearest]
        strength=smoothstep((16.0-z[ids])/2.0)
        target[ids,:2]=p+(closest-p)*strength[:,None]
    mesh.vertices=original+(target-original)*mask[:,None]
    # Area-weighted spatial fairing is independent of Meshy's irregular
    # triangle density. It creates broad neck planes without crumpled facets.
    active=np.flatnonzero(mask>0)
    for iteration in range(18):
        current=mesh.vertices.copy();tree=cKDTree(current)
        areas=np.zeros(len(current));np.add.at(areas,mesh.faces.ravel(),np.repeat(mesh.area_faces/3,3))
        normals=mesh.vertex_normals.copy();updated=current.copy()
        for i,neighbors in zip(active,tree.query_ball_point(current[active],r=1.8)):
            near=np.asarray(neighbors);delta=current[near]-current[i]
            weights=areas[near]*np.exp(-np.sum(delta*delta,axis=1)/(2*.8**2))
            centroid=np.average(current[near],axis=0,weights=weights)
            normal=np.average(normals[near],axis=0,weights=weights);normal/=max(np.linalg.norm(normal),1e-9)
            updated[i]+=normal*np.dot(centroid-current[i],normal)*.7*mask[i]
        mesh.vertices=updated
    # Clean small facets at the preserved jaw/reshaped neck junction without
    # expanding the neck or weakening the protected facial surface.
    seam=smoothstep((z-12.8)/1.6)*smoothstep((16.6-z)/1.3)*smoothstep((4.6-y)/1.5)*mask
    cleaned=mesh.copy()
    trimesh.smoothing.filter_taubin(cleaned,lamb=.45,nu=.46,iterations=120)
    cleanup=(cleaned.vertices-mesh.vertices)*seam[:,None]
    length=np.linalg.norm(cleanup,axis=1)
    cleanup*=np.minimum(1.,.35/np.maximum(length,1e-9))[:,None]
    mesh.vertices+=cleanup
    displacement=mesh.vertices-original
    protected=mask==0
    assert np.array_equal(mesh.vertices[protected],original[protected])
    assert mesh.is_volume
    return mesh,{'method':'Fill full neck/shoulder grooves to sectional convex outlines, then area-weighted spatial fairing',
        'source_sha256':hashlib.sha256((ROOT/'raw/cat-v3.stl').read_bytes()).hexdigest(),
        'max_vertex_displacement_mm':float(np.linalg.norm(displacement,axis=1).max()),
        'jaw_junction_cleanup_max_mm':float(np.linalg.norm(cleanup,axis=1).max()),
        'changed_vertices':int((mask>0).sum()),'protected_vertices':int(protected.sum()),
        'protected_vertex_max_change_mm':0.,'dimensions_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'new_credits':0}

if __name__=='__main__':
    cat,report=revise(trimesh.load(ROOT/'raw/cat-v3.stl',force='mesh'))
    cat.export(ROOT/'models/cat-capstone.stl');cat.export(ROOT/'models/cat-capstone.obj')
    meshes=[]
    for i,species in enumerate(['fox','cat']):
        m=trimesh.load(ROOT/'models'/f'{species}-capstone.stl',force='mesh');m.apply_translation([20+i*40,20,0]);meshes.append((f'{species.title()} capstone',m))
    write_3mf(meshes,ROOT/'models/fox-cat-capstones.3mf')
    (ROOT/'reports/neck-revision.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
