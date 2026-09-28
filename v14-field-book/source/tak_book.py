"""Tak v14 field book: the board folds in half with its face inside; a
snap-in piece tray slides out from under each half. No hardware.

Units: mm. Open, the book lies flat: leaf A at x 0..67.8, leaf B at
x 68.2..136, faces up at z=FACE. The grid stands LINE_RAISE proud of the face in
a second colour. The fold axis runs along y at (x=68, z=AXZ), the top of the
lines, so closing rotates B 180 degrees onto A and the raised grids meet.

Each leaf is a base (2 mm floor skin, fore wall, seam wall, 10 mm back wall), a
glued face plate carrying half the board, and a tray that slides out of the
front end (y=0). A tray locks with a button on a flexible arm in its outer wall
and is released by pressing the button in from the book's side.

The book closes with a buckle at the far edge: a tab on leaf A pushes into a
slot in leaf B's back corner and clicks under a catch. The catch hangs on a
spring panel cut into the outer skin of B's fore wall; pressing that side of
the case pulls the catch clear so the halves lift apart. Flexing members bend
within the print layers. A groove along the fore edge gives the thumb a grip. Hinge knuckles print in place
at both ends of the spine.
"""
from functools import lru_cache
import cadquery as cq

# ---- board
P=24.0
WX=136.0
WY=142.0
SEAM=WX/2
HG=.2
FX0,FY0=8.0,10.0
LINE_W=.8
LINE_D=.6
LINE_CLR=.1                 # groove clearance per side for a separately printed grid

# ---- heights
FLOOR=2.0
DR_Z0=FLOOR+.2
DR_FLOOR=1.0
DR_INNER=17.6
DR_TOP=DR_Z0+DR_FLOOR+DR_INNER      # 20.8
PLATE_Z=DR_TOP+.4                   # 21.2
PLATE=2.0
FACE=PLATE_Z+PLATE                  # 23.2
LINE_RAISE=.4                       # grid stands proud of the face
AXZ=FACE+LINE_RAISE                 # fold axis at the top of the grid lines

# ---- leaf A walls and tray
LEAF_X1=SEAM-HG
FORE=3.0
SEAM_WALL=2.2
BACK=10.0
CLR=.3
DR_WALL=1.2
DR_FRONT=2.0
DR_X=(FORE+CLR,LEAF_X1-SEAM_WALL-CLR)
DR_Y1=WY-BACK-CLR

# ---- push-button tray latch (fore side of each tray)
ARM_Y=(2.6,28.5)          # cantilever in the outer wall, beside the capstone; root at 28.5
ARM_Z=(3.5,16.5)
ARM_SLOT=.8
BTN_Y=(5.0,14.6)
BTN_Z=(5.1,14.9)
BTN_TIP_X=1.6             # button face sits 1.6 mm inside the book's side face
BTN_RAMP=1.7              # 45-degree lead-in on the button's back face
WIN_Y=(4.8,15.0)
WIN_Z=(4.9,15.1)
DISH_R=8.0
DISH_D=1.5                # outer finger dish; the wall is 1.5 mm at the window
RELEASE=FORE+.05-BTN_TIP_X   # inward travel that frees the button, 1.45
CORNER_R=6.0
EDGE_R=2.0
THUMB=1.2

# ---- hinge (print in place)
KR=3.0
RELIEF=KR+.4
PIN_R=1.5
PIN_CLR=.4
KNUCKLE_B=((0.0,4.3),(WY-4.3,WY))        # outer, carry pins
KNUCKLE_A=((4.7,9.0),(WY-9.0,WY-4.7))    # inner, carry sockets

# ---- far-edge buckle: tab on leaf A pushes into a slot in leaf B's back
# corner; a catch ring on a spring panel in B's fore wall grips a notch in the
# tab. Pressing that panel (the side of the case) pulls the catch clear.
# All buckle geometry is given in leaf B's open frame.
TAB_X=(130.2,132.6)
TAB_Y=(134.5,138.9)
TAB_TIP=13.2
TAB_NOTCH_X=1.0             # catch engagement depth
TAB_NOTCH_Z=(15.1,17.5)
SLOT_CLR=.3
SLOT_ARC=1.2
TOOTH_X=(128.8,TAB_X[0]+TAB_NOTCH_X-.2)
TOOTH_Z=(15.3,17.3)
RING_X=(127.4,134.3)
RING_Y=(133.5,139.9)
RING_BAR=.7
RING_Z=(14.8,17.8)
PANEL_X=(134.2,136.2)
PANEL_Y=(115.0,140.2)       # root at 115, free end at the back corner
PANEL_Z=(9.3,19.3)
PANEL_SLIT=.8                # wide enough that the 25 mm bridge over it can't fuse
RING_DROP=2.5                # open space under the catch ring so its first layer can sag freely
PRESS=1.4                   # panel travel that frees the catch


