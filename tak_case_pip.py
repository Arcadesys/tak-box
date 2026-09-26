"""v5 case with pin-free hinges: print-in-place main seams, snap-on lids.

The v5 filament-pin hinges are walled shut at both ends, so a pin cannot be fed
in. Here the two main folds use print-in-place cone-pin hinges and the two lids
snap onto stub axles. Geometry is otherwise tak_case.py's; this module only
replaces the knuckles. Tuned from the hinge test strips (tak_hinges.py).

Frame  center row + both wings, main hinges print already assembled. Print the
       playing face down: the well floors become bridged roofs (supports, all
       reachable from the open wells because the lids are separate parts) and
       the play face lands on the textured PEI.
Lids   print face down, separately, and press onto the wing stubs from above.
"""
import dataclasses
import cadquery as cq
import tak_case as base
from tak_case import box,cylinder,wing_y,lid_blank
from tak_box_base import D as D0

D=dataclasses.replace(D0,barrel_diameter=5.0,knuckle_length=19.0,
                      knuckle_gap=0.4,knuckle_margin=5.7)
L,GAP,COUNT,MARGIN=D.knuckle_length,D.knuckle_gap,D.knuckle_count,D.knuckle_margin
STEP=L+GAP
CLR=0.4                              # radial clearance, print-in-place
# storage: one layer of 8 mm flats needs ~11 mm, not the 19.2 mm v5 cut
TILE_D=10.7                          # tile well depth below the lid plane (z=1.1)
FLOOR_T=3.0                          # plate under the tile well
LANE_W,DIV_W=20.6,1.6                # three lanes, one row of 20 mm flats each, split by thin
                                     # dividers so every well roof spans ~21 mm and bridges
WELL_W=3*LANE_W+2*DIV_W              # 65.0
UNDER_PAN=True                       # open the underside beneath the tile well
KEY_R=10.6                           # keystone pocket: Ø21.2 round bottom for the Ø19.4 pawn
KEY_BOTTOM=-18.6                     # deepest point of the keystone pocket (as in v5)
# magnets are 4 x 2 mm discs: pockets get printing clearance (Ø4.2 x 2.2) and a glue line
MAG_R,MAG_D=2.1,2.2
# main seam: cone pins, Ø2 (barrel Ø5)
PIN_R,PIN_CYL,PIN_CONE=1.0,2.0,0.8
# lid: stub axles + C-clip
LID_R,STUB_R,STUB_LEN,BORE_R,MOUTH=3.0,1.5,9.0,1.7,2.5

def cone(r0,r1,x0,x1,y,z):
    d=1 if x1>x0 else -1
    return cq.Solid.makeCone(r0,r1,abs(x1-x0),cq.Vector(x0,y,z),cq.Vector(d,0,0))

def pin(face,d,y,z,r=PIN_R,cyl=PIN_CYL,tip=PIN_CONE):
    end=face+d*cyl
    return cylinder_x(r,face,end,y,z).fuse(cone(r,r-tip,end,end+d*tip,y,z))

def socket(face,d,y,z,r=PIN_R,cyl=PIN_CYL):
    """Socket for a pin whose knuckle face is `face` and which points along d."""
    bface=face+d*GAP
    end=face+d*(cyl+GAP)
    s=cylinder_x(r+CLR,bface-d*0.05,end,y,z)
    return s.fuse(cone(r+CLR,0.1,end,end+d*(r+CLR-0.1),y,z))

def cylinder_x(r,x0,x1,y,z):
    return cq.Solid.makeCylinder(r,abs(x1-x0),cq.Vector(min(x0,x1),y,z),cq.Vector(1,0,0))

def knuckle_x(k): return MARGIN+k*STEP

def keystone_pocket(y0):
    """Round-bottomed sideways pocket for the pawn: straight walls above a
    semicircle, so face down it prints as a self-supporting arch."""
    yc=y0+41.0                                    # centre of the v5 24 mm pocket
    zc=KEY_BOTTOM+KEY_R
    arc=cq.Solid.makeCylinder(KEY_R,29,cq.Vector(168,yc,zc),cq.Vector(1,0,0))
    top=box(29,2*KEY_R,1.1-zc,168,yc-KEY_R,zc)
    return arc.fuse(top)

