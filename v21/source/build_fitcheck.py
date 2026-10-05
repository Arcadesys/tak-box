"""Optional compact rail/catch check using sections of the full exported V21 parts."""
from pathlib import Path
import hashlib,json,shutil,sys
import cadquery as cq
import trimesh
import case as c
import package_case as pkg
import slice_case as slicer
from build_case import ov
OUT=c.OUT

def render_layers():
 import inspect_case_layers as layers
 stage=OUT/'.slicer-work/fit-check'
 (stage/'previews').mkdir(exist_ok=True)
 layers.OUT=stage;layers.WORK=stage/'.slicer-work'
 layers.PLANS={'rail-and-catch-fit-check':[.2,1.2,2.2,3.2,4.6,5.6,10.4,13.8,15.8]}
 layers.main()
 shutil.copy2(stage/'previews/rail-and-catch-fit-check-layers.png',OUT/'FIT-CHECK/layers.png')
 shutil.copy2(stage/'reports/layer-inspection.json',OUT/'reports/fit-check-layers.json')

def section(s,part):
 front=s.intersect(c.box(-6 if part=='board-left' else 0,70,-1 if part=='board-left' else 0,20,-.1,30))
 rear=s.intersect(c.box(0,70,181,194.8,-.1,30)).translate((0,-160,0))
 bridge=c.box(0,70,19,22,10.6,15.3) if part=='board-left' else c.box(0,70,19,22,0,2.2)
 result=c.union(front,rear,bridge)
 if part=='board-left':result=c.union(result,c.box(-5,1,14,20,10.6,15.3))
 return result.clean()

def main():
 stage=OUT/'.slicer-work/fit-check'
 for name in ['plates','reports','profiles']:(stage/name).mkdir(parents=True,exist_ok=True)
 for p in (OUT/'profiles').glob('*.json'):shutil.copy2(p,stage/'profiles'/p.name)
 dest=OUT/'FIT-CHECK';dest.mkdir(exist_ok=True)
 items=[];checks=[]
 inputs={}
 for part,name,x,rotate in [('housing-left','fit-base',7,False),('board-left','fit-board',95,False)]:
  source=OUT/'models'/f'{part}.step';inputs[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
  s=cq.importers.importStep(str(source)).val()
  s=section(s,part)
  assert s.isValid() and len(s.Solids())==1,name
  cq.exporters.export(s,str(dest/f'{name}.step'))
  cq.exporters.export(s,str(dest/f'{name}.stl'),tolerance=.04,angularTolerance=.12)
  restored=cq.importers.importStep(str(dest/f'{name}.step')).val()
  mesh=trimesh.load(dest/f'{name}.stl',force='mesh')
  assert restored.isValid() and abs(restored.Volume()-s.Volume())<.01
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1 and mesh.volume>0
  checks.append({'name':name+' STEP/STL readback','pass':True})
  if rotate:s=s.rotate((0,0,0),(1,0,0),180)
  b=s.BoundingBox();s=s.translate((x-b.xmin,7-b.ymin,-b.zmin));items.append((name,s))
  checks.append({'name':name+' valid cropped single solid','pass':True})
 # Confirm both retained rail profiles and the catch in this shortened fixture.
 base=cq.importers.importStep(str(dest/'fit-base.step')).val()
 board=cq.importers.importStep(str(dest/'fit-board.step')).val()
 for name,passed in [
  ('coupon assembled disjoint',ov(board,base)<1e-5),
  ('coupon catch holds outward pull',ov(board.translate((-1,0,0)),base)>1),
  ('coupon rails hold lift',ov(board.translate((0,0,.6)),base)>1),
  ('coupon released slide',all(ov(section(c.board('left',c.BOARD_RELEASE),'board-left').translate((-t,0,0)),base)<1e-5 for t in range(0,81,4))),
 ]:
  assert passed,name
  checks.append({'name':name,'pass':bool(passed)})
 pkg.e.OUT=stage
 pkg.e.plate('rail-and-catch-fit-check',items)
 checks+=pkg.checks
 slicer.OUT=stage;slicer.WORK=stage/'.slicer-work';slicer.REPO=c.REPO
 sys.argv=[sys.argv[0]];slicer.main()
 source=stage/'PRINT/rail-and-catch-fit-check-CC2-PLA.3mf'
 shutil.copy2(source,dest/source.name)
 shutil.copy2(stage/'plates/rail-and-catch-fit-check.3mf',dest/'rail-and-catch-fit-check-geometry.3mf')
 sliced=json.loads((stage/'reports/slicing.json').read_text())
 row=sliced['plates']['rail-and-catch-fit-check']
 checks.append({'name':'CC2 slice and exact named-mesh readback','pass':row['passed']})
 (OUT/'reports/fit-check.json').write_text(json.dumps({'checks':checks,'source_STEP_sha256':inputs,'slicing':sliced,'scope':'X=0..70 front and rear sections from the actual left base/board; rear translated 160 mm forward and joined by a bridge. Rail cross-sections and catch dimensions unchanged; added fixture pull tab. Tests rail/catch fit, not full board warping, inner stops, hinge or loaded transport.','physical_acceptance':False},indent=2)+'\n')
 shutil.copy2(stage/'reports/rail-and-catch-fit-check-slice.log',OUT/'reports/rail-and-catch-fit-check-slice.log')
 render_layers()
 print('Optional fit check ready',row['slice_metadata']['prediction'],row['slice_metadata']['weight'])
if __name__=='__main__':main()
