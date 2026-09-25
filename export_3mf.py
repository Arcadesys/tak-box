"""Package the lift-up-well board for the Centauri Carbon 2 slicer profile."""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=ROOT/'work/tak-212-3mf'
PROFILES=WORK/'profiles'
OUT=HERE/'centauri-carbon-2-3mf'
OUT.mkdir(exist_ok=True)
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

groups={
 '01-white-wing-a-center':('process-board.json','filament-white.json',
                            ['wing-shell-a-print.stl','center-row-print.stl']),
 '02-white-wing-b-lid-a':('process-board.json','filament-white.json',
                            ['wing-shell-b-print.stl','playing-lid-a-print.stl']),
 '03-white-lid-b-pins':('process-small.json','filament-white.json',
                          ['playing-lid-b-print.stl','main-hinge-pin.stl',
                           'main-hinge-pin.stl','lid-hinge-pin.stl','lid-hinge-pin.stl']),
 '04-black-raised-grid':('process-overlay.json','filament-black.json',
                           ['black-grid-a-print.stl','black-grid-center-print.stl',
                            'black-grid-b-print.stl']),
 '00-fit-coupon':('process-small.json','filament-white.json',
                    ['fit-coupon/well-end-shell.stl','fit-coupon/lift-up-lid.stl',
                     'fit-coupon/lid-hinge-pin.stl']),
}
for name,(process,filament,models) in groups.items():
    dest=OUT/f'tak-open-wells-v5-cc2-{name}.3mf'
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{PROFILES/"machine.json"};{PROFILES/process}',
         '--load-filaments',str(PROFILES/filament),
         '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),
         *[str(HERE/model) for model in models]]
    result=subprocess.run(cmd,text=True,capture_output=True,timeout=240)
    if result.returncode or not dest.exists():
        raise RuntimeError(f'{name}: {(result.stdout+result.stderr)[-1600:]}')
    tmp=dest.with_suffix('.tmp')
    with ZipFile(dest) as src,ZipFile(tmp,'w') as dst:
        assert src.testzip() is None
        for item in src.infolist():
            data=src.read(item.filename)
            if item.filename=='Metadata/project_settings.config':
                cfg=json.loads(data)
                cfg['curr_bed_type']='Textured PEI Plate'
                data=json.dumps(cfg,indent='\t').encode()
            dst.writestr(item,data)
    os.replace(tmp,dest)
    with ZipFile(dest) as project:assert project.testzip() is None
    print(name,dest.stat().st_size,len(models),flush=True)
