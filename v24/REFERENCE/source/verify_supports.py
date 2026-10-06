"""Export-based material probes of hinge load paths; no strength simulation."""
import json
import cadquery as cq
import case as c
from geometry_utils import ov
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));print(name,ok,flush=True)
p={s:cq.importers.importStep(str(c.OUT/'models'/f'housing-{s}.step')).val() for s in ('left','right')}
for side,s in p.items():
 for a,b in c.base.FAMILIES['tray-'+side]:
  for z in (1,2.2,5,10,c.base.AX[1]-2.5):
   probe=c.box(90.1,97.7,a+.2,b-.2,z-.05,z+.05)
   if side=='right':probe=c.mirror(probe)
   check(f'{side} support {a} continuous width at Z{z}',probe.cut(s).Volume()<1e-6,{'probed_width_mm':7.6,'probed_axial_mm':b-a-.4})
 for a,b in c.base.FAMILIES['tray-'+side]:
  ring=c.base.cyly(4.05,a+.5,b-.5).cut(c.base.cyly(2.45,a+.49,b-.49))
  check(f'{side} journal {a} radial wall material',ring.cut(s).Volume()<1e-5,{'outer_radius_mm':4.5,'socket_radius_mm':2.4,'nominal_radial_wall_mm':2.1,'outer_edge_rounding_mm':.4,'probed_ring_thickness_mm':1.6})
check('opposed pivots block axial withdrawal',all(ov(p['left'],p['right'].translate((0,d,0)))>1 for d in (-3,3)))
# Compare actual board geometry with the predecessor only for compatibility.
old=cq.importers.importStep(str(c.REPO/'v23/models/board-left.step')).val().translate((0,0,1.2))
check('baseline board replacement required',ov(old,p['left'])>1e-5,{'overlap_mm3':ov(old,p['left'])})
report={'checks':[{('pass' if k=='pass_' else k):v for k,v in row.items()} for row in checks], 'physical_strength_verified':False,'limitations':['Material sections and motion cannot predict printed impact strength, layer adhesion or fatigue.','No fracture photo, fused-joint observation or measured force is available.','Original reported failure is attributed only to the thin bar carrying the hinge; exact location remains unknown.']}
(c.OUT/'reports/supports.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(x['pass_'] for x in checks)
