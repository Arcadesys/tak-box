"""Dry-slice new compact parts; reuse only exact shared-board input hashes."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import design as d

PACKAGE = Path(__file__).resolve().parents[1]
EXE = Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
WORK = PACKAGE/'.slicer-work'


def main():
    assert EXE.exists(),'Installed ElegooSlicer unavailable; slicing not verified'
    (WORK/'config').mkdir(parents=True,exist_ok=True)
    report = {'slicer':'ElegooSlicer','physical_print':False,'plates':{}}
    previous = json.loads((d.BASE_PACKAGE/'reports/slicing.json').read_text())
    for name in ('board-felt-backing','board-grooved-option'):
        entry = previous['plates'][name].copy()
        assert entry['passed']
        assert entry['input_geometry_sha256']==hashlib.sha256((PACKAGE/'plates'/f'{name}.3mf').read_bytes()).hexdigest()
        entry['evidence_reused_for_unchanged_geometry']=True
        entry['evidence_source']='full-size-pagoda-v1/reports/slicing.json'
        report['plates'][name]=entry
    machine = d.ROOT/'pieces/profiles/machine.json'
    filament = d.ROOT/'v16-field-book/profiles/filament-pla-black.json'
    config = json.loads((d.ROOT/'pieces/profiles/process-pieces.json').read_text())
    config.update({'curr_bed_type':'Textured PEI Plate','enable_prime_tower':'0',
                   'wall_loops':'4','sparse_infill_density':'20%',
                   'top_shell_layers':'5','bottom_shell_layers':'5','enable_support':'0'})
    process = WORK/'structure-process.json'
    process.write_text(json.dumps(config,indent=2)+'\n')
    for name,count in (('platform',1),('tray',1),('grip-coupons',2)):
        dest = WORK/f'{name}-cc2.3mf'
        command = [str(EXE),'--datadir',str(WORK/'config'),'--load-settings',f'{machine};{process}',
                   '--load-filaments',str(filament),'--ensure-on-bed','--slice','0',
                   '--export-3mf',str(dest),str(PACKAGE/'plates'/f'{name}.3mf')]
        result = subprocess.run(command,capture_output=True,text=True,timeout=300)
        (WORK/f'{name}.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0,(name,result.returncode,(result.stdout+result.stderr)[-1200:])
        with ZipFile(dest) as z:
            assert z.testzip() is None
            info = ET.fromstring(z.read('Metadata/slice_info.config'))
            objects = info.findall('.//object')
            assert len(objects)==count and all(o.get('skipped')=='false' for o in objects)
            values = {v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')}
            assert values['outside']=='false'
            gcode = z.read('Metadata/plate_1.gcode')
            assert b';LAYER_CHANGE' in gcode and len(gcode)>1000
        report['plates'][name] = {'passed':True,'exit_code':0,'objects':count,'outside_bed':False,
            'support_used':values.get('support_used'),'estimated_seconds':values.get('prediction'),
            'estimated_grams':values.get('weight'),'machine':'Repository CC2 0.4 mm',
            'material':'PLA','layer_mm':.2,
            'input_geometry_sha256':hashlib.sha256((PACKAGE/'plates'/f'{name}.3mf').read_bytes()).hexdigest(),
            'gcode_sha256':hashlib.sha256(gcode).hexdigest(),
            'sliced_project_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
        (PACKAGE/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')
        print(name,report['plates'][name],flush=True)
    report['profile_sha256']={str(p.relative_to(d.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (machine,filament,d.ROOT/'pieces/profiles/process-pieces.json')}
    report['generated_structure_process']=config
    (PACKAGE/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
