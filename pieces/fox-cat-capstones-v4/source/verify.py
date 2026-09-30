"""Verify exported meshes and conservative OCC storage/motion envelopes.

No box or regular-piece geometry is modified. An enclosing box passing is a
stronger exclusion test than testing only the sculpture's occupied volume.
Physical print tolerances, rolling, transport and touch remain untested.
"""
from pathlib import Path
import argparse, hashlib, json, math, sys
import numpy as np
from scipy.spatial import ConvexHull
import trimesh
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'v16-field-book'/'source'))
import tak_book as c

def ov(a,b):
    return max(0.,float(a.intersect(b).Volume()))

def sh_mesh(shape):
    v,f=shape.tessellate(.03,.1)
    return trimesh.Trimesh([[p.x,p.y,p.z] for p in v],f,process=True)

def stored(mesh):
    m=mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]))
    cx,ya,yb=c.cap_slot()
    m.apply_translation([cx-m.bounds[:,0].mean(),ya+.4-m.bounds[0,1],c.DR_Z0+c.DR_FLOOR-m.bounds[0,2]])
    return m

def mesh_check(mesh):
    base=np.all(np.abs(mesh.triangles[:,:,2])<2e-6,axis=1)
    points=mesh.vertices[np.abs(mesh.vertices[:,2])<2e-6,:2]
    hull=ConvexHull(points)
    distances=-(hull.equations[:,:2]@mesh.center_mass[:2]+hull.equations[:,2])
    result={'dimensions_mm':mesh.extents.tolist(),'bounds_mm':mesh.bounds.tolist(),'faces':len(mesh.faces),
        'watertight':bool(mesh.is_watertight),'consistent_winding':bool(mesh.is_winding_consistent),
        'positive_volume':bool(mesh.volume>0),'connected_components':len(mesh.split(only_watertight=False)),
        'volume_mm3':float(mesh.volume),'planar_base_area_mm2':float(mesh.area_faces[base].sum()),
        'center_of_mass_mm':mesh.center_mass.tolist(),'COM_to_base_hull_margin_mm':float(distances.min()),
        'estimated_PLA_mass_g':float(mesh.volume*.00124)}
    assert result['watertight'] and result['consistent_winding'] and result['connected_components']==1
    assert result['positive_volume'] and result['planar_base_area_mm2']>40 and distances.min()>2
    assert np.all(mesh.extents<=np.array([18.6,18.6,24.4])+1e-5)
    return result

