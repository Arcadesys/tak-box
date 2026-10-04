"""Tak v17 compact folio, mm. Two 21-stone edge-on banks under one lid.

An independent roof retains the pieces; board B folds face inward onto A.
Four corner M3 screws pass through
both closed leaves into replaceable hex nuts in the storage shell.
No snap-fit is used for transport retention. Physical fit remains untested.
"""
from functools import lru_cache
from pathlib import Path
import cadquery as cq

P=36.; WX=196.; WY=202.; SEAM=98.; HG=.2
SHELL_H=23.; H=24.; FLOOR=2.; BOARD=3.; FACE=H+BOARD; LIP=1.; AXZ=FACE+LIP
FLAT=19.5; THICK=8.; LANE_W=20.2; LANE_L=56.7
LANES=[(x,y) for y in (10.,80.) for x in (8.,30.,52.)]
CAPS=[(75.0,y) for y in (10.,80.)]
SCREWS=[(x,y) for x in (4.,90.) for y in (5.,197.)]
KR=3.; PIN_R=1.5; PIN_CLR=.4
KNUCKLE_A=((4.7,9.),(WY-9.,WY-4.7))
KNUCKLE_B=((0.,4.3),(WY-4.3,WY))
ROOT=Path(__file__).resolve().parents[2]

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def cylinder(r,z0,z1,x,y):
    return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))

def cyly(r,y0,y1,x,z):
    return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))

def mirror(s): return s.mirror('YZ',(SEAM,0,0))
def fold(s,a): return s.rotate((SEAM,0,AXZ),(SEAM,1,AXZ),-a)

def nut(x,y,z0,z1):
    # M3 DIN934: nominal AF 5.5, thickness 2.4; trial AF 5.7.
    return cq.Workplane('XY',origin=(x,y,z0)).polygon(6,5.7/(3**.5/2)).extrude(z1-z0).val()

def grip_notch(x,y):
    return box(x+3.,x+17.2,y-2.1,y+.1,12.,H+.1)

@lru_cache(None)
def shell():
    s=box(0.,SEAM-HG,0.,WY,0.,SHELL_H).cut(box(2.,SEAM-HG-2.,2.,WY-2.,FLOOR,H+.1))
    for x,y in SCREWS:
        s=s.fuse(box(max(0.,x-4.),x+4.,y-5.,y+5.,FLOOR,SHELL_H))
        # Top-loaded nut, supported on a ledge; screw reaches below it.
        s=s.cut(nut(x,y,18.,H+.1)).cut(cylinder(1.7,15.,H+.1,x,y))
    for x,y in LANES:
        lane=box(x-1.2,x+LANE_W+1.2,y-2.,y+LANE_L+1.2,FLOOR,20.5)
        lane=lane.cut(box(x,x+LANE_W,y,y+LANE_L,FLOOR-.1,H+.1))
        s=s.fuse(lane.cut(grip_notch(x,y)))
    for x,y in CAPS:
        # Pawn lying on its side, envelope 19.4 x 25.4 x 19.4.
        wall=box(x-1.2,x+20.2+1.2,y-1.2,y+26.2+1.2,FLOOR,20.5)
        wall=wall.cut(box(x,x+20.2,y,y+26.2,FLOOR-.1,H+.1))
        s=s.fuse(wall)
    return s.clean()

def hinge(side):
    own,other=(KNUCKLE_A,KNUCKLE_B) if side=='A' else (KNUCKLE_B,KNUCKLE_A)
    p=box(0.,SEAM-HG,0.,WY,H,FACE)
    if side=='B': p=mirror(p)
    for y0,y1 in other: p=p.cut(cyly(KR+.4,y0-.4,y1+.4,SEAM,AXZ))
    for y0,y1 in own:
        xs=(SEAM-KR-.7,SEAM-HG) if side=='A' else (SEAM+HG,SEAM+KR+.7)
        p=p.fuse(cyly(KR,y0,y1,SEAM,AXZ)).fuse(box(*xs,y0,y1,H,AXZ))
    if side=='B':
        for mouth,d in ((4.3,1),(WY-4.3,-1)):
            end=mouth+d*2.5
            pin=cyly(PIN_R,min(mouth,end),max(mouth,end),SEAM,AXZ)
            cone=cq.Solid.makeCone(PIN_R,.3,1.2,cq.Vector(SEAM,end,AXZ),cq.Vector(0,d,0))
            p=p.fuse(pin).fuse(cone)
    else:
        for mouth,d in ((4.7,1),(WY-4.7,-1)):
            end=mouth+d*2.8
            hole=cyly(PIN_R+PIN_CLR,min(mouth-d*.05,end),max(mouth-d*.05,end),SEAM,AXZ)
            cone=cq.Solid.makeCone(PIN_R+PIN_CLR,.1,1.3,cq.Vector(SEAM,end,AXZ),cq.Vector(0,d,0))
            p=p.cut(hole.fuse(cone))
    return p

