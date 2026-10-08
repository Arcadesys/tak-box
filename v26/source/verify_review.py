"""Audit exported V26 closure engagement and unchanged art/body interfaces."""
from pathlib import Path
import sys,json,hashlib,importlib.util
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
checks=[]
def load(n):return cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val()
def check(n,ok,d=None):
 checks.append(dict(name=n,pass_=bool(ok),detail=d));assert ok,(n,d)
def main():
 h={s:load('housing-design-'+s) for s in ('left','right')};hook=load('hook-design-closed');park=load('hook-design-parked')
 gap=park.distance(h['left']);check('exported hook minimum body clearance',gap>.39,dict(gap_mm=gap))
 for a in range(0,91,5):
  gap=b.c.hook_rotate(hook,a).distance(h['left']);check('exported hook own-body gap '+str(a),gap>.39,dict(gap_mm=gap))
 check('latched hook stops early case opening',any(b.ov(hook,b.c.fold(h['right'],a))>.1 for a in (179,178,177)),dict(overlap_mm3={a:b.ov(hook,b.c.fold(h['right'],a)) for a in (179,178,177)}))
 for side in h:
  parts={r:load('board-'+side+'-'+r) for r in b.ROLES}
  for role in ('grid','stars','orange','purple'):
   old=cq.importers.importStep(str(OUT/'reference/board-inlays'/f'board-{side}-{role}.step')).val()
   check(side+'/'+role+' retained inlay geometry',old.cut(parts[role]).Volume()<1e-5 and parts[role].cut(old).Volume()<1e-5)
  for i,(role,s) in enumerate(parts.items()):
   for other,t in list(parts.items())[i+1:]:check(side+'/'+role+'/'+other+' disjoint material',b.ov(s,t)<1e-5)
  old=cq.importers.importStep(str(OUT/'reference/plain-bodies'/f'housing-design-{side}.step')).val()
  g=b.guides(side);allowed=b.c.union(b.c.box(-.1,10,69,111,-.1,13),b.c.box(78,103,-.1,9.6,-.1,23),b.c.box(78,103,190.4,200.1,-.1,23))
  allowed=b.c.union(allowed,b.c.box(-.1,4.01,-.1,4.01,-.1,17.1),b.c.box(-.1,4.01,195.99,200.1,-.1,17.1))
  if side=='right':allowed=b.c.mirror(allowed)
  original=b.c.union(old,g)
  removed=original.cut(h[side]);added=h[side].cut(original)
  def outside(delta):return 0.0 if abs(delta.Volume())<1e-7 else delta.cut(allowed).Volume()
  check(side+' body modifications stay in main-hinge bays, hook mount and outer corner rounds',outside(removed)<1e-5 and outside(added)<1e-5)
 report=dict(passed=True,checks=checks,command=[sys.executable,str(Path(__file__).resolve())],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physical_acceptance=False,scope='Nominal exported CAD material and early opening obstruction; no physical retention force rating.')
 (OUT/'reports/review-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'exported review audits')
if __name__=='__main__':main()
