"""Integrated v21 case, original Cat/Witch target, mm. Flex poses are assumptions."""
from pathlib import Path
from functools import lru_cache
import sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parent
sys.path.insert(0,str(OUT/'source/vendor/body'))
import folio as base
box=base.box
mirror=base.mirror
fold=base.fold
HINGE_PIN_D=1.75
HINGE_BORE_D=2.0
CAP_BORE_D=1.9
# Only bases are hinged. Three interleaved barrels per end reduce free pin span.
base.L=194.8
base.FAMILIES={
 'tray-left':((-14.,-9.8),(-4.6,-.4),(199.8,204.2)),
 'tray-right':((-9.4,-5.),(195.2,199.4),(204.6,208.8)),
}
BOARD_RELEASE=2.8
BOARD_TRAVEL=106
HOOK_Y_SHIFT=-100


def union(*shapes):
 s=shapes[0]
 for t in shapes[1:]:s=s.fuse(t)
 return s.clean()

def filament_main_bores(s,side,kind):
 # Fill only the baseline pin passages, preserving individual hinge families.
 family=("tray" if kind=="housing" else "board")+"-"+side
 for a,b in base.FAMILIES[family]:
  passage=base.cyly(HINGE_BORE_D/2,a-.01,b+.01)
  if kind in ('board','housing'):
   # Board prints face up: a 45-degree roof above the circular pin envelope.
   h=HINGE_BORE_D/2/(2**.5)
   roof=cq.Workplane('XZ').polyline([(98-h,16.3+h),(98+h,16.3+h),(98,16.3+2*h)]).close().extrude(b-a+.02).val().translate((0,b+.01,0))
   passage=union(passage,roof)
  s=union(s,base.cyly(1.72,a,b)).cut(passage)
 return s.clean()

# Side hook rotates in the YZ plane; X is its filament-pivot axis.
HOOK_AXIS=(-5.2,-6.,7.)
HOOK_OPEN_ANGLE=65

def x_cylinder(r,a,b,y,z):
 return cq.Solid.makeCylinder(r,b-a,cq.Vector(a,y,z),cq.Vector(1,0,0))

def hook_rotate(s,angle):
 return s.rotate(HOOK_AXIS,(-4.2,-6.,7.),angle)

def hook_pivot_passage():
 h=1/(2**.5)
 roof=cq.Workplane('YZ').polyline([(94-h,7+h),(94+h,7+h),(94,7+2*h)]).close().extrude(4.61).val().translate((-3.61,0,0))
 return union(x_cylinder(1,-3.61,1.0,94,7),roof).translate((0,HOOK_Y_SHIFT,0))

def hook_pivot_mount():
 # Flat friction bearing pad and reverse stop beneath the broad thumb foot.
 return union(x_cylinder(4.5,-3.6,.8,94,7),box(-3.2,.8,89.5,98.5,2.5,7),box(-6.8,.8,98.7,103,0,4.6)).translate((0,HOOK_Y_SHIFT,0)).cut(hook_pivot_passage()).clean()

def hook_keeper():
 # Closed-pose headed catch: the head prevents the hook sliding off sideways.
 return union(x_cylinder(4,-3.2,.8,90,25),x_cylinder(2,-7.2,-3,90,25),x_cylinder(3.5,-8.8,-7.2,90,25)).translate((0,HOOK_Y_SHIFT,0))

@lru_cache(None)
def side_hook(angle=0):
 # Broad rigid hook, open mouth toward +Y. Opening load seats it toward stop.
 yz=[(91,5),(99.5,5),(99.5,9),(95,9),(87.6,22),(87.6,27.65),(98,27.65),(98,31),(84,31),(84,21)]
 p=cq.Workplane('YZ').polyline(yz).close().extrude(3.2).val().translate((-6.8,0,0))
 p=union(p,x_cylinder(4.5,-6.8,-3.6,94,7))
 p=p.cut(x_cylinder(1,-6.81,-3.59,94,7)).clean()
 return hook_rotate(p.translate((0,HOOK_Y_SHIFT,0)),angle)

def open_from_closed(s,angle):
 return s.rotate((98,0,16.3),(98,1,16.3),angle)

def beam(y0,y1,x0,x1,z0,z1,delta=0):
 def d(y):
  u=(y-y0)/(y1-y0)
  return delta*u*u*(3-u)/2
 pts=[(x0-d(y),y) for y in [y0+i*(y1-y0)/40 for i in range(41)]]
 pts += [(x1-d(y),y) for y in [y1-i*(y1-y0)/40 for i in range(41)]]
 return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1-z0).val()

def x_prism(points,x0,x1):
 # YZ section extruded along X: rails and board edges run sideways.
 return cq.Workplane('YZ').polyline(points).close().extrude(x1-x0).val().translate((x0,0,0))

def board_catch(release=0):
 def d(x):
  u=x/54
  return release*u*u*(3-u)/2
 pts=[(x,5.1+d(x)) for x in [54*i/40 for i in range(41)]]
 pts += [(x,6.3+d(x)) for x in [54*i/40 for i in range(40,-1,-1)]]
 arm=cq.Workplane('XY').workplane(offset=10.6).polyline(pts).close().extrude(4.7).val()
 return union(box(0,3,5.1,9.5,10.6,15.3),arm,box(34,54,-.2+release,5.2+release,10.6,15.3))

