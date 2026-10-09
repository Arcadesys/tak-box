"""Exported flat-capstone storage, grasp clearance and playing-footprint checks."""
from pathlib import Path
import hashlib,json
import cadquery as cq
import case as c
OUT=c.OUT
checks=[]
def check(name,passed,detail=None):
 checks.append({'name':name,'pass':bool(passed),'detail':detail})
 assert passed,(name,detail)
for team,side in [('cat','left'),('witch','right')]:
 part=cq.importers.importStep(str(OUT/'models'/f'capstone-{team}.step')).val()
 b=part.BoundingBox();center=part.Center();stored=c.stored_capstone(team,side)
 housing=cq.importers.importStep(str(OUT/'models'/f'housing-{side}.step')).val()
 board=cq.importers.importStep(str(OUT/'models'/f'board-{side}.step')).val()
 check(team+' one-piece low-relief capstone',part.isValid() and len(part.Solids())==1 and abs(b.zlen-8)<1e-5,{'size_mm':[b.xlen,b.ylen,b.zlen],'body_height_mm':6.8,'raised_detail_mm':1.2})
 check(team+' fits one 36 mm playing cell with finger margin',b.xlen<=26 and b.ylen<=20,{'minimum_edge_margin_mm':min((36-b.xlen)/2,(36-b.ylen)/2)})
 check(team+' mass center over a centered 20 mm flat',abs(center.x)<8 and abs(center.y)<8,{'centroid_xy_mm':[center.x,center.y]})
 contact=part.intersect(c.box(-10,10,-10,10,0,.1)).Volume()/.1
 check(team+' broad contact on a 20 mm flat',contact>150,{'approximate_contact_area_mm2':contact,'physical_stack_stability':'unobserved'})
 check(team+' covered bay blocks upward lift',stored.translate((0,0,.6)).intersect(board).Volume()>.1)
 for dx,dy in [(3,0),(-3,0),(0,3),(0,-3)]:
  check(team+f' rim holds with maximum roof play {dx},{dy}',stored.translate((dx,dy,.39)).intersect(housing).Volume()>.1)
 check(team+' exposed capstone has 4.5 mm grasp above rim',abs(stored.BoundingBox().zmax-5.7-4.5)<1e-5)
 report={'checks':checks,'target':'V23 flat Cat/Witch capstones only; original sculpted capstones are incompatible with these bays','source_sha256':hashlib.sha256((OUT/'source/flat_capstones.py').read_bytes()).hexdigest(),'physical_acceptance':False}
(OUT/'reports/flat-capstones.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(checks),'flat-capstone checks PASS')
