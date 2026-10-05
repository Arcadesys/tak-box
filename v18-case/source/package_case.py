"""Place all integrated case parts on CC2 beds; verify exported geometry."""
from pathlib import Path
from zipfile import ZipFile
import argparse,json,sys,xml.etree.ElementTree as ET
import cadquery as cq
import numpy as np
import trimesh
import case as c
sys.path.insert(0,str(c.REPO/'v17-four-leaf/source'))
import export_utils as e
OUT=c.REPO/'v18-case';e.OUT=OUT
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok:raise RuntimeError(name)
e.check=check

def load(name,rotation=None):
 p=(c.REPO/'v18-recessed-clasp/parts/V18-slider.step' if name=='clasp-slider' else OUT/'models'/f'{name}.step')
 s=cq.importers.importStep(str(p)).val()
 if rotation:s=s.rotate((0,0,0),rotation[0],rotation[1])
 return s

def place(name,x,y,rotation=None):
 s=load(name,rotation);b=s.BoundingBox()
 return name,s.translate((x-b.xmin,y-b.ymin,-b.zmin))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+');args=parser.parse_args()
 plans={
 '01-left-housing-clasp-and-cap-compartment':[place('housing-left',10,7,((1,0,0),-90))],
 '02-right-housing-and-keeper':[place('housing-right',10,10,((1,0,0),-90))],
 '03-board-leaves':[place('board-left',7,7),place('board-right',115,7)],
 '04-piece-drawers':[place('drawer-left',7,7,((0,1,0),90)),place('drawer-right',24,7,((0,1,0),-90))],
 '05-hatch-slider-and-four-axle-caps':[place('capstone-hatch',7,7),place('clasp-slider',110,7)]+[(f'axle-end-cap-{i+1}',place('axle-end-cap',110+12*i,50)[1]) for i in range(4)],
 }
 rows={}
 for name,items in plans.items():
  for i,(label,s) in enumerate(items):
   a=s.BoundingBox()
   check(name+'/'+label+' bed and build height',a.xmin>=6.9 and a.ymin>=6.9 and a.xmax<=249 and a.ymax<=249 and a.zmax<=250 and a.zmin>=-1e-6,[a.xlen,a.ylen,a.zlen])
   for label2,t in items[i+1:]:
    b=t.BoundingBox();gap=max(b.xmin-a.xmax,a.xmin-b.xmax,b.ymin-a.ymax,a.ymin-b.ymax)
    check(label+' separation '+label2,gap>=5,gap)
  if not args.only or name in args.only:e.plate(name,items)
  rows[name]={'objects':[n for n,_ in items],'orientation':'Side-oriented housings and drawers; boards/hatch face up; original frozen slider side orientation; axle caps bore up.','supports':True}
 (OUT/'reports/plates.json').write_text(json.dumps({'bed_mm':[256,256],'checks':checks,'plates':rows,'steel_axles_printed':False,'physical_acceptance':False},indent=2)+'\n')
 print('Five complete-case geometry plates exported and read back.')
if __name__=='__main__':main()
