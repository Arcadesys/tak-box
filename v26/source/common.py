"""V25 isolated fit coupons from PR31 V24 CAD. Units mm; no physical acceptance."""
from pathlib import Path
import sys,json,hashlib,platform
import cadquery as cq
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'v26'
sys.path.insert(0,str(OUT/'reference/v24/source'))
import case as c
from geometry_utils import ov
import package_case as pkg
import export_utils as e
e.OUT=OUT; e.mesh=pkg.welded_mesh
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail))
 if not ok: raise RuntimeError(name+': '+str(detail))
e.check=check
AX=(98,17.5)
FILAMENT_D=1.75
FILAMENT_LENGTH=5.4
ROUND_RELIEF_R=(8**2+17.5**2)**.5+.45
def cy(r,a,b):return cq.Solid.makeCylinder(r,b-a,cq.Vector(98,a,17.5),cq.Vector(0,1,0))
def hinge(side,gap,label=''):
 s=c.housing(side).intersect(c.box(76,120,0,26,-.1,30))
 cut=c.box(90.1,120,-.1,26.1,-1,31)
 if side=='right':cut=c.mirror(cut)
 s=s.cut(cut)
 spans=[(4.9,7.6)] if side=='left' else [(1.7,4.5)]
 for a,b in spans:
  root=c.box(90,98,a,b,0,17.5)
  if side=='right':root=c.mirror(root)
  journal=cq.Workplane('XY').newObject([cy(4.5,a,b)]).edges().fillet(.4).val()
  # Fixed left barrel has a 0.5 mm blind end. Bond the filament only here.
  bore_end=b-.5 if side=='left' else b+.02
  s=c.union(s,root,journal).cut(cy((FILAMENT_D+gap)/2,a-.02,bore_end))
 for a,b in ([(1.7,4.5)] if side=='left' else [(4.9,7.6)]):
  s=s.cut(cy((8**2+17.5**2)**.5+.45,a-.15,b+.15))
 # Retain fixture floor/support stock without touching the opposite moving root.
 if label:
  mark=cq.Workplane('XY').workplane(offset=2.19).text(label,3,.5,combine=False).val().translate((82 if side=='left' else 114,24,0))
  s=c.union(s,mark)
 return s.clean()
def filament():
 # Reference hardware only; never exported as a printable pin.
 return cy(FILAMENT_D/2,1.7,7.1)
def rounded_board(side):
 # Actual V24 board-edge section, restoring stock before replacing its square
 # corner cut with circular clearance for the tall support's swept envelope.
 p=c.x_prism([(3.1,11.8),(26,11.8),(26,16.5),(4.2,16.5),(3.1,15.4)],76,97.8)
 p=p.cut(cy(ROUND_RELIEF_R,-1,9.6))
 p=p.cut(c.box(7.6,97.81,9.6,10.4,15.9,16.51))
 p=p.cut(c.box(79.6,80.4,9.6,26.01,15.9,16.51))
 return p.clean() if side=='left' else c.mirror(p).clean()
def lip_board(t,label=''):
 s=c.board('left').translate((0,0,1)).intersect(c.box(0,18,22,58,11,18))
 s=s.cut(c.box(-.1,12,25.5,54.5,11,14.8))
 # Rounded plan root, wide blade flexes in Z; kept below the playing face.
 beam=c.round_box(0,14,26,54,12.8,12.8+t,.6)
 # Root connects to retained board at x12–14. Withdrawal shoulder at x1.2.
 catch=cq.Workplane('XZ').polyline([(1.2,12.8),(1.2,12.2),(2.2,12.2),(3.2,12.8)]).close().extrude(27).val().translate((0,53.5,0))
 s=c.union(s,beam,catch).clean()
 if label:
  mark=cq.Workplane('XY').workplane(offset=17.19).text(label,3,.5,combine=False).val().translate((4,56,0))
  s=s.cut(mark)
 return s.clean()
