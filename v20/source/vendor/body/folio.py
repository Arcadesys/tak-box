"""Four independent leaves on one axis. Preliminary topology study, mm."""
from functools import lru_cache
import cadquery as cq

AX=(98.,16.3)
L=192.8
FAMILIES={
 'tray-left':((-18.,-12.4),(193.2,198.8)),
 'board-left':((-12.,-6.4),(199.2,204.8)),
 'board-right':((-6.,-.4),(205.2,210.8)),
 'tray-right':((0.,5.6),(211.2,216.8)),
}

def box(x0,x1,y0,y1,z0,z1):
 return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def cyly(r,y0,y1):
 return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(AX[0],y0,AX[1]),cq.Vector(0,1,0))
def mirror(s): return s.mirror('YZ',(98,0,0))
def fold(s,a): return s.rotate((98,0,16.3),(98,1,16.3),-a)

def hinged(p,name,z0,z1):
 right=name.endswith('right')
 # Every leaf has its own spaced knuckles on the same axis, at both ends.
 for a,b in FAMILIES[name]:
  root=box(95.5,97.8,a,b,z0,16.3).fuse(box(90.,97.8,a,b,z0,z1))
  if right: root=mirror(root)
  end=box(90.,92.,min(a,0),max(b,L),z0,z1)
  if right: end=mirror(end)
  p=p.fuse(root).fuse(end).fuse(cyly(3.,a,b))
 # Relieve all other families, and the shared axle through every barrel.
 for other,segments in FAMILIES.items():
  if other!=name:
   for a,b in segments:
    p=p.cut(cyly(3.25,a-.15,b+.15))
    relief=box(92.1,103.5,a-.15,b+.15,-.1,19.6)
    p=p.cut(relief if not right else mirror(relief))
 for a,b in FAMILIES[name]: p=p.cut(cyly(1.7,a-.01,b+.01))
 return p.clean()

@lru_cache(None)
def housing(side):
 p=box(0,97.8,0,L,0,11.8)
 # Open drawer tunnel with a fixed roof: pieces remain covered in rotation.
 p=p.cut(box(2.4,89.5,-.1,190.8,1.2,10.6))
 return hinged(p,'tray-'+side,0,1.2) if side=='left' else hinged(mirror(p),'tray-'+side,0,1.2)

@lru_cache(None)
def board(side):
 p=box(0,97.8,0,L,12.3,15.3)
 # Recessed grid is deliberately shallow, for a later contrasting inlay.
 for i in range(6):
  y=10+36*i
  p=p.cut(box(7.6,97.81,y-.4,y+.4,14.7,15.31))
 for x in (8,44,80): p=p.cut(box(x-.4,x+.4,9.6,190.4,14.7,15.31))
 p=p.fuse(box(0,1.6,0,L,15.3,16.3))
 for a,b in ((0,1.6),(191.2,L)): p=p.fuse(box(0,94,a,b,15.3,16.3))
 return hinged(p,'board-'+side,12.3,15.3) if side=='left' else hinged(mirror(p),'board-'+side,12.3,15.3)

def stone_envelopes(side):
 out=[]
 for j in range(7):
  for i in range(3):
   x=8+22*i;y=10+21.4*j
   p=box(x+.35,x+19.85,y+.35,y+19.85,2.2,10.2)
   out.append(p if side=='left' else mirror(p))
 return out

def cap_compartment():
 # Separate rear shared compartment, clear of all four swept leaf bodies.
 p=box(0,90,193.2,218,0,22.2)
 return p.cut(box(1.6,88.4,194.8,216.4,1.2,22.3))

def cap_envelopes():
 return [box(x,x+25.4,194.9,214.3,1.2,20.6) for x in (21.3,51.3)]

def axle_parts():
 return [cyly(1.5,-18,5.6),cyly(1.5,193.2,216.8)]

@lru_cache(None)
def drawer(side):
 p=box(2.8,89.1,0,190.4,1.4,2.2)
 for x in (2.8,87.9): p=p.fuse(box(x,x+1.2,0,190.4,2.2,5.7))
 for y in (0,189.2): p=p.fuse(box(2.8,89.1,y,y+1.2,2.2,10.2))
 for i in range(3):
  for j in range(7):
   x=8+22*i;y=10+21.4*j
   rim=box(x-.4,x+20.6,y-.4,y+20.6,2.2,5.7)
   p=p.fuse(rim.cut(box(x,x+20.2,y,y+20.2,2.1,5.8)))
 return p.clean() if side=='left' else mirror(p.clean())
