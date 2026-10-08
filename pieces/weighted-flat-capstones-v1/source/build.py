"""Weighted Cat/Witch sample; legacy positive snap backs up epoxy. Units mm."""
from pathlib import Path
import sys, math, json, hashlib, subprocess
from dataclasses import replace
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
sys.path[:0]=[str(OUT/'source/vendor'),str(REPO/'pieces'),str(REPO/'v26/reference/v24/source'),str(REPO/'v16-field-book/source')]
import geometry as gen
import spec as specs
import flat_capstones as original
from mesh_export import export_stl
SIDE_WALL=1.6; SEAT_WALL=1.2; ROOF=.8; CLEARANCE=.2; CAT_FILL_BOTTOM=1.9
# Straight original silhouette edges with room for the recovered snap arms.
EDGES={'cat':[((-7.2,-9.3),(-12,-5)),((12,-5),(7.2,-9.3))],
       'witch':[((-4,10),(-11,-1)),((11,-1),(9,7))]}
C=specs.ClosureSpec()
def volume(obj):return obj.val().Volume()
def bounds(obj):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(obj.val().wrapped,b,False,False)
 q=b.Get();return np.array([q[:3],q[3:]])
def wp(s):return cq.Workplane(obj=s)
def prism(wire,z,h):
 s=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,h)).translate((0,0,z))
 # Offset wires inherit orientation; normalize before using them as cutters.
 if s.Volume()<0:s.wrapped.Reverse()
 assert s.isValid() and s.Volume()>0
 return wp(s)
def inward(wire,d):
 wires=wire.offset2D(-d);assert len(wires)==1 and wires[0].isValid(),('offset',d)
 return wires[0]
def transform(obj,frame):return obj.rotate((0,0,0),(0,0,1),frame['angle_deg']).translate((*frame['origin_xy'],0))
def outer_capstone(team):
 if team=='cat':return original.capstone(team)
 # Broad brim and crown, with a bent point and tactile star. Fits the existing
 # 26 x 20 x 8 mm capstone envelope; extra ballast space comes from XY area.
 outline=[(-13,-10),(13,-10),(13,-2),(11,-1),(9,7),(12,8),(-4,10),(-11,-1),(-13,-2)]
 body=cq.Workplane('XY').polyline(outline).close().extrude(original.BODY_H).edges('|Z').fillet(.4).val()
 details=[original.raised_polygon([(-9,-1.5),(9,-1.5),(8.5,.2),(-8,.2)]),original.raised_polygon([(-1,1.2),(.1,3.5),(2.5,4.6),(.1,5.7),(-1,8),(-2.1,5.7),(-4.5,4.6),(-2.1,3.5)])]
 result=original.union(body,*details)
 assert result.isValid() and len(result.Solids())==1,'redesigned outer hat'
 return result
