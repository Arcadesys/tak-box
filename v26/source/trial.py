"""Production-sized clip and captive-hook trials; robust floors, no print dispatch."""
from pathlib import Path
import importlib.util,json,sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mechanisms',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
c=b.c;checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,(name,detail)
b.b.check=check;b.b.e.check=check;b.b.pkg.check=check

def main():
 full=b.housing('left');hook=b.hook(90)
 fixture=c.union(full.intersect(c.box(0,15,68,122,0,18)),c.box(6.1,15,68,122,0,3.4))
 for a in range(0,91,2):check('trial hook rotation '+str(a),b.ov(b.hook(a),fixture)<1e-5)
 for dx in (-1,1):check('trial hook axial capture '+str(dx),b.ov(hook.translate((dx,0,0)),fixture)>.1)
 for name,s in [('hook-trial-fixture-design',fixture),('hook-trial-design',hook)]:cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 shift=(8,-60,0);items=[('hook-trial-fixture',fixture.translate(shift)),('hook-trial',hook.translate(shift))]
 for name,s in items:b.b.export(name,s)
 b.b.e.plate('01-V26-captive-hook-trial',items);b.b.pkg.OUT=OUT;b.b.pkg.housing_support_clearance('01-V26-captive-hook-trial',items)
 seat=full.intersect(c.box(0,66,0,17,0,18)).clean()
 clip=b.board_parts('left')['body'].intersect(c.box(0,62,0,16,11,18)).clean()
 check('clip trial retains full arm and root',b.board_catch().cut(clip).Volume()<1e-5)
 check('clip trial seat one solid',seat.isValid() and len(seat.Solids())==1)
 check('clip trial floor production 3.4mm',c.box(12,64,4,7,.1,3.39).cut(seat).Volume()<1e-5)
 check('clip seated clear',b.ov(clip,seat)<1e-5)
 check('clip blocks one millimetre withdrawal',b.ov(clip.translate((-1,0,0)),seat)>.1)
 released=b.board_parts('left',2.8)['body'].intersect(c.box(0,62,0,16,11,18))
 for d in range(0,64,2):check('released trial slide '+str(d),b.ov(released.translate((-d,0,0)),seat)<1e-5)
 for name,s in [('clip-trial-seat-design',seat),('clip-trial-board-design',clip)]:cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 items=[('clip-trial-seat',b.b.bed(seat,8,8)),('clip-trial-board',b.b.bed(clip,8,35))]
 for name,s in items:b.b.export(name,s)
 b.b.e.plate('02-V26-board-clip-trial',items)
 report=dict(passed=True,checks=checks,command=[sys.executable,str(Path(__file__).resolve())],hook_print_translation_mm=shift,clip_width_mm=2.4,root_width_mm=3.2,release_travel_mm=2.8,floor_mm=3.4,physical_acceptance=False,printer_started=False,limitations=['Trial fixture is thickened outside the hook envelope; whole-case stiffness and loaded transport are not tested.','Release poses are assumed geometry, not stress or force predictions.'])
 (OUT/'reports/trial-geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'mechanism trial checks')
if __name__=='__main__':main()
