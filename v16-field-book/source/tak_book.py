"""Tak v16 field book: the board folds in half with its face inside; a
snap-in piece tray slides out from under each half. No hardware.

Units: mm. Open, the book lies flat: leaf A at x 0..SEAM-HG, leaf B at
x SEAM+HG..WX, faces up at z=FACE. The grid is inlaid flush with the face in
a second colour. The fold axis runs along y at (x=68, z=AXZ), the top of the
lines, so closing rotates B 180 degrees onto A and the lips meet.

Each leaf is a base (2 mm floor skin, fore wall, seam wall, 10 mm back wall,
two cross ribs behind the tray), a
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
import math
import cadquery as cq
import decor as dc

# ---- board
P=36.0                      # cell pitch; 19.5 mm flats leave 16.5 mm between neighbours, room for a fingertip either side of a stack
FX0,FY0=8.0,10.0            # fore-edge and front-edge margins to the first grid line
WX=2*FX0+5*P
WY=FY0+5*P+12.0             # 12 mm at the back: the back wall and lip
SEAM=WX/2
HG=.2
LINE_W=.8
LINE_D=.6
LINE_CLR=0.0                # 0: grid is fused in a multi-colour print

# ---- heights
FLOOR=2.0
DR_Z0=FLOOR+.2
DR_FLOOR=1.0
DR_INNER=19.0               # room for the 19.4 mm pawn lying in its dish (0.4 mm below the floor)
DR_TOP=DR_Z0+DR_FLOOR+DR_INNER      # 22.2
CRADLE_D=.4                 # capstone cradle depth in the tray floor
CRADLE_R=10.1               # cradle radius: the pawn's 9.7 mm plus 0.4 mm
PLATE_Z=DR_TOP+.4                   # 21.2
PLATE=2.0
FACE=PLATE_Z+PLATE                  # 23.2
LINE_RAISE=0.0                      # grid is flush with the face (inlaid)
LIP=1.0                             # outer lip above the face; protects painted surfaces
LIP_W=1.6
AXZ=FACE+LIP                        # fold axis at the top of the lips, which meet when closed

# ---- leaf A walls and tray
LEAF_X1=SEAM-HG
FORE=3.0
SEAM_WALL=2.2
BACK=10.0
CLR=.3
DR_WALL=1.2
DR_FRONT=2.0
DR_X=(FORE+CLR,LEAF_X1-SEAM_WALL-CLR)
TRAY_LEN=132.0              # the tray needs only the pieces' length; the cavity behind it stays empty
DR_Y1=TRAY_LEN
# Cross ribs in the empty chamber behind the tray, floor to plate seat: they tie
# the floor skin to the plate and cut its 92 mm span into ~20 mm bays. Clear of
# the tray (ends at 132) and of leaf B's buckle panel (starts at y=175).
RIB_T=1.2
RIB_Y=(152.0,170.0)         # rib centre lines
# The bulkhead closes the box section at the tray's end (fore wall to seam wall,
# floor to plate seat), and a spine rib ties it to the cross ribs. Base only: the
# trays, plates, pegs and glue wells are printed and do not change.
BULK_Y=DR_Y1+2.2            # bulkhead centre line: 1.6 mm behind the tray's end
SPINE_W=1.2
SPINE_Y=(BULK_Y,170.0)

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
TAB_X=(WX-5.8,WX-3.4)
TAB_Y=(WY-7.5,WY-3.1)
TAB_TIP=13.2
TAB_NOTCH_X=1.0             # catch engagement depth
TAB_NOTCH_Z=(15.1,17.5)
SLOT_CLR=.3
SLOT_ARC=1.2
TOOTH_X=(WX-27.2,TAB_X[0]+TAB_NOTCH_X-.2)
TOOTH_Z=(15.3,17.3)
RING_X=(WX-8.6,WX-1.7)
RING_Y=(WY-8.5,WY-2.1)
RING_BAR=.7
RING_Z=(14.8,17.8)
PANEL_X=(WX-1.8,WX+.2)
PANEL_Y=(WY-27.0,WY-1.8)    # root 27 mm from the back, free end at the back corner
PANEL_Z=(9.3,19.3)
PANEL_SLIT=.8                # wide enough that the 25 mm bridge over it can't fuse
RING_DROP=2.5                # open space under the catch ring so its first layer can sag freely
PRESS=1.4                   # panel travel that frees the catch

# ---- plate-to-base registration for gluing. The plate sits plastic on plastic
# on the wall tops; glue lives in shallow wells in its underside, so the glue
# can't lift the lips. Two pegs on each base's wall tops locate the plate: a
# round one on the back wall (x and y) and a small one on the fore wall near the
# front, in a slot along y (rotation). The pegs print upward with the base; the
# sockets open onto the plate's bed face. Leaf A frame throughout.
FIT=.3                      # plate notch clearance around the knuckle blocks
PEG_H=1.4                   # socket leaves 0.4 mm (two layers) of plate over it
PEG_CLR=.15                 # radial / per-side socket clearance
SOCKET_D=PEG_H+.2
PEG_BACK=(16.0,WY-BACK/2,1.5)       # x, y, radius: clear of leaf B's buckle
PEG_FORE=(FORE/2,24.0,1.0)          # on the 3 mm fore wall
PEG_SLOT=3.0                        # extra socket length along y at the fore peg
WELL_D=.4
WELL_W=1.2
_SW=SEAM-HG-SEAM_WALL/2      # seam wall centre line
WELLS=[(.9,2.1,y,y+20) for y in (34,72,110,148)]+\
      [(_SW-.45,_SW+.45,y,y+20) for y in (20,63,106,149)]+\
      [(x,x+18,WY-5.6,WY-4.4) for x in (22,44,66)]   # fore wall, seam wall, back wall

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
    for y in RIB_Y:
        p=p.fuse(box(FORE-.01,LEAF_X1-SEAM_WALL+.01,y-RIB_T/2,y+RIB_T/2,FLOOR-.01,PLATE_Z))
    p=p.fuse(box(FORE-.01,LEAF_X1-SEAM_WALL+.01,BULK_Y-RIB_T/2,BULK_Y+RIB_T/2,FLOOR-.01,PLATE_Z))
    xm=(FORE+LEAF_X1-SEAM_WALL)/2
    p=p.fuse(box(xm-SPINE_W/2,xm+SPINE_W/2,SPINE_Y[0],SPINE_Y[1],FLOOR-.01,PLATE_Z))
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
    p=_base_body().fuse(pegs())
    if side=='B':
        p=mirror_b(p)
        p=_buckle_socket(p)
    own,other=(KNUCKLE_A,KNUCKLE_B) if side=='A' else (KNUCKLE_B,KNUCKLE_A)
    for y0,y1 in other:
        p=p.cut(cyly(RELIEF,y0-.4,y1+.4,SEAM,AXZ))
    for y0,y1 in own:
        p=p.fuse(cyly(KR,y0,y1,SEAM,AXZ))
        # Root the knuckle down into the base. The block stays on this leaf's
        # side below the axis, a quadrant the other leaf never sweeps through.
        xs=(SEAM-RELIEF-.3,LEAF_X1) if side=='A' else (SEAM+HG,SEAM+RELIEF+.3)
        p=p.fuse(box(*xs,y0,y1,PLATE_Z-.2,AXZ))
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

def _notches(side):
    """Plate cut-outs around the knuckles, in leaf A's frame."""
    return ((-.1,FY0+.3),(WY-FY0-.3,WY+.1))