@lru_cache(None)
def grid(side):
    lines=[]
    for i in range(6):
        y=10.+P*i
        lines.append(box(8.-.4,SEAM-HG,y-.4,y+.4,FACE-.6,FACE))
    for i in range(3):
        x=8.+P*i
        lines.append(box(x-.4,x+.4,10.-.4,190.+.4,FACE-.6,FACE))
    s=lines[0]
    for q in lines[1:]: s=s.fuse(q)
    return s.clean() if side=='A' else mirror(s.clean())

@lru_cache(None)
def board(side):
    p=hinge(side)
    rim=box(0.,SEAM-HG,0.,WY,FACE,AXZ).cut(box(1.6,SEAM+.1,1.6,WY-1.6,FACE-.1,AXZ+.1))
    for ya,yb in ((-.1,9.4),(WY-9.4,WY+.1)):
        rim=rim.cut(box(SEAM-KR-.7,SEAM+.1,ya,yb,FACE-.1,AXZ+.1))
    if side=='B': rim=mirror(rim)
    p=p.fuse(rim).cut(grid(side))
    for x,y in SCREWS:
        xx=x if side=='A' else WX-x
        p=p.cut(cylinder(1.7,H-.1,AXZ+.1,xx,y))
    return p.clean()

@lru_cache(None)
def retaining_lid():
    # Printed upside down on its uninterrupted flat roof, tongues pointing up.
    p=box(0.,SEAM-HG,0.,WY,SHELL_H,H)
    for x,y in SCREWS: p=p.cut(cylinder(1.7,SHELL_H-.1,H+.1,x,y))
    for x,y in LANES:
        p=p.fuse(box(x+3.4,x+16.8,y-1.6,y-.4,12.4,SHELL_H+.01))
    for y in (30.,110.,180.):
        p=p.fuse(box(2.4,3.6,y,y+10.,SHELL_H-1.2,SHELL_H+.01))
        p=p.fuse(box(94.2,95.4,y+10.,y+20.,SHELL_H-1.2,SHELL_H+.01))
    return p.clean()

def pieces(size=FLAT):
    out=[]
    for x,y in LANES:
        for i in range(7):
            out.append(box(x+(LANE_W-size)/2,x+(LANE_W+size)/2,y+.35+i*THICK,y+.35+(i+1)*THICK,FLOOR,FLOOR+size))
    for x,y in CAPS:
        out.append(box(x+.4,x+19.8,y+.4,y+25.8,FLOOR,FLOOR+19.4))
    return out

def real_caps():
    out=[]
    for team,(x,y) in zip(('cat','witch'),CAPS):
        s=cq.importers.importStep(str(ROOT/'pieces'/f'{team}-capstone.step')).val()
        s=s.rotate((0,0,0),(1,0,0),-90)
        b=s.BoundingBox()
        s=s.translate((x+10.1-(b.xmin+b.xmax)/2,y+.4-b.ymin,FLOOR-b.zmin))
        out.append(s)
    return out

def pose(s):
    b=s.BoundingBox(); return s.translate((-b.xmin,-b.ymin,-b.zmin))

def fit_trial(clearance=.3):
    """Nut/screw/lid coupon; trial actual M3 screw and nut before full print."""
    b=box(0,18,0,18,0,8).cut(nut(9,9,3,8.1)).cut(cylinder(1.5+clearance,0,8.1,9,9))
    lids=[box(0,18,0,18,0,3).cut(cylinder(1.5+clearance,-.1,3.1,9,9)) for _ in range(2)]
    return [b,*lids]
