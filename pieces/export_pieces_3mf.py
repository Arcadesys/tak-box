"""Package the Team Cat / Team Witch piece plates for the Centauri Carbon 2.

One project per team: 21 flat stones plus the pawn capstone, each a separate
object so the slicer can arrange them and any one can be deselected.
Uses the CC2 machine profile in profiles/ and a local .slicer-work data dir.
"""
from pathlib import Path
from zipfile import ZipFile
import json,os,subprocess

HERE=Path(__file__).resolve().parent
WORK=HERE/'.slicer-work'
MACHINE=HERE/'profiles/machine.json'
PROFILES=HERE/'profiles'
OUT=HERE/'plates'
OUT.mkdir(exist_ok=True)
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

plates={
 'tak-pieces-cc2-10-cat-orange':('cat','filament-orange.json'),
 'tak-pieces-cc2-11-witch-purple':('witch','filament-purple.json'),
}
for name,(team,filament) in plates.items():
    dest=OUT/f'{name}.3mf'
    models=[HERE/f'{team}-flat.stl']*21+[HERE/f'{team}-capstone.stl']
    cmd=[EXE,'--datadir',str(WORK/'config'),
         '--load-settings',f'{MACHINE};{PROFILES/"process-pieces.json"}',
         '--load-filaments',str(PROFILES/filament),
         '--arrange','1','--ensure-on-bed','--export-3mf',str(dest),
         *map(str,models)]
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
