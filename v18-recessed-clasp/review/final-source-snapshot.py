from pathlib import Path
import sys,json
import cadquery as cq
R=Path(__file__).parent
sys.path.insert(0,str(R.parent/'clasp-comparison'))
from common import box,ov,export_parts
# Coordinates: slider retracts -X; keeper/case half opens +Z. All mm.
def unite(parts):
 s=parts[0]
 for p in parts[1:]:s=s.fuse(p)
 return s.clean()
# Two roofed channels capture rigid rails; recessed centre admits press-and-slide finger.
receiver=unite([box(-12,40,0,40,0,1),box(-12,40,0,7,1,8.5),box(-12,40,33,40,1,8.5),box(-12,40,0,9.8,5.2,8.5),box(-12,40,30.2,40,5.2,8.5)])
receiver=receiver.fuse(box(-12,-10,0,40,1,8.5)).clean()
# Registration cage represents the case rim: keeper can lift +Z but cannot slide out sideways.
receiver=unite([receiver,box(39,66,0,4,-1.6,6),box(39,66,36,40,-1.6,6),box(39,66,0,40,-1.6,-.4),box(64,66,0,7,0,6),box(64,66,33,40,0,6)])
receiver=unite([receiver,box(-10,40,7,9.8,1,2),box(-10,40,30.2,33,1,2)])
# Hard detent shoulders, main lock and rear open-position retention. Central 12mm finger slot stays open.
for x in [10,22,31]:
 receiver=receiver.fuse(box(x,x+2,9.8,14,5.4,8.5)).fuse(box(x,x+2,26,30.2,5.4,8.5)).clean()
# Rigid bolt skeleton. Leaf is isolated from the rails and carries no keeper opening load.
rigid=unite([box(1,39,7.4,9.6,2.4,4.8),box(1,39,30.4,32.6,2.4,4.8),box(1,4,7.4,32.6,2.4,4.8),box(34,38.5,7.4,32.6,2.4,4.8),box(38,45,11.4,28.6,2.4,4.8)])
# Lead-in bevel on bolt nose; top/front only, retains flat lower load face.
cut=cq.Workplane('XZ').polyline([(43.5,4.8),(45.01,4.8),(45.01,3.29)]).close().extrude(42,both=True).val()
rigid=rigid.cut(cut).clean()
def leaf(delta):
 def d(x):
  u=(x-3)/22
  return delta*(u*u*(3-u)/2 if u<=1 else 1+1.5*(u-1))
 xs=[3+i*.5 for i in range(45)]
 pts=[(x,3.2-d(x)) for x in xs]+[(x,4.8-d(x)) for x in reversed(xs)]
 beam=cq.Workplane('XZ').polyline(pts).close().extrude(12).val().translate((0,26,0))
 # Pad and tooth follow end tangent. Both axial faces have positive square shoulders; small top chamfer only. Press to close as well as open.
 pts=[(25,3.7),(29,3.7),(29,6.5),(28.7,6.8),(25,6.8)]
 tooth=cq.Workplane('XZ').polyline([(x,z-d(x)) for x,z in pts]).close().extrude(20).val().translate((0,30,0))
 return beam.fuse(tooth).clean()
def slider(delta=0,travel=0):return rigid.fuse(leaf(delta)).clean().translate((-travel,0,0))
# Keeper lower shelf bears against rigid bolt underside when keeper lifts. Coupon end-web registers +X.
keeper=unite([box(41,55,5,35,0,2),box(48,55,5,35,2,8.5),box(41,55,5,7,2,8.5),box(41,55,33,35,2,8.5),box(48,63,5,35,0,2)])
# Small entry chamfer on shelf leading edge (not load-bearing overlap).
parts={'V18-receiver':receiver,'V18-slider':slider(),'V18-keeper':keeper}
if __name__=='__main__':
 r=export_parts(R/'parts',parts,{'V18-receiver':((1,0,0),90),'V18-slider':((1,0,0),90),'V18-keeper':((1,0,0),90)},meta={'version':18,'status':'unprinted engineering coupon, not integrated case','assembly':'Insert slider from +X while depressing tooth until it passes receiver lock tabs. Align keeper beyond receiver. Closing and opening both require press then slide. Closing moves +X; opening moves -X.','no_screws':True})
 states={ '01-locked':(0,0,0),'02-pressed':(1.8,0,0),'03-slid-clear':(1.8,10,0),'04-open':(0,10,12)}
 for name,(d,t,lift) in states.items():
  out=R/'states'/name;out.mkdir(parents=True,exist_ok=True)
  for n,s in {'receiver':receiver,'slider':slider(d,t),'keeper':keeper.translate((0,0,lift))}.items():cq.exporters.export(s,str(out/(n+'.stl')),tolerance=.04,angularTolerance=.12)
  cq.exporters.export(cq.Compound.makeCompound([receiver,slider(d,t),keeper.translate((0,0,lift))]),str(out/'assembly.step'))
 tests={'press_path':[],'pressed_slide_path':[],'locked_slide_barrier':[],'keeper_lift_barrier':[],'pressed_only_lift_barrier':[],'open_lift_path':[],'assembly_insertion':[]}
 for d in [i*.1 for i in range(19)]:tests['press_path'].append([d,ov(slider(d),receiver),ov(slider(d),keeper)])
 for t in [i*.25 for i in range(41)]:tests['pressed_slide_path'].append([t,ov(slider(1.8,t),receiver),ov(slider(1.8,t),keeper)])
 for t in [.2,.5,1,1.1,1.5,2,3]:tests['locked_slide_barrier'].append([t,ov(slider(0,t),receiver)])
 for z in [.2,.4,.5,1,2,4]:
  tests['keeper_lift_barrier'].append([z,ov(slider(),keeper.translate((0,0,z)))])
  tests['pressed_only_lift_barrier'].append([z,ov(slider(1.8),keeper.translate((0,0,z)))])
 for z in [i*.5 for i in range(31)]:tests['open_lift_path'].append([z,ov(slider(0,10),keeper.translate((0,0,z))),ov(receiver,keeper.translate((0,0,z)))])
 for x in [i*.5 for i in range(81)]:tests['assembly_insertion'].append([x,ov(slider(1.8,-x),receiver)])
 tests['open_rest_interference']=ov(slider(0,10),receiver)
 tests['nominal']={'leaf_length_mm':22,'leaf_thickness_mm':1.6,'leaf_width_mm':12,'tip_deflection_mm':1.8,'button_local_press_mm':1.8*(1+1.5*2/22),'slide_mm':10,'locked_keeper_overlap_mm':4,'keeper_vertical_clearance_mm':.4,'rail_vertical_clearance_mm':.4,'button_recess_mm':1.7,'estimated_small_deflection_root_strain':1.5*1.6*1.8/22**2,'linear_beam_force_N_at_E_2GPa':2000*12*1.6**3*1.8/(4*22**3),'not_proof':'Assumed cubic cantilever shape for geometric swept checks; no FEA/material validation, fatigue or measured force.'}
 (R/'checks.json').write_text(json.dumps(tests,indent=2))
 print(json.dumps({k:max((max(row[1:]) for row in v),default=0) if isinstance(v,list) else v for k,v in tests.items()},indent=2))
