"""STEP models, full-size STLs and fit-trial STLs for the v13 book."""
from pathlib import Path
import json,sys
import cadquery as cq
import tak_book as c
from mesh_export import export_stl

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
MODELS=OUT/'models';FULL=OUT/'stl'/'full';TRIALS=OUT/'stl'/'trials';REPORTS=OUT/'reports'
for d in (MODELS,FULL,TRIALS,REPORTS):d.mkdir(parents=True,exist_ok=True)
report={'design':'fold-in-half-book-board-inside-two-slide-out-trays-m3-clasp',
        'units':'mm','physical_fit_accepted':False,'parts':{}}

def bounds(s):
    b=s.BoundingBox();return [round(x,4) for x in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)]

def save(name,s,folder=None,pose='as modelled'):
    assert s.isValid() and len(s.Solids())==1,name
    row={'bounds':bounds(s),'volume_mm3':round(s.Volume(),3)}
    if folder is None:
        cq.exporters.export(s,str(MODELS/(name+'.step')))
    else:
        if pose=='flip':p=c.print_pose(s,True)
        elif pose=='clasp':p=c.print_pose(s.rotate((0,0,0),(1,0,0),-90))
        else:p=c.print_pose(s)
        row['print_orientation']=pose;row['print_bounds']=bounds(p)
        row['stl_weld']=export_stl(p,folder/(name+'.stl'))
    report['parts'][('stl/' if folder else 'step/')+name]=row
    print(name,'ok',flush=True)

named={'plate-a':(c.plate('A'),'as modelled'),'plate-b':(c.plate('B'),'as modelled'),
       'grid-inlay-a':(c.inlay('A'),'as modelled'),'grid-inlay-b':(c.inlay('B'),'as modelled'),
       'tray':(c.tray_a(),'as modelled'),'clasp':(c.clasp_flat(),'clasp')}
for n,(s_,pose) in named.items():
    save(n,s_);save(n,s_,FULL,pose)
save('base-a',c.base('A'));save('base-b',c.base('B'))
# The two bases print together, open flat, with the hinge in place.
hinged=cq.Compound.makeCompound([c.base('A'),c.base('B')])
cq.exporters.export(hinged,str(MODELS/'bases-hinged.step'))
pose=c.print_pose(hinged)
report['parts']['stl/bases-hinged-print-in-place']={'solids':2,'bounds':bounds(pose),
    'stl_weld':export_stl(pose,FULL/'bases-hinged-print-in-place.stl')}
print('bases-hinged ok',flush=True)
for n,a_ in (('assembly-closed',c.assembly(180)),('assembly-open',c.assembly(0)),
             ('assembly-trays-out',c.assembly(0,(70,70)))):
    cq.exporters.export(a_,str(MODELS/(n+'.step')));print(n,'exported',flush=True)

# Trials: spine-end hinge pair, clasp corner pair plus clasp, detent corner.
hc=c.box(c.SEAM-14,c.SEAM+14,-.5,16,-.1,c.AXZ+3.2)
ht=cq.Compound.makeCompound([c.base('A').intersect(hc),c.base('B').intersect(hc)])
p=c.print_pose(ht)
report['parts']['stl/trial-hinge-pair']={'solids':2,'stl_weld':export_stl(p,TRIALS/'trial-hinge-pair.stl')}
cc=c.box(-.1,24,c.WY-14,c.WY+4,-.1,c.FACE+.1)
save('trial-clasp-base-a',c.base('A').intersect(cc),TRIALS)
ccb=c.box(c.WX-24,c.WX+.1,c.WY-14,c.WY+4,-.1,c.FACE+.1)
save('trial-clasp-base-b',c.base('B').intersect(ccb),TRIALS)
save('trial-clasp',c.clasp_flat(),TRIALS,'clasp')
# Latch: front fore corner of a base and the matching front of a tray.
lc=c.box(-.1,26,-.1,40,-.1,c.PLATE_Z+.1)
save('trial-latch-base',c.base('A').intersect(lc),TRIALS)
save('trial-latch-tray',c.tray_a().intersect(c.box(-.1,30,-.1,40,-.1,c.PLATE_Z)),TRIALS)
json.dump(report,open(REPORTS/'build-report.json','w'),indent=1)
print('built')
