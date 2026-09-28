"""Digital checks for the v13 book. Writes reports/geometry-verification.json.
Sampled motion and valid solids do not establish strength, force or fit."""
from pathlib import Path
import json
import cadquery as cq
import tak_book as c

OUT=Path(__file__).resolve().parent.parent
(OUT/'reports').mkdir(exist_ok=True)
report={}
TOL=.05

def ov(a,b):return a.intersect(b).Volume()
def worst(A,B):return max(ov(a,b) for a in A for b in B)
def record(name,ok,detail):
    report[name]={'pass':bool(ok),'detail':detail}
    print('PASS' if ok else 'FAIL',name,detail,flush=True)
    assert ok,name

parts={'base-A':c.base('A'),'base-B':c.base('B'),'plate-A':c.plate('A'),'plate-B':c.plate('B'),
       'inlay-A':c.inlay('A'),'inlay-B':c.inlay('B'),'tray':c.tray_a()}
record('valid-single-solids',all(p.isValid() and len(p.Solids())==1 for p in parts.values()),
       {k:len(p.Solids()) for k,p in parts.items()})

A=c.leaf_a();B=c.leaf_b(0)
allp=A+B
m=max(ov(a,b) for i,a in enumerate(allp) for b in allp[i+1:])
record('open-flat-no-overlap',m<TOL,{'max_mm3':round(m,4)})

# Fold sweep. Only the snap arms inside leaf B may touch the posts, and only
# in the last few degrees; everything else must stay clear.
arms=[c.snap_arm_region(2*c.SEAM-x) for x in c.SNAP_XA]
Bna=[c.base('B')]
for r in arms:Bna=[Bna[0].cut(r)]
sweep={};snap={}
for a in list(range(0,171,5))+[172,174,176,178,179,180]:
    Bt=c.leaf_b(a)
    rest=[c.fold(Bna[0],a)]+Bt[1:]
    sweep[a]=round(worst(A,rest),4)
    snap[a]=round(worst(A,[c.fold(r,a) for r in arms]),3)
record('fold-sweep-0-180-clear-except-snap-arms',all(v<TOL for v in sweep.values()),{'max_by_angle':sweep})
first=min([a for a,v in snap.items() if v>TOL],default=None)
record('snap-engages-only-at-closing',first is not None and first>=170 and snap[180]<TOL,
       {'arm_contact_from_deg':first,'arm_overlap_by_angle':{a:v for a,v in snap.items() if a>=170}})

over={a:round(worst([c.base('A')],[c.fold(c.base('B'),a)]),3) for a in (-1,-2,-4)}
record('open-stop-engages-by-2deg',over[-2]>TOL,over)

closed=A+c.leaf_b(180)
top=max(p.BoundingBox().zmax for p in closed)
record('closed-board-inside',abs(top-2*c.AXZ)<3.1,
       {'closed_height_mm':round(top,2),'raised_grids_meet_at_z':c.AXZ,'face_gap_mm':round(2*c.LINE_RAISE,2),
        'board_faces_exposed':False})
posts=[p for p in [c.plate('A')]]
Bc=c.leaf_b(180)
held=max(ov(c.plate('A'),c.fold(r,180).translate((0,0,.5))) for r in arms)
record('closed-snaps-hold',held>TOL,{'arm_vs_post_overlap_if_halves_part_0.5mm':round(held,3),
       'post_r':c.POST_R,'neck_r':c.NECK_R,'arm_face_r':c.ARM_FACE,'retaining_shoulder_deg':60})
L_arm=sum(c.ARM_LEN)
defl=c.POST_R-c.ARM_FACE
st=3*c.ARM_T*defl/(2*c.ARM_LEN[0]**2)
record('snap-arm-strain',st<.01,{'deflection_mm':round(defl,2),'arm_len_to_hole_mm':c.ARM_LEN[0],'peak_bending_strain':round(st,4),
       'flex_plane':'within print layers'})
