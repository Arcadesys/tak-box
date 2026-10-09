"""Loaded export checks for removable trays, access and geometric containment."""
import hashlib,json
import cadquery as cq
import case as c
from geometry_utils import ov
from loaded_pieces import loaded
OUT=c.OUT
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail});print(name,ok,flush=True)
for side in ('left','right'):
 shapes={kind:cq.importers.importStep(str(OUT/'models'/f'{kind}-{side}.step')).val() for kind in ('housing','tray','board')}
 h,t,b=(shapes[k] for k in ('housing','tray','board'));pieces=loaded(side)
 assembly=cq.Compound.makeCompound([t]+[s for _,s in pieces])
 check(side+' all 22 pieces clear exported tray',max(ov(s,t) for _,s in pieces)<1e-5)
 check(side+' loaded tray seats without interference',ov(assembly,h)<1e-5 and ov(assembly,b)<1e-5)
 check(side+' loaded removal/repacking every 1 mm through 25 mm',all(ov(assembly.translate((0,0,z)),h)<1e-5 for z in range(26)))
 check(side+' both covered and released board travel over loaded tray',all(ov(c.slide(c.board(side,c.BOARD_RELEASE),side,d),assembly)<1e-5 for d in range(0,107,2)))
 for dx,dy in ((.7,0),(-.7,0),(0,.7),(0,-.7)):
  check(side+f' seat blocks tray shift {dx},{dy}',ov(t.translate((dx,dy,0)),h)>.01)
 check(side+' cover blocks empty and loaded tray upward motion at 0.6 mm',ov(t.translate((0,0,.6)),b)>.01 and ov(assembly.translate((0,0,.6)),b)>.01)
 check(side+' cover blocks each piece at 0.6 mm lift',all(ov(s.translate((0,0,.6)),b)>.01 for _,s in pieces))
 # At maximum nominal vertical slack, the rims still stop planar piece motion.
 check(side+' pocket rims retain all pieces at full 0.4 mm roof slack',all(ov(s.translate((dx,dy,.4)),t)>.01 for _,s in pieces for dx,dy in ((3,0),(-3,0),(0,3),(0,-3))))
 for x in (53.5,78.5):
  finger=cq.Solid.makeCylinder(7,5,cq.Vector(x,180,5.4))
  if side=='right':finger=c.mirror(finger)
  check(side+f' 14 mm fingertip probe beside grip X{x}',ov(finger,assembly)<1e-5 and ov(finger,h)<1e-5)
 floor=c.box(14,85,11,189,2.21,3.39)
 if side=='right':floor=c.mirror(floor)
 check(side+' continuous 1.2 mm tray floor',floor.cut(t).Volume()<1e-5)
 bottom=t.intersect(c.box(-1,197,0,201,2.2,2.3))
 check(side+' broad flat support footprint on table',bottom.Volume()/.1>13000,{'contact_area_lower_bound_mm2':bottom.Volume()/.1,'tray_width_length_height_mm':[76.2,182.1,9.2]})
 # The complete loaded tray clears the opposite loaded module through folding.
 other='right' if side=='left' else 'left'
 obstacles=[cq.importers.importStep(str(OUT/'models'/f'{k}-{other}.step')).val() for k in ('housing','board','tray')]+[s for _,s in loaded(other)]
 check(side+' full loaded tray/other module folding every 10 degrees',all(ov(assembly if side=='left' else c.fold(assembly,a),p if side=='right' else c.fold(p,a))<1e-5 for a in range(0,181,10) for p in obstacles))
 cq.exporters.export(assembly,str(OUT/'models'/f'tray-loaded-{side}.step'))
report={'checks':checks,'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (OUT/'source').glob('*.py')},'piece_package':'42 original Cat/Witch 20x20x8 mm flats and the supplied 8 mm V23 flat capstones; old sculpted/weighted packages unqualified','stack_mm':{'case_floor':2.2,'tray_floor':1.2,'piece_height':8,'roof_clearance':.4,'board_body':4.7},'closed_height_mm':35,'physical_acceptance':False,'limitations':['Motion and containment use rigid sampled poses, not a continuous or drop simulation.','Open trays remain upright during removal/repacking; they do not clamp pieces against inversion.','1.2 mm floors, actual grasp, full-tray warp/flex, release, closed shake/drop/carry retention and hinge fatigue require physical observation.']}
(OUT/'reports/trays.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(x['pass'] for x in checks)
