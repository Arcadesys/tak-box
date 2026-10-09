"""Manifest, one-root print kit, hashes/ZIP/link/readback audit; no publishing."""
from pathlib import Path
import hashlib,json,re,zipfile,ast
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 geo=json.loads((OUT/'reports/geometry.json').read_text());sli=json.loads((OUT/'reports/slicing.json').read_text())
 assert all(x['pass_'] for x in geo['checks']) and sli['passed']
 assert sha(OUT/'plates/01-V25-hinge-lip-coupons.3mf')==sli['input_sha256']
 assert sha(OUT/'PRINT/01-V25-hinge-lip-coupons-CC2-PLA.3mf')==sli['project_sha256']
 for p,h in sli['profiles_sha256'].items():assert sha(OUT/'profiles'/p)==h
 assert sha(OUT/'reference/v24/source/case.py')==geo['source_case_sha256']
 files=sorted(p for p in OUT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.slicer-work','__pycache__')) and p.name not in ('V25-COUPON-KIT.zip','MANIFEST.json','PACKAGE-AUDIT.json') and not p.name.startswith('.'))
 for p in files:
  if p.suffix=='.py':ast.parse(p.read_text())
  if p.suffix=='.json':json.loads(p.read_text())
  if p.suffix=='.3mf':
   with zipfile.ZipFile(p) as z:assert z.testzip() is None
  if p.name in ('START-HERE.md','ENGINEERING.md'):
   for s in re.findall(r'\]\(([^)]+)\)',p.read_text()):
    if not s.startswith(('https:','http:','#')):assert (p.parent/s).exists(),s
 manifest=dict(version='V25 filament hinge and rounded board coupons',source_revision=geo['source_revision'],units='mm',geometry_checks=len(geo['checks']),named_printed_parts=len(sli['mesh_readback']),estimated_seconds=int(sli['plate_metadata']['prediction']),estimated_grams=float(sli['plate_metadata']['weight']),physical_acceptance=False,printer_started=False,files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
 (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 dest=OUT/'V25-COUPON-KIT.zip'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files+[OUT/'MANIFEST.json']:z.write(p,Path('v25')/p.relative_to(OUT))
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None and {Path(p).parts[0] for p in z.namelist()}=={'v25'}
  got=json.loads(z.read('v25/MANIFEST.json'))
  for row in got['files']:
   data=z.read('v25/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
  assert len([p for p in z.namelist() if p.startswith('v25/PRINT/')])==1
 audit=dict(passed=True,files=len(files)+1,root='v25',zip_bytes=dest.stat().st_size,zip_sha256=sha(dest),geometry_checks=len(geo['checks']),named_printed_parts=len(sli['mesh_readback']),physical_acceptance=False,printer_started=False)
 (OUT/'reports/PACKAGE-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
