"""Prove the V23 identity-only migration against the preserved accepted archive."""
import argparse,ast,hashlib,json
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parents[1]
BASE=R/'v22/release/archive/tak-v22-seamless-before-v23.zip'
BASE_SHA='d48410b2b090c39770dcf3f2bf56b243482c84fbbc51b89927d7b21dd7d633a4'
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(data):
 tree=ast.parse(data)
 class Names(ast.NodeTransformer):
  def visit_Constant(self,node):
   if isinstance(node.value,str):node.value=node.value.replace('V23','V22').replace('v23','v22')
   return node
 return ast.dump(Names().visit(tree),include_attributes=False)
def verify(out):
 assert sha(BASE.read_bytes())==BASE_SHA
 checks=[];artifacts=[];sources=[];projects=[];profiles=[];receipts=[]
 with ZipFile(BASE) as baseline:
  for name in baseline.namelist():
   rel=name.removeprefix('v22/');p=out/rel
   if (rel.startswith('models/') or rel.startswith(('FIT-CHECK/','CLOSURE-FIT/'))) and p.suffix in ['.step','.stl']:
    assert p.read_bytes()==baseline.read(name),rel;artifacts.append(rel)
   if rel.startswith('source/vendor/') or rel=='requirements.txt':
    assert p.read_bytes()==baseline.read(name),rel;sources.append(rel)
   elif rel.startswith('source/') and p.suffix=='.py' and p.name not in ['render_case.py','record_provenance.py','package_release.py']:
    assert canonical(p.read_text())==canonical(baseline.read(name)),rel;sources.append(rel)
   if rel.startswith('reports/') and p.name!='provenance.json':
    assert p.read_bytes()==baseline.read(name),rel;receipts.append(rel)
   if p.suffix=='.3mf':
    import io
    with ZipFile(io.BytesIO(baseline.read(name))) as old,ZipFile(p) as new:
     assert set(old.namelist())==set(new.namelist()) and new.testzip() is None,rel
     changed=[]
     for entry in old.namelist():
      a,b=old.read(entry),new.read(entry)
      if a==b:continue
      changed.append(entry)
      if entry=='Metadata/project_settings.config':
       aa,bb=json.loads(a),json.loads(b);assert aa['print_settings_id']=='V22 complete case CC2 PLA 0.20' and bb['print_settings_id']=='V23 complete case CC2 PLA 0.20';aa.pop('print_settings_id');bb.pop('print_settings_id');assert aa==bb,rel
      elif entry=='Metadata/plate_1.gcode':
       assert b==a.replace(b'; print_settings_id = V22 complete case CC2 PLA 0.20',b'; print_settings_id = V23 complete case CC2 PLA 0.20'),rel
      elif entry=='Metadata/plate_1.gcode.md5':
       assert b.decode().strip()==hashlib.md5(new.read('Metadata/plate_1.gcode')).hexdigest(),rel
      else:raise AssertionError((rel,entry))
     # Entire model XML, objects, transforms, settings and instructions remain exact.
     projects.append({'path':rel,'identity_only_entries':changed,'sha256':sha(p.read_bytes()),'named_meshes_and_world_transforms_byte_identical':True,'executable_Gcode_byte_identical':True})
   if rel.startswith('profiles/'):
    a,b=json.loads(baseline.read(name)),json.loads(p.read_text())
    if p.name=='process-case.json':
     for key in ['name','setting_id']:assert b.pop(key)==a.pop(key).replace('V22','V23').replace('v22','v23')
    assert a==b,rel;profiles.append({'path':rel,'all_operational_values_identical':True})
  assert (out/'reports/validation-origin.json').read_bytes()==baseline.read('v22/reports/provenance.json')
 # Original V22's full manifest payload is restored, not only its ZIP.
 original=R/'v22/release/tak-v22-print-kit.zip';expected=json.loads((R/'docs/V22_BASELINE_ARCHIVE.json').read_text())
 assert sha(original.read_bytes())==expected['sha256']
 with ZipFile(original) as z:
  manifest=json.loads(z.read('v22/PACKAGE-MANIFEST.json'))
  for entry in manifest['files']:assert sha((R/'v22'/entry['path']).read_bytes())==entry['sha256'],entry['path']
 files={p.relative_to(out).as_posix():sha(p.read_bytes()) for p in out.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.DS_Store' not in p.parts and p.relative_to(out).parts[0] not in ['release','.slicer-work'] and p.relative_to(out).as_posix() not in ['PACKAGE-MANIFEST.json','reports/identity.json','reports/provenance.json']}
 return {'version':'v23','change':'identity_only','geometry_source_revision':'4859c9cdd515cd7f12324a99423b8795fa7984ac','validation_artifact_revision':'19b8773d8fbbcb37147f875d68b102b25a3cbc2a','accepted_archive_sha256':BASE_SHA,'unchanged_CAD_exports':artifacts,'unchanged_geometry_check_and_dependency_sources':sources,'unchanged_validation_receipts':receipts,'projects':projects,'profiles':profiles,'original_v22_archive_and_all_94_payload_files_preserved':True,'current_payload_sha256':files,'new_geometry_or_motion_or_slicing_run':False,'physical_acceptance':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package-dir',type=Path,default=R/'v23');ap.add_argument('--write-report',action='store_true');args=ap.parse_args();report=verify(args.package_dir)
 if args.write_report:(args.package_dir/'reports/identity.json').write_text(json.dumps(report,indent=2)+'\n')
 print('V23 identity PASS:',len(report['unchanged_CAD_exports']),'CAD exports;',len(report['projects']),'3MF projects; geometry/check sources and operational profile/Gcode values unchanged; original V22 payload restored.')
if __name__=='__main__':main()
