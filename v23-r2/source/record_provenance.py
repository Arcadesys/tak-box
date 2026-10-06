"""Require fresh R2 checks and record hashes before packaging a print candidate."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 reports={n:json.loads((OUT/'reports'/f'{n}.json').read_text()) for n in ['geometry','field','hardware','supports','trays','plates','pin-toolpaths','pip-hinges','fit-check','tray-trial']}
 counts={}
 for n,d in reports.items():
  assert d['checks'] and all(r['pass'] for r in d['checks']),n
  counts[n]=len(d['checks'])
 assert reports['geometry']['source_sha256']['case.py']==sha(OUT/'source/case.py')
 assert reports['trays']['source_sha256']['case.py']==sha(OUT/'source/case.py')
 for n,want in reports['fit-check']['source_STEP_sha256'].items():assert want==sha(OUT/'models'/n)
 assert reports['tray-trial']['source_tray_STEP_sha256']==sha(OUT/'models/tray-left.step')
 assert reports['tray-trial']['source_case_py_sha256']==sha(OUT/'source/case.py')
 for n in ['layer-inspection','fit-check-layers','tray-trial-layers']:
  d=json.loads((OUT/'reports'/f'{n}.json').read_text());assert all(x['visual_review']!='pending' for x in d.values()),n
 slices=json.loads((OUT/'reports/slicing.json').read_text());assert len(slices['plates'])==4
 for profile,h in slices['profiles_sha256'].items():assert h==sha(OUT/'profiles'/profile)
 for n,row in slices['plates'].items():
  assert row['passed'] and row['input_sha256']==sha(OUT/'plates'/f'{n}.3mf') and row['project_sha256']==sha(OUT/'PRINT'/row['project'])
 for n,folder in [('fit-check','FIT-CHECK'),('tray-trial','TRAY-FIT')]:
  d=reports[n]['slicing'];assert d['profiles_sha256']==slices['profiles_sha256']
  for row in d['plates'].values():assert row['passed'] and row['project_sha256']==sha(OUT/folder/row['project'])
 baseline=OUT.parent/'v23/release/tak-v23-print-kit.zip'
 if baseline.exists():assert sha(baseline)=='33510a63581b1a8b5f3c5afde34ed99acf6ecd5ccfb6bc49956e6d6e2b9e1221'
 git=subprocess.run(['git','rev-parse','HEAD'],cwd=OUT,capture_output=True,text=True)
 gaps=[g for r in reports['pip-hinges']['checks'] for g in r.get('estimated_bead_edge_gaps_mm',[])]
 files=[p for directory in ['source','profiles','models','PRINT','plates','FIT-CHECK','TRAY-FIT','previews','reports'] for p in (OUT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='provenance.json']
 report={'version':'V23 R2','status':'digital checks complete; physical trial candidate','source_commit':git.stdout.strip() if git.returncode==0 else None,'environment':{'python':sys.version,'cadquery':cq.__version__,'platform':platform.platform(),'slicer':slices['slicer']},'checks':counts,'total_checks':sum(counts.values()),'slices':{'full_build':4,'small_trials':2,'full_seconds':slices['total_estimated_seconds'],'full_grams':slices['total_estimated_grams']},'closed_envelope_mm':reports['hardware']['closed_envelope_including_hardware_mm'],'sampled_bead_edge_hinge_gap_range_mm':[min(gaps),max(gaps)],'physical_acceptance':False,'printer_started':False,'source_and_output_sha256':{str(p.relative_to(OUT)):sha(p) for p in sorted(files)},'baseline_zip_sha256':'33510a63581b1a8b5f3c5afde34ed99acf6ecd5ccfb6bc49956e6d6e2b9e1221'}
 (OUT/'reports/provenance.json').write_text(json.dumps(report,indent=2)+'\n');print('Provenance PASS',report['total_checks'],'checks; four full and two trial slices')
if __name__=='__main__':main()