@lru_cache(None)
def board(side,release=0):
 # One part is both playing surface and the sealed storage top.
 p=x_prism([(3.1,10.6),(192.3,10.6),(192.3,14.2),(191.2,15.3),(4.2,15.3),(3.1,14.2)],0,97.8)
 p=p.cut(box(3,57,2.9,9.5,10.5,15.4))
 p=union(p,board_catch(release),box(-5,1,80,112,10.6,15.3),box(0,1.6,10,190,15.3,16.3))
 # Stops lie outside the complete 180 mm field and block over-insertion.
 p=p.cut(box(95,98,2.9,5.4,10.5,15.4)).cut(box(95,98,190.4,192.4,10.5,15.4))
 for i in range(6):
  y=10+36*i
  p=p.cut(box(7.6,97.81,y-.4,y+.4,14.7,15.31))
 for x in (8,44,80):p=p.cut(box(x-.4,x+.4,9.6,190.4,14.7,15.31))
 return p.clean() if side=='left' else mirror(p).clean()

def slide(s,side,distance):
 return s.translate(((-distance if side=='left' else distance),0,0))

def pocket_rims():
 rims=[]
 for i in range(3):
  for j in range(7):
   x=12+22*i;y=10+22.6*j
   rim=box(x-1.05,x+21.25,y-1.05,y+21.25,2.19,5.7)
   rim=rim.cut(box(x-.25,x+20.45,y-.25,y+20.45,2.18,5.71))
   rim=rim.cut(box(x+5.1,x+15.1,y-1.06,y-.24,3.2,5.71))
   rims.append(rim)
 return rims

HATCH_AXIS=(0,221.8,23.2)
def hatch_rotate(s,angle):return s.rotate(HATCH_AXIS,(1,221.8,23.2),-angle)
def hatch_clip(release=0):
 root=union(box(-2,1.8,197,200,22.4,24.4),box(-2,-.8,197,200,18,24.4))
 return union(root,beam(197,218,-2,-.8,18,21.6,release),box(-.9-release,1-release,215,218,19.2,21.25))

def cylx(r,a,b):return cq.Solid.makeCylinder(r,b-a,cq.Vector(a,221.8,23.2),cq.Vector(1,0,0))
def fixed_hatch_passage(a,b):
 # Housing prints bottom down: bore roof points upward in Z.
 h=HINGE_BORE_D/2/(2**.5)
 roof=cq.Workplane('YZ').polyline([(221.8-h,23.2+h),(221.8+h,23.2+h),(221.8,23.2+2*h)]).close().extrude(b-a).val().translate((a,0,0))
 return union(cylx(HINGE_BORE_D/2,a,b),roof)
@lru_cache(None)
def hatch(release=0):
 p=union(box(.3,86.7,195.5,218.1,22.4,25.8),box(14,73,217.5,221.8,22.4,25.8),cylx(2.6,14,73),hatch_clip(release))
 h=HINGE_BORE_D/2/(2**.5)
 roof=cq.Workplane('YZ').polyline([(221.8-h,23.2-h),(221.8+h,23.2-h),(221.8,23.2-2*h)]).close().extrude(59.02).val().translate((13.99,0,0))
 return p.cut(union(cylx(HINGE_BORE_D/2,13.99,73.01),roof)).clean()

@lru_cache(None)
def housing(side):
 # Fixed seats and open top print on a broad base, with no internal roof.
 p=box(0,97.8,0,194.8,0,10.3).cut(box(2.4,89.5,2.4,193,2.2,30))
 p=union(p,*pocket_rims(),box(0,97.8,0,2.4,10.3,15.8),box(0,97.8,193,194.8,10.3,15.8))
 front=x_prism([(2.4,13.8),(4.4,15.8),(2.4,15.8)],57,97.8)
 rear=x_prism([(193,13.8),(191,15.8),(193,15.8)],0,97.8)
 p=union(p,front,rear,box(95.3,97.8,2.4,5.1,10.3,15.8),box(95.3,97.8,190.7,193,10.3,15.8))
 # Front button window; the outer front rail is relieved for its full stroke.
 p=p.cut(box(33.5,54.5,-.3,2.41,10.4,16))
 # The hook lives at the front corner, entirely ahead of the board slide path.
 p=union(p,box(0,6,-14,2.4,0,10.3))
 if side=='right':p=mirror(p)
 p=filament_main_bores(base.hinged(p,'tray-'+side,0,1.2),side,'housing')
 if side=='right':
  p=union(p,fold(hook_keeper(),180))
 else:
  p=union(p,hook_pivot_mount())
  compartment=box(0,87,195.2,220,0,22.2).cut(box(1.6,85.4,196.8,218.4,1.2,22.3))
  compartment=compartment.cut(cylx(2.85,12.2,74.8))
  for x in (33.3,63.3):compartment=compartment.cut(cq.Solid.makeCylinder(6,1.4,cq.Vector(x,207.5,-.1)))
  compartment=compartment.cut(box(-.1,1.5,214.8,218.2,18.9,21.4))
  p=union(p,box(0,85,192.4,197,0,1.2),compartment)
  for a,b in ((0,12),(75,87)):
   p=union(p,box(a,b,218.4,222,20,23.2),cylx(2.6,a,b).cut(fixed_hatch_passage(a-.01,b+.01)))
 if side=='left':p=p.cut(hook_pivot_passage()).cut(fixed_hatch_passage(-.01,12.01)).cut(fixed_hatch_passage(74.99,87.01)).clean()
 # Main bores are through passages: bond only the outermost housing barrel
 # to each filament axle after dry assembly. Other leaves remain free.
 return p.clean().fix()

def axle_cap():
 # Bonded filament-pin collar. Through bore avoids a closed-floor transition.
 p=box(-3.5,3.5,-3.5,3.5,0,4)
 return p.cut(cq.Solid.makeCylinder(CAP_BORE_D/2,4.02,cq.Vector(0,0,-.01))).clean()

def parts():
 return {**{f'{kind}-{side}':globals()[kind](side) for side in ('left','right') for kind in ('housing','board')},'capstone-hatch':hatch(),'side-hook':side_hook(),'axle-end-cap':axle_cap()}