def _plate_body(side,top=FACE):
    p=box(0,LEAF_X1,0,WY,PLATE_Z,top)
    p=cq.Workplane(obj=p).edges('|Z and <X').fillet(CORNER_R).val()
    for y0,y1 in _notches(side):
        p=p.cut(box(SEAM-RELIEF-.3-FIT,SEAM,y0,y1,PLATE_Z-.1,top+.1))
    return p.clean()

def pegs():
    """Locating pegs on the base wall tops, chamfered tips (leaf A frame)."""
    out=[]
    for x,y,r in (PEG_BACK,PEG_FORE):
        pg=cq.Solid.makeCylinder(r,PEG_H+.01,cq.Vector(x,y,PLATE_Z-.01),cq.Vector(0,0,1))
        out.append(cq.Workplane(obj=pg).faces('>Z').edges().chamfer(min(.3,r/3)).val())
    return out[0].fuse(out[1])

def sockets():
    """Plate-underside sockets for the pegs: round at the back, a y-slot at the fore."""
    z0,z1=PLATE_Z-.1,PLATE_Z+SOCKET_D
    x,y,r=PEG_BACK
    back=cq.Solid.makeCylinder(r+PEG_CLR,z1-z0,cq.Vector(x,y,z0),cq.Vector(0,0,1))
    x,y,r=PEG_FORE;w=r+PEG_CLR;h=PEG_SLOT/2
    fore=box(x-w,x+w,y-h,y+h,z0,z1)
    for yy in (y-h,y+h):
        fore=fore.fuse(cq.Solid.makeCylinder(w,z1-z0,cq.Vector(x,yy,z0),cq.Vector(0,0,1)))
    return back.fuse(fore).clean()

