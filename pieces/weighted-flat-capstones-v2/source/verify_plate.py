from pathlib import Path
from zipfile import ZipFile
import json,hashlib,re,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def tx(v,el):
 q=np.array([float(a) for a in el.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()]);return v@q[:9].reshape(3,3)+q[9:]
def main():
 provenance=json.loads((OUT/'reports/plate-provenance.json').read_text());geometry=json.loads((OUT/'reports/geometry.json').read_text());expected={s['name']:s for s in provenance['sources']};project=Path(provenance['saved_project']);checks=[];meshes={}
 with ZipFile(project) as z:
  assert z.testzip() is None
  root=ET.fromstring(z.read('3D/3dmodel.model'));cfg=ET.fromstring(z.read('Metadata/model_settings.config'));settings=json.loads(z.read('Metadata/project_settings.config'));info=ET.fromstring(z.read('Metadata/slice_info.config'))
  objects=root.findall('m:resources/m:object',NS);items=root.findall('m:build/m:item',NS);assert len(items)==len(cfg.findall('object'))==8
  for item in items:
   owner=next(q for q in objects if q.get('id')==item.get('objectid'));meta=cfg.find("object[@id='"+owner.get('id')+"']");name=meta.find("metadata[@key='name']").get('value');src=expected[name];slot=int(meta.find("metadata[@key='extruder']").get('value'));assert slot==src['slot']==3
   comp=owner.find('m:components/m:component',NS);sub=ET.fromstring(z.read(comp.get(PROD+'path').lstrip('/')));mesh=sub.find(".//m:object[@id='"+comp.get('objectid')+"']/m:mesh",NS)
   v=np.array([[float(q.get(k)) for k in ('x','y','z')] for q in mesh.findall('m:vertices/m:vertex',NS)]);f=np.array([[int(q.get(k)) for k in ('v1','v2','v3')] for q in mesh.findall('m:triangles/m:triangle',NS)]);m=trimesh.Trimesh(vertices=tx(tx(v,comp),item),faces=f,process=False)
   original=trimesh.load_mesh(src['source']);original.apply_translation(src['translation_mm']);error=max(cKDTree(original.vertices).query(m.vertices)[0].max(),cKDTree(m.vertices).query(original.vertices)[0].max());assert error<.002 and abs(m.volume-original.volume)<.05
   assert m.is_watertight and m.is_winding_consistent and m.body_count==1 and np.allclose(m.bounds,src['bounds_mm'],atol=.002);assert m.bounds[0,2]>=-.002 and np.all(m.bounds[0,:2]>0) and np.all(m.bounds[1,:2]<256)
   assert len(m.faces)==src['triangles'];assert hashlib.sha256(Path(src['source']).read_bytes()).hexdigest()==src['source_sha256']
   checks.append(dict(name=name,label=src['label'],slot=slot,surface_vertex_error_mm=float(error),volume_error_mm3=float(m.volume-original.volume),watertight=True,bodies=1,bounds_mm=m.bounds.tolist(),faces=len(m.faces)));meshes[name]=m
  values={q.get('key'):q.get('value') for q in info.findall('.//plate/metadata')};assert values['outside']=='false' and values['support_used']=='true'
  assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['layer_height']=='0.2' and settings['curr_bed_type']=='Textured PEI Plate'
  assert settings['nozzle_temperature'][2]=='220' and settings['textured_plate_temp'][2]=='55' and settings['filament_max_volumetric_speed'][2]=='6' and settings['outer_wall_speed']=='40'
  assert settings['enable_support']=='1' and settings['support_on_build_plate_only']=='1' and settings['enable_prime_tower']=='0' and len(settings['filament_settings_id'])==3
  gcode=z.read('Metadata/plate_1.gcode');tools=sorted({int(q) for q in re.findall(rb'^T(\d+)\s*$',gcode,re.M)});assert tools==[2];assert b'M190 S55' in gcode and b'M109 S220' in gcode
  (OUT/'reports/sample.gcode').write_bytes(gcode);warnings=[q.attrib for q in info.findall('.//warning')]
 assert geometry['equal_closed_volume_error_ml']<1e-6 and geometry['equal_usable_volume_error_ml']<1e-6
 report=dict(passed=True,logical_pieces=4,object_count=8,used_filament_slots=[3],components_separate=True,full_sets=False,project_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),source_provenance=provenance,geometry_report_sha256=hashlib.sha256((OUT/'reports/geometry.json').read_bytes()).hexdigest(),mesh_readback=checks,gcode_tools_zero_based=tools,plate_metadata=values,slicer_warnings=warnings,profile_summary={k:settings.get(k) for k in ('printer_model','printer_settings_id','print_settings_id','filament_settings_id','filament_colour','curr_bed_type','layer_height','sparse_infill_density','enable_support','support_on_build_plate_only','enable_prime_tower','nozzle_temperature','textured_plate_temp','filament_max_volumetric_speed','outer_wall_speed')},physical_acceptance=False,printer_started=False,ui_visible_loaded=False)
 (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n');np.savez(OUT/'reports/readback-meshes.npz',**{n+'-vertices':m.vertices for n,m in meshes.items()},**{n+'-faces':m.faces for n,m in meshes.items()})
 print(json.dumps({k:report[k] for k in ('passed','object_count','gcode_tools_zero_based','plate_metadata','slicer_warnings')},indent=2))
if __name__=='__main__':main()
