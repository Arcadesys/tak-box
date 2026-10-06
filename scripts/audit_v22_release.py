from pathlib import Path
from zipfile import ZipFile
import ast,hashlib,json,re,subprocess,sys,tempfile
import cadquery as cq
repo=Path(__file__).resolve().parents[1]
archive=repo/'v22/release/tak-v22-seamless-print-kit.zip'
with tempfile.TemporaryDirectory(prefix='tak-v22-audit-') as td:
 root=Path(td).resolve()
 with ZipFile(archive) as z:
  assert z.testzip() is None
  assert {n.split('/')[0] for n in z.namelist()}=={'v22'}
  assert all(not n.endswith('.zip') for n in z.namelist())
  z.extractall(root)
 kit=root/'v22';manifest=json.loads((kit/'PACKAGE-MANIFEST.json').read_text())
 subprocess.run([sys.executable,str(kit/'source/verify_package.py')],check=True,cwd=root)
 links=[]
 for p in kit.rglob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith('#'):continue
   dest=(p.parent/target.split('#')[0]).resolve()
   assert dest.is_relative_to(kit) and dest.exists(),(p,target)
   links.append(str(p.relative_to(kit))+':'+target)
 sys.path.insert(0,str(kit/'source'))
 import case,flat_capstones
 assert Path(case.__file__).resolve().is_relative_to(kit)
 shapes={'housing-left':case.housing('left'),'board-left':case.board('left'),'capstone-cat':flat_capstones.capstone('cat'),'capstone-witch':flat_capstones.capstone('witch')}
 checks=[]
 for name,s in shapes.items():
  exported=cq.importers.importStep(str(kit/'models'/f'{name}.step')).val()
  delta=abs(s.Volume()-exported.Volume())
  assert s.isValid() and len(s.Solids())==1 and delta<1e-5,(name,delta)
  checks.append({'part':name,'valid_single_solid':True,'volume_difference_mm3':delta})
 receipt={'archive':'v22/release/tak-v22-seamless-print-kit.zip','bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'payload_files':len(manifest['files']),'single_root':'v22','print_projects':len(list((kit/'PRINT').glob('*.3mf'))),'fresh_extraction_payload_hashes_and_syntax':True,'relative_markdown_links_checked':len(links),'standalone_CAD_rebuild':checks,'source_revision':json.loads((kit/'reports/provenance.json').read_text())['source_revision'],'command':'Repository CAD Python scripts/audit_v22_release.py; fresh temporary extraction, standard-library package verification, local Markdown links, standalone imported CAD reconstruction versus packaged STEP','physical_acceptance':False,'printer_started':False}
 (repo/'docs/V22_SEAMLESS_PACKAGE_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