def shell(index,d=D):
    """tak_case.shell with print-in-place cone-pin seam knuckles."""
    if index not in (0,1,2):raise ValueError(index)
    if index==1:
        part=box(205,41,4,0,82,0)
        for x in (0,203):part=part.fuse(box(2,37,20.1,x,84,-20.1))
    else:
        y0=wing_y(index)
        part=box(205,82,1,0,y0,0)
        part=part.fuse(box(200,74,21.1,2.5,y0+4,-20.1))
        outer_y=y0 if index==0 else y0+78
        part=part.fuse(box(200,4,21.1,2.5,outer_y,-20.1))
        fixed_y=y0+79.5 if index==0 else y0
        part=part.fuse(box(205,2.5,3,0,fixed_y,1))
        well_y=y0+(7 if index==0 else 10)      # 65 mm well; keeps 6 mm of wall at the latch pockets
        for lane in range(3):
            part=part.cut(box(152,LANE_W,TILE_D,8,well_y+lane*(LANE_W+DIV_W),1.1-TILE_D))
        part=part.cut(keystone_pocket(y0))
        if UNDER_PAN:
            # open pan under the tile well: the wing rests on its rim, and printed
            # face down this recess opens upward, so it needs no support
            pan_top=1.1-TILE_D-FLOOR_T
            # inset 1.5 mm all round so the rails keep their thickness around the magnet holes
            part=part.cut(box(152-3,WELL_W-3,pan_top+20.2,8+1.5,well_y+1.5,-20.2))
    R=d.barrel_diameter/2
    for seam_i,edge_y in enumerate(d.seam_y):
        if index not in (seam_i,seam_i+1):continue
        left=index==seam_i
        # 1) clear the neighbour's knuckle zone, including the gaps beside it
        for k in range(COUNT):
            if (k%2==0)!=left:
                x=knuckle_x(k)
                part=part.cut(cylinder(R+CLR,L+2*GAP,x-GAP,edge_y,d.hinge_z))
        # 2) own knuckles, then pins (even) or sockets (odd)
        for k in range(COUNT):
            if (k%2==0)!=left:continue
            x=knuckle_x(k)
            part=part.fuse(cylinder(R,L,x,edge_y,d.hinge_z))
            lug_y=edge_y-2.4 if left else edge_y
            part=part.fuse(box(L,2.4,2,x,lug_y,0))
            if k%2==0:
                # even knuckles carry pins toward both neighbours
                if k>0:part=part.fuse(pin(x,-1,edge_y,d.hinge_z))
                if k<COUNT-1:part=part.fuse(pin(x+L,1,edge_y,d.hinge_z))
            else:
                # odd knuckles hold the sockets; the neighbours' pin faces
                # sit GAP outside this knuckle and point into it
                part=part.cut(socket(x-GAP,1,edge_y,d.hinge_z))
                if k<COUNT-1:part=part.cut(socket(x+L+GAP,-1,edge_y,d.hinge_z))
    if index in (0,2):
        axis_y=d.seam_y[0 if index==0 else 1]
        unwind=-90 if index==0 else 90
        for x in (12.0,68.0,129.0,185.0):
            pad_y=96.1 if index==0 else 102.9
            face_y=102.1 if index==0 else 102.9
            direction=cq.Vector(0,-1 if index==0 else 1,0)
            pad=box(8,6,5,x,pad_y,-80)
            hole=cq.Solid.makeCylinder(MAG_R,MAG_D,cq.Vector(x+4,face_y,-77.5),direction)
            pad=pad.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            hole=hole.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            part=part.fuse(pad).cut(hole)
    return part.clean()

