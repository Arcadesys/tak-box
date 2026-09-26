"""Package the v7 case (tak_case_v7) as CC2 3MF plates.

90  white  v7 center row (face down) + 10 press-in plugs
91  white  v7 wing A (bottom down) + lid A (face down)
92  white  v7 wing B (bottom down) + lid B (face down)
The black raised-grid overlays are unchanged: print tak-pin-board-cc2-83.

Run export_validate_v7.py first; it writes pin-board-v7/*.stl.
profiles/process-board-pin-v7.json is process-board-pin.json with
bridge_no_support on, so trees stay out of the rubber-foot pockets.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess

HERE=Path(__file__).resolve().parent
V7=HERE/'pin-board-v7'
WORK=HERE.parents[1]/'work/tak-212-3mf'
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
PROCESS=HERE/'profiles/process-board-pin-v7.json'

plates={
 '90-white-center-row-plugs':[V7/'center-row.stl']+[HERE/'pin-board/plug.stl']*10,
 '91-white-wing-a-lid-a':[V7/'wing-a.stl',V7/'lid-a.stl'],
 '92-white-wing-b-lid-b':[V7/'wing-b.stl',V7/'lid-b.stl'],
}
for name,models in plates.items():
    dest=HERE/'centauri-carbon-2-3mf'/f'tak-pin-board-v7-cc2-{name}.3mf'
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{WORK/"profiles/machine.json"};{PROCESS}',
         '--load-filaments',str(WORK/'profiles/filament-white.json'),
         '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),*map(str,models)]
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
    print(dest.name,dest.stat().st_size,flush=True)
