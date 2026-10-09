"""Package only V26 review assets, audit preserved kits and bundled references."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,sys,platform,importlib.metadata
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
PRESERVED={
 'v25/V25-COUPON-KIT.zip':'7075ba1bbb3f7cbd5c867683f46d221b398a2e9b99c92eaa9ec10cae26318cd7',
 'v25/STRENGTH-TRIAL/V25-STRENGTH-TRIAL.zip':'86ece451aa864eb21081b00a71c4a63c0f50f366332ef8c02a6d3b3a40ef0207',
 'v25/REINFORCED-B-TRIAL/V25-REINFORCED-B-TRIAL.zip':'8ced9ddb737f98ca3d1ae8244da7c5f2a6d9f21eb6f82ad7a1cdc5bcf0065918',
 'v25/FIXED-STORAGE/V25-FIXED-STORAGE.zip':'2e20be6253a648bc97d1ff586b569e7a9526fc28d59383c1fe6030f8e40c1dd0',
 'v25/PIP-FIXED-STORAGE/V25-PIP-FIXED-STORAGE.zip':'6ab929a3ac146cfcc17d7eb8d5181fefd56c9f3c6590bc994f5ac5acf1bcc86d',
 'v25/PIP-FIXED-GUIDES/V25-PIP-FIXED-GUIDES.zip':'a17e0f3c72a07d5eec62562ba31813165b0ae1383047639712febd2cc6c682e5'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():return sorted(p for p in OUT.rglob('*') if p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(OUT).parts) and p.suffix not in ('.zip','.pyc') and p.name!='MANIFEST.json' and p.name not in ('package.json','package.log'))
def main():
 preserved={}
 for name,want in PRESERVED.items():
  p=ROOT/name
  if p.exists():assert sha(p)==want,name;preserved[name]=want
 geometry=json.loads((OUT/'reports/geometry.json').read_text());trials=json.loads((OUT/'reports/trial-geometry.json').read_text());slices=json.loads((OUT/'reports/slicing.json').read_text())
 assert geometry['passed'] and trials['passed'] and all(p['passed'] for p in slices['plates'].values())
 for plate,row in slices['plates'].items():
  assert sha(OUT/'plates'/f'{plate}.3mf')==row['input_sha256'] and sha(OUT/'SMALL-TRIALS'/f'{plate}-CC2-PLA.3mf')==row['project_sha256']
  assert all(sha(OUT/'profiles'/name)==digest for name,digest in row['profiles_sha256'].items())
 for name,digest in geometry['source_sha256'].items():assert sha(OUT/name)==digest,(name,'changed after build')
 versions={n:importlib.metadata.version(n) for n in ('cadquery','vtk','trimesh','numpy','scipy','matplotlib','Pillow')}
 report=dict(passed=True,command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,platform=platform.platform(),dependencies=versions,preserved_archives=preserved,clip_arm_mm=2.4,clip_root_mm=3.2,clip_root_blend_mm=1.2,assumed_clip_release_mm=2.8,hook_axle_mm=4,hook_boss_mm=11.6,hook_outer_cheek_mm=2,hook_frame_bridge_mm=3.4,hook_radial_face_gaps_mm=.4,physical_acceptance=False,printer_started=False)
 (OUT/'reports/provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 selected=files();manifest=dict(version='V26 mechanism review',units='mm',files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in selected])
 (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');kit=OUT/'V26-MECHANISM-REVIEW.zip'
 with ZipFile(kit,'w',ZIP_DEFLATED) as z:
  for p in selected+[OUT/'MANIFEST.json']:z.write(p,'v26/'+str(p.relative_to(OUT)))
 with ZipFile(kit) as z:
  assert z.testzip() is None
  for row in manifest['files']:
   data=z.read('v26/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
 (OUT/'reports/package.json').write_text(json.dumps(dict(passed=True,zip_sha256=sha(kit),entries=len(manifest['files'])+1,preserved_archives=len(preserved),physical_acceptance=False),indent=2)+'\n');print('Package PASS',len(manifest['files'])+1,'entries;',len(preserved),'preserved archives')
if __name__=='__main__':main()
