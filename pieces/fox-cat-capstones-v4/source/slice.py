"""Local dry slicing only, using the repository's CC2 PLA profiles.

No printer/network commands. Generated toolpaths are validation evidence,
not a printer job or proof of physical fit.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse,json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--species',nargs='+',default=['fox','cat'],choices=['fox','cat'])
    args=p.parse_args()
    work=ROOT/'.slicer-work'
    work.mkdir(exist_ok=True)
    cfg=json.loads((REPO/'pieces/profiles/process-pieces.json').read_text())
    cfg.update({'name':'Fox and Cat capstones - 0.12 mm PLA proof', 'layer_height':'0.12','initial_layer_print_height':'0.2',
        'enable_support':'1','support_type':'tree(auto)','support_on_build_plate_only':'0',
        'support_top_z_distance':'0.12','support_bottom_z_distance':'0.12','wall_loops':'4','sparse_infill_density':'25%'})
    process=ROOT/'source'/'process-capstones.json'
    process.write_text(json.dumps(cfg,indent=2)+'\n')
    common=[EXE,'--datadir',str(work/'config'),'--load-settings',f'{REPO/"pieces/profiles/machine.json"};{process}',
        '--load-filaments',str(REPO/'pieces/profiles/filament-orange.json')]
    report={}
    for species in args.species:
        plate=ROOT/'models'/f'{species}-cc2-proof.3mf'
        result=subprocess.run(common+['--arrange','1','--ensure-on-bed','--export-3mf',str(plate),str(ROOT/'models'/f'{species}-capstone.stl')],capture_output=True,text=True,timeout=180)
        (ROOT/'reports'/f'{species}-slicer-export.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0 and plate.exists(),result.stderr[-500:]
        # Set PEI bed explicitly as in the current piece-package workflow.
        tmp=plate.with_suffix('.tmp')
        with ZipFile(plate) as src,ZipFile(tmp,'w') as dst:
            for info in src.infolist():
                data=src.read(info.filename)
                if info.filename=='Metadata/project_settings.config':
                    settings=json.loads(data);settings['curr_bed_type']='Textured PEI Plate';data=json.dumps(settings).encode()
                dst.writestr(info,data)
        tmp.replace(plate)
        out=work/species
        out.mkdir(exist_ok=True)
        result=subprocess.run(common+['--slice','0','--outputdir',str(out),str(plate)],capture_output=True,text=True,timeout=240)
        (ROOT/'reports'/f'{species}-slicer.log').write_text(result.stdout+result.stderr)
        gcode=out/'plate_1.gcode'
        assert result.returncode==0 and gcode.exists(),(result.stdout+result.stderr)[-1200:]
        text=gcode.read_text()
        report[species]={'exit_code':result.returncode,'layer_height_mm':.12,'tree_supports_enabled':True,'build_plate_only_supports':False,
            'printer_profile':'Repository Centauri Carbon 2 / 0.4 mm nozzle / PLA / Textured PEI',
            'gcode_generated':True,'gcode_bytes':gcode.stat().st_size,
            'layers':int(re.search(r'; total layers count = (\d+)',text).group(1)),
            'support_toolpath_mentions':len(re.findall(r';TYPE:Support',text)),
            'summary_comments':[line for line in text.splitlines() if re.search('estimated printing time|total filament (used|weight)|total layers count',line)]}
        print(species,'SLICE PASS',report[species]['summary_comments'],flush=True)
    (ROOT/'reports'/'slicing.json').write_text(json.dumps(report,indent=2)+'\n')
