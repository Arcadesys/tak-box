"""Local dry slice checks. Never sends G-code or starts a printer job."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parent
EXE = Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
WORK = PACKAGE/'.slicer-work'


def main():
    report = {'slicer':'ElegooSlicer','physical_print':False,'plates':{}}
    if not EXE.exists():
        report['unavailable']='Installed macOS ElegooSlicer not found'
        (PACKAGE/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')
        print(report['unavailable'])
        return
    (WORK/'config').mkdir(parents=True,exist_ok=True)
    plans = [('closure-coupon','pieces',6),('cat-flats-21','pieces',21),
             ('fox-flats-21','pieces',21),('floors-21','pieces',21),
             ('fox-cat-capstones','caps',2),('tray','structure',1),
             ('board-felt-backing','structure',1),('board-grooved-option','structure',1),
             ('platform','structure',1)]
    for name,mode,count in plans:
        config = json.loads((REPO/'pieces/profiles/process-pieces.json').read_text())
        config.update({'curr_bed_type':'Textured PEI Plate','enable_prime_tower':'0'})
        if mode=='caps':
            config.update({'layer_height':'.12','wall_loops':'4',
                'sparse_infill_density':'25%','enable_support':'1',
                'support_type':'tree(auto)','support_on_build_plate_only':'0'})
        elif mode=='structure':
            config.update({'wall_loops':'4','sparse_infill_density':'20%',
                           'top_shell_layers':'5','bottom_shell_layers':'5','enable_support':'0'})
        process = WORK/f'{mode}-process.json'
        process.write_text(json.dumps(config,indent=2)+'\n')
        filament = REPO/('pieces/profiles/filament-orange.json' if mode=='pieces'
                         else 'v16-field-book/profiles/filament-pla-black.json')
        dest = WORK/f'{name}-cc2.3mf'
        command = [str(EXE),'--datadir',str(WORK/'config'),'--load-settings',
            f'{REPO/"pieces/profiles/machine.json"};{process}',
            '--load-filaments',str(filament),'--ensure-on-bed','--slice','0',
            '--export-3mf',str(dest),str(PACKAGE/'plates'/f'{name}.3mf')]
        result = subprocess.run(command,capture_output=True,text=True,timeout=300)
        (WORK/f'{name}.log').write_text(result.stdout+result.stderr)
        if result.returncode:
            report['plates'][name]={'exit_code':result.returncode,'passed':False,
                'error_tail':(result.stdout+result.stderr)[-1500:]}
        else:
            with ZipFile(dest) as z:
                assert z.testzip() is None
                info = ET.fromstring(z.read('Metadata/slice_info.config'))
                objects = info.findall('.//object')
                assert len(objects)==count and all(o.get('skipped')=='false' for o in objects),name
                values = {v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')}
                assert values['outside']=='false',name
                gcode = z.read('Metadata/plate_1.gcode')
                assert b';LAYER_CHANGE' in gcode and len(gcode)>1000,name
                report['plates'][name]={'exit_code':0,'passed':True,'objects':count,
                    'outside_bed':False,'support_used':values.get('support_used'),
                    'estimated_seconds':values.get('prediction'),'estimated_grams':values.get('weight'),
                    'gcode_sha256':hashlib.sha256(gcode).hexdigest(),
                    'machine':'Repository CC2 0.4 mm','material':'PETG' if mode=='pieces' else 'PLA',
                    'layer_mm':.12 if mode=='caps' else .2,
                    'sliced_project_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
        (PACKAGE/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')
        print(name,report['plates'][name].get('passed'),flush=True)
    assert all(p.get('passed') for p in report['plates'].values()),'One or more local slice checks failed'


if __name__=='__main__':
    main()
