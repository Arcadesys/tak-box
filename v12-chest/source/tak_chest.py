"""Tak v12 chest: the board lives inside a hinged box. Units: mm.

Open the lid and the 205 x 205 mm playing field is inside the base, flanked by
two tall bays. Each bay holds a lidded player tray: 21 flats on edge in one
lane and a capstone in a short lane. The tray lifts straight up out of its bay
and becomes that player's own piece tray. The closed box is protected by the
lid rim; the board is recessed below it and never touches the lid.

Base and lid are each printed as two halves that meet at x=82, a black grid
line, and are joined with hourglass keys. Hinge axis runs along x at the back.
"""
from pathlib import Path
from functools import lru_cache
import cadquery as cq

ROOT=Path(__file__).resolve().parent
S=205.0
SEAM_X=82.0

# ---- tray (local frame: x 0..TO, y 0..TL, z 0..TH; floor underside at z=0)
TW=2.4
TI=20.4
TO=TI+2*TW
TL=205.0
TH=25.6
TFLOOR=2.4
GROOVE_Z=(22.4,24.2)
GROOVE_D=1.0
LID_Z=(22.7,23.9)
LID_FITS={'A':.20,'B':.30,'C':.40}
RIB_FITS={'A':.10,'B':.20,'C':.30}
FIT='B'
FLATS_END_Y=174.4
DIVIDER=(174.4,175.6)
RIB_W=4.0
RIB_OUT=1.2

# ---- chest
BASE_H=29.0
FLOOR=2.4
BOARD_TOP=27.5
FW=5.0
BKW=5.0
DIV=4.0
BAYW=25.6
OUTW=4.0
X0=-(OUTW+BAYW+DIV)
X1=S-X0
Y0=-FW
Y1=S+BKW
LID_H=9.0
LID_SKIN=3.6
CORNER_R=4.0
BAY_Y=(-.5,S+.5)
BAY_X={'left':(-(DIV+BAYW),-DIV),'right':(S+DIV,S+DIV+BAYW)}
SLOT_HALF=2.3
SLOT_Y=(-2.0,S+2.0)
TRAY_CLEAR=(BAYW-TO)/2

# ---- hinge
Y_AX=Y1+4.0
Z_AX=BASE_H
HINGE_R=4.0
PIN_R=1.5
PIN_CLR=.4
KGAP=.4
PIN_LEN=2.5

MAGNET_D=6.2
MAGNET_DEPTH=2.2
MAGNET_X=(38.0,167.0)
KEY_Y_BASE=(40.0,102.5,165.0)
KEY_CLR=.25


def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()

def cylz(r,x,y,z0,z1):
    return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0),cq.Vector(0,0,1))

def cylx(r,x0,x1,y,z):
    return cq.Solid.makeCylinder(r,x1-x0,cq.Vector(x0,y,z),cq.Vector(1,0,0))

def conex(r0,r1,x0,x1,y,z):
    return cq.Solid.makeCone(r0,r1,abs(x1-x0),cq.Vector(x0,y,z),cq.Vector(1 if x1>x0 else -1,0,0))


# ====================================================================== tray
def _tray_body():
    p=box(0,TO,0,TL,0,TH)
    p=p.cut(box(TW,TO-TW,TW,TL-TW,TFLOOR,TH+.1))
    p=p.fuse(box(TW,TO-TW,DIVIDER[0],DIVIDER[1],TFLOOR,GROOVE_Z[0]-.2))
    # Sliding-lid grooves, open at the +y end, closed by the front wall.
    for x0,x1 in ((TW-GROOVE_D,TW+.01),(TO-TW-.01,TO-TW+GROOVE_D)):
        p=p.cut(box(x0,x1,TW,TL+.1,GROOVE_Z[0],GROOVE_Z[1]))
    # The lid also passes through the +y end wall.
    p=p.cut(box(TW-GROOVE_D,TO-TW+GROOVE_D,TL-TW-.01,TL+.1,GROOVE_Z[0],GROOVE_Z[1]))
    # Finger relief over the lid end.
    p=p.cut(box(8.0,TO-8.0,TL-2.4,TL+.1,GROOVE_Z[1],TH+.1))
    return p.clean()

