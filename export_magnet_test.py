"""Magnet fit test tab: three Ø4 x 2 mm magnet pockets, one per clearance.

1 dimple  Ø4.1 x 2.1   tight press fit
2 dimples Ø4.2 x 2.2   what the case uses
3 dimples Ø4.3 x 2.3   loose, for glue
Print, drop a magnet in each, and tell me which one you want.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'/'magnet'; OUT.mkdir(parents=True,exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

tab=cq.Workplane('XY').box(46,14,4,centered=False).edges('|Z').fillet(2).val()
for n,(d,depth) in enumerate(((4.1,2.1),(4.2,2.2),(4.3,2.3)),1):
    cx=9+(n-1)*14
    tab=tab.cut(cq.Solid.makeCylinder(d/2,depth+0.1,cq.Vector(cx,6.0,4-depth),cq.Vector(0,0,1)))
    for k in range(n):   # dimples along the far edge, centred on the pocket
        dx=cx+(k-(n-1)/2)*1.8
        tab=tab.cut(cq.Solid.makeCylinder(0.7,0.7,cq.Vector(dx,11.5,3.3),cq.Vector(0,0,1)))
assert tab.isValid()
cq.exporters.export(cq.Workplane().add(tab),str(OUT/'magnet-fit-tab.stl'),tolerance=.01,angularTolerance=.1)
dest=HERE/'print/archive/2-hinge-experiments'/'tak-magnet-fit-test-cc2-60.3mf'
dest.parent.mkdir(parents=True,exist_ok=True)
cmd=[EXE,'--datadir',str(WORK/'config'),
     '--load-settings',f'{WORK/"profiles/machine.json"};{HERE/"profiles/process-pieces.json"}',
     '--load-filaments',str(WORK/'profiles/filament-white.json'),
     '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),str(OUT/'magnet-fit-tab.stl')]
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
