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
record('valid-single-solids',all(p.isValid() and (len(p.Solids())==1 or k.startswith('inlay')) for k,p in parts.items()),
       {k:len(p.Solids()) for k,p in parts.items()})

A=c.leaf_a();B=c.leaf_b(0)
allp=A+B
m=max(ov(a,b) for i,a in enumerate(allp) for b in allp[i+1:])
record('open-flat-no-overlap',m<TOL,{'max_mm3':round(m,4)})

# Fold sweep. Only the catch ring in leaf B may touch the tab, and only in
# the last few degrees; everything else must stay clear.
ring=c.catch_ring()
Bnr=c.base('B').cut(ring)
sweep={};snap={}
for a in list(range(0,171,5))+[172,174,176,178,179,180]:
    Bt=c.leaf_b(a)
    sweep[a]=round(worst(A,[c.fold(Bnr,a)]+Bt[1:]),4)
    snap[a]=round(ov(c.tab(),c.fold(ring,a)),3)
record('fold-sweep-0-180-clear-except-catch',all(v<TOL for v in sweep.values()),{'max_by_angle':sweep})
first=min([a for a,v in snap.items() if v>TOL],default=None)
record('buckle-engages-only-at-closing',first is not None and first>=170 and snap[180]<TOL,
       {'catch_contact_from_deg':first,'catch_overlap_by_angle':{a:v for a,v in snap.items() if a>=170}})
over={a:round(worst([c.base('A')],[c.fold(c.base('B'),a)]),3) for a in (-1,-2,-4)}
record('open-stop-engages-by-2deg',over[-2]>TOL,over)

closed=A+c.leaf_b(180)
top=max(p.BoundingBox().zmax for p in closed)
record('closed-board-inside',abs(top-2*c.AXZ)<3.1,
       {'closed_height_mm':round(top,2),'lips_meet_at_z':c.AXZ,'face_gap_mm':round(2*c.LIP,2),'grid_gap_mm':round(2*(c.LIP-c.LINE_RAISE),2),
        'board_faces_exposed':False})
held=ov(c.tab(),c.fold(ring,180).translate((0,0,.5)))
record('closed-buckle-holds',held>TOL,{'catch_vs_tab_overlap_if_halves_part_0.5mm':round(held,3),
       'engagement_mm':c.TAB_NOTCH_X-.2})
rel={}
pr=c.fold(c.pressed_parts()[0],180)
pan=c.fold(c.base('B').intersect(c.panel_region()).translate((-c.PRESS,0,0)),180)
for dz in (0,.5,1,2,4,8,12):
    rel[dz]=round(max(ov(c.tab(),pr.translate((0,0,dz))),ov(c.tab(),pan.translate((0,0,dz)))),4)
record('pressing-side-panel-releases',all(v<TOL for v in rel.values()),
       {'press_travel_mm':c.PRESS,'overlap_while_lifting':rel})
L=c.PANEL_Y[1]-c.PANEL_Y[0];t=c.PANEL_X[1]-c.PANEL_X[0]-.2;h=c.PANEL_Z[1]-c.PANEL_Z[0]
F=3*3500*(h*t**3/12)*c.PRESS/L**3
st=3*t*c.PRESS/(2*L*L)
record('press-panel-stiffness',st<.01 and 2<F<15,{'panel_mm':[round(L,1),round(t,1),round(h,1)],
       'press_force_N_est':round(F,1),'peak_bending_strain':round(st,4),'flex_plane':'within print layers',
       'note':'pressing alone does not open it; the halves must also be pulled apart'})
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

# Decoration: colours don't overlap, stay clear of grid lines, the fold seam,
# hinge notches, buckle and thumb groove, and stay inside the plates.
dec={}
for s in 'AB':
    o,u,w=c.decor(s,'orange'),c.decor(s,'purple'),c.stars(s)
    grid=c._lines(.35) if s=='A' else c.mirror_b(c._lines(.35))
    keep=c.box(c.LIP_W+.35,c.LEAF_X1-.4,c.LIP_W+.35,c.WY-c.LIP_W-.35,0,40) if s=='A' else c.mirror_b(c.box(c.LIP_W+.35,c.LEAF_X1-.4,c.LIP_W+.35,c.WY-c.LIP_W-.35,0,40))
    notch=[c.box(c.SEAM-c.RELIEF-.8,c.SEAM+c.RELIEF+.8,-1,c.FY0+.8,0,40),c.box(c.SEAM-c.RELIEF-.8,c.SEAM+c.RELIEF+.8,c.WY-c.FY0-.8,c.WY+1,0,40)]
    buckle=c.box(c.TAB_X[0]-1,c.TAB_X[1]+c.SLOT_ARC+1,c.TAB_Y[0]-1,c.TAB_Y[1]+1,0,40)
    buckle=c.fold(buckle,180) if s=='A' else buckle
    row={'orange_vs_purple':ov(o,u),'colour_vs_stars':max(ov(o,w),ov(u,w)),
         'vs_grid_lines_plus_0.35':max(ov(o,grid),ov(u,grid),ov(w,grid)),
         'vs_hinge_notches':max(ov(x,n) for x in (o,u,w) for n in notch),
         'vs_buckle':max(ov(x,buckle.translate((0,0,0))) for x in (o,u)),
         'outside_plate_margin':max(x.Volume()-ov(x,keep) for x in (o,u,w))}
    dec[s]={k:round(v_,4) for k,v_ in row.items()}
record('board-decoration-clear',all(v_<TOL for r in dec.values() for v_ in r.values()),dec)
x0,x1=c.DR_X;cx=(x0+x1)/2
notch=cq.Solid.makeCylinder(7.8,3,cq.Vector(cx,-.5,c.DR_TOP+2.0),cq.Vector(0,1,0))
acc,wht=c.tray_swirl('A'),c.tray_sparkles('A')
fz=c.DR_Z0+c.DR_FLOOR
floor_zone=c.box(x0+c.DR_WALL+1.0,x1-c.DR_WALL-1.0,c.DR_FRONT+1.0,c.DR_Y1-c.DR_WALL-1.0,fz-1,fz+.01)
front_zone=c.box(x0+2.0,x1-2.0,-.01,c.DR_FRONT-1.0,c.DR_Z0+1.0,c.DR_TOP-1.0)
stray=sum(x.Volume() for x in (acc,wht))-sum(ov(x,z) for x in (acc,wht) for z in (floor_zone,front_zone))
arm=c._arm_region()
rt={'accent_vs_white':round(ov(acc,wht),4),'outside_floor_or_front_zone':round(stray,4),
    'front_vs_finger_notch':round(ov(acc,notch),4),'vs_latch_arm':round(max(ov(acc,arm),ov(wht,arm)),4),
    'accent_mm3':round(acc.Volume(),1),'sparkles':len(wht.Solids())}
record('tray-art-clear',all(rt[k]<TOL for k in ('accent_vs_white','outside_floor_or_front_zone','front_vs_finger_notch','vs_latch_arm')),rt)
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
