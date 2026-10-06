"""Integrated v23 case, original Cat/Witch flats plus V23 flat capstones, mm. Flex poses are assumptions."""
from pathlib import Path
from functools import lru_cache
import sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parent
sys.path.insert(0,str(OUT/'source/vendor/body'))
import folio as base
box=base.box
mirror=base.mirror
def fold(s,a):return s.rotate((98,0,17.5),(98,1,17.5),-a)
base.AX=(98.,17.5)
TRAY_FLOOR=1.2
PIECE_Z=3.4
HINGE_PIN_D=1.75
HINGE_BORE_D=2.0
CAP_BORE_D=1.9
# V16-style opposed captive pivots: print both bases together, open flat.
base.L=200.0
base.FAMILIES={'tray-left':((4.9,9.2),(190.8,195.1)),'tray-right':((.2,4.5),(195.5,199.8))}
PRINT_BASE_SHIFT=(17,21,0)
PIP_PIN_R=2.0
PIP_CLEARANCE=.4
PIP_STATIONS=((4.5,4.9,1),(195.5,195.1,-1))
BOARD_RELEASE=2.8
BOARD_TRAVEL=106
HOOK_Y_SHIFT=8.25
HOOK_X_SHIFT=8.8
GRIP_CENTERS=(43.,157.)


def union(*shapes):
 s=shapes[0]
 for t in shapes[1:]:s=s.fuse(t)
 return s.clean()

def pip_pin(face,d):
 end=face+d*1.9
 pin=base.cyly(PIP_PIN_R,min(face,end),max(face,end))
 return union(pin,cq.Solid.makeCone(PIP_PIN_R,.5,.8,cq.Vector(98,end,base.AX[1]),cq.Vector(0,d,0)))

def pip_socket(mouth,d):
 end=mouth+d*2.0
 cavity=base.cyly(PIP_PIN_R+PIP_CLEARANCE,min(mouth-d*.05,end),max(mouth-d*.05,end))
 return union(cavity,cq.Solid.makeCone(PIP_PIN_R+PIP_CLEARANCE,.1,1.0,cq.Vector(98,end,base.AX[1]),cq.Vector(0,d,0)))

def pip_hinges(s,side):
 # The inherited helper supplies rooted barrels; fill its old axle passages.
 for a,b in base.FAMILIES['tray-'+side]:s=union(s,base.cyly(1.72,a,b))
 for face,mouth,d in PIP_STATIONS:
  s=union(s,pip_pin(face,d)) if side=='right' else s.cut(pip_socket(mouth,d))
 return s.clean()

# Recessed side hook rotates in YZ; X is its filament-pivot axis.
HOOK_AXIS=(3.6,100.8,5.8)
HOOK_OPEN_ANGLE=90

def x_cylinder(r,a,b,y,z):
 return cq.Solid.makeCylinder(r,b-a,cq.Vector(a,y,z),cq.Vector(1,0,0))

def hook_rotate(s,angle):
 return s.rotate(HOOK_AXIS,(4.6,100.8,5.8),angle)

def hook_pivot_passage():
 y,z=HOOK_AXIS[1:];h=1/(2**.5)
 roof=cq.Workplane('YZ').polyline([(y-h,z+h),(y+h,z+h),(y,z+2*h)]).close().extrude(4.61).val().translate((5.19,0,0))
 return union(x_cylinder(1,5.19,9.8,y,z),roof)

def hook_pivot_mount():
 return union(x_cylinder(4,5.2,9.6,100.8,5.8),box(5.6,9.6,96.8,104.8,1.8,5.8),box(2,9.6,104.4,107,1.2,3.4)).cut(hook_pivot_passage()).clean()

def hook_keeper():
 return union(x_cylinder(3.5,5.6,9.6,100.5,29.4),x_cylinder(1.5,1.6,5.8,100.5,29.4),x_cylinder(2.8,0,1.6,100.5,29.4))

