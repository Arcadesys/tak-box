"""Verify 1.75 mm PLA filament axles and bonded end caps against exported case CAD."""
from pathlib import Path
import json
import cadquery as cq
import case as c
OUT=c.OUT
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap' and not n.startswith('capstone-')}
cap=cq.importers.importStep(str(OUT/'models/axle-end-cap.step')).val()
hardware={
 'filament-hook-pivot':c.x_cylinder(c.HINGE_PIN_D/2,-8.8,.8,-6,7),
}
hardware['retention-cap-hook']=cap.rotate((0,0,0),(0,1,0),90).translate((-10.8,-6,7))
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
probe('hook pivot bore',parts['side-hook'],c.x_cylinder(.99,-6.5,-3.9,-6,7),c.x_cylinder(1.1,-6.5,-3.9,-6,7).cut(c.x_cylinder(1.02,-6.51,-3.89,-6,7)))
probe('end cap 1.9 mm bore',cap,cq.Solid.makeCylinder(.94,1,cq.Vector(0,0,2)),cq.Solid.makeCylinder(1.05,1,cq.Vector(0,0,2)).cut(cq.Solid.makeCylinder(.97,1.02,cq.Vector(0,0,1.99))))

cq.exporters.export(cq.Compound.makeCompound(list(hardware.values())),str(OUT/'models/hardware-reference-NOT-PRINTED.step'))
report={'checks':checks,'closed_envelope_including_hardware_mm':envelope,'filament_axles_mm':{'material':'PLA','diameter':c.HINGE_PIN_D,'hook_pivot_length':9.6},'hinge_bore_mm':c.HINGE_BORE_D,'cap_bore_mm':c.CAP_BORE_D,'nominal_pin_diametral_clearance_mm':c.HINGE_BORE_D-c.HINGE_PIN_D,'printed_retention_caps':1,'hook_bearing_endplay_nominal_mm':0,'rod_in_cap_depth_mm':2,'retention':'Main folding pivots print captive and take no glue. Bond hook pin at its fixed mount. Bond caps to pins. Keep adhesive out of moving joints. The single hook collar lightly contacts its bearing face.','physical_acceptance':False,'note':'Filament references are assembly hardware only and excluded from print plates. The closure catch itself is a headed printed pin integrated into the housing.'}
(OUT/'reports/hardware.json').write_text(json.dumps(report,indent=2)+'\n')
print('Hardware readback PASS',envelope)
