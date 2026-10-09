"""Verify 1.75 mm PLA filament axles and bonded end caps against exported case CAD."""
from pathlib import Path
import json
import cadquery as cq
import case as c
OUT=c.OUT
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap'}
cap=cq.importers.importStep(str(OUT/'models/axle-end-cap.step')).val()
hardware={
 'filament-main-axle-front':cq.Solid.makeCylinder(c.HINGE_PIN_D/2,24.9,cq.Vector(98,-20.5,16.3),cq.Vector(0,1,0)),
 'filament-main-axle-rear':cq.Solid.makeCylinder(c.HINGE_PIN_D/2,24.9,cq.Vector(98,194.4,16.3),cq.Vector(0,1,0)),
 'filament-hook-pivot':c.x_cylinder(c.HINGE_PIN_D/2,-8.8,.8,94,7),
 'filament-hatch-axle':cq.Solid.makeCylinder(c.HINGE_PIN_D/2,92,cq.Vector(-2.5,219.8,23.2),cq.Vector(1,0,0)),
}
for name,y,angle in [('front-a',-22.5,-90),('rear-b',221.3,90)]:
 hardware['retention-cap-'+name]=cap.rotate((0,0,0),(1,0,0),angle).translate((98,y,16.3))
hardware['retention-cap-hatch-a']=cap.rotate((0,0,0),(0,1,0),90).translate((-4.5,219.8,23.2))
hardware['retention-cap-hatch-b']=cap.rotate((0,0,0),(0,1,0),-90).translate((91.5,219.8,23.2))
hardware['retention-cap-hook']=cap.rotate((0,0,0),(0,1,0),90).translate((-10.8,94,7))
checks=[]
def ov(a,b):
 x,y=a.BoundingBox(),b.BoundingBox()
 if any(getattr(x,k+'max')<=getattr(y,k+'min')+1e-7 or getattr(y,k+'max')<=getattr(x,k+'min')+1e-7 for k in 'xyz'):return 0
 return max(0,a.intersect(b).Volume())
for pose in ('open','closed'):
 case={n:(c.fold(s,180) if pose=='closed' and n.endswith('-right') else c.side_hook(c.HOOK_OPEN_ANGLE) if pose=='open' and n=='side-hook' else s) for n,s in parts.items()}
 for n,h in hardware.items():
  volumes={m:ov(h,s) for m,s in case.items()};passed=max(volumes.values())<1e-5
  checks.append({'name':pose+'/'+n,'pass':passed,'overlap_mm3':volumes})
  assert passed,(pose,n,volumes)
 compound=cq.Compound.makeCompound(list(case.values())+list(hardware.values()))
 cq.exporters.export(compound,str(OUT/'models'/f'assembly-{pose}-with-hardware.step'))
 if pose=='closed':
  b=compound.BoundingBox();envelope=[b.xlen,b.ylen,b.zlen]
# Exported CAD must have a 2.0 mm passage, not the previous 3.4 mm bore.
def probe(name,part,clearance,wall):
 gap=ov(part,clearance);material=ov(part,wall)
 passed=gap<1e-5 and material>wall.Volume()*.99
 checks.append({'name':name,'pass':passed,'passage_overlap_mm3':gap,'wall_fraction':material/wall.Volume()})
 assert passed,(name,gap,material)
for side in ('left','right'):
 for kind in ('housing','board'):
  family=('tray' if kind=='housing' else 'board')+'-'+side
  for a,b in c.base.FAMILIES[family]:
   mid=(a+b)/2
   wall=c.base.cyly(1.1,mid-.5,mid+.5).cut(c.base.cyly(1.02,mid-.51,mid+.51))
   if kind in ('board','housing'):wall=wall.cut(c.box(96,100,mid-.51,mid+.51,17.0,18))
   probe(kind+'-'+side+f' bore at Y={mid}',parts[kind+'-'+side],c.base.cyly(.99,mid-.5,mid+.5),wall)
for name,x in [('housing-left',6),('housing-left',81),('capstone-hatch',43.5)]:
 wall=c.cylx(1.1,x-.5,x+.5).cut(c.cylx(1.02,x-.51,x+.51))
 if name=='housing-left':wall=wall.cut(c.box(x-.51,x+.51,218,222,23.9,25))
 else:wall=wall.cut(c.box(x-.51,x+.51,218,222,21,22.5))
 probe(name+f' hatch bore at X={x}',parts[name],c.cylx(.99,x-.5,x+.5),wall)
probe('hook pivot bore',parts['side-hook'],c.x_cylinder(.99,-6.5,-3.9,94,7),c.x_cylinder(1.1,-6.5,-3.9,94,7).cut(c.x_cylinder(1.02,-6.51,-3.89,94,7)))
probe('end cap 1.9 mm bore',cap,cq.Solid.makeCylinder(.94,1,cq.Vector(0,0,2)),cq.Solid.makeCylinder(1.05,1,cq.Vector(0,0,2)).cut(cq.Solid.makeCylinder(.97,1.02,cq.Vector(0,0,1.99))))

cq.exporters.export(cq.Compound.makeCompound(list(hardware.values())),str(OUT/'models/hardware-reference-NOT-PRINTED.step'))
report={'checks':checks,'closed_envelope_including_hardware_mm':envelope,'filament_axles_mm':{'material':'PLA','diameter':c.HINGE_PIN_D,'front_length':24.9,'rear_length':24.9,'hatch_length':92,'hook_pivot_length':9.6},'hinge_bore_mm':c.HINGE_BORE_D,'cap_bore_mm':c.CAP_BORE_D,'nominal_pin_diametral_clearance_mm':c.HINGE_BORE_D-c.HINGE_PIN_D,'printed_retention_caps':5,'hinge_endplay_gap_mm':.5,'hook_bearing_endplay_nominal_mm':0,'rod_in_cap_depth_mm':2,'retention':'Bond main pins only at the exposed outer housing barrels (left front, right rear); bond hatch pin at one fixed ear and hook pin at its fixed mount. Bond caps to pins. Keep adhesive out of moving joints. Hook collar lightly contacts its bearing face; other caps have 0.5 mm running gaps.','physical_acceptance':False,'note':'Filament references are assembly hardware only and excluded from print plates. The closure catch itself is a headed printed pin integrated into the housing.'}
(OUT/'reports/hardware.json').write_text(json.dumps(report,indent=2)+'\n')
print('Hardware readback PASS',envelope)