def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()

def cyly(r,y0,y1,x,z):
    return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))

def coney(r0,r1,y0,y1,x,z):
    d=1 if y1>y0 else -1
    return cq.Solid.makeCone(r0,r1,abs(y1-y0),cq.Vector(x,y0,z),cq.Vector(0,d,0))

def mirror_b(s):
    return s.mirror('YZ',(SEAM,0,0))

def fold(s,angle):
    """Rotate a leaf-B shape about the spine. 0 = open flat, 180 = closed."""
    return s.rotate((SEAM,0,AXZ),(SEAM,1,AXZ),-angle)


# ================================================================== base
def _base_body():
    p=box(0,LEAF_X1,0,WY,0,PLATE_Z)
    p=cq.Workplane(obj=p).edges('|Z and <X').fillet(CORNER_R).val()
    p=cq.Workplane(obj=p).faces('<Z').edges().fillet(EDGE_R).val()
    p=p.cut(box(FORE,LEAF_X1-SEAM_WALL,-.1,WY-BACK,FLOOR,PLATE_Z+.1))
    # Latch window through the fore wall, inside a shallow finger dish.
    p=p.cut(box(DISH_D-.01,FORE+.1,*WIN_Y,*WIN_Z))
    cy,cz=sum(WIN_Y)/2,sum(WIN_Z)/2
    p=p.cut(cq.Solid.makeCylinder(DISH_R,DISH_D+.1,cq.Vector(-.1,cy,cz),cq.Vector(1,0,0)))
    # Lead-in on the inner front corner of the fore wall for the button ramp.
    lead=(cq.Workplane('XY',origin=(0,0,WIN_Z[0]-1)).polyline([(FORE+.01,-.1),(FORE-1.0,-.1),(FORE+.01,1.0)])
          .close().extrude(WIN_Z[1]-WIN_Z[0]+2).val())
    return p.cut(lead).clean()

def _pin(face_y,d):
    end=face_y+d*2.5
    return cyly(PIN_R,min(face_y,end),max(face_y,end),SEAM,AXZ).fuse(
        coney(PIN_R,.3,end,end+d*1.2,SEAM,AXZ))

def _socket(mouth_y,d):
    end=mouth_y+d*2.8
    s=cyly(PIN_R+PIN_CLR,min(mouth_y-d*.05,end),max(mouth_y-d*.05,end),SEAM,AXZ)
    return s.fuse(coney(PIN_R+PIN_CLR,.1,end,end+d*1.3,SEAM,AXZ))

@lru_cache(None)
def base(side):
    assert side in 'AB'
    p=_base_body()
    if side=='B':
        p=mirror_b(p)
        p=_buckle_socket(p)
        p=p.cut(_deboss())
    own,other=(KNUCKLE_A,KNUCKLE_B) if side=='A' else (KNUCKLE_B,KNUCKLE_A)
    for y0,y1 in other:
        p=p.cut(cyly(RELIEF,y0-.4,y1+.4,SEAM,AXZ))
    for y0,y1 in own:
        p=p.fuse(cyly(KR,y0,y1,SEAM,AXZ))
    if side=='B':
        p=p.fuse(_pin(KNUCKLE_B[0][1],1)).fuse(_pin(KNUCKLE_B[1][0],-1))
    else:
        p=p.cut(_socket(KNUCKLE_A[0][0],1)).cut(_socket(KNUCKLE_A[1][1],-1))
    return p.clean()


# ============================================================ face plate
def _lines(clr=0.0):
    out=[]
    w=LINE_W/2+clr
    for i in range(6):
        y=FY0+P*i
        out.append(box(FX0-w,LEAF_X1,y-w,y+w,FACE-LINE_D-clr,FACE+LINE_RAISE))
    for i in range(3):
        x=FX0+P*i
        out.append(box(x-w,x+w,FY0-w,FY0+5*P+w,FACE-LINE_D-clr,FACE+LINE_RAISE))
    s=out[0]
    for o in out[1:]:s=s.fuse(o)
    return s.clean()

