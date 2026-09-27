"""v5 case with 1.75 mm filament-pin hinges: separate center row, wings and lids.

Each hinge pin is a length of filament threaded through all ten knuckles: snug in
the fixed part's knuckles, free-turning in the moving part's, with a press-in plug
(tak_pinfit.plug) seated in a counterbore at each end. The margin at both board
edges is opened with a Ø4.4 channel so the filament can be fed in and the plug
flange sits flush.

Fixed side  main seams: center row      lids: wing
Free side   main seams: wing            lids: lid

Bore sizes are confirmed by the printed pin-fit coupon (tak_pinfit.py): strip 2
(fixed 1.90 / free 2.20) fit correctly, and the Ø1.70 plug hole grips best.

Layout, lanes, keystone pocket and magnets are tak_case_pip's. The underside pan
is dropped because the wings now print bottom down (wells open upward, no
supports), where the pan would be an unsupported 149 x 62 mm roof.
"""
import cadquery as cq
import tak_case_pip as p
import tak_pinfit as f
from tak_case import box,cylinder,wing_y,lid_blank

D=p.D
L,GAP,COUNT,MARGIN,STEP,CLR=p.L,p.GAP,p.COUNT,p.MARGIN,p.STEP,p.CLR
knuckle_x=p.knuckle_x
SEAM_R,LID_R=D.barrel_diameter/2,p.LID_R     # Ø5 main seam, Ø6 lid barrels
LID_Z=1.0

D_FIXED,D_FREE=1.90,2.20      # coupon strip 2, confirmed on the printed coupon
PLUG_HOLE=1.70                # confirmed on the printed coupon
CB_R,CB_D=f.CB_R,f.CB_D       # plug counterbore Ø3.2 x 1.5
CHANNEL_R=2.2                 # Ø4.4 feed channel through the 5.7 mm margins
LEAD=0.5                      # 45 degree lead-in on free-knuckle faces
PIN_LEN=knuckle_x(COUNT-1)+L-knuckle_x(0)+1.0   # knuckle span + both plug flanges

# Fill the closed gap above the unchanged wings' bodies (4 mm below the
# hinge axes). The skirt follows the existing circular barrel relief, rather
# than putting a square corner into the rotating barrel's path.
CENTER_CLEARANCE=0.4
CENTER_SKIN_DEPTH=4.0-CENTER_CLEARANCE
CENTER_END_T=2.5-CENTER_CLEARANCE  # wing body starts at x=2.5 / ends at 202.5

def center_outer_skirt(d=D):
    """Underside skin and two end feet; all dimensions are in the open pose.

    The end feet retain the -20.1 mm table plane. Hinge-concentric relief
    leaves 0.4 mm around the existing 2.5 mm barrels at every fold angle.
    The playing slab, knuckles, pin bores and feed channels are built below
    by the original shell code.
    """
    y0,y1=d.seam_y
    width=y1-y0-2*CENTER_CLEARANCE
    skirt=box(205,width,CENTER_SKIN_DEPTH,0,y0+CENTER_CLEARANCE,-CENTER_SKIN_DEPTH)
    for x in (0,205-CENTER_END_T):
        skirt=skirt.fuse(box(CENTER_END_T,width,20.1,x,y0+CENTER_CLEARANCE,-20.1))
    for y in d.seam_y:
        skirt=skirt.cut(cylinder(SEAM_R+CENTER_CLEARANCE,205.2,-0.1,y,d.hinge_z))
    return skirt.clean()

def cone_x(r0,r1,x0,d,y,z):
    return cq.Solid.makeCone(r0,r1,abs(r0-r1),cq.Vector(x0,y,z),cq.Vector(d,0,0))

def bore(part,k,fixed,y,z):
    """Cut knuckle k's bore (snug or free); outer knuckles get a plug counterbore."""
    x=knuckle_x(k); d=D_FIXED if fixed else D_FREE; r=d/2
    part=part.cut(cq.Solid.makeCylinder(r,L+0.1,cq.Vector(x-0.05,y,z),cq.Vector(1,0,0)))
    if not fixed:
        part=part.cut(cone_x(r+LEAD,r,x-0.05,1,y,z)).cut(cone_x(r+LEAD,r,x+L+0.05,-1,y,z))
    if k==0:
        part=part.cut(cq.Solid.makeCylinder(CB_R,CB_D+0.1,cq.Vector(x-0.1,y,z),cq.Vector(1,0,0)))
        part=part.cut(cone_x(r+0.5,r,x+CB_D,1,y,z))
    if k==COUNT-1:
        part=part.cut(cq.Solid.makeCylinder(CB_R,CB_D+0.1,cq.Vector(x+L-CB_D,y,z),cq.Vector(1,0,0)))
        part=part.cut(cone_x(r+0.5,r,x+L-CB_D,-1,y,z))
    return part

def feed_channels(part,y,z):
    """Open both board-edge margins along the hinge axis."""
    for x0,x1 in ((-0.1,knuckle_x(0)),(knuckle_x(COUNT-1)+L,205.1)):
        part=part.cut(cq.Solid.makeCylinder(CHANNEL_R,x1-x0,cq.Vector(x0,y,z),cq.Vector(1,0,0)))
    return part