def lid_pair(index,d=D):
    """Wing base with stub axles on even knuckles; lid with C-clip barrels on
    odd knuckles. Lid plate hangs off +Y (index 0) or -Y (index 2)."""
    base_part,lid=shell(index,d),lid_blank(index)
    axis_y=0 if index==0 else 205
    side=1 if index==0 else -1                 # direction from the axis into the lid plate
    axis_z=1.0
    R=LID_R
    fw=(L-2*0.8)/3
    # 1) clear each side's neighbour knuckle zone, gaps included
    for k in range(COUNT):
        x=knuckle_x(k)
        cut=cylinder(R+CLR,L+2*GAP,x-GAP,axis_y,axis_z)
        if k%2==0: lid=lid.cut(cut)
        else: base_part=base_part.cut(cut)
    # 2) base knuckles + stubs, lid clip barrels
    for k in range(COUNT):
        x=knuckle_x(k)
        if k%2==0:                              # base knuckle: barrel + stubs
            base_part=base_part.fuse(cylinder(R,L,x,axis_y,axis_z))
            for face,dr,has in ((x,-1,k>0),(x+L,1,k<COUNT-1)):
                if not has:continue
                end=face+dr*STUB_LEN
                base_part=base_part.fuse(cylinder_x(STUB_R,face,end-dr*0.5,axis_y,axis_z))
                base_part=base_part.fuse(cone(STUB_R,STUB_R-0.5,end-dr*0.5,end,axis_y,axis_z))
        else:                                   # lid knuckle: C-clip barrel
            barrel=cylinder(R,L,x,axis_y,axis_z)
            # 45-degree fillet under the outboard half so it prints face-down
            barrel=barrel.fuse(box(L,2.12,0.88,x,axis_y-side*2.12 if side>0 else axis_y,3.12))
            lid=lid.fuse(barrel)
            lid=lid.cut(cylinder_x(BORE_R,x-.1,x+L+.1,axis_y,axis_z))
            hw=MOUTH/2
            lid=lid.cut(box(L+.2,MOUTH,R+0.1,x-.1,axis_y-hw,axis_z-R-0.1))
            zb=axis_z-R-0.1
            flare=(cq.Workplane('YZ').polyline([(axis_y-hw-1.05,zb),(axis_y+hw+1.05,zb),
                   (axis_y+hw,zb+1.3),(axis_y-hw,zb+1.3)]).close().extrude(L+.2)
                   .translate((x-.1,0,0)).val())
            lid=lid.cut(flare)
            for i in (1,2):                      # relief slits: three flexing fingers
                sx=x+i*fw+(i-1)*0.8
                y0s,y1s=(axis_y-R-0.2,axis_y+0.3) if side>0 else (axis_y-0.3,axis_y+R+0.2)
                lid=lid.cut(box(0.8,y1s-y0s,2*R+0.4,sx,y0s,axis_z-R-0.2))
    return base_part.clean(),lid.clean()

LID_PIN_R,LID_PIN_CYL,LID_PIN_TIP=1.5,2.5,1.2      # the pin tested on the hinge strips

def lid_pair_pip(index,d=D):
    """Print-in-place lid hinge (Ø6 barrels, Ø3 pins, 0.4 mm clearance).

    Even knuckles belong to the wing and carry the pins; odd knuckles belong to
    the lid and hold the sockets. Printed with the lid swung open 180 degrees.
    """
    base_part,lid=shell(index,d),lid_blank(index)
    axis_y=0 if index==0 else 205
    az,R=1.0,LID_R
    for k in range(COUNT):
        x=knuckle_x(k)
        cut=cylinder(R+CLR,L+2*GAP,x-GAP,axis_y,az)
        if k%2==0: lid=lid.cut(cut)
        else: base_part=base_part.cut(cut)
    for k in range(COUNT):
        x=knuckle_x(k)
        barrel=cylinder(R,L,x,axis_y,az)
        # flat 3 mm strip on the play-face side of the barrel gives the first
        # layer something to stick to when printed face down
        barrel=barrel.fuse(box(L,3.0,0.4,x,axis_y-1.5,3.6))
        if k%2==0:
            base_part=base_part.fuse(barrel)
            if k>0:base_part=base_part.fuse(pin(x,-1,axis_y,az,LID_PIN_R,LID_PIN_CYL,LID_PIN_TIP))
            if k<COUNT-1:base_part=base_part.fuse(pin(x+L,1,axis_y,az,LID_PIN_R,LID_PIN_CYL,LID_PIN_TIP))
        else:
            lid=lid.fuse(barrel)
            lid=lid.cut(socket(x-GAP,1,axis_y,az,LID_PIN_R,LID_PIN_CYL))
            if k<COUNT-1:lid=lid.cut(socket(x+L+GAP,-1,axis_y,az,LID_PIN_R,LID_PIN_CYL))
    # two Ø4 x 2 magnet pairs hold each lid shut (as in v5): pockets in the wall top
    # and in the lid underside, on the seam side
    latch_y=75 if index==0 else 130
    for x in (42,163):
        base_part=base_part.cut(cq.Solid.makeCylinder(MAG_R,MAG_D,cq.Vector(x,latch_y,1),cq.Vector(0,0,-1)))
        lid=lid.cut(cq.Solid.makeCylinder(MAG_R,MAG_D,cq.Vector(x,latch_y,1),cq.Vector(0,0,1)))
    return base_part.clean(),lid.clean()

def sol(o): return o.val() if hasattr(o,'val') else o

def posed(shape,index,degrees):return base.posed(shape,index,degrees)

def lid_open(lid,index,degrees):return base.lid_open(lid,index,degrees)
