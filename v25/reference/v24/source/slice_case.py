"""Dry slice the three mechanical CC2 plates and verify named embedded mesh readback."""
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1];WORK=OUT/'.slicer-work'
EXE=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mesh(el):
 vs=[[float(v.get(c)) for c in ('x','y','z')] for v in el.find('m:vertices',NS)]
 fs=[[int(v.get(c)) for c in ('v1','v2','v3')] for v in el.find('m:triangles',NS)]
 m=trimesh.Trimesh(vertices=vs,faces=fs,process=False)
 assert m.is_watertight and m.is_winding_consistent and m.body_count==1
 return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+');args=parser.parse_args()
 WORK.mkdir(parents=True,exist_ok=True)
 version=subprocess.run([str(EXE),'--help'],capture_output=True,text=True).stdout.splitlines()[0]
 report={'slicer':version,'printer':'Elegoo Centauri Carbon 2 0.4 nozzle','physical_acceptance':False,'printer_started':False,'profiles_sha256':{p.name:sha(p) for p in (OUT/'profiles').glob('*.json')},'plates':{}}
 previous=json.loads((OUT/'reports/slicing.json').read_text()) if (OUT/'reports/slicing.json').exists() else None
 for source in sorted((OUT/'plates').glob('*.3mf')):
  if source.name.endswith('-CC2-PLA.3mf'):continue
  if source.stem=='02-sliding-board-tops':continue  # Four-colour pipeline owns this plate.
  name=source.stem;dest=OUT/'PRINT'/(name+'-CC2-PLA.3mf');dest.parent.mkdir(exist_ok=True)
  if args.only and name not in args.only:
   row=previous['plates'][name]
   assert row['input_sha256']==sha(source) and row['project_sha256']==sha(dest) and previous['profiles_sha256']==report['profiles_sha256']
   row['unchanged_slice_evidence_reused']=True;report['plates'][name]=row;continue
  command=[str(EXE),'--datadir',str(WORK/'config'),'--load-settings',f'{OUT/"profiles/machine.json"};{OUT/"profiles/process-case.json"}','--load-filaments',str(OUT/'profiles/filament-pla.json'),'--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(source)]
  p=subprocess.run(command,capture_output=True,text=True,timeout=300)
  (OUT/'reports'/f'{name}-slice.log').write_text(p.stdout+p.stderr)
  row={'passed':False,'exit_code':p.returncode,'input_sha256':sha(source),'command':[x.replace(str(REPO),'<repo>') for x in command]}
  report['plates'][name]=row
  if p.returncode:
   (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n');raise RuntimeError(name+': see slice log')
  with ZipFile(source) as z:
   original=ET.fromstring(z.read('3D/3dmodel.model'))
   build_count=len(original.find('m:build',NS))
   all_meshes={o.get('name'):mesh(o.find('m:mesh',NS)) for o in original.findall('m:resources/m:object',NS) if o.find('m:mesh',NS) is not None}
   blockers={n:m for n,m in all_meshes.items() if n=='pin-bore-support-blocker'}
   want={n:m for n,m in all_meshes.items() if n not in blockers}
  with ZipFile(dest) as z:
   assert z.testzip() is None
   info=ET.fromstring(z.read('Metadata/slice_info.config'))
   objects=info.findall('.//object');values={v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')}
   if objects:assert len(objects)==build_count and all(o.get('skipped')=='false' for o in objects)
   model_cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
   assert len(model_cfg.findall('object'))==build_count
   if name.startswith('01-'):
    assert all(o.find('metadata[@key="support_object_xy_distance"]').get('value')=='0.8' and o.find('metadata[@key="support_on_build_plate_only"]').get('value')=='1' and o.find('metadata[@key="brim_width"]').get('value')=='0' for o in model_cfg.findall('object'))
   assert values['outside']=='false'
   settings=json.loads(z.read('Metadata/project_settings.config'))
   assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['wall_loops']=='4' and settings['enable_support']=='1'
   root=ET.fromstring(z.read('3D/3dmodel.model'));got=[]
   assert len(root.find('m:build',NS))==build_count
   for comp in root.findall('.//m:component',NS):
    path=comp.get(PROD+'path').lstrip('/');sub=ET.fromstring(z.read(path))
    m=mesh(sub.find(".//m:object[@id='"+comp.get('objectid')+"']/m:mesh",NS));label=Path(path).stem.rsplit('_',1)[0]
    if label not in all_meshes:
     part=model_cfg.find(".//part[@id='"+comp.get('objectid')+"']")
     label=part.find("metadata[@key='name']").get('value')
    expected=all_meshes[label]
    owner=next(o for o in root.findall('m:resources/m:object',NS) if comp in o.findall('m:components/m:component',NS))
    instance=root.find("m:build/m:item[@objectid='"+owner.get('id')+"']",NS)
    world=m.vertices.copy()
    for element in (comp,instance):
     transform=np.array([float(v) for v in element.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()])
     world=world@transform[:9].reshape(3,3)+transform[9:]
    assert cKDTree(expected.vertices).query(world)[0].max()<4e-5,(label,'assembly placement changed')
    assert m.is_watertight and m.is_winding_consistent and m.volume>0 and m.body_count==1
    assert len(m.faces)==len(expected.faces) and abs(m.volume-expected.volume)<.05
    assert np.allclose(np.sort(m.extents),np.sort(expected.extents),atol=2e-5)
    # The slicer stores float32 mesh coordinates; tolerate <0.00003 mm recentering error.
    av=expected.vertices-expected.bounds.mean(axis=0);bv=m.vertices-m.bounds.mean(axis=0)
    vertex_error=float(cKDTree(av).query(bv)[0].max())
    ac=expected.triangles_center-expected.bounds.mean(axis=0);bc=m.triangles_center-m.bounds.mean(axis=0)
    face_error=float(cKDTree(ac).query(bc)[0].max())
    assert vertex_error<3e-5 and face_error<3e-5,(label,vertex_error,face_error)
    if label in blockers:
     metadata_parts=model_cfg.findall('.//part')
     matching=[p for p in metadata_parts if any(v.get('key')=='name' and v.get('value')==label for v in p.findall('metadata'))]
     assert len(matching)==1 and matching[0].get('subtype')=='support_blocker'
    else:got.append(label)
   assert set(got)==set(want)
   gcode=z.read('Metadata/plate_1.gcode');assert b';LAYER_CHANGE' in gcode
   (WORK/f'{name}.gcode').write_bytes(gcode)
  row.update(passed=True,warnings=[w.attrib for w in info.findall('.//warning')],objects=got,non_printing_support_blockers=list(blockers),slice_metadata=values,project_sha256=sha(dest),project=dest.name,gcode_sha256=hashlib.sha256(gcode).hexdigest())
  (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')
  print(name,values['prediction'],values['weight'],'PASS',flush=True)
 if previous and '02-sliding-board-tops' in previous['plates']:
  row=previous['plates']['02-sliding-board-tops']
  assert row['input_sha256']==sha(OUT/'plates/02-sliding-board-tops.3mf') and row['project_sha256']==sha(OUT/'PRINT'/row['project'])
  report['plates']['02-sliding-board-tops']=row
  report['board_profiles']=previous.get('board_profiles','See board-inlays/profiles')
 report['total_estimated_seconds']=sum(int(p['slice_metadata']['prediction']) for p in report['plates'].values())
 report['total_estimated_grams']=sum(float(p['slice_metadata']['weight']) for p in report['plates'].values())
 (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