@lru_cache(None)
def side_hook(angle=0):
 # Narrow load-bearing hook parks below the board; broad surrounding well
 # gives thumb access. The catch is behind the pivot in Y, seating on stop.
 yz=[(98,3.8),(104.9,3.8),(104.9,7.8),(101.8,7.8),(98.6,25.9),(98.6,31.4),(103,31.4),(103,33.5),(96.5,33.5),(96.5,24.9)]
 p=cq.Workplane('YZ').polyline(yz).close().extrude(3.2).val().translate((2,0,0))
 p=union(p,x_cylinder(4,2,5.2,100.8,5.8)).cut(x_cylinder(1,1.99,5.21,100.8,5.8)).clean()
 return hook_rotate(p,angle)

def open_from_closed(s,angle):
 return s.rotate((98,0,17.5),(98,1,17.5),angle)

def x_prism(points,x0,x1):
 # YZ section extruded along X: rails and board edges run sideways.
 return cq.Workplane('YZ').polyline(points).close().extrude(x1-x0).val().translate((x0,0,0))

def board_catch(release=0):
 def d(x):
  u=x/54
  return release*u*u*(3-u)/2
 pts=[(x,5.1+d(x)) for x in [54*i/40 for i in range(41)]]
 pts += [(x,6.3+d(x)) for x in [54*i/40 for i in range(40,-1,-1)]]
 arm=cq.Workplane('XY').workplane(offset=11.8).polyline(pts).close().extrude(4.7).val()
 return union(box(0,3,5.1,9.5,11.8,16.5),arm,box(34,54,.2+release,5.2+release,11.8,16.5))

@lru_cache(None)
def board(side,release=0):
 # One part is both playing surface and the sealed storage top.
 p=x_prism([(3.1,11.8),(192.3,11.8),(192.3,15.4),(191.2,16.5),(4.2,16.5),(3.1,15.4)],0,97.8)
 p=p.cut(box(3,57,2.9,9.5,11.7,16.6))
 p=union(p,board_catch(release),box(0,1.6,10,190,16.5,17.5))
 for y in GRIP_CENTERS:
  p=p.cut(round_box(-2,2.2,y-14,y+14,11.7,17.6,2.0,'Z'))
 p=p.cut(round_box(-.2,5.7,70,122,11.7,17.6,2.5,'Z'))
 p=p.cut(round_box(79,99,-1,9.6,11.7,18.2,1.3)).cut(round_box(79,99,190.4,201,11.7,18.2,1.3))
 # Stops lie outside the complete 180 mm field and block over-insertion.
 p=p.cut(box(95,98,2.9,5.4,11.7,16.6)).cut(box(95,98,190.4,192.4,11.7,16.6))
 for i in range(6):
  y=10+36*i
  p=p.cut(box(7.6,97.81,y-.4,y+.4,15.9,16.51))
 for x in (8,44,80):p=p.cut(box(x-.4,x+.4,9.6,190.4,15.9,16.51))
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
 s=s.translate((28.6-(b.xmin+b.xmax)/2,178.5-(b.ymin+b.ymax)/2,PIECE_Z))
 return s if side=='left' else mirror(s)

def round_box(x0,x1,y0,y1,z0,z1,r,axis='Z'):
 return cq.Workplane('XY').newObject([box(x0,x1,y0,y1,z0,z1)]).edges('|'+axis).fillet(r).val()

def closure_recess():
 # Complete closed-pose recess; cuts both halves at their common seam.
 return round_box(-.2,9.4,69.2,122,1.2,33.8,5,'X')

def rounded_hinges(p,side):
 # Full-height 8 mm radial roots replace the former 2.3 mm upper webs.
 # Opposite stations receive circular running relief for the entire root.
 for a,b in base.FAMILIES['tray-'+side]:
  root=box(90,98,a,b,0,base.AX[1])
  if side=='right':root=mirror(root)
  journal=cq.Workplane('XY').newObject([base.cyly(4.5,a,b)]).edges().fillet(.4).val()
  p=union(p,root,journal)
 for other,segments in base.FAMILIES.items():
  if other!='tray-'+side:
   for a,b in segments:p=p.cut(base.cyly((8**2+base.AX[1]**2)**.5+.45,a-.15,b+.15))
 for face,mouth,d in PIP_STATIONS:
  p=union(p,pip_pin(face,d)) if side=='right' else p.cut(pip_socket(mouth,d))
 return p.clean()

