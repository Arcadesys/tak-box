"""Verify current receipts and record source/dependency provenance for packaging."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
from importlib.metadata import version
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 reports={n:json.loads((OUT/'reports'/f'{n}.json').read_text()) for n in ['geometry','field','hardware','plates','slicing','pin-toolpaths','pip-hinges','flat-capstones','layer-inspection']}
 checks=[]
 for n in ['geometry','field','hardware','plates','pin-toolpaths','pip-hinges','flat-capstones']:
  rows=reports[n]['checks'];assert rows and all(x['pass'] for x in rows),n
  checks.append({'report':n+'.json','checks':len(rows),'pass':True})
 for name in ['case.py','build_case.py','flat_capstones.py']:
  assert reports['geometry']['source_sha256'][name]==sha(OUT/'source'/name),name
 slicing=reports['slicing'];assert len(slicing['plates'])==3
 assert slicing['profiles_sha256']=={p.name:sha(p) for p in (OUT/'profiles').glob('*.json')}
 for name,row in slicing['plates'].items():
  assert row['passed'] and row['input_sha256']==sha(OUT/'plates'/f'{name}.3mf')
  assert row['project_sha256']==sha(OUT/'PRINT'/row['project'])
  assert row['gcode_sha256']==sha(OUT/'.slicer-work'/f'{name}.gcode')
  assert reports['layer-inspection'][name]['visual_review']=='reviewed',name
  for pin in reports['pin-toolpaths']['checks']:
   if pin['name'].startswith(name+'/'):assert pin['gcode_sha256']==row['gcode_sha256']
 fit=json.loads((OUT/'reports/fit-check.json').read_text())
 assert all(x['pass'] for x in fit['checks'])
 for name,digest in fit['source_STEP_sha256'].items():assert sha(OUT/'models'/name)==digest
 frow=fit['slicing']['plates']['captive-hinge-fit-check']
 assert sha(OUT/'FIT-CHECK/captive-hinge-fit-check-CC2-PLA.3mf')==frow['project_sha256']
 assert sha(OUT/'FIT-CHECK/captive-hinge-fit-check-geometry.3mf')==frow['input_sha256']
 assert all(x['visual_review']=='reviewed' for x in json.loads((OUT/'reports/fit-check-layers.json').read_text()).values())
 for check in reports['pip-hinges']['checks']:
  if 'gcode_sha256' in check:
   expected=frow['gcode_sha256'] if check['name'].startswith('trial/') else slicing['plates']['01-print-in-place-bases']['gcode_sha256']
   assert check['gcode_sha256']==expected,check['name']
 checks.append({'report':'fit-check.json','checks':len(fit['checks']),'pass':True})
 paths=list((OUT/'source').glob('*.py'))+[OUT/'requirements.txt']
 paths += list((OUT/'source/vendor').rglob('*.py'))
 for p in paths:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
 source_revision=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True).stdout.strip() or 'unavailable outside repository; use source hashes'
 result={'source_revision':source_revision,'runtime_python':sys.version,'installed_dependencies':{n:version(n) for n in ['cadquery','cadquery-ocp','trimesh','numpy','scipy','vtk','matplotlib']},'base_revision':'0fd6806','recovery_base_revision':'2589129101d6f63533b425bff4855ec84a735904','python_environment':'.slicer-work/cad-venv (Python 3.12.13; requirements.txt)','source_and_dependency_sha256':{p.relative_to(OUT).as_posix():sha(p) for p in paths},'cad_validation_snapshot_defining_sources_match':True,'checks':checks,'three_project_input_profile_hashes_match':True,'selected_layer_visual_reviews_recorded':True,'capstone_layout':'One-piece flat Cat/Witch capstones in shallow bays under the sliding boards; rear compartment and hatch removed','captive_hinge_toolpath_scope':reports['pip-hinges']['scope'],'filament_toolpath_scope':reports['pin-toolpaths']['scope'],'closure':'Side swivel hook over a headed printed pin; friction set by bonded pivot collar. No detent/force/physical retention qualification.','printer_started':False,'physical_acceptance':False,'clasp_trial':'Earlier recessed clasp printed per user; new hook untested.','earlier_filament_test':'User reports 1.75 mm PLA held in place; exact component revision, load and cycle count unknown.'}
 (OUT/'reports/provenance.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Current sources, three input/project/profile/Gcode hashes, report checks and syntax PASS.')
if __name__=='__main__':main()
