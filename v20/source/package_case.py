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

def housing_support_clearance(name,part):
 # Keep support away from the 2 mm bore walls. This applies to housings only;
 # boards and lids retain the 0.35 mm global side clearance.
 path=OUT/'plates'/f'{name}.3mf'
 with ZipFile(path) as z:payload={n:z.read(n) for n in z.namelist()}
 root=ET.fromstring(payload['3D/3dmodel.model']);ns='{'+e.NS+'}'
 ET.SubElement(root,ns+'metadata',name='BambuStudio:3mfVersion').text='1'
 config=ET.Element('config');obj=ET.SubElement(config,'object',id='1')
 ET.SubElement(obj,'metadata',key='name',value=part)
 ET.SubElement(obj,'metadata',key='support_object_xy_distance',value='0.8')
 volume=ET.SubElement(obj,'part',id='1',subtype='normal_part')
 ET.SubElement(volume,'metadata',key='name',value=part)
 payload['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
 payload['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
 with ZipFile(path,'w',ZIP_DEFLATED) as z:
  for n,data in payload.items():z.writestr(n,data)
 with ZipFile(path) as z:
  assert z.testzip() is None
  cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
  check(name+' housing support side clearance readback',cfg.find('.//metadata[@key="support_object_xy_distance"]').get('value')=='0.8',{'support_object_xy_distance_mm':.8})

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+');args=parser.parse_args()
 plans={
 '01-left-housing-hook-pivot-and-cap-compartment':[place('housing-left',10,7)],
 '02-right-housing-and-hook-pin':[place('housing-right',10,10)],
 '03-board-leaves':[place('board-left',7,7),place('board-right',115,7)],
 '04-sliding-storage-lids':[place('lid-left',7,7,((1,0,0),180)),place('lid-right',112,7,((1,0,0),180))],
 '05-hatch-hook-and-five-axle-caps':[place('capstone-hatch',7,7,((1,0,0),180)),place('side-hook',110,7,((0,1,0),90))]+[(f'axle-end-cap-{i+1}',place('axle-end-cap',110+12*i,50)[1]) for i in range(5)],
 }
 rows={}
 for name,items in plans.items():
  for i,(label,s) in enumerate(items):
   a=s.BoundingBox()
   check(name+'/'+label+' bed and build height',a.xmin>=6.9 and a.ymin>=6.9 and a.xmax<=249 and a.ymax<=249 and a.zmax<=250 and a.zmin>=-1e-6,[a.xlen,a.ylen,a.zlen])
   for label2,t in items[i+1:]:
    b=t.BoundingBox();gap=max(b.xmin-a.xmax,a.xmin-b.xmax,b.ymin-a.ymax,a.ymin-b.ymax)
    check(label+' separation '+label2,gap>=5,gap)
  if not args.only or name in args.only:
   e.plate(name,items)
   if name.startswith(('01-','02-')):
    housing_support_clearance(name,items[0][0])
  rows[name]={'objects':[n for n,_ in items],'orientation':'Bases broad bottom down; boards face up; sliding lids and hatch broad top face down; hook flat; collars bore up. All parts below 26 mm tall.','supports':True,'support_object_xy_distance_mm':.8 if name.startswith(('01-','02-')) else .35}
 (OUT/'reports/plates.json').write_text(json.dumps({'bed_mm':[256,256],'checks':checks,'plates':rows,'filament_pins_printed':False,'physical_acceptance':False},indent=2)+'\n')
 print('Five complete-case geometry plates exported and read back.')
if __name__=='__main__':main()
