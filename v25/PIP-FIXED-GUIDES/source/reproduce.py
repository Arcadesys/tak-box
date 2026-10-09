"""Verify ZIP hashes and rebuild extracted guided body and PIP trial geometry without its checkout."""
from pathlib import Path
import hashlib,json,tempfile,zipfile,subprocess,sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def surface_error(a,b):
 errors=cKDTree(b.vertices).query(a.vertices)[0]
 q=a.vertices[errors>=4e-5]
 return float(trimesh.proximity.closest_point_naive(b,q)[1].max()) if len(q) else float(errors.max())
def main():
 kit=OUT/'V25-PIP-FIXED-GUIDES.zip';tested_hash=sha(kit)
 with tempfile.TemporaryDirectory(prefix='tak-v25-PIP-rebuild-') as td:
  with zipfile.ZipFile(kit) as z:
   assert z.testzip() is None
   manifest=json.loads(z.read('v25/PIP-FIXED-GUIDES/MANIFEST.json'))
   for row in manifest['files']:
    data=z.read('v25/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
   z.extractall(td)
  v25=Path(td)/'v25';root=v25/'PIP-FIXED-GUIDES'
  p=subprocess.run([sys.executable,str(root/'source/build.py')],cwd=td,capture_output=True,text=True,timeout=900)
  (OUT/'reports/reproduction-build.log').write_text(p.stdout+p.stderr)
  assert p.returncode==0,p.stderr[-500:]
  p=subprocess.run([sys.executable,str(root/'source/trial.py')],cwd=td,capture_output=True,text=True,timeout=300)
  assert p.returncode==0,p.stderr[-500:]
  geo=json.loads((root/'reports/geometry.json').read_text());rows=[]
  for f in sorted((OUT/'models').glob('*.stl')):
   a=trimesh.load(f,force='mesh');b=trimesh.load(root/'models'/f.name,force='mesh')
   err=max(surface_error(a,b),surface_error(b,a))
   assert err<.002 and np.max(abs(a.extents-b.extents))<.002 and abs(a.volume-b.volume)<.05,(f.name,err)
   rows.append(dict(name=f.name,surface_error_mm=err,volume_error_mm3=float(a.volume-b.volume)))
  assert len(rows)==4
  source_hashes={str(p.relative_to(v25)):sha(p) for p in v25.rglob('*.py')}
  assert all(sha(OUT.parent/rel)==h for rel,h in source_hashes.items())
  d=dict(passed=True,tested_snapshot_zip_sha256=tested_hash,geometry_checks=len(geo['checks']),named_printed_parts=len(rows),surface_tolerance_mm=.002,mesh_checks=rows,checked_source_sha256=source_hashes,physical_acceptance=False)
  (OUT/'reports/reproduction.json').write_text(json.dumps(d,indent=2)+'\n')
  print('Fresh extraction rebuild PASS:',len(geo['checks']),'geometry checks;',len(rows),'equivalent meshes')
if __name__=='__main__':main()
