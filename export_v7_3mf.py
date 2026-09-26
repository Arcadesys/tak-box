"""Package the v7 board (tak_case_v7) as the four CC2 plates in print/v7-board/.

1of4  white  center row (face down) + 10 press-in plugs
2of4  white  wing A (bottom down) + lid A (face down)
3of4  white  wing B (bottom down) + lid B (face down)
4of4  black  raised-grid overlays (unchanged since the pin board)

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

PIN=HERE/'pin-board'
OUT=HERE/'print/v7-board'; OUT.mkdir(parents=True,exist_ok=True)
white=(PROCESS,WORK/'profiles/filament-white.json')
plates={
 '1of4-white-center-row-plugs':(*white,[V7/'center-row.stl']+[PIN/'plug.stl']*10),
 '2of4-white-wing-a-lid-a':(*white,[V7/'wing-a.stl',V7/'lid-a.stl']),
 '3of4-white-wing-b-lid-b':(*white,[V7/'wing-b.stl',V7/'lid-b.stl']),
 '4of4-black-grid':(WORK/'profiles/process-overlay.json',WORK/'profiles/filament-black.json',
                    [PIN/'black-grid-a.stl',PIN/'black-grid-center.stl',PIN/'black-grid-b.stl']),
}
for name,(process,filament,models) in plates.items():
    dest=OUT/f'tak-v7-board-{name}.3mf'
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{WORK/"profiles/machine.json"};{process}',
         '--load-filaments',str(filament),
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