def _tray_ribs(p,fit):
    cx=TO/2
    for y0,y1 in ((-RIB_OUT,.01),(TL-.01,TL+RIB_OUT)):
        p=p.fuse(box(cx-RIB_W/2,cx+RIB_W/2,y0,y1,1.0,21.0))
    push=TRAY_CLEAR+RIB_FITS[fit]
    for y in (50.0,155.0):
        for left in (True,False):
            x=0.0 if left else TO
            d=-1 if left else 1
            tri=(cq.Workplane('XY',origin=(0,0,4.0))
                 .polyline([(x-d*.01,y-.5),(x+d*push,y),(x-d*.01,y+.5)])
                 .close().extrude(16.0).val())
            p=p.fuse(tri)
    return p.clean()

@lru_cache(None)
def tray(fit=None):
    fit=FIT if fit is None else fit
    assert fit in RIB_FITS
    return _tray_ribs(_tray_body(),fit)

@lru_cache(None)
def tray_lid(fit=None):
    fit=FIT if fit is None else fit
    c=LID_FITS[fit]
    p=box(TW-GROOVE_D+c,TO-TW+GROOVE_D-c,TW+.2,TL,LID_Z[0],LID_Z[1])
    return p.clean()


# ============================================================== pieces (fit)
def flat_boxes(x0=0.0,z0=0.0):
    out=[]
    for i in range(21):
        y=4.4+8*i
        out.append(box(x0+TO/2-9.75,x0+TO/2+9.75,y,y+8,z0+TFLOOR,z0+TFLOOR+19.5))
    return out

def capstone_box(x0=0.0,z0=0.0,witch=True):
    w=17.29 if witch else 15.54
    cy=(DIVIDER[1]+TL-TW)/2
    return box(x0+TO/2-w/2,x0+TO/2+w/2,cy-12.5,cy+12.5,z0+TFLOOR,z0+TFLOOR+w)


# ====================================================================== base
def _outer(z0,z1):
    p=(cq.Workplane('XY').box(X1-X0,Y1-Y0,z1-z0,centered=False)
       .translate((X0,Y0,z0)).edges('|Z').fillet(CORNER_R))
    return p.val()

def _bevel(shape,top):
    wp=cq.Workplane(obj=shape)
    sel='>Z' if top else '<Z'
    return wp.faces(sel).edges().chamfer(1.0).val()

def _grid_bodies():
    out=[]
    for n in ('grid-a','grid-center','grid-b'):
        s=cq.importers.importStep(str(ROOT/'references'/(n+'.step'))).val().clean()
        out.append(s.translate((0,0,BOARD_TOP-4.8)))
    return out

def _hourglass(x,y,z0,z1,clr=0.0):
    hw_n,hw_w,ln=4.0+clr,7.0+clr,10.0+clr
    pts=[(x-ln,y-hw_w),(x,y-hw_n),(x+ln,y-hw_w),(x+ln,y+hw_w),(x,y+hw_n),(x-ln,y+hw_w)]
    return cq.Workplane('XY',origin=(0,0,z0)).polyline(pts).close().extrude(z1-z0).val()

def _magnet_pockets(p,z0,z1):
    for x in MAGNET_X:
        p=p.cut(cylz(MAGNET_D/2,x,-FW/2,z0,z1))
    return p

