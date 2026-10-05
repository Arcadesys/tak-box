"""Integrated v18 case, original Cat/Witch target, mm. Flex poses are assumptions."""
from pathlib import Path
from functools import lru_cache
import sys
import cadquery as cq
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'v17-four-leaf/source'))
import folio as base
sys.path.insert(0,str(REPO/'v18-recessed-clasp'))
import build as clasp
box=base.box
mirror=base.mirror
fold=base.fold

def union(*shapes):
 s=shapes[0]
 for t in shapes[1:]:s=s.fuse(t)
 return s.clean()

def clasp_pose(s):
 # Bolt slides along case Y. Keeper lifts with the folded right housing.
 return s.rotate((0,0,0),(0,0,1),90).translate((-2,72,12.3))

def open_from_closed(s,angle):
 return s.rotate((98,0,16.3),(98,1,16.3),angle)

def beam(y0,y1,x0,x1,z0,z1,delta=0):
 def d(y):
  u=(y-y0)/(y1-y0)
  return delta*u*u*(3-u)/2
 pts=[(x0-d(y),y) for y in [y0+i*(y1-y0)/40 for i in range(41)]]
 pts += [(x1-d(y),y) for y in [y1-i*(y1-y0)/40 for i in range(41)]]
 return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1-z0).val()

def board_clip(y,release=0):
 root=union(box(-2,1.8,y,y+3,12.3,14.3),box(-2,-.8,y,y+3,7.2,14.3))
 arm=beam(y,y+25,-2,-.8,7.2,10.8,release)
 tooth=box(-.9-release,1-release,y+22,y+25,8.4,10.3)
 # Closing is manual press/release, square shoulder retention.
 return union(root,arm,tooth)

@lru_cache(None)
def board(side,release=0):
 clips=union(board_clip(5,release),board_clip(155,release))
 return union(base.board(side),clips if side=='left' else mirror(clips))

def drawer_catch(release=0):
 # Press towards drawer centre: negative beam deflection moves it +X.
 root=box(2.8,4,0,3,2.2,6.5)
 arm=beam(0,44,2.8,4,3,6.5,-release)
 tooth=box(-.2+release,2.9+release,32,44,2.5,10)
 return union(root,arm,tooth)

def drawer_stop(release=0):
 root=box(78,79.2,142,145,2.2,6.5)
 arm=beam(142,178,78,79.2,2.5,6.5,release)
 tooth=box(79.1-release,83-release,175,178,4,6.5)
 return union(root,arm,tooth)

@lru_cache(None)
def drawer(side,release=0,stop_release=0):
 p=box(2.8,89.1,0,190.4,1.4,2.2)
 for x in (2.8,87.9):p=p.fuse(box(x,x+1.2,0,190.4,2.2,5.7))
 for y in (0,189.2):p=p.fuse(box(2.8,89.1,y,y+1.2,2.2,10.2))
 # Actual original flats are 20 mm; 20.7 mm pockets give 0.35 mm/side.
 for i in range(3):
  for j in range(7):
   x=8+22*i;y=10+22.6*j
   rim=box(x-1.05,x+21.25,y-1.05,y+21.25,2.2,5.7)
   rim=rim.cut(box(x-.25,x+20.45,y-.25,y+20.45,2.19,5.71))
   # Finger opening on front of every pocket: upper 4.5 mm remains exposed.
   rim=rim.cut(box(x+5.1,x+15.1,y-1.06,y-.24,3.2,5.71))
   p=p.fuse(rim)
 p=p.cut(box(2.6,4.2,-.1,44.1,2.21,6.7)).cut(box(79.6,83.8,-.1,2.6,3.6,10.3)).cut(box(79.6,83.8,188.9,190.5,3.6,10.3))
 p=union(p,drawer_catch(release),drawer_stop(stop_release),box(30,61,-4,1,1.4,6.5))
 return p if side=='left' else mirror(p)

