"""Digital checks for the v13 book. Writes reports/geometry-verification.json.
Sampled motion and valid solids do not establish strength, force or fit."""
from pathlib import Path
import json
import cadquery as cq
import tak_book as c

OUT=Path(__file__).resolve().parent.parent
(OUT/'reports').mkdir(exist_ok=True)
report={}
TOL=.05

def ov(a,b):return a.intersect(b).Volume()
def worst(A,B):return max(ov(a,b) for a in A for b in B)
def record(name,ok,detail):
    report[name]={'pass':bool(ok),'detail':detail}
    print('PASS' if ok else 'FAIL',name,detail,flush=True)
    assert ok,name

parts={'base-A':c.base('A'),'base-B':c.base('B'),'plate-A':c.plate('A'),'plate-B':c.plate('B'),
       'inlay-A':c.inlay('A'),'inlay-B':c.inlay('B'),'tray':c.tray_a(),'clasp':c.clasp_flat()}
record('valid-single-solids',all(p.isValid() and len(p.Solids())==1 for p in parts.values()),
       {k:len(p.Solids()) for k,p in parts.items()})

A=c.leaf_a();B=c.leaf_b(0)
allp=A+B+[c.clasp(90)]
m=max(ov(a,b) for i,a in enumerate(allp) for b in allp[i+1:])
record('open-flat-no-overlap',m<TOL,{'max_mm3':round(m,4)})

sweep={a:round(worst(A+[c.clasp(90)],c.leaf_b(a)),4) for a in range(0,181,5)}
record('fold-sweep-0-180-clear',all(v<TOL for v in sweep.values()),{'max_by_angle':sweep})

over={a:round(worst([c.base('A')],[c.fold(c.base('B'),a)]),3) for a in (-1,-2,-4)}
record('open-stop-engages-by-2deg',over[-2]>TOL,over)

closed=A+c.leaf_b(180)
top=max(p.BoundingBox().zmax for p in closed)
record('closed-board-inside',abs(top-2*c.FACE)<3.1,
       {'closed_height_mm':round(top,2),'faces_meet_at_z':c.FACE,
        'board_faces_exposed':False})
k=c.clasp(0)
record('closed-clasp-locked-clear',worst([k],closed)<TOL,{'max_mm3':round(worst([k],closed),4)})
hold=ov(k,c.fold(c.base('B'),179))
record('closed-clasp-holds-leaf-B',hold>TOL,{'overlap_if_B_opens_1deg':round(hold,3)})
cs={a:round(worst([c.clasp(a)],closed),4) for a in range(0,91,10)}
record('clasp-swing-0-90-clear',all(v<TOL for v in cs.values()),cs)

tr={}
for side in 'AB':
    fixed=[c.base(side),c.plate(side)]
    row={p:round(worst([c.tray(side,p)],fixed),3) for p in (0,1,2,4,6,8,10,20,60,100,132)}
    row['detent_depth_mm']=c.DETENT_H
    row['wall_flex_needed_mm']=round(c.DETENT_H-c.CLR-.0,2)
    tr[side]=row
ok=all(r[0]<TOL and all(r[p]<TOL for p in (10,20,60,100,132)) for r in tr.values())
record('tray-removable-only-detent',ok,tr)
# A tray in the closed book (leaf B upside down) must still be captured.
res={}
for side,leaf in (('A',A),('B',c.leaf_b(180))):
    res[side]=round(worst([leaf[3]],leaf[:2]),4)
record('trays-clear-in-closed-book',all(v<TOL for v in res.values()),res)

res={}
for side in 'AB':
    pb=c.piece_boxes(side);t=c.tray(side)
    res[side]={'vs_tray':round(max(ov(p,t) for p in pb),4),
               'between':round(max(ov(p,q) for i,p in enumerate(pb) for q in pb[i+1:]),4),
               'under_plate_mm':round(c.PLATE_Z-max(p.BoundingBox().zmax for p in pb),2)}
record('pieces-fit-each-tray',all(r['vs_tray']<TOL and r['between']<TOL and r['under_plate_mm']>=.3 for r in res.values()),
       {'per_tray':'21 flats as 11 two-high stacks + capstone lying down',**res})

bo=cq.Compound.makeCompound(A+B+[c.clasp(90)]).BoundingBox()
bc=cq.Compound.makeCompound(closed+[k]).BoundingBox()
record('sizes',True,{'open_xyz':[round(bo.xlen,1),round(bo.ylen,1),round(bo.zlen,1)],
                     'closed_xyz':[round(bc.xlen,1),round(bc.ylen,1),round(bc.zlen,1)],
                     'pitch':c.P,'field':5*c.P})
hinged=cq.Compound.makeCompound([c.base('A'),c.base('B')])
def ext(s):b=s.BoundingBox();return [round(b.xlen,1),round(b.ylen,1),round(b.zlen,1)]
beds={'hinged-bases':ext(hinged),'plate':ext(c.plate('A')),'tray':ext(c.tray_a()),'clasp':ext(c.clasp_flat())}
record('fits-256-bed',all(max(v)<=250 for v in beds.values()),beds)
json.dump(report,open(OUT/'reports'/'geometry-verification.json','w'),indent=1)
print('ALL PASS')
