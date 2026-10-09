"""Midpoint capstone cups and a single-filament four-piece sample. Units mm."""
from pathlib import Path
import importlib.util, json, hashlib, subprocess, sys, math
import cadquery as cq
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
module=importlib.util.spec_from_file_location('weighted_v1',REPO/'pieces/weighted-flat-capstones-v1/source/build.py')
v1=importlib.util.module_from_spec(module);module.loader.exec_module(v1)
volume=v1.volume;bounds=v1.bounds;wp=v1.wp;prism=v1.prism;inward=v1.inward;transform=v1.transform
MID=4.;BOND_GAP=.05;BASE=.9;LIP_OUT=1.45;RECESS=1.2;LIP_TOP=5.35;RECESS_TOP=5.55
ARM_INNER=2.2;ARM_WIDTH=2.8;FLEX_START=1.65;ARM_END=5.35
SHOULDER=4.25;HOOK_TOP=4.65;PROJECTION=.6;POCKET_OUT=.75
FILL_HEADROOM=.25;GLUE_RESERVE_ML=.03
EDGES=v1.EDGES

def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))

def cut(a,b):return a.cut(b,clean=False)
def common(a,b):return a.intersect(b,clean=False)

def valid_one(obj,label):
    assert obj.val().isValid() and len(obj.val().Solids())==1 and volume(obj)>0,label

def frame_for(baseline,p0,p1):
    p0=np.array(p0,float);p1=np.array(p1,float);d=(p1-p0)/np.linalg.norm(p1-p0)
    normal=np.array([-d[1],d[0]]);mid=(p0+p1)/2
    if baseline.isInside(cq.Vector(*(mid+normal*.1),3),.001):normal=-normal
    return dict(origin_xy=mid.tolist(),normal_xy=normal.tolist(),angle_deg=math.degrees(math.atan2(normal[1],normal[0])))