def glue_wells():
    """Shallow wells in the plate underside, over the wall tops (leaf A frame)."""
    s=[box(x0,x1,y0,y1,PLATE_Z-.1,PLATE_Z+WELL_D) for x0,x1,y0,y1 in WELLS]
    return dc.union(s)

def _lip():
    """Raised rim on leaf A's fore, front and back edges (not across the fold)."""
    outer=box(0,LEAF_X1,0,WY,FACE-.01,FACE+LIP)
    outer=cq.Workplane(obj=outer).edges('|Z and <X').fillet(CORNER_R).val()
    inner=box(LIP_W,LEAF_X1+.1,LIP_W,WY-LIP_W,FACE-.1,FACE+LIP+.1)
    inner=cq.Workplane(obj=inner).edges('|Z and <X').fillet(CORNER_R-LIP_W).val()
    lip=outer.cut(inner)
    for y0,y1 in ((-.1,FY0+.3),(WY-FY0-.3,WY+.1)):
        lip=lip.cut(box(SEAM-RELIEF-.3-FIT,SEAM,y0,y1,FACE-.2,FACE+LIP+.1))
    return lip.clean()

# ============================================================ decoration
def _cell(pts):
    """Art was laid out on a 24 mm, 136 mm-wide board; keep each motif in the same
    place relative to its cell. Leaf B positions are measured from the far edge."""
    k=P/24.0
    out=[]
    for x,y,*rest in pts:
        nx=FX0+(x-8.0)*k if x<68 else WX-FX0-(128.0-x)*k
        out.append((nx,FY0+(y-10.0)*k,*rest))
    return out

STARS={'A':[(13.5,15.2),(27.1,40.3),(38.6,54.8),(49.9,31.4),(15.8,64.7),(29.3,109.9),
            (45.2,121.8),(62.8,99.3),(40.8,77.6),(21.9,124.9)],
       'B':[(74.2,19.5),(90.6,49.2),(115.3,28.7),(98.4,68.9),(121.9,77.3),(84.7,95.8),
            (110.6,112.4),(73.9,121.6),(119.6,54.1),(94.4,38.1)]}
GALAXIES={'A':[(18.5,88.5,'purple',.6),(61.5,24.0,'orange',2.2)],
          'B':[(86.0,113.5,'orange',1.3),(116.5,44.5,'purple',3.9)]}
# One of each small symbol per leaf, in cells the galaxies leave empty; each
# leaf gets two orange and two purple.  (kind, x, y, colour, angle)
SYMBOLS={'A':[('planet',44.0,94.0,'orange',-.4),('crescent',42.0,19.0,'purple',2.4),
              ('sparkle',60.0,70.0,'purple',.3),('comet',22.0,49.0,'orange',-.6)],
         'B':[('crescent',116.0,94.0,'orange',.7),('planet',89.0,74.0,'purple',.35),
              ('sparkle',90.0,22.0,'orange',.1),('comet',119.0,121.0,'purple',-2.5)]}
# A few star dots take an accent colour, a little larger so they read on black.
COLOUR_STARS={'A':{(38.6,54.8):'orange',(13.5,15.2):'purple',(62.8,99.3):'purple'},
              'B':{(115.3,28.7):'orange',(84.7,95.8):'orange',(73.9,121.6):'purple'}}
