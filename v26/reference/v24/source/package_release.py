"""Publish and audit the same simple layout in the V24 folder and its ZIP."""
from pathlib import Path
import ast,hashlib,json,re,tempfile,zipfile
from delivery import ROOT,REFERENCE,FULL,TRIALS,sha
from record_provenance import main as record,payload_files

def main():
 provenance=record()
 for name,h in provenance['source_and_output_sha256'].items():assert sha(ROOT/name)==h,name
 files=payload_files()
 manifest={'version':'V24','units':'mm','physical_acceptance':False,'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
 mp=REFERENCE/'PACKAGE-MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');files.append(mp)
 dest=ROOT/'V24-PRINT-KIT.zip'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,Path('v24')/p.relative_to(ROOT))
 with tempfile.TemporaryDirectory(prefix='tak-v24-organized-audit-') as temp:
  with zipfile.ZipFile(dest) as z:
   assert z.testzip() is None and {Path(n).parts[0] for n in z.namelist()}=={'v24'}
   assert not any('..' in Path(n).parts or Path(n).is_absolute() for n in z.namelist())
   z.extractall(temp)
  root=Path(temp)/'v24';got=json.loads((root/'REFERENCE/PACKAGE-MANIFEST.json').read_text());links=0
  for row in got['files']:
   p=root/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
   if p.suffix=='.py':ast.parse(p.read_text())
   if p.suffix=='.json':json.loads(p.read_text())
   if p.suffix=='.3mf':
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
   if p.suffix=='.md':
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
     if not link.startswith(('http:','https:','#')):assert (p.parent/link.split('#')[0]).exists(),(p,link);links+=1
  assert {p.name for p in root.iterdir()}=={'START-HERE.md','FULL-PRINT','SMALL-TRIALS','PREVIEW.png','REFERENCE'}
  assert {p.name for p in (root/'FULL-PRINT').iterdir()}==set(FULL)
  assert {p.name for p in (root/'SMALL-TRIALS').iterdir()}==set(TRIALS)
  assert not (root/'REFERENCE/HISTORY').exists()
  assert not list(root.rglob('*.zip'))
  # Extracted output paths must be the same shallow paths as the working kit.
  for folder,mapping in [('FULL-PRINT',FULL),('SMALL-TRIALS',TRIALS)]:
   for name in mapping:assert sha(root/folder/name)==sha(ROOT/folder/name)
 audit={'pass':True,'payload_files':len(got['files']),'full_projects':4,'small_trial_projects':3,'local_links':links,
  'top_level':['START-HERE.md','FULL-PRINT','SMALL-TRIALS','PREVIEW.png','REFERENCE'],'nested_archives':0,
  'zip_sha256':sha(dest),'zip_bytes':dest.stat().st_size,'physical_acceptance':False}
 (REFERENCE/'reports/PACKAGE-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
