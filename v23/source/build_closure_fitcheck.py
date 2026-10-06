"""Small actual-geometry closure trial with clearly identified fixture additions."""
import hashlib,json,shutil,sys
from pathlib import Path
import cadquery as cq
import trimesh
import case as c
import package_case as pkg
import slice_case as slicer
from build_case import ov
OUT=c.OUT;NAME='recessed-closure-fit-check'

def main():
 stage=OUT/'.slicer-work/closure-fit';dest=OUT/'CLOSURE-FIT';dest.mkdir(exist_ok=True)
 for name in ['models','plates','reports','profiles','previews']:(stage/name).mkdir(parents=True,exist_ok=True)
 for p in (OUT/'profiles').glob('*.json'):shutil.copy2(p,stage/'profiles'/p.name)
 source={};parts={};checks=[]
 def check(name,passed,detail=None):
  checks.append({'name':name,'pass':bool(passed),'detail':detail});assert passed,(name,detail)
 for side in ['left','right']:
  for kind in ['housing','board']:
   name=kind+'-'+side;path=OUT/'models'/(name+'.step');source[name]=hashlib.sha256(path.read_bytes()).hexdigest()
   s=cq.importers.importStep(str(path)).val();crop=c.box(-.1,14,68 if kind=='housing' else 73.5,124 if kind=='housing' else 118.5,-.1,17)
   if side=='right':crop=c.mirror(crop)
   s=s.intersect(crop)
   if kind=='housing':
    fixture=c.union(c.box(11.4,14,68,73,2.19,16.3),c.box(11.4,14,119,124,2.19,16.3),c.box(11.5,14,73.5,118.5,2.19,10.6))
    if side=='right':fixture=c.mirror(fixture)
    s=c.union(s,fixture)
   parts[name]=s
 for name in ['side-hook','axle-end-cap']:
  path=OUT/'models'/(name+'.step');source[name]=hashlib.sha256(path.read_bytes()).hexdigest();parts[name]=cq.importers.importStep(str(path)).val()
 for name,s in parts.items():
  check(name+' valid single solid',s.isValid() and len(s.Solids())==1)
  cq.exporters.export(s,str(dest/(name+'.step')));cq.exporters.export(s,str(dest/(name+'.stl')),tolerance=.04,angularTolerance=.12)
  m=trimesh.load(dest/(name+'.stl'),force='mesh');r=cq.importers.importStep(str(dest/(name+'.step'))).val()
  check(name+' STEP/STL readback',r.isValid() and abs(r.Volume()-s.Volume())<.01 and m.is_watertight and m.is_winding_consistent and m.body_count==1)
  shutil.copy2(dest/(name+'.step'),stage/'models'/(name+'.step'))
 closed={n:c.fold(s,180) if n.endswith('-right') else s for n,s in parts.items() if n!='axle-end-cap'};closed.update(c.hook_hardware())
 for i,(n,s) in enumerate(closed.items()):
  for m,t in list(closed.items())[i+1:]:check(n+'/'+m+' disjoint in closed fixture',ov(s,t)<1e-5)
 check('fixture retains exact keeper engagement',ov(parts['side-hook'],c.open_from_closed(closed['housing-right'],1))>1)
 check('fixture retains reverse stop',ov(c.side_hook(-8),parts['housing-left'])>.01)
 for a in range(91):check('release '+str(a),max(ov(c.side_hook(a),s) for n,s in closed.items() if n!='side-hook')<1e-5)
 pkg.OUT=stage;pkg.e.OUT=stage
 items=[pkg.place('housing-left',7,7),pkg.place('housing-right',32,7),pkg.place('board-left',57,7),pkg.place('board-right',82,7),pkg.place('side-hook',107,7,((0,1,0),90)),pkg.place('axle-end-cap',149,7)]
 pkg.e.plate(NAME,items);pkg.housing_support_clearance(NAME,items);checks+=pkg.checks
 slicer.OUT=stage;slicer.WORK=stage/'.slicer-work';sys.argv=[sys.argv[0]];slicer.main()
 slicing=json.loads((stage/'reports/slicing.json').read_text());row=slicing['plates'][NAME]
 check('CC2 slice and exact named mesh readback',row['passed'])
 shutil.copy2(stage/'PRINT'/row['project'],dest/row['project']);shutil.copy2(stage/'plates'/(NAME+'.3mf'),dest/(NAME+'-geometry.3mf'))
 shutil.copy2(stage/'reports'/(NAME+'-slice.log'),OUT/'reports'/(NAME+'-slice.log'))
 import inspect_case_layers as layers
 layers.OUT=stage;layers.WORK=stage/'.slicer-work';layers.PLANS={NAME:[.2,1.2,2.2,3.4,5.8,7.8,9.8,10.6,14.8,16.2]};layers.main()
 shutil.copy2(stage/'previews'/(NAME+'-layers.png'),dest/'layers.png');shutil.copy2(stage/'reports/layer-inspection.json',OUT/'reports/closure-fit-layers.json')
 report={'checks':checks,'source_STEP_sha256':source,'slicing':slicing,'scope':'Actual cropped housing and board edges, full hook/collar. Fixture-only rear pillars establish the 32.6 mm closed alignment and rear ledges support cropped board edges; these are not full-case features. Not a full-case warping, hinge, slider-latch, storage or transport test.','physical_acceptance':False}
 (OUT/'reports/closure-fit.json').write_text(json.dumps(report,indent=2)+'\n');print('Closure fit project PASS',row['slice_metadata']['prediction'],row['slice_metadata']['weight'])
if __name__=='__main__':main()
