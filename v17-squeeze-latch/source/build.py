from pathlib import Path
import hashlib,json,platform,sys
import cadquery as cq
import folio as c
import export_utils as e
OUT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 print(name,'PASS' if ok else 'FAIL',detail or '',flush=True)
e.check=check
parts={'A-squeeze-clip':c.male(),'B-socket':c.female()}
loaded={}
for name,s in parts.items():
 check(name+' valid single solid',s.isValid() and len(s.Solids())==1)
 cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 cq.exporters.export(s,str(OUT/'models'/f'{name}.stl'),tolerance=.08,angularTolerance=.15)
 loaded[name]=cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
 check(name+' STEP readback',loaded[name].isValid() and abs(loaded[name].Volume()-s.Volume())<.01)
 stats=e.mesh_check(*e.read_stl(OUT/'models'/f'{name}.stl'))
 check(name+' mesh',all(stats[k] for k in ('closed','oriented','positive_volume','nondegenerate')),stats)
a,b=parts.values()
check('locked parts clear',a.intersect(b).Volume()<1e-5)
check('shoulders block 0.5 mm withdrawal',a.translate((0,-.5,0)).intersect(b).Volume()>.1)
# Conservative geometric release envelope, not a simulation of elastic arms.
left=c.arm().translate((2.5,0,0));right=c.arm().mirror('YZ',(12,0,0)).translate((-2.5,0,0))
worst=0
for distance in range(0,34):
 for s in (left,right):worst=max(worst,s.translate((0,-distance,0)).intersect(b).Volume())
check('compressed arm envelopes can withdraw in 1 mm samples',worst<1e-5,worst)
check('central guide can withdraw',all(c.box(10.8,13.2,5,32,0,8).translate((0,-d,0)).intersect(b).Volume()<1e-5 for d in range(34)))
items=[]
for name,s,x in [('A-squeeze-clip',a,8),('B-socket',b,46)]:
 bb=s.BoundingBox();items.append((name,s.translate((x-bb.xmin,8-bb.ymin,-bb.zmin))))
aa,bb=[s.BoundingBox() for _,s in items]
check('plate gap at least 6 mm',bb.xmin-aa.xmax>=6)
e.plate('v17-simple-squeeze-latch',items)
e.render('assembled',[(loaded['A-squeeze-clip'],'#d6a343',1),(loaded['B-socket'],'#547082',.5)],'A clicks into B; squeeze the two side buttons to release')
e.render('print-plate',[(s,col,1) for (_,s),col in zip(items,('#d6a343','#547082'))],'One plate: A clip + B socket')
report={'checks':checks,'command':'python v17-squeeze-latch/source/build.py','python':sys.version,'cadquery':cq.__version__,'platform':platform.platform(),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},'limitations':['Separate hand-held latch trial, not integrated into the case.','Compressed envelopes do not prove elastic insertion/release, fatigue or force.','PETG proposed for the flexible clip; print fit and retention untested.','Generic unsliced 3MF; socket roof needs bridging/support review.']}
(OUT/'reports'/'checks.json').write_text(json.dumps(report,indent=2))
if any(not x['pass'] for x in checks):raise SystemExit('Unresolved latch checks')
