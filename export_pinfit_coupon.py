"""Filament-pin fit coupon: 3MF plate, real 1.75 mm filament is the pin.

Ladders  ten bores 1.70 ... 2.30 mm (small end = notched corner): round and teardrop
Strips   1 dimple  fixed 1.80 / free 2.10     2 dimples 1.90 / 2.20     3 dimples 2.00 / 2.30
Plugs    press-in caps with filament holes 1.60 / 1.70 / 1.75 / 1.80
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_pinfit as f

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'/'pinfit'; OUT.mkdir(parents=True,exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

def place(s,x,y):
    bb=s.BoundingBox(); return s.translate(cq.Vector(x-bb.xmin,y-bb.ymin,-bb.zmin))
parts=[place(f.ladder(False),0,0),place(f.ladder(True),30,0)]
for n,(df,dr) in enumerate(((1.80,2.10),(1.90,2.20),(2.00,2.30))):
    A,B=f.strip(df,dr,n+1)
    w=f.sweep(A,B); print('strip %d fixed %.2f free %.2f: fold 0-110 overlap %.4f mm3'%(n+1,df,dr,w)); assert w<1e-3
    parts.append(place(cq.Compound.makeCompound([A,B]),60,n*36))
for i,h in enumerate((1.60,1.70,1.75,1.80)):
    parts.append(place(f.plug(h),125+(i%2)*8,(i//2)*8))
plate=cq.Compound.makeCompound(parts); bb=plate.BoundingBox()
print('plate %.0f x %.0f x %.1f mm'%(bb.xlen,bb.ylen,bb.zlen)); assert bb.xlen<250 and bb.ylen<250
cq.exporters.export(cq.Workplane().add(plate),str(OUT/'pinfit-plate.stl'),tolerance=.01,angularTolerance=.1)

dest=HERE/'print/archive/2-hinge-experiments'/'tak-filament-pin-fit-coupon-cc2-70.3mf'
dest.parent.mkdir(parents=True,exist_ok=True)
cmd=[EXE,'--datadir',str(WORK/'config'),
     '--load-settings',f'{WORK/"profiles/machine.json"};{HERE/"profiles/process-pinfit.json"}',
     '--load-filaments',str(WORK/'profiles/filament-white.json'),
     '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),str(OUT/'pinfit-plate.stl')]
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
print(dest.name,dest.stat().st_size)
