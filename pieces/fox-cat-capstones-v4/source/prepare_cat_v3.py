"""Historical v3 fairing stage; rejected as final, retained for deterministic v4 reconstruction."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from build import write_3mf
from revise_fox import smoothstep

ROOT=Path(__file__).resolve().parents[1]

def revise(mesh):
    original=mesh.vertices.copy()
    x,y,z=original.T
    # The neck-side transition is behind the face at positive Y. Avoid eyes,
    # muzzle, ears, upper head, torso, tail and all bottom support surfaces.
    mask=smoothstep((z-14.8)/1.8)*smoothstep((21.2-z)/1.6)*smoothstep((x-.3)/2.0)*smoothstep((y+2.2)/2.8)*smoothstep((6.6-y)/1.8)
    fair=mesh.copy()
    trimesh.smoothing.filter_taubin(fair,lamb=.46,nu=.47,iterations=300)
    displacement=(fair.vertices-original)*mask[:,None]
    length=np.linalg.norm(displacement,axis=1)
    displacement*=np.minimum(1.,.8/np.maximum(length,1e-9))[:,None]
    mesh.vertices=original+displacement
    protected=mask==0
    assert np.array_equal(mesh.vertices[protected],original[protected])
    assert mesh.is_volume
    return mesh,{'method':'Masked local surface fairing of neck-side transition; no collar component added or removed',
        'source_sha256':hashlib.sha256((ROOT/'raw/cat-v2.stl').read_bytes()).hexdigest(),
        'max_vertex_displacement_mm':float(np.linalg.norm(displacement,axis=1).max()),'changed_vertices':int((mask>0).sum()),
        'protected_vertices':int(protected.sum()),'protected_vertex_max_change_mm':0.,'base_tail_muzzle_ears_preserved':True,
        'dimensions_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'no_paid_generation':True}