def _base_shell():
    p=_bevel(_outer(0,BASE_H),False)
    p=p.cut(box(0,S,0,S,BOARD_TOP,BASE_H+.1))
    for side,(bx0,bx1) in BAY_X.items():
        p=p.cut(box(bx0,bx1,BAY_Y[0],BAY_Y[1],FLOOR,BASE_H+.1))
        cx=(bx0+bx1)/2
        p=p.cut(box(cx-SLOT_HALF,cx+SLOT_HALF,SLOT_Y[0],BAY_Y[0]+.01,FLOOR,BASE_H+.1))
        p=p.cut(box(cx-SLOT_HALF,cx+SLOT_HALF,BAY_Y[1]-.01,SLOT_Y[1],FLOOR,BASE_H+.1))
    for g in _grid_bodies():
        p=p.cut(g)
    p=_magnet_pockets(p,BASE_H-MAGNET_DEPTH,BASE_H+.1)
    # Thumb scoop in the front wall, clear of the recessed board.
    p=p.cut(cq.Solid.makeSphere(6.5,cq.Vector(S/2,-7.5,BASE_H+1.5)))
    return p.clean()

def _knuckle_layout():
    left=[]
    n=5
    L=(SEAM_X-.2)-X0
    seg=(L-(n-1)*KGAP)/n
    x=X0
    for i in range(n):
        left.append((x,x+seg,'base' if i%2==0 else 'lid'));x+=seg+KGAP
    right=[]
    n=6
    R=X1-(SEAM_X+.2)
    seg=(R-(n-1)*KGAP)/n
    x=SEAM_X+.2
    for i in range(n):
        right.append((x,x+seg,'lid' if i%2==0 else 'base'));x+=seg+KGAP
    return left+right

KNUCKLES=_knuckle_layout()

def _profile(kind):
    """YZ profile of a knuckle: rounded barrel plus 45-degree root web."""
    if kind=='base':
        pts=[(Y1-1,BASE_H-9),(Y1+2,BASE_H-9),(Y1+8,BASE_H-3),(Y1+8,BASE_H),(Y1-1,BASE_H)]
    else:
        pts=[(Y1-1,BASE_H+9),(Y1+2,BASE_H+9),(Y1+8,BASE_H+3),(Y1+8,BASE_H),(Y1-1,BASE_H)]
    return pts

def _knuckle(x0,x1,kind):
    web=(cq.Workplane('YZ',origin=(x0,0,0)).polyline(_profile(kind)).close()
         .extrude(x1-x0).val())
    return web.fuse(cylx(HINGE_R,x0,x1,Y_AX,Z_AX))

def _male_pin(p,face,d):
    end=face+d*PIN_LEN
    return p.fuse(cylx(PIN_R,min(face,end),max(face,end),Y_AX,Z_AX)).fuse(
        conex(PIN_R,.3,end,end+d*1.2,Y_AX,Z_AX))

def _female_socket(p,mouth,d):
    end=mouth+d*(PIN_LEN+.3)
    p=p.cut(cylx(PIN_R+PIN_CLR,min(mouth-d*.05,end),max(mouth-d*.05,end),Y_AX,Z_AX))
    return p.cut(conex(PIN_R+PIN_CLR,.1,end,end+d*1.8,Y_AX,Z_AX))

def _hinge_on(p,owner,side):
    """Fuse this half's knuckles; pins on lid knuckles, sockets on base."""
    for i,(x0,x1,kind) in enumerate(KNUCKLES):
        if kind!=owner or ((x0+x1)/2<SEAM_X)!=(side=='left'):continue
        k=_knuckle(x0,x1,kind)
        if kind=='lid':
            # Pin into each adjacent base knuckle.
            for j,d in ((i-1,-1),(i+1,1)):
                if 0<=j<len(KNUCKLES):
                    face=x0 if d<0 else x1
                    k=_male_pin(k,face,d)
        else:
            for j,d in ((i-1,-1),(i+1,1)):
                if 0<=j<len(KNUCKLES):
                    mouth=x0 if d<0 else x1
                    k=_female_socket(k,mouth,-d)
        p=p.fuse(k)
    return p

def _half(shape,side):
    if side=='left':return shape.intersect(box(X0-1,SEAM_X,Y0-1,Y1+20,-1,80))
    return shape.intersect(box(SEAM_X,X1+1,Y0-1,Y1+20,-1,80))

