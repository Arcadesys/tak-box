"""V26 reinforced sliding-board clips and captive side hook; fixed guides and PIP bodies."""
from pathlib import Path
import importlib.util,sys,json,hashlib,platform,math
import cadquery as cq
from functools import lru_cache
OUT=Path(__file__).resolve().parents[1];V25=OUT
spec=importlib.util.spec_from_file_location('coupon_common',OUT/'source/common.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
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
 s=c.union(s,floor,*guide_parts(side)).clean()
 return captive_mount(s) if side=='left' else s
def guide_parts(side):
 # Exact earlier removable-tray guide layout, now fused into the case floor.
 shapes=[r.translate((1,0,c.TRAY_FLOOR)) for r in c.pocket_rims()]
 shapes.append(c.capstone_rim().translate((1,-.5,c.TRAY_FLOOR)))
 return [c.mirror(r) if side=='right' else r for r in shapes]
def guides(side):
 return c.union(*guide_parts(side))
@lru_cache(None)
def board_parts(side,release=0):
 parts={role:cq.importers.importStep(str(OUT/'reference/board-inlays'/f'board-{side}-{role}.step')).val() for role in ROLES}
 old=c.board_catch();new=board_catch(release)
 if side=='right':old=c.mirror(old);new=c.mirror(new)
 parts['body']=c.union(parts['body'].cut(old),new)
 notch=c.box(5.69,6.2,70,122,11.7,17.6)
 parts['body']=parts['body'].cut(c.mirror(notch) if side=='right' else notch).clean()
 return parts
@lru_cache(None)
def board(side,release=0):return cq.Compound.makeCompound(list(board_parts(side,release).values()))
def export_reference(name,s):
 check(name+' CAD validity',s.isValid() and s.Volume()>0)
 p=OUT/'models'/f'{name}.step';cq.exporters.export(s,str(p));got=cq.importers.importStep(str(p)).val()
 check(name+' STEP readback',got.isValid() and abs(got.Volume()-s.Volume())<.02)
def board_catch(release=0):
 # Wider plan-flex beam, gradual root transition; same 2.8 mm release travel.
 xs=[54*i/80 for i in range(81)]
 def d(x):
  u=x/54;return release*u*u*(3-u)/2
 def width(x):
  u=min(1,max(0,(x-3)/12));return 3.2-.8*u*u*(3-2*u)
 pts=[(x,6.1-width(x)+d(x)) for x in xs]
 pts += [(x,6.1+d(x)) for x in reversed(xs)]
 arm=cq.Workplane('XY').workplane(offset=11.8).polyline(pts).close().extrude(4.7).val()
 blend=c.box(3,4.2,6.1,7.3,11.8,16.5).cut(cq.Solid.makeCylinder(1.2,4.72,cq.Vector(4.2,7.3,11.79)))
 return c.union(c.box(0,3,2.9,9.51,11.8,16.5),arm,blend,c.box(34,54,.2+release,5.2+release,11.8,16.5))

def captive_mount(s):
 # Fixed outer cheek and inner original mount enclose a horizontal bridge axle.
 # Bearing relief reaches the bed, where the rotating hook has a broad foot.
 s=s.cut(c.x_cylinder(7.0,1.99,6.01,100.8,5.8)).cut(c.box(1.99,6.01,72.3,94.6,-.1,4.4))
 cheek=c.round_box(0,2.0,94.2,110,0,11.6,1,'X')
 bridge=c.box(0,9.6,108.3,110,0,3.4)
 axle=c.x_cylinder(2,1.7,6.2,100.8,5.8)
 return c.union(s,cheek,bridge,axle,c.hook_pivot_passage()).clean()

@lru_cache(None)
def hook(angle=0):
 # Keep the closure tooth and lever, replace its small filament bearing.
 old=c.side_hook().translate((.4,0,0))
 old=old.cut(c.x_cylinder(4.01,2.39,5.61,100.8,5.8))
 boss=c.x_cylinder(5.8,2.4,5.6,100.8,5.8)
 # Broad bed foot is defined in parked (90 degree) pose and rotates with hook.
 foot=c.hook_rotate(c.box(2.4,5.6,97.8,103.8,0,.8),-90)
 s=c.union(old,boss,foot).cut(c.x_cylinder(2.4,2.39,5.61,100.8,5.8)).clean()
 return c.hook_rotate(s,angle)

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
  if baseline.exists() and side=='right':
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
   check(side+f' reference cover slide {d}',ov(c.slide(board(side,c.BOARD_RELEASE),side,d),h[side])<1e-5 and all(ov(c.slide(board(side,c.BOARD_RELEASE),side,d),p)<1e-5 for _,p in pieces[side]))
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
 print('Starting integrated fold checks',flush=True)
 for angle in range(0,181,2):
  if angle%30==0:print('Fold',angle,flush=True)
  right=c.fold(h['right'],angle);rb=c.fold(boards['right'],angle)
  check(f'body and cover fold {angle}',ov(h['left'],right)<1e-5 and ov(h['left'],rb)<1e-5 and ov(boards['left'],right)<1e-5 and ov(boards['left'],rb)<1e-5)
  if angle%10==0:
   moving_pieces=[c.fold(p,angle) for _,p in pieces['right']]
   fixed_obstacles=[h['left'],boards['left']]+[p for _,p in pieces['left']]
   moving_obstacles=[right,rb]
   check(f'packed reference set fold {angle}',all(ov(p,s)<1e-5 for p in moving_pieces for s in fixed_obstacles) and all(ov(p,s)<1e-5 for _,p in pieces['left'] for s in moving_obstacles))
 dims=cq.Compound.makeCompound([h['left'],c.fold(h['right'],180)]).BoundingBox()
 check('closed envelope unchanged',abs(dims.xlen-102.5)<.002 and abs(dims.ylen-200)<.002 and abs(dims.zlen-35)<.002,dict(x=dims.xlen,y=dims.ylen,z=dims.zlen))
 print('Checking clip and captive hook',flush=True)
 for side in h:
  parts=board_parts(side)
  check(side+' revised clip board is one solid',len(parts['body'].Solids())==1 and parts['body'].isValid())
  field=c.box(7.6,188.4,9.6,190.4,0,18)
  old=cq.importers.importStep(str(OUT/'reference/board-inlays'/f'board-{side}-body.step')).val()
  check(side+' board playing field unchanged',old.intersect(field).cut(parts['body']).Volume()<1e-5 and parts['body'].intersect(field).cut(old).Volume()<1e-5)
  check(side+' clip blocks withdrawal at rest',ov(c.slide(boards[side],side,1),h[side])>.1)
  for rel in (0,.7,1.4,2.1,2.8):check(side+f' assumed clip flex pose {rel}',ov(board(side,rel),h[side])<1e-5)
  for role,s in parts.items():
   cq.exporters.export(s,str(OUT/'models'/f'board-{side}-{role}.step'))
   if role=='body':b.export('board-'+side+'-body',s)
 for angle in range(0,91,2):
  moving=hook(angle)
  check(f'captive hook own-body rotation {angle}',ov(moving,h['left'])<1e-5)
  check(f'captive hook closed-case rotation {angle}',ov(moving,c.fold(h['right'],180))<1e-5)
  check(f'captive hook closed-boards rotation {angle}',all(ov(moving,s)<1e-5 for s in (boards['left'],c.fold(boards['right'],180))))
 check('hook parked bed foot',abs(hook(90).BoundingBox().zmin)<1e-5)
 check('hook radial axle clearance',hook(90).distance(c.x_cylinder(2,2.4,5.6,100.8,5.8))>.39)
 for dx in (-1,1):check('hook axial capture '+str(dx),ov(hook(90).translate((dx,0,0)),h['left'])>.1)
 for angle in range(0,181,2):check(f'parked hook case fold {angle}',ov(hook(90),c.fold(h['right'],angle))<1e-5)
 for side in h:
  for d in range(0,107,2):check(side+f' parked hook board removal {d}',ov(c.slide(board(side,2.8),side,d),hook(90))<1e-5)
 export_reference('hook-design-closed',hook());export_reference('hook-design-parked',hook(90))
 print('Exporting final geometry',flush=True)
 items=[];specs={}
 for side in ('left','right'):
  name='housing-'+side;model=h[side].translate(c.PRINT_BASE_SHIFT)
  specs[name]=b.export(name,model);items.append((name,model))
  check(name+' bed bounds',model.BoundingBox().xmin>=0 and model.BoundingBox().xmax<256 and model.BoundingBox().ymin>=0 and model.BoundingBox().ymax<256)
 model=hook(90).translate(c.PRINT_BASE_SHIFT);specs['captive-hook']=b.export('captive-hook',model);items.append(('captive-hook',model))
 check('paired PIP bodies have no overlap',ov(items[0][1],items[1][1])<1e-5)
 b.e.plate('01-V26-PIP-guides-and-hook',items)
 b.pkg.OUT=OUT;b.pkg.check=check
 b.pkg.housing_support_clearance('01-V26-PIP-guides-and-hook',items)
 from zipfile import ZipFile
 import xml.etree.ElementTree as ET
 with ZipFile(OUT/'plates/01-V26-PIP-guides-and-hook.3mf') as z:
  ns={'m':b.e.NS};root=ET.fromstring(z.read('3D/3dmodel.model'))
  check('PIP pair has one assembly build item',len(root.findall('m:build/m:item',ns))==1)
  check('PIP assembly retains both bodies and captive hook',len(root.findall('.//m:component',ns))==3)
 source_files=[Path(__file__).resolve(),OUT/'source/common.py',V25/'reference/v24/source/case.py',V25/'reference/v24/source/loaded_pieces.py']
 report=dict(passed=True,version='V26 reinforced clip and captive hook review',units='mm',parent_revision='c101d7d6585c363e23cf140f9059f38a96a8d6c8',reference_revision='8085e9d79ffff3c69f07a1cca67595994237869e',command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,cadquery=cq.__version__,platform=platform.platform(),source_sha256={str(p.relative_to(V25)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},reference_body_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/plain-bodies').glob('*.step')},reference_board_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference/board-inlays').glob('*.step')},checks=checks,specifications=specs,printed_parts=3,main_hinge='opposed captive PIP pivots',nominal_pin_diameter_mm=4,nominal_radial_and_face_clearance_mm=.4,print_translation_mm=c.PRINT_BASE_SHIFT,removable_tray=False,pocket_rims=True,guide_top_mm=6.9,guide_height_above_floor_mm=3.5,fixed_floor_mm=3.4,piece_package='42 original Cat/Witch 20x20x8 mm flats and two supplied 8 mm V23 flat capstones; no weighted or sculpted pieces',packed_piece_count=44,closed_dimensions_mm=[dims.xlen,dims.ylen,dims.zlen],physical_acceptance=False,printer_started=False,limitations=['Rigid sampled poses and nominal-piece guides; physical loading, dumping and shake/drop/transport remain unverified.','Wider board clip and captive hook are unprinted; release force and retention are physical gates. Rounded-cover underside remains pending.','Two new bodies required; previous physical PIP success has no identified version or recorded strength rating.'])
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'V26 mechanism checks;',len(items),'PIP case components; 44 reference pieces')
if __name__=='__main__':main()
