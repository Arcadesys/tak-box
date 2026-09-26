"""Hinge tuning coupon: three clearances of each hinge on one CC2 plate (one object).

PIP   clearance 0.3 / 0.4 / 0.5 mm  -> 1 / 2 / 3 dimples on the B plate
snap  mouth     2.3 / 2.5 / 2.7 mm  -> 1 / 2 / 3 dimples on the clip plate
Strips are 59 x ~19 mm (12 mm plate depth) to keep the plate quick and cheap.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_hinges as h

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'/'tuning'; OUT.mkdir(parents=True,exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
DEPTH=12.0

def save(shape,name):
    cq.exporters.export(cq.Workplane().add(shape),str(OUT/f'{name}.stl'),tolerance=.01,angularTolerance=.1)

# Grid layout (one row per variant): snap stubs | snap clip | PIP strip
COLS=(0.0,65.0,130.0); ROW=36.0
def place(shape,col,row):
    bb=shape.BoundingBox()
    return shape.translate(cq.Vector(COLS[col]-bb.xmin,row*ROW-bb.ymin,-bb.zmin))
parts=[]
for n,clr in enumerate((0.3,0.4,0.5),0):
    a,b=h.build_pip(clr,DEPTH,n+1); assert h.sweep(a,b,f'pip clr {clr}')<1e-6
    parts.append(place(cq.Compound.makeCompound([a,b]),2,n))
for n,mouth in enumerate((2.3,2.5,2.7),0):
    a,b=h.build_snap(mouth,DEPTH,n+1); assert h.sweep(a,b,f'snap mouth {mouth}')<1e-6
    parts+= [place(a,0,n),place(b,1,n)]
plate=cq.Compound.makeCompound(parts)
bb=plate.BoundingBox(); assert bb.xlen<250 and bb.ylen<250,(bb.xlen,bb.ylen)
save(plate,'tuning-plate')
models=[OUT/'tuning-plate.stl']

dest=HERE/'print/archive/2-hinge-experiments'/'tak-hinge-tuning-coupon-cc2-21.3mf'
dest.parent.mkdir(parents=True,exist_ok=True)
cmd=[EXE,'--datadir',str(WORK/'config'),
     '--load-settings',f'{WORK/"profiles/machine.json"};{HERE/"profiles/process-pieces.json"}',
     '--load-filaments',str(WORK/'profiles/filament-white.json'),
     '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),*map(str,models)]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=240)
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
print(dest.name,dest.stat().st_size,len(models),'objects')
