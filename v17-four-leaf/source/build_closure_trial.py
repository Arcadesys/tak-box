"""Export an actual over-center linkage trial separately from the case study."""
from pathlib import Path
import json,math
import cadquery as cq
import closure_trial as c
import export_utils as e

OUT=Path(__file__).resolve().parents[1]
(OUT/'plates').mkdir(exist_ok=True)
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 print(name,ok,detail or '',flush=True)
e.check=check
parts=c.coupon()
for name,s in parts.items():
 check(name+' solid',s.isValid() and len(s.Solids())==1)
 cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 cq.exporters.export(s,str(OUT/'models'/f'{name}.stl'),tolerance=.08,angularTolerance=.15)
 stats=e.mesh_check(*e.read_stl(OUT/'models'/f'{name}.stl'))
 check(name+' mesh',all(stats[k] for k in ('closed','oriented','positive_volume','nondegenerate')),stats)
 b=s.BoundingBox();e.plate(name,[(name,s.translate((5-b.xmin,5-b.ymin,-b.zmin)))])

hook=parts['latch-hook'];keeper=parts['latch-keeper']
check('keeper and closed hook clear',hook.intersect(keeper).Volume()<1e-5)
check('positive hook blocks 0.25 mm keeper lift',hook.intersect(keeper.translate((0,0,.25))).Volume()>.01)
check('released hook clears keeper',c.hook_released(34).scale(.85).intersect(keeper).Volume()<1e-5)
o=c.O;a=c.crank();k=c.C
# Closed crank lies beyond the pivot/keeper dead-center line; preload is
# deliberately not claimed from nominal CAD contact alone.
cross=(k[0]-o[0])*(a[1]-o[1])-(k[1]-o[1])*(a[0]-o[0])
check('crank passes dead-center line',cross<0,cross)
e.render('04-closure-trial',[(s,col,1) for s,col in zip(parts.values(),('#444657','#d79849','#8a659e','#444657'))],'Direct over-center draw-latch trial; separate from body study')
(OUT/'reports'/'closure-trial.json').write_text(json.dumps({'checks':checks,'limitations':['Not integrated into four-leaf housing.','Permanent M2.5 pivot hardware required; no screws needed for routine opening.','Preload, stop strength, release comfort and cycling require physical trial.','Generic 3MF, not sliced.']},indent=2))
if any(not x['pass'] for x in checks):raise SystemExit('Closure trial has unresolved checks')
