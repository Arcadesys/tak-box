"""Tak v13 book: the board folds in half with its face inside; a removable
piece tray slides out from under each half.

Units: mm. Open, the book lies flat: leaf A at x 0..67.8, leaf B at
x 68.2..136, faces up at z=FACE. The grid lines stand LINE_RAISE proud of the face in a
second colour. The fold axis runs along y at (x=68, z=AXZ), the top of the
lines, so closing rotates B 180 degrees onto A and the raised grids meet. Each leaf is a base
(floor, fore wall, seam wall, back wall), a glued face plate carrying half the
5 x 5 board, and a tray that slides out of the front end (y=0). Each tray
snaps in: a button on a flexible arm in its outer wall locks into a window in
the fore wall, and is pressed in from the book's side to release the tray. Hinge knuckles
print in place at both ends of the spine. A clasp on the back face of leaf A,
pivoting on an M3 screw, hooks a stud on leaf B.
"""
from functools import lru_cache
import cadquery as cq

# ---- board
P=24.0
WX=136.0
WY=138.0
SEAM=WX/2
HG=.2
FX0,FY0=8.0,9.0
LINE_W=.8
LINE_D=.6

# ---- heights
FLOOR=1.0
DR_Z0=FLOOR+.2
DR_FLOOR=1.0
DR_INNER=17.6
DR_TOP=DR_Z0+DR_FLOOR+DR_INNER      # 19.8
PLATE_Z=DR_TOP+.4                   # 20.2
PLATE=2.0
FACE=PLATE_Z+PLATE                  # 22.2
LINE_RAISE=.4                       # grid stands proud of the face
AXZ=FACE+LINE_RAISE                 # fold axis at the top of the grid lines

# ---- leaf A walls and tray
LEAF_X1=SEAM-HG
FORE=3.0
SEAM_WALL=2.2
BACK=6.0
CLR=.3
DR_WALL=1.2
DR_FRONT=2.0
DR_X=(FORE+CLR,LEAF_X1-SEAM_WALL-CLR)
DR_Y1=WY-BACK-CLR

# ---- push-button tray latch (fore side of each tray)
ARM_Y=(2.6,28.5)          # cantilever in the outer wall, beside the capstone; root at 28.5
ARM_Z=(3.5,16.5)
ARM_SLOT=.6
BTN_Y=(5.0,14.6)
BTN_Z=(5.1,14.9)
BTN_TIP_X=1.6             # button face sits 1.6 mm inside the book's side face
BTN_RAMP=1.7              # 45-degree lead-in on the button's back face
WIN_Y=(4.8,15.0)
WIN_Z=(4.9,15.1)
DISH_R=8.0
DISH_D=1.5                # outer finger dish; the wall is 1.5 mm at the window
RELEASE=FORE+.05-BTN_TIP_X   # inward travel that frees the button, 1.45
CORNER_R=3.0

# ---- hinge (print in place)
KR=3.0
RELIEF=KR+.4
PIN_R=1.5
PIN_CLR=.4
KNUCKLE_B=((0.0,4.3),(WY-4.3,WY))        # outer, carry pins
KNUCKLE_A=((4.7,9.0),(WY-9.0,WY-4.7))    # inner, carry sockets

# ---- clasp
PIVOT=(10.0,10.0)                        # x,z on leaf A back face
STUD=(10.0,2*AXZ-10.0)                  # closed-pose x,z of the stud on B
STUD_R=1.8
CLASP_T=2.6
CLASP_GAP=.3
CLASP_W=8.0
M3_PILOT=1.3
M3_CLEAR=1.65
M3_DEPTH=5.5


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
    p=cq.Workplane(obj=p).faces('<Z').edges().chamfer(.5).val()
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
    if side=='A':
        x,z=PIVOT
        p=p.cut(cyly(M3_PILOT,WY-M3_DEPTH,WY+.1,x,z))
    else:
        p=mirror_b(p)
        ox,oz=2*SEAM-STUD[0],2*AXZ-STUD[1]
        stud=cyly(STUD_R,WY-.01,WY+CLASP_GAP+CLASP_T+.5,ox,oz)
        stud=cq.Workplane(obj=stud).faces('>Y').edges().chamfer(.4).val()
        p=p.fuse(stud)
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
def _lines():
    out=[]
    for i in range(6):
        y=FY0+P*i
        out.append(box(FX0-LINE_W/2,LEAF_X1,y-LINE_W/2,y+LINE_W/2,FACE-LINE_D,FACE+LINE_RAISE))
    for i in range(3):
        x=FX0+P*i
        out.append(box(x-LINE_W/2,x+LINE_W/2,FY0-LINE_W/2,FY0+5*P+LINE_W/2,FACE-LINE_D,FACE+LINE_RAISE))
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
    p=_plate_body().cut(_lines()).clean()
    return p if side=='A' else mirror_b(p)

@lru_cache(None)
def inlay(side):
    g=_lines().intersect(_plate_body(FACE+LINE_RAISE)).clean()
    return g if side=='A' else mirror_b(g)


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


# ================================================================== clasp
@lru_cache(None)
def clasp_flat():
    """Pivot at origin in XZ, plate spans y 0..CLASP_T, arm along +z.
    The hook slot opens toward -x."""
    L=STUD[1]-PIVOT[1]
    w=CLASP_W/2
    r=STUD_R+.25
    top=L+r+2.2
    arm=box(-w,w,0,CLASP_T,-w,top)
    arm=cq.Workplane(obj=arm).edges('|Y').fillet(w-.01).val()
    arm=arm.cut(cyly(M3_CLEAR,-.1,CLASP_T+.1,0,0))
    slot=box(-w-.1,0,-.1,CLASP_T+.1,L-r,L+r).fuse(cyly(r,-.1,CLASP_T+.1,0,L))
    lead=(cq.Workplane('XZ').polyline([(-w-.1,L-r),(-w-.1,L-r-1.8),(-w+1.6,L-r)])
          .close().extrude(-(CLASP_T+.2)).translate((0,-.1,0)).val())
    return arm.cut(slot).cut(lead).clean()

def clasp(angle=0.0):
    """0 = locked (arm up). 90 = resting along +x on leaf A's back face."""
    s=clasp_flat().rotate((0,0,0),(0,1,0),angle)
    x,z=PIVOT
    return s.translate((x,WY+CLASP_GAP,z))


# ============================================================= assemblies
def leaf_a(pull=0.0):
    return [base('A'),plate('A'),inlay('A'),tray('A',pull)]

def leaf_b(angle=0.0,pull=0.0):
    return [fold(p,angle) for p in (base('B'),plate('B'),inlay('B'),tray('B',pull))]

def assembly(angle=0.0,pulls=(0.0,0.0),clasp_angle=None):
    ca=(90.0 if angle<180 else 0.0) if clasp_angle is None else clasp_angle
    return cq.Compound.makeCompound(leaf_a(pulls[0])+leaf_b(angle,pulls[1])+[clasp(ca)])


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