COLOUR_STAR_R=.6
for _s in 'AB':
    SYMBOLS[_s]=[(k,*_cell([(x,y)])[0],c,a) for k,x,y,c,a in SYMBOLS[_s]]
    COLOUR_STARS[_s]={_cell([xy])[0]:c for xy,c in COLOUR_STARS[_s].items()}
for _d in (STARS,GALAXIES):
    for _s in 'AB':_d[_s]=_cell(_d[_s])

def _symbol(kind,x,y,ang,z0,z1):
    if kind=='planet':return dc.planet(x,y,z0,z1,tilt=ang)
    if kind=='crescent':return dc.crescent(x,y,2.5,ang,z0,z1)
    if kind=='sparkle':return dc.poly(dc.sparkle(x,y,2.6,ang),z0,z1)
    if kind=='comet':return dc.comet(x,y,ang,z0,z1)
    raise ValueError(kind)

@lru_cache(None)
def decor(side,colour):
    """Flush inlay solid of one accent colour on one leaf (world/open frame)."""
    z0,z1=FACE-dc.DEPTH,FACE
    parts=[]
    for x,y,c,rot in GALAXIES[side]:
        if c!=colour:continue
        arms,(cx,cy,r)=dc.galaxy(x,y,rot=rot)
        parts+= [dc.stroke(a,z0,z1,.7) for a in arms]+[dc.dot(cx,cy,r,z0,z1)]
    parts+=[_symbol(k,x,y,a,z0,z1) for k,x,y,c,a in SYMBOLS[side] if c==colour]
    parts+=[dc.dot(x,y,COLOUR_STAR_R,z0,z1) for (x,y),c in COLOUR_STARS[side].items() if c==colour]
    return dc.union(parts) if parts else None

@lru_cache(None)
def stars(side):
    z0,z1=FACE-dc.DEPTH,FACE
    return dc.union([dc.dot(x,y,dc.STAR_R,z0,z1) for x,y in STARS[side]
                     if (x,y) not in COLOUR_STARS[side]])

@lru_cache(None)
def plate(side):
    body=_plate_body(side).fuse(_lip()).cut(glue_wells()).cut(sockets())
    p=body if side=='A' else mirror_b(body)
    p=p.cut(_lines(LINE_CLR) if side=='A' else mirror_b(_lines(LINE_CLR)))
    for c in ('orange','purple'):
        if decor(side,c) is not None:p=p.cut(decor(side,c))
    p=p.cut(stars(side))
    return _plate_finish(p,side)

def _plate_finish(p,side):
    """Thumb groove, and the buckle tab (A) or slot (B), in the open frame."""
    # Thumb groove: the fore edges of the two lips form a V when closed.
    top=FACE+LIP
    groove=(cq.Workplane('XZ').polyline([(-.1,top+.1),(THUMB,top+.1),(-.1,top-THUMB)])
            .close().extrude(-(WY+.2)).translate((0,-.1,0)).val())
    if side=='A':
        return p.cut(groove).fuse(tab()).clean()
    return p.cut(mirror_b(groove)).cut(_slot()).clean()

@lru_cache(None)
def inlay(side):
    """White parts: the inlaid grid plus the star dots."""
    g=_lines().intersect(_plate_body(side,FACE+LINE_RAISE)).clean()
    g=g if side=='A' else mirror_b(g)
    return g.fuse(stars(side)).clean()


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
    p=p.cut(_cradle())
    # Free the latch arm: slots above, below and at its front end.
    xs=(x0-.1,x0+DR_WALL+.1)
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[1],ARM_Z[0]-ARM_SLOT,ARM_Z[0]))
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[1],ARM_Z[1],ARM_Z[1]+ARM_SLOT))
    p=p.cut(box(*xs,ARM_Y[0]-ARM_SLOT,ARM_Y[0],ARM_Z[0]-.1,ARM_Z[1]+.1))
    return p.fuse(_button()).clean()

def cap_slot():
    """Where the capstone lies: centre x, front y, back y. Beside the latch arm."""
    x0=DR_X[0]+DR_WALL+.15
    y0=DR_FRONT+.5
    return x0+FLAT-CAP[1]/2+CAP_DX,y0,y0+CAP[0]

