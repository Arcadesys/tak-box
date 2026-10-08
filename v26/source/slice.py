"""Dry slice both V26 mechanism trials, mesh readback and bearing-path checks."""
from pathlib import Path
import sys,json,subprocess,hashlib,xml.etree.ElementTree as ET
from zipfile import ZipFile
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1]
sys.path.append(str(OUT/'reference/v24/source'))
import slice_case as ref
from inspect_case_layers import parse
from verify_pin_toolpaths import hits
from verify_pip_hinges import bead_ranges
EXE=ref.EXE;NS=ref.NS;PROD=ref.PROD

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hook_checks(path,shift):
 segs=parse(path);rows=[];x=shift[0]+4.;y=shift[1]+100.8;z0=5.8
 P=np.array([[p[0][0],p[0][1],z] for z,_,p in segs]);Q=np.array([[p[1][0],p[1][1],z] for z,_,p in segs]);support=np.array([r.startswith('Support') for _,r,_ in segs])
 n=int(hits(P[support],Q[support],np.array([shift[0]+2.4,y,z0]),np.array([shift[0]+5.6,y,z0]),2.4).sum())
 rows.append(dict(name='No support centerlines inside hook bearing',pass_=n==0,intrusions=n))
 levels=sorted({z for z,_,_ in segs});views=[]
 for dz in (-1,-.6,-.2,.2,.6,1):
  z=min(levels,key=lambda zz:abs(zz-(z0+dz)))
  crop=[(r,p) for zz,r,p in segs if zz==z and min(q[0] for q in p)<x+.5 and max(q[0] for q in p)>x-.5 and min(q[1] for q in p)<y+7 and max(q[1] for q in p)>y-7]
  ranges=bead_ranges([(r,[(p[0][1],p[0][0]),(p[1][1],p[1][0])]) for r,p in crop],x)
  centers=[i for i,q in enumerate(ranges) if q[0]<y+1.2 and q[1]>y-1.2];gaps=[]
  if centers:
   a,b=min(centers),max(centers)
   if a>0 and b+1<len(ranges):gaps=[ranges[a][0]-ranges[a-1][1],ranges[b+1][0]-ranges[b][1]]
  rows.append(dict(name=f'Hook radial bead gaps Z{z}',pass_=bool(len(gaps)==2 and min(gaps)>.1),gaps_mm=gaps))
  views.append((z,crop,gaps))
 for dz in (-.6,.6):
  z=min(levels,key=lambda zz:abs(zz-(z0+dz)))
  for dy in (-3.2,3.2):
   at=y+dy
   crop=[(r,p) for zz,r,p in segs if zz==z and min(q[1] for q in p)<at+.5 and max(q[1] for q in p)>at-.5 and min(q[0] for q in p)<shift[0]+10 and max(q[0] for q in p)>shift[0]-.1]
   ranges=bead_ranges(crop,at);centers=[i for i,q in enumerate(ranges) if q[0]<x+.5 and q[1]>x-.5];gaps=[]
   if centers:
    a,b=min(centers),max(centers)
    if a>0 and b+1<len(ranges):gaps=[ranges[a][0]-ranges[a-1][1],ranges[b+1][0]-ranges[b][1]]
   rows.append(dict(name=f'Hook face bead gaps Z{z} Y{at}',pass_=bool(len(gaps)==2 and min(gaps)>.1),gaps_mm=gaps))
 import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 fig,axes=plt.subplots(2,3,figsize=(17,10))
 for ax,(z,crop,gaps) in zip(axes.flat,views):
  for sup,col,style in [(False,'#123957','solid'),(True,'#9a3150','dashed')]:ax.add_collection(LineCollection([p for role,p in crop if role.startswith('Support')==sup],colors=col,linestyles=style,linewidths=1.5))
  ax.axvline(x,color='black',ls=':');ax.set_xlim(x-4.5,x+4.5);ax.set_ylim(y-7,y+7);ax.set_aspect('equal');ax.set_title(f'Z{z:g}: '+', '.join(f'{g:.2f} mm' for g in gaps),fontsize=18);ax.tick_params(labelsize=12)
 fig.suptitle('Captive hook — sampled actual paths / 0.50 mm assumed bead width',fontsize=22);fig.tight_layout(rect=(0,0,1,.94));fig.savefig(OUT/'previews/07-hook-sliced-gaps.png',dpi=120);plt.close(fig)
 return rows

