#!/usr/bin/env python3
"""Export and slice the Tak v14 print plates for the Elegoo CC2 as 3MF projects.

Each plate is one colour. STLs keep their exported print orientation.
"""
from __future__ import annotations
import argparse, json, os, re, struct, subprocess
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT
MODELS=OUT; PROFILES=OUT/'profiles'; SLICER=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
SCRATCH=Path(os.environ.get('TAK_SLICER_WORK',str(ROOT/'.slicer-work')))
PROC='process-v14-pla.json'
T='stl/trials/';F='stl/full/'
PLATES={
 '00-fit-trials-charcoal':([T+'trial-hinge-pair',T+'trial-buckle-tab-plate',T+'trial-buckle-socket-base',T+'trial-buckle-socket-plate',T+'trial-latch-base',T+'trial-latch-tray'],1,PROC),
 '01-hinged-bases-charcoal':([F+'bases-hinged-print-in-place'],1,PROC),
 '02-trays-charcoal':([F+'tray',F+'tray'],1,PROC),
 '03-board-plates-white':([F+'plate-a',F+'plate-b'],1,PROC),
 '04-grid-inlays-black':([F+'grid-inlay-a',F+'grid-inlay-b'],1,PROC),
}

NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02','p':'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'}
def run(cmd:list[str])->subprocess.CompletedProcess[str]:
 return subprocess.run(cmd,text=True,capture_output=True)
def stl_stats(path:Path)->tuple[int,tuple[float,...]]:
 data=path.read_bytes()
 if len(data)>=84:
  count=struct.unpack_from('<I',data,80)[0]
  if 84+50*count==len(data):
   mins=[float('inf')]*3; maxs=[float('-inf')]*3
   for i in range(count):
    vals=struct.unpack_from('<12fH',data,84+50*i)
    for j in range(3):
     for k in (3,6,9): mins[j]=min(mins[j],vals[k+j]); maxs[j]=max(maxs[j],vals[k+j])
   return count,tuple(mins+maxs)
 text=data.decode('ascii',errors='ignore'); verts=[]
 for row in text.splitlines():
  m=re.match(r'\s*vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)',row)
  if m: verts.append(tuple(map(float,m.groups())))
 if not verts: raise ValueError(f'Cannot read STL bounds: {path}')
 return len(verts)//3,tuple([min(v[i] for v in verts) for i in range(3)]+[max(v[i] for v in verts) for i in range(3)])
