"""Direct over-center draw-latch coupon, not integrated case geometry.
85% of the earlier 35.1 mm linkage; M2.5 permanent pivots, 2.89 mm bores.
No closure pin, magnets or sleeve. Units mm. Physical performance untested.
"""
from functools import lru_cache
import cadquery as cq
from folio import box
SHELL_H=23.6
def cyly(r,y0,y1,x,z):
 return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
LATCH_Y=(34.,144.)
O=(-5.,16.)
C=(-3.,33.6)
CRANK_R=6.
CLOSED=275.
OPEN=220.

def crank(angle=CLOSED):
    import math
    a=math.radians(angle)
    return (O[0]+CRANK_R*math.cos(a),O[1]+CRANK_R*math.sin(a))

def xz_bar(a,b,width,y0,y1):
    import math
    dx,dz=b[0]-a[0],b[1]-a[1];ll=math.hypot(dx,dz)
    px,pz=-dz/ll*width/2,dx/ll*width/2
    pts=[(a[0]+px,a[1]+pz),(b[0]+px,b[1]+pz),(b[0]-px,b[1]-pz),(a[0]-px,a[1]-pz)]
    return cq.Workplane('XZ',origin=(0,y0,0)).polyline(pts).close().extrude(-(y1-y0)).val()

def latch_mount(y):
    # Rigid guard cheeks protect the closed handle; pivots are steel M3.
    p=box(-.5,.01,y,y+14.,2.,SHELL_H)
    for ya,yb in ((y,y+1.),(y+13.,y+14.)):
        p=p.fuse(box(-9.,.01,ya,yb,2.,SHELL_H))
    p=p.cut(cyly(1.7,y-.1,y+14.1,*O))
    # Square stop just beyond the closed handle; pull load pushes into it.
    p=p.fuse(box(-1.751,.01,y+1.,y+13.,2.,7.))
    return p.clean()

def keeper(y):
    # Broad rectangular ledge, not a closure pin. Hooks bear on its top.
    return box(-4.2,2.,y+3.,y+11.,32.4,33.6).fuse(box(0.,2.,y+2.,y+12.,30.5,33.6)).clean()

def keeper_all():
    return keeper(LATCH_Y[0]).fuse(keeper(LATCH_Y[1]))

@lru_cache(None)
def lever(y=LATCH_Y[0],angle=CLOSED):
    import math
    A=crank();a=math.radians(CLOSED)
    end=(O[0]+12.*math.cos(a),O[1]+12.*math.sin(a))
    p=None
    for ya,yb in ((y+1.2,y+4.2),(y+9.8,y+12.8)):
        part=xz_bar(O,end,4.4,ya,yb).fuse(cyly(3.2,ya,yb,*O)).fuse(cyly(3.2,ya,yb,*A)).fuse(cyly(2.2,ya,yb,*end))
        part=part.cut(cyly(1.7,ya-.1,yb+.1,*O)).cut(cyly(1.7,ya-.1,yb+.1,*A))
        p=part if p is None else p.fuse(part)
    p=p.fuse(cyly(2.2,y+1.2,y+12.8,*end)).clean()
    return p.rotate((O[0],y,O[1]),(O[0],y+1,O[1]),-(angle-CLOSED))

@lru_cache(None)
def draw_hook(y=LATCH_Y[0]):
    A=crank();H=(-5.,31.)
    p=xz_bar(A,H,2.8,y+4.5,y+9.5).fuse(cyly(3.2,y+4.5,y+9.5,*A))
    h=box(-6.5,-1.,y+4.5,y+9.5,30.8,35.1)
    h=h.cut(box(-4.4,-.9,y+4.4,y+9.6,32.2,33.6))
    return p.fuse(h).cut(cyly(1.7,y+4.4,y+9.6,*A)).clean()

def hook_released(y):
    A=crank();B=crank(OPEN)
    p=draw_hook(y).translate((B[0]-A[0],0,B[1]-A[1]))
    return p.rotate((B[0],y,B[1]),(B[0],y+1,B[1]),-30.)

def pivot_hardware(y):
    A=crank()
    return [cyly(1.5,y,y+20.,*O),cyly(2.75,y-3.,y,*O),
            cyly(1.5,y+1.2,y+17.2,*A),cyly(2.75,y-1.8,y+1.2,*A)]


def coupon():
 scale=.85;y=34.
 mount=latch_mount(y).fuse(box(-.5,8,y,y+14,2,8))
 top=keeper(y).fuse(box(0,8,y+2,y+12,30.5,33.6))
 return {
  'latch-mount':mount.scale(scale),
  'latch-lever':lever(y).scale(scale),
  'latch-hook':draw_hook(y).scale(scale),
  'latch-keeper':top.scale(scale),
 }
