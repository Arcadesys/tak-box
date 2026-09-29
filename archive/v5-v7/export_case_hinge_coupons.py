"""Real-geometry hinge coupon: a 58 mm slice of the v5 case with the new hinges.

Frame slice  center row + both wing edges with print-in-place cone-pin seam
             hinges, printed face down (as the full frame would be).
Lid slice    wing edge with stub axles + the matching lid with C-clip barrels
             (printed face down, pressed on from above).
The crop planes sit at gap centres and keep an even/odd/even knuckle triple,
so no pin is cut off from its knuckle.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_case_pip as p

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'/'case'; OUT.mkdir(parents=True,exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

X0=p.knuckle_x(2)-p.GAP/2            # gap centre before an even knuckle
X1=p.knuckle_x(4)+p.L+p.GAP/2        # gap centre after the next even knuckle
def crop(y0,y1): return p.box(X1-X0,y1-y0,40,X0,y0,-21)

def facedown(shape):
    s=shape.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
    return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))

def sweep_ok(pairs,label,angles,move):
    worst=0.0
    for deg in angles:
        for fixed,moving in pairs:
            worst=max(worst,fixed.intersect(move(moving,deg)).Volume())
    print(label,'max overlap %.4f mm3'%worst); assert worst<1e-3

# ---- frame slice
S=[p.sol(p.shell(i)) for i in (0,1,2)]
c=crop(49.8,155.2)
F=[s.intersect(c) for s in S]
for i,f in enumerate(F): assert f.isValid() and len(f.Solids())==1,(i,len(f.Solids()))
sweep_ok([(F[1],F[0])],'frame wing0 fold 0-90',range(0,91,15),lambda s,d:p.posed(s,0,d))
sweep_ok([(F[1],F[2])],'frame wing2 fold 0-90',range(0,91,15),lambda s,d:p.posed(s,2,d))
frame=facedown(cq.Compound.makeCompound(F))

# ---- lid slice
base,lid=p.lid_pair(0); base,lid=p.sol(base),p.sol(lid)
c=crop(-4,30)
b=base.intersect(c); l=lid.intersect(c)
for n,s in (('base',b),('lid',l)): assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
sweep_ok([(b,l)],'lid open 0-110',range(0,111,15),lambda s,d:p.lid_open(s,0,d))
def bottom(s): return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))
base_p=bottom(b); lid_p=facedown(l)

# ---- one plate, laid out on a grid
def place(s,x,y):
    bb=s.BoundingBox(); return s.translate(cq.Vector(x-bb.xmin,y-bb.ymin,0))
w=X1-X0
parts=[place(frame,0,0),place(base_p,w+8,0),place(lid_p,w+8,50)]
plate=cq.Compound.makeCompound(parts)
bb=plate.BoundingBox(); print('plate %.0f x %.0f x %.1f mm'%(bb.xlen,bb.ylen,bb.zlen))
assert bb.xlen<250 and bb.ylen<250
cq.exporters.export(cq.Workplane().add(plate),str(OUT/'case-hinge-coupon-plate.stl'),tolerance=.02,angularTolerance=.1)
for name,s in (('frame-slice',frame),('lid-base-slice',base_p),('lid-slice',lid_p)):
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'{name}.stl'),tolerance=.02,angularTolerance=.1)

# ---- 3MF: halves profile (normal supports, bridging) plus a 3-layer raft. In the face-down
# pose the wing rims sit 3 mm above the bed and the open lid floats, so only the center plate
# touches the bed directly; a raft bonds every part. Coupon only: it roughens the play face.
pp=HERE/'profiles'/'process-coupon-raft.json'
dest=HERE/'centauri-carbon-2-3mf'/'tak-case-hinge-coupon-cc2-30.3mf'
cmd=[EXE,'--datadir',str(WORK/'config'),
     '--load-settings',f'{WORK/"profiles/machine.json"};{pp}',
     '--load-filaments',str(WORK/'profiles/filament-white.json'),
     '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),str(OUT/'case-hinge-coupon-plate.stl')]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=300)
if r.returncode or not dest.exists(): raise RuntimeError((r.stdout+r.stderr)[-1600:])
tmp=dest.with_suffix('.tmp')
with ZipFile(dest) as src,ZipFile(tmp,'w') as dst:
    for item in src.infolist():
        data=src.read(item.filename)
        if item.filename=='Metadata/project_settings.config':
            cfg=json.loads(data); cfg['curr_bed_type']='Textured PEI Plate'
            data=json.dumps(cfg,indent='\t').encode()
        dst.writestr(item,data)
os.replace(tmp,dest)
print(dest.name,dest.stat().st_size)
