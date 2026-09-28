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