def main():
 proc=OUT/'profiles/process-case.json';settings=json.loads(proc.read_text())
 settings.update(name='Tak V26 mechanism trials 0.20 PLA',print_settings_id='Tak V26 mechanism trials 0.20 PLA',setting_id='tak-v26-mechanisms-020',brim_width='0',support_on_build_plate_only='1',support_object_xy_distance='0.8',inner_wall_speed='40',outer_wall_speed='30',top_surface_speed='35',sparse_infill_speed='80',support_speed='40',support_interface_speed='30')
 proc.write_text(json.dumps(settings,indent=2)+'\n');stage=OUT/'.slicer-work';stage.mkdir(exist_ok=True)
 reports={}
 for plate in ('01-V26-captive-hook-trial','02-V26-board-clip-trial'):
  src=OUT/'plates'/f'{plate}.3mf';dest=OUT/'SMALL-TRIALS'/f'{plate}-CC2-PLA.3mf'
  cmd=[str(EXE),'--datadir',str(stage/'config'),'--load-settings',str(OUT/'profiles/machine.json')+';'+str(proc),'--load-filaments',str(OUT/'profiles/filament-pla.json'),'--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(src)]
  if '--verify-only' in sys.argv and dest.exists():p=subprocess.CompletedProcess(cmd,0)
  else:
   p=subprocess.run(cmd,capture_output=True,text=True,timeout=300);(OUT/'reports'/f'{plate}-slice.log').write_text(p.stdout+p.stderr)
  assert p.returncode==0,plate
  with ZipFile(src) as z:
   root=ET.fromstring(z.read('3D/3dmodel.model'));want={o.get('name'):ref.mesh(o.find('m:mesh',NS)) for o in root.findall('m:resources/m:object',NS) if o.find('m:mesh',NS) is not None};build_count=len(root.find('m:build',NS))
  with ZipFile(dest) as z:
   assert z.testzip() is None;info=ET.fromstring(z.read('Metadata/slice_info.config'));values={v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')};assert values['outside']=='false'
   cfg=ET.fromstring(z.read('Metadata/model_settings.config'));root=ET.fromstring(z.read('3D/3dmodel.model'));assert len(root.find('m:build',NS))==build_count
   got=[];checks=[]
   for comp in root.findall('.//m:component',NS):
    sub=ET.fromstring(z.read(comp.get(PROD+'path').lstrip('/')));m=ref.mesh(sub.find(".//m:object[@id='"+comp.get('objectid')+"']/m:mesh",NS))
    part=cfg.find(".//part[@id='"+comp.get('objectid')+"']");label=part.find("metadata[@key='name']").get('value');expected=want[label]
    owner=next(o for o in root.findall('m:resources/m:object',NS) if comp in o.findall('m:components/m:component',NS));instance=root.find("m:build/m:item[@objectid='"+owner.get('id')+"']",NS)
    v=m.vertices.copy()
    for el in (comp,instance):
     q=np.array([float(a) for a in el.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()]);v=v@q[:9].reshape(3,3)+q[9:]
    shift=float(expected.bounds[0,2]-v[:,2].min());assert abs(shift)<.002;expected.apply_translation([0,0,-shift]);forward=cKDTree(expected.vertices).query(v)[0];back=cKDTree(v).query(expected.vertices)[0]
    a=float(forward.max());b=float(back.max())
    if a>=4e-5:a=float(trimesh.proximity.closest_point_naive(expected,v[forward>=4e-5])[1].max())
    if b>=4e-5:b=float(trimesh.proximity.closest_point_naive(trimesh.Trimesh(vertices=v,faces=m.faces,process=False),expected.vertices[back>=4e-5])[1].max())
    assert max(a,b)<.002 and abs(m.volume-expected.volume)<.05
    got.append(label);checks.append(dict(name=label,watertight=True,single_body=True,surface_error_mm=max(a,b),volume_error_mm3=float(m.volume-expected.volume)))
   assert set(got)==set(want)
   settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['wall_loops']=='4' and settings['layer_height']=='0.2' and settings['support_on_build_plate_only']=='1' and settings['brim_width']=='0'
   gcode=z.read('Metadata/plate_1.gcode');assert b';LAYER_CHANGE' in gcode;(stage/f'{plate}.gcode').write_bytes(gcode)
   rows=hook_checks(stage/f'{plate}.gcode',json.loads((OUT/'reports/trial-geometry.json').read_text())['hook_print_translation_mm']) if plate.startswith('01') else []
   reports[plate]=dict(passed=all(q['pass_'] for q in rows),exit_code=p.returncode,command=cmd,input_sha256=sha(src),project_sha256=sha(dest),profiles_sha256={p.name:sha(p) for p in (OUT/'profiles').glob('*.json')},mesh_readback=checks,plate_metadata=values,bearing_checks=rows,warnings=[x.attrib for x in info.findall('.//warning')],gcode_sha256=hashlib.sha256(gcode).hexdigest())
   (OUT/'reports/slicing.json').write_text(json.dumps(dict(plates=reports,physical_acceptance=False,printer_started=False,source_sha256={str(p.relative_to(OUT)):sha(p) for p in (OUT/'source').glob('*.py')},scope='Dry trial slices; sampled 0.50 mm bead gaps and support-centerline checks, not release force or durability.'),indent=2)+'\n')
   assert reports[plate]['passed'],rows
   print(plate,'PASS',values['prediction'],'seconds',values['weight'],'grams',flush=True)
if __name__=='__main__':main()