def _plate_body(top=FACE):
    p=box(0,LEAF_X1,0,WY,PLATE_Z,top)
    p=cq.Workplane(obj=p).edges('|Z and <X').fillet(CORNER_R).val()
    for y0,y1 in ((-.1,FY0+.3),(WY-FY0-.3,WY+.1)):
        p=p.cut(box(SEAM-RELIEF-.3,SEAM,y0,y1,PLATE_Z-.1,top+.1))
    return p.clean()

@lru_cache(None)
def plate(side):
    p=_plate_body().cut(_lines(LINE_CLR))
    # Thumb groove: the fore edges of the two plates form a V when closed.
    groove=(cq.Workplane('XZ').polyline([(-.1,FACE+.1),(THUMB,FACE+.1),(-.1,FACE-THUMB)])
            .close().extrude(-(WY+.2)).translate((0,-.1,0)).val())
    p=p.cut(groove)
    if side=='A':
        return p.fuse(tab()).clean()
    p=mirror_b(p.clean())
    return p.cut(_slot()).clean()

@lru_cache(None)
def inlay(side):
    g=_lines().intersect(_plate_body(FACE+LINE_RAISE)).clean()
    return g if side=='A' else mirror_b(g)


# ================================================================ buckle
def _tab_b():
    """Tab in leaf B's frame at the closed pose."""
    top=2*AXZ-FACE+.01
    t=box(*TAB_X,*TAB_Y,TAB_TIP,top)
    t=t.cut(box(TAB_X[0]-.1,TAB_X[0]+TAB_NOTCH_X,TAB_Y[0]-.1,TAB_Y[1]+.1,*TAB_NOTCH_Z))
    # Lead-in on the tip's inner edge cams the catch aside.
    cam=(cq.Workplane('XZ').polyline([(TAB_X[0]-.1,TAB_TIP-.1),(TAB_X[0]+1.5,TAB_TIP-.1),(TAB_X[0]-.1,TAB_TIP+1.6)])
         .close().extrude(-(TAB_Y[1]-TAB_Y[0]+.2)).translate((0,TAB_Y[0]-.1,0)).val())
    return t.cut(cam)

@lru_cache(None)
def tab():
    """The tab on leaf A's plate (world frame)."""
    return fold(_tab_b(),180).clean()

def _slot():
    # Wider on the outer side: the tab swings out along its arc as it enters.
    return box(TAB_X[0]-SLOT_CLR,TAB_X[1]+SLOT_ARC,TAB_Y[0]-SLOT_CLR,TAB_Y[1]+SLOT_CLR,TAB_TIP-SLOT_CLR,FACE+.2)

@lru_cache(None)
def catch_ring():
    x0,x1=RING_X;y0,y1=RING_Y;z0,z1=RING_Z;b=RING_BAR
    r=box(x0,x0+1.4,y0,y1,z0,z1)
    r=r.fuse(box(x0,x1,y0,y0+b,z0,z1)).fuse(box(x0,x1,y1-b,y1,z0,z1))
    tooth=box(x0+1.39,TOOTH_X[1],TAB_Y[0]+.1,TAB_Y[1]-.1,*TOOTH_Z)
    tooth=cq.Workplane(obj=tooth).edges('|Y and >Z and >X').chamfer(1.0).val()
    return r.fuse(tooth).clean()

def _buckle_socket(p):
    x0,x1=PANEL_X;y0,y1=PANEL_Y;z0,z1=PANEL_Z;s=PANEL_SLIT
    # Free the panel: behind, above, below and at its free end.
    p=p.cut(box(x0-s,x0,y0,y1+s,z0-s,z1+s))
    p=p.cut(box(x0-s,x1,y0,y1+s,z1,z1+s)).cut(box(x0-s,x1,y0,y1+s,z0-s,z0))
    p=p.cut(box(x0-s,x1,y1,y1+s,z0-s,z1+s))
    # Cavity for the catch ring's travel, and the tab slot.
    p=p.cut(box(RING_X[0]-PRESS-.3,x0,RING_Y[0]-.3,RING_Y[1]+.3,RING_Z[0]-RING_DROP,RING_Z[1]+.3))
    p=p.cut(_slot())
    return p.fuse(catch_ring())

def panel_region():
    x0,x1=PANEL_X;y0,y1=PANEL_Y;z0,z1=PANEL_Z
    return box(x0,x1,y0+.01,y1,z0,z1)

def pressed_parts():
    """Catch ring and panel free end, moved in by PRESS (translation; conservative)."""
    return [catch_ring().translate((-PRESS,0,0))]


