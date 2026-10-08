"""Self-contained strength kit with shared CAD sources; preserve the earlier kit."""
from pathlib import Path
import ast,hashlib,json,re,zipfile
OUT=Path(__file__).resolve().parents[1];V25=OUT.parent
ZIP=OUT/'V25-PIP-FIXED-STORAGE.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload():
 own=[p for p in OUT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.slicer-work','__pycache__')) and p.name not in ('V25-PIP-FIXED-STORAGE.zip','MANIFEST.json','PACKAGE-AUDIT.json','reproduction.json','reproduction-build.log','reproduction-run.log') and not p.name.startswith('.')]
 common=[V25/'source/build.py',V25/'requirements.txt']
 refs=[p for p in (V25/'reference/v24/source').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 return sorted(set(own+common+refs))
def main():
 geo=json.loads((OUT/'reports/geometry.json').read_text());sli=json.loads((OUT/'reports/slicing.json').read_text())
 assert geo['passed'] and all(r['pass_'] for r in geo['checks']) and sli['passed']
 assert sha(OUT/'plates/01-V25-PIP-fixed-storage.3mf')==sli['input_sha256']
 assert sha(OUT/'PRINT/01-V25-PIP-fixed-storage-CC2-PLA.3mf')==sli['project_sha256']
 for n,h in sli['profiles_sha256'].items():assert sha(OUT/'profiles'/n)==h
 for n,h in geo['source_sha256'].items():assert sha(V25/n)==h
 for n,h in geo['reference_board_sha256'].items():assert sha(OUT/'reference/board-inlays'/n)==h
 trial=json.loads((OUT/'reports/trial-geometry.json').read_text());ts=json.loads((OUT/'reports/trial-slicing.json').read_text())
 assert trial['passed'] and ts['passed'] and all(q['pass_'] for q in trial['checks'])
 assert sha(OUT/'source/trial.py')==trial['source_sha256']
 assert sha(OUT/'plates/02-V25-PIP-hinge-trial.3mf')==ts['input_sha256']
 assert sha(OUT/'PRINT/02-V25-PIP-hinge-trial-CC2-PLA.3mf')==ts['project_sha256']
 for n,h in ts['profiles_sha256'].items():assert sha(OUT/'profiles'/n)==h
 for report in (sli,ts):
  for n,h in report['source_sha256'].items():
   p=OUT/'source'/n if n!='slice_case.py' else V25/'reference/v24/source'/n
   assert sha(p)==h
 files=payload()
 for p in files:
  if p.suffix=='.py':ast.parse(p.read_text())
  if p.suffix=='.json':json.loads(p.read_text())
  if p.suffix=='.3mf':
   with zipfile.ZipFile(p) as z:assert z.testzip() is None
  if p.suffix=='.md':
   for n in re.findall(r'\]\(([^)]+)\)',p.read_text()):
    if not n.startswith(('https:','http:','#')):assert (p.parent/n).exists(),n
 manifest=dict(version='V25 PIP fixed-storage bodies',reference_revision=geo['reference_revision'],units='mm',geometry_checks=len(geo['checks']),printed_parts=2,supplemental_trial_parts=2,trial_geometry_checks=len(trial['checks']),estimated_seconds=int(sli['plate_metadata']['prediction']),estimated_grams=float(sli['plate_metadata']['weight']),physical_acceptance=False,printer_started=False,files=[dict(path=str(p.relative_to(V25)),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
 mf=OUT/'MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files+[mf]:z.write(p,Path('v25')/p.relative_to(V25))
  z.writestr('v25/START-HERE.md','# V25 PIP fixed storage\n\nOpen [the fixed-storage guide](PIP-FIXED-STORAGE/START-HERE.md).\n')
 with zipfile.ZipFile(ZIP) as z:
  assert z.testzip() is None and {Path(n).parts[0] for n in z.namelist()}=={'v25'}
  for row in manifest['files']:
   data=z.read('v25/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
  assert len([n for n in z.namelist() if '/PRINT/' in n])==2
 audit=dict(passed=True,entries=len(files)+2,zip_sha256=sha(ZIP),zip_bytes=ZIP.stat().st_size,geometry_checks=len(geo['checks']),printed_parts=2,physical_acceptance=False,printer_started=False)
 (OUT/'reports/PACKAGE-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
