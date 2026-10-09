"""Package only the current R2 kit, then independently inspect its ZIP payload."""
from pathlib import Path
import ast,hashlib,json,re,tempfile,zipfile
OUT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 provenance=json.loads((OUT/'reports/provenance.json').read_text())
 for name,h in provenance['source_and_output_sha256'].items():assert sha((OUT/name).read_bytes())==h,name
 dirs={'source','profiles','models','PRINT','plates','FIT-CHECK','TRAY-FIT','previews','reports'}
 files=sorted(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (p.relative_to(OUT).parts[0] in dirs or p.name in ['START-HERE.md','BUILD-PROVENANCE.md','ACCEPTANCE.md','requirements.txt']))
 manifest={'version':'V23 R2','units':'mm','physical_acceptance':False,'files':[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]}
 mp=OUT/'PACKAGE-MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');files.append(mp)
 dest=OUT/'release/tak-v23-r2-print-kit.zip';dest.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,Path('v23-r2')/p.relative_to(OUT))
 with tempfile.TemporaryDirectory(prefix='tak-v23-r2-audit-') as temp:
  with zipfile.ZipFile(dest) as z:
   assert z.testzip() is None and {Path(n).parts[0] for n in z.namelist()}=={'v23-r2'}
   assert not any('..' in Path(n).parts or Path(n).is_absolute() for n in z.namelist())
   z.extractall(temp)
  root=Path(temp)/'v23-r2';got=json.loads((root/'PACKAGE-MANIFEST.json').read_text());links=0
  for row in got['files']:
   p=root/row['path'];data=p.read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['path']
   if p.suffix=='.py':ast.parse(data)
   if p.suffix=='.json':json.loads(data)
   if p.suffix=='.3mf':
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
   if p.suffix=='.md':
    for link in re.findall(r'\]\(([^)]+)\)',data.decode()):
     if not link.startswith(('http:','https:','#')):assert (p.parent/link.split('#')[0]).exists(),link;links+=1
  assert len(list((root/'PRINT').glob('*.3mf')))==4
  assert len(list((root/'FIT-CHECK').glob('*CC2-PLA.3mf')))==1 and len(list((root/'TRAY-FIT').glob('*CC2-PLA.3mf')))==1
 audit={'pass':True,'payload_files':len(got['files']),'full_projects':4,'small_trial_projects':2,'local_links':links,'zip_sha256':sha(dest.read_bytes()),'zip_bytes':dest.stat().st_size,'physical_acceptance':False}
 # Outside the archive to avoid a circular ZIP hash.
 (OUT/'release/AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
