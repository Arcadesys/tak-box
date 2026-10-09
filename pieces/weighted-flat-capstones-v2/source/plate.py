"""One four-piece print block: eight separate components; silk slot 3 or a provisional black PLA variant."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,shutil,subprocess,sys,xml.etree.ElementTree as ET
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
def node(p,t,**a):return ET.SubElement(p,'{'+NS+'}'+t,a)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 global OUT
 black='--black' in sys.argv
 source_out=OUT
 slot=1 if black else 3
 if black:
  OUT=source_out/'BLACK'
  for folder in ('profiles','reports','PRINT'): (OUT/folder).mkdir(parents=True,exist_ok=True)
  for profile in ('machine','process','black'): shutil.copy2(source_out/'profiles'/f'{profile}.json',OUT/'profiles'/f'{profile}.json')
  shutil.copy2(source_out/'reports/geometry.json',OUT/'reports/geometry.json')
 geometry=json.loads((OUT/'reports/geometry.json').read_text());assert geometry['passed']
 specs=[]
 for team,kind,x in (('cat','capstone',72),('witch','capstone',108),('cat','regular',144),('witch','regular',171)):
  parts=('lower','upper') if kind=='capstone' else ('body','floor')
  for suffix,y in zip(parts,(90,125)):
   label=f'{team}-{kind}-{suffix}';specs.append((f'SLOT {slot} {team.title()} {kind} {suffix}',label,slot,x,y))
 root=ET.Element('{'+NS+'}model',unit='millimeter');resources=node(root,'resources');build=node(root,'build');config=ET.Element('config');manifest=[]
 for idx,(name,label,slot,x,y) in enumerate(specs,1):
  p=source_out/'models'/f'{label}.stl';m=trimesh.load_mesh(p);assert m.is_watertight and m.body_count==1
  move=np.array([x,y,0])-m.bounds[0];v=m.vertices+move
  ob=node(resources,'object',id=str(idx),type='model',name=name);mesh=node(ob,'mesh');vs=node(mesh,'vertices');fs=node(mesh,'triangles')
  for q in v:node(vs,'vertex',**{a:format(float(b),'.9g') for a,b in zip(('x','y','z'),q)})
  for q in m.faces:node(fs,'triangle',**{a:str(int(b)) for a,b in zip(('v1','v2','v3'),q)})
  node(build,'item',objectid=str(idx));o=ET.SubElement(config,'object',id=str(idx));ET.SubElement(o,'metadata',key='name',value=name);ET.SubElement(o,'metadata',key='extruder',value=str(slot));part=ET.SubElement(o,'part',id=str(idx),subtype='normal_part');ET.SubElement(part,'metadata',key='name',value=name);ET.SubElement(part,'metadata',key='extruder',value=str(slot))
  manifest.append(dict(name=name,label=label,source=str(p),source_sha256=sha(p),slot=slot,translation_mm=move.tolist(),bounds_mm=[v.min(0).tolist(),v.max(0).tolist()],volume_mm3=float(m.volume),triangles=len(m.faces)))
 raw=OUT/'PRINT/Tak-FOUR-PIECE-MIDPOINT-geometry.3mf'
 with ZipFile(raw,'w',ZIP_DEFLATED) as z:
  z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True));z.writestr('Metadata/model_settings.config',ET.tostring(config,encoding='utf-8',xml_declaration=True))
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="text/xml"/></Types>')
  z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 profiles=OUT/'profiles'
 process=json.loads((profiles/'process.json').read_text());process.update(name=('Tak four-piece midpoint sample 0.20 Black PLA S1' if black else 'Tak four-piece midpoint sample 0.20 Silk PLA S3'),enable_support='1',support_on_build_plate_only='1',enable_prime_tower='0');(profiles/'process.json').write_text(json.dumps(process,indent=2)+'\n')
 dest=OUT/'PRINT'/('Tak-FOUR-PIECE-SAMPLE-MIDPOINT-BLACK-SLOT-1.3mf' if black else 'Tak-FOUR-PIECE-SAMPLE-MIDPOINT-SLOT-3.3mf')
 command=[EXE,'--debug','3','--logfile',str(OUT/'reports/slicer-debug.log'),'--datadir',str(OUT/'.slicer-config'),'--load-settings',str(profiles/'machine.json')+';'+str(profiles/'process.json'),'--load-filaments',';'.join(str(profiles/(q+'.json')) for q in (('black',) if black else ('black','white','silk-orange-placeholder'))),'--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(raw)]
 report=dict(units='mm',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),logical_piece_count=4,object_count=8,used_filament_slots=[slot],components_are_separate=True,full_sets=False,sources=manifest,profiles_sha256={p.name:sha(p) for p in profiles.glob('*.json')},geometry_report_sha256=sha(OUT/'reports/geometry.json'),command=command,saved_project=str(dest),physical_acceptance=False,printer_started=False,display_colours_provisional=True,material=('Stored generic black PLA profile; current spool not yet confirmed' if black else 'User confirmed Elegoo silk PLA'),current_spool_verified=False,support_reason='Upper capstone cups have face-down raised features requiring external support. Lower cups and regular body/floors print opening/tongue up. All parts use one feed slot; no purge tower needed')
 (OUT/'reports/plate-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 result=subprocess.run(command,capture_output=True,text=True,timeout=600);(OUT/'reports/slice.log').write_text(result.stdout+result.stderr);report['slice_exit_code']=result.returncode
 (OUT/'reports/plate-provenance.json').write_text(json.dumps(report,indent=2)+'\n');assert result.returncode==0,(result.returncode,result.stdout,result.stderr)
 print(dest,flush=True)
if __name__=='__main__':main()
