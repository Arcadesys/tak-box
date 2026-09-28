"""Engineering STEP and fit-only PLA meshes for the guarded inward-fold case.

Full-board print meshes remain held until the physical hinge/key/closure trials.
"""
from pathlib import Path
import json,sys
import cadquery as cq
import tak_drawers as v
from mesh_export import export_stl

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
MODELS=OUT/'models';MODELS.mkdir(parents=True,exist_ok=True)
REPORTS=OUT/'reports';REPORTS.mkdir(parents=True,exist_ok=True)
report={'design':'guarded-inward-fold-face-trays-recessed-board-catch',
        'units':'mm','physical_fit_accepted':False,
        'full_board_print_files_released':False,
        'key_fit_selected':v.KEY_FIT,'closure_fit_selected':v.CLOSURE_FIT,
        'case_x_bounds':v.CASE_X,'parts':{}}

def bounds(s):
    b=s.BoundingBox()
    return [round(x,6) for x in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)]

def save(name,s,stl=False,solids=1):
    assert s.isValid(),name
    assert len(s.Solids())==solids,(name,len(s.Solids()),solids)
    cq.exporters.export(s,str(MODELS/(name+'.step')))
    row={'valid':True,'solids':solids,'bounds':bounds(s),
         'volume_mm3':round(s.Volume(),6)}
    if stl:
        pose=v.print_pose(s)
        row['print_pose']='panel_flat_back_or_tray_floor_down'
        row['print_bounds']=bounds(pose)
        row['stl_weld']=export_stl(pose,MODELS/(name+'.stl'))
    report['parts'][name]=row
    print(name,'valid',flush=True)

def label_coupon(shape,label,x,y,top=v.TOP):
    # Six millimetre letter in a clear backing patch, away from fit surfaces.
    tag=cq.Workplane('XY').text(label,6,.5,font='Arial',kind='bold',combine=True).val()
    b=tag.BoundingBox()
    tag=tag.translate((x-(b.xmin+b.xmax)/2,
                       y-(b.ymin+b.ymax)/2,top-.4))
    return shape.cut(tag).clean()

for n,s in v.mechanical_parts().items():save(n,s)
save('pip-board-engineering',v.top_assembly(),solids=3)

# One entire x end keeps both PIP axes, the full fixed protection contour,
# and both fitted open stops. It is narrow enough to print as a single trial.
end_crop=v.box(-20.5,30,-2.3,207.3,-.1,28)
end_parts=[v.wing(0).intersect(end_crop),v.center().intersect(end_crop),
           v.wing(2).intersect(end_crop)]
save('fit-protected-hinge-frame',cq.Compound.makeCompound(end_parts),
     stl=True,solids=3)
save('fit-stop-shoe-left',v.stop_shoe('left'),stl=True)

# Actual fixed post and female ear, including their matching short seat pads.
key_crop=v.box(-8.1,16,6,20,-.1,25.1)
save('fit-key-wing',v.wing(0).intersect(key_crop),stl=True)
for fit in v.FITS:
    sample=v.tray(0,fit).intersect(key_crop)
    save('fit-key-tray-'+fit,
         label_coupon(sample,fit,9,13,v.TRAY_FLOOR_TOP),stl=True)

# The right end is representative of the mirrored left release. Every coupon
# retains its backing, rounded outside skin, press mouth, flex root and stop.
catch_crop=v.box(208,225.5,30,54,-.1,28)
receiver_crop=v.box(208,225.5,151,173,-.1,25.1)
for fit in v.FITS:
    sample=v.wing(0,fit).intersect(catch_crop)
    save('fit-recessed-catch-'+fit,
         label_coupon(sample,fit,214.5,33.7),stl=True)
save('fit-recessed-receiver',v.wing(2).intersect(receiver_crop),stl=True)

# Longer follow-up trials check the four-key spacing and real filled-tray form.
# Their panels retain the new protective cheek and recessed closure.
fixture=v.wing(0).intersect(v.box(-20.5,225.5,-2.3,75,-.1,28))
fixture=fixture.cut(v.box(10,195,10,65,-.1,4.1)).clean()
save('full-length-guarded-key-frame-trial',fixture,stl=True)
save('full-length-tray-a-trial',v.tray(0),stl=True)
save('full-length-tray-b-trial',v.tray(2),stl=True)

for name,shape in (
    ('assembly-open',v.assembly(0)),
    ('assembly-closed',v.assembly(-90)),
    ('assembly-access',v.assembly(0,with_trays=False)),
    ('assembly-lifted',v.assembly(0,lift=v.TRAY_LIFT)),
    ('assembly-closed-loaded-envelope',v.assembly(-90,with_pieces=True)),
):
    assert shape.isValid(),name
    cq.exporters.export(shape,str(MODELS/(name+'.step')))
    report['parts'][name]={'valid':True,'solids':len(shape.Solids()),
                           'bounds':bounds(shape),
                           'volume_mm3':round(shape.Volume(),6)}
    print(name,'exported',flush=True)
(REPORTS/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
