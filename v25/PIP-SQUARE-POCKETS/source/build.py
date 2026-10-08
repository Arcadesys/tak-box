"""V25 fixed square pockets and three-knuckle captive printed posts. No removable trays."""
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
R=math.hypot(8,17.5)+.45
ROLES=('body','grid','stars','orange','purple')
FIXED=((.3,2.8),(6.8,9.3),(190.7,193.2),(197.2,199.7))
MOVING=((3.2,6.4),(193.6,196.8))
POST_SPANS=((.3,9.3),(190.7,199.7))
def post():return c.union(*(b.cy(2,a,z) for a,z in POST_SPANS))
def rims(side):
 parts=[v.translate((1,0,1.2)) for v in c.pocket_rims()]+[c.capstone_rim().translate((1,-.5,1.2))]
 return parts if side=='left' else [c.mirror(v) for v in parts]
def housing(side):
 s=c.housing(side)
 # Remove the previous opposed pin/socket stations, preserving the shell.
 for a,z in ((-.1,9.6),(190.4,200.1)):
  cut=c.box(90.1,120,a,z,-1,31)
  if side=='right':cut=c.mirror(cut)
  s=s.cut(cut)
 floor=c.union(c.box(11.2,89.5,2.4,193,2.19,3.4),c.box(76,90.2,0,200,0,3.4))
 if side=='right':floor=c.mirror(floor)
 s=c.union(s,floor,*rims(side))
 own=FIXED if side=='left' else MOVING
 other=MOVING if side=='left' else FIXED
 for a,z in own:
  root=c.box(90,98,a,z,0,17.5)
  if side=='right':root=c.mirror(root)
  journal=cq.Workplane('XY').newObject([b.cy(4.5,a,z)]).edges().fillet(.4).val()
  s=c.union(s,root,journal)
 for a,z in other:s=s.cut(b.cy(R,a-.15,z+.15))
 if side=='left':s=c.union(s,post())
 else:
  for a,z in MOVING:s=s.cut(b.cy(2.4,a-.02,z+.02))
 return s.clean()
def board_parts(side):return {role:cq.importers.importStep(str(OUT/'reference/board-inlays'/f'board-{side}-{role}.step')).val() for role in ROLES}
def board(side):return cq.Compound.makeCompound(list(board_parts(side).values()))
def export_reference(name,s):
 check(name+' CAD validity',s.isValid() and s.Volume()>0)
 p=OUT/'models'/f'{name}.step';cq.exporters.export(s,str(p));got=cq.importers.importStep(str(p)).val()
 check(name+' STEP readback',got.isValid() and abs(got.Volume()-s.Volume())<.02)
