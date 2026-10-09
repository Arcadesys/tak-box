"""Three-knuckle V25 strength coupon. Filament hardware is never printed."""
from pathlib import Path
import sys,json,math,hashlib,platform,importlib.util
import cadquery as cq
import numpy as np
OUT=Path(__file__).resolve().parents[1];V25=OUT.parent
spec=importlib.util.spec_from_file_location('coupon_common',V25/'source/build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
c=b.c;ov=b.ov
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,(name,detail)
b.OUT=OUT;b.check=check;b.e.OUT=OUT;b.e.check=check
R=max(math.hypot(8,17.5),math.hypot(98-88.2,17.5-2.19))+.45
b.ROUND_RELIEF_R=R
FIXED=((.3,2.8),(6.8,9.3));MOVING=((3.2,6.4),)
def hinge(side,gap,label=''):
 s=c.housing(side).intersect(c.box(76,120,0,26,-.1,30))
 cut=c.box(90.1,120,-.1,26.1,-1,31)
 if side=='right':cut=c.mirror(cut)
 s=s.cut(cut)
 floor=c.box(76,90.2,0,26,0,2.2)
 if side=='right':floor=c.mirror(floor)
 s=c.union(s,floor)
 own=FIXED if side=='left' else MOVING;other=MOVING if side=='left' else FIXED
 for a,z in own:
  root=c.box(90,98,a,z,0,17.5)
  gusset=cq.Workplane('XZ').polyline([(88.2,2.19),(90.2,10.5),(90.2,2.19)]).close().extrude(z-a).val().translate((0,z,0))
  if side=='right':root=c.mirror(root);gusset=c.mirror(gusset)
  journal=cq.Workplane('XY').newObject([b.cy(4.5,a,z)]).edges().fillet(.4).val()
  bore=1.95 if side=='left' else 1.75+gap
  s=c.union(s,root,gusset,journal).cut(b.cy(bore/2,a-.02,z+.02))
 if side=='left':
  # Recesses for heads formed from the filament itself, not printed caps.
  s=s.cut(b.cy(1.75,.28,1.0)).cut(b.cy(1.75,8.6,9.32))
 for a,z in other:s=s.cut(b.cy(R,a-.15,z+.15))
 if label:
  mark=cq.Workplane('XY').workplane(offset=2.19).text(label,3,.5,combine=False).val().translate((81 if side=='left' else 115,4,0));s=c.union(s,mark)
 return s.clean()
def raw_filament():return b.cy(.875,.3,9.3)
def headed_filament():return c.union(b.cy(.875,.9,8.7),b.cy(1.6,.3,.9),b.cy(1.6,8.7,9.3))
def main():
 items=[];specs={}
 left_board=b.rounded_board('left');right_board=b.rounded_board('right')
 original=c.board('left');original_right=c.board('right');tray_l=c.tray('left');tray_r=c.tray('right');field=c.box(76,97.8,10,26,11.8,16.5)
 check('local flat playing-field material unchanged',left_board.intersect(field).cut(original).Volume()<1e-5 and original.intersect(field).cut(left_board).Volume()<1e-5)
 pin=headed_filament();raw=raw_filament()
 for i,gap in enumerate((.2,.35,.5)):
  key=f'S{i+1}';left=hinge('left',gap,key);right=hinge('right',gap,key)
  check(key+' static tray clearance',all(ov(t,s)<1e-5 for t in (tray_l,tray_r) for s in (left,right,pin)))
  check(key+' filament runs clear',ov(pin,left)<1e-5 and ov(pin,right)<1e-5)
  check(key+' both formed heads block axial escape',ov(left,pin.translate((0,.25,0)))>.1 and ov(left,pin.translate((0,-.25,0)))>.1)
  check(key+' raw filament unretained without both formed heads',all(ov(s,raw.translate((0,d,0)))<1e-5 for s in (left,right) for d in (-1.,1.)))
  check(key+' double supported moving bearing',abs(MOVING[0][0]-FIXED[0][1]-.4)<1e-9 and abs(FIXED[1][0]-MOVING[0][1]-.4)<1e-9)
  for a,z in FIXED:
   probe=c.box(90.5,96,a+.2,z-.2,2.4,11.5)
   check(key+f' fixed rooted bearing {a}',abs(left.intersect(probe).Volume()-probe.Volume())<1e-5)
  for angle in range(0,181,2):
   moving=c.fold(right,angle);board=c.fold(right_board,angle)
   check(f'{key} joint sweep {angle}',ov(left,moving)<1e-5 and ov(pin,moving)<1e-5)
   check(f'{key} actual V24 board clearance {angle}',all(ov(original,s)<1e-5 and ov(c.fold(original_right,angle),s)<1e-5 for s in (left,moving,pin)))
   check(f'{key} actual tray fold clearance {angle}',all(ov(tray_l,s)<1e-5 and ov(c.fold(tray_r,angle),s)<1e-5 for s in (left,moving,pin)))
   check(f'{key} curved board sweep {angle}',ov(left_board,board)<1e-5 and all(ov(left_board,s)<1e-5 and ov(board,s)<1e-5 for s in (left,moving,pin)))
  for side,s,x in [('fixed',left,8+i*60),('moving',right,35+i*60)]:
   name=key+'-'+side;model=b.bed(s,x,8);specs[name]=b.export(name,model);items.append((name,model))
  cq.exporters.export(cq.Compound.makeCompound([left,right,pin]),str(OUT/'models'/f'{key}-assembly.step'))
  specs[key]=dict(fixed_bores_mm=1.95,moving_bore_mm=1.75+gap,fixed_segments_mm=FIXED,moving_segments_mm=MOVING,barrel_d_mm=9,root_width_mm=8,gusset_x_start_mm=88.2,nominal_filament_d_mm=1.75,formed_head_d_mm=3.2,formed_head_thickness_mm=.6,head_recess_d_mm=3.5,head_axial_clearance_mm=.1,finished_axle_length_mm=9,raw_stock_volume_equivalent_length_mm=11.812244897959183,retention='Two formed filament heads; physical forming and pull strength unverified',printed_pin=False)
 for side,x in [('left',8),('right',40)]:
  name='BOARD-'+side;s=b.bed(b.rounded_board(side),x,46);specs[name]=b.export(name,s);items.append((name,s))
 for i,(name,s) in enumerate(items):
  v,_=b.pkg.welded_mesh(s);lo=v.min(axis=0);hi=v.max(axis=0)
  check(name+' on 256mm bed',min(lo[:2])>=0 and max(hi[:2])<=256 and lo[2]>=-1e-5)
  for name2,t in items[i+1:]:check(name+' plate separation '+name2,ov(s,t)<1e-5)
 b.e.plate('01-V25-strength-hinges',items)
 cq.exporters.export(cq.Compound.makeCompound([hinge('left',.35,'S2'),hinge('right',.35,'S2'),pin,left_board,right_board]),str(OUT/'models/S2-with-boards.step'))
 report=dict(passed=True,version='V25 strength trial',reference_revision='8085e9d79ffff3c69f07a1cca67595994237869e',source_sha256={str(p.relative_to(V25)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),V25/'source/build.py',V25/'reference/v24/source/case.py']},python=sys.version,cadquery=cq.__version__,platform=platform.platform(),command=[sys.executable,str(Path(__file__).resolve())],units='mm',checks=checks,specifications=specs,rounded_relief_radius_mm=R,printed_parts=len(items),physical_acceptance=False,full_case_integration=False,printer_started=False)
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'strength-trial checks;',len(items),'printed parts')
if __name__=='__main__':main()
