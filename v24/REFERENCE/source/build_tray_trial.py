"""Small cropped seat/tray trial: three flats, capstone bay and pinch handle."""
import json,shutil,sys,hashlib
import cadquery as cq
import trimesh
import case as c
import package_case as pkg
import slice_case as slicer
import inspect_case_layers as layers
from geometry_utils import ov
OUT=c.OUT;NAME='removable-tray-access-trial'
def main():
 stage=OUT/'.slicer-work/tray-trial';dest=OUT/'TRAY-FIT'
 for d in ['plates','reports','profiles','previews']:(stage/d).mkdir(parents=True,exist_ok=True)
 for p in (OUT/'profiles').glob('*.json'):shutil.copy2(p,stage/'profiles'/p.name)
 window=c.box(9.5,91,139,193.1,0,20)
 source=OUT/'models/tray-left.step'
 tray=cq.importers.importStep(str(source)).val().intersect(window)
 seat=c.housing('left',False).intersect(window)
 checks=[];items=[]
 for name,s,x in [('seat-section',seat,7),('tray-section',tray,105)]:
  assert s.isValid() and len(s.Solids())==1
  path=dest/(name+'.step');cq.exporters.export(s,str(path));cq.exporters.export(s,str(path.with_suffix('.stl')),tolerance=.04,angularTolerance=.12)
  restored=cq.importers.importStep(str(path)).val();mesh=trimesh.load(path.with_suffix('.stl'),force='mesh')
  assert restored.isValid() and abs(restored.Volume()-s.Volume())<.01 and mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1
  checks.append({'name':name+' valid solid and STEP/STL readback','pass':True})
  b=s.BoundingBox();items.append((name,pkg.on_bed(s.translate((x-b.xmin,7-b.ymin,-b.zmin)))))
 assert all(ov(tray.translate((0,0,z)),seat)<1e-5 for z in (0,.2,1,2,4,8,16))
 checks.append({'name':'nominal seating and vertical removal','pass':True})
 pkg.OUT=stage;pkg.e.OUT=stage;pkg.e.plate(NAME,items);checks+=pkg.checks
 slicer.OUT=stage;slicer.WORK=stage/'.slicer-work';slicer.REPO=c.REPO;sys.argv=[sys.argv[0]];slicer.main()
 for a,b in [(stage/'PRINT'/f'{NAME}-CC2-PLA.3mf',dest/f'{NAME}-CC2-PLA.3mf'),(stage/'plates'/f'{NAME}.3mf',dest/f'{NAME}-geometry.3mf')]:shutil.copy2(a,b)
 sliced=json.loads((stage/'reports/slicing.json').read_text());checks.append({'name':'CC2 slice and exact mesh/placement readback','pass':sliced['plates'][NAME]['passed']})
 report={'checks':checks,'slicing':sliced,'source_tray_STEP_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_case_py_sha256':hashlib.sha256((OUT/'source/case.py').read_bytes()).hexdigest(),'scope':'Actual rear 54 mm of proposed tray and empty case seat. Three flat pockets, capstone bay and full pinch handle. Open-ended section has no full-case containment function. Does not qualify full-tray warping, raised shell/rails, closure or carry retention.','physical_acceptance':False}
 (OUT/'reports/tray-trial.json').write_text(json.dumps(report,indent=2)+'\n')
 layers.OUT=stage;layers.WORK=stage/'.slicer-work';layers.PLANS={NAME:[.2,.6,1.2,2.2,3.2,4,4.6,5.2,7,9.2,10.2]};layers.main()
 shutil.copy2(stage/'previews'/f'{NAME}-layers.png',dest/'layers.png');shutil.copy2(stage/'reports/layer-inspection.json',OUT/'reports/tray-trial-layers.json')
 print('Tray access trial ready',flush=True)
if __name__=='__main__':main()
