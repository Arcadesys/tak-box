"""CC2 slicer verification using existing PETG profiles. Never sends a print."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT.parent / 'profiles'
EXE = '/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
WORK = ROOT / '.slicer-work'
(WORK / 'config').mkdir(parents=True, exist_ok=True)
config = json.loads((PROFILES / 'process-pieces.json').read_text())
config['curr_bed_type'] = 'Textured PEI Plate'
(ROOT / 'profiles').mkdir(exist_ok=True)
process_path = ROOT / 'profiles' / 'process-fox-knurled.json'
process_path.write_text(json.dumps(config, indent=2) + '\n')
report = {'slicer': 'ElegooSlicer', 'machine': 'Elegoo Centauri Carbon 2',
          'filament': 'PETG from existing project profiles', 'nozzle_mm': .4,
          'layer_mm': .2, 'printed': False, 'plates': {}}
for name, filament, count in (
        ('fox-sample-first', 'filament-orange.json', 1),
        ('fox-21-flats', 'filament-orange.json', 21)):
    dest = ROOT / 'plates' / f'{name}-cc2.3mf'
    cmd = [EXE, '--datadir', str(WORK / 'config'), '--load-settings',
           f'{PROFILES / "machine.json"};{process_path}', '--load-filaments',
           str(PROFILES / filament), '--ensure-on-bed', '--slice', '0',
           '--export-3mf', str(dest), str(ROOT / 'plates' / f'{name}.3mf')]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=240)
    (WORK / f'{name}.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (name, (result.stdout + result.stderr)[-1200:])
    with ZipFile(dest) as archive:
        assert archive.testzip() is None
        project = json.loads(archive.read('Metadata/project_settings.config'))
        assert project['curr_bed_type'] == 'Textured PEI Plate'
        assert project['printer_model'] == 'Elegoo Centauri Carbon 2'
        info = ET.fromstring(archive.read('Metadata/slice_info.config'))
        objects = info.findall('.//object')
        assert len(objects) == count and all(x.get('skipped') == 'false' for x in objects)
        values = {x.get('key'): x.get('value') for x in info.findall('.//plate/metadata')}
        assert values['outside'] == 'false'
        gcode = archive.read('Metadata/plate_1.gcode')
        assert len(gcode) > 1000 and b';LAYER_CHANGE' in gcode
        report['plates'][name] = {'exit_code': result.returncode, 'objects': count,
            'outside_bed': False, 'support_used': values.get('support_used'),
            'estimated_seconds': int(values['prediction']),
            'estimated_print_material_g': float(values['weight']),
            'gcode_bytes': len(gcode), 'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
            'file_sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}
        print(name, report['plates'][name], flush=True)
(ROOT / 'reports' / 'slicer-verification.json').write_text(json.dumps(report, indent=2) + '\n')
