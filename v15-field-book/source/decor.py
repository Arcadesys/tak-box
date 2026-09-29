"""Flush colour inlays for the v15 board and trays. Units: mm.

Everything here is a 2D stroke or dot extruded DEPTH into a face. Strokes are
0.8 mm wide (two 0.4 mm lines) with at least 0.4 mm between neighbouring turns,
so a 0.4 mm nozzle can reproduce them.

- Galaxies: small two-arm spirals, sparse, inside the black cells.
- Comets: a white head with a tapered tail and a side streak in orange or purple.
- Stars: 0.9 mm white dots and a few white four-point sparkles in the cells.
- Tray floors: a crescent moon in the player colour and white sparkles.
"""
import math
import cadquery as cq

W=.8          # stroke width
DEPTH=.6
STAR_R=.45


def _stroke2d(pts,w=W):
    """Polygon outline of a polyline stroked to width w (no end caps)."""
    left=[];right=[]
    n=len(pts)
    for i,(x,y) in enumerate(pts):
        x0,y0=pts[max(i-1,0)];x1,y1=pts[min(i+1,n-1)]
        dx,dy=x1-x0,y1-y0;L=math.hypot(dx,dy) or 1
        nx,ny=-dy/L*w/2,dx/L*w/2
        left.append((x+nx,y+ny));right.append((x-nx,y-ny))
    return left+right[::-1]

def stroke(pts,z0,z1,w=W):
    """Extruded stroke with round caps, between z0 and z1."""
    s=cq.Workplane('XY',origin=(0,0,z0)).polyline(_stroke2d(pts,w)).close().extrude(z1-z0).val()
    for x,y in (pts[0],pts[-1]):
        s=s.fuse(cq.Solid.makeCylinder(w/2,z1-z0,cq.Vector(x,y,z0),cq.Vector(0,0,1)))
    return s.clean()

def dot(x,y,r,z0,z1):
    return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0),cq.Vector(0,0,1))

def union(shapes):
    s=shapes[0]
    for o in shapes[1:]:s=s.fuse(o)
    return s.clean()


# ------------------------------------------------------------------ motifs
def galaxy(cx,cy,r=3.4,rot=0.0):
    """Two-arm spiral galaxy: a core dot plus two trailing arms."""
    arms=[]
    for arm in (0,math.pi):
        pts=[]
        n=40
        for k in range(n+1):
            t=k/n
            rr=1.15+(r-1.15)*t
            a=rot+arm+t*math.pi*1.05
            pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
        arms.append(pts)
    return arms,(cx,cy,1.05)   # overlaps the arm roots; a tangent join makes knife edges


def comet(x,y,ang,r=1.3,L=14.0,bend=.10):
    """(head circle, tail outline, streak outline) for a comet whose tail points along ang.

    The tail tapers from just under the head's width to 0.8 mm and curves
    slightly; a 0.8 mm streak runs beside it, 0.9 mm clear of the head. Same
    maths as tak-open-wells-v5's tak_symbols.comet.
    """
    dx,dy=math.cos(ang),math.sin(ang);px,py=-dy,dx
    def centre(t,off=0.0):
        s=L*t;b=bend*L*t*t
        return x+dx*s+px*(b+off),y+dy*s+py*(b+off)
    def band(t0,t1,hw,off=0.0,n=24):
        left=[];right=[]
        for k in range(n+1):
            t=t0+(t1-t0)*k/n;cx,cy=centre(t,off);w=hw(t)
            left.append((cx+px*w,cy+py*w));right.append((cx-px*w,cy-py*w))
        return left+right[::-1]
    tail=band(0,1,lambda t:.85*r*(1-t)+.4*t)
    streak=band(.15,.65,lambda t:.4,off=r+.9)
    return (x,y,r),tail,streak


# ------------------------------------------------------- moons and sparkles
def poly(pts,z0,z1):
    return cq.Workplane('XY',origin=(0,0,z0)).polyline(pts).close().extrude(z1-z0).val()

def sparkle(x,y,R=2.0,rot=0.0):
    """Four-point star."""
    pts=[]
    for k in range(8):
        r=R if k%2==0 else R*.3
        a=rot+k*math.pi/4
        pts.append((x+r*math.cos(a),y+r*math.sin(a)))
    return pts

def crescent(x,y,r,ang,z0,z1):
    """Crescent moon opening toward ang."""
    outer=cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0),cq.Vector(0,0,1))
    cut=cq.Solid.makeCylinder(r*.82,z1-z0+.2,cq.Vector(x+.48*r*math.cos(ang),y+.48*r*math.sin(ang),z0-.1),cq.Vector(0,0,1))
    return outer.cut(cut).clean()

def sparkles_in_gaps(u0,u1,v0,v1,to_xy,keep,z0,z1,R=1.9,clear=1.2,every=9.0,seed=1,jitter=1.5):
    """Place sparkles on a jittered lattice wherever they clear the vine."""
    import random
    rnd=random.Random(seed)
    out=[]
    u=u0+R+1
    while u<u1-R-1:
        v=v0+R+1+rnd.random()*2
        while v<v1-R-1:
            uu=min(max(u+rnd.uniform(-jitter,jitter),u0+R+.5),u1-R-.5)
            x,y=to_xy(uu,v)
            if all(math.hypot(x-a,y-b)>R+clear for a,b in keep):
                rr=R*rnd.uniform(.7,1.0)
                out.append(poly(sparkle(x,y,rr,rnd.uniform(0,.4)),z0,z1))
                keep=keep+[(x,y)]
            v+=every*rnd.uniform(.8,1.2)
        u+=every*.8
    return union(out) if out else None
