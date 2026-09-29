#!/usr/bin/env python3
"""Build and slice the Tak v15 print plates for the Elegoo CC2 (4-colour).

Every plate loads the same four filaments, so the numbering matches everywhere:
1 black, 2 white, 3 orange, 4 purple. Multi-colour parts are reassembled from
their per-colour STLs (stl/full/<part>.<colour>.stl) with the slicer's
assemble list, which keeps the parts registered and assigns each its filament.
"""
from __future__ import annotations
import json, os, re, subprocess
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
PROFILES=ROOT/'profiles'
SLICER=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
WORK=Path(os.environ.get('TAK_SLICER_WORK',str(ROOT/'.slicer-work')))
COLOURS=['black','white','orange','purple']
FIL={c:i+1 for i,c in enumerate(COLOURS)}
FULL=ROOT/'stl/full';TRIALS=ROOT/'stl/trials'

def group(stem,pos=None):
    """All per-colour STLs of one part, as one assembled object."""
    files=sorted(FULL.glob(f'{stem}.*.stl'))
    assert files,stem
    return [(f,FIL[f.name.split('.')[-2]],pos) for f in files]

def single(path,pos=None):
    return [(path,FIL['black'],pos)]

# (objects, need_arrange). Each object is a list of (stl, filament, (x, y) or None).
PLATES={
 '00-fit-trials-black':([single(p) for p in sorted(TRIALS.glob('*.stl'))],True),
 '01-hinged-bases-black':([single(FULL/'bases-hinged-print-in-place.stl')],True),
 '02-trays-4colour':([group('tray-a',(28,40)),group('tray-b',(110,40))],False),
 '03-board-plates-4colour':([group('board-plate-a',(24,42)),group('board-plate-b',(110,42))],False),
}

def run(cmd):
    return subprocess.run(cmd,text=True,capture_output=True)

def common():
    fils=';'.join(str(PROFILES/f'filament-pla-{c}.json') for c in COLOURS)
    return [str(SLICER),'--datadir',str(WORK/'slicer-data'),
            '--load-settings',f"{PROFILES/'machine.json'};{PROFILES/'process-v15-pla.json'}",
            '--load-filaments',fils]

def assemble_list(name,objects,arrange):
    objs=[]
    for i,parts in enumerate(objects,1):
        for path,fil,pos in parts:
            x,y=pos if pos else (0,0)
            objs.append({'path':str(path),'count':1,'filaments':[fil],'assemble_index':[i],
                         'pos_x':[x],'pos_y':[y],'pos_z':[0]})
    doc={'plates':[{'plate_name':name,'need_arrange':arrange,'objects':objs}]}
    p=WORK/f'{name}.assemble.json';p.write_text(json.dumps(doc,indent=1));return p

def set_bed(plate):
    tmp=plate.with_suffix('.tmp.3mf')
    with ZipFile(plate) as src,ZipFile(tmp,'w') as dst:
        for ent in src.infolist():
            data=src.read(ent.filename)
            if ent.filename=='Metadata/project_settings.config':
                cfg=json.loads(data);cfg['curr_bed_type']='Textured PEI Plate'
                data=json.dumps(cfg,indent='\t').encode()
            dst.writestr(ent,data)
    os.replace(tmp,plate)

def check_project(plate,objects):
    with ZipFile(plate) as z:
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
    got=[]
    for obj in cfg.findall('object'):
        got.append(sorted(int(m.get('value')) for part in obj.findall('part')
                          for m in part.findall('metadata') if m.get('key')=='extruder'))
    want=sorted(sorted(f for _,f,_ in parts) for parts in objects)
    if sorted(got)!=want:raise RuntimeError(f'{plate.name}: parts/filaments {got} != {want}')
    return got

def stats(gcode):
    t=gcode.read_text(errors='replace')
    g=lambda p:(m.group(1).strip() if (m:=re.search(p,t,re.M)) else None)
    grams=[float(x) for x in g(r'^; filament used \[g\] = (.+)$').split(',')]
    return {'estimated_time':g(r'^; estimated printing time \(normal mode\) = (.+)$'),
            'layers':int(g(r'^; total layer number: (.+)$')),
            'filament_g':{c:round(v,2) for c,v in zip(COLOURS,grams)},
            'total_g':float(g(r'^; total filament used \[g\] = (.+)$')),
            'colour_changes':max(0,len(re.findall(r'^M6211 T\d',t,re.M))-1),
            'supports':g(r'^; enable_support = (.+)$')}

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    for d in ('plates','gcode'):(ROOT/d).mkdir(exist_ok=True)
    for old in list((ROOT/'plates').glob('*.3mf'))+list((ROOT/'gcode').glob('*.gcode')):old.unlink()
    report={'filaments':FIL,'plates':{}}
    for name,(objects,arrange) in PLATES.items():
        plate=ROOT/'plates'/f'plate{name}.3mf';gcode=ROOT/'gcode'/f'plate{name}.gcode'
        lst=assemble_list(name,objects,arrange)
        print(name,'exporting 3mf',flush=True)
        r=run(common()+['--load-assemble-list',str(lst),'--export-3mf',str(plate)])
        if r.returncode or not plate.exists():raise RuntimeError(f'{name} export: {r.stdout[-800:]}{r.stderr[-800:]}')
        set_bed(plate)
        parts=check_project(plate,objects)
        out=WORK/'out';out.mkdir(exist_ok=True)
        for f in out.glob('*.gcode'):f.unlink()
        print(name,'slicing',flush=True)
        r=run(common()+['--slice','0','--outputdir',str(out),str(plate)])
        raw=out/'plate_1.gcode'
        if r.returncode or not raw.exists():raise RuntimeError(f'{name} slice exit {r.returncode}: {r.stdout[-800:]}')
        os.replace(raw,gcode)
        s=stats(gcode)
        report['plates'][name]={'3mf':str(plate.relative_to(ROOT)),'gcode':str(gcode.relative_to(ROOT)),
                                'objects_filaments':parts,**s}
        print(json.dumps({'plate':name,**s}),flush=True)
    (ROOT/'reports/package-report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
