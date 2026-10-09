"""Install verified four-colour projects as V24's default boards and third trial."""
from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 report=json.loads((OUT/'reports/slicing.json').read_text())
 deposition=json.loads((OUT/'reports/colour-layers.json').read_text())
 assert all(c['pass'] for c in deposition['checks'])
 mapping=[('02-boards-black-white-silk','PRINT/02-sliding-board-tops-CC2-PLA.3mf'),
          ('00-inlay-trial-black-white-silk','INLAY-FIT/four-colour-inlay-trial-CC2-PLA.3mf')]
 for stem,target in mapping:
  source=OUT/'PRINT'/(stem+'-CC2.3mf');row=report['plates'][stem]
  assert row['readback_passed'] and sha(source)==row['output_sha256']
  assert deposition['projects'][source.name]['gcode_sha256']==row['gcode_sha256']
  dest=ROOT/target;dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
 shutil.copy2(OUT/'plates/02-boards-black-white-silk.3mf',ROOT/'plates/02-sliding-board-tops.3mf')
 current=json.loads((ROOT/'reports/slicing.json').read_text())
 row=report['plates']['02-boards-black-white-silk'].copy()
 row.update(passed=True,project='02-sliding-board-tops-CC2-PLA.3mf',project_sha256=row['output_sha256'],
            evidence='board-inlays/reports/slicing.json',four_materials=True)
 current['plates']['02-sliding-board-tops']=row
 current['total_estimated_seconds']=sum(int(p['slice_metadata']['prediction']) for p in current['plates'].values())
 current['total_estimated_grams']=round(sum(float(p['slice_metadata']['weight']) for p in current['plates'].values()),2)
 current['board_profiles']='board-inlays/profiles; two silk placeholders require actual profiles and reslice'
 (ROOT/'reports/slicing.json').write_text(json.dumps(current,indent=2)+'\n')
 print('Installed four-colour default board project and small trial.',flush=True)

if __name__=='__main__':main()
