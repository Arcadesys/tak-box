"""Filament-pin fit coupon parts: bore ladders, three-knuckle hinge strips and cap plugs.

The pin is a piece of 1.75 mm filament (never printed). Rule under test: the pin is
held snugly by the fixed part's knuckles and turns freely in the other part's, and a
small press-in plug seats in a counterbore at each end.
"""
import math
import cadquery as cq

# ---- bore ladders: one block, ten horizontal bores, smallest at the notched corner
LADDER=(1.70,1.75,1.80,1.85,1.90,1.95,2.00,2.10,2.20,2.30)
LAD_L,LAD_W,LAD_H,LAD_PITCH=22.0,61.0,8.0,6.0

def ladder(teardrop=False):
    blk=cq.Workplane('XY').box(LAD_L,LAD_W,LAD_H,centered=False).val()
    for i,d in enumerate(LADDER):
        y=3.5+i*LAD_PITCH; z=LAD_H/2; r=d/2
        prof=cq.Workplane('YZ').center(y,z).circle(r)
        if teardrop:                       # point at the top so a horizontal hole prints round at the sides
            k=r/math.sqrt(2)
            prof=prof.polyline([(-k,k),(0,r*math.sqrt(2)),(k,k)]).close()
        bore=prof.extrude(LAD_L+0.2).translate((-0.1,0,0)).val()
        blk=blk.cut(bore)
        # 45 degree lead-in on the entry face
        blk=blk.cut(cq.Solid.makeCone(r+0.6,r,0.6,cq.Vector(0,y,z),cq.Vector(1,0,0)))
    return blk.cut(cq.Workplane('XY').box(3,3,LAD_H+1,centered=False).translate((-0.5,-0.5,-0.5)).val())  # notch: small end

# ---- three-knuckle hinge strips (A fixed / B free / A fixed), real 19 mm knuckles
R,T,AXZ,EDGE,L,GAP,DEPTH=2.5,3.0,2.5,2.9,19.0,0.4,12.0
W=3*L+2*GAP
CB_R,CB_D=1.6,1.5            # counterbore for the end plug (Ø3.2 x 1.5)

def _box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()

def _cyl(r,x0,x1): return cq.Solid.makeCylinder(r,x1-x0,cq.Vector(x0,0,AXZ),cq.Vector(1,0,0))
def _cone(r0,r1,x0,d): return cq.Solid.makeCone(r0,r1,abs(r0-r1),cq.Vector(x0,0,AXZ),cq.Vector(d,0,0))

def strip(d_fixed,d_free,dimples=0):
    A=_box(0,W,-EDGE-DEPTH,-EDGE,0,T); B=_box(0,W,EDGE,EDGE+DEPTH,0,T)
    kn=[(k*(L+GAP),k*(L+GAP)+L) for k in range(3)]
    for k,(x0,x1) in enumerate(kn):
        knuckle=_cyl(R,x0,x1).fuse(_box(x0,x1,-EDGE if k%2==0 else 0,0 if k%2==0 else EDGE,0,T))
        knuckle=knuckle.fuse(_box(x0,x1,-1.77,1.77,0,0.73))              # 45-degree base so it prints flat
        if k%2==0: A=A.fuse(knuckle)
        else: B=B.fuse(knuckle)
    # bores: snug in A's knuckles, free in B's; lead-ins on B's faces to help threading
    for k,(x0,x1) in enumerate(kn):
        d=d_fixed if k%2==0 else d_free
        bore=_cyl(d/2,x0-0.05,x1+0.05)
        if k%2==0: A=A.cut(bore)
        else:
            B=B.cut(bore)
            B=B.cut(_cone(d/2+0.5,d/2,x0-0.05,1)).cut(_cone(d/2+0.5,d/2,x1+0.05,-1))
    # counterbores + 45 degree lead-in for the plugs at both outer ends
    A=A.cut(_cyl(CB_R,-0.1,CB_D)).cut(_cyl(CB_R,W-CB_D,W+0.1))
    A=A.cut(_cone(d_fixed/2+0.5,d_fixed/2,CB_D,1)).cut(_cone(d_fixed/2+0.5,d_fixed/2,W-CB_D,-1))
    for i in range(dimples):
        B=B.cut(cq.Solid.makeCylinder(0.7,0.7,cq.Vector(5+3*i,EDGE+DEPTH/2,T-0.6),cq.Vector(0,0,1)))
    return A.clean(),B.clean()

def plug(hole):
    """Press-in cap: Ø3.1 x 1.4 shaft, Ø4.0 x 0.5 flange, filament hole through the middle."""
    p=cq.Workplane('XY').circle(1.55).extrude(1.4).faces('>Z').workplane().circle(2.0).extrude(0.5).val()
    return p.cut(cq.Solid.makeCylinder(hole/2,3.0,cq.Vector(0,0,-0.5),cq.Vector(0,0,1)))

def sweep(A,B,limit=110,step=10):
    worst=0.0
    for deg in range(0,limit+1,step):
        worst=max(worst,A.intersect(B.rotate(cq.Vector(0,0,AXZ),cq.Vector(1,0,AXZ),deg)).Volume())
    return worst
