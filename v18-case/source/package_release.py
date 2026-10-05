"""Pin and assemble the complete first-print kit, retaining source dependencies."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
REPO=Path(__file__).resolve().parents[2];OUT=REPO/'v18-case'
def sha(data):return hashlib.sha256(data).hexdigest()
def eligible(p):return p.is_file() and '__pycache__' not in p.parts and '.DS_Store' not in p.parts

def main():
 files=[p for p in OUT.rglob('*') if eligible(p) and 'release' not in p.relative_to(OUT).parts and p.name!='PACKAGE-MANIFEST.json']
 entries=[{'path':p.relative_to(REPO).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(files)]
 manifest=OUT/'PACKAGE-MANIFEST.json'
 manifest.write_text(json.dumps({'version':'v18','kind':'complete_case_first_print','physical_acceptance':False,'units':'mm','files':entries},indent=2)+'\n')
 lock_path=REPO/'docs/V18-FREEZE.json';lock=json.loads(lock_path.read_text())
 lock['integrated_case_manifest']={'path':manifest.relative_to(REPO).as_posix(),'bytes':manifest.stat().st_size,'sha256':sha(manifest.read_bytes())}
 lock_path.write_text(json.dumps(lock,indent=2)+'\n')
 dependencies=[REPO/e['path'] for e in lock['files']]
 dependencies += list((REPO/'v17-four-leaf/source').glob('*.py'))
 dependencies += [REPO/'v17-four-leaf/requirements.txt',REPO/'v17-four-leaf/README.md']
 dependencies += [REPO/'pieces'/n for n in ['tak_pieces.py','cat-flat.stl','witch-flat.stl','cat-capstone.stl','witch-capstone.stl']]
 dependencies += [REPO/n for n in ['README.md','AGENTS.md','CODEX.md','scripts/verify_v18_freeze.py','docs/TAK_PROJECT_BRIEF.md','docs/V18_FINAL.md','docs/V18_CHECKPOINT.md','docs/V18-FREEZE.json']]
 payload=sorted(set(files+[manifest]+dependencies));dest=OUT/'release/tak-v18-complete-case-CC2-PLA.zip';dest.parent.mkdir(exist_ok=True)
 with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=9) as kit:
  for p in payload:
   assert eligible(p),p
   kit.write(p,p.relative_to(REPO).as_posix())
 with ZipFile(dest) as kit:
  assert kit.testzip() is None
  assert set(kit.namelist())=={p.relative_to(REPO).as_posix() for p in payload}
  for p in payload:assert sha(kit.read(p.relative_to(REPO).as_posix()))==sha(p.read_bytes()),p
  for e in entries:assert sha(kit.read(e['path']))==e['sha256'],e['path']
 print(f'Complete v18 kit PASS: {len(payload)} files; manifest hashes, ZIP CRC and payload readback; {dest.stat().st_size} bytes.')
if __name__=='__main__':main()
