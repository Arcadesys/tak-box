"""Current inlaid V24 receipt; reuse only byte-verified mechanical evidence."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 old=read(OUT/'reports/historical-identity-provenance.json')
 original=old['source_and_output_sha256']
 # Exact retained mechanical exports, profiles, trials, source and reports.
 selected=[n for n in original if n.startswith(('models/','profiles/','FIT-CHECK/','TRAY-FIT/','source/vendor/'))]
 selected += ['source/case.py','source/flat_capstones.py','source/loaded_pieces.py']
 selected += ['reports/'+n+'.json' for n in ('hardware','supports','trays','pin-toolpaths','pip-hinges','fit-check','tray-trial','identity')]
 selected += [f'PRINT/{n}-CC2-PLA.3mf' for n in ('01-print-in-place-bases','03-removable-player-trays','04-flat-capstones-hook-and-collar')]
 selected += [f'plates/{n}.3mf' for n in ('01-print-in-place-bases','03-removable-player-trays','04-flat-capstones-hook-and-collar')]
 for n in selected:assert sha(OUT/n)==original[n],n
 (OUT/'reports/unchanged-mechanics.json').write_text(json.dumps({'pass':True,'baseline_commit':'b766181','baseline_zip_sha256':'5d48e11d789e2d2e1de48067df9993958c19a91a95c3c81998b7d06d61d66a9d','files_sha256':{n:original[n] for n in sorted(set(selected))},'note':'Monolithic board exports are retained mechanical references. Actual print/preview components are board-inlays/models. Historical identity and groove-only field receipts are not current board validation.'},indent=2)+'\n')
 checks={}
 for name in ('geometry','colour-layers','hardware-interfaces'):
  d=read(OUT/'board-inlays/reports'/f'{name}.json')
  assert d['checks'] and all(c['pass'] for c in d['checks']),name
  checks[name]=len(d['checks'])
 hardware=read(OUT/'board-inlays/reports/hardware-interfaces.json')
 for path,want in hardware['sources_sha256'].items():assert sha(OUT.parent/path)==want,path
 geometry=read(OUT/'board-inlays/reports/geometry.json')
 for path,want in geometry['sources_sha256'].items():assert sha(OUT.parent/path)==want,path
 slices=read(OUT/'board-inlays/reports/slicing.json')
 for n,want in slices['profiles_sha256'].items():assert sha(OUT/'board-inlays/profiles'/n)==want,n
 for stem,row in slices['plates'].items():
  assert row['readback_passed'] and row['input_sha256']==sha(OUT/'board-inlays/plates'/(stem+'.3mf'))
  assert row['output_sha256']==sha(OUT/'board-inlays/PRINT'/(stem+'-CC2.3mf'))
 all_slices=read(OUT/'reports/slicing.json')
 for stem,row in all_slices['plates'].items():
  assert row['passed'] and row['project_sha256']==sha(OUT/'PRINT'/row['project'])
  assert row['input_sha256']==sha(OUT/'plates'/(stem+'.3mf'))
 assert sha(OUT/'PRINT/02-sliding-board-tops-CC2-PLA.3mf')==slices['plates']['02-boards-black-white-silk']['output_sha256']
 assert sha(OUT/'INLAY-FIT/four-colour-inlay-trial-CC2-PLA.3mf')==slices['plates']['00-inlay-trial-black-white-silk']['output_sha256']
 directories=['source','profiles','models','PRINT','plates','FIT-CHECK','TRAY-FIT','INLAY-FIT','board-inlays','previews','reports']
 files=[p for d in directories for p in (OUT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.slicer-work' not in p.parts and p.name!='provenance.json']
 report={'version':'V24','status':'four-colour integration digitally verified; actual silk profiles and reslice required',
  'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=OUT,text=True).strip(),
  'environment':{'python':sys.version,'cadquery':cq.__version__,'platform':platform.platform(),'slicer':slices['slicer_version']},
  'new_checks':checks,'reused_mechanical_evidence':'reports/unchanged-mechanics.json',
  'historical_identity_only':'reports/historical-identity-provenance.json',
  'slices':{'full_build':4,'small_trials':3,'full_seconds':all_slices['total_estimated_seconds'],'full_grams':all_slices['total_estimated_grams'],'silk_profile_final':False},
  'closed_envelope_mm':[102.5,200,35],'field_mm':[180,180],'pitch_mm':36,'inlay_depth_mm':.6,
  'material_slots':{'1':'Black PLA body','2':'White PLA grid and stars','3':'Silk accent 1 placeholder (gold preview)','4':'Silk accent 2 placeholder (purple preview)'},
  'physical_acceptance':False,'printer_started':False,
  'source_and_output_sha256':{str(p.relative_to(OUT)):sha(p) for p in sorted(files)}}
 (OUT/'reports/provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Current V24 provenance PASS',checks,report['slices'])
if __name__=='__main__':main()