@lru_cache(None)
def base_shell_full():
    return _base_shell()

def key_shapes():
    return [_hourglass(SEAM_X,y,0,18) for y in KEY_Y_BASE]

@lru_cache(None)
def base(side):
    assert side in ('left','right')
    p=_half(base_shell_full(),side)
    for y in KEY_Y_BASE:
        p=p.cut(_hourglass(SEAM_X,y,-.1,18.0,KEY_CLR))
    return _hinge_on(p,'base',side).clean()

@lru_cache(None)
def grid_inlay(index,side):
    assert side in ('left','right')
    g=_grid_bodies()[index]
    b=box(X0,SEAM_X,-1,300,0,60) if side=='left' else box(SEAM_X,X1,-1,300,0,60)
    return g.intersect(b).clean()


# ======================================================================= lid
def _lid_shell():
    p=_bevel(_outer(BASE_H,BASE_H+LID_H),True)
    p=p.cut(box(X0+OUTW,X1-OUTW,0,S,BASE_H-.1,BASE_H+LID_H-LID_SKIN))
    # Raised top panel with a chamfered edge, plus four corner studs.
    panel=(cq.Workplane('XY').box(X1-X0-40,Y1-Y0-30,.8,centered=False)
           .translate((X0+20,Y0+15,BASE_H+LID_H)).edges('>Z').chamfer(.6).val())
    p=p.fuse(panel)
    for x in (X0+11,X1-11):
        for y in (Y0+11,Y1-11):
            p=p.fuse(cq.Solid.makeCone(3.6,2.0,1.8,cq.Vector(x,y,BASE_H+LID_H-.1),cq.Vector(0,0,1)))
    p=_magnet_pockets(p,BASE_H-.1,BASE_H+MAGNET_DEPTH)
    return p.clean()

@lru_cache(None)
def lid_shell_full():
    return _lid_shell()

LID_KEY_Y=(30.0,102.5,175.0)

@lru_cache(None)
def lid(side):
    assert side in ('left','right')
    p=_half(lid_shell_full(),side)
    # Thin butt-strap keys sit in pockets in the underside of the top skin.
    for y in LID_KEY_Y:
        p=p.cut(_hourglass(SEAM_X,y,BASE_H+LID_H-LID_SKIN-.1,BASE_H+LID_H-1.8,KEY_CLR))
    return _hinge_on(p,'lid',side).clean()

def lid_key_shapes():
    return [_hourglass(SEAM_X,y,BASE_H+LID_H-LID_SKIN,BASE_H+LID_H-1.8) for y in LID_KEY_Y]


# ================================================================== assembly
def tray_pose(side,lift=0.0,fit=None):
    x=BAY_X[side][0]+TRAY_CLEAR
    return tray(fit).translate((x,0,FLOOR+lift)),tray_lid(fit).translate((x,0,FLOOR+lift)),x

def lid_posed(shape,angle):
    """Open the lid about the back hinge; positive angle raises the front."""
    return shape.rotate((0,Y_AX,Z_AX),(1,Y_AX,Z_AX),-angle)

def assembly(angle=0.0,lift=(0.0,0.0),with_pieces=False,with_lids=True):
    parts=[base('left'),base('right')]
    for i in range(3):
        parts.append(grid_inlay(i,'left'));parts.append(grid_inlay(i,'right'))
    for side,l in zip(('left','right'),lift):
        t,tl,x=tray_pose(side,l)
        parts.append(t)
        if with_lids:parts.append(tl)
        if with_pieces:
            for f in flat_boxes(x,FLOOR+l):parts.append(f)
            parts.append(capstone_box(x,FLOOR+l,side=='right'))
    for s in ('left','right'):
        parts.append(lid_posed(lid(s),angle))
    return cq.Compound.makeCompound(parts)

def print_pose(shape,flip=False):
    if flip:
        b=shape.BoundingBox()
        shape=shape.rotate((0,0,0),(1,0,0),180)
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))
