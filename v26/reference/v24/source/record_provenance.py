"""Prove organization-only changes against the accepted colour-inlay delivery."""
from pathlib import Path
from zipfile import ZipFile
import ast,hashlib,json,platform,subprocess,sys,xml.etree.ElementTree as ET
from delivery import ROOT,REFERENCE,FULL,TRIALS,publish,sha

def mapped(old):
 if old.startswith('release/'):return REFERENCE/'HISTORY'/old.removeprefix('release/')
 if old=='START-HERE.md':return REFERENCE/'ENGINEERING-GUIDE.md'
 if old=='PACKAGE-MANIFEST.json':return REFERENCE/'HISTORY/accepted-colour-PACKAGE-MANIFEST.json'
 if old=='reports/provenance.json':return REFERENCE/'reports/accepted-inlay-provenance.json'
 return REFERENCE/old

def normalized(text):
 # Only repository discovery paths changed in CAD/support sources.
 tree=ast.parse(text.replace("OUT.parent.parent/'v23", "OUT.parent/'v23"))
 for n in ast.walk(tree):
  if hasattr(n,'type_params') and not n.type_params:del n.type_params  # Python 3.9/3.12 AST parity.
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REPO' for t in n.targets):n.value=ast.Constant('REPOSITORY_ROOT')
 return hashlib.sha256(ast.dump(tree,include_attributes=False).encode()).hexdigest()

def payload_files():
 files=[]
 for p in ROOT.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(ROOT)
  if any(x in rel.parts for x in ('HISTORY','.slicer-work','__pycache__')) or p.name=='.DS_Store':continue
  if rel.parts[0] not in ('REFERENCE','FULL-PRINT','SMALL-TRIALS','START-HERE.md','PREVIEW.png'):continue
  if p.name in ('PACKAGE-MANIFEST.json','PACKAGE-AUDIT.json'):continue
  files.append(p)
 return sorted(files)

def main():
 rows=publish()
 baseline=json.loads((REFERENCE/'reports/layout-baseline.json').read_text())
 accepted=json.loads((REFERENCE/'reports/accepted-inlay-provenance.json').read_text())
 history=REFERENCE/'HISTORY/tak-v24-print-kit.zip'
 if history.exists():assert sha(history)==baseline['zip_sha256']
 # Every geometry, machine/material/process profile, print project, preview and
 # accepted evidence file is preserved byte-for-byte at its mapped location.
 preserved=[]
 for old,want in baseline['tracked_sha256'].items():
  if old.endswith('.py') or old.endswith('.md') or old=='PACKAGE-MANIFEST.json':continue
  path=mapped(old)
  if old.startswith('release/') and not history.exists():continue
  assert path.is_file() and sha(path)==want,old
  preserved.append(old)
 algorithms=[]
 for old,want in baseline['normalized_source_ast'].items():
  if old in ('source/record_provenance.py','source/package_release.py'):continue
  assert normalized(mapped(old).read_text())==want,old
  algorithms.append(old)
 # User extractions move into HISTORY without changing any contents.
 extraction_count=0
 for old,want in baseline['user_extractions_sha256'].items():
  path=mapped(old)
  if history.exists():assert path.exists() and sha(path)==want,old;extraction_count+=1
 # External historical archives are intentionally outside the downloadable kit.
 for source_name in ('geometry','hardware-interfaces','colour-layers'):
  report=json.loads((REFERENCE/'board-inlays/reports'/(source_name+'.json')).read_text())
  assert report['checks'] and all(x['pass'] for x in report['checks'])
 projects=[]
 ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
 for row in rows:
  path=ROOT/row['path'];old=row['accepted_build_output'].removeprefix('REFERENCE/')
  assert row['sha256']==baseline['tracked_sha256'][old]
  with ZipFile(path) as z:
   assert z.testzip() is None
   code_names=[n for n in z.namelist() if n.endswith('.gcode')];assert len(code_names)==1
   cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
   settings=json.loads(z.read('Metadata/project_settings.config'))
   mesh=ET.fromstring(z.read('3D/3dmodel.model'))
   colors=settings['filament_colour']
   if 'FOUR-COLOUR' in path.name:
    slots={int(p.get('value')) for p in cfg.findall(".//part/metadata[@key='extruder']")}
    assert slots=={1,2,3,4} and colors==['#111111','#FFFFFF','#D6A54C','#B887DD']
    assert len(mesh.find('m:build',ns))==(2 if row['path'].startswith('FULL-PRINT') else 1)
   projects.append({**row,'byte_identical_to_accepted':True,'filament_colours':colors,'gcode_sha256':hashlib.sha256(z.read(code_names[0])).hexdigest()})
 # Import/path smoke check; no solids regenerated and no slicer invoked.
 import case
 sys.path.insert(0,str(REFERENCE/'board-inlays/source'))
 import inlays
 assert case.OUT==REFERENCE and inlays.OUT==REFERENCE/'board-inlays'
 assert case.REPO==ROOT.parent and inlays.REPO==ROOT.parent
 for p in (REFERENCE/'source/vendor/body/folio.py',REFERENCE/'source/vendor/pieces/tak_pieces.py',REFERENCE/'board-inlays/source/vendor/artwork/tak_book.py'):
  assert p.is_file(),p
 for p in payload_files():
  if p.suffix=='.py':ast.parse(p.read_text())
 evidence={'pass':True,'accepted_revision':baseline['source_commit'],'accepted_zip_sha256':baseline['zip_sha256'],
  'preserved_binary_data_files':len(preserved),'unchanged_algorithm_sources':len(algorithms),'preserved_user_extraction_files':extraction_count,
  'projects':projects,'generator_paths_verified':True,'geometry_resliced_or_rebuilt':False,'physical_acceptance':False}
 (REFERENCE/'reports/organization.json').write_text(json.dumps(evidence,indent=2)+'\n')
 git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
 report={'version':'V24','status':'organized delivery; accepted print content unchanged','source_commit':git.stdout.strip() if git.returncode==0 else None,
  'accepted_inlay_revision':accepted['source_commit'],'accepted_checks_reused':accepted['new_checks'],
  'organization_evidence':'reports/organization.json','closed_envelope_mm':[102.5,200,35],'field_mm':[180,180],'pitch_mm':36,
  'material_slots':accepted['material_slots'],'slices':accepted['slices'],'physical_acceptance':False,'printer_started':False,
  'source_and_output_sha256':{str(p.relative_to(ROOT)):sha(p) for p in payload_files() if p!=REFERENCE/'reports/provenance.json'}}
 (REFERENCE/'reports/provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Organization provenance PASS:',len(projects),'identical sliced projects;',len(algorithms),'unchanged algorithm sources;',len(preserved),'preserved artifacts')
 return report
if __name__=='__main__':main()