def _cradle():
    """A shallow trough in the tray floor that keeps the pawn from rolling: a
    cylinder of radius CRADLE_R whose bottom is CRADLE_D below the floor top."""
    x,ya,yb=cap_slot()
    zc=DR_Z0+DR_FLOOR-CRADLE_D+CRADLE_R
    return cq.Solid.makeCylinder(CRADLE_R,yb-ya+1.0,cq.Vector(x,ya-.5,zc),cq.Vector(0,1,0))

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

TRAY_MOON=(DR_X[0]+.53*(DR_X[1]-DR_X[0]),.65*DR_Y1,4.2)   # crescent on tray A's floor: x, y, radius

@lru_cache(None)
def _tray_art_a():
    """Tray A floor art: (player-colour crescent moon, white sparkles).

    Both sit in the floor's top three layers, so colour swaps stay few and
    the orange/purple filament use is about a gram.
    """
    x0,x1=DR_X
    fz=DR_Z0+DR_FLOOR
    z0,z1=fz-dc.DEPTH,fz
    fx0,fx1=x0+DR_WALL+1.2,x1-DR_WALL-1.2
    fy0,fy1=DR_FRONT+1.2,DR_Y1-DR_WALL-1.2
    mx,my,mr=TRAY_MOON
    moon=dc.crescent(mx,my,mr,math.pi*.25,z0,z1)
    keep=[(mx+mr*math.cos(a),my+mr*math.sin(a)) for a in [i*math.pi/8 for i in range(16)]]+[(mx,my)]
    cxx,cya,cyb=cap_slot()
    keep+=[(cxx,cya-2+i*3.0) for i in range(int((cyb-cya)/3)+3)]    # keep sparkles out of the cradle
    white=dc.sparkles_in_gaps(fy0,fy1,fx0,fx1,lambda u,v:(v,u),keep,z0,z1,R=2.1,clear=2.5,every=19.0,seed=7,jitter=5.0)
    return moon,white

@lru_cache(None)
def _tray_swirl_a():
    return _tray_art_a()[0]

@lru_cache(None)
def tray_body(side):
    acc,white=_tray_art_a()
    t=tray_a().cut(acc).cut(white).clean()
    return t if side=='A' else mirror_b(t)

@lru_cache(None)
def tray_sparkles(side):
    w=_tray_art_a()[1]
    return w if side=='A' else mirror_b(w)

@lru_cache(None)
def tray_swirl(side):
    s=_tray_swirl_a()
    return s if side=='A' else mirror_b(s)


# ============================================================= assemblies
def leaf_a(pull=0.0):
    return [base('A'),plate('A'),inlay('A'),tray('A',pull)]

def leaf_b(angle=0.0,pull=0.0):
    return [fold(p,angle) for p in (base('B'),plate('B'),inlay('B'),tray('B',pull))]

def assembly(angle=0.0,pulls=(0.0,0.0)):
    return cq.Compound.makeCompound(leaf_a(pulls[0])+leaf_b(angle,pulls[1]))


# ========================================================= piece envelopes
FLAT=20.0                   # real flats are 20 x 20 x 8 (pieces/tak_pieces.py)
STACK_H=16.0
CAP_DX=2.0                  # capstone sits this far in from the latch-arm wall so the pressed arm clears it
CAP=(25.4,19.4,19.4)        # the pawn capstone lying on its side: length, width, height

