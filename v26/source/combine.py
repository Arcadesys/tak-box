"""Place the unchanged hook and clip trials together; retain captive geometry."""
from pathlib import Path
from zipfile import ZipFile
import importlib.util,json,sys,hashlib,xml.etree.ElementTree as ET
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('layout',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,(name,detail)
b.b.e.check=check;b.b.pkg.check=check;b.b.pkg.OUT=OUT

def main():
 items=[];sources={}
 for name in ('hook-trial-fixture','hook-trial','clip-trial-seat','clip-trial-board'):
  p=OUT/'models'/f'{name}.step';s=cq.importers.importStep(str(p)).val();sources[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
  if name.startswith('clip'):s=s.translate((32,0,0))
  check(name+' unchanged single valid solid',s.isValid() and len(s.Solids())==1)
  bb=s.BoundingBox();check(name+' CC2 bed bounds',bb.xmin>=-.002 and bb.ymin>=-.002 and abs(bb.zmin)<.002 and bb.xmax<256 and bb.ymax<256 and bb.zmax<250)
  items.append((name,s))
 for i,(name,s) in enumerate(items):
  for other,t in items[i+1:]:check(name+'/'+other+' no overlap',b.ov(s,t)<1e-5)
 check('hook/clip fixture separation at least 16mm',items[2][1].BoundingBox().xmin-items[0][1].BoundingBox().xmax>16)
 plate='03-V26-combined-mechanism-trials';b.b.e.plate(plate,items);b.b.pkg.housing_support_clearance(plate,items)
 with ZipFile(OUT/'plates'/f'{plate}.3mf') as z:
  root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'m':b.b.e.NS}
  check('all four parts retain one placed assembly',len(root.findall('m:build/m:item',ns))==1 and len(root.findall('.//m:component',ns))==4)
  check('four unique named meshes retained',set(o.get('name') for o in root.findall('m:resources/m:object',ns) if o.find('m:mesh',ns) is not None)=={n for n,_ in items})
 report=dict(passed=True,checks=checks,command=[sys.executable,str(Path(__file__).resolve())],source_sha256=sources,hook_translation_from_original_plate_mm=[0,0,0],clip_translation_from_original_plate_mm=[32,0,0],hook_print_translation_mm=[8,-60,0],geometry_changed=False,physical_acceptance=False,printer_started=False)
 (OUT/'reports/combined-layout.json').write_text(json.dumps(report,indent=2)+'\n')
 import render_utils as r
 r.OUT=OUT;r.colors.update(hook=(.95,.55,.12),clip=(.32,.47,.60))
 scene=[(('hook-moving' if n=='hook-trial' else 'clip-'+n if n.startswith('clip') else 'housing-fixture'),s) for n,s in items]
 r.render('08-combined-trials',scene,'V26 — hook and board clip trials / one plate',(-120,-180,220))
 print('PASS',len(checks),'combined placement and 3MF checks')
if __name__=='__main__':main()
