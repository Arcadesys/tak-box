from pathlib import Path
import hashlib,json,platform,sys
import cadquery as cq
import folio as c
import export_utils as e

OUT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 print(name, 'PASS' if ok else 'FAIL',detail or '',flush=True)

parts={}
for side in ('left','right'):
 for kind in ('housing','board','drawer'):
  name=kind+'-'+side; s=getattr(c,kind)(side);parts[name]=s
  check(name+' solid',s.isValid() and len(s.Solids())==1,len(s.Solids()))
parts['rear-cap-compartment']=c.cap_compartment()
for i,s in enumerate(c.axle_parts()): parts['common-axle-'+str(i)]=s
for name,s in parts.items():
 cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 cq.exporters.export(s,str(OUT/'models'/f'{name}.stl'),tolerance=.08,angularTolerance=.15)
 loaded=cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
 check(name+' STEP readback',loaded.isValid() and abs(loaded.Volume()-s.Volume())<.01)
 stats=e.mesh_check(*e.read_stl(OUT/'models'/f'{name}.stl'))
 check(name+' STL',all(stats[k] for k in ('closed','oriented','positive_volume','nondegenerate')),stats)

for side in ('left','right'):
 stones=c.stone_envelopes(side)
 for obstruction in ('housing','board','drawer'):
  volumes=[s.intersect(parts[obstruction+'-'+side]).Volume() for s in stones]
  check(side+' flats clear '+obstruction,max(volumes)<1e-5,max(volumes))
 check(side+' drawer clear housing',parts['drawer-'+side].intersect(parts['housing-'+side]).Volume()<1e-5)
for i,s in enumerate(c.cap_envelopes()):
 check('cap '+str(i)+' clears compartment',s.intersect(parts['rear-cap-compartment']).Volume()<1e-5)

left=[parts[n+'-left'] for n in ('housing','board','drawer')]
right=[parts[n+'-right'] for n in ('housing','board','drawer')]
worst=(0,None)
for angle in range(0,181,10):
 for i,a in enumerate(left+[parts['rear-cap-compartment']]):
  for j,b in enumerate(right):
   v=a.intersect(c.fold(b,angle)).Volume()
   if v>worst[0]:worst=(v,(angle,i,j))
check('paired right leaves fold 0..180 in 10 degree samples',worst[0]<1e-5,worst)
# Independent board access motion, with the housing roof still enclosing flats.
for side,sign in (('left',-1),('right',1)):
 worst=0
 for angle in range(0,91,10):
  b=c.fold(parts['board-'+side],angle*sign)
  worst=max(worst,b.intersect(parts['housing-'+side]).Volume())
 check(side+' independent board 0..90 degree samples',worst<1e-5,worst)

scene=[]
colors={'housing':'#363747','board':'#222435','drawer':'#9459a8'}
for side in ('left','right'):
 for kind in ('housing','board','drawer'):
  s=cq.importers.importStep(str(OUT/'models'/f'{kind}-{side}.step')).val()
  scene.append((s,colors[kind],1))
scene.append((parts['rear-cap-compartment'],'#725341',1))
e.render('01-open',scene,'v17: four independent leaves on a common hinge axis')
closed=[]
for side in ('left','right'):
 for kind in ('housing','board','drawer'):
  s=parts[kind+'-'+side]
  closed.append((s if side=='left' else c.fold(s,180),colors[kind],1))
closed.append((parts['rear-cap-compartment'],'#725341',1))
e.render('02-closed',closed,'Body-only fold study; closure and hatch development pending')
exploded=[]
for side in ('left','right'):
 exploded.extend([(parts['housing-'+side],colors['housing'],.3),(parts['board-'+side].translate((0,0,35)),colors['board'],1),(parts['drawer-'+side].translate((0,-80,0)),colors['drawer'],1)])
e.render('03-drawer-access',exploded,'Covered drawer housings; boards lifted only for visibility')
report={'checks':checks,'python':sys.version,'cadquery':cq.__version__,'platform':platform.platform(),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},'limitations':['Architecture study only: drawer latches/stops, rear hatch, board snaps and direct case closure not modeled.','Sampled motion does not establish continuous swept clearance or physical performance.','Capstones checked as conservative original envelopes, not detailed shapes.','No slicing or physical tests. No print plates released.']}
(OUT/'reports'/'study.json').write_text(json.dumps(report,indent=2))
if any(not x['pass'] for x in checks): raise SystemExit('Study has unresolved checks; read report.')