def capstone(team,extra=0):
 print('Building capstone '+team,flush=True)
 baseline=outer_capstone(team);wire=wp(baseline).faces('<Z').val().outerWire()
 outer=wp(baseline.translate((0,0,extra)))
 if extra:outer=outer.union(prism(wire,0,extra))
 seatwire=inward(wire,SEAT_WALL);cavitywire=inward(wire,SIDE_WALL)
 floorwire=inward(wire,SEAT_WALL+CLEARANCE);tonguewire=inward(wire,SIDE_WALL+CLEARANCE)
 cavity_top=original.BODY_H+extra-ROOF
 seat=prism(seatwire,-.1,1.3);cavity=prism(cavitywire,1.19,cavity_top-1.19)
 body=outer.cut(seat).cut(cavity)
 floor=prism(floorwire,0,1).union(prism(tonguewire,.99,.61))
 hooks=[];frames=[];pockets=[];lips=[]
 for p0,p1 in EDGES[team]:
  p0=np.array(p0,dtype=float);p1=np.array(p1,dtype=float);d=(p1-p0)/np.linalg.norm(p1-p0)
  normal=np.array([-d[1],d[0]]);mid=(p0+p1)/2
  if baseline.isInside(cq.Vector(*(mid+normal*.1),3),.001):normal=-normal
  assert not baseline.isInside(cq.Vector(*(mid+normal*.1),3),.001)
  origin=mid-normal*(SEAT_WALL+CLEARANCE);frame={'origin_xy':origin.tolist(),'normal_xy':normal.tolist(),'angle_deg':math.degrees(math.atan2(normal[1],normal[0]))}
  arm_y0=-C.arm_length/2+C.attach_length;arm_y1=C.arm_length/2+C.slot_gap/2
  long=wp(cq.Workplane('XY').box(C.slot_gap,arm_y1-arm_y0,2).val()).translate((-C.arm_width-C.slot_gap/2,(arm_y0+arm_y1)/2,.8))
  end=cq.Workplane('XY').box(C.arm_width+C.slot_gap+.5,C.slot_gap,2).translate((-(C.arm_width+C.slot_gap)/2,C.arm_length/2,.8))
  floor=floor.cut(transform(long,frame)).cut(transform(end,frame))
  hook_y=C.arm_length/2-C.hook_width*.75
  hook=transform(gen._snap_hook(1,0,C,hook_y),frame)
  assert floor.intersect(hook.translate((-.00001*normal[0],-.00001*normal[1],0))).val().Volume()>0,'hook touches floor'
  floor=floor.union(hook);hooks.append(hook)
  # The same pocket/ramp mechanism, with a bounded relief behind its barb.
  pocket=cq.Workplane('XY').box(C.hook_engagement+C.clearance+.15,C.hook_width+.35,C.pocket_height).translate((C.clearance+(C.hook_engagement+C.clearance)/2,hook_y,.2+C.pocket_height/2))
  pocket=transform(pocket,frame);body=body.cut(pocket);pockets.append(pocket);frames.append(frame)
 body=body.clean();floor=floor.clean()
 assert body.val().isValid() and floor.val().isValid() and len(body.val().Solids())==len(floor.val().Solids())==1,(team,'body valid/solids',body.val().isValid(),len(body.val().Solids()),'floor valid/solids',floor.val().isValid(),len(floor.val().Solids()))
 overlap=volume(body.intersect(floor));assert overlap<1e-6,(team,'seated overlap',overlap)
 # Void inside the original outer solid, after snapping the floor in. Includes
 # the small closure clearances; epoxy will occupy some of this nominal space.
 assert volume(floor.cut(outer,clean=False))<1e-6,(team,'floor outside outer envelope')
 interior_ml=(volume(outer)-volume(body)-volume(floor))/1000
 area=cq.Face.makeFromWires(cavitywire).Area()
 pull_checks=[]
 for dz in (.1,.2,.4,.7):
  collision=volume(body.intersect(floor.translate((0,0,-dz))))
  if .2<=dz<=.4:assert collision>1e-4,(team,'retaining hooks must block outward translation',dz,collision)
  pull_checks.append({'outward_mm':dz,'collision_mm3':collision,'capture':collision>1e-4})
 # Isolate barb insertion clearance from other floor features. An inward
 # displacement of engagement + allowance must clear the unpocketed throat.
 throat=outer.cut(seat).cut(cavity)
 for frame,hook in zip(frames,hooks):
  n=np.array(frame['normal_xy']);deflected=hook.translate((-(C.hook_engagement+.04)*n[0],-(C.hook_engagement+.04)*n[1],-.25))
  assert volume(throat.intersect(deflected))<1e-6,(team,'deflected barb throat')
  # Exact horizontal retaining underside must exist at z=.30.
  underside=[f for f in hook.val().Faces() if abs(f.Center().z-.30)<1e-5 and f.normalAt().z<-.9]
  assert underside and sum(f.Area() for f in underside)>0
 return dict(body=body,floor=floor,outer=outer,interior_ml=interior_ml,cavity_top=cavity_top,cavity_wire=cavitywire,area=area,frames=frames,pull_checks=pull_checks,height=8+extra)