def tray_seat_stops():
 # Low solid ledges locate the removable floor within 0.4 mm in plan.
 return [box(12,88,6,8,2.19,3.2),box(12,88,190.9,193,2.19,3.2),
         box(88.2,89.6,35,50,2.19,3.2),box(88.2,89.6,145,160,2.19,3.2)]

@lru_cache(None)
def housing(side, fixed_pockets=False):
 outline=round_box(0,97.8,0,200,0,17.0,3)
 outline=cq.Workplane('XY').newObject([outline]).edges('<Z or >Z').fillet(.8).val()
 p=outline.intersect(box(-1,99,-1,201,0,11.5)).cut(box(2.4,89.5,2.4,193,2.2,30))
 p=union(p,*(pocket_rims()+[capstone_rim()] if fixed_pockets else tray_seat_stops()),outline.intersect(box(-1,99,0,2.4,11.5,17.2)),outline.intersect(box(-1,99,193,200,11.5,17.2)))
 front=x_prism([(2.4,15.0),(4.4,17.0),(2.4,17.0)],57,97.8)
 rear=x_prism([(193,15.0),(191,17.0),(193,17.0)],0,97.8)
 p=union(p,front,rear,box(95.3,97.8,2.4,5.1,11.5,17.0),box(95.3,97.8,190.7,193,11.5,17.0))
 p=p.cut(box(33.5,54.5,-.3,2.41,11.6,17.2))
 # Local wall stock replaces empty side margin; it does not enlarge the shell.
 p=union(p,box(0,11.2,68,124,0,11.5))
 for y in GRIP_CENTERS:
  p=union(p,box(0,11.2,y-17,y+17,0,11.5))
  p=p.cut(round_box(-.2,7.2,y-15,y+15,2.8,15.2,4,'X'))
 # Cut the closed recess from the relevant half before mirroring/folding.
 p=p.cut(closure_recess() if side=='left' else closure_recess().mirror('XY',(0,0,17.5)))
 # Keep the full rounded outer edge while clearing opposite hinge roots.
 p=p.cut(round_box(92.4,99,-1,9.3,11.5,17.7,1.3)).cut(round_box(92.4,99,190.7,201,11.5,17.7,1.3))
 p=p.intersect(outline)
 if side=='right':p=mirror(p)
 p=rounded_hinges(p,side)
 if side=='right':p=union(p,fold(hook_keeper(),180))
 else:p=union(p,hook_pivot_mount()).cut(hook_pivot_passage()).clean()
 return p.clean().fix()

def axle_cap():
 # Round 2 mm collar fits wholly inside the closure recess.
 return cq.Solid.makeCylinder(3.5,2).cut(cq.Solid.makeCylinder(CAP_BORE_D/2,2.02,cq.Vector(0,0,-.01))).clean()

def hook_hardware():
 return {'filament-hook-pivot':x_cylinder(HINGE_PIN_D/2,1,9.6,HOOK_AXIS[1],5.8),
 'retention-cap-hook':axle_cap().rotate((0,0,0),(0,1,0),90).translate((0,HOOK_AXIS[1],5.8))}

@lru_cache(None)
def tray(side):
 floor=round_box(11.6,87.8,8.4,190.5,2.2,PIECE_Z,1.5)
 rims=[s.translate((1,0,TRAY_FLOOR)) for s in pocket_rims()]+[capstone_rim().translate((1,-.5,TRAY_FLOOR))]
 handle=round_box(62,70,170,190,PIECE_Z-.01,PIECE_Z+8,1.5)
 p=union(floor,*rims,handle)
 return p if side=='left' else mirror(p)

def parts():
 import flat_capstones
 return {**{f'{kind}-{side}':globals()[kind](side) for side in ('left','right') for kind in ('housing','board','tray')},'capstone-cat':flat_capstones.capstone('cat'),'capstone-witch':flat_capstones.capstone('witch'),'side-hook':side_hook(),'axle-end-cap':axle_cap()}