def piece_boxes(side='A',pull=0.0):
    """11 two-high flat stacks and the capstone, standing in 3 columns, spread
    evenly so there is a fingertip of air between neighbours. The narrower
    capstone sits by the latch arm, leaving it room to flex."""
    x0=DR_X[0]+DR_WALL+.15;x1=DR_X[1]-DR_WALL-.15
    y0=DR_FRONT+.5;y1=DR_Y1-DR_WALL-.5
    z=DR_Z0+DR_FLOOR
    colx=[x0+i*(x1-x0-FLAT)/2 for i in range(3)]
    cx=x0+FLAT-CAP[1]+CAP_DX
    out=[box(cx,cx+CAP[1],y0,y0+CAP[0],z-CRADLE_D,z-CRADLE_D+CAP[2])]
    g=(y1-y0-CAP[0]-3*FLAT)/3
    for j in range(3):
        y=y0+CAP[0]+g+j*(FLAT+g)
        out.append(box(colx[0],colx[0]+FLAT,y,y+FLAT,z,z+STACK_H))
    g=(y1-y0-4*FLAT)/3
    for i in (1,2):
        for j in range(4):
            y=y0+j*(FLAT+g)
            out.append(box(colx[i],colx[i]+FLAT,y,y+FLAT,z,z+STACK_H))
    out=[b.translate((0,-pull,0)) for b in out]
    return out if side=='A' else [mirror_b(b) for b in out]

# ============================================================ tray insert
# Added after the trays were printed, so it does not touch the tray: a separate
# part that drops onto the tray floor. The flats lie flat in a single layer
# (4 across, 5 deep), so the insert is four lanes 20.0 mm wide and 5 flats long
# behind a pawn saddle, with one more pocket beside the pawn for the 21st flat.
# A flat drops in anywhere along its lane and slides up to the last one.
# FLAT above stays 20.0 because the tray's cradle position is derived from it.
FLAT_PRINTED=19.5           # the printed flats are 0.5 mm under the real 20 mm
FLAT_T=8.0                  # flat thickness
LANE=20.0                   # lane inside width: 0.25 mm each side of a printed flat
LANES=4
LANE_FLATS=5
LANE_SLACK=.5               # end play along a full lane
OUT_W=1.2                   # outer lane walls (three perimeters)
DIV_W=1.6                   # shared dividers between lanes
RAIL_H=3.5                  # lane walls: under half a flat, so a flat is easy to pinch out
RAIL_FLARE=.4               # lead-in chamfer on the inner top edges
INS_CLR=.15                 # gap to the tray walls, so it drops in
INS_WALL=.8                 # end walls and saddle
INS_FLOOR=.8                # floor under the lanes and the 21st-flat pocket, so the insert lifts out with its flats
TAB_W=30.0                  # lift tab at the back: a plate with a finger hole
TAB_T=1.6
TAB_H=16.0
TAB_HOLE_R=4.0
STOP_H=9.0                  # end stop that keeps the pawn from sliding out of its cradle
STOP_GAP=.4                 # from the pawn's end to the stop
SADDLE_GAP=.35              # each side of the pawn's widest point
SADDLE_H=6.0                # saddle wall height, hugging the pawn's lower body
SADDLE_L_Y0=16.0            # left wall starts here: the pressed latch arm swings out to x=6.5 at the front

def _ins_layout():
    """Everything the checks need, in tray A: lane boxes (x0,x1,y0,y1) inside the walls,
    the 21st-flat pocket inside box, the pawn stop and the saddle wall x positions."""
    bx0=DR_X[0]+DR_WALL+INS_CLR;bx1=DR_X[1]-DR_WALL-INS_CLR
    total=LANES*LANE+2*OUT_W+(LANES-1)*DIV_W
    x=bx0+(bx1-bx0-total)/2+OUT_W
    cx,ya,yb=cap_slot()
    stop=(cx-CAP[1]/2,cx+CAP[1]/2,yb+STOP_GAP,yb+STOP_GAP+INS_WALL)
    ly0=stop[3];ly1=ly0+LANE_FLATS*FLAT_PRINTED+LANE_SLACK
    lanes=[]
    for i in range(LANES):
        lanes.append((x,x+LANE,ly0,ly1));x+=LANE+DIV_W
    xr=stop[1]+SADDLE_GAP+INS_WALL
    sy0=DR_FRONT+INS_CLR
    pocket=(xr,xr+LANE,sy0+INS_WALL,sy0+INS_WALL+LANE)
    return lanes,pocket,stop