def export(label,obj):
 assert obj.val().isValid() and len(obj.val().Solids())==1
 p=OUT/'models'/f'{label}.stl';weld=export_stl(obj,p)
 cq.exporters.export(obj,str(p.with_suffix('.step')))
 back=cq.importers.importStep(str(p.with_suffix('.step')));assert back.val().isValid() and len(back.val().Solids())==1
 assert abs(volume(back)-volume(obj))<.001 and np.allclose(bounds(back),bounds(obj),atol=1e-5)
 m=trimesh.load_mesh(p);deg=(m.area_faces<1e-12)
 if deg.any():m.update_faces(~deg);m.remove_unreferenced_vertices();m.export(p);m=trimesh.load_mesh(p)
 assert m.is_watertight and m.is_winding_consistent and m.body_count==1 and m.volume>0,label
 assert abs(m.volume-volume(obj))<1.0,(label,m.volume,volume(obj))
 return dict(stl=str(p.relative_to(OUT)),step=str(p.with_suffix('.step').relative_to(OUT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),step_sha256=hashlib.sha256(p.with_suffix('.step').read_bytes()).hexdigest(),volume_mm3=volume(obj),mesh_volume_mm3=float(m.volume),bounds_mm=bounds(obj).tolist(),watertight=True,mesh_bodies=1,triangles=len(m.faces),welding=weld,degenerate_triangles_removed=int(deg.sum()))
def main():
 for d in ('models','reports','previews','PRINT','profiles'):(OUT/d).mkdir(exist_ok=True)
 report=dict(units='mm',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),generator_reference=json.loads((OUT/'source/vendor/reference.json').read_text()),physical_acceptance=False,printed=False,printer_started=False,parameters=dict(side_wall_mm=SIDE_WALL,seat_wall_mm=SEAT_WALL,roof_under_raised_face_mm=ROOF,clearance_mm=CLEARANCE,snap_engagement_mm=C.hook_engagement,arm_length_mm=C.arm_length,arm_width_mm=C.arm_width,slot_gap_mm=C.slot_gap),parts={},capstones={},regulars={})
 cat=capstone('cat');witch=capstone('witch')
 # Match the complete closed void while retaining the original 8 mm height.
 # The broad hat has more XY space, allowing a thicker roof than the Cat.
 roof_add=(witch['interior_ml']-cat['interior_ml'])*1000/witch['area'];assert roof_add>0
 new_top=witch['cavity_top']-roof_add;assert new_top>2
 witch['body']=witch['body'].union(prism(witch['cavity_wire'],new_top,roof_add+.01))
 witch['cavity_top']=new_top
 witch['interior_ml']=(volume(witch['outer'])-volume(witch['body'])-volume(witch['floor']))/1000
 print('Matched capstone volume; hat roof '+str(ROOF+roof_add)+' mm',flush=True)
 target=cat['area']*(cat['cavity_top']-CAT_FILL_BOTTOM)/1000
 for team,q in (('cat',cat),('witch',witch)):
  fill_bottom=q['cavity_top']-target*1000/q['area'];assert fill_bottom>=1.8-1e-8
  fill=prism(q['cavity_wire'],fill_bottom,q['cavity_top']-fill_bottom)
  assert volume(fill.intersect(q['body']))<1e-6 and volume(fill.intersect(q['floor']))<1e-6
  assert abs(volume(fill)/1000-target)<1e-8 and abs(q['interior_ml']-cat['interior_ml'])<1e-8
  # CAD material exists for the 0.8 mm roof, with no cavity behind raised detail.
  assert bounds(q['outer'])[1,2]-q['height']<1e-5
  printed=q['body'].rotate((0,0,0),(1,0,0),180).translate((0,0,q['height']))
  report['parts'][f'{team}-capstone-body']=export(f'{team}-capstone-body',printed)
  report['parts'][f'{team}-capstone-floor']=export(f'{team}-capstone-floor',q['floor'])
  cq.exporters.export(cq.Compound.makeCompound([q['body'].val(),q['floor'].val()]),str(OUT/'models'/f'{team}-capstone-assembled.step'))
  cq.exporters.export(fill,str(OUT/'models'/f'{team}-capstone-usable-fill.step'))
  report['capstones'][team]=dict(height_mm=q['height'],height_increase_mm=q['height']-8,usable_fill_ml=volume(fill)/1000,total_closed_interior_ml=q['interior_ml'],fill_limit_depth_from_open_rim_mm=fill_bottom,headroom_above_floor_tongue_mm=fill_bottom-1.6,pull_checks=q['pull_checks'],snap_frames=q['frames'],roof_mm=original.BODY_H-q['cavity_top'],body_floor_overlap_mm3=volume(q['body'].intersect(q['floor'])),same_xy_as_original=(team=='cat'),redesigned_witch_hat=(team=='witch'),body_print_opening_up=True,support_for_face_down_raised_details=True,current_8mm_capstone_case_compatible=q['height']<=8.00001)
 for team in ('cat','witch'):
  print('Building regular '+team,flush=True)
  spec=specs.StoneSpec(height=8,engraving=specs.EngravingSpec(kind='builtin',value=team,depth=.4,scale=1.25/1.1 if team=='cat' else 1.2),texture=specs.TextureSpec(kind='none'))
  body,solved=gen.make_body(spec);floor=gen.make_floor(spec)
  overlap=volume(body.intersect(floor));assert overlap<1e-6,(team,overlap)
  assert np.allclose(bounds(body)[1]-bounds(body)[0],[20,20,8],atol=1e-6)
  stacked=cq.Compound.makeCompound([body.val(),floor.val()]);assert stacked.intersect(stacked.translate((0,0,8))).Volume()<1e-6
  pull=[]
  for dz in (.2,.4):
   collision=volume(body.intersect(floor.translate((0,0,-dz))));assert collision>1e-4;pull.append(dict(outward_mm=dz,collision_mm3=collision))
  printed=body.rotate((0,0,0),(1,0,0),180).translate((0,0,8))
  report['parts'][f'{team}-regular-body']=export(f'{team}-regular-body',printed)
  report['parts'][f'{team}-regular-floor']=export(f'{team}-regular-floor',floor)
  cq.exporters.export(stacked,str(OUT/'models'/f'{team}-regular-assembled.step'))
  report['regulars'][team]=dict(dimensions_mm=[20,20,8],ballast=solved,body_floor_overlap_mm3=overlap,pull_checks=pull,mechanism='recovered piece-generator-v1, unchanged default snap parameters',body_print_opening_up=True)
 report['equal_volume_error_ml']=abs(cat['interior_ml']-witch['interior_ml']);report['usable_volume_error_ml']=abs(report['capstones']['cat']['usable_fill_ml']-report['capstones']['witch']['usable_fill_ml'])
 report['environment']=dict(python=sys.version,executable=sys.executable,cadquery=cq.__version__,numpy=np.__version__,trimesh=trimesh.__version__)
 report['sources_sha256']={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*(OUT/'source/vendor').glob('*.py'),REPO/'v26/reference/v24/source/flat_capstones.py',REPO/'pieces/tak_pieces.py']}
 report['passed']=True;(OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':True,'capstones':{team:{k:v for k,v in q.items() if k not in ('snap_frames','pull_checks')} for team,q in report['capstones'].items()},'print_parts':len(report['parts'])},indent=2),flush=True)
if __name__=='__main__':main()
