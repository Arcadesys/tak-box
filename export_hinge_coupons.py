"""Export the hinge test strips (STL/STEP) and a single Centauri Carbon 2 plate."""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_hinges as h

HERE=Path(__file__).resolve().parent
OUT=HERE/'hinge-coupons'; OUT.mkdir(exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

def save(shape,name):
    cq.exporters.export(cq.Workplane().add(shape),str(OUT/f'{name}.stl'),tolerance=.01,angularTolerance=.1)

pa,pb=h.build_pip(); sa,sb=h.build_snap()
worst=max(h.sweep(pa,pb,'pip'),h.sweep(sa,sb,'snap'))
assert worst<1e-6
save(cq.Compound.makeCompound([pa,pb]),'pip-hinge-strip')      # printed already hinged
save(sa,'snap-hinge-a-stubs'); save(sb,'snap-hinge-b-clip')
cq.exporters.export(cq.Workplane().add(cq.Compound.makeCompound([pa,pb])),str(OUT/'pip-hinge-strip.step'))
cq.exporters.export(cq.Workplane().add(cq.Compound.makeCompound([sa,sb])),str(OUT/'snap-hinge-assembled.step'))

dest=HERE/'print/archive/2-hinge-experiments'/'tak-hinge-coupons-cc2-20.3mf'
dest.parent.mkdir(parents=True,exist_ok=True)
models=[OUT/'pip-hinge-strip.stl',OUT/'snap-hinge-a-stubs.stl',OUT/'snap-hinge-b-clip.stl']
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
print(dest.name,dest.stat().st_size)
