"""Center-joint coupon: a 58 mm slice of the two print halves, real geometry.

Piece A  wing 0 edge (lane 3, divider, pan, print-in-place seam) + front center half with a nipple
Piece B  back center half with the matching hole + wing 2 edge (seam, lane 1, pan)
Glue A to B at the center seam, play faces down on a flat surface, and you have a
five-part mini case: test the nipple fit, the flush play face, both seam hinges and
the bridged lane roofs. Coupon only: printed on a raft so the wings and the play face bond to the bed.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_case_pip as p
import halves_split as hs

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'/'joint'; OUT.mkdir(parents=True,exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

X0=p.knuckle_x(4)-p.GAP/2             # gap centre before even knuckle 4
X1=p.knuckle_x(6)+p.L+p.GAP/2         # gap centre after even knuckle 6
assert X0<hs.NIPPLE_X[1]<X1
def crop(y0,y1): return p.box(X1-X0,y1-y0,40,X0,y0,-21)

def facedown(shape):
    s=shape.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
    return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))

w0,w2=p.sol(p.shell(0)),p.sol(p.shell(2))
front,back=hs.center_halves()
# crop on the outer faces of a full lane divider (49.8 and 155.2), so the lane roof stays
# anchored on both sides and prints as a real bridge instead of a one-sided shelf
wa=w0.intersect(crop(49.8,84.6)); fa=front.intersect(crop(79,hs.SPLIT+hs.NIPPLE_LEN+0.1))
wb=w2.intersect(crop(120.4,155.2)); fb=back.intersect(crop(hs.SPLIT,124))
for n,s in (('wing0',wa),('front',fa),('back',fb),('wing2',wb)): assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))

# checks on the cropped parts
print('joined center halves overlap %.4f mm3'%fa.intersect(fb).Volume())
worst=0
for deg in range(0,91,15):
    worst=max(worst,p.sol(p.posed(wa,0,deg)).intersect(fa).Volume(),p.sol(p.posed(wb,2,deg)).intersect(fb).Volume())
print('seams fold 0-90: max overlap %.4f mm3'%worst); assert worst<1e-3

A=facedown(cq.Compound.makeCompound([wa,fa])); B=facedown(cq.Compound.makeCompound([fb,wb]))
def place(s,x,y):
    bb=s.BoundingBox(); return s.translate(cq.Vector(x-bb.xmin,y-bb.ymin,0))
w=X1-X0
plate=cq.Compound.makeCompound([place(A,0,0),place(B,w+10,0)])
bb=plate.BoundingBox(); print('plate %.0f x %.0f x %.1f mm'%(bb.xlen,bb.ylen,bb.zlen))
cq.exporters.export(cq.Workplane().add(plate),str(OUT/'joint-coupon-plate.stl'),tolerance=.02,angularTolerance=.1)
for n,s in (('piece-A',A),('piece-B',B)):
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'{n}.stl'),tolerance=.02,angularTolerance=.1)

dest=HERE/'print/archive/2-hinge-experiments'/'tak-center-joint-coupon-cc2-50.3mf'
dest.parent.mkdir(parents=True,exist_ok=True)
cmd=[EXE,'--datadir',str(WORK/'config'),
     '--load-settings',f'{WORK/"profiles/machine.json"};{HERE/"profiles/process-coupon-raft.json"}',
     '--load-filaments',str(WORK/'profiles/filament-white.json'),
     '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),str(OUT/'joint-coupon-plate.stl')]
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