def verify_plate(plate:Path, inputs:list[Path], process:Path, filament:Path)->dict:
 with ZipFile(plate) as z:
  names=z.namelist(); cfg=json.loads(z.read('Metadata/project_settings.config'))
  model=ET.fromstring(z.read('3D/3dmodel.model'))
  comps=model.findall('.//m:component',NS)
  objmodels=[n for n in names if n.startswith('3D/Objects/') and n.endswith('.model')]
  if len(comps)!=len(inputs) or len(objmodels)!=len(inputs): raise RuntimeError(f'{plate.name}: expected {len(inputs)} objects; got {len(comps)} components, {len(objmodels)} mesh files')
  # Each source mesh is re-centered inside its component. The outer build item
  # supplies its final translation/rotation on the plate; compose both transforms.
  # Only proper XY rotations and translations are allowed: no scale, tilt, or mirror.
  dot=lambda a,b:sum(x*y for x,y in zip(a,b))
  def matrix(t,label):
   if len(t)!=12: raise RuntimeError(f'{plate.name}: malformed {label} transform')
   m=[t[0:3],t[3:6],t[6:9]]
   det=(m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
   if any(abs(dot(m[i],m[j])-(1 if i==j else 0))>1e-6 for i in range(3) for j in range(3)) or abs(det-1)>1e-6 or any(abs(m[2][i]-(1 if i==2 else 0))>1e-6 for i in range(3)) or abs(m[0][2])>1e-6 or abs(m[1][2])>1e-6:
    raise RuntimeError(f'{plate.name}: {label} transform scales, tilts, or mirrors the print pose: {t}')
   return m
  parents={}
  for obj in model.findall('./m:resources/m:object',NS):
   for c in obj.findall('./m:components/m:component',NS): parents[c.attrib.get('{'+NS['p']+'}path')]=obj.attrib['id']
  build={x.attrib['objectid']:list(map(float,x.attrib.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split())) for x in model.findall('./m:build/m:item',NS)}
  transforms=[]; world_boxes=[]
  for c in comps:
   ci=list(map(float,c.attrib.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split())); cm=matrix(ci,'component')
   path=c.attrib.get('{'+NS['p']+'}path'); parent=parents.get(path)
   if parent not in build: raise RuntimeError(f'{plate.name}: missing build transform for {path}')
   bt=build[parent]; bm=matrix(bt,'build-item')
   # 3MF uses row-vector transforms: apply component, then outer build item.
   def apply_point(pt,t):return [sum(pt[i]*t[3*i+j] for i in range(3))+t[9+j] for j in range(3)]
   child=ET.fromstring(z.read(path.lstrip('/'))); verts=child.findall('.//m:vertex',NS)
   placed=[apply_point(apply_point([float(v.attrib[a]) for a in 'xyz'],ci),bt) for v in verts]
   wb=tuple([min(v[i] for v in placed) for i in range(3)]+[max(v[i] for v in placed) for i in range(3)])
   if wb[0]<-0.01 or wb[1]<-0.01 or wb[2]<-0.01 or wb[3]>256.01 or wb[4]>256.01 or wb[5]>256.01:
    raise RuntimeError(f'{plate.name}: transformed mesh outside 256 mm bed or below Z=0: {wb}')
   transforms.append({'path':path,'component_matrix':ci[:9],'component_translation_mm':ci[9:12],'build_item_matrix':bt[:9],'build_item_translation_mm':bt[9:12],'composed_bounds_mm':wb}); world_boxes.append(wb)
  plate_bounds=tuple([min(b[i] for b in world_boxes) for i in range(3)]+[max(b[i+3] for b in world_boxes) for i in range(3)])
  # Slicer stores untransformed source mesh per object. Check every stored vertex envelope and triangle count.
  matched=[]
  for inp in inputs:
   count,bounds=stl_stats(inp); candidates=[]
   for n in objmodels:
    if Path(n).name.startswith(inp.name+'_'):
     root=ET.fromstring(z.read(n)); verts=root.findall('.//m:vertex',NS); tris=root.findall('.//m:triangle',NS)
     vb=tuple([min(float(v.attrib[a]) for v in verts) for a in ('x','y','z')]+[max(float(v.attrib[a]) for v in verts) for a in ('x','y','z')])
     source_size=tuple(bounds[i+3]-bounds[i] for i in range(3)); mesh_size=tuple(vb[i+3]-vb[i] for i in range(3))
     if len(tris)==count and all(abs(a-b)<0.002 for a,b in zip(mesh_size,source_size)): candidates.append(n)
   if not candidates: raise RuntimeError(f'{plate.name}: saved mesh does not match {inp.name} (source triangles={count}, dimensions={[round(bounds[i+3]-bounds[i],3) for i in range(3)]})')
   matched.append({'source':inp.name,'triangle_count':count,'bounds_mm':bounds})
  if cfg.get('curr_bed_type')!='Textured PEI Plate': raise RuntimeError(f'{plate.name}: build plate is {cfg.get("curr_bed_type")}')
  if cfg.get('layer_height')!='0.2' or cfg.get('wall_loops')!='4': raise RuntimeError(f'{plate.name}: layer/wall settings mismatch')
  if cfg.get('filament_type')!=['PLA']: raise RuntimeError(f'{plate.name}: filament is not PLA')
  return {'object_count':len(comps),'mesh_matches':matched,'object_transforms_and_bounds':transforms,'plate_bounds_mm':plate_bounds,'bed':cfg['curr_bed_type'],'process_file':process.name,'filament_file':filament.name}
def slice_info(gcode:Path)->dict:
 text=gcode.read_text(errors='replace')
 get=lambda pat: (re.search(pat,text,re.M).group(1).strip() if re.search(pat,text,re.M) else None)
 layers=get(r'^; total layer number: (.+)$')
 time=get(r'^; estimated printing time \(normal mode\) = (.+)$')
 grams=get(r'^; total filament used \[g\] = (.+)$')
 length=get(r'^; filament used \[mm\] = (.+)$')
 mm3=get(r'^; filament used \[cm3\] = (.+)$')
 bed=get(r'^; first_layer_bed_temperature = (.+)$'); nozzle=get(r'^; first_layer_temperature = (.+)$')
 if not layers or bed!='60' or nozzle!='210' or get(r'^; curr_bed_type = (.+)$')!='Textured PEI Plate': raise RuntimeError(f'{gcode.name}: missing layer count or wrong PLA/bed profile')
 return {'layers':int(layers),'estimated_time':time,'filament_g':float(grams),'filament_mm':float(length),'filament_cm3':float(mm3),'first_layer_bed_c':int(bed),'first_layer_nozzle_c':int(nozzle),'wall_loops':int(get(r'^; wall_loops = (.+)$')),'layer_height_mm':float(get(r'^; layer_height = (.+)$')),'supports':get(r'^; enable_support = (.+)$'),'support_buildplate_only':get(r'^; support_on_build_plate_only = (.+)$')}
def prepare_bed(plate:Path)->None:
 tmp=plate.with_suffix('.tmp.3mf')
 with ZipFile(plate) as src,ZipFile(tmp,'w') as dst:
  for ent in src.infolist():
   data=src.read(ent.filename)
   if ent.filename=='Metadata/project_settings.config':
    cfg=json.loads(data); cfg['curr_bed_type']='Textured PEI Plate'; data=json.dumps(cfg,indent='\t').encode()
   dst.writestr(ent,data)
 os.replace(tmp,plate)
def main()->None:
 ap=argparse.ArgumentParser(); ap.add_argument('--plates',nargs='*',choices=PLATES); args=ap.parse_args()
 wanted=args.plates or list(PLATES)
 if not SLICER.is_file(): ap.error(f'Missing slicer: {SLICER}')
 (OUT/'plates').mkdir(exist_ok=True); (OUT/'gcode').mkdir(exist_ok=True); (SCRATCH/'slicer-logs').mkdir(parents=True,exist_ok=True)
 report=json.loads((OUT/'reports/package-report.json').read_text()) if (OUT/'reports/package-report.json').exists() else {'plates':{}}
 for name in wanted:
  stems,arrange,procname=PLATES[name]; inputs=[MODELS/f'{s}.stl' for s in stems]; missing=[str(p) for p in inputs if not p.is_file()]
  if missing: raise FileNotFoundError(', '.join(missing))
  proc=PROFILES/procname; filament=PROFILES/'filament-pla-cc2.json'; machine=PROFILES/'machine.json'
  plate=OUT/'plates'/f'plate{name}.3mf'; gcode=OUT/'gcode'/f'plate{name}.gcode'; log=SCRATCH/'slicer-logs'/f'plate{name}.log'
  common=[str(SLICER),'--datadir',str((SCRATCH/'slicer-data').resolve()),'--load-settings',f'{machine.resolve()};{proc.resolve()}','--load-filaments',str(filament.resolve())]
  exp=run(common+['--arrange',str(arrange),'--orient','0','--export-3mf',str(plate.resolve()),*[str(p.resolve()) for p in inputs]])
  log.write_text('EXPORT stdout:\n'+exp.stdout+'\nEXPORT stderr:\n'+exp.stderr)
  if exp.returncode: raise RuntimeError(f'{name} export failed: {exp.stderr[-1600:]}')
  prepare_bed(plate)
  geometry=verify_plate(plate,inputs,proc,filament)
  sliced=run(common+['--arrange','0','--orient','0','--slice','0','--outputdir',str((OUT/'gcode').resolve()),str(plate.resolve())])
  with log.open('a') as f: f.write('\nSLICE stdout:\n'+sliced.stdout+'\nSLICE stderr:\n'+sliced.stderr)
  if sliced.returncode: raise RuntimeError(f'{name} slice failed: {sliced.stderr[-1600:]}')
  raw=OUT/'gcode'/'plate_1.gcode'
  if not raw.exists(): raise RuntimeError(f'{name}: slicer did not create plate_1.gcode')
  os.replace(raw,gcode)
  metrics=slice_info(gcode)
  report['plates'][name]={'3mf':str(plate.relative_to(ROOT)),'gcode':str(gcode.relative_to(ROOT)),'geometry':geometry,'toolpath':metrics,'slicer_exit_code':sliced.returncode}
  (OUT/'reports/package-report.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({'plate':name,'gcode':str(gcode),'toolpath':metrics,'slicer_stderr':sliced.stderr.strip()}))
if __name__=='__main__': main()
