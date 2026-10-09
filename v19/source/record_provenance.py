"""Verify current receipts and record source/dependency provenance for packaging."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 reports={n:json.loads((OUT/'reports'/f'{n}.json').read_text()) for n in ['geometry','field','hardware','plates','slicing','pin-toolpaths','layer-inspection']}
 checks=[]
 for n in ['geometry','field','hardware','plates','pin-toolpaths']:
  rows=reports[n]['checks'];assert rows and all(x['pass'] for x in rows),n
  checks.append({'report':n+'.json','checks':len(rows),'pass':True})
 for name in ['case.py','build_case.py']:
  assert reports['geometry']['source_sha256'][name]==sha(OUT/'source'/name),name
 slicing=reports['slicing'];assert len(slicing['plates'])==5
 assert slicing['profiles_sha256']=={p.name:sha(p) for p in (OUT/'profiles').glob('*.json')}
 for name,row in slicing['plates'].items():
  assert row['passed'] and row['input_sha256']==sha(OUT/'plates'/f'{name}.3mf')
  assert row['project_sha256']==sha(OUT/'PRINT'/row['project'])
  assert row['gcode_sha256']==sha(OUT/'.slicer-work'/f'{name}.gcode')
  assert reports['layer-inspection'][name]['visual_review']=='reviewed',name
  for pin in reports['pin-toolpaths']['checks']:
   if pin['name'].startswith(name+'/'):assert pin['gcode_sha256']==row['gcode_sha256']
 paths=list((OUT/'source').glob('*.py'))+[OUT/'requirements.txt']
 paths += list((OUT/'source/vendor').rglob('*.py'))
 for p in paths:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
 result={'base_revision':'1e8944b646a6bf7190b0d1752ce53c1ed5ae7132','recovery_base_revision':'2589129101d6f63533b425bff4855ec84a735904','python_environment':'.slicer-work/cad-venv (Python 3.12.13; requirements.txt)','source_and_dependency_sha256':{p.relative_to(OUT).as_posix():sha(p) for p in paths},'cad_validation_snapshot_defining_sources_match':True,'checks':checks,'five_project_input_profile_hashes_match':True,'selected_layer_visual_reviews_recorded':True,'filament_toolpath_scope':reports['pin-toolpaths']['scope'],'closure':'Side swivel hook over a headed printed pin; friction set by bonded pivot collar. No detent/force/physical retention qualification.','printer_started':False,'physical_acceptance':False,'clasp_trial':'Earlier recessed clasp printed per user; new hook untested.','earlier_filament_test':'User reports 1.75 mm PLA held in place; exact component revision, load and cycle count unknown.'}
 (OUT/'reports/provenance.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Current sources, five input/project/profile/Gcode hashes, report checks and syntax PASS.')
if __name__=='__main__':main()