HATCH_AXIS=(0,219.8,23.2)
def hatch_rotate(s,angle):return s.rotate(HATCH_AXIS,(1,219.8,23.2),-angle)
def hatch_clip(release=0):
 root=union(box(-2,1.8,195,198,22.4,24.4),box(-2,-.8,195,198,18,24.4))
 return union(root,beam(195,216,-2,-.8,18,21.6,release),box(-.9-release,1-release,213,216,19.2,21.25))

def cylx(r,a,b):return cq.Solid.makeCylinder(r,b-a,cq.Vector(a,219.8,23.2),cq.Vector(1,0,0))
@lru_cache(None)
def hatch(release=0):
 p=union(box(.3,86.7,193.5,216.1,22.4,24.4),box(14,73,215.5,219.8,22.4,24.4),cylx(2.6,14,73),hatch_clip(release))
 return p.cut(cylx(1.7,13.99,73.01)).clean()

@lru_cache(None)
def housing(side):
 p=base.housing(side)
 def tool(s):return s if side=='left' else mirror(s)
 # Closed drawer catch window and two board-snap pockets.
 p=p.cut(tool(box(-.3,2.41,31.5,44.5,2.3,10.2)))
 for y in (5,155):p=p.cut(tool(box(-.1,1.5,y+21.8,y+25.2,8.1,10.6)))
 # Positive withdrawal stop in the empty outer lane; press arm to remove.
 ramp=cq.Workplane('YZ').polyline([(2.5,4),(14.5,10.7),(2.5,10.7)]).close().extrude(3.4).val().translate((80,0,0))
 p=p.fuse(tool(union(box(80,83.4,0,2.5,4,10.7),ramp))).clean()
 if side=='right':
  k=clasp_pose(clasp.keeper)
  bridge=union(box(-9,-.2,120,135,18.8,24.3),box(-9,2.4,120,135,20.8,24.3))
  p=union(p,fold(union(k,bridge),180))
 else:
  p=union(p,clasp_pose(clasp.receiver),box(-8,2.4,60,112,0,11.8),box(-8,-.2,60,112,11.7,13.3))
  compartment=box(0,87,193.2,218,0,22.2).cut(box(1.6,85.4,194.8,216.4,1.2,22.3))
  compartment=compartment.cut(cylx(2.85,12.2,74.8))
  for x in (33.3,63.3):compartment=compartment.cut(cq.Solid.makeCylinder(6,1.4,cq.Vector(x,205.5,-.1)))
  compartment=compartment.cut(box(-.1,1.5,212.8,216.2,18.9,21.4))
  p=union(p,box(0,85,190.4,195,0,1.2),compartment)
  for a,b in ((0,12),(75,87)):
   p=union(p,box(a,b,216.4,220,20,23.2),cylx(2.6,a,b).cut(cylx(1.7,a-.01,b+.01)))
 if side=='left':p=p.cut(cylx(1.7,-.01,12.01)).cut(cylx(1.7,74.99,87.01)).clean()
 # Blind outer ends retain the main axles without a cap in the playing field.
 p=union(p,base.cyly(1.7,4.6,5.6) if side=='right' else base.cyly(1.7,193.2,194.2))
 return p.clean()

@lru_cache(None)
def slider(delta=0,travel=0):return clasp_pose(clasp.slider(delta,travel))

def axle_cap():
 # Glue-on permanent axle end cap, not a case closure. 3.2 mm nominal bore.
 p=cq.Solid.makeCylinder(3.5,4,cq.Vector(0,0,0))
 return p.cut(cq.Solid.makeCylinder(1.6,3,cq.Vector(0,0,1))).clean()

def parts():
 return {**{f'{kind}-{side}':globals()[kind](side) for side in ('left','right') for kind in ('housing','board','drawer')},'capstone-hatch':hatch(),'clasp-slider':slider(),'axle-end-cap':axle_cap()}
