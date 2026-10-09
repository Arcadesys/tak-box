"""Full-length, two-pivot PIP trial cut from actual replacement case bodies."""
from pathlib import Path
import importlib.util,json,sys,hashlib
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pip_build',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
c=b.c;checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,(name,detail)
b.check=check;b.b.check=check;b.b.e.check=check;b.b.pkg.check=check

def main():
 full={s:cq.importers.importStep(str(OUT/'models'/f'housing-design-{s}.step')).val() for s in ('left','right')}
 parts={s:v.intersect(c.box(76,120,0,200,-.1,24)).clean() for s,v in full.items()}
 for side,v in parts.items():
  check(side+' actual production hinge strip',v.isValid() and len(v.Solids())==1 and b.ov(v,full[side])>0 and v.cut(full[side]).Volume()<1e-5)
  probe=c.box(76.2,89.4,10,190,.1,3.39)
  if side=='right':probe=c.mirror(probe)
  check(side+' continuous 3.4mm floor and wide spine',abs(v.intersect(probe).Volume()-probe.Volume())<1e-5)
 for d in (-3,3):check('trial opposed axial capture '+str(d),b.ov(parts['left'],parts['right'].translate((0,d,0)))>1)
 for face,mouth,d in c.PIP_STATIONS:check('trial captive pivot clearance '+str(face),c.pip_pin(face,d).distance(parts['left'])>.39)
 for angle in range(0,181,2):check('trial fold '+str(angle),b.ov(parts['left'],c.fold(parts['right'],angle))<1e-5)
 items=[]
 for side,v in parts.items():
  name='trial-hinge-'+side;cq.exporters.export(v,str(OUT/'models'/f'{name}-design.step'))
  model=v.translate(c.PRINT_BASE_SHIFT);b.b.export(name,model);items.append((name,model))
 b.b.e.plate('02-V25-PIP-hinge-trial',items);b.b.pkg.OUT=OUT;b.b.pkg.housing_support_clearance('02-V25-PIP-hinge-trial',items)
 report=dict(passed=True,checks=checks,printed_parts=2,physical_acceptance=False,printer_started=False,command=[sys.executable,str(Path(__file__).resolve())],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),floor_mm=3.4,spine_probe_width_mm=13.2,length_mm=200,scope='Exact production hinge ends plus a continuous production-thickness spine. Does not qualify loaded complete-case durability.')
 (OUT/'reports/trial-geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'full-length PIP strip checks')
if __name__=='__main__':main()