def lip_seat(label=''):
 s=c.housing('left').intersect(c.box(0,18,22,58,0,18))
 # Positive square withdrawal stop with lead-in roof at the far outside edge.
 s=c.union(s,c.box(0,1.1,26.3,53.7,11.49,12.6)).clean()
 # Short fixture guides simulate full-board transverse constraint; not a copied rail.
 for a,b,foot0,foot1 in ((21.2,21.6,21.2,22.2),(58.4,58.8,57.8,58.8)):
  s=c.union(s,c.box(10,18,a,b,0,14.1),c.box(10,18,foot0,foot1,0,2.2))
 if label:
  mark=cq.Workplane('XY').workplane(offset=2.19).text(label,3,.5,combine=False).val().translate((8,56,0))
  s=c.union(s,mark)
 return s.clean()
def bed(s,x,y,rotation=None):
 if rotation:s=s.rotate((0,0,0),rotation[0],rotation[1])
 v,_=pkg.welded_mesh(s);lo=v.min(axis=0)
 return s.translate((x-lo[0],y-lo[1],-lo[2]))
def export(name,s):
 check(name+' CAD valid single solid',s.isValid() and len(s.Solids())==1)
 cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
 vs,fs=pkg.welded_mesh(s)
 trimesh.Trimesh(vertices=vs,faces=fs,process=False).export(OUT/'models'/f'{name}.stl')
 back=cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
 m=trimesh.load(OUT/'models'/f'{name}.stl',force='mesh')
 check(name+' STEP and watertight STL',back.isValid() and abs(back.Volume()-s.Volume())<.01 and m.is_watertight and m.is_winding_consistent and m.body_count==1 and m.volume>0,dict(size_mm=m.extents.tolist(),volume_mm3=float(m.volume)))
 return dict(size_mm=m.extents.tolist(),sha256=hashlib.sha256((OUT/'models'/f'{name}.stl').read_bytes()).hexdigest())
