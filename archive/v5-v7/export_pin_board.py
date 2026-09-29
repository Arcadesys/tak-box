"""Full filament-pin board: checks, print STLs and four CC2 3MF plates.

80  white  center row (face down) + 10 press-in plugs
81  white  wing A (bottom down) + lid A (face down)
82  white  wing B (bottom down) + lid B (face down)
83  black  raised grid overlays (v5, lid pieces notched clear of the wing knuckles)

White plates use profiles/process-board-pin.json: 0.20 mm, 4 walls, 35% gyroid,
tree supports on the build plate only, so nothing grows inside the pin bores.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess,sys
import cadquery as cq
import tak_case_pin as m
import tak_pinfit as f

HERE=Path(__file__).resolve().parent
OUT=HERE/'pin-board'; OUT.mkdir(exist_ok=True)
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

w0,l0=map(m.sol,m.lid_pair(0)); w2,l2=map(m.sol,m.lid_pair(2))
center=m.sol(m.shell(1))
overlays=[m.overlay(i) for i in range(3)]
parts={'wing A':w0,'center':center,'wing B':w2,'lid A':l0,'lid B':l2}
for n,s in {**parts,**{f'overlay {i}':o for i,o in enumerate(overlays)}}.items():
    assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
for s in (w0,center,w2): assert abs(s.BoundingBox().zmin+20.1)<1e-5

def clear(a,b): return a.intersect(b).Volume()
def sweep(label,pairs,angles):
    worst=max(clear(a,b(deg)) for deg in angles for a,b in pairs)
    print('%-28s max overlap %.4f mm3'%(label,worst)); assert worst<1e-3

# filament threads every knuckle and both feed channels without touching anything
for pin in ('seam0','seam1','lid0','lid2'):
    fil=m.filament(pin)
    worst=max(clear(fil,s) for s in parts.values())
    print('%-28s max overlap %.4f mm3'%(f'filament {pin}',worst)); assert worst<1e-3
sweep('lid A open 0-110',[(w0,lambda d:m.lid_open(l0,0,d))],range(0,111,10))
sweep('lid B open 0-110',[(w2,lambda d:m.lid_open(l2,2,d))],range(0,111,10))
sweep('lid A overlay open 0-110',[(w0,lambda d:m.lid_open(overlays[0],0,d))],range(0,111,10))
sweep('lid B overlay open 0-110',[(w2,lambda d:m.lid_open(overlays[2],2,d))],range(0,111,10))
sweep('wing A + lid fold 0-90',[(center,lambda d:m.posed(w0,0,d)),(center,lambda d:m.posed(l0,0,d))],range(0,91,10))
sweep('wing B + lid fold 0-90',[(center,lambda d:m.posed(w2,2,d)),(center,lambda d:m.posed(l2,2,d))],range(0,91,10))
side=lambda w,l,i,d:m.posed(w,i,d).fuse(m.posed(l,i,d))
worst=max(clear(side(w0,l0,0,d),side(w2,l2,2,d)) for d in range(0,91,10))
print('%-28s max overlap %.4f mm3'%('side A vs side B fold 0-90',worst)); assert worst<1e-3

# Validate CAD without requiring the machine-specific slicer paths below.
if '--check-only' in sys.argv:
    sys.exit(0)

def pose(s,mode):
    if mode=='face_down': s=s.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
    return s.translate(cq.Vector(0,0,-s.BoundingBox().zmin))
stl={'center-row':pose(center,'face_down'),
     'wing-a':pose(w0,'bottom_down'),'lid-a':pose(l0,'face_down'),
     'wing-b':pose(w2,'bottom_down'),'lid-b':pose(l2,'face_down'),
     'plug':pose(f.plug(m.PLUG_HOLE),'bottom_down'),
     'black-grid-a':pose(overlays[0],'bottom_down'),
     'black-grid-center':pose(overlays[1],'bottom_down'),
     'black-grid-b':pose(overlays[2],'bottom_down')}
for n,s in stl.items():
    cq.exporters.export(cq.Workplane().add(s),str(OUT/f'{n}.stl'),tolerance=.02,angularTolerance=.1)

plates={
 '80-white-center-row-plugs':('process-board-pin.json','filament-white.json',['center-row']+['plug']*10),
 '81-white-wing-a-lid-a':('process-board-pin.json','filament-white.json',['wing-a','lid-a']),
 '82-white-wing-b-lid-b':('process-board-pin.json','filament-white.json',['wing-b','lid-b']),
 '83-black-raised-grid':(None,'filament-black.json',['black-grid-a','black-grid-center','black-grid-b']),
}
for name,(process,filament,models) in plates.items():
    pp=HERE/'profiles'/process if process else WORK/'profiles/process-overlay.json'
    dest=HERE/'centauri-carbon-2-3mf'/f'tak-pin-board-cc2-{name}.3mf'
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{WORK/"profiles/machine.json"};{pp}',
         '--load-filaments',str(WORK/'profiles'/filament),
         '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),*[str(OUT/f'{n}.stl') for n in models]]
    r=subprocess.run(cmd,text=True,capture_output=True,timeout=300)
    if r.returncode or not dest.exists(): raise RuntimeError(name+(r.stdout+r.stderr)[-1600:])
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
print('filament pin length each: %.1f mm (4 pins); bores fixed %.2f / free %.2f, plug hole %.2f'
      %(m.PIN_LEN,m.D_FIXED,m.D_FREE,m.PLUG_HOLE))