def capstone(team):
    print('Building equal-half '+team,flush=True)
    baseline=v1.outer_capstone(team);outer=wp(baseline)
    wire=outer.faces('<Z').val().outerWire()
    wall=1.6 if team=='cat' else 2.2
    inner=inward(wire,wall);lip_inner=inward(wire,wall+.6)
    # Equal nominal external depths, with a symmetric 0.05 mm epoxy bond gap.
    lower=common(outer,box(-20,20,-20,20,-.1,MID-BOND_GAP/2))
    lower=cut(lower,prism(inner,BASE,8))
    lip=prism(inward(wire,LIP_OUT),MID-BOND_GAP/2-.01,LIP_TOP-(MID-BOND_GAP/2)+.01)
    lip=cut(lip,prism(lip_inner,MID-.1,3))
    lower=lower.union(lip,clean=False)
    upper=common(outer,box(-20,20,-20,20,MID+BOND_GAP/2,8.1))
    upper=cut(upper,prism(inward(wire,RECESS),MID-.1,RECESS_TOP-(MID-.1)))
    upper=cut(upper,prism(inner,RECESS_TOP-.01,6-(RECESS_TOP-.01)))
    frames=[];hooks=[];arms=[];guards=[];exclusions=[];pockets=[]
    for p0,p1 in EDGES[team]:
        frame=frame_for(baseline,p0,p1);frames.append(frame)
        local=lambda obj:transform(obj,frame)
        # Inward flexing fingers are rooted below the midpoint. Their relief
        # slots stop behind a continuous external wall, not in the epoxy seam.
        stem=box(-ARM_INNER,-LIP_OUT,-ARM_WIDTH/2,ARM_WIDTH/2,BASE-.05,ARM_END)
        root=box(-ARM_INNER,-1.1,-ARM_WIDTH/2-.35,ARM_WIDTH/2+.35,BASE-.05,FLEX_START+.01)
        lower=lower.union(local(stem),clean=False).union(local(root),clean=False)
        for sign in (-1,1):
            y0,y1=(ARM_WIDTH/2,ARM_WIDTH/2+.4) if sign==1 else (-ARM_WIDTH/2-.4,-ARM_WIDTH/2)
            lower=cut(lower,local(box(-3.8,-1.1,y0,y1,FLEX_START,ARM_END+.05)))
        lower=cut(lower,local(box(-LIP_OUT,-1.1,-ARM_WIDTH/2,ARM_WIDTH/2,FLEX_START,4.05)))
        # Clear the inner side even on the thicker Witch lip. Guard walls keep
        # steel shot/sand away from the tab's deflection space.
        lower=cut(lower,local(box(-3.8,-ARM_INNER,-ARM_WIDTH/2,ARM_WIDTH/2,FLEX_START,ARM_END+.05)))
        guard=box(-3.6,-2.9,-2.6,2.6,BASE-.05,LIP_TOP)
        for sign in (-1,1):
            y0,y1=(2.0,2.6) if sign==1 else (-2.6,-2.0)
            guard=guard.union(box(-3.6,-1.4,y0,y1,BASE-.05,LIP_TOP),clean=False)
        guard=local(guard);guards.append(guard);lower=lower.union(guard,clean=False)
        points=[(-LIP_OUT,SHOULDER),(-LIP_OUT+PROJECTION,SHOULDER),(-LIP_OUT+PROJECTION,HOOK_TOP),(-LIP_OUT,ARM_END)]
        hook=cq.Workplane('XZ').polyline(points).close().extrude(ARM_WIDTH/2,both=True)
        hook=local(hook);hooks.append(hook);lower=lower.union(hook,clean=False)
        arm=local(stem);arms.append(arm)
        pocket=local(box(-1.3,-POCKET_OUT,-ARM_WIDTH/2-.2,ARM_WIDTH/2+.2,4.05,5.30))
        pockets.append(pocket);upper=cut(upper,pocket)
        exclusions.append(local(box(-3.6,.1,-2.6,2.6,BASE,ARM_END+.1)))
    lower=lower.clean();upper=upper.clean()
    valid_one(lower,team+' lower');valid_one(upper,team+' upper')
    assert volume(common(lower,upper))<1e-6,(team,'assembled overlap')
    assert volume(cut(lower,outer))<1e-6,(team,'lower outside silhouette')
    assert volume(cut(upper,outer))<1e-6,(team,'upper outside silhouette')
    checks=[]
    for dz in (.1,.3,.5,.7):
        collision=volume(common(lower,upper.translate((0,0,dz))))
        if dz>=.3:assert collision>1e-4,(team,'barbs do not obstruct separation',dz,collision)
        checks.append(dict(upper_withdrawal_mm=dz,interference_mm3=collision))
    for frame,hook,arm in zip(frames,hooks,arms):
        n=np.array(frame['normal_xy']);delta=(-(PROJECTION-(LIP_OUT-RECESS)+.05)*n[0],-(PROJECTION-(LIP_OUT-RECESS)+.05)*n[1],0)
        deflected=hook.translate(delta)
        throat=common(outer,box(-20,20,-20,20,4.025,6.05))
        throat=cut(throat,prism(inward(wire,RECESS),3.9,1.66))
        assert volume(common(throat,deflected))<1e-6,(team,'deflected hook throat')
        assert volume(common(arm.translate(delta),wp(cq.Compound.makeCompound([q.val() for q in guards]))))<1e-6,(team,'arm guard blocks deflection')
        shoulder=[f for f in hook.val().Faces() if abs(f.Center().z-SHOULDER)<1e-6 and f.normalAt().z<-.9]
        assert shoulder and abs(sum(f.Area() for f in shoulder)-ARM_WIDTH*PROJECTION)<1e-5
    excluded=wp(cq.Compound.makeCompound([q.val() for q in exclusions]))
    def fill_to(z):
        lip_base=MID-BOND_GAP/2-.01
        q=prism(inner,BASE,min(z,lip_base)-BASE)
        if z>lip_base:q=q.union(prism(lip_inner,lip_base,z-lip_base),clean=False)
        return cut(q,excluded)
    return dict(lower=lower,upper=upper,outer=outer,inner=inner,lip_inner=lip_inner,wire=wire,wall=wall,roof_top=6.,frames=frames,checks=checks,fill_to=fill_to,pockets=pockets)

