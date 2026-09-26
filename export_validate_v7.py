"""v7 checks and print STLs: tak_case_pin's collision sweeps on the v7 parts,
plus the new feet, notches, flush ends and rubber-foot pockets.
Writes pin-board-v7/*.stl in the same print poses as export_pin_board.py."""
from pathlib import Path
import cadquery as cq
import tak_case_v7 as v
import tak_pinfit as f

HERE=Path(__file__).resolve().parent
OUT=HERE/'pin-board-v7'; OUT.mkdir(exist_ok=True)
S=v.S

w0,l0=map(v.sol,v.lid_pair(0)); w2,l2=map(v.sol,v.lid_pair(2))
center=v.sol(v.center_row())
overlays=[v.overlay(i) for i in range(3)]
parts={'wing A':w0,'center':center,'wing B':w2,'lid A':l0,'lid B':l2}
for n,s in parts.items():
    assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
for s in (w0,w2): assert abs(s.BoundingBox().zmin+20.1)<1e-5
assert abs(center.BoundingBox().zmin+20.1)<0.05   # feet stop 2 deg short of vertical
for s in (w0,w2,l0,l2,center):
    b=s.BoundingBox(); assert b.xmin>-1e-6 and b.xmax<S+1e-6

def clear(a,b): return a.intersect(b).Volume()
def check(label,worst):
    print('%-34s max overlap %.4f mm3'%(label,worst)); assert worst<1e-3
def sweep(label,pairs,angles):
    check(label,max(clear(a,b(deg)) for deg in angles for a,b in pairs))

for pin in ('seam0','seam1','lid0','lid2'):
    fil=v.filament(pin)
    check(f'filament {pin}',max(clear(fil,s) for s in parts.values()))
sweep('lid A open 0-110',[(w0,lambda d:v.lid_open(l0,0,d))],range(0,111,10))
sweep('lid B open 0-110',[(w2,lambda d:v.lid_open(l2,2,d))],range(0,111,10))
sweep('lid A overlay open 0-110',[(w0,lambda d:v.lid_open(overlays[0],0,d))],range(0,111,10))
sweep('lid B overlay open 0-110',[(w2,lambda d:v.lid_open(overlays[2],2,d))],range(0,111,10))
sweep('wing A + lid fold 0-90',[(center,lambda d:v.posed(w0,0,d)),(center,lambda d:v.posed(l0,0,d))],range(0,91,5))
sweep('wing B + lid fold 0-90',[(center,lambda d:v.posed(w2,2,d)),(center,lambda d:v.posed(l2,2,d))],range(0,91,5))
side=lambda w,l,i,d:v.posed(w,i,d).fuse(v.posed(l,i,d))
check('side A vs side B fold 0-90',max(clear(side(w0,l0,0,d),side(w2,l2,2,d)) for d in range(0,91,10)))

# fitted bumpers: Ø8 hemisphere caps standing 0.8 mm proud of each wing floor
def bumpers(index):
    caps=None
    for x,y in v.BUMPERS[index]:
        # sphere cap of a Ø8 x 2.2 dome seated 1.4 mm deep: only the proud 0.8 mm matters
        cap=cq.Solid.makeCylinder(3.2,0.8,cq.Vector(x,y,v.FLOOR_Z-0.8))
        caps=cap if caps is None else caps.fuse(cap)
    return caps
check('bumpers A vs folded side B',clear(v.posed(bumpers(0),0,90),side(w2,l2,2,90)))
check('bumpers B vs folded side A',clear(v.posed(bumpers(2),2,90),side(w0,l0,0,90)))
check('bumpers A vs folded center',clear(v.posed(bumpers(0),0,90),center))
check('bumpers B vs folded center',clear(v.posed(bumpers(2),2,90),center))

folded=[center,v.posed(w0,0,90),v.posed(l0,0,90),v.posed(w2,2,90),v.posed(l2,2,90)]
allp=folded[0]
for s in folded[1:]: allp=allp.fuse(s)
b=allp.BoundingBox()
print('folded envelope %.1f x %.1f x %.1f mm, fill %.0f%%'%(b.xlen,b.ylen,b.zlen,
      100*allp.Volume()/(b.xlen*b.ylen*b.zlen)))
# flush ends: how much of the end-on silhouette is solid 0.3 mm in from each end
for x in (0.3,S-0.3):
    cut=allp.intersect(cq.Workplane('XY').box(0.2,200,200).translate((x,102.5,-40)).val())
    print('end section at x=%.1f: %.0f%% of its %.0f x %.0f mm rectangle'%(
          x,100*cut.Volume()/0.2/(b.ylen*b.zlen),b.ylen,b.zlen))

def pose(s,mode):
    if mode=='face_down': s=s.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
    return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))
stl={'center-row':pose(center,'face_down'),
     'wing-a':pose(w0,'bottom_down'),'lid-a':pose(l0,'face_down'),
     'wing-b':pose(w2,'bottom_down'),'lid-b':pose(l2,'face_down')}
for n,s in stl.items():
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'{n}.stl'),tolerance=.02,angularTolerance=.1)
for n,s in (('folded',allp),):
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'{n}-preview.stl'),tolerance=.05,angularTolerance=.2)
print('wrote',sorted(p.name for p in OUT.glob('*.stl')))
