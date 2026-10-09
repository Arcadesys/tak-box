"""V25 fixed piece guides and restored opposed captive PIP hinges. No removable trays."""
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
def housing(side):
 # Preserve the earlier opposed captive pivots and full-height 8 mm roots.
 s=c.housing(side)
 floor=c.union(c.box(11.2,89.5,2.4,193,2.19,3.4),c.box(76,90.2,0,200,0,3.4))
 if side=='right':floor=c.mirror(floor)
 # Relieve only the added floor before union: retain the original pin/socket.
 for other,spans in c.base.FAMILIES.items():
  if other!='tray-'+side:
   for a,z in spans:floor=floor.cut(b.cy(R,a-.15,z+.15))
 return c.union(s,floor,*guide_parts(side)).clean()
def guide_parts(side):
 # Exact earlier removable-tray guide layout, now fused into the case floor.
 shapes=[r.translate((1,0,c.TRAY_FLOOR)) for r in c.pocket_rims()]
 shapes.append(c.capstone_rim().translate((1,-.5,c.TRAY_FLOOR)))
 return [c.mirror(r) if side=='right' else r for r in shapes]
def guides(side):
 return c.union(*guide_parts(side))
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
  probe=c.box(12,87,10,190,2.21,3.39)
  if side=='right':probe=c.mirror(probe)
  check(side+' fixed floor replaces tray height',abs(h[side].intersect(probe).Volume()-probe.Volume())<1e-5)
  g=guides(side)
  check(side+' 21 fixed flat guides plus capstone guide',len(guide_parts(side))==22 and g.isValid())
  check(side+' guides are integral body material',g.cut(h[side]).Volume()<1e-5)
  check(side+' guide top 6.9mm leaves 4.5mm piece grasp height',abs(g.BoundingBox().zmax-6.9)<1e-5)
  baseline=OUT/'reference/plain-bodies'/f'housing-design-{side}.step'
  if baseline.exists():
   old=cq.importers.importStep(str(baseline)).val()
   check(side+' body change limited to fixed guides',old.cut(h[side]).Volume()<1e-5 and h[side].cut(c.union(old,g)).Volume()<1e-5)
  for i in range(3):
   for j in range(7):
    wall=c.box(13+22*i-.95,13+22*i-.35,10+22.6*j+1,10+22.6*j+4,3.5,6.8)
    if side=='right':wall=c.mirror(wall)
    check(side+f' fixed guide wall {i},{j}',wall.cut(h[side]).Volume()<1e-5)
  for x in (53.5,78.5):
   finger=cq.Solid.makeCylinder(7,5,cq.Vector(x,180,5.4))
   if side=='right':finger=c.mirror(finger)
   check(side+f' 14mm rear fingertip access {x}',ov(finger,h[side])<1e-5 and all(ov(finger,p)<1e-5 for _,p in pieces[side]))
  check(side+' 21 original flats and one flat capstone',len(pieces[side])==22)
  for name,p in pieces[side]:
   check(name+' fitted in fixed well',ov(p,h[side])<1e-5 and ov(p,boards[side])<1e-5)
   check(name+' seated on fixed floor',abs(p.BoundingBox().zmin-3.4)<1e-5)
   check(name+' fixed guides block 3mm XY shift under cover',all(ov(p.translate((dx,dy,.4)),g)>.01 for dx,dy in ((3,0),(-3,0),(0,3),(0,-3))))
   check(name+' lifts straight out after cover removal',all(ov(p.translate((0,0,z)),h[side])<1e-5 for z in (1,4,8,12)))
   check(name+' cover blocks upward lift at 0.6mm',ov(p.translate((0,0,.6)),boards[side])>.01)
  for d in range(0,107,2):
   check(side+f' reference cover slide {d}',ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),h[side])<1e-5 and all(ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),p)<1e-5 for _,p in pieces[side]))
  export_reference('housing-design-'+side,h[side]);export_reference('board-reference-'+side,boards[side]);export_reference('pieces-reference-'+side,cq.Compound.makeCompound([p for _,p in pieces[side]]))
 for label,delta in [('forward',3),('backward',-3)]:
  check('opposed pivots block '+label+' axial removal',ov(h['left'],h['right'].translate((0,delta,0)))>1)
 for face,mouth,d in c.PIP_STATIONS:
  gap=c.pip_pin(face,d).distance(h['left'])
  check('pivot CAD clearance '+str(face),gap>.39,dict(minimum_surface_gap_mm=gap))
 for side in h:
  for a,z in c.base.FAMILIES['tray-'+side]:
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
 b.e.plate('01-V25-PIP-fixed-guides',items)
 b.pkg.OUT=OUT;b.pkg.check=check
 b.pkg.housing_support_clearance('01-V25-PIP-fixed-guides',items)
 from zipfile import ZipFile
 import xml.etree.ElementTree as ET
 with ZipFile(OUT/'plates/01-V25-PIP-fixed-guides.3mf') as z:
  ns={'m':b.e.NS};root=ET.fromstring(z.read('3D/3dmodel.model'))
  check('PIP pair has one assembly build item',len(root.findall('m:build/m:item',ns))==1)
  check('PIP assembly retains both named body components',len(root.findall('.//m:component',ns))==2)
 source_files=[Path(__file__).resolve(),V25/'source/build.py',V25/'reference/v24/source/case.py',V25/'reference/v24/source/loaded_pieces.py']
 report=dict(passed=True,version='V25 PIP fixed piece guides prototype',units='mm',parent_revision='9eeef7bcd351c5c23f4851a763b39f779db867ea',reference_revision='8085e9d79ffff3c69f07a1cca67595994237869e',command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,cadquery=cq.__version__,platform=platform.platform(),source_sha256={str(p.relative_to(V25)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},reference_body_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/plain-bodies').glob('*.step')},reference_board_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/board-inlays').glob('*.step')},checks=checks,specifications=specs,printed_parts=2,main_hinge='opposed captive PIP pivots',nominal_pin_diameter_mm=4,nominal_radial_and_face_clearance_mm=.4,print_translation_mm=c.PRINT_BASE_SHIFT,removable_tray=False,pocket_rims=True,guide_top_mm=6.9,guide_height_above_floor_mm=3.5,fixed_floor_mm=3.4,piece_package='42 original Cat/Witch 20x20x8 mm flats and two supplied 8 mm V23 flat capstones; no weighted or sculpted pieces',packed_piece_count=44,closed_dimensions_mm=[dims.xlen,dims.ylen,dims.zlen],physical_acceptance=False,printer_started=False,limitations=['Rigid sampled poses and nominal-piece guides; physical loading, dumping and shake/drop/transport remain unverified.','V24 covers and side hook remain references; broad lip and rounded-cover changes are not integrated into the complete case.','Two new bodies required; previous physical PIP success has no identified version or recorded strength rating.'])
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'fixed-guide checks;',len(items),'printed bodies; 44 reference pieces')
if __name__=='__main__':main()