def main():
 specs={};items=[];assemblies={}
 check('source V24 constants',c.base.AX==(98.,17.5) and c.PIP_PIN_R==2 and c.PIP_CLEARANCE==.4)
 # Test actual board/loaded tray geometry around V24 fixed axis; mirror rigid pair.
 left=c.board('left');right=c.board('right');tray=c.tray('left')
 board_l=rounded_board('left');board_r=rounded_board('right')
 # Retained playing-field material is exactly the reference V24 board.
 field=c.box(76,97.8,10.4,26,11.8,16.5)
 check('rounded board retains local playing-field geometry',board_l.intersect(field).cut(left).Volume()<1e-5 and left.intersect(field).cut(board_l).Volume()<1e-5)
 for a in range(0,181,5):
  check(f'V24 reference board fold {a}',ov(left,c.fold(right,a))<1e-5)
 # Lowering the simple fixed axis below face must fail; report overlap, not wishful CAD.
 for delta in (1,2):
  lowered=right.rotate((98,0,16.5-delta),(98,1,16.5-delta),-180)
  overlap=ov(left,lowered)
  check(f'buried simple axis rejected depth {delta}',overlap>1,dict(overlap_mm3=overlap,face_gap_mm=-2*delta))
 for i,gap in enumerate((.2,.35,.5)):
  key=f'H{i+1}';l=hinge('left',gap,key);r=hinge('right',gap,key);p=filament()
  assemblies[key]=[l,r,p]
  for a in range(0,181,5):check(f'{key} hinge sweep {a}',ov(l,c.fold(r,a))<1e-5)
  check(key+' pin running clearance',ov(l,p)<1e-5 and ov(r,p)<1e-5)
  check(key+' blind end blocks inward filament migration',ov(l,p.translate((0,.5,0)))>.1)
  check(key+' unbonded filament can withdraw outward',ov(l,p.translate((0,-1,0)))<1e-5 and ov(r,p.translate((0,-1,0)))<1e-5)
  check(key+' blind wall is 0.5mm',abs(l.intersect(cy(.5,7.1,7.6)).Volume()-cy(.5,7.1,7.6).Volume())<1e-5)
  for a in range(0,181,5):
   check(f'{key} actual V24 board hinge clearance {a}',all(ov(left,s)<1e-5 and ov(c.fold(right,a),s)<1e-5 for s in (l,c.fold(r,a),p)))
   check(f'{key} rounded board / hinge sweep {a}',ov(board_l,c.fold(board_r,a))<1e-5 and all(ov(board_l,s)<1e-5 and ov(c.fold(board_r,a),s)<1e-5 for s in (l,c.fold(r,a),p)))
  parts=[(key+'-left',bed(l,8+i*60,8)),(key+'-right',bed(r,35+i*60,8))]
  for name,s in parts:specs[name]=export(name,s);items.append((name,s))
  specs[key]=dict(filament_d_mm=FILAMENT_D,bore_d_mm=FILAMENT_D+gap,diametral_clearance_mm=gap,knuckle_end_gap_mm=.4,barrel_d_mm=9,axis_mm=[98,17.5],root_radial_mm=8,filament_cut_length_mm=FILAMENT_LENGTH,blind_wall_mm=.5,fixed_bond_length_mm=2.2,axial_retention='Blind stop inward; cured bond in fixed left barrel required against outward withdrawal',printed_pin=False)
 for side,x in [('left',8),('right',40)]:
  name='BOARD-'+side;s=bed(rounded_board(side),x,42)
  specs[name]=export(name,s);items.append((name,s))
 specs['rounded_board_relief']=dict(radius_mm=ROUND_RELIEF_R,y_span_mm=[-1,9.6],playing_field_start_y_mm=10,underside_z_mm=11.8,playing_face_z_mm=16.5,full_case_integration=False)
 assemblies['rounded-board-hinge']=[board_l,board_r,hinge('left',.35,'H2'),hinge('right',.35,'H2'),filament()]
 for i,t in enumerate((.8,1.,1.2)):
  key=f'L{i+1}';b=lip_board(t,key);seat=lip_seat(key);assemblies[key]=[b,seat]
  check(key+' rest lip and seat clear',ov(b,seat)<1e-5)
  check(key+' positive withdrawal catch',ov(b.translate((-.5,0,0)),seat)>.1)
  check(key+' fixture guides block sideways escape',all(ov(b.translate((0,d,0)),seat)>.1 for d in (-.8,.8)))
  # Release check approximates a rigidly lifted fixture; actual blade bending remains physical.
  check(key+' lifted release path',all(ov(b.translate((-d,0,.65)),seat)<1e-5 for d in np.arange(0,22,.5)))
  check(key+' retained tray margin',ov(b,tray)<1e-5)
  right_b=c.mirror(b);right_tray=c.tray('right')
  for a in range(0,181,5):
   rb=right_b.rotate((98,0,18.5),(98,1,18.5),-a)
   rt=right_tray.rotate((98,0,18.5),(98,1,18.5),-a)
   check(f'{key} raised axis lip / actual tray sweep {a}',ov(b,rb)<1e-5 and ov(b,rt)<1e-5 and ov(rb,tray)<1e-5)
  parts=[(key+'-board',bed(b,8+i*60,68)),(key+'-seat',bed(seat,34+i*60,68))]
  for name,s in parts:specs[name]=export(name,s);items.append((name,s))
  specs[key]=dict(blade_width_mm=28,free_length_mm=12,blade_thickness_mm=t,catch_depth_mm=.6,engagement_mm=.4,release_lift_mm=.65,ceiling_z_mm=14.8,face_z_mm=17.5,proposed_half_rise_mm=1,proposed_total_thickness_increase_mm=2,estimated_beam_root_strain_at_release=1.5*t*.65/12**2)
 for i,(n,s) in enumerate(items):
  v,_=pkg.welded_mesh(s);lo=v.min(axis=0);hi=v.max(axis=0)
  check(n+' on 256mm bed',min(lo[:2])>=0 and max(hi[:2])<=256 and lo[2]>=-1e-5)
  for n2,t in items[i+1:]:check(n+' plate separation '+n2,ov(s,t)<1e-5)
 e.plate('01-V25-hinge-lip-coupons',items)
 for name,shapes in assemblies.items():
  cq.exporters.export(cq.Compound.makeCompound(shapes),str(OUT/'models'/f'{name}-assembly.step'))
 report=dict(source_revision='8085e9d79ffff3c69f07a1cca67595994237869e',source_pr='https://github.com/Arcadesys/tak-box/pull/31',source_case_sha256=hashlib.sha256((OUT/'reference/v24/source/case.py').read_bytes()).hexdigest(),cadquery=cq.__version__,python=sys.version,platform=platform.platform(),units='mm',checks=checks,specifications=specs,physical_acceptance=False,full_case_integration=False,printer_started=False)
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS',len(checks),'checks;',len(items),'printed objects',flush=True)
if __name__=='__main__':main()
