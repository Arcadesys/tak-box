"""CC2 PLA dry slice and fresh mesh/profile/G-code readback. Never sends a print."""
from pathlib import Path
import sys,json,subprocess,hashlib,xml.etree.ElementTree as ET
from zipfile import ZipFile
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1];V25=OUT.parent
sys.path.insert(0,str(V25/'reference/v24/source'))
import slice_case as ref
EXE=ref.EXE;NS=ref.NS;PROD=ref.PROD
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 proc=OUT/'profiles/process-case.json';settings=json.loads(proc.read_text())
 settings.update(name='Tak V25 fixed storage bodies 0.20 PLA',print_settings_id='Tak V25 fixed storage bodies 0.20 PLA',setting_id='tak-v25-fixed-storage-020',brim_width='2',inner_wall_speed='40',outer_wall_speed='30',top_surface_speed='35',sparse_infill_speed='80',support_speed='40',support_interface_speed='30')
 proc.write_text(json.dumps(settings,indent=2)+'\n')
 stage=OUT/'.slicer-work';stage.mkdir(exist_ok=True)
 src=OUT/'plates/01-V25-fixed-storage-bodies.3mf';dest=OUT/'PRINT/01-V25-fixed-storage-bodies-CC2-PLA.3mf'
 cmd=[str(EXE),'--datadir',str(stage/'config'),'--load-settings',str(OUT/'profiles/machine.json')+';'+str(proc),'--load-filaments',str(OUT/'profiles/filament-pla.json'),'--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(src)]
 if '--verify-only' in sys.argv:
  code=0
 else:
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=300);(OUT/'reports/slice.log').write_text(p.stdout+p.stderr);code=p.returncode
 report=dict(command=cmd,exit_code=code,slicer='ElegooSlicer 2.4.2',input_sha256=sha(src),profiles_sha256={p.name:sha(p) for p in (OUT/'profiles').glob('*.json')},physical_acceptance=False,printer_started=False)
 if code:
  (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2));raise RuntimeError('Dry slice failed; see reports/slice.log')
 with ZipFile(src) as z:
  root=ET.fromstring(z.read('3D/3dmodel.model'));want={o.get('name'):ref.mesh(o.find('m:mesh',NS)) for o in root.findall('m:resources/m:object',NS)}
 checks=[]
 with ZipFile(dest) as z:
  assert z.testzip() is None
  info=ET.fromstring(z.read('Metadata/slice_info.config'));values={v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')}
  assert values['outside']=='false'
  cfg=ET.fromstring(z.read('Metadata/model_settings.config'));root=ET.fromstring(z.read('3D/3dmodel.model'))
  assert len(root.find('m:build',NS))==len(want)==2
  got=[]
  for comp in root.findall('.//m:component',NS):
   sub=ET.fromstring(z.read(comp.get(PROD+'path').lstrip('/')));m=ref.mesh(sub.find(".//m:object[@id='"+comp.get('objectid')+"']/m:mesh",NS))
   part=cfg.find(".//part[@id='"+comp.get('objectid')+"']");label=part.find("metadata[@key='name']").get('value');expected=want[label]
   owner=next(o for o in root.findall('m:resources/m:object',NS) if comp in o.findall('m:components/m:component',NS));instance=root.find("m:build/m:item[@objectid='"+owner.get('id')+"']",NS)
   v=m.vertices.copy()
   for el in (comp,instance):
    x=np.array([float(q) for q in el.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()]);v=v@x[:9].reshape(3,3)+x[9:]
   # --ensure-on-bed removes tiny tessellation placement offsets (up to .0014 mm).
   shift=float(expected.bounds[0,2]-v[:,2].min());assert abs(shift)<.002
   expected.apply_translation([0,0,-shift])
   errors=cKDTree(expected.vertices).query(v)[0];back_errors=cKDTree(v).query(expected.vertices)[0]
   # Slicer re-triangulates small coplanar label faces. Compare surfaces for changed vertices.
   forward=float(errors.max());backward=float(back_errors.max())
   if forward>=4e-5:forward=float(trimesh.proximity.closest_point_naive(expected,v[errors>=4e-5])[1].max())
   if backward>=4e-5:
    world=trimesh.Trimesh(vertices=v,faces=m.faces,process=False)
    backward=float(trimesh.proximity.closest_point_naive(world,expected.vertices[back_errors>=4e-5])[1].max())
   error=max(forward,backward)
   # 0.002 mm surface tolerance is <1% of the smallest 0.20 mm trial clearance.
   # A new coplanar/edge vertex may lie .0009 mm from the original tessellated surface.
   assert error<.002 and abs(m.volume-expected.volume)<.05,(label,error,len(m.faces),len(expected.faces),m.volume,expected.volume)
   got.append(label);checks.append(dict(name=label,watertight=True,single_body=True,symmetric_vertex_to_surface_error_mm=error,ensure_on_bed_shift_mm=-shift,source_triangles=len(expected.faces),sliced_triangles=len(m.faces),volume_error_mm3=float(m.volume-expected.volume)))
  assert set(got)==set(want)
  gcode=z.read('Metadata/plate_1.gcode');assert b';LAYER_CHANGE' in gcode
  (stage/'coupon.gcode').write_bytes(gcode)
  settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['wall_loops']=='4' and settings['layer_height']=='0.2' and settings['enable_support']=='1'
  report.update(passed=True,surface_tolerance_mm=.002,mesh_readback=checks,plate_metadata=values,warnings=[x.attrib for x in info.findall('.//warning')],project_sha256=sha(dest),gcode_sha256=hashlib.sha256(gcode).hexdigest(),embedded_gcode=True)
 (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n');print('Slice/readback PASS',values['prediction'],'seconds',values['weight'],'grams')
if __name__=='__main__':main()
