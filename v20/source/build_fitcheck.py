"""Optional front-section rail/catch check cut from the full exported V20 parts."""
from pathlib import Path
import hashlib,json,shutil,sys
import cadquery as cq
import trimesh
import case as c
import package_case as pkg
import slice_case as slicer
OUT=c.OUT

def render_layers():
 import inspect_case_layers as layers
 stage=OUT/'.slicer-work/fit-check'
 (stage/'previews').mkdir(exist_ok=True)
 layers.OUT=stage;layers.WORK=stage/'.slicer-work'
 layers.PLANS={'rail-and-catch-fit-check':[.2,1.2,2.2,3.2,5.6,6.2,9.2,10.6,11.8]}
 layers.main()
 shutil.copy2(stage/'previews/rail-and-catch-fit-check-layers.png',OUT/'FIT-CHECK/layers.png')
 shutil.copy2(stage/'reports/layer-inspection.json',OUT/'reports/fit-check-layers.json')

def main():
 stage=OUT/'.slicer-work/fit-check'
 for name in ['plates','reports','profiles']:(stage/name).mkdir(parents=True,exist_ok=True)
 for p in (OUT/'profiles').glob('*.json'):shutil.copy2(p,stage/'profiles'/p.name)
 dest=OUT/'FIT-CHECK';dest.mkdir(exist_ok=True)
 items=[];checks=[]
 inputs={}
 for part,name,x,rotate in [('housing-left','fit-base',7,False),('lid-left','fit-lid',117,True)]:
  source=OUT/'models'/f'{part}.step';inputs[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
  s=cq.importers.importStep(str(source)).val()
  crop=c.box(0,97.8,0,65,-.1,30) if part=='housing-left' else c.box(-1,100,-5,65,-.1,30)
  s=s.intersect(crop).clean()
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
 (OUT/'reports/fit-check.json').write_text(json.dumps({'checks':checks,'source_STEP_sha256':inputs,'slicing':sliced,'scope':'Front 65 mm of actual left base/lid. Tests matching rail and thumb catch only, not full-length warp, rear stop, hinge or transport. No change in rail/catch dimensions.','physical_acceptance':False},indent=2)+'\n')
 shutil.copy2(stage/'reports/rail-and-catch-fit-check-slice.log',OUT/'reports/rail-and-catch-fit-check-slice.log')
 render_layers()
 print('Optional fit check ready',row['slice_metadata']['prediction'],row['slice_metadata']['weight'])
if __name__=='__main__':main()
