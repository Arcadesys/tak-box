"""Place all integrated case parts on CC2 beds; verify exported geometry."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse,json,sys,xml.etree.ElementTree as ET
import cadquery as cq
import numpy as np
import trimesh
import case as c
sys.path.insert(0,str(c.OUT/'source/vendor/body'))
import export_utils as e
OUT=c.OUT;e.OUT=OUT
cad_mesh=e.mesh
def welded_mesh(shape):
 # CadQuery face tessellations duplicate shared vertices. 3MF needs explicit
 # indexed connectivity, rather than relying on the slicer's mesh repair.
 vertices,faces=cad_mesh(shape)
 m=trimesh.Trimesh(vertices=np.round(vertices,6),faces=faces,process=True)
 m.merge_vertices(digits_vertex=6)
 m.remove_unreferenced_vertices()
 assert m.is_watertight and m.is_winding_consistent and m.body_count==1
 return m.vertices,m.faces
e.mesh=welded_mesh
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok:raise RuntimeError(name)
e.check=check

def load(name,rotation=None):
 p=OUT/'models'/f'{name}.step'
 s=cq.importers.importStep(str(p)).val()
 if rotation:s=s.rotate((0,0,0),rotation[0],rotation[1])
 return s

def place(name,x,y,rotation=None):
 s=load(name,rotation);b=s.BoundingBox()
 return name,s.translate((x-b.xmin,y-b.ymin,-b.zmin))

def housing_support_clearance(name,items):
 # Build-plate-only support cannot grow inside a blind captive socket.
 # No brim on the paired bases: avoid joining their 0.4 mm centre seam.
 path=OUT/'plates'/f'{name}.3mf'
 with ZipFile(path) as z:payload={n:z.read(n) for n in z.namelist()}
 root=ET.fromstring(payload['3D/3dmodel.model']);ns='{'+e.NS+'}'
 ET.SubElement(root,ns+'metadata',name='BambuStudio:3mfVersion').text='1'
 resources=root.find(ns+'resources');build=root.find(ns+'build')
 group_id=str(len(items)+1)
 group=ET.SubElement(resources,ns+'object',id=group_id,type='model',name='captive-hinge-assembly')
 components=ET.SubElement(group,ns+'components')
 for i in range(1,len(items)+1):ET.SubElement(components,ns+'component',objectid=str(i))
 for el in list(build):build.remove(el)
 ET.SubElement(build,ns+'item',objectid=group_id)
 config=ET.Element('config');obj=ET.SubElement(config,'object',id=group_id)
 for key,value in {'name':'captive-hinge-assembly','support_object_xy_distance':'0.8','support_on_build_plate_only':'1','brim_width':'0'}.items():ET.SubElement(obj,'metadata',key=key,value=value)
 for i,(part,_) in enumerate(items,1):
  volume=ET.SubElement(obj,'part',id=str(i),subtype='normal_part')
  ET.SubElement(volume,'metadata',key='name',value=part)
 payload['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
 payload['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
 with ZipFile(path,'w',ZIP_DEFLATED) as z:
  for n,data in payload.items():z.writestr(n,data)
 with ZipFile(path) as z:
  assert z.testzip() is None
  cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
  check(name+' joint support and brim overrides',all(o.find('metadata[@key="support_on_build_plate_only"]').get('value')=='1' and o.find('metadata[@key="brim_width"]').get('value')=='0' for o in cfg.findall('object')))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+');args=parser.parse_args()
 plans={
 '01-print-in-place-bases':[(n,load(n).translate(c.PRINT_BASE_SHIFT)) for n in ['housing-left','housing-right']],
 '02-sliding-board-tops':[place('board-left',7,7),place('board-right',121,7)],
 '03-flat-capstones-hook-and-collar':[place('capstone-cat',7,7),place('capstone-witch',45,7),place('side-hook',85,7,((0,1,0),90)),place('axle-end-cap',125,7)],
 }
 rows={}
 for name,items in plans.items():
  for i,(label,s) in enumerate(items):
   a=s.BoundingBox()
   check(name+'/'+label+' bed and build height',a.xmin>=6.9 and a.ymin>=6.9 and a.xmax<=249 and a.ymax<=249 and a.zmax<=250 and a.zmin>=-1e-6,[a.xlen,a.ylen,a.zlen])
   for label2,t in items[i+1:]:
    b=t.BoundingBox();gap=max(b.xmin-a.xmax,a.xmin-b.xmax,b.ymin-a.ymax,a.ymin-b.ymax)
    check(label+' separation '+label2,s.intersect(t).Volume()<1e-5 if name=='01-print-in-place-bases' else gap>=5,{'bounding_gap_mm':gap,'paired_captive_hinges':name=='01-print-in-place-bases'})
  if not args.only or name in args.only:
   e.plate(name,items)
   if name.startswith('01-'):
    housing_support_clearance(name,items)
  rows[name]={'objects':[n for n,_ in items],'orientation':'Bases broad bottom down; sliding boards directly on their flat underside, playing faces up; capstones broad bottom down; hook flat; collar bore up.','supports':True,'support_object_xy_distance_mm':.8 if name.startswith('01-') else .35}
 (OUT/'reports/plates.json').write_text(json.dumps({'bed_mm':[256,256],'checks':checks,'plates':rows,'filament_pins_printed':False,'physical_acceptance':False},indent=2)+'\n')
 print('Three complete-case geometry plates exported and read back.')
if __name__=='__main__':main()
