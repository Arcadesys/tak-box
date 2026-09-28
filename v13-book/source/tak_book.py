"""Tak v13 book: the board folds in half with its face inside; a removable
piece tray slides out from under each half.

Units: mm. Open, the book lies flat: leaf A at x 0..67.8, leaf B at
x 68.2..136, faces up at z=FACE. The fold axis runs along y at (x=68, z=FACE),
so closing rotates B 180 degrees onto A, face to face. Each leaf is a base
(floor, fore wall, seam wall, back wall), a glued face plate carrying half the
5 x 5 board, and a tray that slides out of the front end (y=0). Hinge knuckles
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
DETENT_Y=(122.0,123.0,124.0)
DETENT_H=.7
DETENT_Z=(6.0,14.0)
NOTCH_Y=(121.4,124.6)
NOTCH_D=.8
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
STUD=(10.0,2*FACE-10.0)                  # closed-pose x,z of the stud on B
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
    return s.rotate((SEAM,0,FACE),(SEAM,1,FACE),-angle)


# ================================================================== base
def _base_body():
    p=box(0,LEAF_X1,0,WY,0,PLATE_Z)
    p=cq.Workplane(obj=p).edges('|Z and <X').fillet(CORNER_R).val()
    p=cq.Workplane(obj=p).faces('<Z').edges().chamfer(.5).val()
    p=p.cut(box(FORE,LEAF_X1-SEAM_WALL,-.1,WY-BACK,FLOOR,PLATE_Z+.1))
    # Side detent on the fore wall: works with the tray either way up.
    a,b,c=DETENT_Y
    ramp=(cq.Workplane('XY',origin=(0,0,DETENT_Z[0]))
          .polyline([(FORE-.01,a),(FORE+DETENT_H,b),(FORE-.01,c)]).close()
          .extrude(DETENT_Z[1]-DETENT_Z[0]).val())
    return p.fuse(ramp).clean()

def _pin(face_y,d):
    end=face_y+d*2.5
    return cyly(PIN_R,min(face_y,end),max(face_y,end),SEAM,FACE).fuse(
        coney(PIN_R,.3,end,end+d*1.2,SEAM,FACE))

def _socket(mouth_y,d):
    end=mouth_y+d*2.8
    s=cyly(PIN_R+PIN_CLR,min(mouth_y-d*.05,end),max(mouth_y-d*.05,end),SEAM,FACE)
    return s.fuse(coney(PIN_R+PIN_CLR,.1,end,end+d*1.3,SEAM,FACE))

@lru_cache(None)
def base(side):
    assert side in 'AB'
    p=_base_body()
    if side=='A':
        x,z=PIVOT
        p=p.cut(cyly(M3_PILOT,WY-M3_DEPTH,WY+.1,x,z))
    else:
        p=mirror_b(p)
        ox,oz=2*SEAM-STUD[0],2*FACE-STUD[1]
        stud=cyly(STUD_R,WY-.01,WY+CLASP_GAP+CLASP_T+.5,ox,oz)
        stud=cq.Workplane(obj=stud).faces('>Y').edges().chamfer(.4).val()
        p=p.fuse(stud)
    own,other=(KNUCKLE_A,KNUCKLE_B) if side=='A' else (KNUCKLE_B,KNUCKLE_A)
    for y0,y1 in other:
        p=p.cut(cyly(RELIEF,y0-.4,y1+.4,SEAM,FACE))
    for y0,y1 in own:
        p=p.fuse(cyly(KR,y0,y1,SEAM,FACE))
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
        out.append(box(FX0-LINE_W/2,LEAF_X1,y-LINE_W/2,y+LINE_W/2,FACE-LINE_D,FACE))
    for i in range(3):
        x=FX0+P*i
        out.append(box(x-LINE_W/2,x+LINE_W/2,FY0-LINE_W/2,FY0+5*P+LINE_W/2,FACE-LINE_D,FACE))
    s=out[0]
    for o in out[1:]:s=s.fuse(o)
    return s.clean()

def _plate_body():
    p=box(0,LEAF_X1,0,WY,PLATE_Z,FACE)
    p=cq.Workplane(obj=p).edges('|Z and <X').fillet(CORNER_R).val()
    for y0,y1 in ((-.1,FY0+.3),(WY-FY0-.3,WY+.1)):
        p=p.cut(box(SEAM-RELIEF-.3,SEAM,y0,y1,PLATE_Z-.1,FACE+.1))
    return p.clean()

@lru_cache(None)
def plate(side):
    p=_plate_body().cut(_lines()).clean()
    return p if side=='A' else mirror_b(p)

@lru_cache(None)
def inlay(side):
    g=_lines().intersect(_plate_body()).clean()
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
    p=p.cut(box(x0-.1,x0+NOTCH_D,*NOTCH_Y,DETENT_Z[0]-.4,DETENT_Z[1]+.4))
    return p.clean()

def tray(side,pull=0.0,shift=0.0):
    t=tray_a().translate((shift,-pull,0))
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
    """11 two-high flat stacks and one capstone lying down, 3 across."""
    x0=DR_X[0]+DR_WALL+.15;y0=DR_FRONT+.5;z=DR_Z0+DR_FLOOR
    out=[]
    for k,(i,j) in enumerate((i,j) for j in range(4) for i in range(3)):
        x=x0+i*(FLAT+.35);y=y0+j*(FLAT+.6)
        out.append(box(x,x+FLAT,y,y+FLAT,z,z+STACK_H) if k<11 else
                   box(x,x+CAP[1],y,y+CAP[0],z,z+CAP[2]))
    out=[b.translate((0,-pull,0)) for b in out]
    return out if side=='A' else [mirror_b(b) for b in out]

def print_pose(shape,flip=False):
    if flip:shape=shape.rotate((0,0,0),(1,0,0),180)
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))
