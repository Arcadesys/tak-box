"""Actual-CAD closure and hinge-end trials, before full-build verification."""
import json
import cadquery as cq
import case as c
from build_case import ov
from render_utils import render
OUT=c.OUT
DEST=OUT/'.slicer-work/exterior-trial';DEST.mkdir(parents=True,exist_ok=True)

def main():
 p=c.parts();checks=[]
 def check(name,passed,detail=None):
  checks.append({'name':name,'pass':bool(passed),'detail':detail})
  print(name,'PASS' if passed else 'FAIL',detail,flush=True)
 closed_right=c.fold(p['housing-right'],180)
 for n,s in p.items():check(n+' valid single solid',s.isValid() and len(s.Solids())==1)
 closed=[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in p.items() if n!='axle-end-cap' and not n.startswith('capstone-')]+list(c.hook_hardware().items())
 for n in ['side-hook']:
  b=p[n].BoundingBox();check('hook inside closed side outline',b.xmin>=0 and b.zmin>=0 and b.zmax<=32.6)
 for n,s in c.hook_hardware().items():check(n+' inside closed side outline',s.BoundingBox().xmin>=-1e-6)
 for angle in range(0,91):
  moving=c.side_hook(angle)
  worst=max(ov(moving,s) for n,s in closed if n not in ['side-hook','filament-hook-pivot','retention-cap-hook'])
  check('closure release '+str(angle),worst<1e-5,worst)
 check('locked keeper resists first degree of opening',ov(c.side_hook(),c.open_from_closed(closed_right,1))>1)
 check('reverse stop',ov(c.side_hook(-8),p['housing-left'])>.01)
 parked=c.side_hook(90).BoundingBox();check('parked hook above recess floor and below board',parked.zmin>=1.49 and parked.zmax<=10.0,[parked.zmin,parked.zmax])
 for side in ['left','right']:
  for t in range(0,107,2):
   s=c.slide(c.board(side,c.BOARD_RELEASE),side,t)
   worst=max(ov(s,obj) for obj in [p['housing-left'],p['housing-right'],c.side_hook(90),*c.hook_hardware().values()])
   check(side+' slide '+str(t),worst<1e-5,worst)
 for a in range(0,181,5):check('paired hinge fold '+str(a),ov(p['housing-left'],c.fold(p['housing-right'],a))<1e-5)
 for side in ['left','right']:
  crop=c.box(-.1,12,68,124,-.1,17)
  if side=='right':crop=c.mirror(crop)
  for kind in ['housing','board']:
   name=kind+'-'+side;shape=p[name].intersect(crop)
   check(name+' cropped closure trial connected',shape.isValid() and len(shape.Solids())==1)
   cq.exporters.export(shape,str(DEST/(name+'.step')))
 for name in ['side-hook','axle-end-cap']:cq.exporters.export(p[name],str(DEST/(name+'.step')))
 # Roundtrip STEP ensures these previews show exported trial geometry.
 crop=c.box(-.1,13,66,126,-.1,33)
 shapes=[]
 for n,s in closed:
  s=s.intersect(crop)
  if s.Volume()>1e-5:
   path=DEST/(n+'-closed.step');cq.exporters.export(s,str(path));restored=cq.importers.importStep(str(path)).val()
   shapes.append(('hardware' if n.startswith(('filament','retention')) else n,restored))
 render('10-exterior-trial-closed',shapes,'V23 centered hook — all hardware within the side outline',(-500,-150,300))
 render('11-exterior-trial-open',[(n,c.hook_rotate(s,90) if n=='side-hook' else s) for n,s in shapes],'V23 hook parked — below the sliding board path',(-500,-150,300))
 (OUT/'reports/exterior-trial.json').write_text(json.dumps({'checks':checks,'scope':'Actual source geometry; closed closure STEP roundtrip renders, full hook and slide samples, hinge fold; physical acceptance unobserved.','physical_acceptance':False},indent=2)+'\n')
 assert all(row['pass'] for row in checks)
 print('Exterior mechanism trial PASS',flush=True)
if __name__=='__main__':main()
