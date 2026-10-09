"""Fresh extraction audit and isolated rebuild of the two small mechanism trials."""
from pathlib import Path
import hashlib,json,tempfile,zipfile,subprocess,sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def error(a,b):
 d=cKDTree(b.vertices).query(a.vertices)[0];q=a.vertices[d>=4e-5]
 return float(trimesh.proximity.closest_point_naive(b,q)[1].max()) if len(q) else float(d.max())
def main():
 kit=OUT/'V26-MECHANISM-REVIEW.zip'
 with tempfile.TemporaryDirectory(prefix='tak-v26-trial-rebuild-') as td:
  with zipfile.ZipFile(kit) as z:
   assert z.testzip() is None;manifest=json.loads(z.read('v26/MANIFEST.json'))
   for row in manifest['files']:
    data=z.read('v26/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
   z.extractall(td)
  root=Path(td)/'v26'
  p=subprocess.run([sys.executable,str(root/'source/trial.py')],cwd=td,capture_output=True,text=True,timeout=300)
  (OUT/'reports/reproduction-trial.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-500:]
  rows=[]
  for n in ('hook-trial-fixture','hook-trial','clip-trial-seat','clip-trial-board'):
   a=trimesh.load_mesh(OUT/'models'/f'{n}.stl');b=trimesh.load_mesh(root/'models'/f'{n}.stl');gap=max(error(a,b),error(b,a))
   assert a.is_watertight and b.is_watertight and a.body_count==1 and b.body_count==1 and gap<.002 and abs(a.volume-b.volume)<.05
   rows.append(dict(name=n,surface_error_mm=gap,volume_error_mm3=float(a.volume-b.volume)))
 report=dict(passed=True,scope='All archive bytes audited; only the two small mechanism trials rebuilt in an isolated extraction, not full CAD or slicer reproduction.',command=[sys.executable,str(Path(__file__).resolve())],zip_input_sha256=sha(kit),manifest_files=len(manifest['files']),mesh_equivalence=rows,physical_acceptance=False)
 (OUT/'reports/reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print('Isolated trial rebuild PASS',len(rows),'equivalent meshes')
if __name__=='__main__':main()
