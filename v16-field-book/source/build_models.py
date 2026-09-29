"""STEP models, full-size STLs and fit-trial STLs for the v16 field book.

Multi-colour parts are written as one STL per colour, all moved by the same
translation, so the slicer can reassemble them exactly:
stl/full/<part>.<colour>.stl
"""
from pathlib import Path
import json,sys
import cadquery as cq
import tak_book as c
from mesh_export import export_stl

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
MODELS=OUT/'models';FULL=OUT/'stl'/'full';TRIALS=OUT/'stl'/'trials';REPORTS=OUT/'reports'
for d in (MODELS,FULL,TRIALS,REPORTS):d.mkdir(parents=True,exist_ok=True)
report={'design':'v16-field-book-far-edge-buckle-snap-in-trays-no-hardware',
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

def save_group(name,parts):
    """parts: {colour: shape}. The black body sets the shared print translation."""
    body=parts['black'];bb=body.BoundingBox()
    for s in parts.values():
        sb=s.BoundingBox();assert sb.zmin>=bb.zmin-1e-6,(name,'part below body')
    t=(-bb.xmin,-bb.ymin,-bb.zmin)
    row={}
    for col,s in parts.items():
        assert s.isValid(),(name,col)
        cq.exporters.export(s,str(MODELS/f'{name}.{col}.step'))
        p=s.translate(t)
        row[col]={'solids':len(s.Solids()),'volume_mm3':round(s.Volume(),3),'print_bounds':bounds(p),
                  'stl_weld':export_stl(p,FULL/f'{name}.{col}.stl')}
    report['parts']['stl/'+name]=row
    print(name,'ok',list(parts),flush=True)

for s_ in 'AB':
    save_group(f'board-plate-{s_.lower()}',{'black':c.plate(s_),'white':c.inlay(s_),
               'orange':c.decor(s_,'orange'),'purple':c.decor(s_,'purple')})
save_group('tray-a',{'black':c.tray_body('A'),'orange':c.tray_swirl('A'),'white':c.tray_sparkles('A')})
save_group('tray-b',{'black':c.tray_body('B'),'purple':c.tray_swirl('B'),'white':c.tray_sparkles('B')})
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

# Trials: spine-end hinge pair, far-edge buckle, tray latch.
hc=c.box(c.SEAM-14,c.SEAM+14,-.5,16,-.1,c.AXZ+3.2)
ht=cq.Compound.makeCompound([c.base('A').intersect(hc),c.base('B').intersect(hc)])
p=c.print_pose(ht)
report['parts']['stl/trial-hinge-pair']={'solids':2,'stl_weld':export_stl(p,TRIALS/'trial-hinge-pair.stl')}
# Buckle: plate-A corner with the tab, and leaf B's back corner with the
# spring panel, catch ring and slot (base and plate).
bx=c.box(c.WX-28,c.WX+.1,c.WY-32,c.WY+.1,-.1,c.PLATE_Z+.1)
save('trial-buckle-tab-plate',c.plate('A').intersect(c.box(-.1,16,c.WY-22,c.WY+.1,c.PLATE_Z-.1,c.FACE+12)),TRIALS)
save('trial-buckle-socket-base',c.base('B').intersect(bx),TRIALS)
save('trial-buckle-socket-plate',c.plate('B').intersect(c.box(c.WX-20,c.WX+.1,c.WY-22,c.WY+.1,c.PLATE_Z-.1,c.FACE+.1)),TRIALS)
# Latch: front fore corner of a base and the matching front of a tray.
lc=c.box(-.1,26,-.1,40,-.1,c.PLATE_Z+.1)
save('trial-latch-base',c.base('A').intersect(lc),TRIALS)
save('trial-latch-tray',c.tray_a().intersect(c.box(-.1,30,-.1,40,-.1,c.PLATE_Z)),TRIALS)
json.dump(report,open(REPORTS/'build-report.json','w'),indent=1)
print('built')
