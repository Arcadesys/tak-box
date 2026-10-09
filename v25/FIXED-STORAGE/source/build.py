"""V25 plain fixed storage wells and selected B filament hinges. No removable trays."""
from pathlib import Path
import importlib.util,sys,json,hashlib,platform,math
import cadquery as cq
OUT=Path(__file__).resolve().parents[1];V25=OUT.parent
spec=importlib.util.spec_from_file_location('coupon_common',V25/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
c=b.c;ov=b.ov
sys.path.insert(0,str(V25/'reference/v24/source'))
from loaded_pieces import loaded
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,(name,detail)
b.OUT=OUT;b.check=check;b.e.OUT=OUT;b.e.check=check
FIXED=((.3,2.8),(6.8,9.3),(190.7,193.2),(197.2,199.7))
MOVING=((3.2,6.4),(193.6,196.8))
R=math.hypot(8,17.5)+.45
ROLES=('body','grid','stars','orange','purple')
def housing(side):
 s=c.housing(side)
 for a,z in ((-.1,9.5),(190.5,200.1)):
  cut=c.box(90.1,120,a,z,-1,31)
  if side=='right':cut=c.mirror(cut)
  s=s.cut(cut)
 # Replace the old removable floor with stock joined permanently to the case.
 floor=c.union(c.box(11.2,89.5,2.4,193,2.19,3.4),c.box(76,90.2,0,200,0,3.4))
 if side=='right':floor=c.mirror(floor)
 s=c.union(s,floor)
 own=FIXED if side=='left' else MOVING;other=MOVING if side=='left' else FIXED
 for a,z in own:
  root=c.box(90,98,a,z,0,17.5)
  gusset=cq.Workplane('XZ').polyline([(88.2,2.19),(90.2,10.5),(90.2,2.19)]).close().extrude(z-a).val().translate((0,z,0))
  if side=='right':root=c.mirror(root);gusset=c.mirror(gusset)
  journal=cq.Workplane('XY').newObject([b.cy(4.5,a,z)]).edges().fillet(.4).val()
  s=c.union(s,root,gusset,journal).cut(b.cy((1.95 if side=='left' else 2.10)/2,a-.02,z+.02))
 if side=='left':
  for a,z in ((.28,1.),(8.6,9.32),(190.68,191.4),(199.,199.72)):s=s.cut(b.cy(1.75,a,z))
 for a,z in other:s=s.cut(b.cy(R,a-.15,z+.15))
 return s.clean()
def pin(a):return c.union(b.cy(.875,a+.6,a+8.4),b.cy(1.6,a,a+.6),b.cy(1.6,a+8.4,a+9))
def board_parts(side):return {role:cq.importers.importStep(str(OUT/'reference/board-inlays'/f'board-{side}-{role}.step')).val() for role in ROLES}
def board(side):return cq.Compound.makeCompound(list(board_parts(side).values()))
def export_reference(name,s):
 check(name+' CAD validity',s.isValid() and s.Volume()>0)
 p=OUT/'models'/f'{name}.step';cq.exporters.export(s,str(p));got=cq.importers.importStep(str(p)).val()
 check(name+' STEP readback',got.isValid() and abs(got.Volume()-s.Volume())<.02)
def main():
 h={side:housing(side) for side in ('left','right')};boards={side:board(side) for side in h};pins=[pin(.3),pin(190.7)]
 pieces={side:loaded(side) for side in h};mechanical={side:c.board(side) for side in h}
 for side in h:
  check(side+' connected case body',h[side].isValid() and len(h[side].Solids())==1)
  probe=c.box(12,87,10,190,2.21,3.39);well=c.box(11.21,89.49,10,190,3.401,5.7)
  if side=='right':probe=c.mirror(probe);well=c.mirror(well)
  check(side+' fixed floor replaces tray height',abs(h[side].intersect(probe).Volume()-probe.Volume())<1e-5)
  check(side+' open well has no exposed pocket rims or tray stops',ov(h[side],well)<1e-5)
  check(side+' 21 original flats and one flat capstone',len(pieces[side])==22)
  for name,p in pieces[side]:
   check(name+' fitted in fixed well',ov(p,h[side])<1e-5 and ov(p,boards[side])<1e-5)
   check(name+' seated on fixed floor',abs(p.BoundingBox().zmin-3.4)<1e-5)
   check(name+' cover blocks upward lift at 0.6mm',ov(p.translate((0,0,.6)),boards[side])>.01)
  for d in range(0,107,2):
   check(side+f' reference cover slide {d}',ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),h[side])<1e-5 and all(ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),p)<1e-5 for _,p in pieces[side]))
  export_reference('housing-design-'+side,h[side]);export_reference('board-reference-'+side,boards[side]);export_reference('pieces-reference-'+side,cq.Compound.makeCompound([p for _,p in pieces[side]]))
 for i,p in enumerate(pins):
  check(f'axle {i} running fit',all(ov(p,s)<1e-5 for s in h.values()))
  check(f'axle {i} two heads block both axial directions',all(ov(p.translate((0,d,0)),h['left'])>.1 for d in (-.25,.25)))
 export_reference('filament-reference-NOT-PRINTED',cq.Compound.makeCompound(pins))
 for angle in range(0,181,2):
  right=c.fold(h['right'],angle);rb=c.fold(boards['right'],angle)
  check(f'body and cover fold {angle}',ov(h['left'],right)<1e-5 and ov(h['left'],rb)<1e-5 and ov(boards['left'],right)<1e-5 and ov(boards['left'],rb)<1e-5 and all(ov(p,right)<1e-5 for p in pins))
  if angle%10==0:
   moving_pieces=[c.fold(p,angle) for _,p in pieces['right']]
   fixed_obstacles=[h['left'],boards['left']]+[p for _,p in pieces['left']]
   moving_obstacles=[right,rb]
   check(f'packed reference set fold {angle}',all(ov(p,s)<1e-5 for p in moving_pieces for s in fixed_obstacles) and all(ov(p,s)<1e-5 for _,p in pieces['left'] for s in moving_obstacles))
 dims=cq.Compound.makeCompound([h['left'],c.fold(h['right'],180)]).BoundingBox()
 check('closed envelope unchanged',abs(dims.xlen-102.5)<.002 and abs(dims.ylen-200)<.002 and abs(dims.zlen-35)<.002,dict(x=dims.xlen,y=dims.ylen,z=dims.zlen))
 items=[];specs={}
 for side,x in [('left',8),('right',113)]:
  name='housing-'+side;model=b.bed(h[side],x,8);specs[name]=b.export(name,model);items.append((name,model))
  check(name+' bed bounds',model.BoundingBox().xmin>=0 and model.BoundingBox().xmax<256 and model.BoundingBox().ymin>=0 and model.BoundingBox().ymax<256)
 check('plate parts separate',ov(items[0][1],items[1][1])<1e-5)
 b.e.plate('01-V25-fixed-storage-bodies',items)
 source_files=[Path(__file__).resolve(),V25/'source/build.py',V25/'reference/v24/source/case.py',V25/'reference/v24/source/loaded_pieces.py']
 report=dict(passed=True,version='V25 fixed storage / B hinge prototype',units='mm',parent_revision='5ad905e42ad8133c05efbf77971b21f5f3970c43',reference_revision='8085e9d79ffff3c69f07a1cca67595994237869e',command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,cadquery=cq.__version__,platform=platform.platform(),source_sha256={str(p.relative_to(V25)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},reference_board_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/board-inlays').glob('*.step')},checks=checks,specifications=specs,printed_parts=2,removable_tray=False,pocket_rims=False,fixed_floor_mm=3.4,piece_package='42 original Cat/Witch 20x20x8 mm flats and two supplied 8 mm V23 flat capstones; no weighted or sculpted pieces',packed_piece_count=44,closed_dimensions_mm=[dims.xlen,dims.ylen,dims.zlen],physical_acceptance=False,printer_started=False,limitations=['Rigid poses; no random loose-piece packing or shake/drop/transport simulation.','V24 covers and side hook remain references; broad lip and rounded-cover changes are not integrated into the complete case.','Two new bodies required; stronger coupon does not establish whole-case durability.'])
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'fixed-storage checks;',len(items),'printed bodies; 44 reference pieces')
if __name__=='__main__':main()
