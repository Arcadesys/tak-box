"""Flush colour inlays for the v14 board and trays. Units: mm.

Everything here is a 2D stroke or dot extruded DEPTH into a face. Strokes are
0.8 mm wide (two 0.4 mm lines) with at least 0.4 mm between neighbouring turns,
so a 0.4 mm nozzle can reproduce them.

- Border vines: a wave with curls, orange on leaf A (cat), purple on leaf B (witch).
- Galaxies: small two-arm spirals, sparse, inside the black cells.
- Stars: 0.9 mm white dots scattered through the cells.
- Tray swirls: a pair of curls on each tray front.
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
def spiral(cx,cy,r_out,r_in,turns,start,hand=1,step=.25):
    """Archimedean spiral from the outer end inward. hand=+1 CCW inward."""
    out=[];n=max(12,int(turns*2*math.pi*r_out/step))
    for k in range(n+1):
        t=k/n
        r=r_out+(r_in-r_out)*t
        a=start+hand*t*turns*2*math.pi
        out.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return out

def vine(u0,u1,vc,half,to_xy,curl_every=22.0,phase=0.0):
    """A wave along u (u0..u1) around v=vc, with a curl at every crest.

    half: usable half-height of the band. to_xy maps (u,v) -> (x,y).
    Returns a list of polylines in xy.
    """
    amp=half*.28
    lam=2*curl_every
    base=[]
    n=int((u1-u0)/.4)
    for k in range(n+1):
        u=u0+(u1-u0)*k/n
        base.append((u,vc+amp*math.sin(2*math.pi*(u-u0)/lam+phase)))
    lines=[[to_xy(u,v) for u,v in base]]
    r_out=half-amp-W/2-.35
    turns=1.6 if r_out>2.6 else .95
    k=0
    u=u0+lam/4
    while u<u1-lam/8:
        side=1 if math.sin(2*math.pi*(u-u0)/lam+phase)>0 else -1
        # The curl hangs off the crest toward the band's middle and winds in.
        vb=vc+side*amp
        cx,cy=u+r_out*.15,vb-side*(r_out+W*.1)
        # Start on the top/bottom of the circle so it leaves the wave tangentially.
        start=math.pi/2 if side>0 else -math.pi/2
        pts=spiral(cx,cy,r_out,.7,turns,start,hand=side)
        lines.append([to_xy(a,b) for a,b in pts])
        u+=lam/2;k+=1
    return lines

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


# ------------------------------------------------------- cosmic witchy vine
def poly(pts,z0,z1):
    return cq.Workplane('XY',origin=(0,0,z0)).polyline(pts).close().extrude(z1-z0).val()

def leaf(x,y,ang,L=6.0,Wd=2.4,n=16):
    """Pointed almond leaf with its base at (x,y), pointing along ang."""
    ca,sa=math.cos(ang),math.sin(ang)
    side=[];other=[]
    for k in range(n+1):
        t=k/n;s=t*L;w=Wd/2*math.sin(math.pi*t)**.8
        side.append((x+s*ca-w*sa,y+s*sa+w*ca))
        other.append((x+s*ca+w*sa,y+s*sa-w*ca))
    return side+other[::-1][1:-1]

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

def cosmic_vine(u0,u1,v0,v1,to_xy,z0,z1,stem_w=1.2,seed=0.0,moons=True,leaf_len=6.0,amp_frac=.42):
    """A leafy vine meandering along u inside the band v0..v1.

    Returns (accent_solid, sparkle_polygons_xy). Sparkles are placed later,
    in the gaps, in a second colour.
    """
    vc=(v0+v1)/2;half=(v1-v0)/2
    amp=half*amp_frac
    def stem_v(u):
        p=(u-u0)
        return vc+amp*(math.sin(p/9.0+seed)*.75+math.sin(p/4.1+2*seed)*.25)
    n=int((u1-u0)/.35)
    stem=[(u0+(u1-u0)*k/n,) for k in range(n+1)]
    stem=[(u,stem_v(u)) for (u,) in stem]
    shapes=[stroke([to_xy(u,v) for u,v in stem],z0,z1,stem_w)]
    keep=[to_xy(u,v) for u,v in stem]           # occupied points for sparkle spacing
    # Leaves every ~6.5 mm, alternating sides, swept back along the stem.
    u=u0+3.0;side=1;k=0
    while u<u1-3:
        v=stem_v(u);dv=(stem_v(u+.3)-stem_v(u-.3))/.6
        base=math.atan2(dv,1.0)
        ang=base+side*math.radians(48)
        # Leaves stay inside the band: size them to the room left beside the stem.
        L=min(leaf_len,(half-abs(v-vc)-stem_w/2-.3)/math.sin(math.radians(60)))
        # Every third leaf trades for a curling tendril in wide bands.
        if not (k%3==2 and half>5) and L>=2.0:
            pts=leaf(u,v,ang,L,max(L*.4,1.0))
            xy=[to_xy(a,b) for a,b in pts]
            shapes.append(poly(xy,z0,z1));keep+=xy
        elif L<2.0:
            # Too narrow for leaves: a berry budding off the stem instead.
            r=.7;d=stem_w/2+r-.25
            bv=v+side*d
            if v0+r+.1<bv<v1-r-.1:
                x,y=to_xy(u,bv)
                shapes.append(dot(x,y,r,z0,z1));keep.append((x,y))
        if k%3==2 and half>5:
            r=min(3.2,half*.45)
            cx,cy=u+.6,v+side*(r+1.2)
            sp=spiral(cx,cy,r,.7,1.35,-side*math.pi/2,hand=side)
            spxy=[to_xy(a,b) for a,b in sp]
            shapes.append(stroke(spxy,z0,z1,.9));keep+=spxy
        u+=6.5;side=-side;k+=1
    if moons and half>6:
        for frac,sd in ((.3,1),(.72,-1)):
            mu=u0+(u1-u0)*frac
            # Midway between the stem and the band edge, never against the wall.
            edge=v1-3.4 if sd>0 else v0+3.4
            mv=(stem_v(mu)+edge)/2
            mv=min(max(mv,v0+3.4),v1-3.4)
            x,y=to_xy(mu,mv)
            if any(math.hypot(x-a,y-b)<3.6 for a,b in keep):continue
            shapes.append(crescent(x,y,2.6,math.pi*(.25 if sd>0 else 1.25),z0,z1))
            keep+=[(x+2.6*math.cos(a),y+2.6*math.sin(a)) for a in [i*math.pi/6 for i in range(12)]]+[(x,y)]
    return union(shapes),keep

def sparkles_in_gaps(u0,u1,v0,v1,to_xy,keep,z0,z1,R=1.9,clear=1.2,every=9.0,seed=1):
    """Place sparkles on a jittered lattice wherever they clear the vine."""
    import random
    rnd=random.Random(seed)
    out=[]
    u=u0+R+1
    while u<u1-R-1:
        v=v0+R+1+rnd.random()*2
        while v<v1-R-1:
            x,y=to_xy(u+rnd.uniform(-1.5,1.5),v)
            if all(math.hypot(x-a,y-b)>R+clear for a,b in keep):
                rr=R*rnd.uniform(.7,1.0)
                out.append(poly(sparkle(x,y,rr,rnd.uniform(0,.4)),z0,z1))
                keep=keep+[(x,y)]
            v+=every*rnd.uniform(.8,1.2)
        u+=every*.8
    return union(out) if out else None