def shell(index,d=D):
    """Structural section with bored seam knuckles (no lid hinge yet)."""
    if index not in (0,1,2):raise ValueError(index)
    if index==1:
        part=box(205,41,4,0,82,0)
        part=part.fuse(center_outer_skirt(d))
    else:
        y0=wing_y(index)
        part=box(205,82,1,0,y0,0)
        part=part.fuse(box(200,74,21.1,2.5,y0+4,-20.1))
        outer_y=y0 if index==0 else y0+78
        part=part.fuse(box(200,4,21.1,2.5,outer_y,-20.1))
        fixed_y=y0+79.5 if index==0 else y0
        part=part.fuse(box(205,2.5,3,0,fixed_y,1))
        well_y=y0+(7 if index==0 else 10)
        for lane in range(3):
            part=part.cut(box(152,p.LANE_W,p.TILE_D,8,well_y+lane*(p.LANE_W+p.DIV_W),1.1-p.TILE_D))
        part=part.cut(p.keystone_pocket(y0))
    for seam_i,edge_y in enumerate(d.seam_y):
        if index not in (seam_i,seam_i+1):continue
        left=index==seam_i
        for k in range(COUNT):
            if (k%2==0)!=left:
                part=part.cut(cylinder(SEAM_R+CLR,L+2*GAP,knuckle_x(k)-GAP,edge_y,d.hinge_z))
        for k in range(COUNT):
            if (k%2==0)!=left:continue
            x=knuckle_x(k)
            part=part.fuse(cylinder(SEAM_R,L,x,edge_y,d.hinge_z))
            part=part.fuse(box(L,2.4,2,x,edge_y-2.4 if left else edge_y,0))
        for k in range(COUNT):
            if (k%2==0)==left:
                part=bore(part,k,fixed=index==1,y=edge_y,z=d.hinge_z)
        part=feed_channels(part,edge_y,d.hinge_z)
    if index in (0,2):
        axis_y=d.seam_y[0 if index==0 else 1]
        unwind=-90 if index==0 else 90
        for x in (12.0,68.0,129.0,185.0):
            pad_y=96.1 if index==0 else 102.9
            face_y=102.1 if index==0 else 102.9
            direction=cq.Vector(0,-1 if index==0 else 1,0)
            pad=box(8,6,5,x,pad_y,-80)
            hole=cq.Solid.makeCylinder(p.MAG_R,p.MAG_D,cq.Vector(x+4,face_y,-77.5),direction)
            pad=pad.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            hole=hole.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            part=part.fuse(pad).cut(hole)
    return part.clean()

def lid_pair(index,d=D):
    """Wing (even knuckles, snug) and lid (odd knuckles, free) on the outer edge."""
    base_part,lid=shell(index,d),lid_blank(index)
    axis_y=0 if index==0 else 205
    for k in range(COUNT):
        cut=cylinder(LID_R+CLR,L+2*GAP,knuckle_x(k)-GAP,axis_y,LID_Z)
        if k%2==0: lid=lid.cut(cut)
        else: base_part=base_part.cut(cut)
    for k in range(COUNT):
        x=knuckle_x(k)
        barrel=cylinder(LID_R,L,x,axis_y,LID_Z)
        if k%2==0:
            base_part=bore(base_part.fuse(barrel),k,True,axis_y,LID_Z)
        else:
            # flat strip on the play-face side: bed contact when the lid prints face down
            barrel=barrel.fuse(box(L,3.0,0.4,x,axis_y-1.5,3.6))
            lid=bore(lid.fuse(barrel),k,False,axis_y,LID_Z)
    base_part=feed_channels(base_part,axis_y,LID_Z)
    lid=feed_channels(lid,axis_y,LID_Z)
    latch_y=75 if index==0 else 130
    for x in (42,163):
        base_part=base_part.cut(cq.Solid.makeCylinder(p.MAG_R,p.MAG_D,cq.Vector(x,latch_y,1),cq.Vector(0,0,-1)))
        lid=lid.cut(cq.Solid.makeCylinder(p.MAG_R,p.MAG_D,cq.Vector(x,latch_y,1),cq.Vector(0,0,1)))
    return base_part.clean(),lid.clean()

def overlay(index):
    """v5 black accent, notched clear of the wing's lid-hinge knuckles."""
    import tak_case as base
    o=base.overlay(index)
    if index==1:return o
    axis_y=0 if index==0 else 205
    for k in range(0,COUNT,2):
        o=o.cut(cylinder(LID_R+CLR,L+2*GAP,knuckle_x(k)-GAP,axis_y,LID_Z))
    return o.clean()

def pin_axis(name):
    """(y, z) of each filament pin: seam 0, seam 1, lid 0, lid 2."""
    return {'seam0':(D.seam_y[0],D.hinge_z),'seam1':(D.seam_y[1],D.hinge_z),
            'lid0':(0,LID_Z),'lid2':(205,LID_Z)}[name]

def filament(name,d=1.75):
    y,z=pin_axis(name)
    return cq.Solid.makeCylinder(d/2,PIN_LEN-1.0,cq.Vector(knuckle_x(0),y,z),cq.Vector(1,0,0))

sol=p.sol
posed=p.posed
lid_open=p.lid_open