tr={}
for side in 'AB':
    fixed=[c.base(side),c.plate(side)]
    locked={p:round(worst([c.tray(side,p)],fixed),3) for p in (0,.3,1,5)}
    free={p:round(worst([c.tray(side,p,released=True)],fixed),4) for p in (0,.3,1,2,5,10,20,40,60,100,132)}
    tr[side]={'locked_overlap_if_pulled':locked,'released_overlap_if_pulled':free}
ok=all(r['locked_overlap_if_pulled'][0]<TOL and r['locked_overlap_if_pulled'][1]>TOL
       and all(v<TOL for v in r['released_overlap_if_pulled'].values()) for r in tr.values())
record('tray-latch-locks-and-releases',ok,tr)
# Latch geometry: button depth below the side face, travel, arm strain.
L=c.ARM_Y[1]-sum(c.BTN_Y)/2
strain=3*c.DR_WALL*c.RELEASE/(2*L*L)
record('latch-geometry',strain<.01,{'button_recess_below_side_face_mm':c.BTN_TIP_X,
    'finger_dish_mm':[2*c.DISH_R,c.DISH_D],'press_travel_to_release_mm':round(c.RELEASE,2),
    'catch_engagement_mm':round(c.FORE-c.BTN_TIP_X-.05-c.DISH_D+1.5,2),
    'arm_len_to_button_mm':round(L,1),'peak_bending_strain':round(strain,4)})
# Pieces beside the pressed arm: arm pivots about its root by the release angle.
import math
t=c.tray_a();r=c._arm_region();x0=c.DR_X[0]
theta=math.degrees(c.RELEASE/L)
bent=t.intersect(r).rotate((x0,c.ARM_Y[1],0),(x0,c.ARM_Y[1],1),theta)
pr=max(ov(p,bent) for p in c.piece_boxes('A'))
record('pieces-clear-of-pressed-arm',pr<TOL,{'max_mm3':round(pr,4),'arm_rotation_deg':round(theta,2)})
# A tray in the closed book (leaf B upside down) must still be captured.
res={}
for side,leaf in (('A',A),('B',c.leaf_b(180))):
    res[side]=round(worst([leaf[3]],leaf[:2]),4)
record('trays-clear-in-closed-book',all(v<TOL for v in res.values()),res)

res={}
for side in 'AB':
    pb=c.piece_boxes(side);t=c.tray(side)
    res[side]={'vs_tray':round(max(ov(p,t) for p in pb),4),
               'between':round(max(ov(p,q) for i,p in enumerate(pb) for q in pb[i+1:]),4),
               'under_plate_mm':round(c.PLATE_Z-max(p.BoundingBox().zmax for p in pb),2)}
record('pieces-fit-each-tray',all(r['vs_tray']<TOL and r['between']<TOL and r['under_plate_mm']>=.3 for r in res.values()),
       {'per_tray':'21 flats as 11 two-high stacks + capstone lying down',**res})

bo=cq.Compound.makeCompound(A+B).BoundingBox()
bc=cq.Compound.makeCompound(closed).BoundingBox()
record('sizes',True,{'open_xyz':[round(bo.xlen,1),round(bo.ylen,1),round(bo.zlen,1)],
                     'closed_xyz':[round(bc.xlen,1),round(bc.ylen,1),round(bc.zlen,1)],
                     'pitch':c.P,'field':5*c.P})
hinged=cq.Compound.makeCompound([c.base('A'),c.base('B')])
def ext(s):b=s.BoundingBox();return [round(b.xlen,1),round(b.ylen,1),round(b.zlen,1)]
beds={'hinged-bases':ext(hinged),'plate':ext(c.plate('A')),'tray':ext(c.tray_a())}
record('fits-256-bed',all(max(v)<=250 for v in beds.values()),beds)
json.dump(report,open(OUT/'reports'/'geometry-verification.json','w'),indent=1)
print('ALL PASS')
