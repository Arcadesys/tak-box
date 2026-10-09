"""Build one self-contained v19 folder, without archived versions or nested ZIPs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
OUT=Path(__file__).resolve().parents[1]
DIRS={'PRINT','plates','models','source','profiles','previews','reports'}
FILES={'START-HERE.md','BUILD-PROVENANCE.md','ACCEPTANCE.md','requirements.txt'}
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 files=sorted(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.DS_Store' not in p.parts and (p.relative_to(OUT).parts[0] in DIRS or p.relative_to(OUT).as_posix() in FILES))
 assert len(list((OUT/'PRINT').glob('*.3mf')))==5
 assert all(p.name.endswith('-CC2-PLA.3mf') for p in (OUT/'PRINT').iterdir())
 assert all(p.suffix!='.zip' for p in files)
 entries=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]
 manifest=OUT/'PACKAGE-MANIFEST.json'
 manifest.write_text(json.dumps({'version':'v19','kind':'complete_case_first_print','units':'mm','physical_acceptance':False,'files':entries},indent=2)+'\n')
 dest=OUT/'release/tak-v19-print-kit.zip';dest.parent.mkdir(exist_ok=True)
 with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for p in files+[manifest]:z.write(p,'v19/'+p.relative_to(OUT).as_posix())
 with ZipFile(dest) as z:
  assert z.testzip() is None
  assert {n.split('/')[0] for n in z.namelist()}=={'v19'}
  assert not any(part.startswith(('v17','v18')) for n in z.namelist() for part in n.split('/'))
  assert len([n for n in z.namelist() if n.startswith('v19/PRINT/')])==5
  for e in entries:assert sha(z.read('v19/'+e['path']))==e['sha256'],e['path']
 print(f'V19 kit PASS: one v19 folder, five PRINT projects, {len(files)+1} files, ZIP CRC and all payload hashes verified; {dest.stat().st_size} bytes.')
if __name__=='__main__':main()
