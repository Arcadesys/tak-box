"""Digital checks for the v16 book. Writes reports/geometry-verification.json.
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
    free={p:round(worst([c.tray(side,p,released=True)],fixed),4) for p in (0,.3,1,2,5,10,20,40,60,100,round(c.DR_Y1))}
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
    res[side]={'vs_tray_stacks':round(max(ov(p,t) for p in pb[1:]),4),
               'between':round(max(ov(p,q) for i,p in enumerate(pb) for q in pb[i+1:]),4),
               'under_plate_mm':round(c.PLATE_Z-max(p.BoundingBox().zmax for p in pb),2)}
record('pieces-fit-each-tray',all(r['vs_tray_stacks']<TOL and r['between']<TOL and r['under_plate_mm']>=.3 for r in res.values()),
       {'per_tray':'21 flats as 11 two-high stacks + capstone, standing',**res})

# The real pieces (pieces/*.step), not envelopes: each team's pawn capstone lies
# in its cradle and two real flats stand stacked, all inside the tray and clear
# of the plate above. The boxes above are only a layout; this is the fit.
PIECES=OUT.parent/'pieces'
def _load(name):
    return cq.importers.importStep(str(PIECES/f'{name}.step')).val()
def _upright(sh):
    b=sh.BoundingBox();return sh.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
real={}
for side,team in (('A','cat'),('B','witch')):
    cap=_upright(_load(f'{team}-capstone')).rotate((0,0,0),(1,0,0),-90)   # pawn axis along +y
    b=cap.BoundingBox()
    x,ya,yb=c.cap_slot()
    cap=cap.translate((x-(b.xmin+b.xmax)/2,ya-b.ymin,c.DR_Z0+c.DR_FLOOR-c.CRADLE_D-b.zmin))
    b=cap.BoundingBox()
    fl=_upright(_load(f'{team}-flat'))
    stack=[fl,fl.translate((0,0,8))]
    slot=c.piece_boxes('A')[4].BoundingBox()     # first stack of the second column (leaf A frame)
    sx,sy=(slot.xmin+slot.xmax)/2,(slot.ymin+slot.ymax)/2
    stk=[f.translate((sx,sy,c.DR_Z0+c.DR_FLOOR)) for f in stack]
    if side=='B':cap=c.mirror_b(cap);stk=[c.mirror_b(f) for f in stk]
    t=c.tray(side)
    real[side]={'capstone_vs_tray':round(ov(cap,t),4),
        'capstone_top_under_plate_mm':round(c.PLATE_Z-cap.BoundingBox().zmax,2),
        'capstone_vs_plate_and_base':round(worst([cap],[c.plate(side),c.base(side)]),4),
        'capstone_size_mm':[round(b.xlen,1),round(b.ylen,1),round(b.zlen,1)],
        'flats_vs_tray':round(max(ov(f,t) for f in stk),4),
        'flats_vs_plate_and_base':round(max(worst([f],[c.plate(side),c.base(side)]) for f in stk),4)}
record('real-capstone-and-flats-fit',all(r['capstone_vs_tray']<TOL and r['capstone_vs_plate_and_base']<TOL
       and r['capstone_top_under_plate_mm']>=.3 and r['flats_vs_tray']<TOL and r['flats_vs_plate_and_base']<TOL
       for r in real.values()),real)

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

# Playability: v15's 8.5 mm gaps were too tight to pinch a stack out of a full
# board. Keep a fingertip (15 mm) of air beside every stone on the board and
# at least 12 mm between the stacks in each tray.
def _gaps(bs):
    """Smallest clear gap between any two boxes (axis-aligned)."""
    bb=[x.BoundingBox() for x in bs]
    return min(max(a.xmin-b.xmax,b.xmin-a.xmax,a.ymin-b.ymax,b.ymin-a.ymax)
               for i,a in enumerate(bb) for b in bb[i+1:])
board_gap=c.P-c.FLAT
tray_gap=_gaps(c.piece_boxes('A'))
record('finger-room',board_gap>=15 and tray_gap>=12,{'board_gap_between_stones_mm':board_gap,
       'tray_gap_between_stacks_mm':round(tray_gap,1),'v15_board_gap_mm':8.5})

# Glue-up registration: two pegs on each base locate its plate. Nominal is
# clear; a 0.3 mm shift (twice the clearance) or a 0.3 degree twist about the back peg is blocked.
# Every glue well sits over a wall top with 0.5 mm of land around it.
reg={}
for s_ in 'AB':
    p,b=c.plate(s_),c.base(s_)
    px,py,_=c.PEG_BACK
    if s_=='B':px=2*c.SEAM-px
    r={'nominal':round(ov(p,b),4)}
    for ax,v in (('x+',(.3,0,0)),('x-',(-.3,0,0)),('y+',(0,.3,0)),('y-',(0,-.3,0))):
        r[ax+'0.3']=round(ov(p.translate(v),b),3)
    for d in (.3,-.3):
        r[f'twist{d:+}deg']=round(ov(p.rotate((px,py,0),(px,py,1),d),b),3)
    reg[f'plate-{s_}']=r
land=[]
for s_ in 'AB':
    for x0,x1,y0,y1 in c.WELLS:
        pr=c.box(x0-.5,x1+.5,y0-.5,y1+.5,c.PLATE_Z-.5,c.PLATE_Z)
        pr=pr if s_=='A' else c.mirror_b(pr)
        land.append(round(pr.Volume()-ov(pr,c.base(s_)),4))
reg['glue_well_land_missing_mm3']=max(land)
# The plate over each socket must be solid up to the face: no grid or art cut into its roof.
roof=[]
for s_ in 'AB':
    k=c.sockets().translate((0,0,c.SOCKET_D+.1)).intersect(c.box(-1,c.WX+1,-1,c.WY+1,c.PLATE_Z,c.FACE))
    k=k if s_=='A' else c.mirror_b(k)
    roof.append(round(k.Volume()-ov(k,c.plate(s_)),4))
reg['socket_roof_mm']=round(c.FACE-c.PLATE_Z-c.SOCKET_D,2)
reg['socket_roof_missing_mm3']=max(roof)
reg['peg_mm']={'back_d':2*c.PEG_BACK[2],'fore_d':2*c.PEG_FORE[2],'height':c.PEG_H,'clearance':c.PEG_CLR}
record('plates-register-for-gluing',
       all(r['nominal']<TOL and all(v>TOL for k_,v in r.items() if k_!='nominal')
           for k_,r in reg.items() if k_.startswith('plate'))
       and max(land)<TOL and max(roof)<TOL and reg['socket_roof_mm']>=.4,reg)

# Cross ribs behind the tray: clear of the fully inserted tray and of leaf B's
# buckle panel and its slits, and they reach the plate seat so the plate rests on them.
rib_lo=c.BULK_Y-c.RIB_T/2;rib_hi=max(c.RIB_Y)+c.RIB_T/2
ribs={'tray_clear_mm':round(rib_lo-c.DR_Y1,2),
      'panel_clear_mm':round(c.PANEL_Y[0]-c.PANEL_SLIT-rib_hi,2),
      'tray_overlap_mm3':round(max(ov(c.tray(s_),c.base(s_)) for s_ in 'AB'),4)}
seat=c.box(c.FORE+1,c.LEAF_X1-c.SEAM_WALL-1,rib_lo,rib_hi,c.PLATE_Z-.05,c.PLATE_Z)
ribs['seat_mm3']=round(ov(seat,c.base('A')),3)
spine=c.box((c.FORE+c.LEAF_X1-c.SEAM_WALL)/2-c.SPINE_W/2+.1,(c.FORE+c.LEAF_X1-c.SEAM_WALL)/2+c.SPINE_W/2-.1,c.SPINE_Y[0]+1,c.SPINE_Y[1]-1,c.PLATE_Z-.05,c.PLATE_Z)
ribs['spine_seat_mm3']=round(ov(spine,c.base('A')),3)
_rz=(c.PLATE_Z-.2,c.PLATE_Z+c.WELL_D+.1)
_newribs=c.box(c.FORE,c.LEAF_X1-c.SEAM_WALL,c.BULK_Y-c.RIB_T/2,c.BULK_Y+c.RIB_T/2,*_rz).fuse(
    c.box((c.FORE+c.LEAF_X1-c.SEAM_WALL)/2-c.SPINE_W/2,(c.FORE+c.LEAF_X1-c.SEAM_WALL)/2+c.SPINE_W/2,c.SPINE_Y[0],c.SPINE_Y[1],*_rz))
ribs['new_ribs_vs_plate_sockets_and_glue_wells_mm3']=round(ov(_newribs,c.sockets())+ov(_newribs,c.glue_wells()),4)
record('cross-ribs',ribs['tray_clear_mm']>=1.5 and ribs['spine_seat_mm3']>0 and ribs['new_ribs_vs_plate_sockets_and_glue_wells_mm3']<TOL and ribs['panel_clear_mm']>=2
       and ribs['tray_overlap_mm3']<TOL and ribs['seat_mm3']>0,ribs)


# Tray insert (added after the trays were printed). The flats lie flat, 4 across
# and 5 deep, in four lanes; the 21st flat has its own pocket; the pawn lies in
# a saddle. Flats are checked packed to the front and to the back of every lane.
ins={}
lanes,pocket,stop=c._ins_layout()
for side,team in (('A','cat'),('B','witch')):
    I=c.tray_insert(side);t=c.tray(side)
    z=c.DR_Z0+c.DR_FLOOR+c.INS_FLOOR;h=c.FLAT_PRINTED     # flats rest on the insert floor
    def flats(back):
        out=[]
        for x0,x1,y0,y1 in lanes:
            cx_=(x0+x1)/2
            for j in range(c.LANE_FLATS):
                y=(y1-c.LANE_FLATS*h+j*h) if back else (y0+j*h)
                out.append(c.box(cx_-h/2,cx_+h/2,y,y+h,z,z+c.FLAT_T))
        px0,px1,py0,py1=pocket;cx_,cy_=(px0+px1)/2,(py0+py1)/2
        out.append(c.box(cx_-h/2,cx_+h/2,cy_-h/2,cy_+h/2,z,z+c.FLAT_T))
        return out
    S=flats(False)+flats(True)
    capst=_upright(_load(f'{team}-capstone')).rotate((0,0,0),(1,0,0),-90)
    b=capst.BoundingBox();x,ya,yb=c.cap_slot()
    capst=capst.translate((x-(b.xmin+b.xmax)/2,ya-b.ymin,c.DR_Z0+c.DR_FLOOR-c.CRADLE_D-b.zmin))
    if side=='B':S=[c.mirror_b(s_) for s_ in S];capst=c.mirror_b(capst)
    ib=I.BoundingBox()
    ins[side]={'solids':len(I.Solids()),'valid':I.isValid(),
        'vs_tray':round(ov(I,t),4),'vs_pressed_arm':round(ov(I,bent if side=='A' else c.mirror_b(bent)),4),
        'vs_plate_and_base':round(worst([I],[c.plate(side),c.base(side)]),4),
        'flats_vs_insert':round(max(ov(s_,I) for s_ in S),4),
        'capstone_vs_insert':round(ov(capst,I),4),
        'flats_vs_tray':round(max(ov(s_,t) for s_ in S),4),
        'top_under_plate_mm':round(c.PLATE_Z-ib.zmax,2),
        'lane_clearance_per_side_mm':round((c.LANE-c.FLAT_PRINTED)/2,3),
        'wall_gap_to_tray_mm':c.INS_CLR,'mass_g_pla':round(I.Volume()*1.24e-3,1)}
ins['lane_length_mm']=round(lanes[0][3]-lanes[0][2],1)
ins['flats_held']=c.LANES*c.LANE_FLATS+1
record('tray-insert-fits',all(r['solids']==1 and r['valid'] and r['vs_tray']<TOL and r['vs_pressed_arm']<TOL
       and r['vs_plate_and_base']<TOL and r['flats_vs_insert']<TOL and r['capstone_vs_insert']<TOL
       and r['flats_vs_tray']<TOL and r['top_under_plate_mm']>=1 for k_,r in ins.items() if k_ in 'AB')
       and ins['flats_held']==21,ins)

hinged=cq.Compound.makeCompound([c.base('A'),c.base('B')])
def ext(s):b=s.BoundingBox();return [round(b.xlen,1),round(b.ylen,1),round(b.zlen,1)]
beds={'hinged-bases':ext(hinged),'plate':ext(c.plate('A')),'tray':ext(c.tray_a()),'tray-insert':ext(c.tray_insert_a())}
record('fits-256-bed',all(max(v)<=250 for v in beds.values()),beds)
json.dump(report,open(OUT/'reports'/'geometry-verification.json','w'),indent=1)
print('ALL PASS')
