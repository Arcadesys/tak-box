"""Fresh extraction and identity-only proof for the V23 release."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,subprocess,sys,tempfile
from verify_v23_identity import verify
R=Path(__file__).resolve().parents[1];archive=R/'v23/release/tak-v23-print-kit.zip'
with tempfile.TemporaryDirectory(prefix='tak-v23-audit-') as td:
 root=Path(td).resolve()
 with ZipFile(archive) as z:
  assert z.testzip() is None and {n.split('/')[0] for n in z.namelist()}=={'v23'}
  assert not any(n.endswith('.zip') for n in z.namelist())
  z.extractall(root)
 kit=root/'v23'
 subprocess.run([sys.executable,str(kit/'source/verify_package.py')],check=True,cwd=root)
 links=[]
 for p in kit.rglob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith('#'):continue
   dest=(p.parent/target.split('#')[0]).resolve();assert dest.is_relative_to(kit) and dest.exists(),(p,target)
   links.append(str(p.relative_to(kit))+':'+target)
 proof=verify(kit)
 manifest=json.loads((kit/'PACKAGE-MANIFEST.json').read_text());provenance=json.loads((kit/'reports/provenance.json').read_text())
 receipt={'version':'v23','archive':str(archive.relative_to(R)),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'single_root':'v23','print_projects':len(list((kit/'PRINT').glob('*.3mf'))),'payload_files':len(manifest['files']),'fresh_payload_hashes_and_syntax':True,'relative_markdown_links_checked':len(links),'CAD_exports_byte_identical_to_accepted_seamless':len(proof['unchanged_CAD_exports']),'three_mf_projects_meshes_transforms_and_operational_values_equivalent':len(proof['projects']),'original_v22_archive_and_payload_preserved':True,'source_revision':provenance['source_revision'],'geometry_source_revision':proof['geometry_source_revision'],'prior_geometry_motion_and_slices_reused':True,'physical_acceptance':False,'printer_started':False}
 (R/'docs/V23_PACKAGE_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
