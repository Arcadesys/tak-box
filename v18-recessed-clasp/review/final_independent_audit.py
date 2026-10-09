from pathlib import Path
import json,hashlib,time
R=Path(__file__).resolve().parents[1]
p=R/'build.py'; data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
ns={'__file__':str(p),'__name__':'independent_review_import'}; exec(compile(data,str(p),'exec'),ns)
receiver=ns['receiver']; keeper=ns['keeper']; slider=ns['slider']; ov=ns['ov']
cache={}
def s(d=0,t=0,z=0):
 k=(d,t,z)
 if k not in cache: cache[k]=slider(d,t).translate((0,0,z))
 return cache[k]
def vol(a,b):return round(ov(a,b),8)
def row(d,t,z=0):return {'delta_mm':d,'retract_mm':t,'slider_z_mm':z,'receiver_overlap_mm3':vol(s(d,t,z),receiver),'keeper_overlap_mm3':vol(s(d,t,z),keeper)}
res={'source_sha256':sha,'cad_only':True,'source_snapshot':'review/final-source-snapshot.py','limitations':'Discrete prescribed-shape rigid overlap tests, not FEA, print force, friction, tolerance distribution, physical validation, or exhaustive arbitrary-pose search.'}
(R/'review'/'final-source-snapshot.py').write_bytes(data)
res['press_path']=[row(i*.1,0) for i in range(19)]
res['pressed_slide_and_reverse_closing_path']=[row(1.8,i*.5) for i in range(21)]
res['released_relock_path']=[row(i*.1,0) for i in range(19)]
res['normal_locked_unpressed_retract']=[row(0,t) for t in [0,.5,1,1.05,1.5,2,3,4,5,10]]
res['downward_float_unpressed_retract']=[row(0,t,-.4) for t in [0,.5,1,1.05,1.5,2,3,4,5,10]]
res['downward_float_press']=[row(d,0,-.4) for d in [0,.5,1,1.4,1.8,1.9,2]]
res['downward_float_pressed_slide']=[row(1.8,t,-.4) for t in [0,1,2,3,4,5,7,10,11,11.1,12]]
res['unpressed_forward_retention']=[row(0,t) for t in [0,-1,-2,-2.1,-2.5,-3,-4]]
res['open_rest']=[row(0,t) for t in [10,10.5,11,11.1,12]]
res['assembly_insertion_keeper_removed']=[{'forward_mm':x,'receiver_overlap_mm3':vol(s(1.8,-x),receiver)} for x in [i for i in range(71)]]
res['overtravel_floor_stop']=[row(d,0) for d in [1.8,2,2.1,2.12,2.13,2.2,2.4,2.5]]
res['keeper_lift_pressed_and_unpressed']=[{'keeper_z_mm':z,'rest_overlap':vol(keeper.translate((0,0,z)),s()),'pressed_overlap':vol(keeper.translate((0,0,z)),s(1.8)),'downward_float_overlap':vol(keeper.translate((0,0,z)),s(0,0,-.4)),'upward_float_overlap':vol(keeper.translate((0,0,z)),s(0,0,.4))} for z in [0,.2,.4,.5,.6,.8,.9,1,2]]
res['open_lift_path']=[{'keeper_z_mm':z,'receiver_overlap':vol(keeper.translate((0,0,z)),receiver),'slider_overlap':vol(keeper.translate((0,0,z)),s(0,10))} for z in [i for i in range(16)]]
res['registration']=[{'dx_mm':x,'dy_mm':y,'dz_mm':z,'receiver_overlap':vol(keeper.translate((x,y,z)),receiver),'slider_overlap':vol(keeper.translate((x,y,z)),s())} for x,y,z in [(0,0,0),(1,0,0),(1.1,0,0),(2,0,0),(4,0,0),(-1,0,0),(-1.1,0,0),(0,1,0),(0,1.1,0),(0,-1,0),(0,-1.1,0),(1,1,.4),(1.1,1.1,.4),(1,1,.8),(1.1,1.1,.8),(0,0,-.4),(0,0,-1),(0,0,-2),(0,0,-6)]]
res['envelopes']={}
for label,d,t,z in [('locked',0,0,0),('pressed',1.8,0,0),('retracted',0,10,0),('locked_upper_float',0,0,.4)]:
 bb=s(d,t,z).BoundingBox();res['envelopes'][label]=[round(v,6) for v in [bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax]]
out=R/'review'/'final-independent-probes.json';out.write_text(json.dumps(res,indent=2));print('source',sha)
for k,v in res.items():
 if isinstance(v,list):
  numeric=[r.get('receiver_overlap_mm3',r.get('receiver_overlap',0)) for r in v]
  print(k,'rows',len(v),'max_receiver_overlap',max(numeric,default=0))
print(out)