def _deboss():
    """TAK in leaf B's floor, mirrored so it reads correctly on the closed cover."""
    t=cq.Workplane('XY').text('TAK',16,.7,font='Arial',kind='bold',combine=True).val()
    b=t.BoundingBox()
    t=t.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-.1))
    t=t.mirror('YZ',(0,0,0))
    return t.translate((SEAM+LEAF_X1/2+HG,WY/2,0))


# ================================================================== trays
@lru_cache(None)
def tray_a():
    x0,x1=DR_X
    p=box(x0,x1,0,DR_Y1,DR_Z0,DR_TOP)
    p=p.cut(box(x0+DR_WALL,x1-DR_WALL,DR_FRONT,DR_Y1-DR_WALL,DR_Z0+DR_FLOOR,DR_TOP+.1))
    p=cq.Workplane(obj=p).faces('<Z').edges().chamfer(.4).val()
    cx=(x0+x1)/2
    # Finger notch in the front's top edge.
    p=p.cut(cq.Solid.makeCylinder(7.0,DR_FRONT+.2,cq.Vector(cx,-.1,DR_TOP+2.0),cq.Vector(0,1,0)))
    # Free the latch arm: slots above, below and at its front end.
    xs=(x0-.1,x0+DR_WALL+.1)
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[1],ARM_Z[0]-ARM_SLOT,ARM_Z[0]))
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[1],ARM_Z[1],ARM_Z[1]+ARM_SLOT))
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[0],ARM_Z[0]-.1,ARM_Z[1]+.1))
    return p.fuse(_button()).clean()

def _button():
    x0=DR_X[0]
    b=box(BTN_TIP_X,x0+.01,*BTN_Y,*BTN_Z)
    # Square front face locks; the back face ramps so the tray snaps in.
    ramp=(cq.Workplane('XY',origin=(0,0,BTN_Z[0]-.1))
          .polyline([(BTN_TIP_X-.1,BTN_Y[1]-BTN_RAMP),(BTN_TIP_X-.1,BTN_Y[1]+.1),(x0+.02,BTN_Y[1]+.1)])
          .close().extrude(BTN_Z[1]-BTN_Z[0]+.2).val())
    b=b.cut(ramp)
    return cq.Workplane(obj=b).faces('<X').edges().chamfer(.3).val()

def _arm_region():
    x0=DR_X[0]
    return box(BTN_TIP_X-.1,x0+DR_WALL+.05,ARM_Y[0]-.05,ARM_Y[1]-.05,ARM_Z[0]-.05,ARM_Z[1]+.05)

@lru_cache(None)
def tray_released():
    """Arm and button pressed in by RELEASE (translated; conservative)."""
    t=tray_a();r=_arm_region()
    return t.cut(r).fuse(t.intersect(r).translate((RELEASE,0,0))).clean()

def tray(side,pull=0.0,shift=0.0,released=False):
    t=(tray_released() if released else tray_a()).translate((shift,-pull,0))
    return t if side=='A' else mirror_b(t)


# ============================================================= assemblies
def leaf_a(pull=0.0):
    return [base('A'),plate('A'),inlay('A'),tray('A',pull)]

def leaf_b(angle=0.0,pull=0.0):
    return [fold(p,angle) for p in (base('B'),plate('B'),inlay('B'),tray('B',pull))]

def assembly(angle=0.0,pulls=(0.0,0.0)):
    return cq.Compound.makeCompound(leaf_a(pulls[0])+leaf_b(angle,pulls[1]))


# ========================================================= piece envelopes
FLAT=19.5
STACK_H=16.0
CAP=(25.0,17.29,17.11)

def piece_boxes(side='A',pull=0.0):
    """11 two-high flat stacks and the capstone lying down, 3 across.
    The narrower capstone sits by the latch arm, leaving it room to flex."""
    x0=DR_X[0]+DR_WALL+.15;y0=DR_FRONT+.5;z=DR_Z0+DR_FLOOR
    cx=x0+FLAT-CAP[1]
    out=[box(cx,cx+CAP[1],y0,y0+CAP[0],z,z+CAP[2])]
    for j in range(3):
        y=y0+CAP[0]+.6+j*(FLAT+.6)
        out.append(box(x0,x0+FLAT,y,y+FLAT,z,z+STACK_H))
    for i in (1,2):
        for j in range(4):
            x=x0+i*(FLAT+.35);y=y0+j*(FLAT+.6)
            out.append(box(x,x+FLAT,y,y+FLAT,z,z+STACK_H))
    out=[b.translate((0,-pull,0)) for b in out]
    return out if side=='A' else [mirror_b(b) for b in out]

def print_pose(shape,flip=False):
    if flip:shape=shape.rotate((0,0,0),(1,0,0),180)
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))