@lru_cache(None)
def tray_insert_a():
    z0=DR_Z0+DR_FLOOR
    lanes,pocket,stop=_ins_layout()
    def wall(xa,xb,y0,y1,h=RAIL_H,fl=RAIL_FLARE,left=True,right=True):
        """A wall from x=xa to xb along y, with a lead-in chamfer on the chosen top edges."""
        fa=fl if left else 0;fb=fl if right else 0
        pts=[(xa,z0),(xb,z0),(xb,z0+h-fb),(xb-fb,z0+h),(xa+fa,z0+h),(xa,z0+h-fa)]
        pts=[q for i,q in enumerate(pts) if q!=pts[i-1]]      # no flare on a side: drop the repeated corner
        return cq.Workplane('XZ',origin=(0,y0,0)).polyline(pts).close().extrude(-(y1-y0)).val()
    ins=[]
    ly0,ly1=lanes[0][2],lanes[0][3]
    yb=ly1+INS_WALL
    # lane walls: outer walls flared inward only, dividers flared both sides
    ins.append(wall(lanes[0][0]-OUT_W,lanes[0][0],stop[2],yb,left=False))
    for a,b in zip(lanes,lanes[1:]):
        ins.append(wall(a[1],b[0],stop[2],yb))
    ins.append(wall(lanes[-1][1],lanes[-1][1]+OUT_W,stop[2],yb,right=False))
    xl0=lanes[0][0]-OUT_W;xl1=lanes[-1][1]+OUT_W
    ins.append(box(xl0,xl1,stop[2],stop[3],z0,z0+RAIL_H))      # front bar across the lanes
    ins.append(box(xl0,xl1,ly1,yb,z0,z0+RAIL_H))               # back bar
    # pawn saddle: stop wall behind it, and side walls hugging its body
    sy0=DR_FRONT+INS_CLR
    xl=stop[0]-SADDLE_GAP;xr=stop[1]+SADDLE_GAP
    ins.append(box(min(stop[0],xl-INS_WALL),xr+INS_WALL,stop[2],stop[3],z0,z0+STOP_H))
    ins.append(wall(xl-INS_WALL,xl,SADDLE_L_Y0,stop[3],SADDLE_H,.4,left=False))
    ins.append(wall(xr,xr+INS_WALL,sy0,stop[3],SADDLE_H,.4,right=False))
    # pocket for the 21st flat, sharing the saddle's right wall
    px0,px1,py0,py1=pocket
    ins.append(wall(px1,px1+INS_WALL,sy0,py1+INS_WALL,left=True,right=False))
    ins.append(box(xr,px1+INS_WALL,sy0,sy0+INS_WALL,z0,z0+RAIL_H))
    ins.append(box(xr,px1+INS_WALL,py1,py1+INS_WALL,z0,z0+RAIL_H))
    # Floor under the lanes and the pocket. None under the pawn: it has only
    # about 0.1 mm of headroom under the plate, so it stays in the tray's groove.
    ins.append(box(xl0,xl1,stop[2],yb,z0,z0+INS_FLOOR))
    ins.append(box(xr,px1+INS_WALL,sy0,py1+INS_WALL,z0,z0+INS_FLOOR))
    # Lift tab behind the lanes, with a teardrop finger hole (prints without support).
    tx=(xl0+xl1)/2
    tab=box(tx-TAB_W/2,tx+TAB_W/2,yb-.01,yb+TAB_T,z0,z0+TAB_H)
    hz=z0+TAB_H*.5
    hole=cq.Solid.makeCylinder(TAB_HOLE_R,TAB_T+1,cq.Vector(tx,yb-.5,hz),cq.Vector(0,1,0))
    tri=(cq.Workplane('XZ',origin=(0,yb-.5,0))
         .polyline([(tx-TAB_HOLE_R*.7071,hz+TAB_HOLE_R*.7071),(tx,hz+TAB_HOLE_R*1.4142),(tx+TAB_HOLE_R*.7071,hz+TAB_HOLE_R*.7071)])
         .close().extrude(-(TAB_T+1)).val())
    ins.append(tab.cut(hole).cut(tri))
    r=ins[0]
    for x in ins[1:]:r=r.fuse(x)
    return r.clean()

def tray_insert(side):
    t=tray_insert_a()
    return t if side=='A' else mirror_b(t)

def print_pose(shape,flip=False):
    if flip:shape=shape.rotate((0,0,0),(1,0,0),180)
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))