def export(label,obj):
    valid_one(obj,label);path=OUT/'models'/f'{label}.stl'
    welded=v1.export_stl(obj,path);cq.exporters.export(obj,str(path.with_suffix('.step')))
    back=cq.importers.importStep(str(path.with_suffix('.step')))
    valid_one(back,label+' STEP');assert abs(volume(back)-volume(obj))<.001 and np.allclose(bounds(back),bounds(obj),atol=1e-5)
    m=trimesh.load_mesh(path);deg=m.area_faces<1e-12
    if deg.any():m.update_faces(~deg);m.remove_unreferenced_vertices();m.export(path);m=trimesh.load_mesh(path)
    assert m.is_watertight and m.is_winding_consistent and m.body_count==1 and m.volume>0,label
    assert abs(m.volume-volume(obj))<1.,(label,m.volume,volume(obj))
    return dict(stl=str(path.relative_to(OUT)),step=str(path.with_suffix('.step').relative_to(OUT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),volume_mm3=volume(obj),mesh_volume_mm3=float(m.volume),bounds_mm=bounds(obj).tolist(),watertight=True,mesh_bodies=1,triangles=len(m.faces),welding=welded)

def textured_cat(body):
    tools=[]
    for row,z in enumerate((2.4,4.3,6.2)):
        for i in range(-3,4):
            x=i*2.4+(1.2 if row%2 else 0)
            if abs(x)>7.2:continue
            d=.7;points=[(x-d,z),(x,z+d),(x+d,z),(x,z-d)]
            tool=cq.Workplane('XZ',origin=(0,-10.05,0)).polyline(points).close().extrude(-.35)
            tools.append(tool.val())
    compound=wp(cq.Compound.makeCompound(tools));out=body
    for angle in (0,90,180,270):out=cut(out,compound.rotate((0,0,0),(0,0,1),angle))
    out=out.clean();valid_one(out,'reverse diamond Cat')
    assert np.allclose(bounds(out),bounds(body),atol=1e-6)
    for z0,z1 in ((0,1.6),(7.1,8.01)):
        removed=common(cut(body,out),box(-11,11,-11,11,z0,z1))
        assert volume(removed)<1e-6,'texture entered closure or stacking faces'
    return out,dict(kind='recessed diamond pockets',depth_mm=.3,diamond_width_mm=1.4,diamond_height_mm=1.4,pitch_mm=2.4,row_centres_mm=[2.4,4.3,6.2],faces=4,added_material_mm3=volume(cut(out,body)),removed_mm3=volume(body)-volume(out),closure_and_stacking_faces_unchanged=True)

def main():
    for name in ('models','reports','PRINT','previews'):(OUT/name).mkdir(exist_ok=True)
    caps={team:capstone(team) for team in ('cat','witch')}
    cat=caps['cat'];witch=caps['witch']
    closed=lambda q:(volume(q['outer'])-volume(q['lower'])-volume(q['upper']))/1000
    # Match closed space by thickening the Witch roof inside its unchanged
    # silhouette. Both internal lips must retain their ceiling clearance.
    extra=(closed(witch)-closed(cat))*1000/cq.Face.makeFromWires(witch['inner']).Area()
    assert extra>0,'Witch cavity area/roof needs revision'
    new_top=6.-extra;assert new_top>=RECESS_TOP+.05,(new_top,'lip ceiling clearance')
    witch['upper']=witch['upper'].union(prism(witch['inner'],new_top,extra+.01)).clean();witch['roof_top']=new_top
    valid_one(witch['upper'],'Witch matched upper')
    assert abs(closed(cat)-closed(witch))<1e-7
    capacity={team:volume(q['fill_to'](LIP_TOP-FILL_HEADROOM))/1000 for team,q in caps.items()}
    target=min(capacity.values())-GLUE_RESERVE_ML;assert target>.65
    report=dict(units='mm',base_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),physical_evidence=dict(source='user report relayed by coordinating chat',v1_regular_snaps='worked in user test',v1_cat_capstone='printed; seats without a click or clicks then separates',v1_witch_capstone='unprinted/retention untested',new_v2_retention_verified=False),quantity=dict(logical_pieces=4,printable_components=8,full_sets=False),parts={},capstones={},regulars={},parameters=dict(midpoint_mm=MID,nominal_external_half_depth_mm=4.,epoxy_seam_gap_mm=BOND_GAP,lip_top_mm=LIP_TOP,lip_recess_clearance_mm=LIP_OUT-RECESS,radial_snap_engagement_mm=PROJECTION-(LIP_OUT-RECESS),barb_width_mm=ARM_WIDTH,barb_plateau_thickness_mm=HOOK_TOP-SHOULDER,arm_radial_thickness_mm=ARM_INNER-LIP_OUT,flex_start_mm=FLEX_START,protected_finger_cavity=True,minimum_fill_headroom_mm=FILL_HEADROOM,glue_reserve_ml=GLUE_RESERVE_ML),physical_acceptance=False,printer_started=False)
    for team,q in caps.items():
        lo,hi=BASE+.01,LIP_TOP-FILL_HEADROOM
        for _ in range(25):
            mid=(lo+hi)/2
            if volume(q['fill_to'](mid))/1000>target:hi=mid
            else:lo=mid
        fill=q['fill_to']((lo+hi)/2);assert abs(volume(fill)/1000-target)<1e-6
        assert volume(common(fill,q['lower']))<1e-6 and volume(common(fill,q['upper']))<1e-6,(team,'fill overlap',volume(common(fill,q['lower'])),volume(common(fill,q['upper'])))
        report['parts'][f'{team}-capstone-lower']=export(f'{team}-capstone-lower',q['lower'])
        printed_upper=q['upper'].rotate((0,0,0),(1,0,0),180).translate((0,0,8))
        report['parts'][f'{team}-capstone-upper']=export(f'{team}-capstone-upper',printed_upper)
        assembled=cq.Compound.makeCompound([q['lower'].val(),q['upper'].val()]);cq.exporters.export(assembled,str(OUT/'models'/f'{team}-capstone-assembled.step'))
        cq.exporters.export(fill,str(OUT/'models'/f'{team}-capstone-usable-fill.step'))
        report['capstones'][team]=dict(external_envelope_mm=[26,20,8],nominal_external_half_depths_mm=[4,4],seam_centre_z_mm=4.,bond_gap_mm=BOND_GAP,hidden_lip_above_midpoint_mm=LIP_TOP-MID,usable_fill_ml=volume(fill)/1000,closed_void_before_glue_ml=closed(q),safe_fill_limit_z_from_bottom_mm=(lo+hi)/2,fill_surface_below_lip_mm=LIP_TOP-(lo+hi)/2,headroom_and_glue_capacity_ml=capacity[team]-volume(fill)/1000,roof_mm=6.8-q['roof_top'],minimum_main_side_wall_mm=q['wall'],minimum_receiver_wall_at_pocket_mm=POCKET_OUT,straight_pull_checks=q['checks'],snap_frames=q['frames'],body_halves_overlap_mm3=volume(common(q['lower'],q['upper'])),same_external_silhouette_as_v1=True,physical_retention_verified=False)
    for team in ('cat','witch'):
        print('Building '+team+' regular',flush=True)
        spec=v1.specs.StoneSpec(height=8,engraving=v1.specs.EngravingSpec(kind='builtin',value=team,depth=.4,scale=1.25/1.1 if team=='cat' else 1.2),texture=v1.specs.TextureSpec(kind='none'))
        body,solved=v1.gen.make_body(spec);floor=v1.gen.make_floor(spec)
        texture={'kind':'unchanged smooth sides'}
        if team=='cat':body,texture=textured_cat(body)
        assert volume(common(body,floor))<1e-6
        original_floor=cq.importers.importStep(str(REPO/'pieces/weighted-flat-capstones-v1/models'/f'{team}-regular-floor.step'))
        assert volume(cut(floor,original_floor))+volume(cut(original_floor,floor))<1e-6,'working regular floor changed'
        printed=body.rotate((0,0,0),(1,0,0),180).translate((0,0,8))
        report['parts'][f'{team}-regular-body']=export(f'{team}-regular-body',printed)
        report['parts'][f'{team}-regular-floor']=export(f'{team}-regular-floor',floor)
        assembled=cq.Compound.makeCompound([body.val(),floor.val()]);cq.exporters.export(assembled,str(OUT/'models'/f'{team}-regular-assembled.step'))
        assert assembled.intersect(assembled.translate((0,0,8))).Volume()<1e-6
        report['regulars'][team]=dict(dimensions_mm=[20,20,8],ballast=solved,texture=texture,closure_architecture='unchanged V1 body / flat snap floor / epoxy',floor_same_as_v1=True,physical_texture_acceptance=False)
    report['equal_closed_volume_error_ml']=abs(closed(cat)-closed(witch));report['equal_usable_volume_error_ml']=abs(report['capstones']['cat']['usable_fill_ml']-report['capstones']['witch']['usable_fill_ml'])
    report['environment']=dict(python=sys.version,executable=sys.executable,cadquery=cq.__version__,numpy=np.__version__,trimesh=trimesh.__version__)
    sources=[Path(__file__),REPO/'pieces/weighted-flat-capstones-v1/source/build.py',*(REPO/'pieces/weighted-flat-capstones-v1/source/vendor').glob('*.py'),REPO/'v26/reference/v24/source/flat_capstones.py',REPO/'pieces/tak_pieces.py']
    report['source_sha256']={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report['passed']=True;(OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'print_parts':len(report['parts']),'capstones':{t:{k:v for k,v in q.items() if k not in ('snap_frames','straight_pull_checks')} for t,q in report['capstones'].items()}},indent=2),flush=True)
if __name__=='__main__':main()
