"""Engineering STEP, full-size part STLs and fit-trial STLs for the v12 chest.

Full parts are released for convenience but are not fit-tested: print the
fit trials first. Grid inlays are separate bodies for multicolour printing.
"""
from pathlib import Path
import json,sys
import cadquery as cq
import tak_chest as c
from mesh_export import export_stl

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
MODELS=OUT/'models';MODELS.mkdir(parents=True,exist_ok=True)
STL=OUT/'stl';FULL=STL/'full';TRIALS=STL/'trials'
for d in (FULL,TRIALS):d.mkdir(parents=True,exist_ok=True)
REPORTS=OUT/'reports';REPORTS.mkdir(exist_ok=True)
report={'design':'jumanji-style-hinged-chest-board-inside-two-lift-out-lidded-trays',
        'units':'mm','physical_fit_accepted':False,'fit_selected':c.FIT,'parts':{}}

def bounds(s):
    b=s.BoundingBox();return [round(x,4) for x in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)]

def save(name,s,folder=None,flip=False,solids=1):
    assert s.isValid(),name
    assert len(s.Solids())==solids,(name,len(s.Solids()))
    row={'valid':True,'solids':solids,'bounds':bounds(s),'volume_mm3':round(s.Volume(),3)}
    if folder is None:
        cq.exporters.export(s,str(MODELS/(name+'.step')))
    else:
        pose=c.print_pose(s,flip)
        row['print_bounds']=bounds(pose)
        row['print_orientation']='top face down' if flip else 'as modelled'
        row['stl_weld']=export_stl(pose,folder/(name+'.stl'))
    report['parts'][('stl/' if folder else 'step/')+name]=row
    print(name,'ok',flush=True)

def label(shape,text,x,y,z):
    tag=cq.Workplane('XY').text(text,6,.5,font='Arial',kind='bold',combine=True).val()
    b=tag.BoundingBox()
    tag=tag.translate((x-(b.xmin+b.xmax)/2,y-(b.ymin+b.ymax)/2,z-.4))
    return shape.cut(tag).clean()

# ---- engineering STEP (assembly frame)
for side in ('left','right'):
    save(f'base-{side}',c.base(side))
    save(f'lid-{side}',c.lid(side))
    for i in range(3):save(f'grid-{i}-{side}',c.grid_inlay(i,side))
save('tray',c.tray());save('tray-lid',c.tray_lid())
for name,shape in (('assembly-closed',c.assembly(0)),
                   ('assembly-open',c.assembly(100,lift=(0,0),with_pieces=True)),
                   ('assembly-trays-out',c.assembly(100,lift=(45,45),with_pieces=True))):
    cq.exporters.export(shape,str(MODELS/(name+'.step')))
    print(name,'exported',flush=True)

# ---- full-size parts. Bases print floor-down; lids print top-down.
for side in ('left','right'):
    save(f'base-{side}',c.base(side),FULL)
    save(f'lid-{side}',c.lid(side),FULL,flip=True)
    for i in range(3):save(f'grid-{i}-{side}',c.grid_inlay(i,side),FULL)
for fit in c.LID_FITS:
    save(f'tray-{fit}',c.tray(fit),FULL)
    save(f'tray-lid-{fit}',c.tray_lid(fit),FULL,flip=True)
for i,k in enumerate(c._hourglass(c.SEAM_X,y,0,18) for y in c.KEY_Y_BASE):
    save(f'seam-key-base-{i+1}',k,FULL)
for i,k in enumerate(c.lid_key_shapes()):
    save(f'seam-key-lid-{i+1}',k,FULL)

# ---- fit trials
# Tray end: real +y end wall, lid grooves, slot rib and one crush-rib pair.
tray_crop=c.box(-1,c.TO+1,120,c.TL+2,-.1,c.TH+.1)
lid_crop=c.box(0,c.TO,120,c.TL+1,c.LID_Z[0]-.1,c.LID_Z[1]+.1)
for fit in c.LID_FITS:
    t=c.tray(fit).intersect(tray_crop)
    save(f'trial-tray-end-{fit}',label(t,fit,c.TO/2,140,c.TFLOOR),TRIALS)
    l=c.tray_lid(fit).intersect(lid_crop)
    save(f'trial-tray-lid-{fit}',label(l,fit,c.TO/2,150,c.LID_Z[1]),TRIALS,flip=True)

# Bay end with rib slot, back wall and the first base knuckle; matching lid corner.
bay_crop=c.box(-34,14,120,224,-.1,c.BASE_H+6)
lid_corner=c.box(-34,14,120,224,c.BASE_H-.5,c.BASE_H+c.LID_H+3)
save('trial-bay-hinge-base',c.base('left').intersect(bay_crop),TRIALS)
save('trial-bay-hinge-lid',c.lid('left').intersect(lid_corner),TRIALS,flip=True)

# Seam: both halves near x=82, with their key pockets, plus the real key.
seam_base=c.box(60,104,20,60,-.1,c.BASE_H+.1)
save('trial-seam-base-left',c.base('left').intersect(seam_base),TRIALS)
save('trial-seam-base-right',c.base('right').intersect(seam_base),TRIALS)
save('trial-seam-key',c._hourglass(c.SEAM_X,40,0,18),TRIALS)

json.dump(report,open(REPORTS/'build-report.json','w'),indent=1)
print('built')
