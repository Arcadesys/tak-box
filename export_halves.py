"""Two flat print halves with print-in-place hinges everywhere.

Half A  lid 0 (open 180 deg) + wing 0 + front half of the center row
Half B  back half of the center row + wing 2 + lid 2 (open 180 deg)

Each half prints face down (play face on the textured PEI) and comes off the bed
already hinged: lid hinge and its main seam are print-in-place. The center row
is split on its centerline (y = 102.5); the halves are joined there with three
alignment nipples and glue, pressed together face down on a flat surface so the
play faces stay flush.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess
import cadquery as cq
import tak_case_pip as p

HERE=Path(__file__).resolve().parent
OUT=HERE/'halves'; OUT.mkdir(exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
import halves_split as hs

def facedown(shape):
    s=shape.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
    return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))

front,back=hs.center_halves()
assert front.isValid() and back.isValid() and len(front.Solids())==1 and len(back.Solids())==1

b0,l0=p.lid_pair_pip(0); b2,l2=p.lid_pair_pip(2)
b0,l0,b2,l2=map(p.sol,(b0,l0,b2,l2))
A=cq.Compound.makeCompound([b0,p.sol(p.lid_open(l0,0,180)),front])
B=cq.Compound.makeCompound([back,b2,p.sol(p.lid_open(l2,2,180))])
parts={'A':facedown(A),'B':facedown(B)}
for n,s in parts.items():
    bb=s.BoundingBox(); print('half',n,'%.0f x %.0f x %.1f mm'%(bb.xlen,bb.ylen,bb.zlen))
    assert bb.xlen<250 and bb.ylen<250
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'half-{n}.stl'),tolerance=.02,angularTolerance=.1)

for n in 'AB':
    dest=HERE/'print/archive/2-hinge-experiments'/f'tak-case-half-{n}-cc2-4{"01"[n=="B"]}.3mf'
    dest.parent.mkdir(parents=True,exist_ok=True)
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{WORK/"profiles/machine.json"};{HERE/"profiles/process-halves.json"}',
         '--load-filaments',str(WORK/'profiles/filament-white.json'),
         '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),str(OUT/f'half-{n}.stl')]
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
