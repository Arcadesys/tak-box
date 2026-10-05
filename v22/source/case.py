"""Integrated v22 case, original Cat/Witch flats plus V22 flat capstones, mm. Flex poses are assumptions."""
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
# V16-style opposed captive pivots: print both bases together, open flat.
base.L=194.8
base.FAMILIES={'tray-left':((-9.3,-5.0),(195.2,199.5)),'tray-right':((-14.,-9.7),(199.9,204.2))}
PRINT_BASE_SHIFT=(17,21,0)
PIP_PIN_R=1.5
PIP_CLEARANCE=.4
PIP_STATIONS=((-9.7,-9.3,1),(199.9,199.5,-1))
BOARD_RELEASE=2.8
BOARD_TRAVEL=106
HOOK_Y_SHIFT=-100


def union(*shapes):
 s=shapes[0]
 for t in shapes[1:]:s=s.fuse(t)
 return s.clean()

def pip_pin(face,d):
 end=face+d*2.5
 pin=base.cyly(PIP_PIN_R,min(face,end),max(face,end))
 return union(pin,cq.Solid.makeCone(PIP_PIN_R,.3,1.2,cq.Vector(98,end,base.AX[1]),cq.Vector(0,d,0)))

def pip_socket(mouth,d):
 end=mouth+d*2.8
 cavity=base.cyly(PIP_PIN_R+PIP_CLEARANCE,min(mouth-d*.05,end),max(mouth-d*.05,end))
 return union(cavity,cq.Solid.makeCone(PIP_PIN_R+PIP_CLEARANCE,.1,1.3,cq.Vector(98,end,base.AX[1]),cq.Vector(0,d,0)))

def pip_hinges(s,side):
 # The inherited helper supplies rooted barrels; fill its old axle passages.
 for a,b in base.FAMILIES['tray-'+side]:s=union(s,base.cyly(1.72,a,b))
 for face,mouth,d in PIP_STATIONS:
  s=union(s,pip_pin(face,d)) if side=='right' else s.cut(pip_socket(mouth,d))
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

def capstone_rim():
 rim=box(12.9,42.3,167.3,190.7,2.19,5.7).cut(box(14,41.2,168.4,189.6,2.18,5.71))
 # Two broad grasp openings; the piece also projects 4.5 mm above this rim.
 return rim.cut(box(21,34,167.2,168.5,3.2,5.71)).cut(box(12.8,14.1,175,183,3.2,5.71)).clean()

def stored_capstone(team,side):
 import flat_capstones
 s=flat_capstones.capstone(team);b=s.BoundingBox()
 s=s.translate((27.6-(b.xmin+b.xmax)/2,179-(b.ymin+b.ymax)/2,2.2))
 return s if side=='left' else mirror(s)

@lru_cache(None)
def housing(side):
 # Fixed seats and open top print on a broad base, with no internal roof.
 p=box(0,97.8,0,194.8,0,10.3).cut(box(2.4,89.5,2.4,193,2.2,30))
 p=union(p,*pocket_rims(),capstone_rim(),box(0,97.8,0,2.4,10.3,15.8),box(0,97.8,193,194.8,10.3,15.8))
 front=x_prism([(2.4,13.8),(4.4,15.8),(2.4,15.8)],57,97.8)
 rear=x_prism([(193,13.8),(191,15.8),(193,15.8)],0,97.8)
 p=union(p,front,rear,box(95.3,97.8,2.4,5.1,10.3,15.8),box(95.3,97.8,190.7,193,10.3,15.8))
 # Front button window; the outer front rail is relieved for its full stroke.
 p=p.cut(box(33.5,54.5,-.3,2.41,10.4,16))
 # The hook lives at the front corner, entirely ahead of the board slide path.
 p=union(p,box(0,6,-14,2.4,0,10.3))
 if side=='right':p=mirror(p)
 p=pip_hinges(base.hinged(p,'tray-'+side,0,1.2),side)
 if side=='right':p=union(p,fold(hook_keeper(),180))
 else:p=union(p,hook_pivot_mount()).cut(hook_pivot_passage()).clean()
 # Main folding pivots print captive; no inserted main pins or glue.
 return p.clean().fix()

def axle_cap():
 # Bonded filament-pin collar. Through bore avoids a closed-floor transition.
 p=box(-3.5,3.5,-3.5,3.5,0,4)
 return p.cut(cq.Solid.makeCylinder(CAP_BORE_D/2,4.02,cq.Vector(0,0,-.01))).clean()

def parts():
 import flat_capstones
 return {**{f'{kind}-{side}':globals()[kind](side) for side in ('left','right') for kind in ('housing','board')},'capstone-cat':flat_capstones.capstone('cat'),'capstone-witch':flat_capstones.capstone('witch'),'side-hook':side_hook(),'axle-end-cap':axle_cap()}