def main():
 h={side:housing(side) for side in ('left','right')};boards={side:board(side) for side in h}
 pieces={side:loaded(side) for side in h};mechanical={side:c.board(side) for side in h}
 for side in h:
  check(side+' connected case body',h[side].isValid() and len(h[side].Solids())==1)
  probe=c.box(12,87,10,190,2.21,3.39);well=c.box(11.21,89.49,10,190,3.401,5.7)
  if side=='right':probe=c.mirror(probe);well=c.mirror(well)
  check(side+' fixed floor replaces tray height',abs(h[side].intersect(probe).Volume()-probe.Volume())<1e-5)
  check(side+' 21 square rims and one capstone rim',len(rims(side))==22)
  for i,rim in enumerate(rims(side)):
   check(side+f' rim {i+1} integrated into body',rim.cut(h[side]).Volume()<1e-5)
  check(side+' rims retain each piece at full 0.4mm roof slack',all(ov(p.translate((dx,dy,.4)),h[side])>.01 for _,p in pieces[side] for dx,dy in ((3,0),(-3,0),(0,3),(0,-3))))
  check(side+' pieces lift vertically after cover removal',all(ov(p.translate((0,0,d)),h[side])<1e-5 for _,p in pieces[side] for d in (1,4,8,16)))
  check(side+' 21 original flats and one flat capstone',len(pieces[side])==22)
  for name,p in pieces[side]:
   check(name+' fitted in fixed well',ov(p,h[side])<1e-5 and ov(p,boards[side])<1e-5)
   check(name+' seated on fixed floor',abs(p.BoundingBox().zmin-3.4)<1e-5)
   check(name+' cover blocks upward lift at 0.6mm',ov(p.translate((0,0,.6)),boards[side])>.01)
  for d in range(0,107,2):
   check(side+f' reference cover slide {d}',ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),h[side])<1e-5 and all(ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),p)<1e-5 for _,p in pieces[side]))
  export_reference('housing-design-'+side,h[side]);export_reference('board-reference-'+side,boards[side]);export_reference('pieces-reference-'+side,cq.Compound.makeCompound([p for _,p in pieces[side]]))
 for label,delta in [('forward',3),('backward',-3)]:
  check('opposed pivots block '+label+' axial removal',ov(h['left'],h['right'].translate((0,delta,0)))>1)
 check('central posts integral to both stationary outer knuckles',post().cut(h['left']).Volume()<1e-5)
 for a,z in MOVING:
  gap=b.cy(2,a,z).distance(h['right'])
  check('post radial clearance '+str(a),gap>.399,dict(minimum_surface_gap_mm=gap))
  check('moving knuckle held between two fixed knuckles '+str(a),any(abs(a-fz-.4)<1e-8 for _,fz in FIXED) and any(abs(fa-z-.4)<1e-8 for fa,_ in FIXED))
 for side in h:
  for a,z in (FIXED if side=='left' else MOVING):
   for height in (1,4,8,12):
    probe=c.box(90.2,97.8,a+.2,z-.2,height,height+.5)
    if side=='right':probe=c.mirror(probe)
    check(side+f' full-height root {a} Z{height}',abs(probe.Volume()-h[side].intersect(probe).Volume())<1e-5)
 for angle in range(0,181,2):
  right=c.fold(h['right'],angle);rb=c.fold(boards['right'],angle)
  check(f'body and cover fold {angle}',ov(h['left'],right)<1e-5 and ov(h['left'],rb)<1e-5 and ov(boards['left'],right)<1e-5 and ov(boards['left'],rb)<1e-5)
  if angle%10==0:
   moving_pieces=[c.fold(p,angle) for _,p in pieces['right']]
   fixed_obstacles=[h['left'],boards['left']]+[p for _,p in pieces['left']]
   moving_obstacles=[right,rb]
   check(f'packed reference set fold {angle}',all(ov(p,s)<1e-5 for p in moving_pieces for s in fixed_obstacles) and all(ov(p,s)<1e-5 for _,p in pieces['left'] for s in moving_obstacles))
 dims=cq.Compound.makeCompound([h['left'],c.fold(h['right'],180)]).BoundingBox()
 check('closed envelope unchanged',abs(dims.xlen-102.5)<.002 and abs(dims.ylen-200)<.002 and abs(dims.zlen-35)<.002,dict(x=dims.xlen,y=dims.ylen,z=dims.zlen))
 items=[];specs={}
 for side in ('left','right'):
  name='housing-'+side;model=h[side].translate(c.PRINT_BASE_SHIFT)
  specs[name]=b.export(name,model);items.append((name,model))
  check(name+' bed bounds',model.BoundingBox().xmin>=0 and model.BoundingBox().xmax<256 and model.BoundingBox().ymin>=0 and model.BoundingBox().ymax<256)
 check('paired PIP bodies have no overlap',ov(items[0][1],items[1][1])<1e-5)
 b.e.plate('01-V25-PIP-square-pockets',items)
 b.pkg.OUT=OUT;b.pkg.check=check
 b.pkg.housing_support_clearance('01-V25-PIP-square-pockets',items)
 from zipfile import ZipFile
 import xml.etree.ElementTree as ET
 with ZipFile(OUT/'plates/01-V25-PIP-square-pockets.3mf') as z:
  ns={'m':b.e.NS};root=ET.fromstring(z.read('3D/3dmodel.model'))
  check('PIP pair has one assembly build item',len(root.findall('m:build/m:item',ns))==1)
  check('PIP assembly retains both named body components',len(root.findall('.//m:component',ns))==2)
 source_files=[Path(__file__).resolve(),V25/'source/build.py',V25/'reference/v24/source/case.py',V25/'reference/v24/source/loaded_pieces.py']
 report=dict(passed=True,version='V25 square pockets and three-knuckle captive post',units='mm',parent_revision='9eeef7b',reference_revision='8085e9d79ffff3c69f07a1cca67595994237869e',command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,cadquery=cq.__version__,platform=platform.platform(),source_sha256={str(p.relative_to(V25)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},reference_board_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/board-inlays').glob('*.step')},checks=checks,specifications=specs,printed_parts=2,main_hinge='fixed outer / moving central / fixed outer; integral 4mm post',nominal_pin_diameter_mm=4,nominal_radial_and_face_clearance_mm=.4,print_translation_mm=c.PRINT_BASE_SHIFT,removable_tray=False,pocket_rims=True,pocket_count_per_half=22,pocket_rim_top_mm=6.9,fixed_floor_mm=3.4,piece_package='42 original Cat/Witch 20x20x8 mm flats and two supplied 8 mm V23 flat capstones; no weighted or sculpted pieces',packed_piece_count=44,closed_dimensions_mm=[dims.xlen,dims.ylen,dims.zlen],physical_acceptance=False,printer_started=False,limitations=['Rigid sampled poses; no shake/drop/transport simulation.','V24 covers and side hook remain references; broad lip and rounded-cover changes are not integrated into the complete case.','Two new bodies required; previous physical PIP success has no identified version or recorded strength rating.'])
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'pocket and captive-post checks;',len(items),'printed bodies; 44 reference pieces')
if __name__=='__main__':main()
