"""Export and check the open-well Tak case CAD prototype."""
from pathlib import Path
import json
import cadquery as cq
import tak_case as m

OUT=Path(__file__).resolve().parent
pair0=m.lid_pair(0)
pair2=m.lid_pair(2)
bodies=[pair0[0],m.shell(1),pair2[0]]
lids=[pair0[1],pair2[1]]
overlays=[m.overlay(i) for i in range(3)]
pieces=[m.pieces(i) for i in (0,2)]
main_pins=[m.main_pin(i) for i in range(2)]
lid_pins=[m.lid_pin(i) for i in (0,2)]

def is_clear(a,b):return a.intersect(b).Volume()<1e-4

assert all(x.isValid() and len(x.Solids())==1
           for x in bodies+lids+overlays+main_pins+lid_pins)
# Every structural section must reach the same table plane when fully open.
resting_heights=[b.BoundingBox().zmin for b in bodies]
assert all(abs(z+20.1)<1e-5 for z in resting_heights),resting_heights
assert all(abs(b.BoundingBox().zmax-4)<1e-5 for b in bodies)
assert [len(group) for group in pieces]==[22,22]
for index,lid in ((0,lids[0]),(2,lids[1])):
    assert is_clear(bodies[index],lid)
    assert all(is_clear(bodies[index],p) and is_clear(lid,p)
               for p in pieces[0 if index==0 else 1])
    for angle in range(0,111,5):
        moving=m.lid_open(lid,index,angle)
        assert all(is_clear(moving,other) for other in bodies)
    assert is_clear(lid,overlays[index])

for angle in range(0,91,5):
    posed_bodies=[m.posed(bodies[i],i,angle) for i in range(3)]
    posed_lids=[m.posed(lids[0],0,angle),m.posed(lids[1],2,angle)]
    for i,j in ((0,1),(0,2),(1,2)):
        assert is_clear(posed_bodies[i],posed_bodies[j]),(angle,i,j)
    for lid in posed_lids:
        assert all(is_clear(lid,other) for other in posed_bodies)
    assert is_clear(posed_lids[0],posed_lids[1])

# 7 columns × 3 rows of flats fit in each broad well, with a sideways K.
for index in (0,2):
    y0=m.wing_y(index)
    well_y=y0+(8 if index==0 else 10)
    assert all(8<=p.BoundingBox().xmin and p.BoundingBox().xmax<=160
               and well_y<=p.BoundingBox().ymin and p.BoundingBox().ymax<=well_y+64
               and -18.1<p.BoundingBox().zmin and p.BoundingBox().zmax<1
               for p in pieces[0 if index==0 else 1][:-1])
    k=pieces[0 if index==0 else 1][-1].BoundingBox()
    assert 168<k.xmin and k.xmax<197 and y0+29<k.ymin and k.ymax<y0+53
    assert -18.6<k.zmin and k.zmax<2.6

def export_step(path,items):
    a=cq.Assembly(name='Tak open wells prototype')
    for name,shape,color in items:a.add(shape,name=name,color=cq.Color(*color))
    a.save(str(path),exportType='STEP')
    reopened=cq.importers.importStep(str(path)).val()
    assert reopened.isValid()
    return len(reopened.Solids())

white=(.94,.94,.91);black=(.05,.05,.06);stone=(.56,.32,.16)
open_items=[(f'wing shell {i}',bodies[i],white) for i in range(3)]
open_items += [(f'playing lid {i}',lids[n],white) for n,i in enumerate((0,2))]
open_items += [(f'black grid {i}',overlays[i],black) for i in range(3)]
open_items += [(f'main pin {i}',p,white) for i,p in enumerate(main_pins)]
open_items += [(f'lid pin {i}',p,white) for i,p in enumerate(lid_pins)]
access_items=[item for item in open_items if not item[0].startswith('playing lid')
              and not item[0].startswith('black grid')]
access_items += [('playing lid 0 open',m.lid_open(lids[0],0,105),white),
                 ('playing lid 2 open',m.lid_open(lids[1],2,105),white)]
access_items += [(f'flat or keystone {i}-{n}',p,stone)
                 for i,group in enumerate(pieces) for n,p in enumerate(group)]
closed_items=[(name,m.posed(shape,index,90),color)
              for name,shape,color in open_items
              for index in ([0] if name.endswith('0') else
                            [2] if name.endswith('2') else [1])]

step_solids={
 'play':export_step(OUT/'tak-open-wells-v5-play.step',open_items),
 'access':export_step(OUT/'tak-open-wells-v5-access.step',access_items),
 'closed':export_step(OUT/'tak-open-wells-v5-closed.step',closed_items),
}

def print_pose(shape,mode):
    if mode=='face_down':shape=shape.rotate((0,0,0),(1,0,0),180)
    return shape.translate((0,0,-shape.BoundingBox().zmin))

print_parts={
 'wing-shell-a-print.stl':print_pose(bodies[0],'bottom_down'),
 'center-row-print.stl':print_pose(bodies[1],'face_down'),
 'wing-shell-b-print.stl':print_pose(bodies[2],'bottom_down'),
 'playing-lid-a-print.stl':print_pose(lids[0],'face_down'),
 'playing-lid-b-print.stl':print_pose(lids[1],'face_down'),
 'black-grid-a-print.stl':print_pose(overlays[0],'bottom_down'),
 'black-grid-center-print.stl':print_pose(overlays[1],'bottom_down'),
 'black-grid-b-print.stl':print_pose(overlays[2],'bottom_down'),
 'main-hinge-pin.stl':print_pose(main_pins[0],'bottom_down'),
 'lid-hinge-pin.stl':print_pose(lid_pins[0],'bottom_down'),
}
for name,shape in print_parts.items():
    assert shape.isValid() and len(shape.Solids())==1,name
    cq.exporters.export(shape,str(OUT/name),tolerance=.08,angularTolerance=.1)

report={
 'status':'CAD prototype; physical fit and printability not established',
 'storage':{'wing_wells':2,'flats_per_well':21,
            'flat_well_inner_mm':[152,64,19.1],
            'keystone_recess_inner_mm':[29,24,21.2],
            'modeled_keystone_mm':[19.8,19.8,25.4]},
 'parts':{'shells':3,'playing_lids':2,'black_overlays':3,
          'main_hinge_pins':2,'lid_hinge_pins':2},
 'clearance':{'closed_core_gap_mm':.8,'lid_open_sweep_deg':[0,110],
              'main_fold_sweep_deg':[0,90],
              'open_resting_plane_z_mm':round(resting_heights[1],3)},
 'step_solid_counts':step_solids,
 'stl_count':len(print_parts),
 'physical_print_tested':False,
}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