def verify(species,mesh):
    result=mesh_check(mesh)
    m=stored(mesh)
    m.export(ROOT/'models'/f'{species}-storage-pose.stl')
    lo,hi=m.bounds
    envelope=c.box(lo[0],hi[0],lo[1],hi[1],lo[2],hi[2])
    t=c.tray_a()
    L=c.ARM_Y[1]-(c.BTN_Y[0]+c.BTN_Y[1])/2
    angle=math.degrees(c.RELEASE/L)
    bent=t.intersect(c._arm_region()).rotate((c.DR_X[0],c.ARM_Y[1],0),(c.DR_X[0],c.ARM_Y[1],1),angle)
    result['storage']={'rotation':'-90 degrees about X; upright Z becomes tray +Y',
        'placement_bounds_mm':m.bounds.tolist(),'plate_clearance_mm':float(c.PLATE_Z-hi[2]),
        'saddle_clearance_left_mm':float(lo[0]-(c.cap_slot()[0]-c.CAP[1]/2-c.SADDLE_GAP)),
        'saddle_clearance_right_mm':float(c.cap_slot()[0]+c.CAP[1]/2+c.SADDLE_GAP-hi[0]),
        'front_clearance_mm':float(lo[1]-c.DR_FRONT),'stop_clearance_mm':float(c.cap_slot()[2]+c.STOP_GAP-hi[1]),
        'method':'Actual exported vertex bounds enclosed by exact OCC solid; no reliance on old pawn model',
        'floor':'Bounds placed on unrecessed floor at z=3.2 mm; actual sculpture may settle into shallow cradle'}
    result['envelope_overlap_mm3']={}
    for side in 'AB':
        e=envelope if side=='A' else c.mirror_b(envelope)
        objects={'tray':c.tray(side),'insert':c.tray_insert(side),'plate':c.plate(side),'base':c.base(side),
            'translated_pressed_tray':c.tray(side,released=True),'rotated_pressed_arm':bent if side=='A' else c.mirror_b(bent)}
        result['envelope_overlap_mm3'][side]={name:ov(e,sh) for name,sh in objects.items()}
        assert all(v<1e-5 for v in result['envelope_overlap_mm3'][side].values())
    # Exact source transforms include the upside-down B capstone when closed.
    A=envelope
    B=c.fold(c.mirror_b(envelope),180)
    result['closed_box_envelope_overlap_mm3']={'other_capstone':ov(A,B),
        'A_vs_B_base':ov(A,c.fold(c.base('B'),180)), 'A_vs_B_plate':ov(A,c.fold(c.plate('B'),180)),
        'B_vs_A_base':ov(B,c.base('A')),'B_vs_A_plate':ov(B,c.plate('A'))}
    assert all(v<1e-5 for v in result['closed_box_envelope_overlap_mm3'].values())
    pulls=[0,10,30,60,100,132,160]
    result['tray_with_capstone_slide_mm3']={str(p):max(ov(envelope.translate((0,-p,0)),c.base('A')),ov(envelope.translate((0,-p,0)),c.plate('A'))) for p in pulls}
    assert all(v<1e-5 for v in result['tray_with_capstone_slide_mm3'].values())
    # Tray must come out before lifting; lifting under the installed plate is blocked.
    dzs=[0,1,3,6,9,12,20,30]
    result['lift_out_with_tray_removed_mm3']={str(dz):max(ov(envelope.translate((0,0,dz)),c.tray_a()),ov(envelope.translate((0,0,dz)),c.tray_insert_a())) for dz in dzs}
    assert all(v<1e-5 for v in result['lift_out_with_tray_removed_mm3'].values())
    # Direct mesh intersections supplement the exact conservative OCC checks.
    collisions={}
    for name,sh in [('tray',t),('insert',c.tray_insert_a()),('plate',c.plate('A')),('pressed_arm',bent)]:
        other=sh_mesh(sh)
        other.merge_vertices(merge_tex=True,merge_norm=True)
        other.update_faces(other.nondegenerate_faces())
        trimesh.repair.fix_normals(other,multibody=True)
        assert other.is_volume,name
        cross=trimesh.boolean.intersection([m,other],engine='manifold')
        collisions[name]=float(abs(cross.volume)) if len(cross.faces) else 0.
    result['actual_mesh_overlap_mm3']=collisions
    assert all(v<1e-5 for v in collisions.values())
    # A cylinder enclosing every XY vertex also encloses every roll about the
    # sculpture's upright axis (tray Y). This covers arbitrary axial roll, not
    # only one attractive nominal pose. Its bottom rests on the flat floor.
    radius=float(np.linalg.norm(mesh.vertices[:,:2],axis=1).max())
    cx,ya,yb=c.cap_slot()
    cylinder=cq.Solid.makeCylinder(radius,float(mesh.extents[2]),cq.Vector(cx,ya+.4,c.DR_Z0+c.DR_FLOOR+radius),cq.Vector(0,1,0))
    roll={name:ov(cylinder,sh) for name,sh in [('tray',t),('insert',c.tray_insert_a()),('plate',c.plate('A')),('base',c.base('A')),('pressed_arm',bent)]}
    result['all_axial_rolls_cylindrical_bound']={'diameter_mm':2*radius,'headroom_mm':c.PLATE_Z-(c.DR_Z0+c.DR_FLOOR+2*radius),
        'saddle_clearance_per_side_mm':(c.CAP[1]+2*c.SADDLE_GAP)/2-radius,'overlap_mm3':roll,
        'method':'Exact enclosing cylinder bounds every roll about the storage longitudinal axis. Bounding cylinder does not establish self-settling or retention.'}
    assert all(v<1e-5 for v in roll.values())
    result['removal_access']={'procedure':'Slide tray fully out, then grasp body/tail and lift vertically',
        'insert_wall_height_mm':c.SADDLE_H,'exposed_height_above_side_wall_mm':float(hi[2]-(c.DR_Z0+c.DR_FLOOR+c.SADDLE_H)),
        'limitation':'Nominal gaps are not fingertip slots. Grasp, tactile identity, release, rolling and transport need physical tests.'}
    result['digital_pass']=True
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--species',nargs='+',default=['fox','cat'],choices=['fox','cat'])
    args=p.parse_args()
    result={'box_source_sha256':hashlib.sha256((REPO/'v16-field-book/source/tak_book.py').read_bytes()).hexdigest(),
        'closed_box_mm':[c.SEAM+3,c.WY,2*c.AXZ], 'physical_acceptance':'UNTESTED','species':{}}
    for species in args.species:
        m=trimesh.load(ROOT/'models'/f'{species}-capstone.stl',force='mesh')
        result['species'][species]=verify(species,m)
        print(species,'PASS',result['species'][species]['dimensions_mm'],flush=True)
    (ROOT/'reports'/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
