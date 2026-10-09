"""Verify revised exterior envelope, access margins and support wall probes."""
import json
import cadquery as cq
import case as c
from build_case import ov
OUT=c.OUT

def main():
 p={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts()}
 closed={n:c.fold(s,180) if n.endswith('-right') else s for n,s in p.items() if n!='axle-end-cap' and not n.startswith('capstone-')}
 closed.update(c.hook_hardware());checks=[]
 def check(name,passed,detail=None):
  checks.append({'name':name,'pass':bool(passed),'detail':detail})
  assert passed,(name,detail)
 boundary=c.box(0,101,0,200,0,32.6)
 for name,s in closed.items():
  outside=s.cut(boundary).Volume();check(name+' stays inside closed outline',outside<1e-5,outside)
 comp=cq.Compound.makeCompound(list(closed.values()));b=comp.BoundingBox()
 check('thin closed envelope',abs(b.zlen-32.6)<1e-5,[b.xlen,b.ylen,b.zlen])
 # A 12 mm thumb-pad clearance probe reaches the side well beside the hook.
 thumb=c.x_cylinder(6,-3,5.5,113,16.3)
 check('broad thumb access inside closure well',max(ov(thumb,s) for s in closed.values())<1e-5,{'probe_diameter_mm':12,'depth_inside_outline_mm':5.5,'well_width_mm':52,'well_height_mm':30.2})
 for side in ['left','right']:
  housing=p['housing-'+side];board=p['board-'+side]
  for y in c.GRIP_CENTERS:
   grip=c.x_cylinder(3.5,-2,5.5,y,6.5)
   if side=='right':grip=c.mirror(grip)
   check(side+' recessed finger clearance '+str(y),ov(grip,housing)<1e-5 and ov(grip,board)<1e-5,{'probe_diameter_mm':7,'grip_width_mm':30,'grip_depth_mm':7.2,'physical_grip_unobserved':True})
  wall=c.box(9.41,11.19,78,90,3,9)
  if side=='right':wall=c.mirror(wall)
  check(side+' closure backing wall at least 1.8 mm nominal',ov(wall,housing)>wall.Volume()*.999)
  floor=c.box(2,8,80,90,.01,1.19)
  if side=='right':floor=c.mirror(floor)
  check(side+' closure floor at least 1.2 mm nominal',ov(floor,housing)>floor.Volume()*.999)
  # The original full floor beneath pieces remains 2.2 mm thick.
  floor=c.box(13,30,12,28,.01,2.19)
  if side=='right':floor=c.mirror(floor)
  check(side+' piece floor remains 2.2 mm nominal',ov(floor,housing)>floor.Volume()*.999)
  exterior_x=0 if side=='left' else 196
  check(side+' board tabs removed',abs((board.BoundingBox().xmin if side=='left' else board.BoundingBox().xmax)-exterior_x)<1e-6)
 # Matching exterior planes at sample stations clear of the access wells.
 for y in [20,65,135,180]:
  for z in [4,8]:
   a=cq.Vector(.1,y,z);bb=cq.Vector(.1,y,32.6-z)
   check('flush opposite exterior faces '+str((y,z)),closed['housing-left'].isInside(a) and closed['housing-right'].isInside(bb))
 report={'checks':checks,'revision':'v22-seamless','closed_envelope_mm':[b.xlen,b.ylen,b.zlen],'baseline_envelope_mm':[111.8,220.2,32.6],'rounding_mm':{'outer_plan_corners':3,'outer_top_bottom_edges':.8,'hinge_root_plan_corners':1.4,'hinge_root_bottom_edges':.6,'journal_end_edges':.5,'closure_recess_corners':5,'finger_well_corners':4},'physical_acceptance':False,'limitations':'Clearance probes establish geometric access, not human comfort, snag resistance or retention force. Sampled flush faces do not constitute a full surface-tolerance inspection.'}
 (OUT/'reports/exterior.json').write_text(json.dumps(report,indent=2)+'\n');print('Exterior checks PASS',len(checks),report['closed_envelope_mm'])
if __name__=='__main__':main()
