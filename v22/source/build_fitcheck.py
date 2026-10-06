"""Optional captive-hinge trial cropped from both actual exported bases."""
from pathlib import Path
import hashlib,json,shutil,sys
import cadquery as cq
import trimesh
import case as c
import package_case as pkg
import slice_case as slicer
from build_case import ov
OUT=c.OUT
NAME='captive-hinge-fit-check'

def section(s,side):
 front=s.intersect(c.box(88,108,-.1,11,-.1,60))
 rear=s.intersect(c.box(88,108,189,200.1,-.1,60)).translate((0,-175,0))
 bridge=c.box(90,92,9,16,0,1.2)
 if side=='right':bridge=c.mirror(bridge)
 return c.union(front,rear,bridge).clean()

def main():
 stage=OUT/'.slicer-work/fit-check'
 for name in ['plates','reports','profiles','previews']:(stage/name).mkdir(parents=True,exist_ok=True)
 for p in (OUT/'profiles').glob('*.json'):shutil.copy2(p,stage/'profiles'/p.name)
 dest=OUT/'FIT-CHECK';dest.mkdir(exist_ok=True)
 inputs={};shapes={};checks=[]
 for side in ('left','right'):
  source=OUT/'models'/f'housing-{side}.step';inputs[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
  s=section(cq.importers.importStep(str(source)).val(),side);shapes[side]=s
  assert s.isValid() and len(s.Solids())==1
  name='hinge-'+side
  cq.exporters.export(s,str(dest/f'{name}.step'))
  cq.exporters.export(s,str(dest/f'{name}.stl'),tolerance=.04,angularTolerance=.12)
  restored=cq.importers.importStep(str(dest/f'{name}.step')).val();mesh=trimesh.load(dest/f'{name}.stl',force='mesh')
  assert restored.isValid() and abs(restored.Volume()-s.Volume())<.01
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1 and mesh.volume>0
  checks.append({'name':name+' valid single solid and STEP/STL readback','pass':True})
 for name,passed in [
  ('two disjoint captive parts',ov(shapes['left'],shapes['right'])<1e-5),
  ('full fold at 5 degree samples',all(ov(shapes['left'],c.fold(shapes['right'],a))<1e-5 for a in range(0,181,5))),
  ('opposed pins block axial removal',all(ov(shapes['left'],shapes['right'].translate((0,y,0)))>1 for y in (-3,3))),
 ]:
  assert passed,name
  checks.append({'name':name,'pass':bool(passed)})
 bounds=cq.Compound.makeCompound(list(shapes.values())).BoundingBox();shift=(7-bounds.xmin,7-bounds.ymin,0)
 items=[('hinge-'+side,s.translate(shift)) for side,s in shapes.items()]
 pkg.OUT=stage;pkg.e.OUT=stage;pkg.e.plate(NAME,items);pkg.housing_support_clearance(NAME,items);checks+=pkg.checks
 slicer.OUT=stage;slicer.WORK=stage/'.slicer-work';slicer.REPO=c.REPO
 sys.argv=[sys.argv[0]];slicer.main()
 source=stage/'PRINT'/f'{NAME}-CC2-PLA.3mf';shutil.copy2(source,dest/source.name)
 shutil.copy2(stage/'plates'/f'{NAME}.3mf',dest/f'{NAME}-geometry.3mf')
 sliced=json.loads((stage/'reports/slicing.json').read_text());row=sliced['plates'][NAME]
 checks.append({'name':'CC2 slice and exact named-mesh readback','pass':row['passed']})
 (OUT/'reports/fit-check.json').write_text(json.dumps({'checks':checks,'source_STEP_sha256':inputs,'slicing':sliced,'print_translation_mm':shift,'rear_station_shift_mm':-175,'scope':'Actual front/rear hinge cross-sections cropped from exported bases, rear moved 175 mm forward. Added connecting strips. Tests captive-joint release and rotation, not full-base warp, board sliders, capstone fit or transport.','physical_acceptance':False},indent=2)+'\n')
 shutil.copy2(stage/'reports'/f'{NAME}-slice.log',OUT/'reports'/f'{NAME}-slice.log')
 import inspect_case_layers as layers
 layers.OUT=stage;layers.WORK=stage/'.slicer-work'
 ax=c.base.AX[1];layers.PLANS={NAME:[.2,1.2,ax-3,ax-1.9,ax-1.5,ax-.9,ax+.1,ax+1.5,ax+1.9,ax+3]};layers.main()
 shutil.copy2(stage/'previews'/f'{NAME}-layers.png',OUT/'FIT-CHECK/layers.png')
 shutil.copy2(stage/'reports/layer-inspection.json',OUT/'reports/fit-check-layers.json')
 print('Optional captive-hinge trial ready',row['slice_metadata']['prediction'],row['slice_metadata']['weight'])
if __name__=='__main__':main()
