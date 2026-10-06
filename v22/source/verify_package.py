"""Verify the extracted v22 kit with Python's standard library."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parents[1]
def main():
 manifest=json.loads((OUT/'PACKAGE-MANIFEST.json').read_text());assert manifest['version']=='v22'
 for entry in manifest['files']:
  p=OUT/entry['path'];data=p.read_bytes()
  assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
  if p.suffix=='.py':ast.parse(data,filename=str(p))
 assert len(list((OUT/'PRINT').glob('*.3mf')))==3
 print(f"V22 package PASS: {len(manifest['files'])} payload hashes and Python syntax; three print projects. Physical acceptance remains pending.")
if __name__=='__main__':main()
