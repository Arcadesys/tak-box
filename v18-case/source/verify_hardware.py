"""Verify permanent steel axles and bonded end caps against exported case CAD."""
from pathlib import Path
import json
import cadquery as cq
import case as c
OUT=c.REPO/'v18-case'
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap'}
cap=cq.importers.importStep(str(OUT/'models/axle-end-cap.step')).val()
hardware={
 'steel-main-axle-front':cq.Solid.makeCylinder(1.5,24.9,cq.Vector(98,-20.5,16.3),cq.Vector(0,1,0)),
 'steel-main-axle-rear':cq.Solid.makeCylinder(1.5,24.9,cq.Vector(98,194.4,16.3),cq.Vector(0,1,0)),
 'steel-hatch-axle':cq.Solid.makeCylinder(1.5,92,cq.Vector(-2.5,219.8,23.2),cq.Vector(1,0,0)),
}
for name,y,angle in [('front-a',-22.5,-90),('rear-b',221.3,90)]:
 hardware['retention-cap-'+name]=cap.rotate((0,0,0),(1,0,0),angle).translate((98,y,16.3))
hardware['retention-cap-hatch-a']=cap.rotate((0,0,0),(0,1,0),90).translate((-4.5,219.8,23.2))
hardware['retention-cap-hatch-b']=cap.rotate((0,0,0),(0,1,0),-90).translate((91.5,219.8,23.2))
checks=[]
def ov(a,b):
 x,y=a.BoundingBox(),b.BoundingBox()
 if any(getattr(x,k+'max')<=getattr(y,k+'min')+1e-7 or getattr(y,k+'max')<=getattr(x,k+'min')+1e-7 for k in 'xyz'):return 0
 return max(0,a.intersect(b).Volume())
for pose in ('open','closed'):
 case={n:(c.fold(s,180) if pose=='closed' and n.endswith('-right') else s) for n,s in parts.items()}
 for n,h in hardware.items():
  volumes={m:ov(h,s) for m,s in case.items()};passed=max(volumes.values())<1e-5
  checks.append({'name':pose+'/'+n,'pass':passed,'overlap_mm3':volumes})
  assert passed,(pose,n,volumes)
 compound=cq.Compound.makeCompound(list(case.values())+list(hardware.values()))
 cq.exporters.export(compound,str(OUT/'models'/f'assembly-{pose}-with-hardware.step'))
 if pose=='closed':
  b=compound.BoundingBox();envelope=[b.xlen,b.ylen,b.zlen]
cq.exporters.export(cq.Compound.makeCompound(list(hardware.values())),str(OUT/'models/hardware-reference-NOT-PRINTED.step'))
report={'checks':checks,'closed_envelope_including_hardware_mm':envelope,'steel_axles_mm':{'diameter':3,'front_length':24.9,'rear_length':24.9,'hatch_length':92},'printed_retention_caps':4,'endplay_gap_mm':.5,'rod_in_cap_depth_mm':2,'retention':'Bond end caps to steel rods; keep adhesive out of rotating barrels. Confirm actual stack-up before bonding.','physical_acceptance':False,'note':'Axles are permanent hinge hardware, not a closure pin. No steel-reference objects are included in print plates.'}
(OUT/'reports/hardware.json').write_text(json.dumps(report,indent=2)+'\n')
print('Hardware readback PASS',envelope)
